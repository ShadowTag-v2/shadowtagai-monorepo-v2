"""
Gemini Ingestion Pipeline - Main Orchestrator.

Coordinates the nightly intelligence collection run:
1. Collect from multiple sources (with ethics checks)
2. Classify data into tiers
3. Generate AM briefing
4. Track metrics and performance

Target Runtime: ~45 minutes for nightly batch
Monthly Cost: ~$77 operational
"""

from __future__ import annotations

import asyncio
import logging
import time
from datetime import datetime
from typing import Any

from .briefing import BriefingGenerator, DailyBriefing
from .ethics import EthicalComplianceChecker, RateLimitRule
from .lineage import DataLineageTracker
from .sources import DEFAULT_SOURCES, SourceManager
from .tiers import TierClassifier

logger = logging.getLogger(__name__)


class IngestionPipeline:
    """
    Main orchestrator for intelligence ingestion.

    Architecture: GKE CronJob Multi-Container
    Schedule: Nightly (typically 2-3 AM)
    Runtime: ~45 minutes target
    Cost: ~$77/month operational
    """

    def __init__(
        self,
        source_manager: SourceManager | None = None,
        ethics_checker: EthicalComplianceChecker | None = None,
        tier_classifier: TierClassifier | None = None,
        briefing_generator: BriefingGenerator | None = None,
    ):
        # Initialize components
        self.source_manager = source_manager or SourceManager(sources=DEFAULT_SOURCES)
        self.ethics_checker = ethics_checker or EthicalComplianceChecker()
        self.tier_classifier = tier_classifier or TierClassifier()
        self.briefing_generator = briefing_generator or BriefingGenerator()
        self.lineage_tracker = DataLineageTracker()

        # Metrics
        self.metrics: dict[str, Any] = {
            "start_time": None,
            "end_time": None,
            "runtime_seconds": 0.0,
            "total_items_collected": 0,
            "total_items_classified": 0,
            "sources_processed": 0,
            "errors": 0,
        }

    async def run_nightly_ingestion(
        self,
        max_items_per_source: int = 100,
        output_path: str | None = None,
    ) -> DailyBriefing:
        """
        Run the complete nightly ingestion pipeline.

        Steps:
        1. Collect from all sources (with ethical compliance)
        2. Classify items into tiers
        3. Generate daily briefing
        4. Save outputs

        Args:
            max_items_per_source: Max items to collect per source
            output_path: Path to save briefing (optional)

        Returns:
            DailyBriefing for the day
        """
        self.metrics["start_time"] = datetime.now()
        start_perf = time.perf_counter()

        logger.info("=" * 60)
        logger.info("🌙 STARTING NIGHTLY INGESTION PIPELINE")
        logger.info("=" * 60)

        try:
            # Step 1: Collect from sources
            logger.info("\n📥 Step 1/3: Collecting from sources...")
            collected_data = await self._collect_with_ethics(max_items_per_source)

            # Flatten collected items
            all_items = []
            for _, items in collected_data.items():
                all_items.extend(items)

            self.metrics["total_items_collected"] = len(all_items)
            self.metrics["sources_processed"] = len(collected_data)

            logger.info(f"✓ Collected {len(all_items)} items from {len(collected_data)} sources")

            # Track lineage for collected items
            for item in all_items:
                # Assume item is a dict with 'content' and 'source' keys
                # If not, we'd need to adapt this
                source = item.get("source", "unknown")
                content = item.get("content", str(item))
                lineage_id = self.lineage_tracker.track_item(source, content, stage="collected")
                item["lineage_id"] = lineage_id  # Attach ID to item for downstream tracking

            # Step 2: Classify into tiers
            logger.info("\n🏆 Step 2/3: Classifying into tiers...")
            classified_items = self.tier_classifier.classify_batch(all_items)

            # Update lineage for classified items
            for classified_item in classified_items:
                # classified_items are likely ClassifiedItem objects or dicts
                # We need to access the original item's lineage_id
                # Assuming ClassifiedItem wraps the original item or has the ID
                # item can be dict or object
                if isinstance(classified_item, dict):
                    lid = classified_item.get("lineage_id")
                    tier = classified_item.get("tier", "unknown")
                else:
                    lid = getattr(classified_item, "lineage_id", None)
                    tier = getattr(classified_item, "tier", "unknown")

                if lid:
                    self.lineage_tracker.update_item(
                        lid, stage="classified", metadata={"tier": tier}
                    )

            self.metrics["total_items_classified"] = len(classified_items)

            tier_dist = self.tier_classifier.get_tier_distribution()
            logger.info(f"✓ Classified {len(classified_items)} items:")
            logger.info(
                f"  - Tier 1 (High): {tier_dist['tier_1']['count']} ({tier_dist['tier_1']['percentage']:.1f}%)"
            )
            logger.info(
                f"  - Tier 2 (Med):  {tier_dist['tier_2']['count']} ({tier_dist['tier_2']['percentage']:.1f}%)"
            )
            logger.info(
                f"  - Tier 3 (Low):  {tier_dist['tier_3']['count']} ({tier_dist['tier_3']['percentage']:.1f}%)"
            )

            # Step 3: Generate briefing
            logger.info("\n📊 Step 3/3: Generating daily briefing...")
            briefing = await self.briefing_generator.generate_briefing(
                classified_items=classified_items,
                source_stats=self.source_manager.get_coverage_stats(),
                compliance_stats=self.ethics_checker.get_compliance_stats(),
            )

            logger.info("✓ Briefing generated successfully")

            # Save briefing if path provided
            if output_path:
                await self._save_briefing(briefing, output_path)

            # Record metrics
            self.metrics["end_time"] = datetime.now()
            self.metrics["runtime_seconds"] = time.perf_counter() - start_perf

            # Log summary
            self._log_summary(briefing)

            return briefing

        except Exception as e:
            logger.error(f"❌ Pipeline failed: {e}", exc_info=True)
            self.metrics["errors"] += 1
            raise

    async def _collect_with_ethics(
        self,
        max_items_per_source: int,
    ) -> dict[str, list[dict]]:
        """
        Collect from sources with ethical compliance checks.

        For each source:
        1. Check rate limits
        2. Check robots.txt (if applicable)
        3. Collect with appropriate delays
        """
        collected = {}

        for source in self.source_manager.list_sources(enabled_only=True):
            try:
                # Check rate limit
                rate_limit = RateLimitRule(
                    requests_per_minute=source.rate_limit,
                    requests_per_hour=source.rate_limit * 60,
                    requests_per_day=source.rate_limit * 1440,
                )

                can_proceed = await self.ethics_checker.check_rate_limit(
                    source.name,
                    rate_limit,
                )

                if not can_proceed:
                    logger.warning(f"Skipping {source.name} due to rate limit")
                    continue

                # Check robots.txt for web sources
                if source.url and source.respect_robots_txt:
                    allowed = await self.ethics_checker.check_robots_txt(
                        source.url,
                        source.user_agent,
                    )

                    if not allowed:
                        logger.warning(f"Skipping {source.name} - blocked by robots.txt")
                        continue

                # Collect items
                items = await self.source_manager.collect_from_source(
                    source,
                    max_items_per_source,
                )

                collected[source.name] = items

                # Respect crawl delay
                delay = self.ethics_checker.get_crawl_delay(source.url)
                await asyncio.sleep(delay)

            except Exception as e:
                logger.error(f"Error collecting from {source.name}: {e}")
                self.metrics["errors"] += 1
                continue

        return collected

    async def _save_briefing(self, briefing: DailyBriefing, output_path: str):
        """Save briefing to file."""
        try:
            markdown = briefing.to_markdown()

            # Write to file
            with open(output_path, "w") as f:
                f.write(markdown)

            logger.info(f"✓ Briefing saved to {output_path}")

        except Exception as e:
            logger.error(f"Failed to save briefing: {e}")

    def _log_summary(self, briefing: DailyBriefing):
        """Log pipeline execution summary."""
        logger.info("\n" + "=" * 60)
        logger.info("✅ NIGHTLY INGESTION COMPLETE")
        logger.info("=" * 60)

        logger.info(f"\n⏱️  Runtime: {self.metrics['runtime_seconds']:.1f}s")
        logger.info(f"📥 Items Collected: {self.metrics['total_items_collected']}")
        logger.info(f"🏆 Items Classified: {self.metrics['total_items_classified']}")
        logger.info(f"📡 Sources Processed: {self.metrics['sources_processed']}")

        logger.info("\n📊 Quality Breakdown:")
        logger.info(f"   - Tier 1 (High): {briefing.tier_1_items}")
        logger.info(f"   - Tier 2 (Med):  {briefing.tier_2_items}")
        logger.info(f"   - Tier 3 (Low):  {briefing.tier_3_items}")

        # Performance assessment
        runtime_minutes = self.metrics["runtime_seconds"] / 60
        target_runtime = 45  # minutes

        logger.info("\n⚡ Performance:")
        logger.info(f"   - Runtime: {runtime_minutes:.1f} min (target: {target_runtime} min)")

        if runtime_minutes <= target_runtime:
            logger.info("   - ✓ Within target runtime")
        else:
            logger.info(f"   - ⚠️ Exceeded target by {runtime_minutes - target_runtime:.1f} min")

        if self.metrics["errors"] > 0:
            logger.warning(f"\n⚠️  Errors encountered: {self.metrics['errors']}")

        logger.info("\n" + "=" * 60)

    def get_metrics(self) -> dict:
        """Get pipeline execution metrics."""
        return {
            **self.metrics,
            "coverage_stats": self.source_manager.get_coverage_stats(),
            "tier_distribution": self.tier_classifier.get_tier_distribution(),
            "compliance_stats": self.ethics_checker.get_compliance_stats(),
        }


# CLI entry point for GKE CronJob
async def main():
    """Main entry point for nightly ingestion."""
    from ..monitoring import setup_logging

    setup_logging("INFO")

    pipeline = IngestionPipeline()

    # Run nightly ingestion
    briefing = await pipeline.run_nightly_ingestion(
        max_items_per_source=100,
        output_path="/tmp/daily_briefing.md",
    )

    # Print briefing
    print("\n" + briefing.to_markdown())


if __name__ == "__main__":
    asyncio.run(main())
