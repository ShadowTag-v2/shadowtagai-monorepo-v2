# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Gemini Ingestion Layer API
FastAPI endpoints for interfacing with the ingestion pipeline
"""

from datetime import datetime, timezone, timedelta
from typing import Any
from enum import Enum

from fastapi import FastAPI, Query, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, field_validator
import asyncio

# Initialize FastAPI app
app = FastAPI(
    title="Gemini Ingestion Layer API",
    description="PNKLN Core Stack™ Intelligence Collection Pipeline",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


# ============================================================================
# Models
# ============================================================================


class TierLevel(str, Enum):
    """Tier classification levels"""

    TIER_1 = "tier_1"
    TIER_2 = "tier_2"
    TIER_3 = "tier_3"


class SourceType(str, Enum):
    """Data source types"""

    YOUTUBE = "youtube"
    TWITTER = "twitter"
    NEWS = "news"
    RSS = "rss"
    WEB_SCRAPER = "web_scraper"
    API_INTEGRATION = "api_integration"


class JobStatus(str, Enum):
    """CronJob execution status"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


class IngestedItem(BaseModel):
    """Single ingested intelligence item"""

    id: str = Field(..., description="Unique item identifier")
    source_type: SourceType = Field(..., description="Source type")
    source_url: str = Field(..., description="Original URL")
    title: str = Field(..., description="Item title")
    content: str = Field(..., description="Item content/summary")
    tier: TierLevel = Field(..., description="Classification tier")
    relevance_score: float = Field(..., ge=0, le=100, description="Relevance score (0-100)")
    engagement_score: int = Field(..., ge=0, description="Social engagement metrics")
    published_at: datetime = Field(..., description="Publication timestamp")
    ingested_at: datetime = Field(..., description="Ingestion timestamp")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "ing_20251107_abc123",
                "source_type": "news",
                "source_url": "https://apnews.com/article/example",
                "title": "Breaking: Example News Event",
                "content": "This is a summary of the news article...",
                "tier": "tier_1",
                "relevance_score": 87.5,
                "engagement_score": 1250,
                "published_at": "2025-11-07T14:30:00Z",
                "ingested_at": "2025-11-08T02:15:00Z",
                "metadata": {
                    "author": "AP News",
                    "tags": ["politics", "breaking"],
                },
            }
        }
    )


class JobStatusResponse(BaseModel):
    """CronJob execution status"""

    job_id: str = Field(..., description="Job execution ID")
    status: JobStatus = Field(..., description="Current status")
    start_time: datetime | None = Field(None, description="Job start time")
    end_time: datetime | None = Field(None, description="Job end time")
    runtime_minutes: float | None = Field(None, description="Runtime in minutes")
    items_collected: int = Field(default=0, description="Total items collected")
    items_by_tier: dict[str, int] = Field(default_factory=dict, description="Items by tier")
    sources_active: int = Field(default=0, description="Active sources")
    errors: list[str] = Field(default_factory=list, description="Error messages")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "job_id": "cronjob-20251107-020000",
                "status": "completed",
                "start_time": "2025-11-07T02:00:00Z",
                "end_time": "2025-11-07T02:42:30Z",
                "runtime_minutes": 42.5,
                "items_collected": 3245,
                "items_by_tier": {"tier_1": 487, "tier_2": 1156, "tier_3": 1602},
                "sources_active": 6,
                "errors": [],
            }
        }
    )


class MetricsResponse(BaseModel):
    """Performance metrics"""

    daily_items_avg: float = Field(..., description="Average items per day (7-day)")
    daily_items_trend: str = Field(..., description="Trend: up, down, stable")
    tier_distribution: dict[str, float] = Field(..., description="Tier % distribution")
    cost_per_item: float = Field(..., description="Average cost per item (USD)")
    monthly_cost: float = Field(..., description="Total monthly cost (USD)")
    avg_relevance: float = Field(..., description="Average relevance score")
    uptime_percentage: float = Field(..., description="Successful runs %")
    avg_runtime_minutes: float = Field(..., description="Average runtime (minutes)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "daily_items_avg": 3180,
                "daily_items_trend": "stable",
                "tier_distribution": {"tier_1": 15.2, "tier_2": 34.8, "tier_3": 50.0},
                "cost_per_item": 0.012,
                "monthly_cost": 74.5,
                "avg_relevance": 62.3,
                "uptime_percentage": 99.3,
                "avg_runtime_minutes": 43.2,
            }
        }
    )


class TriggerRequest(BaseModel):
    """Manual trigger request"""

    reason: str = Field(..., description="Reason for manual trigger")
    override_schedule: bool = Field(default=False, description="Override schedule check")
    sources_filter: list[SourceType] | None = Field(None, description="Limit to specific sources")


class SourceConfig(BaseModel):
    """Source configuration"""

    source_type: SourceType = Field(..., description="Source type")
    enabled: bool = Field(default=True, description="Source active")
    priority: int = Field(default=5, ge=1, le=10, description="Priority (1=low, 10=high)")
    rate_limit_delay: float = Field(default=2.0, ge=1.0, description="Rate limit delay (seconds)")
    config: dict[str, Any] = Field(default_factory=dict, description="Source-specific config")

    @field_validator("config")
    def validate_config(cls, v, info):
        """Validate source-specific configuration"""
        source_type = info.data.get("source_type")

        if source_type == SourceType.YOUTUBE:
            required_keys = ["channels", "max_videos_per_channel"]
        elif source_type == SourceType.TWITTER:
            required_keys = ["keywords", "accounts"]
        elif source_type == SourceType.NEWS:
            required_keys = ["outlets", "categories"]
        elif source_type == SourceType.RSS:
            required_keys = ["feeds"]
        elif source_type == SourceType.WEB_SCRAPER:
            required_keys = ["domains", "selectors"]
        else:
            required_keys = []

        for key in required_keys:
            if key not in v:
                raise ValueError(f"Missing required config key: {key}")

        return v


# ============================================================================
# Endpoints
# ============================================================================


@app.get("/", tags=["Health"])
async def root():
    """API root endpoint"""
    return {"service": "Gemini Ingestion Layer API", "version": "1.0.0", "status": "operational", "documentation": "/docs"}


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    # TODO: Implement actual health checks (DB, GCS, etc.)
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc), "checks": {"database": "ok", "gcs": "ok", "redis": "ok"}}


@app.post("/ingestion/trigger", response_model=JobStatusResponse, status_code=status.HTTP_202_ACCEPTED, tags=["Ingestion"])
async def trigger_ingestion(request: TriggerRequest):
    """
    Manually trigger an ingestion job

    This endpoint allows on-demand triggering of the ingestion CronJob,
    bypassing the normal schedule. Useful for:
    - Breaking news events
    - On-demand intelligence gathering
    - Testing and debugging

    **Note**: Requires appropriate permissions.
    """
    # TODO: Implement Kubernetes Job trigger via client library
    # For now, return mock response

    job_id = f"manual-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"

    # Simulate job creation
    await asyncio.sleep(0.1)

    return JobStatusResponse(
        job_id=job_id,
        status=JobStatus.PENDING,
        start_time=None,
        end_time=None,
        runtime_minutes=None,
        items_collected=0,
        items_by_tier={},
        sources_active=0,
        errors=[],
    )


@app.get("/ingestion/status", response_model=JobStatusResponse, tags=["Ingestion"])
async def get_ingestion_status(job_id: str | None = Query(None, description="Specific job ID (default: latest)")):
    """
    Get status of an ingestion job

    Returns the current or historical status of an ingestion job.
    If no job_id is provided, returns the status of the most recent job.
    """
    # TODO: Implement actual status retrieval from DB/Kubernetes

    # Mock response
    return JobStatusResponse(
        job_id=job_id or "cronjob-20251107-020000",
        status=JobStatus.COMPLETED,
        start_time=datetime.now(timezone.utc) - timedelta(minutes=45),
        end_time=datetime.now(timezone.utc),
        runtime_minutes=45.0,
        items_collected=3245,
        items_by_tier={"tier_1": 487, "tier_2": 1156, "tier_3": 1602},
        sources_active=6,
        errors=[],
    )


@app.get("/ingestion/items", response_model=list[IngestedItem], tags=["Ingestion"])
async def get_ingested_items(
    tier: TierLevel | None = Query(None, description="Filter by tier"),
    source_type: SourceType | None = Query(None, description="Filter by source type"),
    since: datetime | None = Query(None, description="Filter by ingested_at >= since"),
    limit: int = Query(100, ge=1, le=1000, description="Max items to return"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
):
    """
    Query ingested items

    Retrieve ingested intelligence items with optional filters.
    Supports pagination for large result sets.

    **Use Cases**:
    - Retrieve latest Tier 1 items for AM briefing
    - Query specific source type (e.g., all YouTube items)
    - Historical data analysis
    """
    # TODO: Implement actual query from PostgreSQL/GCS

    # Mock response
    mock_items = [
        IngestedItem(
            id="ing_20251107_abc123",
            source_type=SourceType.NEWS,
            source_url="https://apnews.com/article/example",
            title="Breaking: Example News Event",
            content="This is a summary of the news article...",
            tier=TierLevel.TIER_1,
            relevance_score=87.5,
            engagement_score=1250,
            published_at=datetime.now(timezone.utc) - timedelta(hours=2),
            ingested_at=datetime.now(timezone.utc),
            metadata={"author": "AP News", "tags": ["politics", "breaking"]},
        )
    ]

    # Apply filters
    filtered = mock_items
    if tier:
        filtered = [item for item in filtered if item.tier == tier]
    if source_type:
        filtered = [item for item in filtered if item.source_type == source_type]
    if since:
        filtered = [item for item in filtered if item.ingested_at >= since]

    # Apply pagination
    return filtered[offset : offset + limit]


@app.get("/ingestion/metrics", response_model=MetricsResponse, tags=["Metrics"])
async def get_metrics(days: int = Query(7, ge=1, le=90, description="Number of days for metrics calculation")):
    """
    Get performance metrics

    Returns aggregated performance metrics over the specified time period.

    **Key Metrics**:
    - Daily items (volume and trend)
    - Tier distribution
    - Cost efficiency
    - Quality scores
    - Uptime
    """
    # TODO: Implement actual metrics calculation from DB

    # Mock response
    return MetricsResponse(
        daily_items_avg=3180,
        daily_items_trend="stable",
        tier_distribution={"tier_1": 15.2, "tier_2": 34.8, "tier_3": 50.0},
        cost_per_item=0.012,
        monthly_cost=74.5,
        avg_relevance=62.3,
        uptime_percentage=99.3,
        avg_runtime_minutes=43.2,
    )


@app.get("/ingestion/sources", response_model=list[SourceConfig], tags=["Configuration"])
async def get_sources():
    """
    Get source configuration

    Returns the current configuration for all data sources.
    """
    # TODO: Implement actual config retrieval from ConfigMap/DB

    # Mock response
    return [
        SourceConfig(
            source_type=SourceType.YOUTUBE,
            enabled=True,
            priority=8,
            rate_limit_delay=2.0,
            config={
                "channels": [
                    "UCxxxxxxxx",  # Example channel ID
                    "UCyyyyyyyy",
                ],
                "max_videos_per_channel": 50,
            },
        ),
        SourceConfig(
            source_type=SourceType.TWITTER,
            enabled=True,
            priority=9,
            rate_limit_delay=2.0,
            config={"keywords": ["AI", "machine learning", "technology"], "accounts": ["@example_account"]},
        ),
    ]


@app.post("/ingestion/sources", response_model=SourceConfig, status_code=status.HTTP_201_CREATED, tags=["Configuration"])
async def update_source(config: SourceConfig):
    """
    Update source configuration

    Updates the configuration for a specific data source.
    Changes take effect on the next CronJob run.

    **Note**: Requires admin permissions.
    """
    # TODO: Implement actual config update to ConfigMap/DB

    # Validate and return
    return config


@app.get("/ingestion/sources/{source_type}/stats", tags=["Metrics"])
async def get_source_stats(source_type: SourceType, days: int = Query(7, ge=1, le=90, description="Number of days for stats")):
    """
    Get source-specific statistics

    Returns detailed statistics for a specific source type.
    """
    # TODO: Implement actual stats retrieval

    # Mock response
    return {
        "source_type": source_type,
        "period_days": days,
        "total_items": 4250,
        "items_by_tier": {"tier_1": 850, "tier_2": 1700, "tier_3": 1700},
        "avg_relevance": 68.5,
        "avg_engagement": 245,
        "uptime_percentage": 98.5,
        "avg_items_per_day": 607,
        "error_rate": 1.2,
    }


# ============================================================================
# Error Handlers
# ============================================================================


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Internal server error", "detail": str(exc), "timestamp": datetime.now(timezone.utc).isoformat()},
    )


# ============================================================================
# Startup/Shutdown Events
# ============================================================================


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    # TODO: Initialize DB connections, GCS clients, etc.
    print("Gemini Ingestion Layer API started")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown"""
    # TODO: Close DB connections, etc.
    print("Gemini Ingestion Layer API shutting down")


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("ingestion:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
