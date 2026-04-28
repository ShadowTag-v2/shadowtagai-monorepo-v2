# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Create legal deadline management tables

Revision ID: 001
Create Date: 2025-11-17
"""

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON

from alembic import op

# revision identifiers
revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Create all tables for legal deadline management"""
    # Legal documents table
    op.create_table(
        "legal_documents",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("document_type", sa.String(50), nullable=False),
        sa.Column("file_name", sa.String(500), nullable=False),
        sa.Column("file_path", sa.String(1000), nullable=False),
        sa.Column("jurisdiction", sa.String(50), nullable=False),
        sa.Column("case_number", sa.String(200), nullable=True),
        sa.Column("filing_date", sa.Date, nullable=True),
        sa.Column("service_date", sa.Date, nullable=True),
        sa.Column("service_method", sa.String(50), nullable=True),
        sa.Column("extracted_text", sa.Text, nullable=True),
        sa.Column("deadlines_count", sa.Integer, default=0),
        sa.Column("processing_status", sa.String(50), default="pending"),
        sa.Column("uploaded_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("processed_at", sa.DateTime, nullable=True),
        sa.Column("uploaded_by", sa.String(200), nullable=False),
        sa.Column("metadata", JSON, nullable=True),
    )
    op.create_index("idx_jurisdiction", "legal_documents", ["jurisdiction"])
    op.create_index("idx_case_number", "legal_documents", ["case_number"])
    op.create_index("idx_uploaded_at", "legal_documents", ["uploaded_at"])
    op.create_index("idx_processing_status", "legal_documents", ["processing_status"])

    # Deadlines table
    op.create_table(
        "deadlines",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column(
            "document_id",
            sa.String(50),
            sa.ForeignKey("legal_documents.id"),
            nullable=False,
        ),
        sa.Column("deadline_type", sa.String(50), nullable=False),
        sa.Column("deadline_date", sa.Date, nullable=False),
        sa.Column("trigger_date", sa.Date, nullable=True),
        sa.Column("trigger_event", sa.Text, nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("jurisdiction", sa.String(50), nullable=False),
        sa.Column("case_number", sa.String(200), nullable=True),
        sa.Column("party_names", JSON, nullable=True),
        sa.Column("confidence", sa.String(50), nullable=False),
        sa.Column("status", sa.String(50), default="pending"),
        sa.Column("requires_review", sa.Boolean, default=False),
        sa.Column("review_reason", sa.Text, nullable=True),
        sa.Column("calculation_details", JSON, nullable=True),
        sa.Column("reminder_schedule", JSON, nullable=True),
        sa.Column("assigned_to", sa.String(200), nullable=True),
        sa.Column("extracted_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("verified_at", sa.DateTime, nullable=True),
        sa.Column("verified_by", sa.String(200), nullable=True),
        sa.Column("metadata", JSON, nullable=True),
    )
    op.create_index("idx_deadline_date", "deadlines", ["deadline_date"])
    op.create_index("idx_deadline_jurisdiction", "deadlines", ["jurisdiction"])
    op.create_index("idx_deadline_case_number", "deadlines", ["case_number"])
    op.create_index("idx_status", "deadlines", ["status"])
    op.create_index("idx_requires_review", "deadlines", ["requires_review"])
    op.create_index("idx_assigned_to", "deadlines", ["assigned_to"])

    # Deadline rules table
    op.create_table(
        "deadline_rules",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("jurisdiction", sa.String(50), nullable=False),
        sa.Column("jurisdiction_type", sa.String(50), nullable=False),
        sa.Column("deadline_type", sa.String(50), nullable=False),
        sa.Column("base_days", sa.Integer, nullable=False),
        sa.Column("exclude_weekends", sa.Boolean, default=True),
        sa.Column("exclude_holidays", sa.Boolean, default=True),
        sa.Column("service_method_additions", JSON, nullable=True),
        sa.Column("trigger_event", sa.String(500), nullable=False),
        sa.Column("rule_source", sa.String(500), nullable=False),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index("idx_jurisdiction_type", "deadline_rules", ["jurisdiction", "deadline_type"])

    # Calendar entries table
    op.create_table(
        "calendar_entries",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("deadline_id", sa.String(50), sa.ForeignKey("deadlines.id"), nullable=False),
        sa.Column("calendar_provider", sa.String(50), nullable=False),
        sa.Column("calendar_id", sa.String(200), nullable=False),
        sa.Column("event_id", sa.String(200), nullable=True),
        sa.Column("synced", sa.Boolean, default=False),
        sa.Column("sync_error", sa.Text, nullable=True),
        sa.Column("last_synced", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index("idx_calendar_deadline_id", "calendar_entries", ["deadline_id"])
    op.create_index("idx_calendar_provider", "calendar_entries", ["calendar_provider"])

    # Reminder logs table
    op.create_table(
        "reminder_logs",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("deadline_id", sa.String(50), sa.ForeignKey("deadlines.id"), nullable=False),
        sa.Column("reminder_date", sa.Date, nullable=False),
        sa.Column("days_before_deadline", sa.Integer, nullable=False),
        sa.Column("notification_channels", JSON, nullable=False),
        sa.Column("recipients", JSON, nullable=False),
        sa.Column("sent", sa.Boolean, default=False),
        sa.Column("sent_at", sa.DateTime, nullable=True),
        sa.Column("error", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index("idx_reminder_date", "reminder_logs", ["reminder_date"])
    op.create_index("idx_reminder_sent", "reminder_logs", ["sent"])

    # Holidays table
    op.create_table(
        "holidays",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("jurisdiction", sa.String(50), nullable=False),
        sa.Column("holiday_date", sa.Date, nullable=False),
        sa.Column("holiday_name", sa.String(200), nullable=False),
        sa.Column("year", sa.Integer, nullable=False),
    )
    op.create_index("idx_jurisdiction_date", "holidays", ["jurisdiction", "holiday_date"])
    op.create_index("idx_year", "holidays", ["year"])

    # Audit logs table
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("entity_type", sa.String(50), nullable=False),
        sa.Column("entity_id", sa.String(50), nullable=False),
        sa.Column("user_id", sa.String(200), nullable=False),
        sa.Column("changes", JSON, nullable=True),
        sa.Column("timestamp", sa.DateTime, server_default=sa.func.now()),
        sa.Column("ip_address", sa.String(50), nullable=True),
        sa.Column("user_agent", sa.String(500), nullable=True),
    )
    op.create_index("idx_entity", "audit_logs", ["entity_type", "entity_id"])
    op.create_index("idx_user_id", "audit_logs", ["user_id"])
    op.create_index("idx_timestamp", "audit_logs", ["timestamp"])

    # ML feedback table
    op.create_table(
        "ml_feedback",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("deadline_id", sa.String(50), nullable=False),
        sa.Column("document_id", sa.String(50), nullable=False),
        sa.Column("predicted_date", sa.Date, nullable=False),
        sa.Column("actual_date", sa.Date, nullable=False),
        sa.Column("prediction_confidence", sa.Float, nullable=False),
        sa.Column("was_correct", sa.Boolean, nullable=False),
        sa.Column("correction_reason", sa.Text, nullable=True),
        sa.Column("extraction_method", sa.String(50), nullable=False),
        sa.Column("features", JSON, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index("idx_was_correct", "ml_feedback", ["was_correct"])
    op.create_index("idx_extraction_method", "ml_feedback", ["extraction_method"])


def downgrade():
    """Drop all tables"""
    op.drop_table("ml_feedback")
    op.drop_table("audit_logs")
    op.drop_table("holidays")
    op.drop_table("reminder_logs")
    op.drop_table("calendar_entries")
    op.drop_table("deadline_rules")
    op.drop_table("deadlines")
    op.drop_table("legal_documents")
