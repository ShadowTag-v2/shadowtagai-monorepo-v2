"""Conversation schemas."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class MessageBase(BaseModel):
    """Base message schema."""

    role: str = Field(..., description="Message role: user, assistant, or system")
    content: str = Field(..., description="Message content")


class MessageCreate(MessageBase):
    """Schema for creating a message."""

    conversation_id: int


class MessageResponse(MessageBase):
    """Schema for message response."""

    id: int
    conversation_id: int
    created_at: datetime
    tokens: int | None = None
    model: str | None = None

    model_config = {"from_attributes": True}


class ConversationBase(BaseModel):
    """Base conversation schema."""

    title: str | None = None
    is_incognito: bool = Field(default=False, description="Incognito mode - not saved to memory")


class ConversationCreate(ConversationBase):
    """Schema for creating a conversation."""

    project_id: int | None = None


class ConversationUpdate(BaseModel):
    """Schema for updating a conversation."""

    title: str | None = None
    is_active: bool | None = None


class ConversationResponse(ConversationBase):
    """Schema for conversation response."""

    id: int
    user_id: int
    project_id: int | None = None
    summary: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_message_at: datetime
    message_count: int | None = None

    model_config = {"from_attributes": True}


class ConversationWithMessages(ConversationResponse):
    """Schema for conversation with messages."""

    messages: list[MessageResponse] = []

    model_config = {"from_attributes": True}
