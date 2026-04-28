# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Environment configuration management"""

# NOTE: Environment variables loaded via `source scripts/load_mcp_secrets.sh`
# or GCP Secret Manager in production. python-dotenv is banned (GEMINI.md §secrets).
from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment"""

    # Google Cloud Configuration
    gcp_project_id: str | None = None
    gcp_location: str = "us-central1"

    # Gemini Model Configuration
    gemini_model: str = "gemini-3.1-flash-lite-preview"

    # RAG Configuration
    default_k: int = 5
    default_chunk_size: int = 300
    default_overlap: int = 50

    # Database Configuration
    database_url: str = (
        "postgresql+asyncpg://ShadowTag-v2_user:secure_password_here@localhost:5432/ShadowTag-v2_db"
    )
    debug: bool = False

    # JWT Security
    secret_key: str = "dev-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 10080

    # Service Configuration
    service_port: int = 8000
    log_level: str = "INFO"

    # Optional Authentication
    api_key: str | None = None

    @field_validator("debug", mode="before")
    @classmethod
    def _coerce_debug(cls, value: object) -> object:
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"1", "true", "yes", "on", "debug", "development", "dev"}:
                return True
            if normalized in {"0", "false", "no", "off", "release", "prod", "production"}:
                return False
        return value

    class Config:
        case_sensitive = False
        extra = "ignore"


# Global settings instance
settings = Settings()
