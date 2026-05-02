"""Application configuration."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    # Application
    app_name: str = "ShadowTag-v2 FastAPI Services"
    app_version: str = "0.1.0"
    debug: bool = False

    # Database
    database_url: str = "sqlite:///./checkpoints.db"

    # Checkpointing
    checkpoint_retention_days: int = 30
    checkpoint_storage_path: str = "./checkpoint_storage"
    max_checkpoints_per_session: int = 100

    # API
    api_prefix: str = "/api/v1"

    model_config = SettingsConfigDict(env_file_encoding="utf-8")


settings = Settings()
