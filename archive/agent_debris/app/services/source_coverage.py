"""
Multi-Source Coverage Analysis for PNKLN Ingestion Layer
Tracks diversity and coverage across YouTube, Twitter, News, RSS, Web, API, Podcast, Research
"""

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.ingestion import SourceMetric, SourceType, MultiSourceCoverage
from typing import Any
from datetime import datetime, timedelta
import math


class SourceCoverageAnalyzer:
    """
    Analyzes multi-source coverage to ensure diverse intelligence gathering
    Prevents over-reliance on single sources
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def analyze_coverage(self, hours: int = 24) -> MultiSourceCoverage:
        """
        Analyze coverage across all source types

        Returns coverage breakdown and diversity score
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)

        # Get counts by source type
        query = (
            select(
                SourceMetric.source_type,
                func.count(SourceMetric.id).label("count"),
            )
            .where(SourceMetric.timestamp >= cutoff_time)
            .group_by(SourceMetric.source_type)
        )

        result = await self.session.execute(query)
        rows = result.all()

        # Initialize counts for all source types
        coverage = {
            "youtube": 0,
            "twitter": 0,
            "news": 0,
            "rss": 0,
            "web": 0,
            "api": 0,
            "podcast": 0,
            "research": 0,
        }

        # Update with actual counts
        total = 0
        for row in rows:
            source_type = row.source_type
            count = row.count
            if source_type in coverage:
                coverage[source_type] = count
                total += count

        # Calculate diversity score (Shannon entropy normalized to 0-100)
        diversity_score = self._calculate_diversity_score(coverage, total)

        return MultiSourceCoverage(
            youtube=coverage["youtube"],
            twitter=coverage["twitter"],
            news=coverage["news"],
            rss=coverage["rss"],
            web=coverage["web"],
            api=coverage["api"],
            podcast=coverage["podcast"],
            research=coverage["research"],
            total_sources=sum(1 for v in coverage.values() if v > 0),
            diversity_score=diversity_score,
        )

    def _calculate_diversity_score(self, coverage: dict[str, int], total: int) -> float:
        """
        Calculate diversity score using Shannon entropy
        Returns 0-100, where 100 = perfectly balanced across all sources
        """
        if total == 0:
            return 0.0

        # Calculate Shannon entropy
        entropy = 0.0
        num_sources = len(coverage)

        for count in coverage.values():
            if count > 0:
                proportion = count / total
                entropy -= proportion * math.log2(proportion)

        # Normalize to 0-100
        max_entropy = math.log2(num_sources)
        diversity_score = (entropy / max_entropy) * 100 if max_entropy > 0 else 0

        return round(diversity_score, 2)

    async def get_source_quality(self, source_type: str, hours: int = 24) -> dict[str, Any]:
        """
        Get quality metrics for a specific source type

        Returns:
        - Average scores (relevance, timeliness, completeness)
        - Item counts
        - Cost metrics
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)

        query = select(
            func.count(SourceMetric.id).label("total_items"),
            func.avg(SourceMetric.relevance_score).label("avg_relevance"),
            func.avg(SourceMetric.timeliness_score).label("avg_timeliness"),
            func.avg(SourceMetric.completeness_score).label("avg_completeness"),
            func.avg(SourceMetric.ethical_score).label("avg_ethical"),
            func.sum(SourceMetric.cost).label("total_cost"),
        ).where(and_(SourceMetric.source_type == source_type, SourceMetric.timestamp >= cutoff_time))

        result = await self.session.execute(query)
        row = result.one()

        total_items = row.total_items or 0
        cost_per_item = (row.total_cost / total_items) if total_items > 0 else 0

        return {
            "source_type": source_type,
            "total_items": total_items,
            "quality_scores": {
                "relevance": round(row.avg_relevance or 0, 2),
                "timeliness": round(row.avg_timeliness or 0, 2),
                "completeness": round(row.avg_completeness or 0, 2),
                "ethical": round(row.avg_ethical or 0, 2),
            },
            "cost_metrics": {
                "total_cost": round(row.total_cost or 0, 2),
                "cost_per_item": round(cost_per_item, 4),
            },
        }

    async def identify_gaps(self, hours: int = 24) -> list[dict[str, Any]]:
        """
        Identify coverage gaps and make recommendations

        Returns list of source types that need more attention
        """
        coverage = await self.analyze_coverage(hours)
        gaps = []

        # Define minimum thresholds for each source
        min_thresholds = {
            "youtube": 50,  # At least 50 YouTube items/day
            "twitter": 100,  # At least 100 Twitter items/day
            "news": 200,  # At least 200 news items/day
            "rss": 50,
            "web": 100,
            "api": 30,
            "podcast": 10,
            "research": 5,
        }

        for source, min_count in min_thresholds.items():
            actual_count = getattr(coverage, source, 0)

            if actual_count < min_count:
                gap_percentage = ((min_count - actual_count) / min_count) * 100

                gaps.append(
                    {
                        "source_type": source,
                        "current_count": actual_count,
                        "target_count": min_count,
                        "gap_items": min_count - actual_count,
                        "gap_percentage": round(gap_percentage, 2),
                        "priority": self._get_gap_priority(gap_percentage),
                        "recommendation": self._get_gap_recommendation(source, actual_count, min_count),
                    }
                )

        # Sort by priority
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        gaps.sort(key=lambda x: priority_order.get(x["priority"], 4))

        return gaps

    def _get_gap_priority(self, gap_percentage: float) -> str:
        """Determine priority based on gap percentage"""
        if gap_percentage >= 80:
            return "critical"
        elif gap_percentage >= 50:
            return "high"
        elif gap_percentage >= 25:
            return "medium"
        else:
            return "low"

    def _get_gap_recommendation(self, source_type: str, current: int, target: int) -> str:
        """Generate recommendation for closing the gap"""
        gap = target - current

        recommendations = {
            "youtube": f"Add {gap} more YouTube channel subscriptions or increase polling frequency",
            "twitter": f"Monitor {gap} more Twitter accounts or hashtags",
            "news": f"Add {gap} more news RSS feeds or increase refresh rate",
            "rss": f"Subscribe to {gap} more RSS feeds across different topics",
            "web": f"Add {gap} more web sources to crawl list",
            "api": f"Integrate {gap} more API sources for data collection",
            "podcast": f"Add {gap} more podcast feeds to transcription pipeline",
            "research": f"Add {gap} more research paper sources or preprint servers",
        }

        return recommendations.get(source_type, f"Increase {source_type} coverage by {gap} items")

    async def get_tier_distribution(self, hours: int = 24) -> dict[str, Any]:
        """
        Analyze tier distribution across all sources

        Returns breakdown of Tier 1/2/3 items
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)

        query = (
            select(
                SourceMetric.tier,
                func.count(SourceMetric.id).label("count"),
            )
            .where(SourceMetric.timestamp >= cutoff_time)
            .group_by(SourceMetric.tier)
        )

        result = await self.session.execute(query)
        rows = result.all()

        tier_counts = {
            "tier_1": 0,
            "tier_2": 0,
            "tier_3": 0,
        }

        total = 0
        for row in rows:
            tier = row.tier
            count = row.count
            if tier in tier_counts:
                tier_counts[tier] = count
                total += count

        # Calculate percentages
        tier_percentages = {tier: round((count / total * 100) if total > 0 else 0, 2) for tier, count in tier_counts.items()}

        # Determine if distribution is healthy
        # Ideally: >20% Tier 1, 30-50% Tier 2, <50% Tier 3
        is_healthy = tier_percentages["tier_1"] >= 20 and tier_percentages["tier_2"] >= 30 and tier_percentages["tier_3"] <= 50

        return {
            "counts": tier_counts,
            "percentages": tier_percentages,
            "total_items": total,
            "is_healthy": is_healthy,
            "recommendation": self._get_tier_recommendation(tier_percentages),
        }

    def _get_tier_recommendation(self, percentages: dict[str, float]) -> str:
        """Generate recommendation based on tier distribution"""
        tier_1 = percentages["tier_1"]
        tier_3 = percentages["tier_3"]

        if tier_1 < 15:
            return "Critical: Add more high-value Tier 1 sources"
        elif tier_1 < 20:
            return "Increase Tier 1 source coverage"
        elif tier_3 > 60:
            return "Too many low-value Tier 3 items - prune or upgrade sources"
        elif tier_3 > 50:
            return "Consider reducing Tier 3 source priority"
        else:
            return "Tier distribution is healthy"

    async def get_coverage_report(self) -> dict[str, Any]:
        """
        Generate comprehensive coverage report

        Includes:
        - Multi-source coverage
        - Quality by source
        - Coverage gaps
        - Tier distribution
        """
        # Get coverage analysis
        coverage = await self.analyze_coverage(24)

        # Get quality for each active source
        quality_by_source = {}
        for source_type in SourceType:
            if getattr(coverage, source_type.value, 0) > 0:
                quality_by_source[source_type.value] = await self.get_source_quality(source_type.value, 24)

        # Identify gaps
        gaps = await self.identify_gaps(24)

        # Get tier distribution
        tier_dist = await self.get_tier_distribution(24)

        return {
            "coverage": coverage.dict(),
            "quality_by_source": quality_by_source,
            "coverage_gaps": gaps,
            "tier_distribution": tier_dist,
            "summary": {
                "total_sources_active": coverage.total_sources,
                "diversity_score": coverage.diversity_score,
                "critical_gaps": len([g for g in gaps if g["priority"] == "critical"]),
                "tier_health": tier_dist["is_healthy"],
            },
        }
