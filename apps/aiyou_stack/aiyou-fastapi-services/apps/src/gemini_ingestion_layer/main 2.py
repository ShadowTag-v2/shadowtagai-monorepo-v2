"""
Main Entry Point for Gemini Ingestion Layer

GKE CronJob multi-container orchestration for nightly intelligence collection.
Target runtime: ~45 minutes/night
Cost model: ~$77/month operational

Called by services in 4 namespaces:
- intelligence
- analytics
- reporting
- api-gateway
"""

import asyncio
import time
from datetime import datetime
from typing import Any

from .briefing import AMBriefingGenerator
from .classification import TierClassifier
from .config import DEFAULT_CONFIG, IngestcionConfig
from .crawling import EthicalCrawler
from .metrics import MetricsCollector
from .quality import QualityGates
from .sources import IngestionItem, NewsSource, TwitterSource, YouTubeSource


class GeminiIngestionLayer:
    """Main orchestrator for ingestion pipeline"""

    def __init__(self, config: IngestcionConfig = None):
        self.config = config or DEFAULT_CONFIG
        self.crawler = EthicalCrawler(
            user_agent=self.config.user_agent,
            respect_robots_txt=self.config.respect_robots_txt,
            default_rate_limit_rpm=self.config.default_rate_limit_rpm,
            request_timeout_seconds=self.config.request_timeout_seconds,
        )
        self.classifier = TierClassifier(
            model=self.config.gemini_model,
            confidence_threshold=self.config.min_relevance_score,
            temperature=self.config.gemini_temperature,
        )
        self.quality_gates = QualityGates(
            daily_items_target=self.config.daily_items_target,
            min_source_diversity=self.config.min_source_diversity,
            cost_per_item_target=self.config.cost_per_item_target_usd,
            min_relevance_score=self.config.min_relevance_score,
            min_timeliness_hours=self.config.min_timeliness_hours,
            min_completeness_pct=self.config.min_completeness_pct,
            target_runtime_minutes=self.config.target_runtime_minutes,
            max_runtime_minutes=self.config.max_runtime_minutes,
        )
        self.briefing_generator = AMBriefingGenerator(format=self.config.briefing_format)
        self.metrics = MetricsCollector()

        # Initialize sources
        self.sources = self._init_sources()

    def _init_sources(self) -> list:
        """Initialize enabled sources"""
        sources = []
        if "youtube" in self.config.enabled_sources:
            sources.append(YouTubeSource("youtube", {}))
        if "twitter" in self.config.enabled_sources:
            sources.append(TwitterSource("twitter", {}))
        if "news" in self.config.enabled_sources:
            sources.append(NewsSource("news", {}))
        return sources

    async def run(self) -> dict[str, Any]:
        """
        Execute full ingestion pipeline.

        Steps:
        1. Fetch from all enabled sources
        2. Classify items into tiers
        3. Evaluate quality gates
        4. Generate AM briefing
        5. Record metrics
        6. Return results

        Returns:
            Run statistics and results
        """
        start_time = time.time()
        print(f"[{datetime.utcnow().isoformat()}] Starting Gemini Ingestion Layer")

        # Step 1: Fetch from sources
        print("Step 1/5: Fetching from sources...")
        all_items: list[IngestionItem] = []
        unique_sources = set()

        for source in self.sources:
            print(f"  Fetching from {source.name}...")
            try:
                items = await source.fetch()
                all_items.extend(items)
                unique_sources.add(source.name)
                print(f"  ✓ {source.name}: {len(items)} items")
            except Exception as e:
                print(f"  ✗ {source.name}: Error - {e}")

        print(f"Total items fetched: {len(all_items)}")

        # Step 2: Classify items
        print("Step 2/5: Classifying items...")
        classified_items = []
        for item in all_items:
            try:
                result = await self.classifier.classify(
                    {
                        "source": item.source,
                        "domain": item.domain,
                        "title": item.title,
                        "text": item.content,
                        "author": item.author,
                        "url": item.url,
                    }
                )
                item.tier = result.tier.value
                item.relevance_score = result.confidence
                classified_items.append(item)
            except Exception as e:
                print(f"  Classification error: {e}")

        print(f"Classified: {len(classified_items)} items")

        # Step 3: Evaluate quality gates
        print("Step 3/5: Evaluating quality gates...")
        runtime_minutes = (time.time() - start_time) / 60

        ingestion_stats = {
            "items_ingested": len(classified_items),
            "unique_sources": len(unique_sources),
            "total_cost_usd": self.classifier.stats["total_cost_usd"],
            "average_relevance_score": (
                sum(i.relevance_score for i in classified_items) / len(classified_items)
                if classified_items
                else 0.0
            ),
            "items_by_age": [i.timestamp for i in classified_items],
            "field_completion_rates": [1.0] * len(classified_items),  # Placeholder
            "runtime_minutes": runtime_minutes,
            "tier_1_count": self.classifier.stats["tier_1_count"],
            "tier_2_count": self.classifier.stats["tier_2_count"],
            "tier_3_count": self.classifier.stats["tier_3_count"],
        }

        gate_result = self.quality_gates.evaluate(ingestion_stats)
        print(self.quality_gates.generate_report(gate_result))

        # Step 4: Generate AM briefing
        print("Step 4/5: Generating AM briefing...")
        briefing = self.briefing_generator.generate(classified_items, ingestion_stats)

        if self.config.briefing_recipients:
            await self.briefing_generator.deliver(briefing, self.config.briefing_recipients)
            print(f"  ✓ Briefing delivered to {len(self.config.briefing_recipients)} recipients")

        # Step 5: Record metrics
        print("Step 5/5: Recording metrics...")
        self.metrics.record_run(ingestion_stats)
        print("  ✓ Metrics recorded")

        # Final summary
        end_time = time.time()
        total_runtime = (end_time - start_time) / 60

        summary = {
            "status": "success" if gate_result.passed else "degraded",
            "runtime_minutes": round(total_runtime, 2),
            "items_ingested": len(classified_items),
            "sources_used": len(unique_sources),
            "quality_gates_passed": gate_result.passed,
            "briefing_generated": True,
            "timestamp": datetime.utcnow().isoformat(),
        }

        print(f"\n{'=' * 70}")
        print("INGESTION COMPLETE")
        print(f"Status: {summary['status'].upper()}")
        print(f"Runtime: {summary['runtime_minutes']} minutes")
        print(f"Items: {summary['items_ingested']}")
        print(f"Quality Gates: {'PASSED' if summary['quality_gates_passed'] else 'FAILED'}")
        print(f"{'=' * 70}\n")

        return summary


async def main():
    """Main entry point for CronJob"""
    layer = GeminiIngestionLayer()
    result = await layer.run()

    # Exit code based on quality gates
    exit_code = 0 if result["quality_gates_passed"] else 1
    exit(exit_code)


if __name__ == "__main__":
    asyncio.run(main())
