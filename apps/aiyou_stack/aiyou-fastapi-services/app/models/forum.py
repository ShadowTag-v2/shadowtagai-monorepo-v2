"""Forum models for categories, topics, and posts."""

import enum
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship

from app.db.base import Base


class PostStatus(enum.StrEnum):
    """Post status enumeration."""

    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    DELETED = "deleted"


class ForumCategory(Base):
    """Forum category model."""

    __tablename__ = "forum_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    icon = Column(String(50), nullable=True)
    color = Column(String(7), nullable=True)  # Hex color code

    # Ordering and visibility
    order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

    # Moderation
    is_locked = Column(Boolean, default=False)
    requires_approval = Column(Boolean, default=False)

    # Statistics
    total_topics = Column(Integer, default=0)
    total_posts = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    topics = relationship("ForumTopic", back_populates="category", cascade="all, delete-orphan")


class ForumTopic(Base):
    """Forum topic model."""

    __tablename__ = "forum_topics"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(
        Integer, ForeignKey("forum_categories.id", ondelete="CASCADE"), nullable=False
    )
    author_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    title = Column(String(255), nullable=False)
    slug = Column(String(255), nullable=False, index=True)

    # Topic properties
    is_pinned = Column(Boolean, default=False)
    is_locked = Column(Boolean, default=False)
    is_featured = Column(Boolean, default=False)

    # Statistics
    view_count = Column(Integer, default=0)
    reply_count = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_activity_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    category = relationship("ForumCategory", back_populates="topics")
    author = relationship("User", foreign_keys=[author_id])
    posts = relationship("ForumPost", back_populates="topic", cascade="all, delete-orphan")


class ForumPost(Base):
    """Forum post model."""

    __tablename__ = "forum_posts"

    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("forum_topics.id", ondelete="CASCADE"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    content = Column(Text, nullable=False)
    status = Column(SQLEnum(PostStatus), default=PostStatus.PUBLISHED, nullable=False)

    # Moderation
    is_edited = Column(Boolean, default=False)
    edited_at = Column(DateTime, nullable=True)
    is_solution = Column(Boolean, default=False)  # Mark as solution for Q&A topics

    # Engagement
    like_count = Column(Integer, default=0)
    report_count = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    topic = relationship("ForumTopic", back_populates="posts")
    author = relationship("User", back_populates="forum_posts")
    comments = relationship("Comment", back_populates="forum_post", cascade="all, delete-orphan")
    reactions = relationship("Reaction", back_populates="forum_post", cascade="all, delete-orphan")
