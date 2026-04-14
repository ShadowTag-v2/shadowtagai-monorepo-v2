"""Forum endpoints for categories, topics, and posts."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_active_user, get_current_superuser
from app.db.session import get_db
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
from app.services.forum_service import ForumService

router = APIRouter()


# ===== Categories =====


@router.get("/categories", response_model=list[ForumCategoryResponse])
async def list_categories(db: Session = Depends(get_db)):
    """List all forum categories."""
    return ForumService.list_categories(db)


@router.post(
    "/categories", response_model=ForumCategoryResponse, status_code=status.HTTP_201_CREATED,
)
async def create_category(
    category_data: ForumCategoryCreate,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db),
):
    """Create a new forum category (admin only)."""
    if ForumService.get_category_by_slug(db, category_data.slug):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Category slug already exists",
        )
    return ForumService.create_category(db, category_data)


@router.get("/categories/{category_id}", response_model=ForumCategoryResponse)
async def get_category(category_id: int, db: Session = Depends(get_db)):
    """Get a forum category."""
    category = ForumService.get_category(db, category_id)
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
    category = ForumService.get_category(db, category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return ForumService.update_category(db, category, category_data)


# ===== Topics =====


@router.get("/categories/{category_id}/topics", response_model=ForumTopicListResponse)
async def list_topics(
    category_id: int, db: Session = Depends(get_db), page: int = 1, size: int = 20,
):
    """List topics in a category."""
    category = ForumService.get_category(db, category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    result = ForumService.list_topics(db, category_id, page, size)

    topic_responses = []
    for item in result["items"]:
        topic_dict = ForumTopicResponse.model_validate(item["topic"])
        if item["author"]:
            topic_dict.author = item["author"]
        topic_responses.append(topic_dict)

    return ForumTopicListResponse(
        items=topic_responses,
        total=result["total"],
        page=result["page"],
        size=result["size"],
        pages=result["pages"],
    )


@router.post("/topics", response_model=ForumTopicResponse, status_code=status.HTTP_201_CREATED)
async def create_topic(
    topic_data: ForumTopicCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create a new forum topic with initial post."""
    category = ForumService.get_category(db, topic_data.category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    if category.is_locked:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Category is locked")

    return ForumService.create_topic(db, topic_data, current_user, category)


@router.get("/topics/{topic_id}", response_model=ForumTopicResponse)
async def get_topic(topic_id: int, db: Session = Depends(get_db)):
    """Get a forum topic."""
    topic = ForumService.get_topic(db, topic_id)
    if not topic:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found")

    ForumService.increment_view_count(db, topic)
    return topic


@router.put("/topics/{topic_id}", response_model=ForumTopicResponse)
async def update_topic(
    topic_id: int,
    topic_data: ForumTopicUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Update a forum topic."""
    topic = ForumService.get_topic(db, topic_id)
    if not topic:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found")

    if topic.author_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this topic",
        )

    return ForumService.update_topic(db, topic, topic_data)


# ===== Posts =====


@router.get("/topics/{topic_id}/posts", response_model=ForumPostListResponse)
async def list_posts(topic_id: int, db: Session = Depends(get_db), page: int = 1, size: int = 20):
    """List posts in a topic."""
    topic = ForumService.get_topic(db, topic_id)
    if not topic:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found")

    result = ForumService.list_posts(db, topic_id, page, size)

    post_responses = []
    for item in result["items"]:
        post_dict = ForumPostResponse.model_validate(item["post"])
        if item["author"]:
            post_dict.author = item["author"]
        post_responses.append(post_dict)

    return ForumPostListResponse(
        items=post_responses,
        total=result["total"],
        page=result["page"],
        size=result["size"],
        pages=result["pages"],
    )


@router.post("/posts", response_model=ForumPostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    post_data: ForumPostCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create a new forum post."""
    topic = ForumService.get_topic(db, post_data.topic_id)
    if not topic:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found")

    if topic.is_locked:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Topic is locked")

    return ForumService.create_post(db, post_data, current_user)


@router.get("/posts/{post_id}", response_model=ForumPostResponse)
async def get_post(post_id: int, db: Session = Depends(get_db)):
    """Get a forum post."""
    post = ForumService.get_post(db, post_id)
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
    post = ForumService.get_post(db, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    if post.author_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this post",
        )

    return ForumService.update_post(db, post, post_data)


@router.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Delete a forum post."""
    post = ForumService.get_post(db, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    if post.author_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this post",
        )

    ForumService.soft_delete_post(db, post)
