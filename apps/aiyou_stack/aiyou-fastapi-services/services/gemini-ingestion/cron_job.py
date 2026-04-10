"""
Gemini Ingestion Layer - Nightly CronJob Entry Point

Orchestrates the complete ingestion pipeline:
1. Fetch from multi-sources (YouTube, Twitter, News, RSS, V2X Mesh)
2. Analyze with Gemini API
3. Classify into tiers
4. Generate AM Briefing
5. Export metrics and artifacts
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from pathlib import Path

from ingestion_core import (
    DataTier,
    EthicalCrawlingConfig,
    IngestionPipeline,
    RelevanceCategory,
    SourceConfig,
    SourceType,
)

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class CronJobRunner:
    """Main CronJob runner"""

    def __init__(self):
        self.output_dir = Path("/app/output")
        self.output_dir.mkdir(exist_ok=True)

        # Load configuration from environment
        self.config = {
            "gemini_api_key": os.getenv("GEMINI_API_KEY"),
            "youtube_api_key": os.getenv("YOUTUBE_API_KEY"),
            "twitter_bearer_token": os.getenv("TWITTER_BEARER_TOKEN"),
            "news_api_key": os.getenv("NEWS_API_KEY"),
            "v2x_mesh_url": os.getenv("V2X_MESH_GATEWAY_URL", "http://v2x-mesh-gateway"),
            "runtime_target_minutes": float(os.getenv("RUNTIME_TARGET_MINUTES", "45")),
        }

    async def run(self):
        """Execute ingestion pipeline"""
        start_time = datetime.now()
        logger.info("=" * 80)
        logger.info("Starting Gemini Ingestion Layer - Nightly Run")
        logger.info(f"Time: {start_time.isoformat()}")
        logger.info("=" * 80)

        try:
            # 1. Initialize pipeline
            logger.info("\n[1/5] Initializing ingestion pipeline...")
            pipeline = await self._initialize_pipeline()

            # 2. Run ingestion
            logger.info("\n[2/5] Running multi-source ingestion...")
            metrics = await pipeline.run()

            # 3. Generate AM briefing
            logger.info("\n[3/5] Generating AM briefing...")
            briefing = pipeline.get_am_briefing()

            # 4. Export artifacts
            logger.info("\n[4/5] Exporting artifacts...")
            await self._export_artifacts(metrics, briefing, pipeline.ingested_items)

            # 5. Report results
            logger.info("\n[5/5] Reporting results...")
            await self._report_results(metrics, briefing, start_time)

            logger.info("\n" + "=" * 80)
            logger.info("✅ Ingestion run completed successfully")
            logger.info("=" * 80)

        except Exception as e:
            logger.error(f"\n❌ Ingestion run failed: {e}", exc_info=True)
            raise

    async def _initialize_pipeline(self) -> IngestionPipeline:
        """Initialize pipeline with sources"""
        # Configure ethical crawling
        crawler_config = EthicalCrawlingConfig(
            rate_limit_requests_per_minute=60, avoid_peak_hours=True
        )

        # Create pipeline
        pipeline = IngestionPipeline(
            crawler_config=crawler_config, gemini_api_key=self.config["gemini_api_key"]
        )

        # Add V2X Mesh source (Tier 1 - highest priority)
        pipeline.add_source(
            SourceConfig(
                source_id="v2x-mesh-prod",
                source_type=SourceType.V2X_MESH,
                url=self.config["v2x_mesh_url"],
                tier=DataTier.TIER_1,
                relevance_categories=[
                    RelevanceCategory.TRAFFIC,
                    RelevanceCategory.SAFETY,
                    RelevanceCategory.TRANSPORTATION,
                ],
                crawl_frequency_hours=1,  # Frequent updates
            )
        )

        # Add YouTube source (Tier 2)
        if self.config["youtube_api_key"]:
            pipeline.add_source(
                SourceConfig(
                    source_id="youtube-traffic-updates",
                    source_type=SourceType.YOUTUBE,
                    url="https://youtube.com",
                    tier=DataTier.TIER_2,
                    relevance_categories=[
                        RelevanceCategory.TRAFFIC,
                        RelevanceCategory.URBAN_MOBILITY,
                    ],
                    api_key=self.config["youtube_api_key"],
                )
            )

        # Add Twitter source (Tier 2)
        if self.config["twitter_bearer_token"]:
            pipeline.add_source(
                SourceConfig(
                    source_id="twitter-traffic-alerts",
                    source_type=SourceType.TWITTER,
                    url="https://twitter.com",
                    tier=DataTier.TIER_2,
                    relevance_categories=[RelevanceCategory.TRAFFIC, RelevanceCategory.SAFETY],
                    api_key=self.config["twitter_bearer_token"],
                )
            )

        # Add News API source (Tier 2)
        if self.config["news_api_key"]:
            pipeline.add_source(
                SourceConfig(
                    source_id="newsapi-transportation",
                    source_type=SourceType.NEWS,
                    url="https://newsapi.org",
                    tier=DataTier.TIER_2,
                    relevance_categories=[
                        RelevanceCategory.TRANSPORTATION,
                        RelevanceCategory.POLICY,
                        RelevanceCategory.INFRASTRUCTURE,
                    ],
                    api_key=self.config["news_api_key"],
                )
            )

        # Add RSS feeds (Tier 3)
        pipeline.add_source(
            SourceConfig(
                source_id="transport-blog-rss",
                source_type=SourceType.RSS,
                url="https://transport.blog/feed",
                tier=DataTier.TIER_3,
                relevance_categories=[RelevanceCategory.TRANSPORTATION],
                crawl_frequency_hours=24,
            )
        )

        logger.info(f"Initialized pipeline with {len(pipeline.sources)} sources")
        return pipeline

    async def _export_artifacts(self, metrics, briefing, items):
        """Export metrics, briefing, and data to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Export metrics
        metrics_file = self.output_dir / f"metrics_{timestamp}.json"
        with open(metrics_file, "w") as f:
            json.dump(
                {
                    "run_id": metrics.run_id,
                    "started_at": metrics.started_at.isoformat(),
                    "completed_at": metrics.completed_at.isoformat()
                    if metrics.completed_at
                    else None,
                    "runtime_seconds": metrics.runtime_seconds,
                    "total_items": metrics.total_items_ingested,
                    "tier_distribution": {
                        "tier_1": metrics.items_by_tier[DataTier.TIER_1],
                        "tier_2": metrics.items_by_tier[DataTier.TIER_2],
                        "tier_3": metrics.items_by_tier[DataTier.TIER_3],
                    },
                    "quality_scores": {
                        "avg_relevance": metrics.avg_relevance_score,
                        "timeliness": metrics.timeliness_score,
                        "completeness": metrics.completeness_score,
                    },
                    "costs": {
                        "total_dollars": metrics.total_cost_dollars,
                        "cost_per_item_cents": metrics.cost_per_item_cents,
                    },
                    "sources": {
                        "crawled": metrics.sources_crawled,
                        "failed": metrics.sources_failed,
                        "by_source": metrics.items_by_source,
                    },
                    "ethical_compliance": {
                        "robots_txt_violations": metrics.robots_txt_violations,
                        "rate_limit_violations": metrics.rate_limit_violations,
                    },
                },
                f,
                indent=2,
            )

        logger.info(f"Exported metrics to {metrics_file}")

        # Export AM briefing
        briefing_file = self.output_dir / f"am_briefing_{timestamp}.json"
        with open(briefing_file, "w") as f:
            json.dump(briefing, f, indent=2)

        logger.info(f"Exported AM briefing to {briefing_file}")

        # Export ingested items (sample)
        items_file = self.output_dir / f"items_sample_{timestamp}.json"
        sample_items = [
            {
                "item_id": item.item_id,
                "source": item.source_id,
                "tier": item.tier.value,
                "title": item.title,
                "relevance_score": item.relevance_score,
                "published_at": item.published_at.isoformat(),
                "url": item.url,
            }
            for item in items[:50]  # First 50 items
        ]

        with open(items_file, "w") as f:
            json.dump(sample_items, f, indent=2)

        logger.info(f"Exported {len(sample_items)} sample items to {items_file}")

    async def _report_results(self, metrics, briefing, start_time):
        """Report results summary"""
        runtime_minutes = metrics.runtime_seconds / 60
        target_minutes = self.config["runtime_target_minutes"]

        logger.info("\n📊 INGESTION RUN SUMMARY")
        logger.info("-" * 80)
        logger.info(f"Run ID: {metrics.run_id}")
        logger.info(
            f"Runtime: {runtime_minutes:.1f} min (target: {target_minutes} min) "
            + ("✅" if runtime_minutes <= target_minutes else "⚠️")
        )

        logger.info("\n📦 ITEMS:")
        logger.info(f"  Total: {metrics.total_items_ingested}")
        logger.info(
            f"  Tier 1: {metrics.items_by_tier[DataTier.TIER_1]} "
            + f"({metrics.items_by_tier[DataTier.TIER_1] / max(1, metrics.total_items_ingested) * 100:.1f}%)"
        )
        logger.info(
            f"  Tier 2: {metrics.items_by_tier[DataTier.TIER_2]} "
            + f"({metrics.items_by_tier[DataTier.TIER_2] / max(1, metrics.total_items_ingested) * 100:.1f}%)"
        )
        logger.info(
            f"  Tier 3: {metrics.items_by_tier[DataTier.TIER_3]} "
            + f"({metrics.items_by_tier[DataTier.TIER_3] / max(1, metrics.total_items_ingested) * 100:.1f}%)"
        )

        logger.info("\n📈 QUALITY:")
        logger.info(
            f"  Relevance: {metrics.avg_relevance_score:.2f} (target: ≥0.7) "
            + ("✅" if metrics.avg_relevance_score >= 0.7 else "⚠️")
        )
        logger.info(f"  Timeliness: {metrics.timeliness_score * 100:.1f}% (target: ≥70%)")
        logger.info(f"  Completeness: {metrics.completeness_score * 100:.1f}% (target: ≥80%)")

        logger.info("\n💰 COSTS:")
        logger.info(f"  Total: ${metrics.total_cost_dollars:.2f}")
        logger.info(f"  Per Item: ${metrics.cost_per_item_cents:.4f}")

        logger.info("\n🌐 SOURCES:")
        logger.info(f"  Successful: {metrics.sources_crawled}")
        logger.info(f"  Failed: {metrics.sources_failed}")

        logger.info("\n✅ ETHICAL COMPLIANCE:")
        logger.info(f"  Robots.txt violations: {metrics.robots_txt_violations}")
        logger.info(f"  Rate limit violations: {metrics.rate_limit_violations}")

        logger.info("\n📰 AM BRIEFING:")
        logger.info(f"  Highlights: {len(briefing.get('highlights', []))}")
        logger.info(f"  Categories: {len(briefing.get('by_category', {}))}")

        logger.info("-" * 80)


async def main():
    """Main entry point"""
    runner = CronJobRunner()

    try:
        await runner.run()
        return 0
    except Exception as e:
        logger.error(f"CronJob failed: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
