"""ORM model for the *player_profiles* table."""

import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, ForeignKey, Integer, String, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from chess_ai.infrastructure.db.base import Base


class PreferredColor(StrEnum):
    WHITE = "white"
    BLACK = "black"
    RANDOM = "random"


class PlayerProfileModel(Base):
    """Extended player statistics and preferences (1-to-1 with User)."""

    __tablename__ = "player_profiles"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        server_default=text("gen_random_uuid()::text"),
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    preferred_color: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default=PreferredColor.RANDOM,
    )
    classical_rating: Mapped[int] = mapped_column(Integer, nullable=False, default=1200)
    blitz_rating: Mapped[int] = mapped_column(Integer, nullable=False, default=1200)
    rapid_rating: Mapped[int] = mapped_column(Integer, nullable=False, default=1200)
    games_played: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    wins: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    losses: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    draws: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    favorite_opening_as_white: Mapped[str | None] = mapped_column(String(100), nullable=True)
    favorite_opening_as_black: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    user: Mapped["UserModel"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "UserModel", back_populates="player_profile"
    )
