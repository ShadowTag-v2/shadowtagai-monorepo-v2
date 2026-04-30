"""User model for analytics tracking"""

import uuid

from sqlalchemy import JSON, Boolean, Column, DateTime, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from src.database import Base


class User(Base):
    """User model for tracking user information and behavior"""

    __tablename__ = "users"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # User identification
    user_id = Column(String(255), unique=True, index=True, nullable=False)
    anonymous_id = Column(String(255), index=True)

    # User properties
    email = Column(String(255), index=True)
    name = Column(String(255))
    hashed_password = Column(String(255))
    properties = Column(JSON, default={})

    # User segments
    segment = Column(String(100), index=True)
    cohort = Column(String(100), index=True)

    # User status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    # Tracking metrics
    first_seen = Column(DateTime(timezone=True), server_default=func.now())
    last_seen = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    event_count = Column(Integer, default=0)
    session_count = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<User(user_id={self.user_id}, email={self.email})>"
