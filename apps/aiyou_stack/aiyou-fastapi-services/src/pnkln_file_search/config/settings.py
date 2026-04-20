"""Settings and configuration management using Pydantic"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Google Cloud Configuration
    gcp_project_id: str = Field(default="pnkln-core-gke", description="GCP Project ID")
    gcp_region: str = Field(default="us-central1", description="GCP Region")
    gcp_storage_bucket: str = Field(
        default="gs://pnkln-policy-corpus",
        description="GCS Bucket for policy documents",
    )

    # Vertex AI Configuration
    vertex_ai_location: str = Field(default="us-central1", description="Vertex AI location")
    vertex_ai_model: str = Field(
        default="gemini-3.1-flash-lite-preview",
        description="Gemini model for file search",
    )

    # File Search Configuration
    file_search_chunk_size: int = Field(
        default=512,
        description="Chunk size for document splitting",
    )
    file_search_chunk_overlap: int = Field(default=100, description="Overlap between chunks")
    file_search_top_k: int = Field(default=5, description="Number of top results to retrieve")

    # Kill Switch Thresholds
    kill_switch_file_search_p99_latency: int = Field(
        default=1000,
        description="P99 latency threshold in ms",
    )
    kill_switch_corpus_sync_failure_rate: float = Field(
        default=0.05,
        description="Max corpus sync failure rate (5%)",
    )
    kill_switch_false_positive_rate: float = Field(
        default=0.10,
        description="Max false positive rate (10%)",
    )

    # Judge #6 Configuration
    judge_p99_latency_target: int = Field(
        default=90,
        description="Judge #6 P99 latency target in ms",
    )
    judge_gemini_allocation: float = Field(
        default=0.40,
        description="Gemini allocation percentage for Judge #6",
    )

    # Service Configuration
    service_port: int = Field(default=8000, description="Service port")
    service_host: str = Field(default="0.0.0.0", description="Service host")
    log_level: str = Field(default="INFO", description="Logging level")

    # Optional Google Cloud credentials path
    google_application_credentials: str | None = Field(
        default=None,
        description="Path to GCP credentials JSON",
    )


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
