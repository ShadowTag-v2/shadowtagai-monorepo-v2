"""Configuration settings for ShadowTag-v4."""

import secrets

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration.
    Allows extra fields to accommodate environment variables used in tests.
    """

    # Base
    project_name: str = "ShadowTag-v4 AI Civilization Layer"
    app_name: str = "ShadowTag-v4 Platform"
    app_version: str = "0.1.0"
    environment: str = "development"
    debug: bool = False
    log_level: str = "INFO"

    # Service Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1
    reload: bool = True

    # Database
    database_url: str = "sqlite:///./shadowtag_v4.db"  # Default to sqlite for dev
    database_echo: bool = False
    database_pool_size: int = 5
    database_max_overflow: int = 10

    # Redis
    redis_url: str = "redis://localhost:6379/0"
    redis_max_connections: int = 10

    # ShadowTag
    shadowtag_enabled: bool = True
    shadowtag_private_key: str | None = None
    shadowtag_chain_id: str = "shadowtag_v4-mainnet"
    shadowtag_ledger_url: str | None = None

    # Starlink Integration
    starlink_enabled: bool = False
    starlink_api_key: str | None = None
    starlink_gateway_url: str | None = None

    # CoreWeave Integration
    coreweave_enabled: bool = False
    coreweave_api_key: str | None = None
    coreweave_cluster_url: str | None = None
    coreweave_default_gpu: str = "L40S"

    # CineVerse
    cineverse_enabled: bool = True
    cineverse_storage_path: str = "/var/lib/shadowtag_v4/cineverse"
    cineverse_max_upload_size_mb: int = 10240  # 10GB
    cineverse_cdn_url: str | None = None

    # GamePort
    gameport_enabled: bool = True
    gameport_max_sessions_per_user: int = 3
    gameport_session_timeout_minutes: int = 120

    # Commerce
    commerce_enabled: bool = True
    commerce_payment_provider: str = "stripe"
    commerce_stripe_api_key: str | None = None
    commerce_tax_rate: float = 0.0  # Default, override per jurisdiction

    # Gemini AI
    gemini_api_key: SecretStr | None = None  # Placeholder for tests
    rate_limit_requests_per_minute: int = 60
    rate_limit_burst: int = 10
    rate_limit_upload_per_hour: int = 20
    vertex_project_id: str | None = None
    gemini_location: str = "us-central1"

    # Security
    secret_key: SecretStr = Field(
        default_factory=lambda: SecretStr(secrets.token_urlsafe(48)),
        min_length=32,
    )  # Generates ephemeral key if SECRET_KEY env var not set
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    cors_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://localhost:8000"],
    )
    auth_enabled: bool = True
    jwt_secret: SecretStr | None = None
    jwt_algorithm: str = "HS256"
    admin_api_key: SecretStr | None = None

    # Rate Limiting
    rate_limit_enabled: bool = True

    # Integrations
    stripe_api_key: str | None = None

    # Kernel Latencies
    kernel_1_max_latency_ms: int = 1000
    kernel_2_max_latency_ms: int = 1000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: object) -> object:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


settings = Settings()


def get_settings():
    return settings
