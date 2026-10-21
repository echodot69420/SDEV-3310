"""Database operations for Member records."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.member import Member


class MemberRepository:
    """Read and write Member rows with a SQLAlchemy Session."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get(self, member_id: int) -> Member | None:
        return self.session.get(Member, member_id)

    def list(self) -> list[Member]:
        return list(self.session.scalars(select(Member).order_by(Member.id)))

    def find_by_unique(self, field: str, value: str, excluding_id: int | None = None) -> Member | None:
        query = select(Member).where(getattr(Member, field) == value)
        if excluding_id is not None:
            query = query.where(Member.id != excluding_id)
        return self.session.scalar(query)

    def add(self, data: dict) -> Member:
        item = Member(**data)
        self.session.add(item)
        return item

    def delete(self, member: Member) -> None:
        self.session.delete(member)
