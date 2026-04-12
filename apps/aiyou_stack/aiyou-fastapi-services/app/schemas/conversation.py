"""Conversation schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.message import MessageResponse


class ConversationBase(BaseModel):
    """Base conversation schema."""

    title: str = Field(..., min_length=1, max_length=500)
    project_id: UUID | None = None
    metadata: dict | None = None
    incognito: bool = False


class ConversationCreate(ConversationBase):
    """Schema for creating a conversation."""

    pass


class ConversationUpdate(BaseModel):
    """Schema for updating a conversation."""

    title: str | None = Field(None, min_length=1, max_length=500)
    metadata: dict | None = None
    active: bool | None = None


class ConversationResponse(ConversationBase):
    """Schema for conversation response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime
    active: bool
    messages: list[MessageResponse] = []


class ConversationListResponse(BaseModel):
    """Schema for listing conversations."""

    conversations: list[ConversationResponse]
    total: int
    page: int
    page_size: int
