"""ORM model for the *game_moves* table."""

import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from chess_ai.infrastructure.db.base import Base


class MoveColor(StrEnum):
    WHITE = "white"
    BLACK = "black"


class GameMoveModel(Base):
    """Individual half-move (ply) within a game."""

    __tablename__ = "game_moves"
    __table_args__ = (
        UniqueConstraint("game_id", "move_number", name="uq_game_moves_game_move_number"),
        Index("ix_game_moves_game_id", "game_id"),
        Index("ix_game_moves_played_at", "played_at"),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        server_default=text("gen_random_uuid()::text"),
    )
    game_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("games.id", ondelete="CASCADE"),
        nullable=False,
    )
    move_number: Mapped[int] = mapped_column(Integer, nullable=False)
    color: Mapped[str] = mapped_column(String(10), nullable=False)
    uci: Mapped[str] = mapped_column(String(10), nullable=False)
    san: Mapped[str] = mapped_column(String(20), nullable=False)
    fen_before: Mapped[str] = mapped_column(Text, nullable=False)
    fen_after: Mapped[str] = mapped_column(Text, nullable=False)
    time_spent_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    clock_remaining_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_in_check: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    played_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # Relationships
    game: Mapped["GameModel"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "GameModel", back_populates="moves"
    )
    move_analysis: Mapped["MoveAnalysisModel | None"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "MoveAnalysisModel", back_populates="game_move", uselist=False, cascade="all, delete-orphan"
    )
