"""Pydantic schemas for chat and conversation endpoints."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class MessageCreate(BaseModel):
    """Schema for creating a message."""

    role: str = Field(..., description="Message role: user, assistant, or system")
    content: str = Field(..., description="Message content")


class MessageResponse(BaseModel):
    """Schema for message response."""

    id: int
    conversation_id: int
    role: str
    content: str
    tokens: int | None = None
    metadata: dict[str, Any] | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConversationCreate(BaseModel):
    """Schema for creating a conversation."""

    user_id: str | None = None
    title: str | None = None
    system_prompt: str | None = None
    model_provider: str = Field(
        default="anthropic",
        description="LLM provider: anthropic or openai",
    )
    model_name: str | None = None
    metadata: dict[str, Any] | None = None


class ConversationResponse(BaseModel):
    """Schema for conversation response."""

    id: int
    session_id: str
    user_id: str | None = None
    title: str | None = None
    system_prompt: str | None = None
    model_provider: str
    model_name: str | None = None
    metadata: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime
    messages: list[MessageResponse] = []

    model_config = ConfigDict(from_attributes=True)


class ChatRequest(BaseModel):
    """Schema for chat completion request."""

    message: str = Field(..., description="User message")
    session_id: str | None = Field(None, description="Conversation session ID")
    system_prompt: str | None = Field(None, description="System prompt override")
    model_provider: str | None = Field(None, description="LLM provider: anthropic or openai")
    model_name: str | None = Field(None, description="Specific model name")
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Temperature for generation",
    )
    max_tokens: int | None = Field(None, gt=0, description="Maximum tokens to generate")
    stream: bool = Field(default=False, description="Enable streaming response")
    save_history: bool = Field(default=True, description="Save conversation to database")


class ChatResponse(BaseModel):
    """Schema for chat completion response."""

    session_id: str
    message: str
    role: str = "assistant"
    model: str
    provider: str
    tokens_used: int | None = None
    metadata: dict[str, Any] | None = None


class EmbeddingRequest(BaseModel):
    """Schema for embedding generation request."""

    text: str | None = Field(None, description="Single text to embed")
    texts: list[str] | None = Field(None, description="Multiple texts to embed")
    model: str | None = Field(None, description="Embedding model to use")


class EmbeddingResponse(BaseModel):
    """Schema for embedding response."""

    embedding: list[float] | None = None
    embeddings: list[list[float]] | None = None
    dimension: int
    model: str


class DocumentAddRequest(BaseModel):
    """Schema for adding documents to a collection."""

    collection_name: str = Field(..., description="Collection name")
    documents: list[str] = Field(..., description="Documents to add")
    metadata: list[dict[str, Any]] | None = Field(None, description="Metadata for each document")
    ids: list[str] | None = Field(None, description="Document IDs")


class SearchRequest(BaseModel):
    """Schema for semantic search request."""

    collection_name: str = Field(..., description="Collection to search")
    query: str = Field(..., description="Search query")
    n_results: int = Field(default=5, ge=1, le=100, description="Number of results")
    where: dict[str, Any] | None = Field(None, description="Metadata filter")


class SearchResponse(BaseModel):
    """Schema for search response."""

    documents: list[str]
    distances: list[float]
    metadata: list[dict[str, Any]]
    ids: list[str]


class PromptTemplateCreate(BaseModel):
    """Schema for creating a prompt template."""

    name: str = Field(..., description="Template name")
    template: str = Field(..., description="Template text with {variables}")
    description: str | None = None
    variables: list[str] = Field(default=[], description="Required variables")
    metadata: dict[str, Any] | None = None


class PromptTemplateResponse(BaseModel):
    """Schema for prompt template response."""

    id: int
    name: str
    template: str
    description: str | None = None
    variables: list[str]
    metadata: dict[str, Any] | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PromptRenderRequest(BaseModel):
    """Schema for rendering a prompt template."""

    template_name: str = Field(..., description="Name of the template to render")
    variables: dict[str, Any] = Field(..., description="Variables to substitute")
