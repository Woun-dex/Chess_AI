"""ORM models for *learning_profiles*, *training_plans*, and *training_plan_items*."""

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy import text as sa_text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from chess_ai.infrastructure.db.base import Base


class LearningProfileModel(Base):
    """Tracks per-user mastery of a chess concept (spaced-repetition data)."""

    __tablename__ = "learning_profiles"
    __table_args__ = (
        UniqueConstraint("user_id", "concept_key", name="uq_learning_profiles_user_concept"),
        Index("ix_learning_profiles_user_id", "user_id"),
        Index("ix_learning_profiles_concept_key", "concept_key"),
        Index("ix_learning_profiles_last_practiced_at", "last_practiced_at"),
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
    concept_key: Mapped[str] = mapped_column(String(100), nullable=False)
    mastery_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    exposures: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    correct_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_practiced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    user: Mapped["UserModel"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "UserModel", back_populates="learning_profiles"
    )


class TrainingPlanModel(Base):
    """Auto-generated personalised training plan for a user."""

    __tablename__ = "training_plans"
    __table_args__ = (Index("ix_training_plans_user_id", "user_id"),)

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
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    valid_until: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Relationships
    items: Mapped[list["TrainingPlanItemModel"]] = relationship(
        "TrainingPlanItemModel",
        back_populates="training_plan",
        cascade="all, delete-orphan",
        order_by="TrainingPlanItemModel.order_index",
    )


class TrainingPlanItemModel(Base):
    """An ordered item (exercise or lesson) inside a training plan."""

    __tablename__ = "training_plan_items"
    __table_args__ = (Index("ix_training_plan_items_plan_id", "training_plan_id"),)

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        server_default=sa_text("gen_random_uuid()::text"),
    )
    training_plan_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("training_plans.id", ondelete="CASCADE"),
        nullable=False,
    )
    exercise_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("exercises.id", ondelete="SET NULL"),
        nullable=True,
    )
    lesson_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("lessons.id", ondelete="SET NULL"),
        nullable=True,
    )
    order_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_completed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    training_plan: Mapped["TrainingPlanModel"] = relationship(
        "TrainingPlanModel", back_populates="items"
    )
    exercise: Mapped["ExerciseModel | None"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "ExerciseModel", back_populates="training_plan_items"
    )
    lesson: Mapped["LessonModel | None"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "LessonModel", back_populates="training_plan_items"
    )
