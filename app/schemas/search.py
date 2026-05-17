# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Search schemas."""

from datetime import datetime
from pydantic import BaseModel, Field


class SearchQuery(BaseModel):
  """Schema for search query."""

  query: str = Field(..., description="Search query text")
  project_id: int | None = Field(None, description="Limit search to specific project")
  top_k: int = Field(
    default=10, ge=1, le=100, description="Number of results to return"
  )
  min_relevance: float = Field(
    default=0.5, ge=0.0, le=1.0, description="Minimum relevance score (0-1)"
  )
  search_conversations: bool = Field(
    default=True, description="Search in conversations"
  )
  search_memories: bool = Field(default=True, description="Search in memories")


class ConversationSearchResult(BaseModel):
  """Schema for conversation search result."""

  conversation_id: int
  conversation_title: str | None
  message_id: int
  message_content: str
  message_role: str
  relevance_score: float
  created_at: datetime
  project_id: int | None = None


class SearchResponse(BaseModel):
  """Schema for search response."""

  query: str
  total_results: int
  conversation_results: list[ConversationSearchResult] = []
  memory_results: list["MemorySearchResult"] = []
  search_time_ms: float


class RecentChatsQuery(BaseModel):
  """Schema for recent chats query."""

  limit: int = Field(
    default=20, ge=1, le=100, description="Number of recent chats to return"
  )
  project_id: int | None = Field(None, description="Filter by project")
  include_incognito: bool = Field(default=False, description="Include incognito chats")


class RecentChatsResponse(BaseModel):
  """Schema for recent chats response."""

  conversations: list["ConversationResponse"] = []
  total: int


# Import for forward references
from app.schemas.memory import MemorySearchResult
from app.schemas.conversation import ConversationResponse

SearchResponse.model_rebuild()
RecentChatsResponse.model_rebuild()
