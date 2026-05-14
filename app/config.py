# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Configuration management for kernel chain service."""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Service configuration with validation."""

    # Google Cloud Configuration
    google_cloud_project: str | None = None
    google_application_credentials: str | None = None

    # Gemini API Configuration
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.0-flash-exp"

    # Service Configuration
    service_name: str = "pnkln-kernel-chain"
    log_level: str = "INFO"
    enable_metrics: bool = True

    # Performance Thresholds (from architecture spec)
    max_latency_p99_ms: int = 90
    max_cost_per_decision: float = 0.001
    target_token_reduction_pct: int = 90

    # Kernel-specific Configuration
    kernel_1_max_latency_ms: int = 40
    kernel_2_max_latency_ms: int = 12
    kernel_1_max_output_tokens: int = 2500
    confidence_threshold: float = 0.85

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
