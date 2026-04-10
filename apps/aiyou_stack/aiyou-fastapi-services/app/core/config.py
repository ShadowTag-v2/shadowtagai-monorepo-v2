"""
Application Configuration with Secrets Management
Security: All secrets via environment variables, no hardcoding
"""

from pydantic import Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings with validation and type safety

    Security Features:
    - No default secrets (forces explicit configuration)
    - Environment variable injection only
    - Validation on critical fields
    """

    # Application
    APP_NAME: str = "ShadowTag-v4 FastAPI Services"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = Field(default="production", pattern="^(development|staging|production)$")
    DEBUG: bool = False

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = Field(default=8000, ge=1000, le=65535)

    # Security - NO DEFAULTS (must be set via environment)
    SECRET_KEY: str = Field(min_length=32, description="JWT secret key, min 32 chars")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, ge=5, le=60)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, ge=1, le=30)

    # Password [VAPORIZED_PWD]
    BCRYPT_ROUNDS: int = Field(default=12, ge=10, le=14)
    MIN_PASSWORD_LENGTH: int = Field(default=12, ge=8)

    # Database
    DATABASE_URL: str = Field(description="PostgreSQL connection string")
    DB_POOL_SIZE: int = Field(default=10, ge=5, le=50)
    DB_MAX_OVERFLOW: int = Field(default=20, ge=10, le=100)
    DB_POOL_TIMEOUT: int = Field(default=30, ge=10, le=60)
    DB_POOL_RECYCLE: int = Field(default=3600, ge=600)

    # CORS - Strict defaults
    ALLOWED_ORIGINS: str = Field(default="http://localhost:3000")
    ALLOWED_METHODS: str = "GET,POST,PUT,DELETE,PATCH"
    ALLOWED_HEADERS: str = "*"

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, ge=10, le=1000)
    RATE_LIMIT_PER_HOUR: int = Field(default=1000, ge=100, le=10000)

    # Stripe Payment Integration
    STRIPE_SECRET_KEY: str = Field(default="", description="Stripe secret key")
    STRIPE_PUBLISHABLE_KEY: str = Field(default="", description="Stripe publishable key")
    STRIPE_WEBHOOK_SECRET: str = Field(default="", description="Stripe webhook secret")

    # Subscription Tiers (prices in cents)
    TIER_FREE_PRICE: int = 0
    TIER_PRO_PRICE: int = 2900  # $29.00/month
    TIER_ENTERPRISE_PRICE: int = 9900  # $99.00/month

    # Logging
    LOG_LEVEL: str = Field(default="INFO", pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")
    LOG_FORMAT: str = Field(default="json", pattern="^(json|text)$")

    # Google Cloud
    GCP_PROJECT_ID: str = Field(default="", description="GCP project ID")
    GCP_REGION: str = "us-central1"
    GCP_SERVICE_ACCOUNT: str = ""

    # Monitoring
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = Field(default=9090, ge=1000, le=65535)

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore"
    )

    @validator("SECRET_KEY")
    def validate_secret_key(cls, v: str) -> str:
        """Ensure secret key is strong"""
        if v == "CHANGE-THIS-TO-RANDOM-SECRET-KEY-MIN-32-CHARS":
            raise ValueError(
                "SECRET_KEY must be changed from default. "
                "Generate with: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
            )
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters")
        return v

    @validator("DATABASE_URL")
    def validate_database_url(cls, v: str) -> str:
        """Validate database URL format"""
        if not v.startswith(("postgresql://REDACTED_USER:REDACTED_PASS@validator("ALLOWED_ORIGINS")
    def validate_allowed_origins(cls, v: str) -> str:
        """Ensure no wildcard CORS in production"""
        if "*" in v:
            raise ValueError(
                "Wildcard (*) CORS origins are not allowed. Specify exact origins for security."
            )
        return v

    def get_cors_origins(self) -> list[str]:
        """Parse CORS origins from comma-separated string"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    def is_production(self) -> bool:
        """Check if running in production"""
        return self.APP_ENV == "production"

    def is_development(self) -> bool:
        """Check if running in development"""
        return self.APP_ENV == "development"


# Global settings instance (lazy loaded)
_settings: Settings | None = None


def get_settings() -> Settings:
    """
    Get application settings (singleton pattern)

    Security: Validates all settings on first access
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
