# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Ingestion Layer Configuration
Quality gates, sources, and operational parameters
"""

from dataclasses import dataclass
from typing import Any
from ..core.gemini_ingestion import Source, SourceType, SourceTier


@dataclass
class IngestionConfig:
    """Configuration for Gemini Ingestion Layer"""

    # Quality gates
    target_items_per_day: int = 1000
    target_unique_sources: int = 10
    target_cost_per_item: float = 0.10  # USD
    target_relevance_score: float = 0.7
    target_runtime_minutes: float = 45.0

    # Tier distribution targets
    target_tier_1_percentage: float = 20.0  # Aim for 20% Tier 1
    target_tier_2_percentage: float = 50.0  # Aim for 50% Tier 2
    target_tier_3_percentage: float = 30.0  # Accept 30% Tier 3

    # Operational costs
    monthly_operational_cost_usd: float = 77.0
    gemini_api_cost_per_1k_items: float = 0.50
    infrastructure_cost_monthly: float = 50.0

    # Ethical compliance
    respect_robots_txt: bool = True
    max_requests_per_hour: int = 60
    user_agent: str = "PNKLNBot/1.0 (+https://pnkln.ai/bot)"

    # Multi-source coverage requirements
    min_source_types: int = 3  # Require at least 3 different source types

    def calculate_monthly_cost(self, items_per_day: int) -> float:
        """Calculate estimated monthly cost"""
        items_per_month = items_per_day * 30
        api_cost = (items_per_month / 1000) * self.gemini_api_cost_per_1k_items
        total_cost = api_cost + self.infrastructure_cost_monthly
        return total_cost

    def validate_quality_gates(self, metrics: dict[str, float]) -> dict[str, bool]:
        """Validate metrics against quality gates"""
        return {
            "items_per_day": metrics.get("items_per_day", 0) >= self.target_items_per_day,
            "unique_sources": metrics.get("unique_sources", 0) >= self.target_unique_sources,
            "cost_per_item": metrics.get("cost_per_item", float("inf")) <= self.target_cost_per_item,
            "relevance_score": metrics.get("relevance_score", 0) >= self.target_relevance_score,
            "runtime_minutes": metrics.get("runtime_minutes", float("inf")) <= self.target_runtime_minutes,
            "tier_1_percentage": metrics.get("tier_1_percentage", 0) >= self.target_tier_1_percentage,
        }

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "quality_gates": {
                "target_items_per_day": self.target_items_per_day,
                "target_unique_sources": self.target_unique_sources,
                "target_cost_per_item": self.target_cost_per_item,
                "target_relevance_score": self.target_relevance_score,
                "target_runtime_minutes": self.target_runtime_minutes,
            },
            "tier_distribution": {
                "tier_1_target": f"{self.target_tier_1_percentage}%",
                "tier_2_target": f"{self.target_tier_2_percentage}%",
                "tier_3_target": f"{self.target_tier_3_percentage}%",
            },
            "operational_costs": {
                "monthly_total": f"${self.monthly_operational_cost_usd}",
                "gemini_api_per_1k": f"${self.gemini_api_cost_per_1k_items}",
                "infrastructure_monthly": f"${self.infrastructure_cost_monthly}",
            },
            "ethical_compliance": {
                "respect_robots_txt": self.respect_robots_txt,
                "max_requests_per_hour": self.max_requests_per_hour,
                "user_agent": self.user_agent,
            },
        }


# Default configuration
DEFAULT_INGESTION_CONFIG = IngestionConfig()


# Default source registry
DEFAULT_SOURCES: list[Source] = [
    # Tier 1: High-value authoritative sources
    Source(
        url="https://www.nytimes.com",
        source_type=SourceType.NEWS,
        tier=SourceTier.TIER_1,
        name="New York Times",
        rate_limit_per_hour=30,
        robots_txt_checked=True,
        robots_txt_compliant=True,
    ),
    Source(
        url="https://www.reuters.com",
        source_type=SourceType.NEWS,
        tier=SourceTier.TIER_1,
        name="Reuters",
        rate_limit_per_hour=30,
        robots_txt_checked=True,
        robots_txt_compliant=True,
    ),
    Source(
        url="https://arxiv.org",
        source_type=SourceType.ACADEMIC,
        tier=SourceTier.TIER_1,
        name="arXiv",
        rate_limit_per_hour=60,
        robots_txt_checked=True,
        robots_txt_compliant=True,
    ),
    Source(
        url="https://www.federalregister.gov",
        source_type=SourceType.GOVERNMENT,
        tier=SourceTier.TIER_1,
        name="Federal Register",
        rate_limit_per_hour=60,
        robots_txt_checked=True,
        robots_txt_compliant=True,
    ),
    # Tier 2: Moderate-value verified sources
    Source(
        url="https://techcrunch.com",
        source_type=SourceType.NEWS,
        tier=SourceTier.TIER_2,
        name="TechCrunch",
        rate_limit_per_hour=60,
        robots_txt_checked=True,
        robots_txt_compliant=True,
    ),
    Source(
        url="https://www.youtube.com",
        source_type=SourceType.YOUTUBE,
        tier=SourceTier.TIER_2,
        name="YouTube",
        rate_limit_per_hour=100,  # API-based
        robots_txt_checked=True,
        robots_txt_compliant=True,
    ),
    Source(
        url="https://twitter.com",
        source_type=SourceType.TWITTER,
        tier=SourceTier.TIER_2,
        name="Twitter",
        rate_limit_per_hour=180,  # API-based
        robots_txt_checked=True,
        robots_txt_compliant=True,
    ),
    # Tier 3: General sources (lower priority)
    Source(
        url="https://news.ycombinator.com",
        source_type=SourceType.WEB,
        tier=SourceTier.TIER_3,
        name="Hacker News",
        rate_limit_per_hour=30,
        robots_txt_checked=True,
        robots_txt_compliant=True,
    ),
    Source(
        url="https://www.reddit.com/r/technology",
        source_type=SourceType.WEB,
        tier=SourceTier.TIER_3,
        name="Reddit Technology",
        rate_limit_per_hour=60,
        robots_txt_checked=True,
        robots_txt_compliant=True,
    ),
]


# Source type coverage requirements
SOURCE_TYPE_REQUIREMENTS = {
    "min_types": 3,  # At least 3 different source types
    "required_types": [
        SourceType.NEWS,  # Must have news sources
        SourceType.ACADEMIC,  # Must have academic sources
    ],
    "recommended_types": [
        SourceType.YOUTUBE,
        SourceType.TWITTER,
        SourceType.GOVERNMENT,
    ],
}
