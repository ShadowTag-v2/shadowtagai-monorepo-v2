"""Webhook models"""

from datetime import datetime
from enum import StrEnum

from sqlalchemy import JSON, Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship

from app.db.session import Base


class WebhookStatus(StrEnum):
    """Webhook status"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"


class WebhookEventStatus(StrEnum):
    """Webhook event processing status"""

    PENDING = "pending"
    PROCESSING = "processing"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRYING = "retrying"


class Webhook(Base):
    """Webhook configuration model"""

    __tablename__ = "webhooks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    integration_id = Column(Integer, ForeignKey("integrations.id"), nullable=True)

    name = Column(String(255), nullable=False)
    url = Column(String(500), nullable=False)
    secret = Column(String(255), nullable=True)  # For signature verification

    # Configuration
    events = Column(JSON, default=[])  # List of event types to listen for
    headers = Column(JSON, default={})  # Custom headers to send

    # Retry configuration
    max_retries = Column(Integer, default=5)
    retry_delay = Column(Integer, default=5)
    timeout = Column(Integer, default=30)

    # Status
    status = Column(SQLEnum(WebhookStatus), default=WebhookStatus.ACTIVE)
    is_verified = Column(Boolean, default=False)

    # Stats
    total_events = Column(Integer, default=0)
    failed_events = Column(Integer, default=0)
    last_triggered_at = Column(DateTime, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="webhooks")
    integration = relationship("Integration", back_populates="webhooks")
    events_rel = relationship(
        "WebhookEvent",
        back_populates="webhook",
        cascade="all, delete-orphan",
    )


class WebhookEvent(Base):
    """Webhook event queue"""

    __tablename__ = "webhook_events"

    id = Column(Integer, primary_key=True, index=True)
    webhook_id = Column(Integer, ForeignKey("webhooks.id"), nullable=False)

    event_type = Column(String(100), nullable=False, index=True)
    payload = Column(JSON, nullable=False)
    status = Column(SQLEnum(WebhookEventStatus), default=WebhookEventStatus.PENDING, index=True)

    # Processing
    retry_count = Column(Integer, default=0)
    next_retry_at = Column(DateTime, nullable=True)
    last_error = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    processed_at = Column(DateTime, nullable=True)

    # Relationships
    webhook = relationship("Webhook", back_populates="events_rel")
    deliveries = relationship(
        "WebhookDelivery",
        back_populates="event",
        cascade="all, delete-orphan",
    )


class WebhookDelivery(Base):
    """Webhook delivery attempts log"""

    __tablename__ = "webhook_deliveries"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("webhook_events.id"), nullable=False)

    # Request
    request_headers = Column(JSON, default={})
    request_body = Column(JSON, nullable=False)

    # Response
    response_status = Column(Integer, nullable=True)
    response_headers = Column(JSON, default={})
    response_body = Column(Text, nullable=True)

    # Timing
    duration_ms = Column(Integer, nullable=True)

    # Status
    success = Column(Boolean, default=False)
    error_message = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    event = relationship("WebhookEvent", back_populates="deliveries")
