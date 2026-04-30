"""User consent model for GDPR/CCPA compliance"""

import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base, TimestampMixin


class ConsentType(enum.StrEnum):
    """Types of consent that can be tracked"""

    NECESSARY = "necessary"  # Required for basic functionality
    FUNCTIONAL = "functional"  # Enhanced functionality
    ANALYTICS = "analytics"  # Usage analytics
    MARKETING = "marketing"  # Marketing communications
    ADVERTISING = "advertising"  # Personalized ads
    THIRD_PARTY = "third_party"  # Third-party data sharing
    PROFILING = "profiling"  # Automated decision making
    GEOLOCATION = "geolocation"  # Location tracking
    BIOMETRIC = "biometric"  # Biometric data


class ConsentMethod(enum.StrEnum):
    """How consent was obtained"""

    EXPLICIT_CHECKBOX = "explicit_checkbox"
    OPT_IN_BUTTON = "opt_in_button"
    VERBAL = "verbal"
    WRITTEN = "written"
    IMPLIED = "implied"
    COOKIE_BANNER = "cookie_banner"


class UserConsent(Base, TimestampMixin):
    """Track user consent for GDPR/CCPA compliance"""

    __tablename__ = "user_consents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # User identification
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    user_email = Column(String(255), index=True)

    # Consent details
    consent_type = Column(SQLEnum(ConsentType), nullable=False, index=True)
    consent_method = Column(SQLEnum(ConsentMethod), nullable=False)

    # Status
    is_granted = Column(Boolean, nullable=False, default=True)
    is_active = Column(Boolean, nullable=False, default=True)

    # Timing
    granted_at = Column(String(255), nullable=False)
    expires_at = Column(String(255))  # When consent expires (if applicable)
    revoked_at = Column(String(255))  # When consent was revoked

    # Context
    ip_address = Column(String(45))  # Where consent was given
    user_agent = Column(String(500))
    consent_text = Column(Text)  # The exact text the user agreed to
    consent_version = Column(String(50))  # Version of terms/privacy policy

    # Legal basis (GDPR Article 6)
    legal_basis = Column(String(100))  # consent, contract, legal_obligation, etc.

    # Compliance
    gdpr_applies = Column(Boolean, default=False)
    ccpa_applies = Column(Boolean, default=False)

    # Additional metadata
    purpose = Column(Text)  # Purpose of data processing
    data_categories = Column(Text)  # What data is covered
    third_parties = Column(Text)  # Third parties data may be shared with
    notes = Column(Text)

    def __repr__(self):
        return f"<UserConsent {self.consent_type} for user {self.user_id}>"

    def is_expired(self) -> bool:
        """Check if consent has expired"""
        if not self.expires_at:
            return False
        return datetime.fromisoformat(self.expires_at) < datetime.utcnow()

    def is_valid(self) -> bool:
        """Check if consent is valid and active"""
        return self.is_granted and self.is_active and not self.revoked_at and not self.is_expired()
