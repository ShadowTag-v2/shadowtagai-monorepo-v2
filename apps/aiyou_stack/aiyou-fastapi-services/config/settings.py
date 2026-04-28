# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration settings."""

    # API Configuration
    app_name: str = "AI Code Refactorer Service"
    app_version: str = "1.0.0"
    debug: bool = False

    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8080

    # Claude Agent SDK Configuration
    anthropic_api_key: str | None = None
    max_tokens: int = 4096
    model: str = "claude-sonnet-4-5-20250929"

    # Vertex AI Configuration
    vertex_project_id: str | None = None
    vertex_location: str = "us-central1"
    vertex_staging_bucket: str | None = None

    # Code Analysis Configuration
    max_file_size: int = 1_000_000  # 1MB
    supported_languages: list[str] = ["python", "javascript", "typescript", "java", "go", "rust"]

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
