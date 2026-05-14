# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
ActiveShield Medical - Database Models
======================================

SQLAlchemy models for persistent audit logging and adverse event tracking.
"""

import uuid

from sqlalchemy import JSON, Boolean, Column, DateTime, Index, Integer, String
from sqlalchemy.sql import func

from src.aiyou.database import Base


class ActiveShieldAuditLog(Base):
    """
    Immutable audit log for all ActiveShield interactions.

    Tracks: Pre-hoc checks, Mid-hoc monitoring, and Post-hoc logging.
    Serves as the legal compliance trail.
    """

    __tablename__ = "activeshield_audit_logs"

    # Identity
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    shield_id = Column(String(64), unique=True, index=True, nullable=False)
    session_id = Column(String(255), index=True, nullable=False)

    # Context
    phase = Column(String(20), nullable=False)  # split from Enum to avoid DB-level enum migration pain
    action = Column(String(32), nullable=False)
    passed = Column(Boolean, nullable=False)

    # Processed Content (Redacted/Sanitized if applicable)
    processed_content = Column(String, nullable=True)  # Can be large text

    # Detailed Data (Stored as JSONB for querying flexibility)
    violations = Column(JSON, default=list)
    warnings = Column(JSON, default=list)
    metadata_ = Column("metadata", JSON, default=dict)  # 'metadata' is reserved in SQLAlchemy Base
    audit_trail = Column(JSON, default=list)  # Text log of decisions

    # Metrics
    processing_time_ms = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (Index("idx_activeshield_session_created", "session_id", "created_at"),)

    def __repr__(self):
        return f"<ActiveShieldAuditLog(id={self.id}, shield_id={self.shield_id}, action={self.action})>"


class ActiveShieldAdverseEvent(Base):
    """
    Registry of critical adverse events and blocked clinical decisions.

    Used for:
    - FDA/Regulatory reporting
    - System safety monitoring
    - Liability exposure tracking
    """

    __tablename__ = "activeshield_adverse_events"

    # Identity
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(255), index=True, nullable=False)
    audit_log_id = Column(String(36), index=True, nullable=True)  # Link to full audit log

    # Event Details
    event_type = Column(String(64), nullable=False)  # e.g., "crisis_intervention", "drug_interaction_block"
    description = Column(String, nullable=False)
    severity = Column(String(32), nullable=False)  # critical, high, moderate

    # Context
    context_snapshot = Column(JSON, default=dict)  # Relevant context at time of event

    # Resolution
    remediated = Column(Boolean, default=False)
    remediation_notes = Column(String, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<ActiveShieldAdverseEvent(id={self.id}, type={self.event_type}, severity={self.severity})>"
