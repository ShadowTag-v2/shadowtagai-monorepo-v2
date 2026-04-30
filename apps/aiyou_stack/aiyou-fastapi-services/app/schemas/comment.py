"""Comment schemas for API validation."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.user import UserSummary


class CommentCreate(BaseModel):
    """Comment creation schema."""

    forum_post_id: int | None = None
    parent_id: int | None = None
    content: str = Field(..., min_length=1)


class CommentUpdate(BaseModel):
    """Comment update schema."""

    content: str = Field(..., min_length=1)


class CommentResponse(BaseModel):
    """Comment response schema."""

    id: int
    forum_post_id: int | None = None
    author_id: int
    parent_id: int | None = None
    content: str
    like_count: int
    is_edited: bool
    edited_at: datetime | None = None
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
    author: UserSummary | None = None

    model_config = ConfigDict(from_attributes=True)


class CommentListResponse(BaseModel):
    """Comment list with pagination."""

    items: list[CommentResponse]
    total: int
    page: int
    size: int
    pages: int
