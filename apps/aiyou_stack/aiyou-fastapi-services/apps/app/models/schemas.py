# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Pydantic schemas for PNKLN Core Stack™ API
Matches API specs from docs/cor8-shadowtag_v4-global-edge-fabric/09-implementation/api-schemas.md
"""

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, HttpUrl

# ============================================================================
# INGESTION API SCHEMAS (PNKLN: Preparation)
# ============================================================================


class SourceType(StrEnum):
    """Data source types for ingestion"""

    NEWS_API = "news_api"
    YOUTUBE = "youtube"
    TWITTER = "twitter"
    RSS = "rss"
    RESEARCH = "research"
    GOVERNMENT = "government"


class Source(BaseModel):
    """Source metadata for ingestion item"""

    type: SourceType
    url: HttpUrl
    domain: str


class ContentMetadata(BaseModel):
    """Content metadata"""

    tags: list[str] = Field(default_factory=list)
    priority: str = "medium"  # low | medium | high


class Content(BaseModel):
    """Content body for ingestion"""

    title: str
    summary: str | None = None
    full_text: str
    published_at: datetime


class IngestionSubmitRequest(BaseModel):
    """Request schema for POST /ingestion/submit"""

    source: Source
    content: Content
    metadata: ContentMetadata = Field(default_factory=ContentMetadata)


class IngestionSubmitResponse(BaseModel):
    """Response schema for POST /ingestion/submit"""

    item_id: str
    status: str = "accepted"
    message: str = "Item queued for classification"
    estimated_processing_time_ms: int = 5000
    next_steps: list[str] = Field(
        default_factory=lambda: ["tier_classification", "validation", "attestation"],
    )


class TierClassification(BaseModel):
    """Tier classification results"""

    tier: int = Field(ge=1, le=3)  # 1=high-value, 2=medium, 3=low
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str
    tags: list[str]


class ValidationResult(BaseModel):
    """Validation result summary"""

    status: str  # passed | failed | flagged
    atp_5_19_coverage: float
    judge_id: str


class ShadowTagAttestation(BaseModel):
    """ShadowTag attestation metadata"""

    attestation_level: str  # L0-L4
    signature: str
    verification_url: HttpUrl


class IngestionItemResponse(BaseModel):
    """Response schema for GET /ingestion/items/{item_id}"""

    item_id: str
    status: str  # pending | processing | completed | failed
    classification: TierClassification | None = None
    validation_result: ValidationResult | None = None
    shadowtag: ShadowTagAttestation | None = None
    processing_time_ms: int | None = None


class SourceHealth(BaseModel):
    """Health status for a data source"""

    id: str
    type: SourceType
    status: str  # healthy | degraded | failed | rate_limited
    daily_quota: int
    quota_used: int
    last_successful_fetch: datetime
    tier_1_yield: float  # Percentage of Tier 1 items from this source


class SourceCoverageResponse(BaseModel):
    """Response schema for GET /ingestion/sources"""

    sources: list[SourceHealth]
    summary: dict[str, int] = Field(
        default_factory=lambda: {
            "total_sources": 0,
            "healthy": 0,
            "degraded": 0,
            "failed": 0,
        },
    )


# ============================================================================
# VALIDATION API SCHEMAS (PNKLN: Judge 6)
# ============================================================================


class ValidationProfile(StrEnum):
    """Validation profiles for different use cases"""

    DEFENSE_ISR = "defense_isr"
    AVIATION = "aviation"
    FAANG = "faang"
    GENERAL = "general"


class ValidationOptions(BaseModel):
    """Validation configuration options"""

    strict_mode: bool = True
    require_human_review: bool = False
    atp_5_19_coverage_threshold: float = 0.98


class ValidationRequest(BaseModel):
    """Request schema for POST /validation/validate"""

    item_id: str
    validation_profile: ValidationProfile = ValidationProfile.GENERAL
    options: ValidationOptions = Field(default_factory=ValidationOptions)


class ATP519Scores(BaseModel):
    """ATP 5-19 compliance scores"""

    source_reliability: str  # A-F scale with description
    credibility: int = Field(ge=1, le=6)  # 1=Confirmed, 6=Improbable
    timeliness: str  # "current (<24h)" | "current (<48h)" | "stale"
    completeness: float = Field(ge=0.0, le=1.0)
    relevance: int = Field(ge=0, le=3)
    classification: str  # UNCLASSIFIED | CONFIDENTIAL | SECRET | etc.


class JRCompliance(BaseModel):
    """Joint Requirements compliance checks"""

    itar_check: str  # passed | failed | flagged
    ear_check: str  # passed | failed | flagged
    nist_rmf_controls: str  # Level 1-6 status
    opsec_violations: list[str] = Field(default_factory=list)


class QualityMetrics(BaseModel):
    """Quality metrics for validation"""

    coverage: float = Field(ge=0.0, le=1.0)
    false_positive_probability: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)


class FailureReason(BaseModel):
    """Detailed failure reason"""

    rule: str
    severity: str  # low | medium | high | critical
    description: str
    matched_text: str | None = None


class FlagReason(BaseModel):
    """Reason for flagging item for review"""

    rule: str
    severity: str
    description: str
    recommendation: str


class ValidationResponse(BaseModel):
    """Response schema for POST /validation/validate"""

    validation_id: str
    result: str  # PASS | FAIL | FLAG
    atp_5_19_scores: ATP519Scores
    jr_compliance: JRCompliance
    quality_metrics: QualityMetrics | None = None
    next_action: str | None = None
    latency_ms: float
    failure_reasons: list[FailureReason] | None = None
    flag_reasons: list[FlagReason] | None = None
    recommended_action: str | None = None
    human_review_required: bool = False


class RuleCategory(BaseModel):
    """Rule category metadata"""

    category: str
    rule_count: int
    description: str


class RulesResponse(BaseModel):
    """Response schema for GET /validation/rules"""

    atp_5_19_rules: dict[str, Any]
    jr_compliance_checks: dict[str, Any]


class BatchValidationRequest(BaseModel):
    """Request schema for POST /validation/batch"""

    items: list[dict[str, str]]  # List of {"item_id": "..."}
    validation_profile: ValidationProfile = ValidationProfile.GENERAL
    options: dict[str, Any] = Field(default_factory=dict)


class BatchValidationResult(BaseModel):
    """Single result in batch validation"""

    item_id: str
    validation_id: str
    result: str  # PASS | FAIL | FLAG
    latency_ms: float


class BatchValidationResponse(BaseModel):
    """Response schema for POST /validation/batch"""

    batch_id: str
    results: list[BatchValidationResult]
    summary: dict[str, Any]


# ============================================================================
# HEALTH & STATUS SCHEMAS
# ============================================================================


class HealthResponse(BaseModel):
    """API health check response"""

    status: str = "healthy"
    version: str = "1.0.0"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    services: dict[str, str] = Field(
        default_factory=lambda: {
            "ingestion": "operational",
            "validation": "operational",
            "gemini_api": "operational",
        },
    )
