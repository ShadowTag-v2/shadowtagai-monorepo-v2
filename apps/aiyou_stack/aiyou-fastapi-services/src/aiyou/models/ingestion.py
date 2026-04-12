"""
ShadowTag-v4 Content Ingestion Models
Handles Gemini-powered content analysis, moderation, and verification
"""

import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import JSON, Boolean, Column, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship

from ..database import Base


class IngestionStatus(StrEnum):
    """Ingestion pipeline status"""

    PENDING = "pending"
    ANALYZING = "analyzing"
    APPROVED = "approved"
    REJECTED = "rejected"
    REQUIRES_REVIEW = "requires_review"
    FAILED = "failed"


class ContentType(StrEnum):
    """Types of content that can be ingested"""

    VIDEO = "video"
    IMAGE = "image"
    AUDIO = "audio"
    TEXT = "text"
    DOCUMENT = "document"
    GAME_ASSET = "game_asset"
    PRODUCT_IMAGE = "product_image"
    USER_GENERATED = "user_generated"


class ModerationCategory(StrEnum):
    """Gemini moderation categories"""

    SAFE = "safe"
    VIOLENCE = "violence"
    HATE_SPEECH = "hate_speech"
    SEXUAL = "sexual"
    DANGEROUS = "dangerous"
    HARASSMENT = "harassment"
    ILLEGAL = "illegal"


class IngestionJob(Base):
    """
    Content ingestion job processed by Gemini
    Tracks the full lifecycle from upload to approval
    """

    __tablename__ = "ingestion_jobs"

    # Primary identification
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)

    # Content metadata
    content_type = Column(SQLEnum(ContentType), nullable=False, index=True)
    file_path = Column(String(1000), nullable=False)  # GCS path
    file_size_bytes = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False)
    original_filename = Column(String(500))

    # Processing status
    status = Column(
        SQLEnum(IngestionStatus), default=IngestionStatus.PENDING, nullable=False, index=True
    )
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Gemini analysis results
    gemini_model_version = Column(String(50))  # e.g., "gemini-1.5-pro"
    gemini_analysis_id = Column(String(100), index=True)  # Vertex AI request ID
    gemini_tokens_used = Column(Integer, default=0)  # For cost tracking

    # Content analysis (from Gemini)
    detected_labels = Column(JSON)  # ["sunset", "beach", "ocean"]
    detected_objects = Column(JSON)  # [{"object": "person", "confidence": 0.95}]
    detected_text = Column(Text)  # OCR results
    detected_language = Column(String(10))  # ISO 639-1 code

    # Moderation results
    moderation_category = Column(
        SQLEnum(ModerationCategory), default=ModerationCategory.SAFE, index=True
    )
    moderation_confidence = Column(Integer)  # 0-100
    moderation_details = Column(JSON)  # Detailed scores per category
    requires_human_review = Column(Boolean, default=False, index=True)

    # Quality assessment
    quality_score = Column(Integer)  # 0-100 (resolution, clarity, etc)
    quality_issues = Column(JSON)  # ["low_resolution", "blurry"]

    # Business logic
    brand_safety_score = Column(Integer)  # 0-100
    copyright_detected = Column(Boolean, default=False, index=True)
    copyright_claims = Column(JSON)  # Potential copyright matches

    # Enrichment data (Gemini-generated)
    generated_title = Column(String(500))
    generated_description = Column(Text)
    generated_tags = Column(JSON)  # Auto-suggested tags
    generated_transcript = Column(Text)  # For video/audio

    # ShadowTag verification
    shadowtag_signature = Column(String(500), index=True)
    verification_chain_id = Column(String(100), index=True)

    # Cost tracking
    processing_cost_cents = Column(Integer, default=0)  # Gemini API costs
    storage_cost_cents = Column(Integer, default=0)  # GCS costs

    # Relationships
    user = relationship("User", back_populates="ingestion_jobs")
    reviews = relationship("IngestionReview", back_populates="job", cascade="all, delete-orphan")

    # Audit
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("idx_ingestion_user_status", "user_id", "status"),
        Index("idx_ingestion_created", "created_at"),
        Index("idx_ingestion_moderation", "moderation_category", "requires_human_review"),
    )


class IngestionReview(Base):
    """
    Human review of ingestion jobs flagged by Gemini
    Trust & Safety team decisions
    """

    __tablename__ = "ingestion_reviews"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String(36), ForeignKey("ingestion_jobs.id"), nullable=False, index=True)
    reviewer_id = Column(String(36), ForeignKey("users.id"), nullable=False)

    # Review decision
    decision = Column(SQLEnum(IngestionStatus), nullable=False)  # APPROVED or REJECTED
    decision_reason = Column(Text)
    policy_violation = Column(String(200))  # Which policy was violated

    # Review metadata
    reviewed_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    review_duration_seconds = Column(Integer)  # Time spent reviewing

    # Escalation
    escalated = Column(Boolean, default=False)
    escalation_reason = Column(Text)

    # Training data
    gemini_correct = Column(Boolean)  # Was Gemini's assessment correct?
    feedback_to_model = Column(JSON)  # Data for fine-tuning

    # Relationships
    job = relationship("IngestionJob", back_populates="reviews")
    reviewer = relationship("User", foreign_keys=[reviewer_id])

    __table_args__ = (
        Index("idx_review_job", "job_id"),
        Index("idx_review_reviewer", "reviewer_id"),
    )


class GeminiUsageMetrics(Base):
    """
    Track Gemini API usage and costs for billing optimization
    """

    __tablename__ = "gemini_usage_metrics"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Time bucket
    date = Column(DateTime(timezone=True), nullable=False, index=True)
    hour = Column(Integer, nullable=False)  # 0-23

    # Model usage
    model_name = Column(String(50), nullable=False, index=True)

    # Request counts
    requests_total = Column(Integer, default=0)
    requests_succeeded = Column(Integer, default=0)
    requests_failed = Column(Integer, default=0)
    requests_ratelimited = Column(Integer, default=0)

    # Token usage
    tokens_input = Column(Integer, default=0)
    tokens_output = Column(Integer, default=0)
    tokens_total = Column(Integer, default=0)

    # Costs (in cents)
    cost_input_cents = Column(Integer, default=0)
    cost_output_cents = Column(Integer, default=0)
    cost_total_cents = Column(Integer, default=0)

    # Performance
    avg_latency_ms = Column(Integer)
    p95_latency_ms = Column(Integer)
    p99_latency_ms = Column(Integer)

    # Content analysis breakdown
    images_processed = Column(Integer, default=0)
    videos_processed = Column(Integer, default=0)
    text_processed = Column(Integer, default=0)
    audio_processed = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        Index("idx_metrics_date_model", "date", "model_name"),
        Index("idx_metrics_created", "created_at"),
    )


class ContentEmbedding(Base):
    """
    Vector embeddings generated by Gemini for similarity search
    Enables content discovery, duplicate detection, recommendation
    """

    __tablename__ = "content_embeddings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(
        String(36), ForeignKey("ingestion_jobs.id"), nullable=False, unique=True, index=True
    )

    # Embedding metadata
    model_name = Column(String(50), nullable=False)  # "textembedding-gecko@003"
    embedding_dimensions = Column(Integer, nullable=False)  # 768 or 1408

    # Vector (stored in separate vector DB like Vertex AI Matching Engine or pgvector)
    # For PostgreSQL with pgvector extension:
    # embedding_vector = Column(Vector(768))  # Requires pgvector extension
    # For now, store reference:
    vector_index_id = Column(String(100), index=True)

    # Similarity search metadata
    content_hash = Column(String(64), index=True)  # For duplicate detection
    nearest_neighbors = Column(JSON)  # Cached top-10 similar content IDs

    # Use cases
    used_for_recommendations = Column(Boolean, default=True)
    used_for_moderation = Column(Boolean, default=True)
    used_for_search = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.utcnow)

    # Relationships
    job = relationship("IngestionJob")


class AutoModerationRule(Base):
    """
    Automated moderation rules based on Gemini outputs
    Configurable thresholds for auto-approve/reject/review
    """

    __tablename__ = "auto_moderation_rules"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Rule identification
    name = Column(String(200), nullable=False)
    description = Column(Text)
    enabled = Column(Boolean, default=True, index=True)

    # Content type targeting
    content_types = Column(JSON)  # ["video", "image"] or null for all

    # Condition (JSON logic)
    condition = Column(JSON, nullable=False)
    # Example: {"moderation_category": "violence", "moderation_confidence": ">80"}

    # Action
    action = Column(SQLEnum(IngestionStatus), nullable=False)  # APPROVED, REJECTED, REQUIRES_REVIEW
    action_reason = Column(String(500))

    # Priority (higher = runs first)
    priority = Column(Integer, default=100, index=True)

    # Effectiveness tracking
    times_triggered = Column(Integer, default=0)
    false_positives = Column(Integer, default=0)  # Human overrides
    false_negatives = Column(Integer, default=0)

    # Audit
    created_by = Column(String(36), ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.utcnow)

    __table_args__ = (Index("idx_rules_enabled_priority", "enabled", "priority"),)
