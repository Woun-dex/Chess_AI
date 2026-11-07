"""Durable tutor graph checkpoints."""

import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Index, String, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from chess_ai.infrastructure.db.base import Base


class TutorCheckpointModel(Base):
    __tablename__ = "tutor_checkpoints"
    __table_args__ = (Index("ix_tutor_checkpoints_session_id", "session_id"),)

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        server_default=text("gen_random_uuid()::text"),
    )
    session_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tutor_sessions.id", ondelete="CASCADE"), nullable=False
    )
    state: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    session: Mapped["TutorSessionModel"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "TutorSessionModel", back_populates="checkpoints"
    )
