"""Application configuration"""

import logging
import os
import secrets
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)

_DEV_FALLBACK_SECRET = secrets.token_urlsafe(32)


class Settings(BaseSettings):
    """Application settings"""

    # Application
    APP_NAME: str = "AI You - Compliance Expert API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/ShadowTag-v2_compliance"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 0

    # Security
    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Anthropic Claude
    ANTHROPIC_API_KEY: str = ""
    CLAUDE_MODEL: str = "claude-3-5-sonnet-20241022"

    # Compliance
    GDPR_ENABLED: bool = True
    CCPA_ENABLED: bool = True
    DATA_RETENTION_DAYS: int = 365
    AUDIT_LOG_RETENTION_DAYS: int = 2555  # 7 years
    CONSENT_EXPIRY_DAYS: int = 730  # 2 years

    # Cookie settings
    COOKIE_CONSENT_REQUIRED: bool = True
    COOKIE_DOMAIN: str = "localhost"
    COOKIE_SECURE: bool = False
    COOKIE_HTTPONLY: bool = True
    COOKIE_SAMESITE: str = "lax"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8000"]
    CORS_ALLOW_CREDENTIALS: bool = True

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"

    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    COMPLIANCE_EMAIL: str = "redacted@shadowtag-v4.local"

    # Data Privacy
    ANONYMIZE_IP: bool = True
    MASK_PII_IN_LOGS: bool = True
    ENCRYPT_SENSITIVE_DATA: bool = True

    model_config = SettingsConfigDict(case_sensitive=True)

    def model_post_init(self, __context: object) -> None:
        """Ensure SECRET_KEY is never empty."""
        if not self.SECRET_KEY:
            env_key = os.environ.get("SECRET_KEY", "")
            if env_key:
                object.__setattr__(self, "SECRET_KEY", env_key)
            else:
                object.__setattr__(self, "SECRET_KEY", _DEV_FALLBACK_SECRET)
                logger.warning(
                    "SECRET_KEY not set — using random per-process fallback. "
                    "Set SECRET_KEY env var via GCP Secret Manager for production."
                )


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()
