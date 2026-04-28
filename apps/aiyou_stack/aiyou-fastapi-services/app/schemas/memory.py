# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Memory schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.memory import MemoryCategory


class MemoryEntryBase(BaseModel):
    """Base memory entry schema."""

    category: MemoryCategory
    content: str = Field(..., min_length=1)
    project_id: UUID | None = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    metadata: dict | None = None


class MemoryEntryCreate(MemoryEntryBase):
    """Schema for creating a memory entry."""

    source_conversation_ids: list[str] | None = None


class MemoryEntryUpdate(BaseModel):
    """Schema for updating a memory entry."""

    content: str | None = Field(None, min_length=1)
    confidence: float | None = Field(None, ge=0.0, le=1.0)
    active: bool | None = None
    metadata: dict | None = None


class MemoryEntryResponse(MemoryEntryBase):
    """Schema for memory entry response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    source_conversation_ids: list[str] | None
    created_at: datetime
    updated_at: datetime
    active: bool


class MemoryListResponse(BaseModel):
    """Schema for listing memory entries."""

    entries: list[MemoryEntryResponse]
    total: int
    by_category: dict | None = None


class MemorySynthesisRequest(BaseModel):
    """Schema for memory synthesis request."""

    project_id: UUID | None = None
    since: datetime | None = None
    force: bool = False


class MemorySynthesisResponse(BaseModel):
    """Schema for memory synthesis response."""

    status: str
    entries_created: int
    entries_updated: int
    conversations_processed: int
