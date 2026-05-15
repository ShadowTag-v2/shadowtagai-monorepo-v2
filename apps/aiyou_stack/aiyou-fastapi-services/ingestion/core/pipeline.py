"""PNKLN Core Stack - Gemini Ingestion Layer Pipeline

Main orchestration pipeline that:
1. Fetches items from multiple sources (YouTube, Twitter, News)
2. Classifies items into tiers using Gemini
3. Applies quality gates and filtering
4. Stores results for downstream consumption
5. Generates AM briefing
6. Tracks costs and runtime

Target metrics:
- Runtime: ~45 minutes per night
- Items: 5,000-10,000 daily
- Cost: ~$77/month
- Quality gates: Relevance ≥70%, Completeness ≥95%, Timeliness <24h
"""

import asyncio
from datetime import datetime

import structlog
from prometheus_client import Counter, Gauge, Histogram

from ingestion.classification.tier_classifier import IngestedItem, TierClassifier, TierScore
from ingestion.core.config import get_config
from ingestion.sources.news_adapter import NewsAdapter
from ingestion.sources.twitter_adapter import TwitterAdapter
from ingestion.sources.youtube_adapter import YouTubeAdapter

logger = structlog.get_logger(__name__)


# Prometheus metrics
items_fetched = Counter("ingestion_items_fetched_total", "Total items fetched", ["source"])
items_classified = Counter("ingestion_items_classified_total", "Total items classified", ["tier"])
pipeline_duration = Histogram("ingestion_pipeline_duration_seconds", "Pipeline execution duration")
pipeline_cost = Gauge("ingestion_pipeline_cost_usd", "Estimated cost of last pipeline run")


class IngestionPipeline:
    """Main ingestion pipeline orchestrator.

    Coordinates fetching, classification, and delivery of intelligence items
    across multiple sources while respecting ethical, cost, and runtime constraints.
    """

    def __init__(self):
        self.config = get_config()
        self.classifier = TierClassifier()

        # Initialize source adapters based on feature flags
        self.adapters = {}

        if self.config.features.enable_youtube_source:
            try:
                self.adapters["youtube"] = YouTubeAdapter()
            except ValueError as e:
                logger.warning("youtube_adapter_disabled", reason=str(e))

        if self.config.features.enable_twitter_source:
            try:
                self.adapters["twitter"] = TwitterAdapter()
            except ValueError as e:
                logger.warning("twitter_adapter_disabled", reason=str(e))

        if self.config.features.enable_news_rss_source:
            try:
                self.adapters["news"] = NewsAdapter()
            except ValueError as e:
                logger.warning("news_adapter_disabled", reason=str(e))

        if not self.adapters:
            raise ValueError("No source adapters enabled! Check configuration.")

        logger.info(
            "pipeline_initialized",
            adapters=list(self.adapters.keys()),
            max_items=self.config.ingestion.max_items_per_run,
            cost_budget=self.config.ingestion.cost_budget_usd,
        )

    async def validate_credentials(self) -> dict[str, bool]:
        """Validate API credentials for all enabled sources."""
        results = {}

        for name, adapter in self.adapters.items():
            try:
                valid = await adapter.validate_credentials()
                results[name] = valid

                if not valid:
                    logger.error(f"{name}_credentials_invalid")

            except Exception as e:
                results[name] = False
                logger.error(f"{name}_validation_error", error=str(e))

        return results

    async def fetch_all_sources(
        self,
        queries: list[str] | None = None,
        since: datetime | None = None,
    ) -> list[IngestedItem]:
        """Fetch items from all enabled sources concurrently.

        Args:
            queries: Search queries/topics
            since: Only fetch items newer than this timestamp

        Returns:
            List of all fetched items

        """
        # Calculate items per source
        total_budget = self.config.ingestion.max_items_per_run
        items_per_source = total_budget // len(self.adapters)

        # Fetch from all sources concurrently
        fetch_tasks = []

        for name, adapter in self.adapters.items():
            task = asyncio.create_task(
                self._fetch_from_source(
                    name,
                    adapter,
                    queries=queries,
                    max_items=items_per_source,
                    since=since,
                ),
            )
            fetch_tasks.append(task)

        results = await asyncio.gather(*fetch_tasks, return_exceptions=True)

        # Flatten results and track metrics
        all_items = []

        for result in results:
            if isinstance(result, Exception):
                logger.error("source_fetch_failed", error=str(result))
            else:
                all_items.extend(result)

        logger.info("fetch_completed", total_items=len(all_items), sources_used=len(self.adapters))

        return all_items

    async def _fetch_from_source(
        self,
        source_name: str,
        adapter,
        queries: list[str] | None,
        max_items: int,
        since: datetime | None,
    ) -> list[IngestedItem]:
        """Fetch items from a single source."""
        items = []

        try:
            async for item in adapter.fetch_items(
                queries=queries,
                max_items=max_items,
                since=since,
            ):
                items.append(item)
                items_fetched.labels(source=source_name).inc()

            logger.info("source_fetch_success", source=source_name, items_fetched=len(items))

        except Exception as e:
            logger.error("source_fetch_error", source=source_name, error=str(e))

        return items

    async def classify_items(self, items: list[IngestedItem]) -> dict[str, TierScore]:
        """Classify all items using Gemini.

        Args:
            items: List of items to classify

        Returns:
            Dictionary mapping item IDs to TierScores

        """
        if not self.config.features.enable_tier_classification:
            logger.warning("tier_classification_disabled")
            return {}

        logger.info("classification_started", total_items=len(items))

        scores = await self.classifier.classify_batch(items, max_concurrent=10)

        # Track metrics
        for score in scores.values():
            items_classified.labels(tier=f"tier_{score.tier}").inc()

        # Log distribution
        distribution = self.classifier.get_tier_distribution(scores)
        quality_metrics = self.classifier.get_quality_metrics(scores)

        logger.info("classification_completed", distribution=distribution, quality=quality_metrics)

        return scores

    def apply_quality_gates(
        self,
        items: list[IngestedItem],
        scores: dict[str, TierScore],
    ) -> tuple[list[IngestedItem], list[IngestedItem]]:
        """Apply quality gates to filter low-quality items.

        Quality gates:
        - Relevance score ≥ 70%
        - Completeness ≥ 95% (has title, content, author)
        - Timeliness < 24h for Tier 1 items

        Returns:
            Tuple of (accepted_items, rejected_items)

        """
        accepted = []
        rejected = []

        for item in items:
            score = scores.get(item.id)

            if not score:
                rejected.append(item)
                continue

            # Check relevance gate
            if score.relevance < self.config.classification.relevance_min_score:
                logger.debug("item_rejected_relevance", item_id=item.id, relevance=score.relevance)
                rejected.append(item)
                continue

            # Check completeness gate
            required_fields = [item.title, item.content, item.author]
            completeness = sum(1 for f in required_fields if f) / len(required_fields)

            if completeness < self.config.classification.completeness_min_pct:
                logger.debug(
                    "item_rejected_completeness",
                    item_id=item.id,
                    completeness=completeness,
                )
                rejected.append(item)
                continue

            # Check timeliness gate for Tier 1 items
            if score.tier == 1:
                max_age = self.config.classification.timeliness_tier_1_hours
                if item.age_hours > max_age:
                    logger.debug(
                        "item_rejected_timeliness",
                        item_id=item.id,
                        age_hours=item.age_hours,
                        tier=1,
                    )
                    rejected.append(item)
                    continue

            accepted.append(item)

        logger.info(
            "quality_gates_applied",
            accepted=len(accepted),
            rejected=len(rejected),
            pass_rate=round(len(accepted) / len(items) * 100, 1) if items else 0,
        )

        return accepted, rejected

    def calculate_costs(self) -> dict:
        """Calculate total pipeline costs."""
        adapter_costs = {
            name: adapter.get_stats()["cost_incurred_usd"]
            for name, adapter in self.adapters.items()
        }

        classifier_cost = self.classifier.get_stats()["estimated_cost_usd"]

        total_cost = sum(adapter_costs.values()) + classifier_cost

        # Update Prometheus gauge
        pipeline_cost.set(total_cost)

        return {
            "total_usd": round(total_cost, 2),
            "by_source": adapter_costs,
            "classification": classifier_cost,
            "budget_usd": self.config.ingestion.cost_budget_usd,
            "budget_remaining_usd": round(self.config.ingestion.cost_budget_usd - total_cost, 2),
            "over_budget": total_cost > self.config.ingestion.cost_budget_usd,
        }

    @pipeline_duration.time()
    async def run(self, queries: list[str] | None = None, since: datetime | None = None) -> dict:
        """Execute the full ingestion pipeline.

        Args:
            queries: Search queries/topics
            since: Only ingest items newer than this timestamp

        Returns:
            Pipeline execution summary

        """
        start_time = datetime.utcnow()

        logger.info("pipeline_run_started", queries=queries, since=since)

        # Step 1: Validate credentials
        credentials_valid = await self.validate_credentials()

        if not all(credentials_valid.values()):
            logger.error("credential_validation_failed", results=credentials_valid)

        # Step 2: Fetch items from all sources
        items = await self.fetch_all_sources(queries=queries, since=since)

        if not items:
            logger.warning("no_items_fetched")
            return {
                "status": "completed",
                "items_fetched": 0,
                "items_accepted": 0,
                "runtime_seconds": 0,
            }

        # Step 3: Classify items
        scores = await self.classify_items(items)

        # Step 4: Apply quality gates
        accepted, rejected = self.apply_quality_gates(items, scores)

        # Step 5: Calculate costs
        costs = self.calculate_costs()

        # Calculate runtime
        runtime = (datetime.utcnow() - start_time).total_seconds()

        # Build summary
        summary = {
            "status": "completed",
            "timestamp": start_time.isoformat(),
            "runtime_seconds": round(runtime, 1),
            "runtime_minutes": round(runtime / 60, 1),
            "items_fetched": len(items),
            "items_accepted": len(accepted),
            "items_rejected": len(rejected),
            "pass_rate_pct": round(len(accepted) / len(items) * 100, 1) if items else 0,
            "tier_distribution": self.classifier.get_tier_distribution(scores),
            "quality_metrics": self.classifier.get_quality_metrics(scores),
            "costs": costs,
            "source_stats": {name: adapter.get_stats() for name, adapter in self.adapters.items()},
            "within_budget": not costs["over_budget"],
            "within_runtime_limit": runtime < (self.config.ingestion.runtime_limit_minutes * 60),
        }

        logger.info("pipeline_run_completed", **summary)

        return summary

    async def close(self) -> None:
        """Close all adapters and cleanup resources."""
        for adapter in self.adapters.values():
            await adapter.close()

        logger.info("pipeline_closed")
