"""Declarative base for all ORM models."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """All models inherit from this class.

    Alembic's autogenerate reads Base.metadata to diff
    against the actual database schema.
    """