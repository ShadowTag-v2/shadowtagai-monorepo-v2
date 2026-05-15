"""Application Configuration

Centralized configuration management using Pydantic settings.
"""

import logging
import os
import secrets

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)

_DEV_FALLBACK_SECRET = secrets.token_urlsafe(32)


class Settings(BaseSettings):
    """Application settings"""

    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "ShadowTag v2 API"
    VERSION: str = "2.0.0"

    # CORS
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8000"]

    # File Upload
    MAX_UPLOAD_SIZE: int = 500 * 1024 * 1024  # 500 MB
    ALLOWED_VIDEO_EXTENSIONS: list[str] = [".mp4", ".avi", ".mkv", ".mov"]
    ALLOWED_AUDIO_EXTENSIONS: list[str] = [".mp3", ".wav", ".flac", ".ogg"]

    # Storage
    UPLOAD_DIR: str = "/tmp/shadowtag/uploads"
    OUTPUT_DIR: str = "/tmp/shadowtag/outputs"
    CHAIN_DB_PATH: str = "/tmp/shadowtag/chains.db"

    # Security
    SECRET_KEY: str = Field(
        default="",
        description="Secret key for signing tokens. Set via SECRET_KEY env var.",
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    # Steganography Defaults
    DEFAULT_BITS_PER_CHANNEL: int = 2
    DEFAULT_AUDIO_METHOD: str = "lsb"
    ENABLE_ENCRYPTION: bool = True
    ENABLE_ERROR_CORRECTION: bool = True

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


settings = Settings()
