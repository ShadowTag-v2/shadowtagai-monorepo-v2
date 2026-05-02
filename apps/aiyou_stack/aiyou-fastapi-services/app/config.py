"""Application configuration management."""

import logging
import os
import secrets
from functools import lru_cache
from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


def _get_secret_key() -> str:
    """Get SECRET_KEY from environment, or generate a secure ephemeral one for dev."""
    key = os.environ.get("SECRET_KEY")
    if key:
        return key
    fallback = secrets.token_urlsafe(32)
    logger.warning(
        "SECRET_KEY not set — using ephemeral per-process key. "
        "Set SECRET_KEY env var for production."
    )
    return fallback


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
    app_name: str = Field(default="ShadowTag-v2 FastAPI Services")
    app_version: str = Field(default="0.1.0")
    debug: bool = Field(default=False)
    environment: str = Field(default="development")

    # API
    api_prefix: str = Field(default="/api/v1")
    cors_origins: list[str] = Field(default=["http://localhost:3000", "http://localhost:8000"])

    # Server
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    reload: bool = Field(default=True)
    workers: int = Field(default=1)

    # Security
    secret_key: str = Field(default_factory=_get_secret_key)
    access_token_expire_minutes: int = Field(default=30)

    # Logging
    log_level: str = Field(default="INFO")

    # Service identity
    service_name: str = Field(default="shadowtag-v4")

    # Metrics
    enable_metrics: bool = Field(default=False)

    # Performance budgets
    max_latency_p99_ms: int = Field(default=5000)
    max_cost_per_decision: float = Field(default=0.10)

    # Sandboxing
    sandbox: SandboxSettings = Field(default_factory=SandboxSettings)

    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_nested_delimiter="__",
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
def get_settings() -> AppSettings:
    """Get cached application settings."""
    return AppSettings()


settings = get_settings()
