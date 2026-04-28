# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Agent schemas."""

from uuid import UUID

from pydantic import BaseModel, Field


class AgentQueryRequest(BaseModel):
    """Schema for agent query request."""

    prompt: str = Field(..., min_length=1)
    project_id: UUID | None = None
    conversation_id: UUID | None = None
    include_memory: bool = True
    include_search: bool = True
    max_tokens: int | None = Field(default=4096, ge=1, le=8192)
    temperature: float | None = Field(default=1.0, ge=0.0, le=1.0)


class AgentQueryResponse(BaseModel):
    """Schema for agent query response."""

    response: str
    conversation_id: UUID
    memory_used: list[str] | None = None
    conversations_referenced: list[UUID] | None = None
    metadata: dict | None = None


class AgentStreamChunk(BaseModel):
    """Schema for agent stream chunk."""

    type: str  # "content", "memory", "search", "done"
    data: str | dict
    metadata: dict | None = None
