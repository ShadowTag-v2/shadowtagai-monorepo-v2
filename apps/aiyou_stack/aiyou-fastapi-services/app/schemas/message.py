"""Message schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.message import MessageRole


class MessageBase(BaseModel):
    """Base message schema."""

    role: MessageRole
    content: str = Field(..., min_length=1)
    metadata: dict | None = None


class MessageCreate(MessageBase):
    """Schema for creating a message."""

    pass


class MessageResponse(MessageBase):
    """Schema for message response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    conversation_id: UUID
    timestamp: datetime
