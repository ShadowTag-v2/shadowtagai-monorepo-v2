# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Application settings and configuration"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


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
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Logging
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
