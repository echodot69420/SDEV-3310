from typing import Any

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from app.exceptions import DuplicateError, NotFoundError
from app.models.book import Book
from app.repositories.books import BookRepository
from app.repositories.members import MemberRepository
from app.services.books.base import BookService


class DatabaseBookService(BookService):
    def __init__(self, factory: sessionmaker[Session]) -> None:
        self.factory = factory

    def create(self, data: dict[str, Any]) -> Book:
        try:
            with self.factory.begin() as session:
                books, members = BookRepository(session), MemberRepository(session)
                if members.get(data["member_id"]) is None:
                    raise NotFoundError("Member not found")
                if books.find_by_isbn(data["isbn"]):
                    raise DuplicateError("ISBN already exists")
                item = books.add(data)
                session.flush()
                return item
        except IntegrityError as exc:
            raise DuplicateError("ISBN already exists") from exc

    def list(self) -> list[Book]:
        with self.factory() as session:
            return BookRepository(session).list()

    def get(self, book_id: int) -> Book:
        with self.factory() as session:
            item = BookRepository(session).get(book_id)
            if item is None:
                raise NotFoundError("Book not found")
            return item

    def update(self, book_id: int, changes: dict[str, Any]) -> Book:
        try:
            with self.factory.begin() as session:
                books, members = BookRepository(session), MemberRepository(session)
                item = books.get(book_id)
                if item is None:
                    raise NotFoundError("Book not found")
                if "member_id" in changes and members.get(changes["member_id"]) is None:
                    raise NotFoundError("Member not found")
                if "isbn" in changes and books.find_by_isbn(changes["isbn"], book_id):
                    raise DuplicateError("ISBN already exists")
                for key, value in changes.items():
                    setattr(item, key, value)
                session.flush()
                return item
        except IntegrityError as exc:
            raise DuplicateError("ISBN already exists") from exc

    def delete(self, book_id: int) -> None:
        with self.factory.begin() as session:
            books = BookRepository(session)
            item = books.get(book_id)
            if item is None:
                raise NotFoundError("Book not found")
            books.delete(item)
