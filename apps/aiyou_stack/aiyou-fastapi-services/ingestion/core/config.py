"""
PNKLN Core Stack - Gemini Ingestion Layer Configuration

This module manages configuration for the ingestion pipeline using Pydantic Settings.
All settings can be overridden via environment variables.
"""

from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AnthropicSettings(BaseSettings):
    """Anthropic API configuration."""

    api_key: str | None = Field(default=None, alias="ANTHROPIC_API_KEY")
    model: str = Field(default="claude-sonnet-4-5-20250929")
    max_tokens: int = Field(default=4096)
    temperature: float = Field(default=0.7)

    model_config = SettingsConfigDict(env_prefix="ANTHROPIC_")


class GCPSettings(BaseSettings):
    """Google Cloud Platform configuration."""

    project_id: str | None = Field(default=None, alias="GCP_PROJECT_ID")
    region: str = Field(default="us-central1")
    credentials_path: str | None = Field(None, alias="GOOGLE_APPLICATION_CREDENTIALS")

    # BigQuery
    dataset_metrics: str = Field(default="pnkln_metrics")
    dataset_ingestion: str = Field(default="pnkln_ingestion")

    # Cloud Storage
    bucket_raw_data: str = Field(default="pnkln-raw-data")
    bucket_processed: str = Field(default="pnkln-processed")

    model_config = SettingsConfigDict(env_prefix="GCP_")


class SourceAPISettings(BaseSettings):
    """External source API credentials."""

    youtube_api_key: str | None = None
    twitter_bearer_token: str | None = None
    twitter_api_key: str | None = None
    twitter_api_secret: str | None = None

    model_config = SettingsConfigDict(env_prefix="")


class IngestionSettings(BaseSettings):
    """Ingestion pipeline operational settings."""

    max_items_per_run: int = Field(default=10000)
    runtime_limit_minutes: int = Field(default=45)
    cost_budget_usd: float = Field(default=77.0)

    # Cost estimates (per item)
    cost_per_youtube_item: float = Field(default=0.005)
    cost_per_twitter_item: float = Field(default=0.003)
    cost_per_news_item: float = Field(default=0.002)
    cost_per_gemini_classification: float = Field(default=0.008)

    @field_validator("max_items_per_run")
    @classmethod
    def validate_max_items(cls, v: int) -> int:
        if v < 100:
            raise ValueError("max_items_per_run must be at least 100")
        if v > 50000:
            raise ValueError("max_items_per_run must not exceed 50,000")
        return v

    model_config = SettingsConfigDict(env_prefix="INGESTION_")


class EthicalCrawlerSettings(BaseSettings):
    """Ethical crawling and compliance settings."""

    max_rate_per_domain: float = Field(default=1.0)  # requests per second
    respect_robots_txt: bool = Field(default=True)
    user_agent: str = Field(default="PNKLN-Ingestion/1.0 (+https://pnkln.ai/bot)")
    request_timeout: int = Field(default=30)
    max_retries: int = Field(default=3)

    # Politeness delays
    min_delay_between_requests: float = Field(default=1.0)  # seconds
    backoff_multiplier: float = Field(default=2.0)

    @field_validator("max_rate_per_domain")
    @classmethod
    def validate_rate(cls, v: float) -> float:
        if v > 10.0:
            raise ValueError("max_rate_per_domain must not exceed 10 req/sec")
        return v

    model_config = SettingsConfigDict(env_prefix="CRAWLER_")


class ClassificationSettings(BaseSettings):
    """Tier classification thresholds and settings."""

    tier_1_score_threshold: float = Field(default=0.80)
    tier_2_score_threshold: float = Field(default=0.50)
    relevance_min_score: float = Field(default=0.70)

    # Quality gates
    completeness_min_pct: float = Field(default=0.95)
    timeliness_tier_1_hours: int = Field(default=24)
    timeliness_tier_2_hours: int = Field(default=72)

    @field_validator("tier_1_score_threshold", "tier_2_score_threshold", "relevance_min_score")
    @classmethod
    def validate_score(cls, v: float) -> float:
        if not 0.0 <= v <= 1.0:
            raise ValueError("Score thresholds must be between 0.0 and 1.0")
        return v

    model_config = SettingsConfigDict(env_prefix="TIER_")


class DatabaseSettings(BaseSettings):
    """Database connection settings."""

    url: str = Field(
        default="postgresql://REDACTED_USER:redacted@shadowtag-v4.local"
    )  # comma-separated
    format: Literal["html", "markdown", "json"] = Field(default="markdown")

    @field_validator("delivery_time")
    @classmethod
    def validate_time_format(cls, v: str) -> str:
        """Validate HH:MM time format."""
        try:
            hour, minute = map(int, v.split(":"))
            if not (0 <= hour < 24 and 0 <= minute < 60):
                raise ValueError
        except (ValueError, AttributeError):
            raise ValueError("delivery_time must be in HH:MM format (e.g., '06:00')")
        return v

    @property
    def recipient_list(self) -> list[str]:
        """Parse comma-separated recipients into a list."""
        return [r.strip() for r in self.recipients.split(",") if r.strip()]

    model_config = SettingsConfigDict(env_prefix="AM_BRIEFING_")


class FeatureFlags(BaseSettings):
    """Feature flags for enabling/disabling functionality."""

    enable_youtube_source: bool = Field(default=True)
    enable_twitter_source: bool = Field(default=True)
    enable_news_rss_source: bool = Field(default=True)
    enable_tier_classification: bool = Field(default=True)
    enable_ethical_filtering: bool = Field(default=True)

    model_config = SettingsConfigDict(env_prefix="ENABLE_")


class Config(BaseSettings):
    """Master configuration combining all settings."""

    # Sub-configurations
    anthropic: AnthropicSettings = Field(default_factory=AnthropicSettings)
    gcp: GCPSettings = Field(default_factory=GCPSettings)
    sources: SourceAPISettings = Field(default_factory=SourceAPISettings)
    ingestion: IngestionSettings = Field(default_factory=IngestionSettings)
    crawler: EthicalCrawlerSettings = Field(default_factory=EthicalCrawlerSettings)
    classification: ClassificationSettings = Field(default_factory=ClassificationSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    monitoring: MonitoringSettings = Field(default_factory=MonitoringSettings)
    delivery: DeliverySettings = Field(default_factory=DeliverySettings)
    features: FeatureFlags = Field(default_factory=FeatureFlags)

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )

    def validate_api_keys(self) -> list[str]:
        """Validate that required API keys are present based on enabled features."""
        missing = []

        if self.features.enable_youtube_source and not self.sources.youtube_api_key:
            missing.append("YOUTUBE_API_KEY")

        if self.features.enable_twitter_source and not self.sources.twitter_bearer_token:
            missing.append("TWITTER_BEARER_TOKEN")

        if not self.anthropic.api_key:
            missing.append("ANTHROPIC_API_KEY")

        return missing

    def get_cost_estimate(
        self,
        youtube_items: int = 0,
        twitter_items: int = 0,
        news_items: int = 0,
        classify_all: bool = True,
    ) -> dict[str, float]:
        """Calculate estimated costs for a given ingestion run."""
        total_items = youtube_items + twitter_items + news_items

        costs = {
            "youtube": youtube_items * self.ingestion.cost_per_youtube_item,
            "twitter": twitter_items * self.ingestion.cost_per_twitter_item,
            "news": news_items * self.ingestion.cost_per_news_item,
            "classification": 0.0,
            "total": 0.0,
        }

        if classify_all:
            costs["classification"] = total_items * self.ingestion.cost_per_gemini_classification

        costs["total"] = sum(costs.values())

        return costs


# Global config instance (lazily created on first call)
_config: Config | None = None


def get_config() -> Config:
    """Get the global configuration instance (lazy singleton)."""
    global _config
    if _config is None:
        _config = Config()
    return _config
