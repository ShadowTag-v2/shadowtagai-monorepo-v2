"""Memory schemas."""

from datetime import datetime
from pydantic import BaseModel, Field


class MemoryBase(BaseModel):
    """Base memory schema."""

    title: str | None = None
    content: str = Field(..., description="Memory content")
    memory_type: str = Field(default="fact", description="Memory type: fact, preference, context, or insight")


class MemoryCreate(MemoryBase):
    """Schema for creating a memory."""

    project_id: int | None = None
    source_conversation_ids: list[int] | None = None
    confidence_score: float = Field(default=1.0, ge=0.0, le=1.0)


class MemoryUpdate(BaseModel):
    """Schema for updating a memory."""

    title: str | None = None
    content: str | None = None
    memory_type: str | None = None
    is_active: bool | None = None


class MemoryResponse(MemoryBase):
    """Schema for memory response."""

    id: int
    user_id: int
    project_id: int | None = None
    confidence_score: float
    is_active: bool
    is_user_edited: bool
    created_at: datetime
    updated_at: datetime
    last_accessed_at: datetime

    model_config = {"from_attributes": True}


class MemorySearchResult(MemoryResponse):
    """Schema for memory search result with relevance score."""

    relevance_score: float = Field(..., description="Semantic similarity score")


class MemorySynthesisResponse(BaseModel):
    """Schema for memory synthesis response."""

    total_memories: int
    synthesis: str
    updated_at: datetime
    project_id: int | None = None
