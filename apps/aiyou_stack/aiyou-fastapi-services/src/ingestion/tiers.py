# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Tier Classification System for Intelligence Data.

Classifies collected data into tiers based on:
- Relevance to key topics
- Timeliness
- Source credibility
- Completeness
- Uniqueness
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class DataTier(Enum):
    """Data quality tiers."""

    TIER_1 = 1  # High value: relevant, timely, credible, complete
    TIER_2 = 2  # Medium value: some value but missing key attributes
    TIER_3 = 3  # Low value: noise, outdated, or low quality


@dataclass
class TierCriteria:
    """Criteria for tier classification."""

    # Relevance (0-1)
    min_relevance: float
    max_relevance: float

    # Timeliness (hours)
    max_age_hours: float

    # Source credibility (0-1)
    min_credibility: float

    # Completeness (0-1)
    min_completeness: float

    # Uniqueness (0-1)
    min_uniqueness: float


# Default tier criteria
TIER_1_CRITERIA = TierCriteria(
    min_relevance=0.7,
    max_relevance=1.0,
    max_age_hours=24,
    min_credibility=0.7,
    min_completeness=0.8,
    min_uniqueness=0.6,
)

TIER_2_CRITERIA = TierCriteria(
    min_relevance=0.4,
    max_relevance=0.7,
    max_age_hours=72,
    min_credibility=0.5,
    min_completeness=0.5,
    min_uniqueness=0.3,
)

TIER_3_CRITERIA = TierCriteria(
    min_relevance=0.0,
    max_relevance=0.4,
    max_age_hours=168,  # 7 days
    min_credibility=0.0,
    min_completeness=0.0,
    min_uniqueness=0.0,
)


@dataclass
class ClassificationScores:
    """Scores for classification."""

    relevance: float  # 0-1: How relevant to key topics
    timeliness: float  # 0-1: How recent/timely
    credibility: float  # 0-1: Source credibility
    completeness: float  # 0-1: Data completeness
    uniqueness: float  # 0-1: Uniqueness/novelty


@dataclass
class ClassifiedItem:
    """Data item with tier classification."""

    item_id: str
    tier: DataTier
    scores: ClassificationScores
    content: dict
    classified_at: datetime
    reasons: list[str]  # Explanation of classification


class TierClassifier:
    """Classifies intelligence data into quality tiers.

    Uses multi-factor scoring to determine data value:
    - Tier 1: High-value, actionable intelligence
    - Tier 2: Useful supporting information
    - Tier 3: Low-value noise or outdated data
    """

    def __init__(
        self,
        tier1_criteria: TierCriteria = TIER_1_CRITERIA,
        tier2_criteria: TierCriteria = TIER_2_CRITERIA,
        tier3_criteria: TierCriteria = TIER_3_CRITERIA,
    ):
        self.tier1_criteria = tier1_criteria
        self.tier2_criteria = tier2_criteria
        self.tier3_criteria = tier3_criteria

        # Statistics
        self.stats = {
            "total_classified": 0,
            "tier_1_count": 0,
            "tier_2_count": 0,
            "tier_3_count": 0,
        }

    def calculate_scores(self, item: dict) -> ClassificationScores:
        """Calculate classification scores for an item.

        This is a simplified implementation. Production version would:
        1. Use LLM to assess relevance to key topics
        2. Verify source credibility against database
        3. Check for duplicates to measure uniqueness
        4. Analyze completeness of data fields
        """
        # Extract metadata
        timestamp = item.get("timestamp")
        source = item.get("source", "unknown")
        content = item.get("content", "")

        # Calculate timeliness
        if timestamp:
            try:
                item_time = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                age_hours = (datetime.now() - item_time).total_seconds() / 3600
                timeliness = max(0.0, 1.0 - (age_hours / 168))  # Decay over 7 days
            except Exception:
                timeliness = 0.5
        else:
            timeliness = 0.5

        # Calculate relevance (mock - would use LLM in production)
        # For now, score based on content length and keywords
        relevance_keywords = ["ai", "llm", "deepseek", "aegaeon", "vllm", "gpu"]
        content_lower = content.lower()
        keyword_matches = sum(1 for kw in relevance_keywords if kw in content_lower)
        relevance = min(1.0, keyword_matches / len(relevance_keywords) * 2)

        # Calculate credibility (mock - would use source reputation system)
        credible_sources = ["arxiv", "youtube", "hackernews", "twitter-ai"]
        credibility = 0.8 if any(cs in source.lower() for cs in credible_sources) else 0.5

        # Calculate completeness
        required_fields = ["id", "source", "content", "timestamp", "url"]
        present_fields = sum(1 for field in required_fields if field in item)
        completeness = present_fields / len(required_fields)

        # Calculate uniqueness (mock - would check against database)
        # For now, assume all items are somewhat unique
        uniqueness = 0.7

        return ClassificationScores(
            relevance=relevance,
            timeliness=timeliness,
            credibility=credibility,
            completeness=completeness,
            uniqueness=uniqueness,
        )

    def classify_item(self, item: dict) -> ClassifiedItem:
        """Classify an item into a tier.

        Args:
            item: Data item to classify

        Returns:
            ClassifiedItem with tier and scores

        """
        self.stats["total_classified"] += 1

        scores = self.calculate_scores(item)
        reasons = []

        # Calculate age
        timestamp = item.get("timestamp")
        age_hours = 999  # default very old
        if timestamp:
            try:
                item_time = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                age_hours = (datetime.now() - item_time).total_seconds() / 3600
            except Exception:
                pass

        # Tier 1: High value
        if (
            scores.relevance >= self.tier1_criteria.min_relevance
            and age_hours <= self.tier1_criteria.max_age_hours
            and scores.credibility >= self.tier1_criteria.min_credibility
            and scores.completeness >= self.tier1_criteria.min_completeness
            and scores.uniqueness >= self.tier1_criteria.min_uniqueness
        ):
            tier = DataTier.TIER_1
            self.stats["tier_1_count"] += 1
            reasons.append(f"High relevance ({scores.relevance:.2f})")
            reasons.append(f"Timely ({age_hours:.1f}h old)")
            reasons.append(f"Credible source ({scores.credibility:.2f})")

        # Tier 2: Medium value
        elif (
            scores.relevance >= self.tier2_criteria.min_relevance
            and age_hours <= self.tier2_criteria.max_age_hours
            and scores.credibility >= self.tier2_criteria.min_credibility
        ):
            tier = DataTier.TIER_2
            self.stats["tier_2_count"] += 1
            reasons.append(f"Moderate relevance ({scores.relevance:.2f})")
            if age_hours > self.tier1_criteria.max_age_hours:
                reasons.append(f"Somewhat dated ({age_hours:.1f}h old)")

        # Tier 3: Low value
        else:
            tier = DataTier.TIER_3
            self.stats["tier_3_count"] += 1
            if scores.relevance < self.tier2_criteria.min_relevance:
                reasons.append(f"Low relevance ({scores.relevance:.2f})")
            if age_hours > self.tier2_criteria.max_age_hours:
                reasons.append(f"Outdated ({age_hours:.1f}h old)")
            if scores.credibility < self.tier2_criteria.min_credibility:
                reasons.append(f"Low credibility ({scores.credibility:.2f})")

        return ClassifiedItem(
            item_id=item.get("id", "unknown"),
            tier=tier,
            scores=scores,
            content=item,
            classified_at=datetime.now(),
            reasons=reasons,
        )

    def classify_batch(self, items: list[dict]) -> list[ClassifiedItem]:
        """Classify multiple items."""
        return [self.classify_item(item) for item in items]

    def get_tier_distribution(self) -> dict:
        """Get distribution of items across tiers."""
        total = self.stats["total_classified"]

        return {
            "total_classified": total,
            "tier_1": {
                "count": self.stats["tier_1_count"],
                "percentage": (self.stats["tier_1_count"] / total * 100) if total > 0 else 0,
            },
            "tier_2": {
                "count": self.stats["tier_2_count"],
                "percentage": (self.stats["tier_2_count"] / total * 100) if total > 0 else 0,
            },
            "tier_3": {
                "count": self.stats["tier_3_count"],
                "percentage": (self.stats["tier_3_count"] / total * 100) if total > 0 else 0,
            },
        }

    def get_quality_score(self) -> float:
        """Calculate overall quality score (0-100).

        Higher percentage of Tier 1 items = higher quality.
        """
        total = self.stats["total_classified"]
        if total == 0:
            return 0.0

        # Weighted score: Tier 1 = 100 pts, Tier 2 = 50 pts, Tier 3 = 0 pts
        score = (self.stats["tier_1_count"] * 100 + self.stats["tier_2_count"] * 50) / total

        return score
