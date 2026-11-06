"""001 initial schema — all 14 tables.

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

PK_DEFAULT = sa.text("gen_random_uuid()::text")


def upgrade() -> None:
    # -----------------------------------------------------------------------
    # users
    # -----------------------------------------------------------------------
    op.create_table(
        "users",
        sa.Column("id", sa.String(36), server_default=PK_DEFAULT, nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("username", sa.String(50), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email", name="uq_users_email"),
        sa.UniqueConstraint("username", name="uq_users_username"),
    )
    op.create_index("ix_users_email", "users", ["email"])
    op.create_index("ix_users_username", "users", ["username"])

    # -----------------------------------------------------------------------
    # player_profiles
    # -----------------------------------------------------------------------
    op.create_table(
        "player_profiles",
        sa.Column("id", sa.String(36), server_default=PK_DEFAULT, nullable=False),
        sa.Column("user_id", sa.String(36), nullable=False),
        sa.Column("preferred_color", sa.String(10), nullable=False, server_default="random"),
        sa.Column("classical_rating", sa.Integer(), nullable=False, server_default="1200"),
        sa.Column("blitz_rating", sa.Integer(), nullable=False, server_default="1200"),
        sa.Column("rapid_rating", sa.Integer(), nullable=False, server_default="1200"),
        sa.Column("games_played", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("wins", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("losses", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("draws", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("favorite_opening_as_white", sa.String(100), nullable=True),
        sa.Column("favorite_opening_as_black", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", name="uq_player_profiles_user_id"),
    )
    op.create_index("ix_player_profiles_user_id", "player_profiles", ["user_id"])

    # -----------------------------------------------------------------------
    # games
    # -----------------------------------------------------------------------
    op.create_table(
        "games",
        sa.Column("id", sa.String(36), server_default=PK_DEFAULT, nullable=False),
        sa.Column("white_player_id", sa.String(36), nullable=False),
        sa.Column("black_player_id", sa.String(36), nullable=True),
        sa.Column("opponent_type", sa.String(20), nullable=False, server_default="stockfish_bot"),
        sa.Column("bot_skill_level", sa.Integer(), nullable=True),
        sa.Column("time_control_seconds", sa.Integer(), nullable=True),
        sa.Column("increment_seconds", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(30), nullable=False, server_default="in_progress"),
        sa.Column("winner_color", sa.String(10), nullable=True),
        sa.Column(
            "initial_fen",
            sa.Text(),
            nullable=False,
            server_default="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
        ),
        sa.Column("pgn", sa.Text(), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["white_player_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["black_player_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_games_white_player_id", "games", ["white_player_id"])
    op.create_index("ix_games_black_player_id", "games", ["black_player_id"])
    op.create_index("ix_games_status", "games", ["status"])
    op.create_index("ix_games_created_at", "games", ["created_at"])

    # -----------------------------------------------------------------------
    # game_moves
    # -----------------------------------------------------------------------
    op.create_table(
        "game_moves",
        sa.Column("id", sa.String(36), server_default=PK_DEFAULT, nullable=False),
        sa.Column("game_id", sa.String(36), nullable=False),
        sa.Column("move_number", sa.Integer(), nullable=False),
        sa.Column("color", sa.String(10), nullable=False),
        sa.Column("uci", sa.String(10), nullable=False),
        sa.Column("san", sa.String(20), nullable=False),
        sa.Column("fen_before", sa.Text(), nullable=False),
        sa.Column("fen_after", sa.Text(), nullable=False),
        sa.Column("time_spent_ms", sa.Integer(), nullable=True),
        sa.Column("clock_remaining_ms", sa.Integer(), nullable=True),
        sa.Column("is_in_check", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("played_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["game_id"], ["games.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("game_id", "move_number", name="uq_game_moves_game_move_number"),
    )
    op.create_index("ix_game_moves_game_id", "game_moves", ["game_id"])
    op.create_index("ix_game_moves_played_at", "game_moves", ["played_at"])

    # -----------------------------------------------------------------------
    # game_analyses
    # -----------------------------------------------------------------------
    op.create_table(
        "game_analyses",
        sa.Column("id", sa.String(36), server_default=PK_DEFAULT, nullable=False),
        sa.Column("game_id", sa.String(36), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("depth", sa.Integer(), nullable=False, server_default="18"),
        sa.Column("total_moves_analyzed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("brilliant_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("great_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("best_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("excellent_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("good_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("inaccuracy_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("mistake_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("blunder_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("avg_centipawn_loss_white", sa.Float(), nullable=True),
        sa.Column("avg_centipawn_loss_black", sa.Float(), nullable=True),
        sa.Column("accuracy_white", sa.Float(), nullable=True),
        sa.Column("accuracy_black", sa.Float(), nullable=True),
        sa.Column("engine_version", sa.String(50), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("retry_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("idempotency_key", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["game_id"], ["games.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("game_id", name="uq_game_analyses_game_id"),
        sa.UniqueConstraint("idempotency_key", name="uq_game_analyses_idempotency_key"),
    )
    op.create_index("ix_game_analyses_game_id", "game_analyses", ["game_id"])
    op.create_index("ix_game_analyses_status", "game_analyses", ["status"])
    op.create_index("ix_game_analyses_idempotency_key", "game_analyses", ["idempotency_key"])

    # -----------------------------------------------------------------------
    # move_analyses
    # -----------------------------------------------------------------------
    op.create_table(
        "move_analyses",
        sa.Column("id", sa.String(36), server_default=PK_DEFAULT, nullable=False),
        sa.Column("game_analysis_id", sa.String(36), nullable=False),
        sa.Column("game_move_id", sa.String(36), nullable=False),
        sa.Column("classification", sa.String(15), nullable=False),
        sa.Column("centipawn_loss", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("eval_before_cp", sa.Integer(), nullable=True),
        sa.Column("eval_after_cp", sa.Integer(), nullable=True),
        sa.Column("mate_in_before", sa.Integer(), nullable=True),
        sa.Column("mate_in_after", sa.Integer(), nullable=True),
        sa.Column("best_move_uci", sa.String(10), nullable=False),
        sa.Column("principal_variation", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"),
        sa.Column("tactical_motifs", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"),
        sa.ForeignKeyConstraint(["game_analysis_id"], ["game_analyses.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["game_move_id"], ["game_moves.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("game_move_id", name="uq_move_analyses_game_move_id"),
    )
    op.create_index("ix_move_analyses_game_analysis_id", "move_analyses", ["game_analysis_id"])
    op.create_index("ix_move_analyses_game_move_id", "move_analyses", ["game_move_id"])

    # -----------------------------------------------------------------------
    # lessons
    # -----------------------------------------------------------------------
    op.create_table(
        "lessons",
        sa.Column("id", sa.String(36), server_default=PK_DEFAULT, nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("concept_key", sa.String(100), nullable=False),
        sa.Column("difficulty_level", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("content_markdown", sa.Text(), nullable=False, server_default=""),
        sa.Column("pgn_examples", sa.Text(), nullable=True),
        sa.Column("is_published", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_lessons_concept_key", "lessons", ["concept_key"])
    op.create_index("ix_lessons_difficulty_level", "lessons", ["difficulty_level"])

    # -----------------------------------------------------------------------
    # exercises
    # -----------------------------------------------------------------------
    op.create_table(
        "exercises",
        sa.Column("id", sa.String(36), server_default=PK_DEFAULT, nullable=False),
        sa.Column("lesson_id", sa.String(36), nullable=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("fen", sa.Text(), nullable=False),
        sa.Column("correct_move_uci", sa.String(10), nullable=False),
        sa.Column("correct_move_san", sa.String(20), nullable=False),
        sa.Column("solution_explanation", sa.Text(), nullable=False, server_default=""),
        sa.Column("difficulty_level", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("concept_key", sa.String(100), nullable=False),
        sa.Column("is_published", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["lesson_id"], ["lessons.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_exercises_concept_key", "exercises", ["concept_key"])
    op.create_index("ix_exercises_difficulty_level", "exercises", ["difficulty_level"])
    op.create_index("ix_exercises_lesson_id", "exercises", ["lesson_id"])

    # -----------------------------------------------------------------------
    # exercise_attempts
    # -----------------------------------------------------------------------
    op.create_table(
        "exercise_attempts",
        sa.Column("id", sa.String(36), server_default=PK_DEFAULT, nullable=False),
        sa.Column("exercise_id", sa.String(36), nullable=False),
        sa.Column("user_id", sa.String(36), nullable=False),
        sa.Column("submitted_move_uci", sa.String(10), nullable=False),
        sa.Column("is_correct", sa.Boolean(), nullable=False),
        sa.Column("time_spent_ms", sa.Integer(), nullable=True),
        sa.Column("attempted_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["exercise_id"], ["exercises.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_exercise_attempts_user_id", "exercise_attempts", ["user_id"])
    op.create_index("ix_exercise_attempts_exercise_id", "exercise_attempts", ["exercise_id"])
    op.create_index("ix_exercise_attempts_attempted_at", "exercise_attempts", ["attempted_at"])

    # -----------------------------------------------------------------------
    # learning_profiles
    # -----------------------------------------------------------------------
    op.create_table(
        "learning_profiles",
        sa.Column("id", sa.String(36), server_default=PK_DEFAULT, nullable=False),
        sa.Column("user_id", sa.String(36), nullable=False),
        sa.Column("concept_key", sa.String(100), nullable=False),
        sa.Column("mastery_score", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("exposures", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("correct_attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_practiced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "concept_key", name="uq_learning_profiles_user_concept"),
    )
    op.create_index("ix_learning_profiles_user_id", "learning_profiles", ["user_id"])
    op.create_index("ix_learning_profiles_concept_key", "learning_profiles", ["concept_key"])
    op.create_index("ix_learning_profiles_last_practiced_at", "learning_profiles", ["last_practiced_at"])

    # -----------------------------------------------------------------------
    # training_plans
    # -----------------------------------------------------------------------
    op.create_table(
        "training_plans",
        sa.Column("id", sa.String(36), server_default=PK_DEFAULT, nullable=False),
        sa.Column("user_id", sa.String(36), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("generated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("valid_until", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_training_plans_user_id", "training_plans", ["user_id"])

    # -----------------------------------------------------------------------
    # training_plan_items
    # -----------------------------------------------------------------------
    op.create_table(
        "training_plan_items",
        sa.Column("id", sa.String(36), server_default=PK_DEFAULT, nullable=False),
        sa.Column("training_plan_id", sa.String(36), nullable=False),
        sa.Column("exercise_id", sa.String(36), nullable=True),
        sa.Column("lesson_id", sa.String(36), nullable=True),
        sa.Column("order_index", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_completed", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["training_plan_id"], ["training_plans.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["exercise_id"], ["exercises.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["lesson_id"], ["lessons.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_training_plan_items_plan_id", "training_plan_items", ["training_plan_id"])

    # -----------------------------------------------------------------------
    # tutor_sessions
    # -----------------------------------------------------------------------
    op.create_table(
        "tutor_sessions",
        sa.Column("id", sa.String(36), server_default=PK_DEFAULT, nullable=False),
        sa.Column("user_id", sa.String(36), nullable=False),
        sa.Column("game_id", sa.String(36), nullable=True),
        sa.Column("session_title", sa.String(255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["game_id"], ["games.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_tutor_sessions_user_id", "tutor_sessions", ["user_id"])
    op.create_index("ix_tutor_sessions_game_id", "tutor_sessions", ["game_id"])

    # -----------------------------------------------------------------------
    # tutor_messages
    # -----------------------------------------------------------------------
    op.create_table(
        "tutor_messages",
        sa.Column("id", sa.String(36), server_default=PK_DEFAULT, nullable=False),
        sa.Column("session_id", sa.String(36), nullable=False),
        sa.Column("role", sa.String(10), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("fen_context", sa.String(100), nullable=True),
        sa.Column("move_context_uci", sa.String(10), nullable=True),
        sa.Column("token_count", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["tutor_sessions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_tutor_messages_session_id", "tutor_messages", ["session_id"])
    op.create_index("ix_tutor_messages_created_at", "tutor_messages", ["created_at"])

    # -----------------------------------------------------------------------
    # outbox_events
    # -----------------------------------------------------------------------
    op.create_table(
        "outbox_events",
        sa.Column("id", sa.String(36), server_default=PK_DEFAULT, nullable=False),
        sa.Column("event_type", sa.String(100), nullable=False),
        sa.Column("aggregate_id", sa.String(36), nullable=False),
        sa.Column("aggregate_type", sa.String(50), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("is_published", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_outbox_events_is_published", "outbox_events", ["is_published"])
    op.create_index("ix_outbox_events_created_at", "outbox_events", ["created_at"])
    op.create_index("ix_outbox_events_aggregate_id", "outbox_events", ["aggregate_id"])
    op.create_index("ix_outbox_events_event_type", "outbox_events", ["event_type"])


def downgrade() -> None:
    op.drop_table("outbox_events")
    op.drop_table("tutor_messages")
    op.drop_table("tutor_sessions")
    op.drop_table("training_plan_items")
    op.drop_table("training_plans")
    op.drop_table("learning_profiles")
    op.drop_table("exercise_attempts")
    op.drop_table("exercises")
    op.drop_table("lessons")
    op.drop_table("move_analyses")
    op.drop_table("game_analyses")
    op.drop_table("game_moves")
    op.drop_table("games")
    op.drop_table("player_profiles")
    op.drop_table("users")
