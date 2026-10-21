"""Shared process-local state for the in-memory service implementations."""

from threading import RLock
from typing import Any


class InMemoryStore:
    """Hold temporary library data shared by member and book services."""

    def __init__(self) -> None:
        self.lock = RLock()
        self.members: dict[int, dict[str, Any]] = {}
        self.books: dict[int, dict[str, Any]] = {}
        self.next_member_id = 1
        self.next_book_id = 1
