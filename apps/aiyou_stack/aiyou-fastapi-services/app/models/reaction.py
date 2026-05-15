"""Reaction models for posts and content."""

import enum
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class ReactionTypeEnum(enum.StrEnum):
    """Reaction type enumeration."""

    LIKE = "like"
    LOVE = "love"
    LAUGH = "laugh"
    WOW = "wow"
    SAD = "sad"
    ANGRY = "angry"
    THUMBS_UP = "thumbs_up"
    THUMBS_DOWN = "thumbs_down"
    FIRE = "fire"
    ROCKET = "rocket"
    EYES = "eyes"
    HEART = "heart"


class ReactionType(Base):
    """Reaction type definition."""

    __tablename__ = "reaction_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    emoji = Column(String(10), nullable=False)
    description = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    order = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    reactions = relationship("Reaction", back_populates="reaction_type")


class Reaction(Base):
    """Reaction model for forum posts."""

    __tablename__ = "reactions"

    id = Column(Integer, primary_key=True, index=True)
    reaction_type_id = Column(
        Integer,
        ForeignKey("reaction_types.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    forum_post_id = Column(Integer, ForeignKey("forum_posts.id", ondelete="CASCADE"), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    reaction_type = relationship("ReactionType", back_populates="reactions")
    user = relationship("User")
    forum_post = relationship("ForumPost", back_populates="reactions")
