"""
Configuration management for ShadowTagAI Governance Service
"""

from functools import lru_cache

from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Service configuration with validation."""

    # Google Cloud Configuration
    google_cloud_project: Optional[str] = None
    google_application_credentials: Optional[str] = None

    # Gemini API Configuration
    gemini_api_key: Optional[str] = None
    gemini_model: str = "gemini-2.0-flash-exp"

    # Service Configuration
    service_name: str = "shadowtagai-kernel-chain"
    log_level: str = "INFO"
    enable_metrics: bool = True

    # Performance Thresholds (from architecture spec)
    max_latency_p99_ms: int = 10000  # Increased for Gemini API latency
    max_cost_per_decision: float = 0.001
    target_token_reduction_pct: int = 90

    # Security
    secret_key: str = Field(default="dev-secret-key-change-in-production")
    api_key_header: str = Field(default="X-API-Key")
    cors_origins: list[str] = Field(default=["*"])

    # Observability
    otel_exporter_otlp_endpoint: str = Field(default="http://localhost:4317")
    enable_metrics: bool = Field(default=True)
    enable_tracing: bool = Field(default=True)
    log_level: str = Field(default="INFO")

    # Governance Frameworks
    eu_ai_act_enabled: bool = Field(default=True)
    dsa_vlop_mode: bool = Field(default=False)
    nist_rmf_enabled: bool = Field(default=True)
    iso_42001_enabled: bool = Field(default=True)

    # Content Safety
    brand_safety_threshold: float = Field(default=0.85)
    content_moderation_enabled: bool = Field(default=True)
    c2pa_verification_enabled: bool = Field(default=True)

    # Adtech Compliance
    vast_version: str = Field(default="4.3")
    om_sdk_enabled: bool = Field(default=True)
    privacy_sandbox_enabled: bool = Field(default=True)

    # Accessibility
    wcag_level: str = Field(default="AA")
    coppa_mode_enabled: bool = Field(default=True)
    age_verification_required: bool = Field(default=True)

    # Rate Limiting
    rate_limit_enabled: bool = Field(default=True)
    rate_limit_requests: int = Field(default=100)
    rate_limit_window: int = Field(default=60)

    # Feature Flags
    blockchain_integration_enabled: bool = Field(default=False)
    persona_iq_override: int = Field(default=160)

    @validator("cors_origins", pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
