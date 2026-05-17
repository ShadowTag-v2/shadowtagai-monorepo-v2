# ⚠️ DEPRECATED — This file contains references to deprecated frameworks
# (AutoGen/AG2, LangGraph, Vertex AI Workbench) that are no longer part of
# the production CounselConduit architecture. These refs are slated for
# removal. See deploy-preflight findings 2026-05-17.
# Production path: apps/counselconduit/api/fastapi_kovel_enclave.py
"""Configuration management for agent-based governance system.

Implements environment-aware settings with validation and defaults
optimized for cost ($0.00027-$0.0012 per decision) and latency (2-5s).
"""

from enum import StrEnum
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvironmentType(StrEnum):
    """Deployment environment types."""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class ModelTier(StrEnum):
    """Gemini model tiers for cost/performance optimization."""

    FLASH_LITE = "gemini-3.1-flash-lite-preview-lite"  # $0.00027/decision
    FLASH = "gemini-3.1-flash-lite-preview"  # $0.0012/decision
    PRO = "gemini-3.1-flash-lite-preview"  # $0.0049/decision


class DeploymentMode(StrEnum):
    """Deployment infrastructure modes."""

    VERTEX_WORKBENCH = "vertex-workbench"  # Development
    CLOUD_RUN = "cloud-run"  # MVP/POC
    GKE_AUTOPILOT = "gke-autopilot"  # Production
    GKE_STANDARD = "gke-standard"  # Enterprise


class GovernanceSettings(BaseSettings):
    """Main configuration for governance system."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Environment
    environment: EnvironmentType = Field(
        default="development",
        description="Deployment environment",
    )
    deployment_mode: DeploymentMode = Field(
        default="vertex-workbench",
        description="Infrastructure deployment mode",
    )

    # Google Cloud
    gcp_project_id: str = Field(
        default="shadowtag-omega-v4",
        description="GCP project ID",
    )
    gcp_region: str = Field(
        default="us-central1",
        description="GCP region for services",
    )
    gcp_location: str = Field(
        default="us-central1",
        description="Vertex AI location",
    )

    # Model Configuration
    default_model: ModelTier = Field(
        default=ModelTier.FLASH,
        description="Default model tier (Flash recommended for production)",
    )
    model_cascading_enabled: bool = Field(
        default=True,
        description="Enable model cascading (30% to Lite, 70% to Flash/Pro)",
    )
    max_input_tokens: int = Field(
        default=1500,
        description="Maximum input tokens per decision",
    )
    max_output_tokens: int = Field(
        default=300,
        description="Maximum output tokens per decision",
    )
    temperature: float = Field(
        default=0.1,
        description="Model temperature (low for deterministic governance)",
    )

    # Cost Optimization
    batch_mode_enabled: bool = Field(
        default=True,
        description="Enable batch API for 50% cost savings on non-urgent requests",
    )
    caching_enabled: bool = Field(
        default=True,
        description="Enable context caching for 75-90% savings",
    )
    cache_ttl_seconds: int = Field(
        default=3600,
        description="Cache TTL for policy documents (1 hour default)",
    )
    cost_target_per_decision: float = Field(
        default=0.01,
        description="Target cost per decision in USD",
    )

    # Performance
    latency_target_p99_ms: int = Field(
        default=5000,
        description="Target P99 latency in milliseconds (5 seconds)",
    )
    latency_target_p50_ms: int = Field(
        default=2000,
        description="Target P50 latency in milliseconds (2 seconds)",
    )
    streaming_enabled: bool = Field(
        default=True,
        description="Enable streaming for faster perceived latency",
    )

    # Multi-Agent Coordination
    enable_gaas_trust_scoring: bool = Field(
        default=True,
        description="Enable GaaS-style trust factor mechanism",
    )
    enable_mi9_telemetry: bool = Field(
        default=True,
        description="Enable MI9 agentic telemetry schema",
    )
    enable_kosmos_reasoning: bool = Field(
        default=False,
        description="Enable Kosmos long-horizon reasoning (resource intensive)",
    )
    trust_score_threshold_high: float = Field(
        default=0.7,
        description="Trust score threshold for high trust tier",
    )
    trust_score_threshold_low: float = Field(
        default=0.3,
        description="Trust score threshold for low trust tier",
    )

    # Security & Fallback
    circuit_breaker_enabled: bool = Field(
        default=True,
        description="Enable circuit breaker pattern",
    )
    circuit_breaker_failure_threshold: int = Field(
        default=5,
        description="Consecutive failures before circuit opens",
    )
    circuit_breaker_timeout_seconds: int = Field(
        default=60,
        description="Timeout before attempting recovery",
    )
    opa_fallback_enabled: bool = Field(
        default=True,
        description="Enable OPA rule engine fallback",
    )
    confidence_threshold: float = Field(
        default=0.6,
        description="Minimum confidence score to accept decision",
    )
    escalation_enabled: bool = Field(
        default=True,
        description="Enable human-in-the-loop escalation",
    )
    escalation_threshold: float = Field(
        default=0.6,
        description="Confidence threshold triggering escalation",
    )

    # Policy RAG
    vector_db_type: Literal["vertex-ai", "pgvector"] = Field(
        default="pgvector",
        description="Vector database for policy retrieval",
    )
    embedding_model: str = Field(
        default="textembedding-gecko@latest",
        description="Embedding model for policy documents",
    )
    retrieval_top_k: int = Field(
        default=5,
        description="Top K policy chunks to retrieve",
    )
    chunk_size: int = Field(
        default=500,
        description="Token size for policy document chunks",
    )
    chunk_overlap: int = Field(
        default=50,
        description="Overlap between chunks",
    )

    # PostgreSQL (for pgvector)
    postgres_host: str | None = Field(
        default=None,
        description="PostgreSQL host for pgvector",
    )
    postgres_port: int = Field(
        default=5432,
        description="PostgreSQL port",
    )
    postgres_database: str = Field(
        default="governance",
        description="PostgreSQL database name",
    )
    postgres_user: str | None = Field(
        default=None,
        description="PostgreSQL username",
    )
    postgres_password: str | None = Field(
        default=None,
        description="PostgreSQL password",
    )

    # Redis (for circuit breaker state)
    redis_host: str = Field(
        default="localhost",
        description="Redis host",
    )
    redis_port: int = Field(
        default=6379,
        description="Redis port",
    )
    redis_db: int = Field(
        default=0,
        description="Redis database number",
    )

    # Observability
    agentops_api_key: str | None = Field(
        default=None,
        description="AgentOps API key for observability",
    )
    enable_cloud_trace: bool = Field(
        default=True,
        description="Enable Google Cloud Trace",
    )
    enable_cloud_logging: bool = Field(
        default=True,
        description="Enable Google Cloud Logging",
    )
    audit_trail_retention_days: int = Field(
        default=180,
        description="Audit trail retention (6 months for EU AI Act)",
    )

    # Migration & Shadow Mode
    shadow_mode_enabled: bool = Field(
        default=False,
        description="Enable shadow mode (dual evaluation without enforcement)",
    )
    shadow_mode_sample_rate: float = Field(
        default=1.0,
        description="Sample rate for shadow mode (0.0-1.0)",
    )
    judge6_endpoint: str | None = Field(
        default=None,
        description="Legacy Judge 6 endpoint for comparison",
    )

    # Rate Limiting
    rate_limit_rpm: int = Field(
        default=2000,
        description="Requests per minute (Tier 1 = 2000)",
    )
    rate_limit_tpm: int = Field(
        default=1000000,
        description="Tokens per minute",
    )

    @field_validator("confidence_threshold", "escalation_threshold")
    @classmethod
    def validate_threshold(cls, v: float) -> float:
        """Validate threshold is between 0 and 1."""
        if not 0 <= v <= 1:
            raise ValueError("Threshold must be between 0 and 1")
        return v

    @field_validator("trust_score_threshold_high", "trust_score_threshold_low")
    @classmethod
    def validate_trust_threshold(cls, v: float) -> float:
        """Validate trust threshold is between 0 and 1."""
        if not 0 <= v <= 1:
            raise ValueError("Trust threshold must be between 0 and 1")
        return v


# Global settings instance
settings = GovernanceSettings()
