from __future__ import annotations

from typing import Any

from app.exceptions import DuplicateError, MemberHasBooksError, NotFoundError
from app.services.in_memory_store import InMemoryStore
from app.services.members.base import MemberService


class InMemoryMemberService(MemberService):
    """Implement Member use cases with process-local storage."""

    def __init__(self, store: InMemoryStore) -> None:
        self._store = store

    def create(self, data: dict[str, Any]) -> dict[str, Any]:
        with self._store.lock:
            if any(m["email"] == data["email"] or m["membership_id"] == data["membership_id"] for m in self._store.members.values()):
                raise DuplicateError("email or membership_id already exists")
            item = {"id": self._store.next_member_id, **data}
            self._store.members[item["id"]] = item
            self._store.next_member_id += 1
            return item

    def list(self) -> list[dict[str, Any]]:
        with self._store.lock:
            return list(self._store.members.values())

    def get(self, member_id: int) -> dict[str, Any]:
        with self._store.lock:
            item = self._store.members.get(member_id)
            if item is None:
                raise NotFoundError("Member not found")
            return item

    def update(self, member_id: int, changes: dict[str, Any]) -> dict[str, Any]:
        with self._store.lock:
            item = self.get(member_id)
            for field in ("email", "membership_id"):
                if field in changes and any(m[field] == changes[field] and m["id"] != member_id for m in self._store.members.values()):
                    raise DuplicateError(f"{field} already exists")
            item.update(changes)
            return item

    def delete(self, member_id: int) -> None:
        with self._store.lock:
            self.get(member_id)
            if any(book["member_id"] == member_id for book in self._store.books.values()):
                raise MemberHasBooksError("Member has associated books")
            del self._store.members[member_id]

    def books(self, member_id: int) -> list[dict[str, Any]]:
        with self._store.lock:
            self.get(member_id)
            return [book for book in self._store.books.values() if book["member_id"] == member_id]
