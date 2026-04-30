"""Configuration management for Ultrathink framework.

Handles:
- Environment variables
- API keys (Anthropic, OpenAI, Google Cloud)
- Service settings
- Security validation

Security: NEVER commit .env files. Use Google Secret Manager in production.
"""

import os
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Global settings for Ultrathink framework.

    Loads from:
    1. Environment variables
    2. .env file (development)
    3. Google Secret Manager (production)

    Usage:
        settings = Settings()
        client = Anthropic(api_key=settings.anthropic_api_key)
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Anthropic Claude API
    anthropic_api_key: str = Field(
        default="",
        description="Anthropic API key (get from console.anthropic.com)",
    )
    anthropic_model: str = Field(
        default="claude-sonnet-4-5-20250929",
        description="Default Claude model to use",
    )
    anthropic_max_tokens: int = Field(default=4096, ge=1, le=8192)
    anthropic_temperature: float = Field(default=0.7, ge=0.0, le=1.0)

    # OpenAI API (optional, for comparison/fallback)
    openai_api_key: str | None = Field(default=None)
    openai_model: str = Field(default="gpt-4o")

    # Google Cloud (for Vertex AI)
    google_project_id: str | None = Field(default=None)
    google_location: str = Field(default="us-central1")

    # Application settings
    environment: Literal["development", "staging", "production"] = Field(default="development")
    debug: bool = Field(default=False)
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(default="INFO")

    # Revenue tracking
    enable_revenue_tracking: bool = Field(default=True)
    enable_cost_monitoring: bool = Field(default=True)

    # Security
    enable_input_sanitization: bool = Field(default=True)
    max_request_size_mb: int = Field(default=10, ge=1, le=100)
    rate_limit_per_minute: int = Field(default=60, ge=1)

    # Performance
    enable_caching: bool = Field(default=True)
    cache_ttl_seconds: int = Field(default=300, ge=0)
    max_concurrent_requests: int = Field(default=10, ge=1, le=100)

    @field_validator("anthropic_api_key")
    @classmethod
    def validate_anthropic_key(cls, v: str) -> str:
        """Validate Anthropic API key format."""
        if not v:
            # Allow empty in development (will use placeholders)
            if os.getenv("ENVIRONMENT") == "production":
                raise ValueError("Anthropic API key required in production")
            return v

        if not v.startswith("sk-ant-"):
            raise ValueError("Invalid Anthropic API key format (must start with sk-ant-)")

        if len(v) < 20:
            raise ValueError("Anthropic API key too short")

        return v

    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.environment == "development"


# Global settings instance
settings = Settings()
