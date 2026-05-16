# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""create_activeshield_tables

Revision ID: 003
Revises: 002
Create Date: 2025-12-09 10:00:00.000000

"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade():
    # Create activeshield_audit_logs table
    op.create_table(
        "activeshield_audit_logs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("shield_id", sa.String(length=64), nullable=False),
        sa.Column("session_id", sa.String(length=255), nullable=False),
        sa.Column("phase", sa.String(length=20), nullable=False),
        sa.Column("action", sa.String(length=32), nullable=False),
        sa.Column("passed", sa.Boolean(), nullable=False),
        sa.Column("processed_content", sa.String(), nullable=True),
        sa.Column("violations", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("warnings", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("audit_trail", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("processing_time_ms", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_activeshield_audit_logs_shield_id",
        "activeshield_audit_logs",
        ["shield_id"],
        unique=True,
    )
    op.create_index(
        "ix_activeshield_audit_logs_session_id",
        "activeshield_audit_logs",
        ["session_id"],
        unique=False,
    )
    op.create_index(
        "idx_activeshield_session_created",
        "activeshield_audit_logs",
        ["session_id", "created_at"],
        unique=False,
    )

    # Create activeshield_adverse_events table
    op.create_table(
        "activeshield_adverse_events",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("session_id", sa.String(length=255), nullable=False),
        sa.Column("audit_log_id", sa.String(length=36), nullable=True),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("description", sa.String(), nullable=False),
        sa.Column("severity", sa.String(length=32), nullable=False),
        sa.Column("context_snapshot", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("remediated", sa.Boolean(), nullable=True),
        sa.Column("remediation_notes", sa.String(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_activeshield_adverse_events_session_id",
        "activeshield_adverse_events",
        ["session_id"],
        unique=False,
    )
    op.create_index(
        "ix_activeshield_adverse_events_audit_log_id",
        "activeshield_adverse_events",
        ["audit_log_id"],
        unique=False,
    )


def downgrade():
    op.drop_index("ix_activeshield_adverse_events_audit_log_id", table_name="activeshield_adverse_events")
    op.drop_index("ix_activeshield_adverse_events_session_id", table_name="activeshield_adverse_events")
    op.drop_table("activeshield_adverse_events")

    op.drop_index("idx_activeshield_session_created", table_name="activeshield_audit_logs")
    op.drop_index("ix_activeshield_audit_logs_session_id", table_name="activeshield_audit_logs")
    op.drop_index("ix_activeshield_audit_logs_shield_id", table_name="activeshield_audit_logs")
    op.drop_table("activeshield_audit_logs")
