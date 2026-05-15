# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Database Models for Zero-Touch Legal Deadline Management
SQLAlchemy ORM models
"""

from datetime import datetime, UTC
from sqlalchemy import Column, String, Integer, Float, Boolean, Date, DateTime, Text, JSON, ForeignKey, Enum as SQLEnum, Index
from sqlalchemy.orm import declarative_base, relationship
import enum

Base = declarative_base()


class JurisdictionType(str, enum.Enum):
    """Jurisdiction types"""

    FEDERAL = "federal"
    STATE = "state"
    LOCAL = "local"
    INTERNATIONAL = "international"


class DeadlineType(str, enum.Enum):
    """Deadline types"""

    FILING = "filing"
    RESPONSE = "response"
    PAYMENT = "payment"
    HEARING = "hearing"
    DISCOVERY = "discovery"
    MOTION = "motion"
    APPEAL = "appeal"
    NOTICE = "notice"
    STATUTE_OF_LIMITATIONS = "statute_of_limitations"
    CONTRACT_OBLIGATION = "contract_obligation"
    COMPLIANCE = "compliance"
    OTHER = "other"


class DeadlineStatus(str, enum.Enum):
    """Deadline status"""

    PENDING = "pending"
    UPCOMING = "upcoming"
    CRITICAL = "critical"
    COMPLETED = "completed"
    MISSED = "missed"
    EXTENDED = "extended"
    CANCELLED = "cancelled"


class DeadlineConfidence(str, enum.Enum):
    """Extraction confidence level"""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNCERTAIN = "uncertain"


class DocumentType(str, enum.Enum):
    """Document types"""

    COURT_ORDER = "court_order"
    COMPLAINT = "complaint"
    SUMMONS = "summons"
    MOTION = "motion"
    NOTICE = "notice"
    CONTRACT = "contract"
    SUBPOENA = "subpoena"
    DISCOVERY_REQUEST = "discovery_request"
    JUDGMENT = "judgment"
    FILING = "filing"
    OTHER = "other"


class LegalDocument(Base):
    """Legal documents uploaded for deadline extraction"""

    __tablename__ = "legal_documents"

    id = Column(String(50), primary_key=True)
    document_type = Column(SQLEnum(DocumentType), nullable=False)
    file_name = Column(String(500), nullable=False)
    file_path = Column(String(1000), nullable=False)
    jurisdiction = Column(String(50), nullable=False)
    case_number = Column(String(200), nullable=True)
    filing_date = Column(Date, nullable=True)
    service_date = Column(Date, nullable=True)
    service_method = Column(String(50), nullable=True)
    extracted_text = Column(Text, nullable=True)
    deadlines_count = Column(Integer, default=0)
    processing_status = Column(String(50), default="pending")
    uploaded_at = Column(DateTime, default=lambda: datetime.now(UTC))
    processed_at = Column(DateTime, nullable=True)
    uploaded_by = Column(String(200), nullable=False)
    metadata = Column(JSON, nullable=True)

    # Relationships
    deadlines = relationship("Deadline", back_populates="document", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index("idx_jurisdiction", "jurisdiction"),
        Index("idx_case_number", "case_number"),
        Index("idx_uploaded_at", "uploaded_at"),
        Index("idx_processing_status", "processing_status"),
    )


class Deadline(Base):
    """Extracted deadlines"""

    __tablename__ = "deadlines"

    id = Column(String(50), primary_key=True)
    document_id = Column(String(50), ForeignKey("legal_documents.id"), nullable=False)
    deadline_type = Column(SQLEnum(DeadlineType), nullable=False)
    deadline_date = Column(Date, nullable=False)
    trigger_date = Column(Date, nullable=True)
    trigger_event = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    jurisdiction = Column(String(50), nullable=False)
    case_number = Column(String(200), nullable=True)
    party_names = Column(JSON, nullable=True)  # List of parties
    confidence = Column(SQLEnum(DeadlineConfidence), nullable=False)
    status = Column(SQLEnum(DeadlineStatus), default=DeadlineStatus.PENDING)
    requires_review = Column(Boolean, default=False)
    review_reason = Column(Text, nullable=True)
    calculation_details = Column(JSON, nullable=True)
    reminder_schedule = Column(JSON, nullable=True)  # List of reminder dates
    assigned_to = Column(String(200), nullable=True)
    extracted_at = Column(DateTime, default=lambda: datetime.now(UTC))
    verified_at = Column(DateTime, nullable=True)
    verified_by = Column(String(200), nullable=True)
    metadata = Column(JSON, nullable=True)

    # Relationships
    document = relationship("LegalDocument", back_populates="deadlines")
    calendar_entries = relationship("CalendarEntry", back_populates="deadline", cascade="all, delete-orphan")
    reminders = relationship("ReminderLog", back_populates="deadline", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index("idx_deadline_date", "deadline_date"),
        Index("idx_jurisdiction", "jurisdiction"),
        Index("idx_case_number", "case_number"),
        Index("idx_status", "status"),
        Index("idx_requires_review", "requires_review"),
        Index("idx_assigned_to", "assigned_to"),
    )


class DeadlineRule(Base):
    """Jurisdiction-specific deadline calculation rules"""

    __tablename__ = "deadline_rules"

    id = Column(String(50), primary_key=True)
    jurisdiction = Column(String(50), nullable=False)
    jurisdiction_type = Column(SQLEnum(JurisdictionType), nullable=False)
    deadline_type = Column(SQLEnum(DeadlineType), nullable=False)
    base_days = Column(Integer, nullable=False)
    exclude_weekends = Column(Boolean, default=True)
    exclude_holidays = Column(Boolean, default=True)
    service_method_additions = Column(JSON, nullable=True)  # Dict of service method -> days
    trigger_event = Column(String(500), nullable=False)
    rule_source = Column(String(500), nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    # Indexes
    __table_args__ = (Index("idx_jurisdiction_type", "jurisdiction", "deadline_type"),)


class CalendarEntry(Base):
    """Calendar synchronization records"""

    __tablename__ = "calendar_entries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    deadline_id = Column(String(50), ForeignKey("deadlines.id"), nullable=False)
    calendar_provider = Column(String(50), nullable=False)
    calendar_id = Column(String(200), nullable=False)
    event_id = Column(String(200), nullable=True)
    synced = Column(Boolean, default=False)
    sync_error = Column(Text, nullable=True)
    last_synced = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))

    # Relationships
    deadline = relationship("Deadline", back_populates="calendar_entries")

    # Indexes
    __table_args__ = (
        Index("idx_deadline_id", "deadline_id"),
        Index("idx_calendar_provider", "calendar_provider"),
    )


class ReminderLog(Base):
    """Reminder notification logs"""

    __tablename__ = "reminder_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    deadline_id = Column(String(50), ForeignKey("deadlines.id"), nullable=False)
    reminder_date = Column(Date, nullable=False)
    days_before_deadline = Column(Integer, nullable=False)
    notification_channels = Column(JSON, nullable=False)  # List of channels used
    recipients = Column(JSON, nullable=False)  # List of recipients
    sent = Column(Boolean, default=False)
    sent_at = Column(DateTime, nullable=True)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))

    # Relationships
    deadline = relationship("Deadline", back_populates="reminders")

    # Indexes
    __table_args__ = (
        Index("idx_reminder_date", "reminder_date"),
        Index("idx_sent", "sent"),
    )


class Holiday(Base):
    """Court holidays by jurisdiction"""

    __tablename__ = "holidays"

    id = Column(Integer, primary_key=True, autoincrement=True)
    jurisdiction = Column(String(50), nullable=False)
    holiday_date = Column(Date, nullable=False)
    holiday_name = Column(String(200), nullable=False)
    year = Column(Integer, nullable=False)

    # Indexes
    __table_args__ = (
        Index("idx_jurisdiction_date", "jurisdiction", "holiday_date"),
        Index("idx_year", "year"),
    )


class AuditLog(Base):
    """Audit trail for all system actions"""

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    action = Column(String(100), nullable=False)
    entity_type = Column(String(50), nullable=False)  # deadline, document, rule, etc.
    entity_id = Column(String(50), nullable=False)
    user_id = Column(String(200), nullable=False)
    changes = Column(JSON, nullable=True)  # Before/after values
    timestamp = Column(DateTime, default=lambda: datetime.now(UTC))
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)

    # Indexes
    __table_args__ = (
        Index("idx_entity", "entity_type", "entity_id"),
        Index("idx_user_id", "user_id"),
        Index("idx_timestamp", "timestamp"),
    )


class MLFeedback(Base):
    """Machine learning feedback for model improvement"""

    __tablename__ = "ml_feedback"

    id = Column(Integer, primary_key=True, autoincrement=True)
    deadline_id = Column(String(50), nullable=False)
    document_id = Column(String(50), nullable=False)
    predicted_date = Column(Date, nullable=False)
    actual_date = Column(Date, nullable=False)
    prediction_confidence = Column(Float, nullable=False)
    was_correct = Column(Boolean, nullable=False)
    correction_reason = Column(Text, nullable=True)
    extraction_method = Column(String(50), nullable=False)
    features = Column(JSON, nullable=True)  # Features used for prediction
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))

    # Indexes
    __table_args__ = (
        Index("idx_was_correct", "was_correct"),
        Index("idx_extraction_method", "extraction_method"),
    )
