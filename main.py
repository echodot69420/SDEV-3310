"""Fake Artist Goes to New York — homepage, lobby page, and game lobby API.

The lobby keeps one WebSocket open per player (/ws/lobby). Clients send a
heartbeat every few seconds; a background sweeper checks every
SWEEP_INTERVAL seconds and disconnects anyone silent for longer than their
timeout (15 seconds while active, longer while their tab is hidden).
"""

import asyncio
import secrets
import time
import uuid
from contextlib import suppress
from pathlib import Path

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="Fake Artist Goes to New York", version="1.0.0")


# --------------------------------------------------------------------------
# Static pages
# --------------------------------------------------------------------------


@app.get("/", include_in_schema=False)
def home() -> FileResponse:
    return FileResponse(BASE_DIR / "index.html")


@app.get("/lobby", include_in_schema=False)
def lobby_page() -> FileResponse:
    return FileResponse(BASE_DIR / "lobby.html")


# --------------------------------------------------------------------------
# Demo: items (unchanged, kept from the original simple server)
# --------------------------------------------------------------------------


class Item(BaseModel):
    name: str
    price: float
    in_stock: bool = True


# In-memory "database"
items: dict[int, Item] = {}
next_id = 1


@app.get("/items")
def list_items():
    return [{"id": item_id, **item.model_dump()} for item_id, item in items.items()]


@app.get("/items/{item_id}")
def get_item(item_id: int):
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"id": item_id, **items[item_id].model_dump()}


@app.post("/items", status_code=201)
def create_item(item: Item):
    global next_id
    items[next_id] = item
    created_id = next_id
    next_id += 1
    return {"id": created_id, **item.model_dump()}


@app.delete("/items/{item_id}", status_code=204)
def delete_item(item_id: int):
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    del items[item_id]


# --------------------------------------------------------------------------
# Game lobby: host / connect / quit
# --------------------------------------------------------------------------

CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # no I, O, 0, 1
CODE_LENGTH = 4
MAX_PLAYERS = 10
MAX_USERNAME_LENGTH = 16
MAX_THEME_LENGTH = 20

# Liveness tuning
HEARTBEAT_TIMEOUT = 15.0   # an active player silent this long is disconnected
AWAY_TIMEOUT = 120.0       # hidden tabs get throttled timers, so allow more
SWEEP_INTERVAL = 15.0      # how often the server checks who is still there


class GamePlayer(BaseModel):
    player_id: str
    username: str
    is_host: bool


class Game(BaseModel):
    code: str
    theme: str
    players: list[GamePlayer]
    started: bool = False


class HostRequest(BaseModel):
    username: str = Field(min_length=2, max_length=MAX_USERNAME_LENGTH)
    theme: str = Field(min_length=1, max_length=MAX_THEME_LENGTH)


class ConnectRequest(BaseModel):
    username: str = Field(min_length=2, max_length=MAX_USERNAME_LENGTH)
    code: str = Field(min_length=1, max_length=CODE_LENGTH)


class QuitRequest(BaseModel):
    code: str = Field(min_length=1, max_length=CODE_LENGTH)
    player_id: str = Field(min_length=1)


# In-memory lobby: game code -> Game
games: dict[str, Game] = {}


def _clean_username(username: str) -> str:
    username = username.strip()
    if len(username) < 2:
        raise HTTPException(status_code=422, detail="Username must be at least 2 characters.")
    return username


def _clean_code(code: str) -> str:
    code = code.strip().upper()
    if not code.isalnum() or len(code) != CODE_LENGTH:
        raise HTTPException(status_code=422, detail=f"Game code must be {CODE_LENGTH} characters.")
    return code


def _clean_theme(theme: str) -> str:
    theme = theme.strip()
    if not 1 <= len(theme) <= MAX_THEME_LENGTH:
        raise HTTPException(
            status_code=422,
            detail=f"Theme must be 1-{MAX_THEME_LENGTH} characters.",
        )
    return theme


def _new_code() -> str:
    """Generate an unused game code, raising if the lobby is out of codes."""
    for _ in range(1000):
        code = "".join(secrets.choice(CODE_ALPHABET) for _ in range(CODE_LENGTH))
        if code not in games:
            return code
    raise HTTPException(status_code=503, detail="No game codes available right now.")


def _get_game(code: str) -> Game:
    game = games.get(code)
    if game is None:
        raise HTTPException(status_code=404, detail="Game not found.")
    return game


def _find_player(game: Game, player_id: str) -> GamePlayer:
    for player in game.players:
        if player.player_id == player_id:
            return player
    raise HTTPException(status_code=404, detail="Player is not in this game.")


def _remove_player(code: str, player_id: str) -> bool:
    """Drop a player from a game; host duties pass on, empty games are deleted.

    Returns True if the player was actually in the game.
    """
    game = games.get(code)
    if game is None:
        return False
    leaving = _find_player_or_none(game, player_id)
    if leaving is None:
        return False

    was_host = leaving.is_host
    game.players = [p for p in game.players if p.player_id != player_id]

    if not game.players:
        del games[code]
    elif was_host:
        game.players[0].is_host = True
    return True


def _find_player_or_none(game: Game, player_id: str) -> GamePlayer | None:
    for player in game.players:
        if player.player_id == player_id:
            return player
    return None


@app.post("/host")
async def host_game(payload: HostRequest) -> Game:
    """Create a new game (with a theme) and return it with the creator as host."""
    username = _clean_username(payload.username)
    theme = _clean_theme(payload.theme)
    game = Game(
        code=_new_code(),
        theme=theme,
        players=[
            GamePlayer(
                player_id=uuid.uuid4().hex,
                username=username,
                is_host=True,
            )
        ],
    )
    games[game.code] = game
    return game


@app.post("/connect")
async def connect(payload: ConnectRequest) -> Game:
    """Join an existing game by code."""
    username = _clean_username(payload.username)
    code = _clean_code(payload.code)
    game = _get_game(code)

    if game.started:
        raise HTTPException(status_code=409, detail="Game already started.")
    if len(game.players) >= MAX_PLAYERS:
        raise HTTPException(status_code=409, detail="Game is full.")
    if any(p.username.lower() == username.lower() for p in game.players):
        raise HTTPException(status_code=409, detail="That username is taken in this game.")

    game.players.append(
        GamePlayer(player_id=uuid.uuid4().hex, username=username, is_host=False)
    )
    await _broadcast_players(code)
    return game


@app.post("/quit")
async def quit_game(payload: QuitRequest) -> dict:
    """Leave a game. Host duties pass to the next player; an empty game is deleted."""
    code = _clean_code(payload.code)
    game = _get_game(code)
    _find_player(game, payload.player_id)

    connection = _connections.get(code, {}).get(payload.player_id)
    if connection is not None:
        # The socket is open, so let it handle both the game state and the
        # broadcast — that keeps the page and the server in agreement.
        await _drop_connection(connection, "quit")
    else:
        _remove_player(code, payload.player_id)
        await _broadcast_players(code)

    remaining = games.get(code)
    if remaining is None:
        return {"code": code, "game_exists": False, "players": []}
    return {"code": code, "game_exists": True, "players": remaining.players}


@app.get("/game/{code}")
async def get_game(code: str) -> Game:
    """Look up a game (useful for debugging and for the lobby UI)."""
    return _get_game(_clean_code(code))


# --------------------------------------------------------------------------
# Persistent lobby connection (WebSocket) with 15-second liveness checks
# --------------------------------------------------------------------------


class LobbyConnection:
    """One live WebSocket belonging to one player in one game."""

    __slots__ = ("websocket", "code", "player_id", "last_seen", "away")

    def __init__(self, websocket: WebSocket, code: str, player_id: str) -> None:
        self.websocket = websocket
        self.code = code
        self.player_id = player_id
        self.last_seen = time.monotonic()
        self.away = False

    @property
    def timeout(self) -> float:
        return AWAY_TIMEOUT if self.away else HEARTBEAT_TIMEOUT

    @property
    def is_stale(self) -> bool:
        return (time.monotonic() - self.last_seen) > self.timeout


# game code -> player_id -> connection
_connections: dict[str, dict[str, LobbyConnection]] = {}
_sweeper_task: asyncio.Task | None = None


def _ensure_sweeper() -> None:
    """Start the periodic liveness sweep (idempotent, called per connection)."""
    global _sweeper_task
    if _sweeper_task is None or _sweeper_task.done():
        _sweeper_task = asyncio.create_task(_sweep_loop())


async def _sweep_loop() -> None:
    """Check every SWEEP_INTERVAL seconds and disconnect silent players."""
    while True:
        await asyncio.sleep(SWEEP_INTERVAL)
        now = time.monotonic()
        stale = [
            connection
            for group in _connections.values()
            for connection in list(group.values())
            if (now - connection.last_seen) > connection.timeout
        ]
        for connection in stale:
            with suppress(Exception):
                await _drop_connection(connection, "heartbeat timeout")


async def _broadcast_players(code: str) -> None:
    """Send the current player list to every open socket in a game."""
    game = games.get(code)
    payload = {
        "type": "players",
        "code": code,
        "theme": game.theme if game else "",
        "game_exists": game is not None,
        "players": [p.model_dump() for p in game.players] if game else [],
        "started": game.started if game else False,
    }
    for connection in list(_connections.get(code, {}).values()):
        with suppress(Exception):
            await connection.websocket.send_json(payload)


async def _drop_connection(connection: LobbyConnection, reason: str) -> None:
    """Detach a connection: remove the player, say why, close, then broadcast.

    Idempotent — the first caller wins, later callers (or the receive loop's
    ``finally``) find the connection already unregistered and do nothing.
    """
    group = _connections.get(connection.code, {})
    if group.pop(connection.player_id, None) is not connection:
        return

    _remove_player(connection.code, connection.player_id)

    with suppress(Exception):
        await connection.websocket.send_json(
            {"type": "bye", "reason": reason, "game_exists": connection.code in games}
        )
    with suppress(Exception):
        await connection.websocket.close(code=4401, reason=reason)

    if not group:
        _connections.pop(connection.code, None)

    await _broadcast_players(connection.code)


@app.websocket("/ws/lobby")
async def lobby_websocket(
    websocket: WebSocket,
    code: str = "",
    player_id: str = "",
) -> None:
    """Persistent lobby connection: heartbeat in, player list out.

    Protocol (JSON messages):
      client -> {"type": "ping"}              heartbeat, resets the 15s timer
      client -> {"type": "away"}              tab is hidden, longer grace period
      client -> {"type": "quit"}              leave the game
      server -> {"type": "players", ...}      broadcast player list
      server -> {"type": "pong"}              heartbeat reply
      server -> {"type": "bye", "reason": ..} you are being disconnected
    """
    await websocket.accept()
    code = code.strip().upper()
    game = games.get(code)

    if game is None:
        await websocket.send_json({"type": "bye", "reason": "game not found"})
        await websocket.close(code=4404, reason="game not found")
        return
    if _find_player_or_none(game, player_id) is None:
        await websocket.send_json({"type": "bye", "reason": "player not in this game"})
        await websocket.close(code=4404, reason="player not in this game")
        return

    _ensure_sweeper()

    group = _connections.setdefault(code, {})
    replaced = group.get(player_id)
    if replaced is not None:
        # Same player reconnected (refreshed the page): drop the old socket.
        with suppress(Exception):
            await replaced.websocket.close(code=4400, reason="replaced by a new connection")

    connection = LobbyConnection(websocket, code, player_id)
    group[player_id] = connection
    await _broadcast_players(code)

    try:
        while True:
            try:
                message = await websocket.receive_json()
            except ValueError:
                with suppress(Exception):
                    await websocket.send_json({"type": "error", "detail": "expected JSON"})
                continue

            if not isinstance(message, dict):
                continue

            connection.last_seen = time.monotonic()
            kind = message.get("type")

            if kind == "ping":
                connection.away = False
                with suppress(Exception):
                    await websocket.send_json({"type": "pong", "at": time.time()})
            elif kind == "away":
                connection.away = True
            elif kind == "quit":
                await _drop_connection(connection, "quit")
                return
            else:
                with suppress(Exception):
                    await websocket.send_json(
                        {"type": "error", "detail": f"unknown message type: {kind!r}"}
                    )
    except WebSocketDisconnect:
        pass
    finally:
        # Fires on page close, network loss, or a kick from the sweeper.
        if _connections.get(connection.code, {}).get(connection.player_id) is connection:
            await _drop_connection(connection, "disconnected")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
