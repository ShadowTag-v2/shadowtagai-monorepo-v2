"""Forum schemas for API validation."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.user import UserSummary


# Forum Category
class ForumCategoryCreate(BaseModel):
    """Forum category creation schema."""

    name: str = Field(..., min_length=1, max_length=100)
    slug: str = Field(..., min_length=1, max_length=100)
    description: str | None = None
    icon: str | None = None
    color: str | None = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    order: int = 0
    is_active: bool = True


class ForumCategoryUpdate(BaseModel):
    """Forum category update schema."""

    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = None
    icon: str | None = None
    color: str | None = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    order: int | None = None
    is_active: bool | None = None
    is_locked: bool | None = None


class ForumCategoryResponse(BaseModel):
    """Forum category response schema."""

    id: int
    name: str
    slug: str
    description: str | None = None
    icon: str | None = None
    color: str | None = None
    order: int
    is_active: bool
    is_locked: bool
    total_topics: int
    total_posts: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Forum Topic
class ForumTopicCreate(BaseModel):
    """Forum topic creation schema."""

    category_id: int
    title: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=255)
    initial_post_content: str = Field(..., min_length=1)


class ForumTopicUpdate(BaseModel):
    """Forum topic update schema."""

    title: str | None = Field(None, min_length=1, max_length=255)
    is_pinned: bool | None = None
    is_locked: bool | None = None
    is_featured: bool | None = None


class ForumTopicResponse(BaseModel):
    """Forum topic response schema."""

    id: int
    category_id: int
    author_id: int
    title: str
    slug: str
    is_pinned: bool
    is_locked: bool
    is_featured: bool
    view_count: int
    reply_count: int
    created_at: datetime
    updated_at: datetime
    last_activity_at: datetime
    author: UserSummary | None = None

    model_config = ConfigDict(from_attributes=True)


# Forum Post
class ForumPostCreate(BaseModel):
    """Forum post creation schema."""

    topic_id: int
    content: str = Field(..., min_length=1)


class ForumPostUpdate(BaseModel):
    """Forum post update schema."""

    content: str = Field(..., min_length=1)
    is_solution: bool | None = None


class ForumPostResponse(BaseModel):
    """Forum post response schema."""

    id: int
    topic_id: int
    author_id: int
    content: str
    status: str
    is_edited: bool
    edited_at: datetime | None = None
    is_solution: bool
    like_count: int
    created_at: datetime
    updated_at: datetime
    author: UserSummary | None = None

    model_config = ConfigDict(from_attributes=True)


# List Responses
class ForumTopicListResponse(BaseModel):
    """Forum topic list with pagination."""

    items: list[ForumTopicResponse]
    total: int
    page: int
    size: int
    pages: int


class ForumPostListResponse(BaseModel):
    """Forum post list with pagination."""

    items: list[ForumPostResponse]
    total: int
    page: int
    size: int
    pages: int
