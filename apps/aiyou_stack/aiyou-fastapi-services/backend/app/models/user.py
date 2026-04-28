# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""User model"""

import uuid

from sqlalchemy import Boolean, Column, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    """User model for managing user accounts"""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))

    # User status
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)

    # Privacy & Compliance
    ip_address = Column(String(45))  # Supports IPv6
    country = Column(String(2))  # ISO country code
    gdpr_applies = Column(Boolean, default=False)
    ccpa_applies = Column(Boolean, default=False)

    # User preferences
    marketing_consent = Column(Boolean, default=False)
    analytics_consent = Column(Boolean, default=False)

    # Metadata
    last_login_at = Column(String(255))
    login_count = Column(Integer, default=0)
    notes = Column(Text)

    def __repr__(self):
        return f"<User {self.email}>"
