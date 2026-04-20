"""Configuration for Gemini Ingestion Layer

Aligned with SHADOWTAGAI Core Stack 2025 technology refresh:
- GKE deployment on Google Cloud Platform
- Gemini 2.5 Flash-Lite for cost-effective LLM operations ($0.10/$0.40 per million tokens)
- Multi-source coverage across YouTube, Twitter, News, and other platforms
- Ethical crawling with compliance standards
"""

import os
from dataclasses import dataclass, field
from enum import StrEnum


class TierLevel(StrEnum):
    """Data quality tier classification"""

    TIER_1 = "tier_1"  # High-value, verified sources
    TIER_2 = "tier_2"  # Medium-value, credible sources
    TIER_3 = "tier_3"  # Low-value, unverified sources


@dataclass
class IngestionConfig:
    """Main configuration for Gemini Ingestion Layer"""

    # GKE CronJob Configuration
    target_runtime_minutes: int = 45
    max_runtime_minutes: int = 60
    cron_schedule: str = "0 2 * * *"  # 2 AM daily

    # Cost Management
    monthly_budget_usd: float = 77.0
    cost_per_item_target_usd: float = 0.001  # $0.001 per item target

    # Performance Targets
    daily_items_target: int = 10000
    min_source_diversity: int = 5

    # Quality Gates
    min_relevance_score: float = 0.60  # 60% confidence threshold (pre-prod)
    min_timeliness_hours: int = 24  # Data must be < 24 hours old
    min_completeness_pct: float = 0.85  # 85% field completion required

    # Tier Distribution Targets (percentage)
    tier_1_target_pct: float = 0.30  # 30% Tier 1
    tier_2_target_pct: float = 0.50  # 50% Tier 2
    tier_3_max_pct: float = 0.20  # Max 20% Tier 3

    # Ethical Crawling
    respect_robots_txt: bool = True
    default_rate_limit_rpm: int = 60  # 60 requests per minute default
    user_agent: str = "SHADOWTAGAI-Gemini-Ingestion/0.1.0 (+https://shadowtagai.ai/bot)"
    request_timeout_seconds: int = 30

    # Multi-Source Configuration
    enabled_sources: list[str] = field(
        default_factory=lambda: ["youtube", "twitter", "news", "reddit", "rss_feeds"],
    )

    # Gemini API Configuration
    gemini_model: str = "gemini-3.1-flash-lite-preview-lite"  # Cost-effective at $0.10/$0.40
    gemini_max_tokens: int = 8192
    gemini_temperature: float = 0.3  # Lower temperature for factual extraction

    # Storage Configuration
    gcs_bucket: str = os.getenv("GCS_BUCKET", "shadowtagai-ingestion-data")
    bigquery_dataset: str = os.getenv("BQ_DATASET", "shadowtagai_ingestion")

    # AM Briefing Configuration
    briefing_recipients: list[str] = field(
        default_factory=lambda: os.getenv("BRIEFING_RECIPIENTS", "").split(","),
    )
    briefing_format: str = "markdown"

    # Monitoring & Metrics
    enable_prometheus: bool = True
    prometheus_port: int = 9090
    enable_distributed_tracing: bool = True

    # Integration with 4 Namespaces
    serving_namespaces: list[str] = field(
        default_factory=lambda: ["intelligence", "analytics", "reporting", "api-gateway"],
    )


@dataclass
class SourceConfig:
    """Configuration for individual data sources"""

    name: str
    enabled: bool = True
    rate_limit_rpm: int = 60
    max_items_per_run: int = 1000
    tier_default: TierLevel = TierLevel.TIER_2

    # Source-specific credentials (loaded from K8s secrets)
    api_key: str = ""
    api_secret: str = ""

    # Custom parameters per source
    custom_params: dict = field(default_factory=dict)


# Source-specific configurations
YOUTUBE_CONFIG = SourceConfig(
    name="youtube",
    rate_limit_rpm=100,  # YouTube API has higher limits
    max_items_per_run=500,
    tier_default=TierLevel.TIER_2,
    custom_params={
        "video_categories": ["News", "Education", "Science & Technology"],
        "min_view_count": 1000,
        "max_video_age_days": 7,
    },
)

TWITTER_CONFIG = SourceConfig(
    name="twitter",
    rate_limit_rpm=300,  # Twitter API v2 limits
    max_items_per_run=2000,
    tier_default=TierLevel.TIER_3,  # Needs verification
    custom_params={"verified_accounts_only": False, "min_follower_count": 100, "languages": ["en"]},
)

NEWS_CONFIG = SourceConfig(
    name="news",
    rate_limit_rpm=60,
    max_items_per_run=1000,
    tier_default=TierLevel.TIER_1,  # News typically high quality
    custom_params={
        "trusted_domains": ["reuters.com", "apnews.com", "bbc.com", "bloomberg.com"],
        "categories": ["technology", "business", "science"],
    },
)

REDDIT_CONFIG = SourceConfig(
    name="reddit",
    rate_limit_rpm=60,
    max_items_per_run=500,
    tier_default=TierLevel.TIER_3,
    custom_params={
        "subreddits": ["technology", "machinelearning", "programming"],
        "min_upvotes": 10,
        "min_comments": 5,
    },
)

RSS_FEEDS_CONFIG = SourceConfig(
    name="rss_feeds",
    rate_limit_rpm=30,
    max_items_per_run=1000,
    tier_default=TierLevel.TIER_2,
    custom_params={
        "feed_urls": [
            "https://news.ycombinator.com/rss",
            "https://techcrunch.com/feed/",
            "https://www.wired.com/feed/rss",
        ],
    },
)

# Export default configuration
DEFAULT_CONFIG = IngestionConfig()
