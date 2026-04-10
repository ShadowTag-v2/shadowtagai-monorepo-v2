"""Data retention policy model for compliance"""

import enum
import uuid

from sqlalchemy import Boolean, Column, Integer, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base, TimestampMixin


class DataCategory(enum.StrEnum):
    """Categories of data subject to retention policies"""

    PERSONAL_DATA = "personal_data"
    FINANCIAL_DATA = "financial_data"
    HEALTH_DATA = "health_data"
    BIOMETRIC_DATA = "biometric_data"
    LOCATION_DATA = "location_data"
    BEHAVIORAL_DATA = "behavioral_data"
    COMMUNICATION_DATA = "communication_data"
    AUDIT_LOGS = "audit_logs"
    CONSENT_RECORDS = "consent_records"
    ANALYTICS_DATA = "analytics_data"
    MARKETING_DATA = "marketing_data"
    BACKUP_DATA = "backup_data"


class DeletionRule(enum.StrEnum):
    """Rules for data deletion"""

    AUTO_DELETE = "auto_delete"  # Automatically delete after retention period
    ANONYMIZE = "anonymize"  # Anonymize instead of delete
    ARCHIVE = "archive"  # Move to archive storage
    MANUAL_REVIEW = "manual_review"  # Require manual review before deletion
    LEGAL_HOLD = "legal_hold"  # Cannot be deleted due to legal reasons


class DataRetentionPolicy(Base, TimestampMixin):
    """Define data retention policies for compliance"""

    __tablename__ = "data_retention_policies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Policy identification
    policy_name = Column(String(255), nullable=False, unique=True, index=True)
    data_category = Column(SQLEnum(DataCategory), nullable=False, index=True)

    # Retention settings
    retention_days = Column(Integer, nullable=False)  # How long to keep data
    deletion_rule = Column(SQLEnum(DeletionRule), nullable=False)

    # Status
    is_active = Column(Boolean, nullable=False, default=True)
    is_required = Column(Boolean, nullable=False, default=False)  # Required by law

    # Legal basis
    legal_requirement = Column(String(255))  # e.g., "GDPR Article 17", "CCPA 1798.105"
    jurisdiction = Column(String(100))  # e.g., "EU", "California", "Global"

    # Policy details
    description = Column(Text)
    purpose = Column(Text)  # Why this data is retained

    # Compliance
    gdpr_compliant = Column(Boolean, default=True)
    ccpa_compliant = Column(Boolean, default=True)

    # Review and audit
    last_reviewed_at = Column(String(255))
    review_frequency_days = Column(Integer, default=365)  # Review annually
    reviewed_by = Column(String(255))

    # Exceptions
    exceptions = Column(Text)  # When this policy doesn't apply
    override_allowed = Column(Boolean, default=False)

    # Metadata
    applies_to_tables = Column(Text)  # Which database tables this affects
    applies_to_files = Column(Text)  # Which file types this affects
    notes = Column(Text)

    def __repr__(self):
        return f"<DataRetentionPolicy {self.policy_name}>"

    def is_due_for_review(self) -> bool:
        """Check if policy is due for review"""
        if not self.last_reviewed_at:
            return True

        from datetime import datetime, timedelta

        last_review = datetime.fromisoformat(self.last_reviewed_at)
        next_review = last_review + timedelta(days=self.review_frequency_days)
        return datetime.utcnow() >= next_review
