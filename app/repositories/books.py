"""Database operations for Book records."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.book import Book


class BookRepository:
    """Read and write Book rows with a SQLAlchemy Session."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get(self, book_id: int) -> Book | None:
        return self.session.get(Book, book_id)

    def list(self) -> list[Book]:
        return list(self.session.scalars(select(Book).order_by(Book.id)))

    def list_for_member(self, member_id: int) -> list[Book]:
        return list(self.session.scalars(select(Book).where(Book.member_id == member_id).order_by(Book.id)))

    def find_by_isbn(self, isbn: str, excluding_id: int | None = None) -> Book | None:
        query = select(Book).where(Book.isbn == isbn)
        if excluding_id is not None:
            query = query.where(Book.id != excluding_id)
        return self.session.scalar(query)

    def add(self, data: dict) -> Book:
        item = Book(**data)
        self.session.add(item)
        return item

    def delete(self, book: Book) -> None:
        self.session.delete(book)
