"""ORM model for the *games* table."""

import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from chess_ai.infrastructure.db.base import Base

STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"


class OpponentType(StrEnum):
    HUMAN = "human"
    STOCKFISH_BOT = "stockfish_bot"
    TRAINING = "training"


class GameStatusValue(StrEnum):
    IN_PROGRESS = "in_progress"
    CHECKMATE = "checkmate"
    STALEMATE = "stalemate"
    INSUFFICIENT_MATERIAL = "insufficient_material"
    SEVENTYFIVE_MOVES = "seventyfive_moves"
    FIVEFOLD_REPETITION = "fivefold_repetition"
    RESIGNED = "resigned"
    DRAW_AGREED = "draw_agreed"


class WinnerColor(StrEnum):
    WHITE = "white"
    BLACK = "black"
    DRAW = "draw"


class GameModel(Base):
    """Persisted chess game aggregate root."""

    __tablename__ = "games"
    __table_args__ = (
        Index("ix_games_white_player_id", "white_player_id"),
        Index("ix_games_black_player_id", "black_player_id"),
        Index("ix_games_status", "status"),
        Index("ix_games_created_at", "created_at"),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        server_default=text("gen_random_uuid()::text"),
    )
    white_player_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    black_player_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    opponent_type: Mapped[str] = mapped_column(
        String(20), nullable=False, default=OpponentType.STOCKFISH_BOT
    )
    bot_skill_level: Mapped[int | None] = mapped_column(Integer, nullable=True)
    time_control_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    increment_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(
        String(30), nullable=False, default=GameStatusValue.IN_PROGRESS
    )
    winner_color: Mapped[str | None] = mapped_column(String(10), nullable=True)
    initial_fen: Mapped[str] = mapped_column(Text, nullable=False, default=STARTING_FEN)
    pgn: Mapped[str | None] = mapped_column(Text, nullable=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    white_player: Mapped["UserModel"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "UserModel", foreign_keys=[white_player_id], back_populates="white_games"
    )
    black_player: Mapped["UserModel | None"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "UserModel", foreign_keys=[black_player_id], back_populates="black_games"
    )
    moves: Mapped[list["GameMoveModel"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "GameMoveModel",
        back_populates="game",
        cascade="all, delete-orphan",
        order_by="GameMoveModel.move_number",
    )
    analysis: Mapped["GameAnalysisModel | None"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "GameAnalysisModel", back_populates="game", uselist=False, cascade="all, delete-orphan"
    )
    tutor_sessions: Mapped[list["TutorSessionModel"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "TutorSessionModel", back_populates="game"
    )
