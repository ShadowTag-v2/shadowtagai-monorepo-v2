"""Gemini Ingestion Layer Service"""

import asyncio
import logging
from datetime import datetime

from app.config import settings
from app.models.pnkln import (
    EthicalComplianceReport,
    IngestedItem,
    IngestionMetrics,
    SourceType,
    TierClassification,
)

logger = logging.getLogger(__name__)


class GeminiIngestionService:
    """Service for Gemini-powered data ingestion pipeline"""

    def __init__(self):
        """Initialize Gemini Ingestion Service"""
        if not settings.GEMINI_API_KEY:
            logger.warning("GEMINI_API_KEY not set. Ingestion will operate in simulation mode.")

        self.enabled_sources = self._get_enabled_sources()
        logger.info(f"Gemini Ingestion Service initialized with sources: {self.enabled_sources}")

    def _get_enabled_sources(self) -> list[SourceType]:
        """Get list of enabled ingestion sources"""
        sources = []
        if settings.ENABLE_YOUTUBE_INGESTION:
            sources.append(SourceType.YOUTUBE)
        if settings.ENABLE_TWITTER_INGESTION:
            sources.append(SourceType.TWITTER)
        if settings.ENABLE_NEWS_INGESTION:
            sources.append(SourceType.NEWS)
        if settings.ENABLE_RSS_INGESTION:
            sources.append(SourceType.RSS)
        return sources

    async def run_ingestion_pipeline(
        self, sources: list[SourceType] | None = None,
    ) -> IngestionMetrics:
        """Run the complete ingestion pipeline

        Args:
            sources: Optional list of sources to ingest from. Defaults to all enabled.

        Returns:
            IngestionMetrics with pipeline results

        """
        start_time = datetime.utcnow()
        sources = sources or self.enabled_sources

        logger.info(f"Starting ingestion pipeline for sources: {sources}")

        # Simulate ingestion from multiple sources
        items = []
        for source in sources:
            source_items = await self._ingest_from_source(source)
            items.extend(source_items)

        # Calculate metrics
        runtime = (datetime.utcnow() - start_time).total_seconds() / 60.0

        metrics = self._calculate_metrics(items, runtime)

        logger.info(
            f"Ingestion complete: {metrics.items_ingested} items, "
            f"{metrics.runtime_minutes:.2f} min, "
            f"${metrics.average_cost_per_item:.4f}/item",
        )

        return metrics

    async def _ingest_from_source(self, source: SourceType) -> list[IngestedItem]:
        """Ingest data from a specific source

        Args:
            source: The source type to ingest from

        Returns:
            List of ingested items

        """
        # Simulate source-specific ingestion
        # In production, this would call actual APIs, crawlers, etc.
        logger.info(f"Ingesting from {source.value}...")

        # Respect ethical crawling limits
        if settings.RESPECT_ROBOTS_TXT:
            await self._check_robots_txt(source)

        # Rate limiting
        await asyncio.sleep(60.0 / settings.RATE_LIMIT_REQUESTS_PER_MINUTE)

        # Simulate items (replace with actual ingestion logic)
        items = self._simulate_ingestion(source, count=20)

        return items

    def _simulate_ingestion(self, source: SourceType, count: int = 20) -> list[IngestedItem]:
        """Simulate ingestion for development/testing"""
        import random

        items = []
        for i in range(count):
            # Random relevance score
            relevance = random.uniform(0.3, 0.95)

            # Classify tier based on relevance
            if relevance >= settings.TIER_1_THRESHOLD:
                tier = TierClassification.TIER_1
            elif relevance >= settings.TIER_2_THRESHOLD:
                tier = TierClassification.TIER_2
            else:
                tier = TierClassification.TIER_3

            item = IngestedItem(
                id=f"{source.value}_{i}_{int(datetime.utcnow().timestamp())}",
                source_type=source,
                source_url=f"https://{source.value}.example.com/item/{i}",
                title=f"Sample {source.value} item {i}",
                content=f"Simulated content from {source.value}",
                tier=tier,
                relevance_score=relevance,
                cost=random.uniform(0.01, 0.08),
            )
            items.append(item)

        return items

    async def _check_robots_txt(self, source: SourceType) -> bool:
        """Check robots.txt compliance for source"""
        # Simulate robots.txt check
        logger.debug(f"Checking robots.txt for {source.value}")
        return True

    def _calculate_metrics(
        self, items: list[IngestedItem], runtime_minutes: float,
    ) -> IngestionMetrics:
        """Calculate ingestion metrics from items"""
        if not items:
            return IngestionMetrics(
                items_ingested=0,
                unique_sources=0,
                average_cost_per_item=0.0,
                runtime_minutes=runtime_minutes,
                average_relevance_score=0.0,
            )

        # Count by source
        source_counts = {
            SourceType.YOUTUBE: 0,
            SourceType.TWITTER: 0,
            SourceType.NEWS: 0,
            SourceType.RSS: 0,
        }
        for item in items:
            if item.source_type in source_counts:
                source_counts[item.source_type] += 1

        # Count by tier
        tier_counts = {
            TierClassification.TIER_1: 0,
            TierClassification.TIER_2: 0,
            TierClassification.TIER_3: 0,
        }
        for item in items:
            tier_counts[item.tier] += 1

        # Calculate averages
        total_cost = sum(item.cost for item in items)
        total_relevance = sum(item.relevance_score for item in items)
        unique_sources = len(set(item.source_url for item in items))

        # Check quality gates
        quality_passed = self._check_quality_gates(items, unique_sources)

        return IngestionMetrics(
            items_ingested=len(items),
            unique_sources=unique_sources,
            average_cost_per_item=total_cost / len(items),
            runtime_minutes=runtime_minutes,
            youtube_items=source_counts[SourceType.YOUTUBE],
            twitter_items=source_counts[SourceType.TWITTER],
            news_items=source_counts[SourceType.NEWS],
            rss_items=source_counts[SourceType.RSS],
            tier_1_count=tier_counts[TierClassification.TIER_1],
            tier_2_count=tier_counts[TierClassification.TIER_2],
            tier_3_count=tier_counts[TierClassification.TIER_3],
            average_relevance_score=total_relevance / len(items),
            quality_gate_passed=quality_passed,
        )

    def _check_quality_gates(self, items: list[IngestedItem], unique_sources: int) -> bool:
        """Check if quality gates are met"""
        if len(items) < settings.MIN_DAILY_ITEMS:
            return False

        if unique_sources < settings.MIN_UNIQUE_SOURCES:
            return False

        avg_cost = sum(item.cost for item in items) / len(items)
        if avg_cost > settings.MAX_COST_PER_ITEM:
            return False

        avg_relevance = sum(item.relevance_score for item in items) / len(items)
        return not avg_relevance < settings.MIN_RELEVANCE_SCORE

    async def get_compliance_report(self) -> EthicalComplianceReport:
        """Get ethical crawling compliance report"""
        # Simulate compliance tracking
        return EthicalComplianceReport(
            robots_txt_violations=0,
            rate_limit_violations=0,
            total_requests=1000,
            compliance_score=1.0,
            flagged_domains=[],
        )
