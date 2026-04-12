"""PNKLN Core Stack Data Models"""

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class SourceType(StrEnum):
    """Supported ingestion source types"""

    YOUTUBE = "youtube"
    TWITTER = "twitter"
    NEWS = "news"
    RSS = "rss"
    WEB = "web"
    API = "api"


class TierClassification(StrEnum):
    """Data tier classification levels"""

    TIER_1 = "tier_1"  # High-value, priority content
    TIER_2 = "tier_2"  # Medium-value content
    TIER_3 = "tier_3"  # Low-value content


class ValidationStatus(StrEnum):
    """Judge #6 validation status"""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    REVIEW_REQUIRED = "review_required"


class IngestedItem(BaseModel):
    """Model for ingested data item"""

    id: str
    source_type: SourceType
    source_url: str
    title: str | None = None
    content: str
    tier: TierClassification
    relevance_score: float = Field(ge=0.0, le=1.0)
    cost: float = Field(ge=0.0)
    ingested_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] | None = None
    validation_status: ValidationStatus = ValidationStatus.PENDING


class IngestionMetrics(BaseModel):
    """Gemini Ingestion Layer metrics"""

    date: datetime = Field(default_factory=datetime.utcnow)
    items_ingested: int = Field(ge=0)
    unique_sources: int = Field(ge=0)
    average_cost_per_item: float = Field(ge=0.0)
    runtime_minutes: float = Field(ge=0.0)

    # Source breakdown
    youtube_items: int = Field(default=0, ge=0)
    twitter_items: int = Field(default=0, ge=0)
    news_items: int = Field(default=0, ge=0)
    rss_items: int = Field(default=0, ge=0)

    # Tier distribution
    tier_1_count: int = Field(default=0, ge=0)
    tier_2_count: int = Field(default=0, ge=0)
    tier_3_count: int = Field(default=0, ge=0)

    # Quality metrics
    average_relevance_score: float = Field(ge=0.0, le=1.0)
    quality_gate_passed: bool = False


class ValidationMetrics(BaseModel):
    """Judge #6 validation metrics"""

    date: datetime = Field(default_factory=datetime.utcnow)
    items_validated: int = Field(ge=0)
    approved_count: int = Field(default=0, ge=0)
    rejected_count: int = Field(default=0, ge=0)
    review_required_count: int = Field(default=0, ge=0)

    # Error rates
    false_positive_rate: float = Field(ge=0.0, le=1.0)
    false_negative_rate: float = Field(ge=0.0, le=1.0)

    # Performance
    average_latency_ms: float = Field(ge=0.0)
    p99_latency_ms: float = Field(ge=0.0)

    # Confidence
    average_confidence: float = Field(ge=0.0, le=1.0)


class EthicalComplianceReport(BaseModel):
    """Ethical crawling compliance report"""

    date: datetime = Field(default_factory=datetime.utcnow)
    robots_txt_violations: int = Field(default=0, ge=0)
    rate_limit_violations: int = Field(default=0, ge=0)
    total_requests: int = Field(ge=0)
    compliance_score: float = Field(ge=0.0, le=1.0)
    flagged_domains: list[str] = Field(default_factory=list)


class QualityGateCheck(BaseModel):
    """Quality gate validation results"""

    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # Gate checks
    daily_items_met: bool
    unique_sources_met: bool
    cost_per_item_met: bool
    relevance_score_met: bool

    # Actual values
    actual_daily_items: int
    actual_unique_sources: int
    actual_cost_per_item: float
    actual_relevance_score: float

    # Overall
    all_gates_passed: bool


class AMBriefing(BaseModel):
    """Morning briefing delivery model"""

    date: datetime = Field(default_factory=datetime.utcnow)
    format: str = "markdown"

    # Summary stats
    new_items_count: int
    tier_1_highlights: list[IngestedItem]

    # Quality overview
    ingestion_metrics: IngestionMetrics
    validation_metrics: ValidationMetrics | None = None
    quality_gate: QualityGateCheck

    # Delivered
    delivered: bool = False
    delivery_time: datetime | None = None


class GKENamespaceStatus(BaseModel):
    """Status for a GKE namespace in PNKLN stack"""

    namespace: str
    healthy: bool
    pod_count: int = Field(ge=0)
    last_check: datetime = Field(default_factory=datetime.utcnow)
    issues: list[str] = Field(default_factory=list)


class PNKLNStackStatus(BaseModel):
    """Overall PNKLN Core Stack status"""

    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # Namespace statuses
    ingestion_status: GKENamespaceStatus
    validation_status: GKENamespaceStatus
    processing_status: GKENamespaceStatus
    delivery_status: GKENamespaceStatus

    # Overall health
    overall_healthy: bool
    active_alerts: list[str] = Field(default_factory=list)
