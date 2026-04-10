"""
AI Threads API Schemas

Pydantic models for AI thread API request/response handling.
Supports thread creation, search, export, and import operations.
"""

from datetime import datetime
from enum import Enum, StrEnum
from typing import Any

from pydantic import BaseModel, Field, field_validator

# ============================================================================
# Enums
# ============================================================================


class ThreadSourceEnum(StrEnum):
    """Source platform for threads."""

    TWITTER_X = "twitter_x"
    LINKEDIN = "linkedin"
    MANUAL = "manual"
    IMPORT = "import"


class ThreadStatusEnum(StrEnum):
    """Processing status for threads."""

    PENDING = "pending"
    PROCESSING = "processing"
    INDEXED = "indexed"
    FAILED = "failed"


class ThreadCategoryEnum(StrEnum):
    """Categories for AI agent threads."""

    AGENT_BASICS = "agent_basics"
    PROMPT_ENGINEERING = "prompt_engineering"
    MEMORY_SYSTEMS = "memory_systems"
    TOOL_INTEGRATION = "tool_integration"
    MULTI_AGENT = "multi_agent"
    RAG_RETRIEVAL = "rag_retrieval"
    DEPLOYMENT = "deployment"
    EVALUATION = "evaluation"
    FRAMEWORKS = "frameworks"
    GENERAL = "general"


class ExportFormat(StrEnum):
    """Export format options."""

    JSON = "json"
    MARKDOWN = "markdown"
    PDF = "pdf"
    TXT = "txt"


class SortOrder(StrEnum):
    """Sort order options."""

    LIKES_DESC = "likes_desc"
    LIKES_ASC = "likes_asc"
    DATE_DESC = "date_desc"
    DATE_ASC = "date_asc"
    RELEVANCE = "relevance"


# ============================================================================
# Author Schemas
# ============================================================================


class AuthorBase(BaseModel):
    """Base author fields."""

    username: str = Field(..., min_length=1, max_length=100)
    display_name: str = Field(..., min_length=1, max_length=200)
    platform: ThreadSourceEnum = ThreadSourceEnum.TWITTER_X


class AuthorCreate(AuthorBase):
    """Schema for creating an author."""

    platform_id: str = Field(..., description="Platform-specific user ID (e.g., @username)")
    profile_url: str | None = None
    avatar_url: str | None = None
    bio: str | None = None
    follower_count: int = 0
    verified: bool = False


class AuthorResponse(AuthorBase):
    """Schema for author response."""

    id: str
    platform_id: str
    profile_url: str | None = None
    avatar_url: str | None = None
    bio: str | None = None
    follower_count: int = 0
    verified: bool = False
    created_at: datetime

    model_config = {"from_attributes": True}


# ============================================================================
# Post Schemas
# ============================================================================


class PostBase(BaseModel):
    """Base post fields."""

    position: int = Field(..., ge=1, description="Position in thread (1-indexed)")
    content: str = Field(..., min_length=1)


class PostCreate(PostBase):
    """Schema for creating a post."""

    platform_post_id: str
    has_media: bool = False
    media_urls: list[str] = []
    media_descriptions: list[str] = []
    has_code: bool = False
    code_language: str | None = None
    likes: int = 0


class PostResponse(PostBase):
    """Schema for post response."""

    id: str
    thread_id: str
    platform_post_id: str
    content_length: int | None = None
    has_media: bool = False
    media_urls: list[str] = []
    media_descriptions: list[str] = []
    has_code: bool = False
    code_language: str | None = None
    likes: int = 0
    created_at: datetime

    model_config = {"from_attributes": True}


# ============================================================================
# Thread Schemas
# ============================================================================


class ThreadBase(BaseModel):
    """Base thread fields."""

    title: str = Field(..., min_length=1, max_length=500)
    category: ThreadCategoryEnum = ThreadCategoryEnum.GENERAL
    tags: list[str] = Field(default_factory=list)


class ThreadCreate(ThreadBase):
    """Schema for creating a thread."""

    platform_post_id: str = Field(..., description="Original post ID from platform")
    platform: ThreadSourceEnum = ThreadSourceEnum.TWITTER_X
    full_content: str = Field(..., min_length=1)
    published_at: datetime

    # Author info (can reference existing or create new)
    author_id: str | None = None
    author: AuthorCreate | None = None

    # Posts
    posts: list[PostCreate] = Field(default_factory=list)

    # Engagement
    likes: int = 0
    retweets: int = 0
    replies: int = 0
    views: int = 0

    # Optional
    source_url: str | None = None
    metadata: dict[str, Any] | None = None

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: list[str]) -> list[str]:
        """Normalize tags to lowercase."""
        return [tag.lower().strip() for tag in v if tag.strip()]


class ThreadUpdate(BaseModel):
    """Schema for updating a thread."""

    title: str | None = None
    category: ThreadCategoryEnum | None = None
    tags: list[str] | None = None
    quality_score: float | None = Field(None, ge=0, le=1)
    relevance_score: float | None = Field(None, ge=0, le=1)
    metadata: dict[str, Any] | None = None


class ThreadSummary(BaseModel):
    """Compact thread summary for lists."""

    id: str
    title: str
    author_username: str
    author_display_name: str
    category: ThreadCategoryEnum
    tags: list[str]
    likes: int
    post_count: int
    published_at: datetime
    status: ThreadStatusEnum

    model_config = {"from_attributes": True}


class ThreadResponse(ThreadBase):
    """Full thread response with all details."""

    id: str
    platform_post_id: str
    platform: ThreadSourceEnum
    full_content: str
    post_count: int

    # Engagement
    likes: int
    retweets: int
    replies: int
    views: int

    # Processing
    status: ThreadStatusEnum
    embedding_id: str | None = None
    quality_score: float | None = None
    relevance_score: float | None = None

    # Source
    source_url: str | None = None
    metadata: dict[str, Any] | None = None

    # Timestamps
    published_at: datetime
    scraped_at: datetime | None = None
    created_at: datetime
    updated_at: datetime | None = None

    # Related
    author: AuthorResponse
    posts: list[PostResponse] = []

    model_config = {"from_attributes": True}


# ============================================================================
# Search Schemas
# ============================================================================


class SearchRequest(BaseModel):
    """Schema for semantic search request."""

    query: str = Field(..., min_length=1, max_length=1000)
    top_k: int = Field(default=10, ge=1, le=100)
    category: ThreadCategoryEnum | None = None
    min_likes: int | None = Field(default=None, ge=0)
    tags: list[str] | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None
    include_posts: bool = False


class SearchResult(BaseModel):
    """Individual search result."""

    thread: ThreadSummary
    score: float = Field(..., description="Relevance score 0-1")
    highlights: list[str] = Field(default_factory=list, description="Matching text snippets")
    matched_post_positions: list[int] = Field(default_factory=list)


class SearchResponse(BaseModel):
    """Search response with results and metadata."""

    query: str
    total_results: int
    results: list[SearchResult]
    search_time_ms: float
    filters_applied: dict[str, Any]


# ============================================================================
# List/Pagination Schemas
# ============================================================================


class ThreadListRequest(BaseModel):
    """Request for paginated thread list."""

    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    category: ThreadCategoryEnum | None = None
    status: ThreadStatusEnum | None = None
    min_likes: int | None = None
    tags: list[str] | None = None
    author_username: str | None = None
    sort: SortOrder = SortOrder.LIKES_DESC


class ThreadListResponse(BaseModel):
    """Paginated thread list response."""

    threads: list[ThreadSummary]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool


# ============================================================================
# Export Schemas
# ============================================================================


class ExportRequest(BaseModel):
    """Request for exporting threads."""

    thread_ids: list[str] | None = None  # Specific IDs, or None for all matching
    format: ExportFormat = ExportFormat.JSON
    category: ThreadCategoryEnum | None = None
    min_likes: int | None = None
    include_posts: bool = True
    include_metadata: bool = False


class ExportResponse(BaseModel):
    """Export response with content or file reference."""

    format: ExportFormat
    thread_count: int
    content: str | None = None  # For JSON/MD/TXT
    file_url: str | None = None  # For PDF or large exports
    file_size_bytes: int | None = None
    generated_at: datetime


# ============================================================================
# Import Schemas
# ============================================================================


class BulkImportRequest(BaseModel):
    """Request for bulk importing threads from raw compilation."""

    content: str = Field(..., min_length=100, description="Raw thread compilation text")
    source: ThreadSourceEnum = ThreadSourceEnum.IMPORT
    auto_categorize: bool = True
    generate_embeddings: bool = True


class BulkImportResult(BaseModel):
    """Result for a single thread import."""

    platform_post_id: str
    success: bool
    thread_id: str | None = None
    error: str | None = None


class BulkImportResponse(BaseModel):
    """Bulk import response."""

    total_found: int
    successfully_imported: int
    failed: int
    results: list[BulkImportResult]
    processing_time_ms: float


# ============================================================================
# Scraper Schemas
# ============================================================================


class ScrapeJobCreate(BaseModel):
    """Request to create a scrape job."""

    query: str = Field(..., min_length=1, max_length=500)
    min_likes: int = Field(default=10, ge=0)
    max_results: int = Field(default=100, ge=1, le=1000)
    scheduled_at: datetime | None = None  # None = run immediately


class ScrapeJobResponse(BaseModel):
    """Scrape job status response."""

    id: str
    query: str
    min_likes: int
    max_results: int
    status: str
    threads_found: int
    threads_saved: int
    error_message: str | None = None
    scheduled_at: datetime | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ============================================================================
# Analytics Schemas
# ============================================================================


class ThreadAnalytics(BaseModel):
    """Analytics for thread collection."""

    total_threads: int
    total_posts: int
    total_authors: int
    indexed_threads: int
    pending_threads: int
    category_distribution: dict[str, int]
    top_tags: list[tuple[str, int]]
    avg_likes: float
    avg_posts_per_thread: float
    date_range: dict[str, datetime | None]
