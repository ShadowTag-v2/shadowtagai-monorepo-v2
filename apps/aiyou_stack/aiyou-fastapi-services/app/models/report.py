"""Report models for content moderation."""

import enum
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship

from app.db.base import Base


class ReportReason(enum.StrEnum):
    """Report reason enumeration."""

    SPAM = "spam"
    HARASSMENT = "harassment"
    HATE_SPEECH = "hate_speech"
    INAPPROPRIATE_CONTENT = "inappropriate_content"
    MISINFORMATION = "misinformation"
    COPYRIGHT = "copyright"
    OTHER = "other"


class ReportStatus(enum.StrEnum):
    """Report status enumeration."""

    PENDING = "pending"
    REVIEWING = "reviewing"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


class Report(Base):
    """Content report model for moderation."""

    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    reporter_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Reported content (one of these will be set)
    reported_post_id = Column(
        Integer, ForeignKey("forum_posts.id", ondelete="CASCADE"), nullable=True,
    )
    reported_comment_id = Column(
        Integer, ForeignKey("comments.id", ondelete="CASCADE"), nullable=True,
    )
    reported_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)

    # Report details
    reason = Column(SQLEnum(ReportReason), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(SQLEnum(ReportStatus), default=ReportStatus.PENDING, nullable=False)

    # Moderation
    moderator_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    moderator_notes = Column(Text, nullable=True)
    resolved_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    reporter = relationship("User", foreign_keys=[reporter_id])
    reported_post = relationship("ForumPost")
    reported_comment = relationship("Comment")
    reported_user = relationship("User", foreign_keys=[reported_user_id])
    moderator = relationship("User", foreign_keys=[moderator_id])
