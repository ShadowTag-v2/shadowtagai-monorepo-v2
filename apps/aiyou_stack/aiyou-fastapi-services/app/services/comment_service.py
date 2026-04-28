# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Comment service layer.

Extracts all database operations from comment routes
into a proper service/repository pattern.
"""

from datetime import datetime
from math import ceil

from sqlalchemy.orm import Session

from app.models.comment import Comment, CommentLike
from app.models.user import User
from app.schemas.user import UserSummary


class CommentService:
    """Service layer for comment operations."""

    @staticmethod
    def create_comment(
        db: Session,
        forum_post_id: int,
        author: User,
        content: str,
        parent_id: int | None = None,
    ) -> Comment:
        """Create a new comment."""
        comment = Comment(
            forum_post_id=forum_post_id,
            author_id=author.id,
            parent_id=parent_id,
            content=content,
        )
        db.add(comment)

        if author.profile:
            author.profile.total_comments += 1

        db.commit()
        db.refresh(comment)
        return comment

    @staticmethod
    def list_comments_for_post(db: Session, post_id: int, page: int = 1, size: int = 20) -> dict:
        """List comments for a post with author info and pagination."""
        query = db.query(Comment).filter(Comment.forum_post_id == post_id, not Comment.is_deleted)
        total = query.count()

        comments = query.order_by(Comment.created_at).offset((page - 1) * size).limit(size).all()

        enriched = []
        for comment in comments:
            author = db.query(User).filter(User.id == comment.author_id).first()
            author_summary = None
            if author and author.profile:
                author_summary = UserSummary(
                    id=author.id,
                    username=author.username,
                    display_name=author.profile.display_name,
                    avatar_url=author.profile.avatar_url,
                    reputation_points=author.profile.reputation_points,
                )
            enriched.append({"comment": comment, "author": author_summary})

        return {
            "items": enriched,
            "total": total,
            "page": page,
            "size": size,
            "pages": ceil(total / size) if total > 0 else 0,
        }

    @staticmethod
    def get_comment(db: Session, comment_id: int) -> Comment | None:
        """Get a comment by ID."""
        return db.query(Comment).filter(Comment.id == comment_id).first()

    @staticmethod
    def update_comment(db: Session, comment: Comment, content: str) -> Comment:
        """Update a comment's content."""
        comment.content = content
        comment.is_edited = True
        comment.edited_at = datetime.utcnow()
        db.commit()
        db.refresh(comment)
        return comment

    @staticmethod
    def soft_delete_comment(db: Session, comment: Comment) -> None:
        """Soft-delete a comment."""
        comment.is_deleted = True
        comment.deleted_at = datetime.utcnow()
        db.commit()

    @staticmethod
    def like_comment(db: Session, comment_id: int, user_id: int) -> None:
        """Like a comment. Raises ValueError if already liked."""
        existing = (
            db.query(CommentLike)
            .filter(CommentLike.comment_id == comment_id, CommentLike.user_id == user_id)
            .first()
        )
        if existing:
            raise ValueError("Comment already liked")

        like = CommentLike(comment_id=comment_id, user_id=user_id)
        db.add(like)

        comment = db.query(Comment).filter(Comment.id == comment_id).first()
        if comment:
            comment.like_count += 1

        db.commit()

    @staticmethod
    def unlike_comment(db: Session, comment_id: int, user_id: int) -> None:
        """Unlike a comment. Raises ValueError if not liked."""
        like = (
            db.query(CommentLike)
            .filter(CommentLike.comment_id == comment_id, CommentLike.user_id == user_id)
            .first()
        )
        if not like:
            raise ValueError("Like not found")

        db.delete(like)

        comment = db.query(Comment).filter(Comment.id == comment_id).first()
        if comment:
            comment.like_count = max(0, comment.like_count - 1)

        db.commit()
