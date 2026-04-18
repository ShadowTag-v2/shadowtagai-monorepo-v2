"""Data models for Gemini Ingestion Layer API"""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class SourceType(StrEnum):
    """Supported intelligence sources"""

    YOUTUBE = "youtube"
    TWITTER = "twitter"
    NEWS_API = "news_api"
    RSS_FEEDS = "rss_feeds"
    REDDIT = "reddit"
    LINKEDIN = "linkedin"
    GITHUB = "github"
    ACADEMIC = "academic"


class DataTier(StrEnum):
    """Data quality tiers"""

    TIER_1 = "tier_1"  # High-value
    TIER_2 = "tier_2"  # Medium-value
    TIER_3 = "tier_3"  # Low-value


class IngestionStatus(StrEnum):
    """Ingestion job status"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL_SUCCESS = "partial_success"


class JobStartRequest(BaseModel):
    """Request to start an ingestion job"""

    max_items_per_source: int = Field(
        default=500,
        ge=100,
        le=1000,
        description="Max items to collect per source",
    )
    enable_ethical_checks: bool = Field(
        default=True,
        description="Enable ethical crawling compliance",
    )


class SourceMetrics(BaseModel):
    """Metrics for a single intelligence source"""

    source_type: SourceType
    items_ingested: int = 0
    items_tier_1: int = 0
    items_tier_2: int = 0
    items_tier_3: int = 0
    avg_relevance_score: float = 0.0
    total_cost_usd: float = 0.0
    errors: int = 0
    last_successful_fetch: datetime | None = None
    tier_1_ratio: float = Field(default=0.0, description="Ratio of Tier 1 items (target ≥40%)")
    cost_per_item: float = Field(default=0.0, description="Cost per item")


class JobResult(BaseModel):
    """Ingestion job result"""

    job_id: str
    status: IngestionStatus
    runtime_minutes: float
    total_items: int
    active_sources_count: int
    tier_1_ratio: float = Field(description="Overall Tier 1 ratio (target ≥40%)")
    avg_cost_per_item: float
    total_cost_usd: float
    quality_gates_passed: dict[str, bool]
    am_briefing_delivered: bool = False
    errors: list[str] = []
    timestamp: datetime
    source_metrics: dict[SourceType, SourceMetrics] = {}


class JobStatusResponse(BaseModel):
    """Response for job status query"""

    job_id: str
    status: IngestionStatus
    started_at: datetime
    runtime_minutes: float | None = None
    progress_pct: float | None = Field(None, description="Progress percentage (0-100)")
    message: str = ""


class JobListResponse(BaseModel):
    """Response for listing jobs"""

    jobs: list[JobStatusResponse]
    total: int
    page: int
    page_size: int


class MetricsSummary(BaseModel):
    """Summary metrics across recent jobs"""

    total_jobs: int
    successful_jobs: int
    failed_jobs: int
    avg_runtime_minutes: float
    avg_items_per_job: int
    avg_tier_1_ratio: float
    avg_cost_per_job: float
    last_job_timestamp: datetime | None = None
