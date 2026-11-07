"""ORM models for *tutor_sessions* and *tutor_messages* tables."""

import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy import text as sa_text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from chess_ai.infrastructure.db.base import Base


class MessageRole(StrEnum):
    STUDENT = "student"
    TUTOR = "tutor"


class TutorSessionModel(Base):
    """An interactive tutoring conversation tied to a user (and optionally a game)."""

    __tablename__ = "tutor_sessions"
    __table_args__ = (
        Index("ix_tutor_sessions_user_id", "user_id"),
        Index("ix_tutor_sessions_game_id", "game_id"),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        server_default=sa_text("gen_random_uuid()::text"),
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    game_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("games.id", ondelete="SET NULL"),
        nullable=True,
    )
    session_title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    user: Mapped["UserModel"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "UserModel", back_populates="tutor_sessions"
    )
    game: Mapped["GameModel | None"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "GameModel", back_populates="tutor_sessions"
    )
    messages: Mapped[list["TutorMessageModel"]] = relationship(
        "TutorMessageModel",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="TutorMessageModel.created_at",
    )
    checkpoints: Mapped[list["TutorCheckpointModel"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "TutorCheckpointModel", back_populates="session", cascade="all, delete-orphan"
    )


class TutorMessageModel(Base):
    """A single turn in a tutor–student conversation."""

    __tablename__ = "tutor_messages"
    __table_args__ = (
        Index("ix_tutor_messages_session_id", "session_id"),
        Index("ix_tutor_messages_created_at", "created_at"),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        server_default=sa_text("gen_random_uuid()::text"),
    )
    session_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("tutor_sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    role: Mapped[str] = mapped_column(String(10), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    fen_context: Mapped[str | None] = mapped_column(String(100), nullable=True)
    move_context_uci: Mapped[str | None] = mapped_column(String(10), nullable=True)
    token_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # Relationships
    session: Mapped["TutorSessionModel"] = relationship(
        "TutorSessionModel", back_populates="messages"
    )
