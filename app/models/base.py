"""Shared SQLAlchemy declarative base for all library ORM models."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Register every ORM model in one SQLAlchemy metadata collection."""
