from typing import Any

from app.exceptions import DuplicateError, NotFoundError
from app.services.books.base import BookService
from app.services.in_memory_store import InMemoryStore


class InMemoryBookService(BookService):
    """Implement Book use cases with process-local storage."""

    def __init__(self, store: InMemoryStore) -> None:
        self._store = store

    def create(self, data: dict[str, Any]) -> dict[str, Any]:
        with self._store.lock:
            if data["member_id"] not in self._store.members:
                raise NotFoundError("Member not found")
            if any(book["isbn"] == data["isbn"] for book in self._store.books.values()):
                raise DuplicateError("ISBN already exists")
            item = {"id": self._store.next_book_id, **data}
            self._store.books[item["id"]] = item
            self._store.next_book_id += 1
            return item

    def list(self) -> list[dict[str, Any]]:
        with self._store.lock:
            return list(self._store.books.values())

    def get(self, book_id: int) -> dict[str, Any]:
        with self._store.lock:
            item = self._store.books.get(book_id)
            if item is None:
                raise NotFoundError("Book not found")
            return item

    def update(self, book_id: int, changes: dict[str, Any]) -> dict[str, Any]:
        with self._store.lock:
            item = self.get(book_id)
            if "member_id" in changes and changes["member_id"] not in self._store.members:
                raise NotFoundError("Member not found")
            if "isbn" in changes and any(b["isbn"] == changes["isbn"] and b["id"] != book_id for b in self._store.books.values()):
                raise DuplicateError("ISBN already exists")
            item.update(changes)
            return item

    def delete(self, book_id: int) -> None:
        with self._store.lock:
            self.get(book_id)
            del self._store.books[book_id]
