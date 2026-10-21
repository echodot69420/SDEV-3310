from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BookService(ABC):
    @abstractmethod
    def create(self, data: dict[str, Any]) -> Any: ...
    @abstractmethod
    def list(self) -> list[Any]: ...
    @abstractmethod
    def get(self, book_id: int) -> Any: ...
    @abstractmethod
    def update(self, book_id: int, changes: dict[str, Any]) -> Any: ...
    @abstractmethod
    def delete(self, book_id: int) -> None: ...
