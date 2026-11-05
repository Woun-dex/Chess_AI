"""ORM model for the *move_analyses* table."""

import uuid
from enum import StrEnum

from sqlalchemy import ForeignKey, Index, Integer, String, Text
from sqlalchemy import text as sa_text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from chess_ai.infrastructure.db.base import Base


class MoveClassification(StrEnum):
    BRILLIANT = "brilliant"
    GREAT = "great"
    BEST = "best"
    EXCELLENT = "excellent"
    GOOD = "good"
    INACCURACY = "inaccuracy"
    MISTAKE = "mistake"
    BLUNDER = "blunder"


class MoveAnalysisModel(Base):
    """Engine evaluation result for a single game move."""

    __tablename__ = "move_analyses"
    __table_args__ = (Index("ix_move_analyses_game_analysis_id", "game_analysis_id"),)

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        server_default=sa_text("gen_random_uuid()::text"),
    )
    game_analysis_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("game_analyses.id", ondelete="CASCADE"),
        nullable=False,
    )
    game_move_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("game_moves.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    classification: Mapped[str] = mapped_column(String(15), nullable=False)
    centipawn_loss: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    eval_before_cp: Mapped[int | None] = mapped_column(Integer, nullable=True)
    eval_after_cp: Mapped[int | None] = mapped_column(Integer, nullable=True)
    mate_in_before: Mapped[int | None] = mapped_column(Integer, nullable=True)
    mate_in_after: Mapped[int | None] = mapped_column(Integer, nullable=True)
    best_move_uci: Mapped[str] = mapped_column(String(10), nullable=False)

    # JSONB for efficient querying on PostgreSQL; falls back to Text-JSON elsewhere
    principal_variation: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    tactical_motifs: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)

    # Relationships
    game_analysis: Mapped["GameAnalysisModel"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "GameAnalysisModel", back_populates="move_analyses"
    )
    game_move: Mapped["GameMoveModel"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "GameMoveModel", back_populates="move_analysis"
    )
