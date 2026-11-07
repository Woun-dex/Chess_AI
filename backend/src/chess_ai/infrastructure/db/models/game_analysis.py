"""ORM model for the *game_analyses* table."""

import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, String, Text, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from chess_ai.infrastructure.db.base import Base


class AnalysisStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class GameAnalysisModel(Base):
    """Analysis job metadata for a completed game (1-to-1 with Game)."""

    __tablename__ = "game_analyses"
    __table_args__ = (Index("ix_game_analyses_status", "status"),)

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        server_default=text("gen_random_uuid()::text"),
    )
    game_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("games.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False, default=AnalysisStatus.PENDING)
    depth: Mapped[int] = mapped_column(Integer, nullable=False, default=18)
    total_moves_analyzed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Classification counts
    brilliant_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    great_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    best_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    excellent_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    good_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    inaccuracy_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    mistake_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    blunder_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Accuracy metrics
    avg_centipawn_loss_white: Mapped[float | None] = mapped_column(Float, nullable=True)
    avg_centipawn_loss_black: Mapped[float | None] = mapped_column(Float, nullable=True)
    accuracy_white: Mapped[float | None] = mapped_column(Float, nullable=True)
    accuracy_black: Mapped[float | None] = mapped_column(Float, nullable=True)

    engine_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Idempotency pattern — prevents duplicate analysis jobs
    idempotency_key: Mapped[str | None] = mapped_column(
        String(100), unique=True, nullable=True, index=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    game: Mapped["GameModel"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "GameModel", back_populates="analysis"
    )
    move_analyses: Mapped[list["MoveAnalysisModel"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "MoveAnalysisModel", back_populates="game_analysis", cascade="all, delete-orphan"
    )
