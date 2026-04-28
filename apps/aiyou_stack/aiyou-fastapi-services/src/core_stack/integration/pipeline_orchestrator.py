# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""PNKLN Core Stack™ — Integration Pipeline Orchestrator
Handles data flow: Gemini Ingestion → Cloud Storage → Judge 6 → Services
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime

import redis.asyncio as redis
from google.cloud import pubsub_v1, storage

from .ingestion_models import IngestedItem, IngestionBriefing, JudgeDecision, SourceTier

logger = logging.getLogger(__name__)


@dataclass
class PipelineConfig:
    """Configuration for integration pipeline"""

    # Cloud Storage
    gcs_bucket: str = "pnkln-ingestion-daily"
    gcs_prefix: str = ""  # Optional subfolder

    # Pub/Sub
    pubsub_project: str = "pnkln-prod"
    pubsub_topic: str = "ingestion-complete"
    pubsub_subscription: str = "judge-6-updater"

    # Redis (Judge 6 cache)
    redis_host: str = "judge-6-redis.gke-inference-system.svc.cluster.local"
    redis_port: int = 6379
    redis_db: int = 0

    # Quality gates
    stale_data_threshold_hours: int = 26  # Alert if no new data in 26 hours
    consecutive_failures_rollback: int = 3  # Rollback after 3 failed ingestions


class IngestionPublisher:
    """Publishes completed ingestion briefing to Cloud Storage and Pub/Sub.
    Runs at end of Gemini Ingestion CronJob (inside quality-gate container).
    """

    def __init__(self, config: PipelineConfig):
        self.config = config
        self.gcs_client = storage.Client()
        self.pubsub_client = pubsub_v1.PublisherClient()
        self.bucket = self.gcs_client.bucket(config.gcs_bucket)

    def publish_briefing(self, briefing: IngestionBriefing) -> str:
        """Publish briefing to Cloud Storage and trigger Pub/Sub event.
        Returns: GCS path (gs://bucket/path)
        """
        # Validate quality gates first
        if not briefing.meets_quality_gates():
            logger.error(
                f"Briefing {briefing.briefing_date} failed quality gates",
                extra={
                    "total_items": briefing.total_items,
                    "avg_relevance": briefing.quality_metrics.avg_relevance,
                    "runtime_minutes": briefing.runtime_minutes,
                },
            )
            # Still publish for debugging, but mark as failed
            # Judge 6 will detect "failed_quality_gates" status

        # Generate GCS path: YYYY-MM-DD-briefing.json
        blob_name = f"{self.config.gcs_prefix}{briefing.briefing_date}-briefing.json"
        blob = self.bucket.blob(blob_name)

        # Upload JSON
        blob.upload_from_string(briefing.to_json(), content_type="application/json")

        gcs_path = f"gs://{self.config.gcs_bucket}/{blob_name}"
        logger.info(f"Published briefing to {gcs_path}")

        # Trigger Pub/Sub event for Judge 6 to consume
        topic_path = self.pubsub_client.topic_path(
            self.config.pubsub_project,
            self.config.pubsub_topic,
        )

        message_data = {
            "briefing_date": briefing.briefing_date,
            "gcs_path": gcs_path,
            "total_items": briefing.total_items,
            "quality_gates_met": briefing.meets_quality_gates(),
        }

        future = self.pubsub_client.publish(topic_path, data=str(message_data).encode("utf-8"))

        message_id = future.result()
        logger.info(f"Published Pub/Sub message {message_id}")

        return gcs_path


class Judge6Updater:
    """Subscribes to Pub/Sub events and updates Judge 6 Redis cache.
    Runs as sidecar in Judge 6 StatefulSet (gke-inference-system).
    """

    def __init__(self, config: PipelineConfig):
        self.config = config
        self.gcs_client = storage.Client()
        self.redis_client: redis.Redis | None = None
        self.subscriber = pubsub_v1.SubscriberClient()
        self.subscription_path = self.subscriber.subscription_path(
            config.pubsub_project,
            config.pubsub_subscription,
        )

    async def connect_redis(self):
        """Establish Redis connection (Judge 6 cache)"""
        self.redis_client = await redis.from_url(
            f"redis://{self.config.redis_host}:{self.config.redis_port}/{self.config.redis_db}",
        )
        logger.info("Connected to Judge 6 Redis cache")

    async def load_briefing_to_cache(self, gcs_path: str) -> bool:
        """Load ingestion briefing from GCS into Judge 6 Redis cache.
        Returns: True if successful, False if quality gates failed
        """
        # Download from GCS
        bucket_name, blob_name = gcs_path.replace("gs://", "").split("/", 1)
        bucket = self.gcs_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        json_str = blob.download_as_text()
        briefing = IngestionBriefing.from_json(json_str)

        logger.info(
            f"Loading briefing {briefing.briefing_date}: "
            f"{briefing.total_items} items, "
            f"quality gates: {briefing.meets_quality_gates()}",
        )

        # Check quality gates
        if not briefing.meets_quality_gates():
            logger.warning(
                f"Briefing {briefing.briefing_date} failed quality gates, using as fallback only",
            )
            # Store with "stale" prefix for manual review
            await self.redis_client.set(
                f"briefing:stale:{briefing.briefing_date}",
                briefing.to_json(),
                ex=86400 * 7,  # Keep for 7 days
            )
            return False

        # Load items into Redis for Judge 6 lookup
        pipeline = self.redis_client.pipeline()

        for item in briefing.items:
            # Store item by ID (fast lookup during validation)
            cache_key = f"item:{item.item_id}"
            pipeline.set(
                cache_key,
                item.to_dict(),
                ex=86400 * 30,  # Expire after 30 days
            )

            # Index by source tier (for analytics)
            tier_key = f"tier:{item.tier.value}:items"
            pipeline.sadd(tier_key, item.item_id)

        # Store briefing metadata
        pipeline.set("briefing:latest", briefing.briefing_date, ex=86400 * 30)

        pipeline.set(
            f"briefing:{briefing.briefing_date}:metadata",
            {
                "total_items": briefing.total_items,
                "tier_distribution": briefing.tier_distribution,
                "quality_metrics": briefing.quality_metrics.to_dict(),
            },
            ex=86400 * 30,
        )

        # Execute Redis pipeline (atomic)
        await pipeline.execute()

        logger.info(
            f"Loaded {briefing.total_items} items into Judge 6 cache ({briefing.briefing_date})",
        )

        return True

    async def pubsub_callback(self, message: pubsub_v1.subscriber.message.Message):
        """Callback for Pub/Sub subscription (triggered on new briefing)"""
        try:
            # Parse message
            data = eval(message.data.decode("utf-8"))
            gcs_path = data["gcs_path"]
            briefing_date = data["briefing_date"]

            logger.info(f"Received ingestion-complete event for {briefing_date}")

            # Load into Judge 6 cache
            success = await self.load_briefing_to_cache(gcs_path)

            if success:
                message.ack()
                logger.info(f"Successfully loaded {briefing_date} into Judge 6")
            else:
                # Quality gates failed, but still ack (logged for manual review)
                message.ack()
                logger.error(f"Quality gates failed for {briefing_date}")

        except Exception as e:
            logger.error(f"Error processing Pub/Sub message: {e}", exc_info=True)
            message.nack()  # Retry

    def start_listening(self):
        """Start Pub/Sub subscription (blocking)"""
        logger.info(f"Listening to {self.subscription_path}")
        streaming_pull_future = self.subscriber.subscribe(
            self.subscription_path,
            callback=lambda msg: asyncio.run(self.pubsub_callback(msg)),
        )

        try:
            streaming_pull_future.result()
        except KeyboardInterrupt:
            streaming_pull_future.cancel()
            logger.info("Stopped Pub/Sub listener")


class Judge6Client:
    """Client for services to query Judge 6 (real-time validation).
    Runs in gke-inference-system, gke-gateway-system, etc.
    """

    def __init__(self, config: PipelineConfig):
        self.config = config
        self.redis_client: redis.Redis | None = None

    async def connect(self):
        """Establish Redis connection to Judge 6 cache"""
        self.redis_client = await redis.from_url(
            f"redis://{self.config.redis_host}:{self.config.redis_port}/{self.config.redis_db}",
        )
        logger.info("Connected to Judge 6")

    async def validate_item(self, item_id: str) -> JudgeDecision:
        """Validate item against Judge 6 policies.
        SLA: <500μs p99 latency, ≥98% coverage
        """
        start_time = datetime.now()

        # Lookup item in cache
        cache_key = f"item:{item_id}"
        item_data = await self.redis_client.get(cache_key)

        latency_us = int((datetime.now() - start_time).total_seconds() * 1_000_000)

        if item_data is None:
            # Item not in cache (coverage gap)
            logger.warning(f"Item {item_id} not found in Judge 6 cache")
            return JudgeDecision(
                item_id=item_id,
                allowed=False,
                latency_us=latency_us,
                coverage=0.0,  # Coverage failure
                reasoning="Item not found in ingestion cache",
                fallback_triggered=True,
                risk_level="RA-1 (Extremely High)",  # Fail-closed
                prb_violations=["Unknown source"],
            )

        # Parse item
        item = IngestedItem.from_dict(eval(item_data))

        # Apply Judge 6 policies (simplified for example)
        # Real implementation: ATP 5-19 CRM, PRB framework, JR doctrine
        allowed = True
        risk_level = "RA-4 (Low)"
        prb_violations = []

        # Example policy: Tier 3 items require higher relevance
        if item.tier == SourceTier.TIER_3 and item.ingestion_score < 0.80:
            allowed = False
            risk_level = "RA-2 (High)"
            prb_violations.append("Low-quality Tier 3 source")

        # Example policy: Reject stale data (>7 days old)
        age_days = (datetime.now() - item.ingestion_timestamp).days
        if age_days > 7:
            allowed = False
            risk_level = "RA-3 (Moderate)"
            prb_violations.append(f"Stale data ({age_days} days old)")

        latency_us = int((datetime.now() - start_time).total_seconds() * 1_000_000)

        decision = JudgeDecision(
            item_id=item_id,
            allowed=allowed,
            latency_us=latency_us,
            coverage=1.0,  # Found in cache
            reasoning=f"Tier {item.tier.value} source, score {item.ingestion_score:.2f}",
            fallback_triggered=False,
            risk_level=risk_level,
            prb_violations=prb_violations,
        )

        # Log if SLA violated
        if not decision.meets_sla():
            logger.error(
                f"Judge 6 SLA violation: {latency_us}μs latency, {decision.coverage:.2%} coverage",
            )

        return decision

    async def get_stats(self) -> dict:
        """Get Judge 6 cache statistics"""
        latest_briefing = await self.redis_client.get("briefing:latest")

        tier_counts = {}
        for tier in [1, 2, 3]:
            tier_key = f"tier:{tier}:items"
            count = await self.redis_client.scard(tier_key)
            tier_counts[f"tier_{tier}"] = count

        return {
            "latest_briefing": latest_briefing.decode() if latest_briefing else None,
            "tier_distribution": tier_counts,
            "total_items": sum(tier_counts.values()),
        }


# Example usage / integration test
async def integration_test():
    """Simulate end-to-end pipeline:
    1. Gemini Ingestion publishes briefing
    2. Judge 6 Updater loads to cache
    3. Service validates item
    """
    config = PipelineConfig()

    # Simulate completed ingestion (would run in CronJob)
    from .ingestion_models import CostSummary, QualityMetrics

    briefing = IngestionBriefing(
        briefing_date="2025-11-15",
        ingestion_window_start=datetime(2025, 11, 15, 2, 0, 0),
        ingestion_window_end=datetime(2025, 11, 15, 2, 45, 0),
        total_items=47234,
        tier_distribution={"tier_1": 12456, "tier_2": 21089, "tier_3": 13689},
        top_topics=[{"topic": "AI Regulation", "items": 8234, "avg_score": 0.87}],
        quality_metrics=QualityMetrics(0.76, 0.94, 0.89, 23),
        cost_summary=CostSummary(2.54, 0.000054, {}, 0.14),
        items=[
            IngestedItem(
                item_id="ing_20251115_000001",
                source="youtube.com/c/cspan",
                tier=SourceTier.TIER_1,
                content_type="video_transcript",
                content="Senate hearing...",
                metadata={},
                ingestion_score=0.92,
                ingestion_timestamp=datetime.now(),
            ),
        ],
        runtime_minutes=44.5,
        crawler_version="v1.0.0",
        classifier_version="v1.0.0",
    )

    # Step 1: Publish (Gemini Ingestion)
    publisher = IngestionPublisher(config)
    gcs_path = publisher.publish_briefing(briefing)
    print(f"✓ Published briefing to {gcs_path}")

    # Step 2: Load to Judge 6 (Updater)
    updater = Judge6Updater(config)
    await updater.connect_redis()
    success = await updater.load_briefing_to_cache(gcs_path)
    print(f"✓ Loaded to Judge 6 cache: {success}")

    # Step 3: Validate item (Service)
    judge_client = Judge6Client(config)
    await judge_client.connect()
    decision = await judge_client.validate_item("ing_20251115_000001")
    print(f"✓ Judge 6 decision: {decision.allowed}, {decision.latency_us}μs")
    print(f"  SLA met: {decision.meets_sla()}")

    # Get stats
    stats = await judge_client.get_stats()
    print(f"✓ Cache stats: {stats}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(integration_test())
