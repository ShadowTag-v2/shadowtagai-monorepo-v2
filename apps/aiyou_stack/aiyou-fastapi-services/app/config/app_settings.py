"""Application configuration management.

Migrated from the standalone app/config.py that was shadowed by the
app/config/ package directory.
"""

import os
from functools import lru_cache
from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class SandboxSettings(BaseSettings):
    """Sandbox configuration settings."""

    enabled: bool = Field(default=True, description="Enable sandboxing features")
    max_execution_time: int = Field(default=30, description="Maximum execution time in seconds")
    max_memory_mb: int = Field(default=512, description="Maximum memory usage in MB")
    max_cpu_percent: float = Field(default=80.0, description="Maximum CPU usage percentage")
    allowed_modules: list[str] = Field(
        default=[
            "math",
            "json",
            "datetime",
            "re",
            "collections",
            "itertools",
            "functools",
        ],
        description="List of allowed Python modules for code execution",
    )
    blocked_builtins: list[str] = Field(
        default=[
            "eval",
            "exec",
            "compile",
            "__import__",
            "open",
            "input",
            "exit",
            "quit",
        ],
        description="List of blocked built-in functions",
    )
    allowed_write_paths: list[str] = Field(
        default=["/tmp/sandbox-temp"],
        description="Filesystem paths allowed for write operations",
    )
    allowed_domains: list[str] = Field(
        default=[
            "api.openai.com",
            "api.anthropic.com",
        ],
        description="Network domains allowed for access",
    )

    model_config = SettingsConfigDict(
        env_prefix="SANDBOX_",
        case_sensitive=False,
    )

    @field_validator("max_cpu_percent")
    @classmethod
    def validate_cpu_percent(cls, v: float) -> float:
        """Validate CPU percentage is between 0 and 100."""
        if not 0 < v <= 100:
            raise ValueError("CPU percentage must be between 0 and 100")
        return v


class AppSettings(BaseSettings):
    """Application settings."""

    # Application
    app_name: str = Field(default="ShadowTag-v4 Platform")
    app_version: str = Field(default="0.1.0")
    debug: bool = Field(default=False)
    environment: str = Field(default="development")

    # API
    api_prefix: str = Field(default="/api/v1")
    cors_origins: list[str] = Field(default=[])

    # Server
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    reload: bool = Field(default=True)
    workers: int = Field(default=1)

    # Security
    secret_key: str = Field(...)  # Required — no default
    access_token_expire_minutes: int = Field(default=30)
    refresh_token_expire_days: int = Field(default=7)
    algorithm: str = Field(default="HS256")

    # Database
    database_url: str = Field(default="sqlite:///./app.db")
    database_pool_size: int = Field(default=5)
    database_max_overflow: int = Field(default=10)

    # Rate Limiting
    rate_limit_enabled: bool = Field(default=True)
    rate_limit_requests_per_minute: int = Field(default=60)
    rate_limit_burst: int = Field(default=10)
    rate_limit_upload_per_hour: int = Field(default=20)

    # Logging
    log_level: str = Field(default="INFO")
    log_file_path: str = Field(default="/tmp/aiyou-services.log")
    log_format: str = Field(default="json")
    log_max_bytes: int = Field(default=10_485_760)  # 10 MB
    log_backup_count: int = Field(default=5)

    # LLM / Gemini
    gemini_api_key: str | None = Field(default=None)
    gemini_project_id: str | None = Field(default=None)
    gemini_location: str = Field(default="us-central1")

    # ShadowTag Blockchain
    shadowtag_enabled: bool = Field(default=False)
    shadowtag_private_key: str | None = Field(default=None)
    shadowtag_chain_id: str | None = Field(default=None)

    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0")
    redis_max_connections: int = Field(default=10)

    # Observability
    service_name: str = Field(default="aiyou-fastapi-services")
    enable_metrics: bool = Field(default=True)
    enable_tracing: bool = Field(default=False)
    otel_exporter_otlp_endpoint: str = Field(default="http://localhost:4317")
    otel_exporter_otlp_insecure: bool = Field(default=True)
    otel_service_name: str = Field(default="aiyou-fastapi-services")

    # Decision limits
    max_cost_per_decision: float = Field(default=1.0)
    max_latency_p99_ms: float = Field(default=5000.0)
    confidence_threshold: float = Field(default=0.7)

    # Kernel configuration
    kernel_1_max_latency_ms: float = Field(default=3000.0)
    kernel_1_max_output_tokens: int = Field(default=4096)
    gemini_model: str = Field(default="gemini-2.5-flash")

    # Alerting
    alert_email_enabled: bool = Field(default=False)
    alert_slack_webhook: str | None = Field(default=None)
    alert_webhook_url: str | None = Field(default=None)

    # Sandboxing
    sandbox: SandboxSettings = Field(default_factory=SandboxSettings)

    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_nested_delimiter="__",
        extra="ignore",
    )

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment is one of allowed values."""
        allowed = ["development", "staging", "production"]
        if v not in allowed:
            raise ValueError(f"Environment must be one of {allowed}")
        return v

    def get_cors_config(self) -> dict[str, Any]:
        """Get CORS configuration."""
        return {
            "allow_origins": self.cors_origins,
            "allow_credentials": True,
            "allow_methods": ["*"],
            "allow_headers": ["*"],
        }


@lru_cache
def get_app_settings() -> AppSettings:
    """Get cached application settings.

    In development, generates a secure ephemeral SECRET_KEY so the app can start
    without explicit env configuration. Production must always set SECRET_KEY.
    """
    if not os.environ.get("SECRET_KEY"):
        import logging as _logging
        import secrets as _secrets

        _logger = _logging.getLogger(__name__)
        _logger.warning(
            "SECRET_KEY not set — using ephemeral per-process key. "
            "Set SECRET_KEY env var for production."
        )
        os.environ["SECRET_KEY"] = _secrets.token_urlsafe(32)
    return AppSettings()
