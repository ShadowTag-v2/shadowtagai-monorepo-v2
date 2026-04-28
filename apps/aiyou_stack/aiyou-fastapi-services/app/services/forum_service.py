# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Forum service layer.

Extracts all database operations from forum routes
into a proper service/repository pattern.
"""

from datetime import datetime
from math import ceil

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.models.forum import ForumCategory, ForumPost, ForumTopic, PostStatus
from app.models.user import User
from app.schemas.forum import (
    ForumCategoryCreate,
    ForumCategoryUpdate,
    ForumPostCreate,
    ForumPostUpdate,
    ForumTopicCreate,
    ForumTopicUpdate,
)
from app.schemas.user import UserSummary


class ForumService:
    """Service layer for forum operations."""

    # ===== Categories =====

    @staticmethod
    def list_categories(db: Session) -> list[ForumCategory]:
        """List all active forum categories."""
        return (
            db.query(ForumCategory)
            .filter(ForumCategory.is_active)
            .order_by(ForumCategory.order)
            .all()
        )

    @staticmethod
    def get_category(db: Session, category_id: int) -> ForumCategory | None:
        """Get a single category by ID."""
        return db.query(ForumCategory).filter(ForumCategory.id == category_id).first()

    @staticmethod
    def get_category_by_slug(db: Session, slug: str) -> ForumCategory | None:
        """Get a category by slug."""
        return db.query(ForumCategory).filter(ForumCategory.slug == slug).first()

    @staticmethod
    def create_category(db: Session, category_data: ForumCategoryCreate) -> ForumCategory:
        """Create a new forum category."""
        category = ForumCategory(**category_data.model_dump())
        db.add(category)
        db.commit()
        db.refresh(category)
        return category

    @staticmethod
    def update_category(
        db: Session,
        category: ForumCategory,
        category_data: ForumCategoryUpdate,
    ) -> ForumCategory:
        """Update an existing category."""
        for field, value in category_data.model_dump(exclude_unset=True).items():
            setattr(category, field, value)
        db.commit()
        db.refresh(category)
        return category

    # ===== Topics =====

    @staticmethod
    def list_topics(db: Session, category_id: int, page: int = 1, size: int = 20) -> dict:
        """List topics in a category with pagination and author info."""
        query = db.query(ForumTopic).filter(ForumTopic.category_id == category_id)
        total = query.count()

        topics = (
            query.order_by(desc(ForumTopic.is_pinned), desc(ForumTopic.last_activity_at))
            .offset((page - 1) * size)
            .limit(size)
            .all()
        )

        # Enrich with author info
        enriched = []
        for topic in topics:
            author = db.query(User).filter(User.id == topic.author_id).first()
            author_summary = None
            if author and author.profile:
                author_summary = UserSummary(
                    id=author.id,
                    username=author.username,
                    display_name=author.profile.display_name,
                    avatar_url=author.profile.avatar_url,
                    reputation_points=author.profile.reputation_points,
                )
            enriched.append({"topic": topic, "author": author_summary})

        return {
            "items": enriched,
            "total": total,
            "page": page,
            "size": size,
            "pages": ceil(total / size) if total > 0 else 0,
        }

    @staticmethod
    def get_topic(db: Session, topic_id: int) -> ForumTopic | None:
        """Get a topic by ID."""
        return db.query(ForumTopic).filter(ForumTopic.id == topic_id).first()

    @staticmethod
    def create_topic(
        db: Session,
        topic_data: ForumTopicCreate,
        author: User,
        category: ForumCategory,
    ) -> ForumTopic:
        """Create a new topic with initial post."""
        topic = ForumTopic(
            category_id=topic_data.category_id,
            author_id=author.id,
            title=topic_data.title,
            slug=topic_data.slug,
        )
        db.add(topic)
        db.flush()

        initial_post = ForumPost(
            topic_id=topic.id,
            author_id=author.id,
            content=topic_data.initial_post_content,
            status=PostStatus.PUBLISHED,
        )
        db.add(initial_post)

        category.total_topics += 1
        category.total_posts += 1

        if author.profile:
            author.profile.total_posts += 1

        db.commit()
        db.refresh(topic)
        return topic

    @staticmethod
    def update_topic(db: Session, topic: ForumTopic, topic_data: ForumTopicUpdate) -> ForumTopic:
        """Update a topic."""
        for field, value in topic_data.model_dump(exclude_unset=True).items():
            setattr(topic, field, value)
        db.commit()
        db.refresh(topic)
        return topic

    @staticmethod
    def increment_view_count(db: Session, topic: ForumTopic) -> None:
        """Increment topic view count."""
        topic.view_count += 1
        db.commit()

    # ===== Posts =====

    @staticmethod
    def list_posts(db: Session, topic_id: int, page: int = 1, size: int = 20) -> dict:
        """List posts in a topic with pagination and author info."""
        query = db.query(ForumPost).filter(
            ForumPost.topic_id == topic_id,
            ForumPost.status == PostStatus.PUBLISHED,
        )
        total = query.count()

        posts = query.order_by(ForumPost.created_at).offset((page - 1) * size).limit(size).all()

        enriched = []
        for post in posts:
            author = db.query(User).filter(User.id == post.author_id).first()
            author_summary = None
            if author and author.profile:
                author_summary = UserSummary(
                    id=author.id,
                    username=author.username,
                    display_name=author.profile.display_name,
                    avatar_url=author.profile.avatar_url,
                    reputation_points=author.profile.reputation_points,
                )
            enriched.append({"post": post, "author": author_summary})

        return {
            "items": enriched,
            "total": total,
            "page": page,
            "size": size,
            "pages": ceil(total / size) if total > 0 else 0,
        }

    @staticmethod
    def get_post(db: Session, post_id: int) -> ForumPost | None:
        """Get a post by ID."""
        return db.query(ForumPost).filter(ForumPost.id == post_id).first()

    @staticmethod
    def create_post(
        db: Session,
        post_data: ForumPostCreate,
        author: User,
    ) -> ForumPost:
        """Create a new forum post."""
        topic = db.query(ForumTopic).filter(ForumTopic.id == post_data.topic_id).first()
        if not topic:
            raise ValueError("Topic not found")

        post = ForumPost(
            topic_id=post_data.topic_id,
            author_id=author.id,
            content=post_data.content,
            status=PostStatus.PUBLISHED,
        )
        db.add(post)

        topic.reply_count += 1
        topic.last_activity_at = datetime.utcnow()

        category = db.query(ForumCategory).filter(ForumCategory.id == topic.category_id).first()
        if category:
            category.total_posts += 1

        if author.profile:
            author.profile.total_posts += 1

        db.commit()
        db.refresh(post)
        return post

    @staticmethod
    def update_post(db: Session, post: ForumPost, post_data: ForumPostUpdate) -> ForumPost:
        """Update a forum post."""
        post.content = post_data.content
        post.is_edited = True
        post.edited_at = datetime.utcnow()

        if post_data.is_solution is not None:
            post.is_solution = post_data.is_solution

        db.commit()
        db.refresh(post)
        return post

    @staticmethod
    def soft_delete_post(db: Session, post: ForumPost) -> None:
        """Soft-delete a forum post."""
        post.status = PostStatus.DELETED
        db.commit()
