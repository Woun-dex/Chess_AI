"""SQLAlchemy 2.0 declarative base shared by all ORM models."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Single shared declarative base for the entire application."""
