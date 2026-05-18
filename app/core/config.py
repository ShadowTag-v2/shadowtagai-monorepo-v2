# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Application configuration."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
  """Application settings."""

  # No .env file — secrets come from GCP Secret Manager (prod) or
  # source scripts/load_mcp_secrets.sh (local dev)
  model_config = SettingsConfigDict(case_sensitive=False)

  # Application
  app_name: str = "Claude Memory & Search Service"
  app_version: str = "1.0.0"
  debug: bool = False
  api_prefix: str = "/api/v1"

  # Server
  host: str = "0.0.0.0"
  port: int = 8000
  reload: bool = False

  # Database
  database_url: str = "sqlite+aiosqlite:///./claude_memory.db"

  # Redis
  redis_url: str = "redis://localhost:6379/0"

  # Security
  secret_key: str = "your-secret-key-change-in-production"
  algorithm: str = "HS256"
  access_token_expire_minutes: int = 30

  # Claude API
  anthropic_api_key: str | None = None

  # Memory Settings
  memory_synthesis_interval_hours: int = 24
  max_memory_items_per_project: int = 1000
  enable_auto_summarization: bool = True
  summarization_min_messages: int = 10

  # Vector Search
  embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
  vector_dimension: int = 384
  search_top_k: int = 10

  # Background Tasks
  celery_broker_url: str = "redis://localhost:6379/1"
  celery_result_backend: str = "redis://localhost:6379/2"

  # Logging
  log_level: str = "INFO"


settings = Settings()
