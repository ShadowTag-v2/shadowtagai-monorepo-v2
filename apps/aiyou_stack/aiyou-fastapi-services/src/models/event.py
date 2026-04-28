# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Event model for analytics tracking"""

import uuid

from sqlalchemy import JSON, Column, DateTime, Float, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from src.database import Base


class Event(Base):
    """Event model for tracking all user events and interactions"""

    __tablename__ = "events"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Event identification
    event_name = Column(String(255), index=True, nullable=False)
    event_type = Column(String(100), index=True)  # page_view, click, conversion, etc.

    # User identification
    user_id = Column(String(255), index=True)
    anonymous_id = Column(String(255), index=True)
    session_id = Column(String(255), index=True)

    # Event properties
    properties = Column(JSON, default={})

    # Page/screen information
    page_url = Column(String(2048))
    page_title = Column(String(500))
    referrer = Column(String(2048))

    # Device and browser
    user_agent = Column(String(500))
    device_type = Column(String(50))  # mobile, tablet, desktop
    browser = Column(String(100))
    os = Column(String(100))

    # Location
    country = Column(String(100))
    region = Column(String(100))
    city = Column(String(100))
    ip_address = Column(String(45))

    # Campaign tracking
    utm_source = Column(String(255))
    utm_medium = Column(String(255))
    utm_campaign = Column(String(255))
    utm_term = Column(String(255))
    utm_content = Column(String(255))

    # Value tracking
    revenue = Column(Float)
    currency = Column(String(10))

    # Timestamps
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Indexes for common queries
    __table_args__ = (
        Index("idx_event_user_timestamp", "user_id", "timestamp"),
        Index("idx_event_name_timestamp", "event_name", "timestamp"),
        Index("idx_event_session", "session_id", "timestamp"),
    )

    def __repr__(self):
        return f"<Event(event_name={self.event_name}, user_id={self.user_id}, timestamp={self.timestamp})>"
