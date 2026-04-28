# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Database models for email automation"""

import enum
from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from .base import Base


class EmailStatus(enum.StrEnum):
    """Email status enumeration"""

    PENDING = "pending"
    SCHEDULED = "scheduled"
    SENDING = "sending"
    SENT = "sent"
    FAILED = "failed"
    BOUNCED = "bounced"
    DELIVERED = "delivered"
    OPENED = "opened"
    CLICKED = "clicked"


class FlowType(enum.StrEnum):
    """Email flow type enumeration"""

    WELCOME = "welcome"
    REENGAGEMENT = "reengagement"
    TRANSACTIONAL = "transactional"
    DRIP_CAMPAIGN = "drip_campaign"
    NEWSLETTER = "newsletter"


class Recipient(Base):
    """Email recipient model"""

    __tablename__ = "recipients"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    metadata = Column(JSON, default={})
    subscribed = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    emails = relationship("Email", back_populates="recipient")
    flow_enrollments = relationship("FlowEnrollment", back_populates="recipient")


class EmailTemplate(Base):
    """Email template model"""

    __tablename__ = "email_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True, nullable=False)
    subject = Column(String(500), nullable=False)
    body_html = Column(Text, nullable=False)
    body_text = Column(Text)
    variables = Column(JSON, default=[])  # List of variable names
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    emails = relationship("Email", back_populates="template")


class EmailFlow(Base):
    """Email flow/campaign model"""

    __tablename__ = "email_flows"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True, nullable=False)
    description = Column(Text)
    flow_type = Column(Enum(FlowType), nullable=False)
    active = Column(Boolean, default=True)
    config = Column(JSON, default={})  # Flow-specific configuration
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    steps = relationship("FlowStep", back_populates="flow", cascade="all, delete-orphan")
    enrollments = relationship("FlowEnrollment", back_populates="flow")


class FlowStep(Base):
    """Email flow step model"""

    __tablename__ = "flow_steps"

    id = Column(Integer, primary_key=True, index=True)
    flow_id = Column(Integer, ForeignKey("email_flows.id"), nullable=False)
    template_id = Column(Integer, ForeignKey("email_templates.id"), nullable=False)
    step_order = Column(Integer, nullable=False)
    delay_days = Column(Integer, default=0)
    delay_hours = Column(Integer, default=0)
    delay_minutes = Column(Integer, default=0)
    conditions = Column(JSON, default={})  # Conditions for sending this step
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    flow = relationship("EmailFlow", back_populates="steps")
    template = relationship("EmailTemplate")


class FlowEnrollment(Base):
    """Track recipient enrollment in email flows"""

    __tablename__ = "flow_enrollments"

    id = Column(Integer, primary_key=True, index=True)
    flow_id = Column(Integer, ForeignKey("email_flows.id"), nullable=False)
    recipient_id = Column(Integer, ForeignKey("recipients.id"), nullable=False)
    current_step = Column(Integer, default=0)
    enrolled_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    active = Column(Boolean, default=True)

    # Relationships
    flow = relationship("EmailFlow", back_populates="enrollments")
    recipient = relationship("Recipient", back_populates="flow_enrollments")


class Email(Base):
    """Individual email model"""

    __tablename__ = "emails"

    id = Column(Integer, primary_key=True, index=True)
    recipient_id = Column(Integer, ForeignKey("recipients.id"), nullable=False)
    template_id = Column(Integer, ForeignKey("email_templates.id"), nullable=True)
    subject = Column(String(500), nullable=False)
    body_html = Column(Text, nullable=False)
    body_text = Column(Text)
    status = Column(Enum(EmailStatus), default=EmailStatus.PENDING, index=True)
    scheduled_at = Column(DateTime, nullable=True)
    sent_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    opened_at = Column(DateTime, nullable=True)
    clicked_at = Column(DateTime, nullable=True)
    failed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    metadata = Column(JSON, default={})
    tracking_id = Column(String(255), unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    recipient = relationship("Recipient", back_populates="emails")
    template = relationship("EmailTemplate", back_populates="emails")
    analytics = relationship("EmailAnalytics", back_populates="email", uselist=False)
    events = relationship("EmailEvent", back_populates="email")


class EmailAnalytics(Base):
    """Email analytics and metrics"""

    __tablename__ = "email_analytics"

    id = Column(Integer, primary_key=True, index=True)
    email_id = Column(Integer, ForeignKey("emails.id"), unique=True, nullable=False)
    open_count = Column(Integer, default=0)
    click_count = Column(Integer, default=0)
    first_opened_at = Column(DateTime, nullable=True)
    last_opened_at = Column(DateTime, nullable=True)
    first_clicked_at = Column(DateTime, nullable=True)
    last_clicked_at = Column(DateTime, nullable=True)
    user_agent = Column(String(500))
    ip_address = Column(String(50))
    location = Column(JSON, default={})

    # Relationships
    email = relationship("Email", back_populates="analytics")


class EmailEvent(Base):
    """Email event tracking"""

    __tablename__ = "email_events"

    id = Column(Integer, primary_key=True, index=True)
    email_id = Column(Integer, ForeignKey("emails.id"), nullable=False)
    event_type = Column(String(50), index=True, nullable=False)  # open, click, bounce, etc.
    event_data = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    email = relationship("Email", back_populates="events")


class CampaignMetrics(Base):
    """Aggregate campaign/flow metrics"""

    __tablename__ = "campaign_metrics"

    id = Column(Integer, primary_key=True, index=True)
    flow_id = Column(Integer, ForeignKey("email_flows.id"), nullable=True)
    date = Column(DateTime, default=datetime.utcnow, index=True)
    emails_sent = Column(Integer, default=0)
    emails_delivered = Column(Integer, default=0)
    emails_opened = Column(Integer, default=0)
    emails_clicked = Column(Integer, default=0)
    emails_bounced = Column(Integer, default=0)
    emails_failed = Column(Integer, default=0)
    open_rate = Column(Float, default=0.0)
    click_rate = Column(Float, default=0.0)
    bounce_rate = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    flow = relationship("EmailFlow")
