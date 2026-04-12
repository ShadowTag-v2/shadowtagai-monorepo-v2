"""
User authentication and profile models.

Handles user accounts, roles, sessions, and authentication tokens.
"""

import uuid
from enum import StrEnum

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database import Base


class UserRole(StrEnum):
    """User role enumeration."""

    ADMIN = "admin"
    CREATOR = "creator"
    SUBSCRIBER = "subscriber"
    MERCHANT = "merchant"
    DEVELOPER = "developer"


class User(Base):
    """
    User account model.

    Tracks user authentication, profile, and subscription status across all services.
    """

    __tablename__ = "users"

    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Authentication
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.SUBSCRIBER, nullable=False)

    # Profile
    full_name = Column(String(200))
    avatar_url = Column(String(500))
    bio = Column(Text)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login_at = Column(DateTime(timezone=True))

    # Subscription & billing
    subscription_tier = Column(String(50))  # free, basic, premium, family
    subscription_expires_at = Column(DateTime(timezone=True))
    lifetime_value_cents = Column(Integer, default=0)  # Revenue tracking

    # Relationships
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    ingestion_jobs = relationship(
        "IngestionJob", back_populates="user", cascade="all, delete-orphan"
    )
    creator_profile = relationship("Creator", back_populates="user", uselist=False)
    subscriptions = relationship("Subscription", back_populates="user")
    orders = relationship("Order", back_populates="user")
    carts = relationship("Cart", back_populates="user")
    game_sessions = relationship("GameSession", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"


class UserSession(Base):
    """
    User session model for tracking active logins.

    Supports multiple concurrent sessions per user (multi-device).
    """

    __tablename__ = "user_sessions"

    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Foreign keys
    user_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Session data
    refresh_token = Column(String(500), unique=True, index=True, nullable=False)
    access_token_jti = Column(String(100), unique=True, index=True)  # JWT ID for access token
    ip_address = Column(String(45))  # IPv4 or IPv6
    user_agent = Column(String(500))
    device_id = Column(String(100), index=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    last_activity_at = Column(DateTime(timezone=True), server_default=func.now())

    # Status
    is_revoked = Column(Boolean, default=False, nullable=False)

    # Relationships
    user = relationship("User", back_populates="sessions")

    def __repr__(self):
        return f"<UserSession(id={self.id}, user_id={self.user_id}, expires_at={self.expires_at})>"


class IngestionJob(Base):
    """Placeholder model for ingestion jobs linked to a user."""

    __tablename__ = "ingestion_jobs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    job_type = Column(String(50))
    status = Column(String(20))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="ingestion_jobs")
