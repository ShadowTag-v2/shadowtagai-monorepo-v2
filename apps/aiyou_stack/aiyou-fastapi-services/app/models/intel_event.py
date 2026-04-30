"""IntelEvent Schema - Structured intelligence event for Gemini normalization layer.

This model defines the canonical format for all ingested intelligence items
after Gemini semantic extraction. Sits between raw scraping (Step 1A) and
JR Engine scoring (Step 2).
"""

import hashlib
from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, field_validator


class DocumentType(StrEnum):
    """Classification of document source type"""

    REGULATION = "regulation"
    DRAFT_BILL = "draft_bill"
    NEWS = "news"
    RFP = "rfp"
    COMPETITOR_RELEASE = "competitor_release"
    PRODUCT_DOC = "product_doc"
    BLOG = "blog"
    LAWSUIT = "lawsuit"
    GUIDANCE = "guidance"
    ACADEMIC = "academic"
    ANNOUNCEMENT = "announcement"
    UNKNOWN = "unknown"


class ChangeType(StrEnum):
    """Type of change represented by this event"""

    NEW_LAW = "new_law"
    AMENDMENT = "amendment"
    GUIDANCE = "guidance"
    ANNOUNCEMENT = "announcement"
    UPDATE = "update"
    REPEAL = "repeal"
    ENFORCEMENT_ACTION = "enforcement_action"
    INITIAL = "initial"  # First time seeing this document


class RiskTag(StrEnum):
    """Predefined risk categories for quick filtering"""

    COMPLIANCE_DEADLINE = "compliance_deadline"
    FINE_PER_VIOLATION = "fine_per_violation"
    CRIMINAL_PENALTY = "criminal_penalty"
    LICENSE_REQUIREMENT = "license_requirement"
    DISCLOSURE_MANDATE = "disclosure_mandate"
    DATA_RETENTION = "data_retention"
    AUDIT_REQUIREMENT = "audit_requirement"
    CONSUMER_PROTECTION = "consumer_protection"
    AI_SPECIFIC = "ai_specific"
    COMPETITIVE_THREAT = "competitive_threat"
    OPPORTUNITY = "opportunity"
    MARKET_SHIFT = "market_shift"


class JRHints(BaseModel):
    """Pre-filled hints for JR Engine scoring (Purpose/Reasons/Brakes)"""

    purpose_candidates: list[str] = Field(
        default_factory=list,
        description="Candidate Purpose statements: how this advances/threatens revenue",
    )
    reasons_candidates: list[str] = Field(
        default_factory=list,
        description="Candidate Reasons: defensible business impacts",
    )
    brakes_candidates: list[str] = Field(
        default_factory=list,
        description="Candidate Brakes: RA levels, mitigations, failure modes",
    )
    suggested_tier: int | None = Field(
        None,
        ge=1,
        le=3,
        description="Gemini's suggested tier (1=high, 2=medium, 3=low)",
    )
    urgency_score: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Urgency score 0-1 (1=immediate action needed)",
    )


class Impact(BaseModel):
    """Structured impact description"""

    description: str = Field(..., description="Human-readable impact description")
    affected_area: str = Field(
        default="general",
        description="Area affected: pricing, operations, legal, product, sales",
    )
    severity: str = Field(
        default="medium",
        description="Impact severity: low, medium, high, critical",
    )
    timeline: str | None = Field(
        None,
        description="When this impact takes effect: immediate, 30_days, 90_days, 1_year",
    )


class IntelEvent(BaseModel):
    """Canonical intelligence event schema.

    Produced by Gemini Normalization Layer from raw scraped documents.
    Consumed by JR Engine for Purpose/Reasons/Brakes scoring.
    """

    # Identity
    id: str = Field(..., description="Unique event ID (UUID or hash-based)")
    source_url: str = Field(..., description="Original source URL")
    source_type: DocumentType = Field(
        default=DocumentType.UNKNOWN,
        description="Classified document type",
    )

    # Metadata
    jurisdiction: str | None = Field(None, description="Jurisdiction code: US, US-CA, EU, UK, etc.")
    effective_date: datetime | None = Field(
        None,
        description="When this regulation/change takes effect",
    )
    publication_date: datetime | None = Field(None, description="When the source was published")

    # Classification
    topic_tags: list[str] = Field(
        default_factory=list,
        description="Topic tags: AI_disclosure, chatbot_labeling, data_privacy, etc.",
    )
    change_type: ChangeType = Field(
        default=ChangeType.INITIAL,
        description="Type of change this represents",
    )

    # Content
    title: str = Field(default="", description="Document title")
    summary: str = Field(default="", description="Gemini-generated summary (2-3 sentences)")
    impacts: list[Impact] = Field(
        default_factory=list,
        description="Structured list of business impacts",
    )
    risk_tags: list[RiskTag] = Field(
        default_factory=list,
        description="Applicable risk tags for quick filtering",
    )

    # JR Engine Integration
    jr_hints: JRHints = Field(
        default_factory=JRHints,
        description="Pre-filled hints for JR Engine scoring",
    )

    # Provenance
    raw_text_hash: str = Field(default="", description="SHA-256 hash of raw input text for dedup")
    gemini_model: str = Field(
        default="gemini-3.1-flash-lite-preview",
        description="Gemini model used for extraction",
    )
    gemini_confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Gemini's confidence in extraction accuracy",
    )
    extraction_version: str = Field(
        default="1.0.0",
        description="Version of extraction prompt/logic",
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When this event was created",
    )
    updated_at: datetime | None = Field(None, description="Last update timestamp")

    # Delta tracking
    previous_version_id: str | None = Field(
        None,
        description="ID of previous version for change tracking",
    )
    delta_summary: str | None = Field(None, description="Summary of changes vs previous version")

    # Raw storage reference
    raw_storage_path: str | None = Field(
        None,
        description="GCS path to raw document: gs://bucket/path",
    )

    @field_validator("raw_text_hash", mode="before")
    @classmethod
    def compute_hash_if_empty(cls, v: str) -> str:
        """Allow empty hash - will be computed during extraction"""
        return v or ""

    @staticmethod
    def hash_text(text: str) -> str:
        """Compute SHA-256 hash of text for deduplication"""
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def to_jr_input(self) -> dict[str, Any]:
        """Convert to JR Engine input format"""
        return {
            "event_id": self.id,
            "source_type": self.source_type.value,
            "jurisdiction": self.jurisdiction,
            "effective_date": self.effective_date.isoformat() if self.effective_date else None,
            "summary": self.summary,
            "impacts": [imp.model_dump() for imp in self.impacts],
            "risk_tags": [tag.value for tag in self.risk_tags],
            "jr_hints": self.jr_hints.model_dump(),
            "urgency": self.jr_hints.urgency_score,
            "confidence": self.gemini_confidence,
        }

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat() if v else None}


class IntelEventBatch(BaseModel):
    """Batch of intel events for pipeline processing"""

    events: list[IntelEvent] = Field(default_factory=list)
    batch_id: str = Field(..., description="Unique batch ID")
    source_job_id: str | None = Field(None, description="Parent ingestion job ID")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    total_raw_documents: int = Field(default=0, description="Total docs before filtering")
    extraction_errors: int = Field(default=0, description="Number of failed extractions")

    @property
    def success_rate(self) -> float:
        """Calculate extraction success rate"""
        total = len(self.events) + self.extraction_errors
        return len(self.events) / total if total > 0 else 0.0


class DeltaResult(BaseModel):
    """Result of comparing two versions of a document"""

    previous_id: str
    current_id: str
    changes: list[str] = Field(default_factory=list, description="List of changes detected")
    change_tags: list[str] = Field(
        default_factory=list,
        description="Tags for change types: reg_deadline, pricing, enforcement, etc.",
    )
    urgency: int = Field(default=3, ge=1, le=5, description="Urgency score 1-5 (5=most urgent)")
    summary: str = Field(default="", description="Human-readable delta summary")
