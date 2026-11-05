"""ORM models for *lessons*, *exercises*, and *exercise_attempts* tables."""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy import text as sa_text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from chess_ai.infrastructure.db.base import Base


class LessonModel(Base):
    """Pedagogical lesson unit."""

    __tablename__ = "lessons"
    __table_args__ = (
        Index("ix_lessons_concept_key", "concept_key"),
        Index("ix_lessons_difficulty_level", "difficulty_level"),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        server_default=sa_text("gen_random_uuid()::text"),
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    concept_key: Mapped[str] = mapped_column(String(100), nullable=False)
    difficulty_level: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    content_markdown: Mapped[str] = mapped_column(Text, nullable=False, default="")
    pgn_examples: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_published: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    exercises: Mapped[list["ExerciseModel"]] = relationship(
        "ExerciseModel", back_populates="lesson"
    )
    training_plan_items: Mapped[list["TrainingPlanItemModel"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "TrainingPlanItemModel", back_populates="lesson"
    )


class ExerciseModel(Base):
    """Tactical puzzle or positional exercise."""

    __tablename__ = "exercises"
    __table_args__ = (
        Index("ix_exercises_concept_key", "concept_key"),
        Index("ix_exercises_difficulty_level", "difficulty_level"),
        Index("ix_exercises_lesson_id", "lesson_id"),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        server_default=sa_text("gen_random_uuid()::text"),
    )
    lesson_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("lessons.id", ondelete="SET NULL"),
        nullable=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    fen: Mapped[str] = mapped_column(Text, nullable=False)
    correct_move_uci: Mapped[str] = mapped_column(String(10), nullable=False)
    correct_move_san: Mapped[str] = mapped_column(String(20), nullable=False)
    solution_explanation: Mapped[str] = mapped_column(Text, nullable=False, default="")
    difficulty_level: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    concept_key: Mapped[str] = mapped_column(String(100), nullable=False)
    is_published: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # Relationships
    lesson: Mapped["LessonModel | None"] = relationship("LessonModel", back_populates="exercises")
    attempts: Mapped[list["ExerciseAttemptModel"]] = relationship(
        "ExerciseAttemptModel", back_populates="exercise", cascade="all, delete-orphan"
    )
    training_plan_items: Mapped[list["TrainingPlanItemModel"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "TrainingPlanItemModel", back_populates="exercise"
    )


class ExerciseAttemptModel(Base):
    """Records a user's attempt at solving an exercise."""

    __tablename__ = "exercise_attempts"
    __table_args__ = (
        Index("ix_exercise_attempts_user_id", "user_id"),
        Index("ix_exercise_attempts_exercise_id", "exercise_id"),
        Index("ix_exercise_attempts_attempted_at", "attempted_at"),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        server_default=sa_text("gen_random_uuid()::text"),
    )
    exercise_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("exercises.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    submitted_move_uci: Mapped[str] = mapped_column(String(10), nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False)
    time_spent_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    attempted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # Relationships
    exercise: Mapped["ExerciseModel"] = relationship(
        "ExerciseModel", back_populates="attempts"
    )
