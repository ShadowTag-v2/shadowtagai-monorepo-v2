# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Search schemas."""

from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.conversation import ConversationResponse
from app.schemas.message import MessageResponse


class SearchRequest(BaseModel):
    """Schema for search request."""

    query: str = Field(..., min_length=1)
    project_id: UUID | None = None
    top_k: int = Field(default=5, ge=1, le=50)
    min_score: float | None = Field(default=None, ge=0.0, le=1.0)


class ConversationSearchResult(BaseModel):
    """Schema for conversation search result."""

    conversation: ConversationResponse
    score: float
    matched_messages: list[MessageResponse] = []


class MessageSearchResult(BaseModel):
    """Schema for message search result."""

    message: MessageResponse
    score: float
    conversation_id: UUID


class SearchResponse(BaseModel):
    """Schema for search response."""

    query: str
    results: list[ConversationSearchResult] | list[MessageSearchResult]
    total: int
