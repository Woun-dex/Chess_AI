"""ORM model for the *outbox_events* table (Transactional Outbox Pattern)."""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Index, String, func
from sqlalchemy import text as sa_text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from chess_ai.infrastructure.db.base import Base


class OutboxEventModel(Base):
    """
    Outbox pattern: domain events written inside the same DB transaction as the
    business state change, then polled and published to the message broker by a
    separate relay process.  The ``is_published`` index is critical — the relay
    query filters ``WHERE is_published = FALSE``.
    """

    __tablename__ = "outbox_events"
    __table_args__ = (
        # Critical: relay polls this index on every tick
        Index("ix_outbox_events_is_published", "is_published"),
        Index("ix_outbox_events_created_at", "created_at"),
        Index("ix_outbox_events_aggregate_id", "aggregate_id"),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        server_default=sa_text("gen_random_uuid()::text"),
    )
    event_type: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )  # e.g. "GameCompleted", "AnalysisRequested"
    aggregate_id: Mapped[str] = mapped_column(String(36), nullable=False)
    aggregate_type: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g. "Game"
    payload: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False, default=dict)
    is_published: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
