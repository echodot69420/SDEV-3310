from typing import Any

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from app.exceptions import DuplicateError, MemberHasBooksError, NotFoundError
from app.models.member import Member
from app.repositories.books import BookRepository
from app.repositories.members import MemberRepository
from app.services.members.base import MemberService


class DatabaseMemberService(MemberService):
    def __init__(self, factory: sessionmaker[Session]) -> None:
        self.factory = factory

    def create(self, data: dict[str, Any]) -> Member:
        try:
            with self.factory.begin() as session:
                members = MemberRepository(session)
                if members.find_by_unique("email", data["email"]) or members.find_by_unique("membership_id", data["membership_id"]):
                    raise DuplicateError("email or membership_id already exists")
                item = members.add(data)
                session.flush()
                return item
        except IntegrityError as exc:
            raise DuplicateError("email or membership_id already exists") from exc

    def list(self) -> list[Member]:
        with self.factory() as session:
            return MemberRepository(session).list()

    def get(self, member_id: int) -> Member:
        with self.factory() as session:
            item = MemberRepository(session).get(member_id)
            if item is None:
                raise NotFoundError("Member not found")
            return item

    def update(self, member_id: int, changes: dict[str, Any]) -> Member:
        try:
            with self.factory.begin() as session:
                members = MemberRepository(session)
                item = members.get(member_id)
                if item is None:
                    raise NotFoundError("Member not found")
                for field in ("email", "membership_id"):
                    if field in changes and members.find_by_unique(field, changes[field], member_id):
                        raise DuplicateError(f"{field} already exists")
                for key, value in changes.items():
                    setattr(item, key, value)
                session.flush()
                return item
        except IntegrityError as exc:
            raise DuplicateError("member value already exists") from exc

    def delete(self, member_id: int) -> None:
        with self.factory.begin() as session:
            members, books = MemberRepository(session), BookRepository(session)
            item = members.get(member_id)
            if item is None:
                raise NotFoundError("Member not found")
            if books.list_for_member(member_id):
                raise MemberHasBooksError("Member has associated books")
            members.delete(item)

    def books(self, member_id: int):
        with self.factory() as session:
            members, books = MemberRepository(session), BookRepository(session)
            if members.get(member_id) is None:
                raise NotFoundError("Member not found")
            return books.list_for_member(member_id)
