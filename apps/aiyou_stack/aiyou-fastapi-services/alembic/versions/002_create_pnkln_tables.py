"""create_pnkln_tables

Revision ID: 002
Revises: 001
Create Date: 2025-12-08 23:30:00.000000

"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- PROVENANCE / SHADOWTAG ---
    op.create_table(
        "watermarks",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("content_hash", sa.String(length=64), nullable=False),
        sa.Column("signature", sa.String(), nullable=False),
        sa.Column("merkle_root", sa.String(), nullable=True),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_watermarks_content_hash"), "watermarks", ["content_hash"], unique=True)
    op.create_index(op.f("ix_watermarks_created_at"), "watermarks", ["created_at"], unique=False)

    # --- GOVERNANCE / JUDGE #6 ---
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("trace_id", sa.String(length=64), nullable=False),
        sa.Column("kernel_name", sa.String(length=128), nullable=False),
        # P/R/B Standard
        sa.Column("purpose_score", sa.Float(), nullable=True),
        sa.Column("reasons_score", sa.Float(), nullable=True),
        sa.Column("brakes_score", sa.Float(), nullable=True),
        sa.Column("decision", sa.Boolean(), nullable=False),
        sa.Column("risk_tier", sa.String(length=16), nullable=False),
        sa.Column("inputs", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("outputs", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("latency_ms", sa.Float(), nullable=True),
        sa.Column("cost_usd", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_audit_logs_trace_id"), "audit_logs", ["trace_id"], unique=False)
    op.create_index(op.f("ix_audit_logs_created_at"), "audit_logs", ["created_at"], unique=False)
    op.create_index(op.f("ix_audit_logs_risk_tier"), "audit_logs", ["risk_tier"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_audit_logs_risk_tier"), table_name="audit_logs")
    op.drop_index(op.f("ix_audit_logs_created_at"), table_name="audit_logs")
    op.drop_index(op.f("ix_audit_logs_trace_id"), table_name="audit_logs")
    op.drop_table("audit_logs")

    op.drop_index(op.f("ix_watermarks_created_at"), table_name="watermarks")
    op.drop_index(op.f("ix_watermarks_content_hash"), table_name="watermarks")
    op.drop_table("watermarks")
