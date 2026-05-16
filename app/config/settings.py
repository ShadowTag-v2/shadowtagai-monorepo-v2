# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Application configuration using Pydantic Settings"""

from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    model_config = ConfigDict(env_file=".env", case_sensitive=True)

    # Google Cloud Platform
    GCP_PROJECT_ID: str = "aiyou-project"
    GCP_REGION: str = "us-central1"
    GCP_LOCATION: str = "us-central1"
    VERTEX_AI_ENDPOINT: str = "https://us-central1-aiplatform.googleapis.com"

    # Google Cloud Storage
    GCS_BUCKET_NAME: str = "aiyou-data-bucket"
    GCS_MODEL_BUCKET: str = "aiyou-models-bucket"

    # Vertex AI
    VERTEX_AI_MODEL: str = "gemini-pro"
    VERTEX_AI_EMBEDDING_MODEL: str = "textembedding-gecko@003"

    # Content Safety
    GOOGLE_CONTENT_SAFETY_THRESHOLD: str = "BLOCK_MEDIUM_AND_ABOVE"

    # Gemini API (used by kernel tests)
    gemini_api_key: str = ""
    kernel_1_max_latency_ms: int = 5000
    kernel_1_max_output_tokens: int = 4096
    kernel_2_max_latency_ms: int = 2000
    confidence_threshold: float = 0.7

    # Redis (GPTRAM memory)
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str | None = None

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/aiyou"
    MONGO_URI: str = "mongodb://localhost:27017/aiyou"

    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_WORKERS: int = 4
    API_RELOAD: bool = False
    MAX_REQUESTS_PER_MINUTE: int = 100

    # TurboAPI Configuration
    TURBO_API_MAX_RPS: int = 40000
    TURBO_API_LAMBDA_TIMEOUT: int = 300

    # MoE-CL Configuration
    MOE_NUM_EXPERTS: int = 8
    MOE_ADAPTER_DIM: int = 64
    MOE_TRAINING_SCHEDULE: str = "nightly"

    # BDH Configuration
    BDH_ATTENTION_TYPE: str = "sparse_linear"
    BDH_GPU_ENABLED: bool = True

    # Nowgrep Configuration
    NOWGREP_INDEX_PATH: str = "/data/nowgrep/indices"
    NOWGREP_VECTOR_DIM: int = 768

    # Monitoring
    PROMETHEUS_PORT: int = 9090
    ENABLE_METRICS: bool = True
    ENABLE_TRACING: bool = True

    # Security
    API_KEY_HEADER: str = "X-API-Key"
    CORS_ORIGINS: str = "*"
    ENABLE_RATE_LIMITING: bool = True

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"


# Global settings instance
settings = Settings()
