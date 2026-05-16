# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Core configuration module for Release Manager.
"""

from typing import Any
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import secrets


class Settings(BaseSettings):
  """Application settings loaded from environment variables."""

  model_config = SettingsConfigDict(
    env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="allow"
  )

  # Application
  APP_NAME: str = "Release Manager"
  APP_VERSION: str = "1.0.0"
  APP_ENV: str = "development"
  DEBUG: bool = False

  # Server
  HOST: str = "0.0.0.0"
  PORT: int = 8000
  RELOAD: bool = False

  # Database
  DATABASE_URL: str = (
    "postgresql+asyncpg://postgres:postgres@localhost:5432/release_manager"
  )
  DATABASE_POOL_SIZE: int = 10
  DATABASE_MAX_OVERFLOW: int = 20

  # Redis
  REDIS_URL: str = "redis://localhost:6379/0"
  REDIS_FEATURE_FLAGS_DB: int = 1

  # Security
  SECRET_KEY: str = secrets.token_urlsafe(32)
  ALGORITHM: str = "HS256"
  ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

  # Deployment Configuration
  DEPLOYMENT_STRATEGY: str = "blue_green"  # blue_green, rolling, canary
  HEALTH_CHECK_TIMEOUT: int = 30
  HEALTH_CHECK_INTERVAL: int = 5
  ROLLBACK_TIMEOUT: int = 300
  MAX_DEPLOYMENT_RETRIES: int = 3

  # Feature Flags
  FEATURE_FLAGS_ENABLED: bool = True
  FEATURE_FLAGS_CACHE_TTL: int = 60

  # Monitoring
  PROMETHEUS_ENABLED: bool = True
  PROMETHEUS_PORT: int = 9090

  # Logging
  LOG_LEVEL: str = "INFO"
  LOG_FORMAT: str = "json"

  # CORS
  BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8000"]

  @field_validator("BACKEND_CORS_ORIGINS", mode="before")
  @classmethod
  def assemble_cors_origins(cls, v: str | list[str]) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
      return [i.strip() for i in v.split(",")]
    elif isinstance(v, (list, str)):
      return v
    raise ValueError(v)

  @property
  def is_production(self) -> bool:
    """Check if running in production environment."""
    return self.APP_ENV == "production"

  @property
  def is_development(self) -> bool:
    """Check if running in development environment."""
    return self.APP_ENV == "development"

  @property
  def database_config(self) -> dict[str, Any]:
    """Get database configuration."""
    return {
      "pool_size": self.DATABASE_POOL_SIZE,
      "max_overflow": self.DATABASE_MAX_OVERFLOW,
      "pool_pre_ping": True,
      "echo": self.DEBUG,
    }


# Global settings instance
settings = Settings()
