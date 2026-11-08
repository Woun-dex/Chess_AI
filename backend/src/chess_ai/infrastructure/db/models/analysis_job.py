"""Durable background analysis jobs."""

import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, Float, Index, Integer, String, Text, UniqueConstraint, func, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from chess_ai.infrastructure.db.base import Base


class AnalysisJobStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    RETRYING = "retrying"
    DEAD = "dead"


class AnalysisJobModel(Base):
    """Idempotent job record and serialized analysis result."""

    __tablename__ = "analysis_jobs"
    __table_args__ = (
        UniqueConstraint("game_id", "game_version", "depth", "multipv", name="uq_analysis_job_request"),
        Index("ix_analysis_jobs_status", "status"),
        Index("ix_analysis_jobs_game_id", "game_id"),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4()),
        server_default=text("gen_random_uuid()::text"),
    )
    game_id: Mapped[str] = mapped_column(String(36), nullable=False)
    game_version: Mapped[int] = mapped_column(Integer, nullable=False)
    depth: Mapped[int] = mapped_column(Integer, nullable=False)
    multipv: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default=AnalysisJobStatus.QUEUED)
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    game_snapshot: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)
    result: Mapped[dict[str, object] | None] = mapped_column(JSONB, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    queued_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    next_retry_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    progress: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
