# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Pydantic models for ingestion layer and intelligence collection."""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class DataSourceType(StrEnum):
    """Types of data sources for ingestion."""

    YOUTUBE = "youtube"
    TWITTER = "twitter"
    NEWS = "news"
    RSS = "rss"
    WEB = "web"
    API = "api"
    CUSTOM = "custom"


class DataTier(StrEnum):
    """Data quality tier classification."""

    TIER_1 = "tier_1"  # High-value, verified sources
    TIER_2 = "tier_2"  # Medium-value, generally reliable
    TIER_3 = "tier_3"  # Low-value, unverified


class IngestionStatus(StrEnum):
    """Status of ingestion job."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


class DataSource(BaseModel):
    """Represents a data source for ingestion."""

    source_id: str = Field(..., description="Unique source identifier")
    name: str = Field(..., description="Source name")
    source_type: DataSourceType = Field(..., description="Type of source")
    tier: DataTier = Field(..., description="Quality tier")
    url: str | None = Field(None, description="Source URL if applicable")
    enabled: bool = Field(default=True, description="Whether source is active")
    rate_limit: int | None = Field(None, description="Requests per minute limit")
    cost_per_item: float | None = Field(None, description="Cost per item ingested (USD)")
    metadata: dict = Field(default_factory=dict, description="Additional metadata")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class IngestionMetrics(BaseModel):
    """Metrics for ingestion operations."""

    date: datetime = Field(default_factory=datetime.utcnow)
    total_items: int = Field(default=0, description="Total items ingested")
    items_by_source: dict[str, int] = Field(default_factory=dict, description="Items per source")
    items_by_tier: dict[str, int] = Field(default_factory=dict, description="Items per tier")
    total_cost: float = Field(default=0.0, description="Total cost (USD)")
    avg_cost_per_item: float = Field(default=0.0, description="Average cost per item")
    runtime_minutes: float = Field(default=0.0, description="Total runtime in minutes")
    success_rate: float = Field(default=0.0, description="Success rate (0-1)")
    error_count: int = Field(default=0, description="Number of errors")

    # Quality gates
    relevance_score: float | None = Field(None, description="Average relevance score (0-1)")
    timeliness_score: float | None = Field(None, description="Timeliness score (0-1)")
    completeness_score: float | None = Field(None, description="Completeness score (0-1)")


class IngestionJob(BaseModel):
    """Represents an ingestion job execution."""

    job_id: str = Field(..., description="Unique job identifier")
    job_name: str = Field(..., description="Job name")
    status: IngestionStatus = Field(..., description="Current status")
    source_ids: list[str] = Field(..., description="Sources to ingest from")

    # Execution details
    start_time: datetime | None = None
    end_time: datetime | None = None
    runtime_minutes: float = Field(default=0.0)

    # Results
    items_collected: int = Field(default=0)
    metrics: IngestionMetrics | None = None
    error_message: str | None = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class EthicalComplianceCheck(BaseModel):
    """Represents an ethical compliance check result."""

    source_id: str = Field(..., description="Source being checked")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # Compliance checks
    robots_txt_compliant: bool = Field(..., description="Respects robots.txt")
    rate_limit_compliant: bool = Field(..., description="Within rate limits")
    terms_of_service_compliant: bool = Field(..., description="Follows ToS")
    transparency_score: float = Field(..., description="Transparency score (0-1)")

    # Details
    violations: list[str] = Field(default_factory=list, description="Any violations found")
    recommendations: list[str] = Field(default_factory=list, description="Recommendations")
    overall_compliant: bool = Field(..., description="Overall compliance status")


class MultiSourceCoverage(BaseModel):
    """Analysis of coverage across multiple sources."""

    analysis_date: datetime = Field(default_factory=datetime.utcnow)
    total_sources: int = Field(..., description="Total number of sources")
    active_sources: int = Field(..., description="Number of active sources")

    # Distribution
    sources_by_type: dict[DataSourceType, int] = Field(default_factory=dict)
    sources_by_tier: dict[DataTier, int] = Field(default_factory=dict)

    # Coverage metrics
    coverage_diversity_score: float = Field(..., description="Diversity score (0-1)")
    tier_1_percentage: float = Field(..., description="Percentage of Tier 1 sources")

    # Gaps and recommendations
    coverage_gaps: list[str] = Field(default_factory=list, description="Identified gaps")
    recommendations: list[str] = Field(default_factory=list, description="Recommendations")


class TierClassificationMetrics(BaseModel):
    """Metrics for tier classification distribution."""

    date: datetime = Field(default_factory=datetime.utcnow)

    # Distribution counts
    tier_1_count: int = Field(default=0)
    tier_2_count: int = Field(default=0)
    tier_3_count: int = Field(default=0)

    # Percentages
    tier_1_percentage: float = Field(default=0.0)
    tier_2_percentage: float = Field(default=0.0)
    tier_3_percentage: float = Field(default=0.0)

    # Quality indicators
    avg_tier_1_relevance: float = Field(default=0.0, description="Avg Tier 1 relevance")
    avg_tier_2_relevance: float = Field(default=0.0, description="Avg Tier 2 relevance")
    avg_tier_3_relevance: float = Field(default=0.0, description="Avg Tier 3 relevance")


class AMBriefingDelivery(BaseModel):
    """AM Briefing delivery effectiveness metrics."""

    briefing_id: str = Field(..., description="Briefing identifier")
    delivery_date: datetime = Field(default_factory=datetime.utcnow)

    # Delivery metrics
    delivery_time: str = Field(..., description="Time delivered (e.g., '06:00 AM')")
    on_time: bool = Field(..., description="Delivered on time")

    # Content metrics
    total_items: int = Field(..., description="Total items in briefing")
    tier_1_items: int = Field(default=0)
    tier_2_items: int = Field(default=0)
    tier_3_items: int = Field(default=0)

    # Quality metrics
    relevance_score: float = Field(..., description="Overall relevance (0-1)")
    timeliness_score: float = Field(..., description="Timeliness score (0-1)")
    completeness_score: float = Field(..., description="Completeness score (0-1)")

    # User feedback (if available)
    user_rating: float | None = Field(None, description="User rating (0-5)")
    feedback: str | None = Field(None, description="User feedback")


# Request/Response models


class CreateDataSourceRequest(BaseModel):
    """Request to create a new data source."""

    name: str
    source_type: DataSourceType
    tier: DataTier
    url: str | None = None
    rate_limit: int | None = None
    cost_per_item: float | None = None
    metadata: dict = Field(default_factory=dict)


class StartIngestionJobRequest(BaseModel):
    """Request to start an ingestion job."""

    job_name: str = Field(..., description="Name for this job")
    source_ids: list[str] = Field(..., description="Sources to ingest from")
    parameters: dict | None = Field(default_factory=dict, description="Additional parameters")


class IngestionJobStatusResponse(BaseModel):
    """Response with ingestion job status."""

    job: IngestionJob
    message: str


class CoverageAnalysisResponse(BaseModel):
    """Response with coverage analysis."""

    coverage: MultiSourceCoverage
    recommendations: list[str]


class ComplianceCheckResponse(BaseModel):
    """Response with compliance check results."""

    checks: list[EthicalComplianceCheck]
    overall_compliant: bool
    violations_count: int
    recommendations: list[str]
