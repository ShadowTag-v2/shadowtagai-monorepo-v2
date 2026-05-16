# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Configuration management for YouAi Governance Service
"""

from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
  """Service configuration with validation."""

  # Google Cloud Configuration
  google_cloud_project: str | None = None
  google_application_credentials: str | None = None

  # Gemini API Configuration
  gemini_api_key: str | None = None
  gemini_model: str = "gemini-3.1-flash-exp"
  gemini_project_id: str | None = None
  gemini_location: str | None = None

  # Service Configuration
  service_name: str = "shadowtagai-kernel-chain"
  service_version: str = "0.1.0"

  # Performance Thresholds (from architecture spec)
  max_latency_p99_ms: int = 10000  # Increased for Gemini API latency
  max_cost_per_decision: float = 0.001
  target_token_reduction_pct: int = 90

  # Kernel Specific Configs
  kernel_1_max_latency_ms: int = 2000
  kernel_1_max_output_tokens: int = 1024
  kernel_2_max_latency_ms: int = 100
  confidence_threshold: float = 0.85

  # Security
  secret_key: str = Field(..., env="SECRET_KEY")
  api_key_header: str = Field(default="X-API-Key")
  cors_origins: list[str] = Field(default=[])

  # Observability
  otel_exporter_otlp_endpoint: str = Field(default="http://localhost:4317")
  enable_metrics: bool = Field(default=True)
  enable_tracing: bool = Field(default=True)
  log_level: str = Field(default="INFO")

  # App Info
  app_name: str = Field(default="AiYou Platform")
  app_version: str = Field(default="0.1.0")
  environment: str = Field(default="development")
  debug: bool = Field(default=False)

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
  rate_limit_requests_per_minute: int = Field(default=60)
  rate_limit_burst: int = Field(default=10)
  rate_limit_upload_per_hour: int = Field(default=20)

  # Database
  database_url: str = Field(default="sqlite:///./aiyou.db")
  database_echo: bool = Field(default=False)
  database_pool_size: int = Field(default=5)
  database_max_overflow: int = Field(default=10)

  # JWT / Auth
  access_token_expire_minutes: int = Field(default=30)
  refresh_token_expire_days: int = Field(default=7)
  algorithm: str = Field(default="HS256")

  # Redis
  redis_url: str | None = None
  redis_max_connections: int = Field(default=20)

  # Feature Flags
  blockchain_integration_enabled: bool = Field(default=False)
  persona_iq_override: int = Field(default=160)

  # =========================================================================
  # ActiveShield Modular Compliance Framework (MCF) Settings
  # =========================================================================

  # MCF Core Settings
  mcf_enabled: bool = Field(default=True, description="Enable MCF compliance engine")
  mcf_default_modules: list[str] = Field(
    default=["eu_ai_act", "gdpr"],
    description="Default compliance modules to enable",
  )

  # ShadowTag v2 Audit Settings
  shadowtag_v2_enabled: bool = Field(
    default=True, description="Enable ShadowTag v2 ledger"
  )
  shadowtag_retention_years: int = Field(
    default=7, description="Audit log retention period"
  )
  shadowtag_enabled: bool = Field(default=True)
  shadowtag_private_key: str | None = None
  shadowtag_chain_id: str | None = None
  ipfs_gateway_url: str | None = Field(
    default=None, description="IPFS gateway for hash pinning"
  )

  # Compliance Module Settings
  mcf_eu_ai_act_enabled: bool = Field(default=True)
  mcf_gdpr_enabled: bool = Field(default=True)
  mcf_dsa_enabled: bool = Field(default=True)
  mcf_ca_sb_243_enabled: bool = Field(default=True)
  mcf_hipaa_enabled: bool = Field(default=True)

  # Pricing Tier Configuration
  mcf_pricing_tier: str = Field(
    default="pro", description="Default pricing tier (free, pro, enterprise)"
  )
  mcf_base_price_usd: float = Field(default=199.0, description="Base monthly price")
  mcf_addon_price_usd: float = Field(default=50.0, description="Per-module addon price")

  # API Rate Limits for MCF
  mcf_rate_limit_assessments: int = Field(
    default=1000, description="Monthly assessment limit"
  )
  mcf_rate_limit_api_calls: int = Field(
    default=50000, description="Monthly API call limit"
  )

  # Post-Generation Validation (GPT Store Pattern)
  mcf_post_gen_validation_enabled: bool = Field(default=True)
  mcf_auto_remediation_enabled: bool = Field(
    default=False, description="Auto-fix non-critical violations"
  )

  @field_validator("cors_origins", mode="before")
  def parse_cors_origins(cls, v):
    if isinstance(v, str):
      return [origin.strip() for origin in v.split(",")]
    return v

  model_config = SettingsConfigDict(
    env_file=".env", case_sensitive=False, extra="ignore"
  )


@lru_cache
def get_settings() -> Settings:
  """Get cached settings instance"""
  return Settings()


settings = get_settings()
