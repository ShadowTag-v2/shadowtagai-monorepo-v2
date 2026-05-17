# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Judge #6 Configuration Management
ATP 5-19 Risk Management API for AI
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
  """Application settings loaded from environment variables"""

  # Application
  APP_NAME: str = "Judge #6 - ATP 5-19 Risk Management API"
  APP_VERSION: str = "1.0.0"
  ENVIRONMENT: str = "development"
  DEBUG: bool = False

  # API
  API_V1_PREFIX: str = "/api/v1"
  HOST: str = "0.0.0.0"
  PORT: int = 8000

  # Security
  SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION"  # Must override in production
  ALGORITHM: str = "HS256"
  ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
  API_KEY_LENGTH: int = 32

  # Database
  DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/judge6"
  DATABASE_ECHO: bool = False

  # Redis
  REDIS_URL: str = "redis://localhost:6379/0"
  CACHE_TTL: int = 300  # 5 minutes

  # AI/ML Models
  GOOGLE_API_KEY: str | None = None  # Gemini
  ANTHROPIC_API_KEY: str | None = None  # Claude backup
  OPENAI_API_KEY: str | None = None  # GPT backup

  # Model Selection
  POLICY_MODEL: str = "gemini-pro"  # Layer 1: Policy understanding
  PYTORCH_MODEL_PATH: str = "./models/enforcement_model.pt"  # Layer 2

  # Performance Targets
  TARGET_P99_LATENCY_MS: int = 90
  MAX_CONCURRENT_REQUESTS: int = 100

  # Rate Limiting (per tier)
  RATE_LIMIT_FREE: int = 1000  # requests per month
  RATE_LIMIT_STARTER: int = 10000
  RATE_LIMIT_PROFESSIONAL: int = 100000
  RATE_LIMIT_ENTERPRISE: int = -1  # Unlimited (or custom)

  # Stripe Billing
  STRIPE_SECRET_KEY: str | None = None
  STRIPE_PUBLISHABLE_KEY: str | None = None
  STRIPE_WEBHOOK_SECRET: str | None = None

  # Price IDs (created in Stripe dashboard)
  STRIPE_PRICE_STARTER_MONTHLY: str | None = None
  STRIPE_PRICE_STARTER_ANNUAL: str | None = None
  STRIPE_PRICE_PROFESSIONAL_MONTHLY: str | None = None
  STRIPE_PRICE_PROFESSIONAL_ANNUAL: str | None = None

  # Monitoring
  SENTRY_DSN: str | None = None
  ENABLE_PROMETHEUS: bool = True

  # CORS
  CORS_ORIGINS: list[str] = [
    "http://localhost:3000",
    "http://localhost:8000",
    "https://judgeasaservice.ai",
  ]

  # ATP 5-19 Risk Levels
  RISK_CATASTROPHIC_THRESHOLD: float = 0.9
  RISK_CRITICAL_THRESHOLD: float = 0.7
  RISK_MODERATE_THRESHOLD: float = 0.4
  RISK_LOW_THRESHOLD: float = 0.2
  # Below 0.2 = NEGLIGIBLE

  # Default Policies (ATP 5-19)
  DEFAULT_POLICY_CORPUS_PATH: str = "./policies/atp-5-19-default.yaml"

  class Config:
    env_file = ".env"
    case_sensitive = True


@lru_cache
def get_settings() -> Settings:
  """
  Get cached settings instance
  Use dependency injection in FastAPI routes:

  @app.get("/")
  async def root(settings: Settings = Depends(get_settings)):
      return {"app": settings.APP_NAME}
  """
  return Settings()


# Export singleton
settings = get_settings()
