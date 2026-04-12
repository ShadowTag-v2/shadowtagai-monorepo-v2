"""Pydantic schemas."""

from app.schemas.user import UserCreate, UserUpdate, UserResponse, Token, TokenData
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse, ProjectStats
from app.schemas.conversation import (
    ConversationCreate,
    ConversationUpdate,
    ConversationResponse,
    ConversationWithMessages,
    MessageCreate,
    MessageResponse,
)
from app.schemas.memory import (
    MemoryCreate,
    MemoryUpdate,
    MemoryResponse,
    MemorySearchResult,
    MemorySynthesisResponse,
)
from app.schemas.search import (
    SearchQuery,
    SearchResponse,
    ConversationSearchResult,
    RecentChatsQuery,
    RecentChatsResponse,
)

__all__ = [
    # User
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "Token",
    "TokenData",
    # Project
    "ProjectCreate",
    "ProjectUpdate",
    "ProjectResponse",
    "ProjectStats",
    # Conversation
    "ConversationCreate",
    "ConversationUpdate",
    "ConversationResponse",
    "ConversationWithMessages",
    "MessageCreate",
    "MessageResponse",
    # Memory
    "MemoryCreate",
    "MemoryUpdate",
    "MemoryResponse",
    "MemorySearchResult",
    "MemorySynthesisResponse",
    # Search
    "SearchQuery",
    "SearchResponse",
    "ConversationSearchResult",
    "RecentChatsQuery",
    "RecentChatsResponse",
]
