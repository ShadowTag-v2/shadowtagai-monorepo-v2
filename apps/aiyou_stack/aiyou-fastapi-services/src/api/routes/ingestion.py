"""Ingestion layer endpoints.

Provides endpoints for managing and monitoring the Gemini Ingestion Layer.
"""

from datetime import datetime
from enum import StrEnum

from fastapi import APIRouter, BackgroundTasks, status
from pydantic import BaseModel, Field

router = APIRouter()


class SourceTier(StrEnum):
    """Source tier classification."""

    TIER_1 = "tier_1"
    TIER_2 = "tier_2"
    TIER_3 = "tier_3"


class SourceType(StrEnum):
    """Type of data source."""

    YOUTUBE = "youtube"
    TWITTER = "twitter"
    NEWS = "news"
    RSS = "rss"
    WEB = "web"
    OTHER = "other"


class IngestionSource(BaseModel):
    """Data source configuration."""

    id: str = Field(..., description="Unique source identifier")
    name: str = Field(..., description="Human-readable source name")
    source_type: SourceType = Field(..., description="Type of source")
    tier: SourceTier = Field(..., description="Quality tier classification")
    enabled: bool = Field(default=True, description="Whether source is active")
    url: str | None = Field(None, description="Source URL if applicable")
    rate_limit_rpm: int = Field(default=60, description="Rate limit in requests per minute")


class IngestionJobStatus(StrEnum):
    """Status of an ingestion job."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class IngestionJob(BaseModel):
    """Ingestion job information."""

    job_id: str
    status: IngestionJobStatus
    started_at: datetime | None = None
    completed_at: datetime | None = None
    items_collected: int = 0
    sources_processed: int = 0
    errors: list[str] = []


class IngestionMetrics(BaseModel):
    """Ingestion layer metrics."""

    total_items_today: int = 0
    active_sources: int = 0
    tier_1_percentage: float = 0.0
    tier_2_percentage: float = 0.0
    tier_3_percentage: float = 0.0
    average_cost_per_item: float = 0.0
    last_job_duration_minutes: float | None = None
    last_job_status: IngestionJobStatus | None = None


@router.get(
    "/sources",
    response_model=list[IngestionSource],
    summary="List Sources",
    description="Get all configured ingestion sources",
)
async def list_sources() -> list[IngestionSource]:
    """List all configured ingestion sources.

    Returns source configurations including tier classifications
    and enabled status.
    """
    # TODO: Implement actual source retrieval from database/config
    return [
        IngestionSource(
            id="youtube-tech",
            name="YouTube Technology Channels",
            source_type=SourceType.YOUTUBE,
            tier=SourceTier.TIER_1,
            enabled=True,
            rate_limit_rpm=30,
        ),
        IngestionSource(
            id="twitter-trends",
            name="Twitter Trending Topics",
            source_type=SourceType.TWITTER,
            tier=SourceTier.TIER_2,
            enabled=True,
            rate_limit_rpm=60,
        ),
    ]


@router.post(
    "/sources",
    response_model=IngestionSource,
    status_code=status.HTTP_201_CREATED,
    summary="Add Source",
    description="Add a new ingestion source",
)
async def add_source(source: IngestionSource) -> IngestionSource:
    """Add a new ingestion source.

    Creates a new source configuration with specified tier
    and rate limiting settings.
    """
    # TODO: Implement actual source creation
    return source


@router.get(
    "/jobs/latest",
    response_model=IngestionJob,
    summary="Get Latest Job",
    description="Get information about the most recent ingestion job",
)
async def get_latest_job() -> IngestionJob:
    """Get the latest ingestion job status.

    Returns information about the most recent ingestion run,
    including items collected and any errors encountered.
    """
    # TODO: Implement actual job retrieval
    return IngestionJob(
        job_id="job-2025-11-15-2300",
        status=IngestionJobStatus.COMPLETED,
        started_at=datetime(2025, 11, 15, 23, 0, 0),
        completed_at=datetime(2025, 11, 15, 23, 42, 0),
        items_collected=1247,
        sources_processed=15,
        errors=[],
    )


@router.post(
    "/jobs/trigger",
    response_model=IngestionJob,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Trigger Job",
    description="Manually trigger an ingestion job",
)
async def trigger_job(background_tasks: BackgroundTasks) -> IngestionJob:
    """Manually trigger an ingestion job.

    Starts a new ingestion run outside of the normal schedule.
    Useful for testing or recovering from failures.
    """
    # TODO: Implement actual job triggering
    job = IngestionJob(
        job_id=f"job-manual-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        status=IngestionJobStatus.PENDING,
    )

    # background_tasks.add_task(run_ingestion_job, job.job_id)

    return job


@router.get(
    "/metrics",
    response_model=IngestionMetrics,
    summary="Get Metrics",
    description="Get ingestion layer performance metrics",
)
async def get_metrics() -> IngestionMetrics:
    """Get ingestion layer metrics.

    Returns key performance indicators including:
    - Items collected per day
    - Source diversity
    - Tier distribution
    - Cost per item
    - Job duration
    """
    # TODO: Implement actual metrics calculation
    return IngestionMetrics(
        total_items_today=1247,
        active_sources=15,
        tier_1_percentage=35.2,
        tier_2_percentage=48.6,
        tier_3_percentage=16.2,
        average_cost_per_item=0.0062,
        last_job_duration_minutes=42.0,
        last_job_status=IngestionJobStatus.COMPLETED,
    )
