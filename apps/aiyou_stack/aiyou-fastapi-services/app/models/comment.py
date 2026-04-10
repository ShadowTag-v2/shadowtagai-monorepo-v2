"""Comment models for forum posts and other content."""

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship

from app.db.base import Base


class Comment(Base):
    """Comment model for forum posts."""

    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    forum_post_id = Column(Integer, ForeignKey("forum_posts.id", ondelete="CASCADE"), nullable=True)
    author_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    parent_id = Column(
        Integer, ForeignKey("comments.id", ondelete="CASCADE"), nullable=True
    )  # For nested comments

    content = Column(Text, nullable=False)

    # Engagement
    like_count = Column(Integer, default=0)

    # Moderation
    is_edited = Column(Boolean, default=False)
    edited_at = Column(DateTime, nullable=True)
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    forum_post = relationship("ForumPost", back_populates="comments")
    author = relationship("User", back_populates="comments")
    likes = relationship("CommentLike", back_populates="comment", cascade="all, delete-orphan")

    # Self-referential relationship for nested comments
    parent = relationship("Comment", remote_side=[id], backref="replies")


class CommentLike(Base):
    """Comment like model."""

    __tablename__ = "comment_likes"

    id = Column(Integer, primary_key=True, index=True)
    comment_id = Column(Integer, ForeignKey("comments.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    comment = relationship("Comment", back_populates="likes")
    user = relationship("User")
