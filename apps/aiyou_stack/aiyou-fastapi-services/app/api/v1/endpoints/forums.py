"""Forum endpoints for categories, topics, and posts."""

from math import ceil

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.core.security import get_current_active_user, get_current_superuser
from app.db.session import get_db
from app.models.forum import ForumCategory, ForumPost, ForumTopic, PostStatus
from app.models.user import User
from app.schemas.forum import (
    ForumCategoryCreate,
    ForumCategoryResponse,
    ForumCategoryUpdate,
    ForumPostCreate,
    ForumPostListResponse,
    ForumPostResponse,
    ForumPostUpdate,
    ForumTopicCreate,
    ForumTopicListResponse,
    ForumTopicResponse,
    ForumTopicUpdate,
)
from app.schemas.user import UserSummary

router = APIRouter()


# ===== Categories =====


@router.get("/categories", response_model=list[ForumCategoryResponse])
async def list_categories(db: Session = Depends(get_db)):
    """List all forum categories."""
    categories = (
        db.query(ForumCategory).filter(ForumCategory.is_active).order_by(ForumCategory.order).all()
    )
    return categories


@router.post(
    "/categories", response_model=ForumCategoryResponse, status_code=status.HTTP_201_CREATED
)
async def create_category(
    category_data: ForumCategoryCreate,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db),
):
    """Create a new forum category (admin only)."""
    # Check if slug exists
    if db.query(ForumCategory).filter(ForumCategory.slug == category_data.slug).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Category slug already exists"
        )

    category = ForumCategory(**category_data.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.get("/categories/{category_id}", response_model=ForumCategoryResponse)
async def get_category(category_id: int, db: Session = Depends(get_db)):
    """Get a forum category."""
    category = db.query(ForumCategory).filter(ForumCategory.id == category_id).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return category


@router.put("/categories/{category_id}", response_model=ForumCategoryResponse)
async def update_category(
    category_id: int,
    category_data: ForumCategoryUpdate,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db),
):
    """Update a forum category (admin only)."""
    category = db.query(ForumCategory).filter(ForumCategory.id == category_id).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    for field, value in category_data.model_dump(exclude_unset=True).items():
        setattr(category, field, value)

    db.commit()
    db.refresh(category)
    return category


# ===== Topics =====


@router.get("/categories/{category_id}/topics", response_model=ForumTopicListResponse)
async def list_topics(
    category_id: int, db: Session = Depends(get_db), page: int = 1, size: int = 20
):
    """List topics in a category."""
    # Verify category exists
    category = db.query(ForumCategory).filter(ForumCategory.id == category_id).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    # Get topics with pagination
    query = db.query(ForumTopic).filter(ForumTopic.category_id == category_id)
    total = query.count()

    topics = (
        query.order_by(desc(ForumTopic.is_pinned), desc(ForumTopic.last_activity_at))
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )

    # Format response with author info
    topic_responses = []
    for topic in topics:
        author = db.query(User).filter(User.id == topic.author_id).first()
        topic_dict = ForumTopicResponse.model_validate(topic)
        if author and author.profile:
            topic_dict.author = UserSummary(
                id=author.id,
                username=author.username,
                display_name=author.profile.display_name,
                avatar_url=author.profile.avatar_url,
                reputation_points=author.profile.reputation_points,
            )
        topic_responses.append(topic_dict)

    return ForumTopicListResponse(
        items=topic_responses,
        total=total,
        page=page,
        size=size,
        pages=ceil(total / size) if total > 0 else 0,
    )


@router.post("/topics", response_model=ForumTopicResponse, status_code=status.HTTP_201_CREATED)
async def create_topic(
    topic_data: ForumTopicCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create a new forum topic with initial post."""
    # Verify category exists
    category = db.query(ForumCategory).filter(ForumCategory.id == topic_data.category_id).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    if category.is_locked:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Category is locked")

    # Create topic
    topic = ForumTopic(
        category_id=topic_data.category_id,
        author_id=current_user.id,
        title=topic_data.title,
        slug=topic_data.slug,
    )
    db.add(topic)
    db.flush()

    # Create initial post
    initial_post = ForumPost(
        topic_id=topic.id,
        author_id=current_user.id,
        content=topic_data.initial_post_content,
        status=PostStatus.PUBLISHED,
    )
    db.add(initial_post)

    # Update category stats
    category.total_topics += 1
    category.total_posts += 1

    # Update user profile stats
    if current_user.profile:
        current_user.profile.total_posts += 1

    db.commit()
    db.refresh(topic)
    return topic


@router.get("/topics/{topic_id}", response_model=ForumTopicResponse)
async def get_topic(topic_id: int, db: Session = Depends(get_db)):
    """Get a forum topic."""
    topic = db.query(ForumTopic).filter(ForumTopic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found")

    # Increment view count
    topic.view_count += 1
    db.commit()

    return topic


@router.put("/topics/{topic_id}", response_model=ForumTopicResponse)
async def update_topic(
    topic_id: int,
    topic_data: ForumTopicUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Update a forum topic."""
    topic = db.query(ForumTopic).filter(ForumTopic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found")

    # Check permissions (author or superuser)
    if topic.author_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this topic"
        )

    for field, value in topic_data.model_dump(exclude_unset=True).items():
        setattr(topic, field, value)

    db.commit()
    db.refresh(topic)
    return topic


# ===== Posts =====


@router.get("/topics/{topic_id}/posts", response_model=ForumPostListResponse)
async def list_posts(topic_id: int, db: Session = Depends(get_db), page: int = 1, size: int = 20):
    """List posts in a topic."""
    # Verify topic exists
    topic = db.query(ForumTopic).filter(ForumTopic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found")

    # Get posts with pagination
    query = db.query(ForumPost).filter(
        ForumPost.topic_id == topic_id, ForumPost.status == PostStatus.PUBLISHED
    )
    total = query.count()

    posts = query.order_by(ForumPost.created_at).offset((page - 1) * size).limit(size).all()

    # Format response with author info
    post_responses = []
    for post in posts:
        author = db.query(User).filter(User.id == post.author_id).first()
        post_dict = ForumPostResponse.model_validate(post)
        if author and author.profile:
            post_dict.author = UserSummary(
                id=author.id,
                username=author.username,
                display_name=author.profile.display_name,
                avatar_url=author.profile.avatar_url,
                reputation_points=author.profile.reputation_points,
            )
        post_responses.append(post_dict)

    return ForumPostListResponse(
        items=post_responses,
        total=total,
        page=page,
        size=size,
        pages=ceil(total / size) if total > 0 else 0,
    )


@router.post("/posts", response_model=ForumPostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    post_data: ForumPostCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create a new forum post."""
    # Verify topic exists
    topic = db.query(ForumTopic).filter(ForumTopic.id == post_data.topic_id).first()
    if not topic:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found")

    if topic.is_locked:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Topic is locked")

    # Create post
    post = ForumPost(
        topic_id=post_data.topic_id,
        author_id=current_user.id,
        content=post_data.content,
        status=PostStatus.PUBLISHED,
    )
    db.add(post)

    # Update topic stats
    topic.reply_count += 1
    from datetime import datetime

    topic.last_activity_at = datetime.utcnow()

    # Update category stats
    category = db.query(ForumCategory).filter(ForumCategory.id == topic.category_id).first()
    if category:
        category.total_posts += 1

    # Update user profile stats
    if current_user.profile:
        current_user.profile.total_posts += 1

    db.commit()
    db.refresh(post)
    return post


@router.get("/posts/{post_id}", response_model=ForumPostResponse)
async def get_post(post_id: int, db: Session = Depends(get_db)):
    """Get a forum post."""
    post = db.query(ForumPost).filter(ForumPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post


@router.put("/posts/{post_id}", response_model=ForumPostResponse)
async def update_post(
    post_id: int,
    post_data: ForumPostUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Update a forum post."""
    post = db.query(ForumPost).filter(ForumPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    # Check permissions (author or superuser)
    if post.author_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this post"
        )

    # Update content
    post.content = post_data.content
    post.is_edited = True
    from datetime import datetime

    post.edited_at = datetime.utcnow()

    if post_data.is_solution is not None:
        post.is_solution = post_data.is_solution

    db.commit()
    db.refresh(post)
    return post


@router.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Delete a forum post."""
    post = db.query(ForumPost).filter(ForumPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    # Check permissions (author or superuser)
    if post.author_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this post"
        )

    # Soft delete
    post.status = PostStatus.DELETED
    db.commit()
    return None
