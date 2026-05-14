# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Configuration for FastAPI service."""

from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # API Settings
    app_name: str = "ShadowTag v2 API"
    app_version: str = "2.0.0"
    debug: bool = False
    api_prefix: str = "/api/v1"

    # CORS
    cors_origins: list[str] = Field(default_factory=lambda: ["*"])
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = Field(default_factory=lambda: ["*"])
    cors_allow_headers: list[str] = Field(default_factory=lambda: ["*"])

    # File Upload
    max_upload_size_mb: int = 500
    upload_dir: str = "/tmp/shadowtag_uploads"
    output_dir: str = "/tmp/shadowtag_outputs"

    # GCP Settings
    gcp_project_id: str | None = None
    gcp_secret_name: str | None = None

    # Blockchain Settings
    blockchain_enabled: bool = False
    default_chain: str = "polygon"

    # Vertex AI
    vertex_location: str = "us-central1"
    vertex_enabled: bool = False

    @property
    def max_upload_size_bytes(self) -> int:
        """Max upload size in bytes."""
        return self.max_upload_size_mb * 1024 * 1024


settings = Settings()
