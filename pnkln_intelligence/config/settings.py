# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
PNKLN Intelligence Pipeline - Configuration Settings
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class GCPSettings(BaseSettings):
  """Google Cloud Platform configuration"""

  project_id: str = Field(..., description="GCP Project ID")
  location: str = Field(default="us-central1", description="GCP region")

  # Storage
  gcs_bucket_raw: str = Field(
    default="pnkln-code-storage-prod", description="Raw data bucket"
  )
  gcs_bucket_processed: str = Field(
    default="pnkln-code-storage-prod", description="Processed data bucket"
  )

  # BigQuery
  bigquery_dataset: str = Field(
    default="code_search", description="BigQuery dataset name"
  )
  bigquery_location: str = Field(default="US", description="BigQuery location")

  # Vertex AI
  vertex_ai_index_display_name: str = Field(
    default="code-embeddings-index", description="Vector search index name"
  )
  vertex_ai_endpoint_display_name: str = Field(
    default="code-search-endpoint", description="Vector search endpoint name"
  )
  vertex_ai_embedding_dimensions: int = Field(
    default=1536, description="Embedding dimensions (768 for CodeBERT, 1536 for OpenAI)"
  )
  vertex_ai_machine_type: str = Field(
    default="e2-standard-16", description="Machine type for index endpoints"
  )
  vertex_ai_min_replicas: int = Field(default=2, description="Minimum replicas for HA")
  vertex_ai_max_replicas: int = Field(
    default=10, description="Maximum replicas for auto-scaling"
  )

  model_config = SettingsConfigDict(env_prefix="GCP_")


class EmbeddingSettings(BaseSettings):
  """Embedding generation configuration"""

  provider: str = Field(
    default="openai", description="Embedding provider: openai, voyage, codebert"
  )
  model_name: str = Field(
    default="text-embedding-3-large", description="Embedding model name"
  )
  dimensions: int = Field(default=1536, description="Embedding dimensions")
  batch_size: int = Field(
    default=100, description="Batch size for embedding generation"
  )
  chunk_size: int = Field(default=1500, description="Code chunk size in tokens")
  chunk_overlap: int = Field(default=300, description="Chunk overlap in tokens")

  # API Keys (loaded from environment)
  openai_api_key: str | None = Field(default=None, description="OpenAI API key")
  voyage_api_key: str | None = Field(default=None, description="Voyage API key")
  anthropic_api_key: str | None = Field(default=None, description="Anthropic API key")

  model_config = SettingsConfigDict(env_prefix="EMBEDDING_")


class ArxivSettings(BaseSettings):
  """arXiv paper discovery configuration"""

  categories: list[str] = Field(
    default=["cs.AI", "cs.LG", "cs.CL", "cs.DC", "cs.SE"],
    description="arXiv categories to monitor",
  )
  max_results_per_query: int = Field(
    default=100, description="Max results per API query"
  )
  delay_seconds: float = Field(default=3.0, description="Delay between API requests")
  num_retries: int = Field(
    default=5, description="Number of retries for failed requests"
  )
  download_pdf: bool = Field(default=True, description="Whether to download PDFs")
  papers_directory: str = Field(
    default="./data/papers", description="Directory to store papers"
  )

  model_config = SettingsConfigDict(env_prefix="ARXIV_")


class RedditSettings(BaseSettings):
  """Reddit aggregation configuration"""

  client_id: str = Field(..., description="Reddit API client ID")
  client_secret: str = Field(..., description="Reddit API client secret")
  user_agent: str = Field(
    default="PNKLN Intelligence Bot 1.0", description="User agent"
  )

  subreddits: list[str] = Field(
    default=[
      "MachineLearning",
      "kubernetes",
      "MLOps",
      "deeplearning",
      "artificial",
      "datascience",
    ],
    description="Subreddits to monitor",
  )
  posts_limit: int = Field(
    default=25, description="Number of posts to fetch per subreddit"
  )

  model_config = SettingsConfigDict(env_prefix="REDDIT_")


class HackerNewsSettings(BaseSettings):
  """Hacker News aggregation configuration"""

  api_base_url: str = Field(
    default="http://hn.algolia.com/api/v1", description="HN Algolia API base URL"
  )
  search_keywords: list[str] = Field(
    default=[
      "machine learning",
      "artificial intelligence",
      "kubernetes",
      "MLOps",
      "LLM",
    ],
    description="Keywords to search for",
  )
  max_results: int = Field(default=100, description="Maximum results per search")
  min_points: int = Field(default=10, description="Minimum points for story filtering")

  model_config = SettingsConfigDict(env_prefix="HN_")


class IngestionSettings(BaseSettings):
  """Repository ingestion configuration"""

  repositories_config: str = Field(
    default="pnkln_intelligence/config/repositories.yaml",
    description="Path to repositories YAML config",
  )
  flattening_tool: str = Field(
    default="repomix", description="Flattening tool: repomix, gitingest"
  )
  output_format: str = Field(
    default="xml", description="Output format: xml, markdown, json, plain"
  )
  include_security_scan: bool = Field(default=True, description="Run security scanning")
  max_file_size_mb: int = Field(default=10, description="Maximum file size to process")

  # Repomix-specific settings
  repomix_compression: bool = Field(
    default=True, description="Enable tree-sitter compression"
  )
  repomix_token_encoder: str = Field(
    default="cl100k_base", description="Token encoder: cl100k_base, o200k_base"
  )

  model_config = SettingsConfigDict(env_prefix="INGESTION_")


class MonitoringSettings(BaseSettings):
  """Monitoring and alerting configuration"""

  enable_prometheus: bool = Field(default=True, description="Enable Prometheus metrics")
  prometheus_port: int = Field(default=8000, description="Prometheus metrics port")

  # Alert thresholds
  vector_search_p95_latency_ms: int = Field(
    default=200, description="P95 latency threshold"
  )
  ingestion_error_rate_percent: float = Field(
    default=1.0, description="Ingestion error rate threshold"
  )
  daily_cost_increase_percent: float = Field(
    default=20.0, description="Daily cost increase threshold"
  )
  index_staleness_hours: int = Field(
    default=24, description="Index staleness threshold"
  )

  model_config = SettingsConfigDict(env_prefix="MONITORING_")


class PipelineSettings(BaseSettings):
  """Main pipeline configuration combining all settings"""

  gcp: GCPSettings = Field(default_factory=GCPSettings)
  embedding: EmbeddingSettings = Field(default_factory=EmbeddingSettings)
  arxiv: ArxivSettings = Field(default_factory=ArxivSettings)
  reddit: RedditSettings = Field(default_factory=RedditSettings)
  hackernews: HackerNewsSettings = Field(default_factory=HackerNewsSettings)
  ingestion: IngestionSettings = Field(default_factory=IngestionSettings)
  monitoring: MonitoringSettings = Field(default_factory=MonitoringSettings)

  # Processing settings
  processing_mode: str = Field(
    default="hybrid", description="Processing mode: batch, streaming, hybrid"
  )
  batch_schedule_cron: str = Field(
    default="0 2 * * *", description="Batch processing schedule (daily 2 AM)"
  )

  model_config = SettingsConfigDict(
    env_file=".env", env_file_encoding="utf-8", env_nested_delimiter="__"
  )


# Global settings instance
def get_settings() -> PipelineSettings:
  """Get or create settings instance"""
  return PipelineSettings()
