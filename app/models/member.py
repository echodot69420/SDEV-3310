"""SQLAlchemy model for library members."""

from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Member(Base):
    """Map Member objects to rows in the members table."""

    __tablename__ = "members"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(320), nullable=False, unique=True, index=True)
    membership_id: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(String(32), nullable=False)
    books: Mapped[list["Book"]] = relationship(back_populates="member")
