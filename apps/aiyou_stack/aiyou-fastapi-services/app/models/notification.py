# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Notification models for user engagement."""

import enum
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship

from app.db.base import Base


class NotificationType(enum.StrEnum):
    """Notification type enumeration."""

    NEW_FOLLOWER = "new_follower"
    NEW_COMMENT = "new_comment"
    NEW_REPLY = "new_reply"
    POST_LIKED = "post_liked"
    COMMENT_LIKED = "comment_liked"
    MENTION = "mention"
    POST_FEATURED = "post_featured"
    BADGE_EARNED = "badge_earned"
    TOPIC_REPLY = "topic_reply"
    SYSTEM = "system"


class Notification(Base):
    """Notification model."""

    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    notification_type = Column(SQLEnum(NotificationType), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=True)

    # Related entities (nullable for flexibility)
    related_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    related_post_id = Column(
        Integer,
        ForeignKey("forum_posts.id", ondelete="SET NULL"),
        nullable=True,
    )
    related_comment_id = Column(
        Integer,
        ForeignKey("comments.id", ondelete="SET NULL"),
        nullable=True,
    )
    related_topic_id = Column(
        Integer,
        ForeignKey("forum_topics.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Link to action
    action_url = Column(String(500), nullable=True)

    # Status
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="notifications")
    related_user = relationship("User", foreign_keys=[related_user_id])
    related_post = relationship("ForumPost")
    related_comment = relationship("Comment")
    related_topic = relationship("ForumTopic")


class NotificationPreference(Base):
    """User notification preferences."""

    __tablename__ = "notification_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    # Email notifications
    email_new_follower = Column(Boolean, default=True)
    email_new_comment = Column(Boolean, default=True)
    email_new_reply = Column(Boolean, default=True)
    email_post_liked = Column(Boolean, default=False)
    email_mention = Column(Boolean, default=True)
    email_digest = Column(Boolean, default=True)

    # In-app notifications
    app_new_follower = Column(Boolean, default=True)
    app_new_comment = Column(Boolean, default=True)
    app_new_reply = Column(Boolean, default=True)
    app_post_liked = Column(Boolean, default=True)
    app_mention = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User")
