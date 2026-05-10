"""Application settings and configuration"""

import logging
import os
import secrets
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)

_DEV_FALLBACK_SECRET = secrets.token_urlsafe(32)


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Application
    APP_NAME: str = "AI You Email Automator"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    API_V1_STR: str = "/api/v1"

    # Database
    DATABASE_URL: str = "sqlite:///./ShadowTag-v2_email.db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Email Configuration
    EMAIL_FROM: str = "noreply@ShadowTag-v2.com"
    EMAIL_FROM_NAME: str = "AI You Email Automator"

    # SMTP Configuration
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    SMTP_TLS: bool = True

    # SendGrid Configuration
    SENDGRID_API_KEY: str | None = None

    # Mailgun Configuration
    MAILGUN_API_KEY: str | None = None
    MAILGUN_DOMAIN: str | None = None

    # Analytics & Tracking
    TRACK_OPENS: bool = True
    TRACK_CLICKS: bool = True
    TRACKING_DOMAIN: str = "track.ShadowTag-v2.com"

    # Rate Limiting
    EMAIL_RATE_LIMIT_PER_HOUR: int = 100
    EMAIL_RATE_LIMIT_PER_DAY: int = 1000

    # Security
    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Logging
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        case_sensitive=True,
    )

    def model_post_init(self, __context: object) -> None:
        """Ensure SECRET_KEY is never empty; warn if using dev fallback."""
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
