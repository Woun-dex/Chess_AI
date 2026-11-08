"""Add append-only learning evidence.

Revision ID: 003
Revises: 002
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "003"
down_revision: str | None = "002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "skill_evidence",
        sa.Column("id", sa.String(36), server_default=sa.text("gen_random_uuid()::text"), nullable=False),
        sa.Column("user_id", sa.String(36), nullable=False),
        sa.Column("skill_key", sa.String(100), nullable=False),
        sa.Column("source_type", sa.String(30), nullable=False),
        sa.Column("source_id", sa.String(36), nullable=False),
        sa.Column("outcome", sa.String(20), nullable=False),
        sa.Column("signal_strength", sa.Float(), nullable=False, server_default="1.0"),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_skill_evidence_user_id", "skill_evidence", ["user_id"])
    op.create_index("ix_skill_evidence_user_skill", "skill_evidence", ["user_id", "skill_key"])
    op.create_index("ix_skill_evidence_occurred_at", "skill_evidence", ["occurred_at"])


def downgrade() -> None:
    op.drop_index("ix_skill_evidence_occurred_at", table_name="skill_evidence")
    op.drop_index("ix_skill_evidence_user_skill", table_name="skill_evidence")
    op.drop_index("ix_skill_evidence_user_id", table_name="skill_evidence")
    op.drop_table("skill_evidence")
