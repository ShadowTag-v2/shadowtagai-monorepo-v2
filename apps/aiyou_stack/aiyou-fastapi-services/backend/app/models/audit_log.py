"""Audit log model for compliance tracking"""

import enum
import uuid

from sqlalchemy import JSON, Column, Integer, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base, TimestampMixin


class ActionType(enum.StrEnum):
    """Types of actions that can be audited"""

    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    CONSENT_GRANTED = "consent_granted"
    CONSENT_REVOKED = "consent_revoked"
    DATA_EXPORT = "data_export"
    DATA_DELETION = "data_deletion"
    ACCESS_DENIED = "access_denied"
    COMPLIANCE_CHECK = "compliance_check"


class AuditLog(Base, TimestampMixin):
    """Audit log for tracking all data access and operations"""

    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Who performed the action
    user_id = Column(UUID(as_uuid=True), index=True)
    user_email = Column(String(255), index=True)

    # What action was performed
    action = Column(SQLEnum(ActionType), nullable=False, index=True)
    resource_type = Column(
        String(100), nullable=False, index=True,
    )  # e.g., "user", "consent", "data"
    resource_id = Column(String(255), index=True)

    # Details of the action
    description = Column(Text)
    changes = Column(JSON)  # Store before/after values for updates

    # Context
    ip_address = Column(String(45))  # Anonymized if ANONYMIZE_IP is enabled
    user_agent = Column(String(500))
    request_method = Column(String(10))  # GET, POST, etc.
    request_path = Column(String(500))

    # Result
    status_code = Column(Integer)
    success = Column(String(10), nullable=False)  # "success", "failure", "denied"
    error_message = Column(Text)

    # Compliance metadata
    gdpr_relevant = Column(String(10), default="false")
    ccpa_relevant = Column(String(10), default="false")
    retention_until = Column(String(255))  # When this log can be deleted

    # Performance
    duration_ms = Column(Integer)  # How long the operation took

    def __repr__(self):
        return f"<AuditLog {self.action} on {self.resource_type} by {self.user_email}>"
