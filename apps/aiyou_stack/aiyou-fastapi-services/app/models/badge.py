"""Badge models for gamification and achievements."""

import enum
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship

from app.db.base import Base


class BadgeCategory(enum.StrEnum):
    """Badge category enumeration."""

    PARTICIPATION = "participation"
    CONTRIBUTION = "contribution"
    EXPERTISE = "expertise"
    MODERATION = "moderation"
    SPECIAL = "special"
    MILESTONE = "milestone"


class BadgeTier(enum.StrEnum):
    """Badge tier enumeration."""

    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"


class Badge(Base):
    """Badge definition model."""

    __tablename__ = "badges"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=False)

    # Badge properties
    category = Column(SQLEnum(BadgeCategory), nullable=False)
    tier = Column(SQLEnum(BadgeTier), nullable=False)
    icon_url = Column(String(500), nullable=True)

    # Requirements
    required_points = Column(Integer, default=0)
    required_posts = Column(Integer, default=0)
    required_comments = Column(Integer, default=0)
    required_likes = Column(Integer, default=0)

    # Visibility
    is_active = Column(Boolean, default=True)
    is_secret = Column(Boolean, default=False)  # Hidden until earned

    # Statistics
    total_awarded = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user_badges = relationship("UserBadge", back_populates="badge")


class UserBadge(Base):
    """User badge assignment model."""

    __tablename__ = "user_badges"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    badge_id = Column(Integer, ForeignKey("badges.id", ondelete="CASCADE"), nullable=False)

    # Award details
    awarded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    progress_at_award = Column(Integer, default=0)

    # Display
    is_featured = Column(Boolean, default=False)  # Show on profile

    # Relationships
    user = relationship("User", back_populates="badges")
    badge = relationship("Badge", back_populates="user_badges")
