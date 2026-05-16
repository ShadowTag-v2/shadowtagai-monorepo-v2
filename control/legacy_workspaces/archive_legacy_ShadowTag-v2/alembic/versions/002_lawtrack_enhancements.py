# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""LawTrack enhancements - jurisdiction rules, matters, timeline events, email ingestion, enforcement

Revision ID: 002
Revises: 001
Create Date: 2025-11-29
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers
revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade():
  """Create LawTrack enhancement tables"""

  # 1. Jurisdiction Rules Table
  op.create_table(
    "jurisdiction_rules",
    sa.Column("id", sa.String(36), primary_key=True),
    sa.Column("jurisdiction", sa.String(100), nullable=False, index=True),
    sa.Column("rule_code", sa.String(100), nullable=False),
    sa.Column("rule_text", sa.Text, nullable=True),
    sa.Column("days_allowed", sa.Integer, nullable=False),
    sa.Column(
      "service_method_adjustments",
      JSONB,
      nullable=True,
      comment='JSON object like {"mail": 3, "electronic": 0}',
    ),
    sa.Column("effective_date", sa.Date, nullable=False),
    sa.Column("deprecated_date", sa.Date, nullable=True),
    sa.Column("confidence_weight", sa.Float, default=1.0),
    sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=sa.func.now()),
  )
  # Composite unique constraint on jurisdiction + rule_code
  op.create_index(
    "idx_jurisdiction_rule_code",
    "jurisdiction_rules",
    ["jurisdiction", "rule_code"],
    unique=True,
  )
  op.create_index(
    "idx_jurisdiction_rules_effective", "jurisdiction_rules", ["effective_date"]
  )
  op.create_index(
    "idx_jurisdiction_rules_deprecated", "jurisdiction_rules", ["deprecated_date"]
  )

  # 2. Matters Table (cases/matters)
  op.create_table(
    "matters",
    sa.Column("id", sa.String(36), primary_key=True),
    sa.Column("case_number", sa.String(200), nullable=False, index=True),
    sa.Column("court", sa.String(200), nullable=False),
    sa.Column("jurisdiction", sa.String(100), nullable=False, index=True),
    sa.Column("plaintiff", sa.String(500), nullable=True),
    sa.Column("defendant", sa.String(500), nullable=True),
    sa.Column("status", sa.String(50), nullable=False, default="ACTIVE", index=True),
    sa.Column(
      "enforcement_level",
      sa.Integer,
      nullable=False,
      default=2,
      comment="1-5 enforcement strictness level",
    ),
    sa.Column(
      "no_slack_mode",
      sa.Boolean,
      nullable=False,
      default=False,
      comment="Zero tolerance mode for deadlines",
    ),
    sa.Column(
      "firm_id",
      sa.String(36),
      nullable=True,
      index=True,
      comment="For multi-tenancy support",
    ),
    sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=sa.func.now()),
  )
  # Foreign key to jurisdiction_rules.jurisdiction
  op.create_foreign_key(
    "fk_matters_jurisdiction",
    "matters",
    "jurisdiction_rules",
    ["jurisdiction"],
    ["jurisdiction"],
  )
  op.create_index("idx_matters_case_court", "matters", ["case_number", "court"])

  # 3. Timeline Events Table
  op.create_table(
    "timeline_events",
    sa.Column("id", sa.String(36), primary_key=True),
    sa.Column(
      "matter_id",
      sa.String(36),
      sa.ForeignKey("matters.id", ondelete="CASCADE"),
      nullable=False,
      index=True,
    ),
    sa.Column(
      "event_type",
      sa.String(100),
      nullable=False,
      index=True,
      comment="E.g., FILING, MOTION, HEARING, RESPONSE_DUE",
    ),
    sa.Column("description", sa.Text, nullable=False),
    sa.Column(
      "trigger_date",
      sa.Date,
      nullable=False,
      comment="Date that triggered this deadline",
    ),
    sa.Column("due_date", sa.Date, nullable=False, index=True),
    sa.Column(
      "color_code",
      sa.String(20),
      nullable=False,
      default="GRAY",
      comment="RED/YELLOW/GREEN/GRAY for urgency visualization",
    ),
    sa.Column(
      "status",
      sa.String(50),
      nullable=False,
      default="PENDING",
      index=True,
      comment="PENDING/COMPLETED/MISSED/CANCELLED",
    ),
    sa.Column(
      "confidence_score",
      sa.Float,
      nullable=True,
      default=1.0,
      comment="ML confidence in deadline calculation",
    ),
    sa.Column(
      "source_ingestion_id",
      sa.String(36),
      nullable=True,
      comment="Reference to email_ingestions.id if auto-parsed",
    ),
    sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=sa.func.now()),
  )
  op.create_index(
    "idx_timeline_events_due_date_status", "timeline_events", ["due_date", "status"]
  )
  op.create_index("idx_timeline_events_color_code", "timeline_events", ["color_code"])
  op.create_index(
    "idx_timeline_events_trigger_date", "timeline_events", ["trigger_date"]
  )

  # 4. Email Ingestions Table
  op.create_table(
    "email_ingestions",
    sa.Column("id", sa.String(36), primary_key=True),
    sa.Column(
      "raw_email",
      sa.Text,
      nullable=False,
      comment="Encrypted or reference to encrypted storage",
    ),
    sa.Column("from_address", sa.String(500), nullable=False, index=True),
    sa.Column("subject", sa.String(1000), nullable=False),
    sa.Column("received_at", sa.DateTime(timezone=True), nullable=False, index=True),
    sa.Column("parsed_case_number", sa.String(200), nullable=True, index=True),
    sa.Column(
      "parsed_events",
      JSONB,
      nullable=True,
      comment="Array of extracted events before timeline insertion",
    ),
    sa.Column(
      "matter_id",
      sa.String(36),
      sa.ForeignKey("matters.id", ondelete="SET NULL"),
      nullable=True,
      index=True,
    ),
    sa.Column(
      "processing_status",
      sa.String(50),
      nullable=False,
      default="PENDING",
      index=True,
      comment="PENDING/PROCESSED/FAILED/REVIEW",
    ),
    sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
    sa.Column("error_message", sa.Text, nullable=True),
    sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=sa.func.now()),
  )
  op.create_index(
    "idx_email_ingestions_status_received",
    "email_ingestions",
    ["processing_status", "received_at"],
  )
  op.create_index("idx_email_ingestions_matter", "email_ingestions", ["matter_id"])

  # 5. Enforcement Configs Table
  op.create_table(
    "enforcement_configs",
    sa.Column("id", sa.String(36), primary_key=True),
    sa.Column(
      "matter_id",
      sa.String(36),
      sa.ForeignKey("matters.id", ondelete="CASCADE"),
      nullable=False,
      unique=True,
      index=True,
      comment="One enforcement config per matter",
    ),
    sa.Column(
      "level",
      sa.Integer,
      nullable=False,
      default=2,
      comment="1=Minimal, 2=Standard, 3=Strict, 4=Maximum, 5=Nuclear",
    ),
    sa.Column("no_slack_mode", sa.Boolean, nullable=False, default=False),
    sa.Column(
      "alert_channels",
      JSONB,
      nullable=False,
      default='["email"]',
      comment="Array of channels: email, sms, slack, teams, webhook",
    ),
    sa.Column(
      "escalation_schedule",
      JSONB,
      nullable=True,
      comment='Array of objects: [{"days_before": 7, "action": "email", "recipients": [...]}]',
    ),
    sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=sa.func.now()),
  )
  op.create_index("idx_enforcement_configs_level", "enforcement_configs", ["level"])

  # 6. Enhance existing Holidays Table - Add recurring column
  op.add_column(
    "holidays",
    sa.Column(
      "recurring",
      sa.Boolean,
      nullable=False,
      default=False,
      server_default="false",
      comment="True for holidays that recur annually",
    ),
  )
  op.create_index("idx_holidays_recurring", "holidays", ["recurring"])

  # Add check constraints for data integrity
  op.execute("""
        ALTER TABLE matters
        ADD CONSTRAINT chk_matters_enforcement_level
        CHECK (enforcement_level >= 1 AND enforcement_level <= 5)
    """)

  op.execute("""
        ALTER TABLE enforcement_configs
        ADD CONSTRAINT chk_enforcement_configs_level
        CHECK (level >= 1 AND level <= 5)
    """)

  op.execute("""
        ALTER TABLE timeline_events
        ADD CONSTRAINT chk_timeline_events_color_code
        CHECK (color_code IN ('RED', 'YELLOW', 'GREEN', 'GRAY', 'BLUE'))
    """)

  op.execute("""
        ALTER TABLE timeline_events
        ADD CONSTRAINT chk_timeline_events_status
        CHECK (status IN ('PENDING', 'COMPLETED', 'MISSED', 'CANCELLED'))
    """)

  op.execute("""
        ALTER TABLE email_ingestions
        ADD CONSTRAINT chk_email_ingestions_processing_status
        CHECK (processing_status IN ('PENDING', 'PROCESSED', 'FAILED', 'REVIEW'))
    """)

  op.execute("""
        ALTER TABLE matters
        ADD CONSTRAINT chk_matters_status
        CHECK (status IN ('ACTIVE', 'CLOSED', 'ARCHIVED', 'ON_HOLD'))
    """)


def downgrade():
  """Drop LawTrack enhancement tables and columns"""

  # Drop check constraints first
  op.execute("ALTER TABLE matters DROP CONSTRAINT IF EXISTS chk_matters_status")
  op.execute(
    "ALTER TABLE email_ingestions DROP CONSTRAINT IF EXISTS chk_email_ingestions_processing_status"
  )
  op.execute(
    "ALTER TABLE timeline_events DROP CONSTRAINT IF EXISTS chk_timeline_events_status"
  )
  op.execute(
    "ALTER TABLE timeline_events DROP CONSTRAINT IF EXISTS chk_timeline_events_color_code"
  )
  op.execute(
    "ALTER TABLE enforcement_configs DROP CONSTRAINT IF EXISTS chk_enforcement_configs_level"
  )
  op.execute(
    "ALTER TABLE matters DROP CONSTRAINT IF EXISTS chk_matters_enforcement_level"
  )

  # Drop tables in reverse order (respecting foreign key dependencies)
  op.drop_table("enforcement_configs")
  op.drop_table("email_ingestions")
  op.drop_table("timeline_events")
  op.drop_table("matters")
  op.drop_table("jurisdiction_rules")

  # Remove enhancement to holidays table
  op.drop_index("idx_holidays_recurring", "holidays")
  op.drop_column("holidays", "recurring")
