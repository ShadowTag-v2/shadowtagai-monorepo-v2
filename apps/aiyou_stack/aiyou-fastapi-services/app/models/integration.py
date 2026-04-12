"""Integration models"""

from datetime import datetime
from enum import StrEnum

from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship

from app.db.session import Base


class IntegrationType(StrEnum):
    """Types of integrations"""

    OAUTH2 = "oauth2"
    API_KEY = "api_key"
    BASIC_AUTH = "basic_auth"
    CUSTOM = "custom"


class IntegrationStatus(StrEnum):
    """Integration status"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    PENDING = "pending"


class Integration(Base):
    """Integration configuration model"""

    __tablename__ = "integrations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    provider = Column(String(100), nullable=False, index=True)  # e.g., "github", "google", "stripe"
    type = Column(SQLEnum(IntegrationType), nullable=False)
    status = Column(SQLEnum(IntegrationStatus), default=IntegrationStatus.PENDING)

    # Configuration
    config = Column(JSON, default={})  # Integration-specific configuration
    metadata = Column(JSON, default={})  # Additional metadata

    # API Details
    base_url = Column(String(500), nullable=True)
    api_version = Column(String(50), nullable=True)

    # Retry Configuration
    max_retries = Column(Integer, default=3)
    retry_backoff = Column(Integer, default=2)
    timeout = Column(Integer, default=30)

    # Status tracking
    last_sync_at = Column(DateTime, nullable=True)
    last_error = Column(Text, nullable=True)
    error_count = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="integrations")
    credentials = relationship(
        "IntegrationCredential", back_populates="integration", cascade="all, delete-orphan"
    )
    webhooks = relationship("Webhook", back_populates="integration", cascade="all, delete-orphan")


class IntegrationCredential(Base):
    """Encrypted credentials for integrations"""

    __tablename__ = "integration_credentials"

    id = Column(Integer, primary_key=True, index=True)
    integration_id = Column(Integer, ForeignKey("integrations.id"), nullable=False)

    # Credentials (encrypted in production)
    access_token = Column(Text, nullable=True)
    refresh_token = Column(Text, nullable=True)
    api_key = Column(Text, nullable=True)
    api_secret = Column(Text, nullable=True)

    # OAuth specific
    token_type = Column(String(50), nullable=True)
    scope = Column(Text, nullable=True)
    expires_at = Column(DateTime, nullable=True)

    # Additional credentials
    extra_data = Column(JSON, default={})

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    integration = relationship("Integration", back_populates="credentials")
