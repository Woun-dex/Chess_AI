"""ORM model for the *users* table."""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from chess_ai.infrastructure.db.base import Base


class UserModel(Base):
    """Persisted user account."""

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        server_default=text("gen_random_uuid()::text"),
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    player_profile: Mapped["PlayerProfileModel"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "PlayerProfileModel", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    white_games: Mapped[list["GameModel"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "GameModel", foreign_keys="GameModel.white_player_id", back_populates="white_player"
    )
    black_games: Mapped[list["GameModel"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "GameModel", foreign_keys="GameModel.black_player_id", back_populates="black_player"
    )
    learning_profiles: Mapped[list["LearningProfileModel"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "LearningProfileModel", back_populates="user", cascade="all, delete-orphan"
    )
    tutor_sessions: Mapped[list["TutorSessionModel"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "TutorSessionModel", back_populates="user", cascade="all, delete-orphan"
    )
