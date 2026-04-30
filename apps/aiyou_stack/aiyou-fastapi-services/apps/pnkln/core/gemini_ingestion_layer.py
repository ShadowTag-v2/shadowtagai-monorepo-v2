"""GEMINI INGESTION LAYER - Batch Intelligence Collection Pipeline
================================================================

ARCHITECTURE: GKE CronJob Multi-Container (vs Judge 6 Real-Time)
RUNTIME: ~45 min/night batch processing (vs p99≤90ms real-time SLA)
PURPOSE: Proactive intelligence collection (vs reactive validation)

SK PATTERN ADAPTATION:
---------------------
Uses SAME Sequential Pipeline pattern from Judge 6, but adapted for:
- Batch processing (nightly cron) vs real-time requests
- Multi-source collection vs single request validation
- Quality gates (items, sources, costs) vs coverage metrics
- Ethical compliance vs enforcement rules

COMPLEMENTARY TO JUDGE #6:
--------------------------
Ingestion Layer (Upstream):        Judge 6 (Downstream):
┌─────────────────────┐           ┌──────────────────────┐
│ Nightly Collection  │           │ Real-time Validation │
│ ~45 min runtime     │  ────────>│ p99≤90ms SLA         │
│ Quality Gates       │           │ 98% Coverage         │
│ Ethical Crawling    │           │ ATP 5-19 Governance  │
└─────────────────────┘           └──────────────────────┘

PERFORMANCE TARGETS:
-------------------
- Runtime: ≤45 min/night (batch efficiency)
- Items/day: 1000-5000 (quality over quantity)
- Sources: 8+ active (YouTube, Twitter, News, etc.)
- Cost/item: ~$0.015 (monthly ~$77 at 5K items)
- Tier 1 ratio: ≥40% (high-value intelligence)

INTEGRATION POINTS:
------------------
- CALLED BY: Scheduler (GKE CronJob), NS mesh services
- CALLS TO: Judge 6 (validation), Cor Brain (routing), NS (persistence)
- HANDOFF: Ingested data → Judge 6 validation → Storage

QUALITY FOCUS:
-------------
- Relevance: Is data actionable for downstream?
- Timeliness: Fresh data (≤24h old for news)
- Completeness: Full metadata (author, timestamp, source)
- Diversity: Balanced across sources (no single-source dominance)

Author: Pnkln Architecture Team
Version: 1.0.0
License: Proprietary
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum

from pnkln.core.cor_orchestrator import ExecutionContext, SequentialPipeline
from pnkln.core.jr_engine import JREngine

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMERATIONS
# ============================================================================


class SourceType(StrEnum):
    """Supported intelligence sources."""

    YOUTUBE = "youtube"
    TWITTER = "twitter"
    NEWS_API = "news_api"
    RSS_FEEDS = "rss_feeds"
    REDDIT = "reddit"
    LINKEDIN = "linkedin"
    GITHUB = "github"
    ACADEMIC = "academic"


class DataTier(StrEnum):
    """Data quality tiers for classification."""

    TIER_1 = "tier_1"  # High-value: verified sources, unique insights
    TIER_2 = "tier_2"  # Medium-value: standard sources, general content
    TIER_3 = "tier_3"  # Low-value: noise, duplicates, low relevance


class IngestionStatus(StrEnum):
    """Status of ingestion job."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL_SUCCESS = "partial_success"


# ============================================================================
# DATA STRUCTURES
# ============================================================================


@dataclass
class IntelligenceItem:
    """Single intelligence item ingested from source.

    Attributes:
        item_id: Unique identifier
        source_type: Where it came from (YouTube, Twitter, etc.)
        content: Main content/text
        metadata: Additional data (author, timestamp, URL, etc.)
        tier: Quality classification (Tier 1/2/3)
        relevance_score: 0.0-1.0 score for relevance
        timestamp: When ingested
        cost_usd: Cost to ingest this item

    """

    item_id: str
    source_type: SourceType
    content: str
    metadata: dict
    tier: DataTier
    relevance_score: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    cost_usd: float = 0.0

    def is_fresh(self, max_age_hours: int = 24) -> bool:
        """Check if item is fresh (≤24h old)."""
        age = datetime.utcnow() - self.timestamp
        return age.total_seconds() / 3600 <= max_age_hours

    def is_high_value(self) -> bool:
        """Check if item is Tier 1 (high-value)."""
        return self.tier == DataTier.TIER_1


@dataclass
class SourceCoverageMetrics:
    """Metrics for multi-source coverage analysis."""

    source_type: SourceType
    items_ingested: int = 0
    items_tier_1: int = 0
    items_tier_2: int = 0
    items_tier_3: int = 0
    avg_relevance_score: float = 0.0
    total_cost_usd: float = 0.0
    errors: int = 0
    last_successful_fetch: datetime | None = None

    @property
    def tier_1_ratio(self) -> float:
        """Calculate Tier 1 ratio (target ≥40%)."""
        return self.items_tier_1 / max(self.items_ingested, 1)

    @property
    def cost_per_item(self) -> float:
        """Calculate cost per item."""
        return self.total_cost_usd / max(self.items_ingested, 1)


@dataclass
class IngestionResult:
    """Result from nightly ingestion job.

    Attributes:
        job_id: Unique job identifier
        status: Job status (completed, failed, etc.)
        runtime_minutes: Total runtime
        items_collected: All items ingested
        source_metrics: Per-source metrics
        quality_gates_passed: Which gates were met
        total_cost_usd: Total job cost
        am_briefing_delivered: Was morning briefing sent?
        errors: List of errors encountered

    """

    job_id: str
    status: IngestionStatus
    runtime_minutes: float
    items_collected: list[IntelligenceItem]
    source_metrics: dict[SourceType, SourceCoverageMetrics]
    quality_gates_passed: dict[str, bool]
    total_cost_usd: float
    am_briefing_delivered: bool = False
    errors: list[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)

    @property
    def total_items(self) -> int:
        """Total items ingested."""
        if self.items_collected:
            return len(self.items_collected)
        return sum(m.items_ingested for m in self.source_metrics.values())

    @property
    def tier_1_ratio(self) -> float:
        """Overall Tier 1 ratio (target ≥40%)."""
        if self.items_collected:
            tier_1_count = sum(1 for item in self.items_collected if item.tier == DataTier.TIER_1)
        else:
            tier_1_count = sum(m.items_tier_1 for m in self.source_metrics.values())

        return tier_1_count / max(self.total_items, 1)

    @property
    def avg_cost_per_item(self) -> float:
        """Average cost per item."""
        return self.total_cost_usd / max(self.total_items, 1)

    @property
    def active_sources_count(self) -> int:
        """Number of sources with successful fetches."""
        return sum(1 for m in self.source_metrics.values() if m.items_ingested > 0)


# ============================================================================
# MOCK SOURCE COLLECTORS (Replace with real implementations)
# ============================================================================


class BaseSourceCollector:
    """Base class for source-specific collectors."""

    def __init__(self, source_type: SourceType):
        self.source_type = source_type
        self.cost_per_api_call = 0.001  # Mock cost

    async def collect(self, _max_items: int = 100) -> SourceCoverageMetrics:
        """Collect items from source.

        Args:
            max_items: Max items to collect

        Returns:
            SourceCoverageMetrics with results

        """
        raise NotImplementedError


class YouTubeCollector(BaseSourceCollector):
    """YouTube intelligence collector (mock implementation)."""

    def __init__(self):
        super().__init__(SourceType.YOUTUBE)

    async def collect(self, _max_items: int = 100) -> SourceCoverageMetrics:
        """Collect YouTube videos matching intelligence criteria."""
        await asyncio.sleep(5.0)  # Simulate API calls

        metrics = SourceCoverageMetrics(source_type=self.source_type)
        metrics.items_ingested = 150
        metrics.items_tier_1 = 60  # 40% Tier 1
        metrics.items_tier_2 = 70
        metrics.items_tier_3 = 20
        metrics.avg_relevance_score = 0.78
        metrics.total_cost_usd = 0.15  # $0.001/item
        metrics.last_successful_fetch = datetime.utcnow()

        return metrics


class TwitterCollector(BaseSourceCollector):
    """Twitter intelligence collector (mock implementation)."""

    def __init__(self):
        super().__init__(SourceType.TWITTER)

    async def collect(self, _max_items: int = 100) -> SourceCoverageMetrics:
        """Collect Twitter posts matching intelligence criteria."""
        await asyncio.sleep(4.0)  # Simulate API calls

        metrics = SourceCoverageMetrics(source_type=self.source_type)
        metrics.items_ingested = 200
        metrics.items_tier_1 = 80  # 40% Tier 1
        metrics.items_tier_2 = 90
        metrics.items_tier_3 = 30
        metrics.avg_relevance_score = 0.72
        metrics.total_cost_usd = 0.20
        metrics.last_successful_fetch = datetime.utcnow()

        return metrics


class NewsAPICollector(BaseSourceCollector):
    """News API collector (mock implementation)."""

    def __init__(self):
        super().__init__(SourceType.NEWS_API)

    async def collect(self, _max_items: int = 100) -> SourceCoverageMetrics:
        """Collect news articles."""
        await asyncio.sleep(3.0)

        metrics = SourceCoverageMetrics(source_type=self.source_type)
        metrics.items_ingested = 120
        metrics.items_tier_1 = 50  # 42% Tier 1
        metrics.items_tier_2 = 50
        metrics.items_tier_3 = 20
        metrics.avg_relevance_score = 0.85
        metrics.total_cost_usd = 0.12
        metrics.last_successful_fetch = datetime.utcnow()

        return metrics


# ============================================================================
# QUALITY GATES
# ============================================================================


class QualityGates:
    """Quality gates for ingestion pipeline.

    Gates replace Judge 6's 98% coverage with multi-dimensional checks:
    - Items/day: 1000-5000 (quality over quantity)
    - Active sources: ≥8 (diversity)
    - Cost/item: ≤$0.02 (efficiency)
    - Tier 1 ratio: ≥40% (value)
    - Relevance: ≥0.70 average (actionability)
    """

    def __init__(self):
        self.gates = {
            "min_items_per_day": 1000,
            "max_items_per_day": 5000,
            "min_active_sources": 8,
            "max_cost_per_item": 0.02,
            "min_tier_1_ratio": 0.40,
            "min_avg_relevance": 0.70,
        }

    def evaluate(self, result: IngestionResult) -> dict[str, bool]:
        """Evaluate all quality gates.

        Args:
            result: Ingestion result to check

        Returns:
            Dict of gate_name → passed (bool)

        """
        gates_passed = {}

        # Gate 1: Items per day in range
        gates_passed["items_per_day"] = (
            self.gates["min_items_per_day"] <= result.total_items <= self.gates["max_items_per_day"]
        )

        # Gate 2: Active sources (diversity)
        gates_passed["active_sources"] = (
            result.active_sources_count >= self.gates["min_active_sources"]
        )

        # Gate 3: Cost per item
        gates_passed["cost_per_item"] = result.avg_cost_per_item <= self.gates["max_cost_per_item"]

        # Gate 4: Tier 1 ratio (high-value intelligence)
        gates_passed["tier_1_ratio"] = result.tier_1_ratio >= self.gates["min_tier_1_ratio"]

        # Gate 5: Average relevance score
        avg_relevance = sum(m.avg_relevance_score for m in result.source_metrics.values()) / max(
            len(result.source_metrics),
            1,
        )
        gates_passed["avg_relevance"] = avg_relevance >= self.gates["min_avg_relevance"]

        return gates_passed


# ============================================================================
# GEMINI INGESTION LAYER
# ============================================================================


class GeminiIngestionLayer:
    """Batch intelligence collection pipeline using SK Sequential Pattern.

    RUNTIME: ~45 min/night (vs Judge 6 p99≤90ms)
    PATTERN: Sequential Pipeline with quality gates
    INTEGRATION: Called by GKE CronJob, calls Judge 6 for validation

    Pipeline Stages:
    1. Multi-source collection (~30 min) - Parallel collectors
    2. Tier classification (~10 min) - ML-based scoring
    3. Quality gate validation (~2 min) - Check thresholds
    4. AM briefing generation (~3 min) - Summary for morning delivery
    """

    def __init__(self):
        """Initialize Gemini Ingestion Layer."""
        self.jr_engine = JREngine()
        self.quality_gates = QualityGates()

        # Initialize collectors
        self.collectors = {
            SourceType.YOUTUBE: YouTubeCollector(),
            SourceType.TWITTER: TwitterCollector(),
            SourceType.NEWS_API: NewsAPICollector(),
            # Add more collectors as needed
        }

        # Build sequential pipeline
        self.pipeline = SequentialPipeline("gemini_ingestion_pipeline")
        self._build_pipeline()

        logger.info("Gemini Ingestion Layer initialized (~45 min runtime target)")

    def _build_pipeline(self) -> None:
        """Construct batch ingestion pipeline stages."""

        # Stage 1: Multi-source collection (parallel)
        async def multi_source_collection(ctx: ExecutionContext, job_config: dict) -> dict:
            """Collect from all active sources in parallel."""
            start_time = time.perf_counter()

            # Execute all collectors concurrently
            tasks = [
                collector.collect(max_items=job_config.get("max_items_per_source", 500))
                for collector in self.collectors.values()
            ]

            source_metrics_list = await asyncio.gather(*tasks, return_exceptions=True)

            # Build metrics dict
            source_metrics = {}
            for collector_type, metrics in zip(
                self.collectors.keys(),
                source_metrics_list,
                strict=False,
            ):
                if isinstance(metrics, Exception):
                    logger.error(f"Collector {collector_type} failed: {metrics}")
                    source_metrics[collector_type] = SourceCoverageMetrics(
                        source_type=collector_type,
                    )
                else:
                    source_metrics[collector_type] = metrics

            latency_minutes = (time.perf_counter() - start_time) / 60
            ctx.set_variable("collection_time_minutes", latency_minutes)
            ctx.set_variable("source_metrics", source_metrics)

            logger.info(f"Multi-source collection completed in {latency_minutes:.1f} min")

            return {"job_config": job_config, "source_metrics": source_metrics}

        # Stage 2: Tier classification
        async def tier_classification(ctx: ExecutionContext, data: dict) -> dict:
            """Classify items into Tier 1/2/3 based on quality."""
            start_time = time.perf_counter()

            data["source_metrics"]

            # Mock tier classification (real implementation would use ML model)
            # Already done in collectors for demo, but would re-score here

            latency_minutes = (time.perf_counter() - start_time) / 60
            ctx.set_variable("classification_time_minutes", latency_minutes)

            logger.info(f"Tier classification completed in {latency_minutes:.1f} min")

            return data

        # Stage 3: Quality gate validation
        async def quality_gate_validation(ctx: ExecutionContext, data: dict) -> dict:
            """Validate against quality gates."""
            start_time = time.perf_counter()

            # Build mock IngestionResult for gate checking
            source_metrics = data["source_metrics"]
            sum(m.items_ingested for m in source_metrics.values())
            total_cost = sum(m.total_cost_usd for m in source_metrics.values())
            sum(m.items_tier_1 for m in source_metrics.values())

            mock_result = IngestionResult(
                job_id=ctx.request_id,
                status=IngestionStatus.RUNNING,
                runtime_minutes=0,  # Will be calculated
                items_collected=[],  # Not needed for gate check
                source_metrics=source_metrics,
                quality_gates_passed={},
                total_cost_usd=total_cost,
            )

            gates_passed = self.quality_gates.evaluate(mock_result)
            ctx.set_variable("quality_gates_passed", gates_passed)

            latency_minutes = (time.perf_counter() - start_time) / 60

            logger.info(
                f"Quality gates: {sum(gates_passed.values())}/{len(gates_passed)} passed "
                f"({latency_minutes:.1f} min)",
            )

            return {**data, "quality_gates_passed": gates_passed}

        # Stage 4: AM briefing generation
        async def am_briefing_generation(ctx: ExecutionContext, data: dict) -> dict:
            """Generate morning briefing summary."""
            start_time = time.perf_counter()

            # Mock briefing generation (real implementation would use Gemini)
            source_metrics = data["source_metrics"]
            gates_passed = data["quality_gates_passed"]

            briefing = {
                "title": "Daily Intelligence Briefing",
                "date": datetime.utcnow().strftime("%Y-%m-%d"),
                "summary": {
                    "total_items": sum(m.items_ingested for m in source_metrics.values()),
                    "active_sources": len(
                        [m for m in source_metrics.values() if m.items_ingested > 0],
                    ),
                    "tier_1_items": sum(m.items_tier_1 for m in source_metrics.values()),
                    "gates_passed": f"{sum(gates_passed.values())}/{len(gates_passed)}",
                },
                "top_insights": [
                    "Mock insight 1: Trend detected in YouTube data",
                    "Mock insight 2: High relevance scores from News API",
                    "Mock insight 3: Twitter volume spike in tech sector",
                ],
            }

            ctx.set_variable("am_briefing", briefing)
            ctx.set_variable("am_briefing_delivered", True)

            latency_minutes = (time.perf_counter() - start_time) / 60

            logger.info(f"AM briefing generated in {latency_minutes:.1f} min")

            return {**data, "am_briefing": briefing, "am_briefing_delivered": True}

        # Add stages to pipeline
        self.pipeline.add_stage(
            "multi_source_collection",
            multi_source_collection,
            timeout_ms=35 * 60 * 1000,  # 35 min timeout
        )

        self.pipeline.add_stage(
            "tier_classification",
            tier_classification,
            timeout_ms=12 * 60 * 1000,  # 12 min timeout
        )

        self.pipeline.add_stage(
            "quality_gate_validation",
            quality_gate_validation,
            timeout_ms=3 * 60 * 1000,  # 3 min timeout
        )

        self.pipeline.add_stage(
            "am_briefing_generation",
            am_briefing_generation,
            timeout_ms=5 * 60 * 1000,  # 5 min timeout
        )

    async def run_nightly_job(
        self,
        job_id: str,
        max_items_per_source: int = 500,
    ) -> IngestionResult:
        """Execute nightly ingestion job.

        Args:
            job_id: Unique job identifier
            max_items_per_source: Max items to collect per source

        Returns:
            IngestionResult with full job metrics

        Runtime Target:
            ≤45 minutes total

        """
        start_time = time.perf_counter()

        logger.info(f"Starting nightly ingestion job {job_id} (~45 min target)")

        # Create execution context (45 min budget)
        context = ExecutionContext(
            request_id=job_id,
            latency_budget_ms=45 * 60 * 1000,  # 45 min in milliseconds
        )

        # Job configuration
        job_config = {
            "max_items_per_source": max_items_per_source,
            "enable_ethical_checks": True,
        }

        try:
            # Execute pipeline
            pipeline_result = await self.pipeline.execute(context, job_config)

            # Build final result
            runtime_minutes = (time.perf_counter() - start_time) / 60

            result = IngestionResult(
                job_id=job_id,
                status=IngestionStatus.COMPLETED,
                runtime_minutes=runtime_minutes,
                items_collected=[],  # Mock (would be full list)
                source_metrics=pipeline_result["source_metrics"],
                quality_gates_passed=pipeline_result["quality_gates_passed"],
                total_cost_usd=sum(
                    m.total_cost_usd for m in pipeline_result["source_metrics"].values()
                ),
                am_briefing_delivered=pipeline_result.get("am_briefing_delivered", False),
            )

            # Check runtime SLA
            if runtime_minutes > 45:
                logger.warning(f"Job {job_id} exceeded 45 min target: {runtime_minutes:.1f} min")
            else:
                logger.info(
                    f"Job {job_id} completed in {runtime_minutes:.1f} min (under 45 min target)",
                )

            return result

        except Exception as e:
            runtime_minutes = (time.perf_counter() - start_time) / 60
            logger.error(f"Job {job_id} failed after {runtime_minutes:.1f} min: {e}")

            return IngestionResult(
                job_id=job_id,
                status=IngestionStatus.FAILED,
                runtime_minutes=runtime_minutes,
                items_collected=[],
                source_metrics={},
                quality_gates_passed={},
                total_cost_usd=0.0,
                errors=[str(e)],
            )


# ============================================================================
# EXAMPLE USAGE
# ============================================================================


async def example_usage():
    """Demonstrate Gemini Ingestion Layer."""
    ingestion = GeminiIngestionLayer()

    # Run nightly job
    print("=== Nightly Intelligence Collection Job ===")
    result = await ingestion.run_nightly_job(job_id="job_2025_11_15", max_items_per_source=500)

    print(f"\nJob Status: {result.status.value}")
    print(f"Runtime: {result.runtime_minutes:.1f} min (target ≤45 min)")
    print(f"Total Items: {result.total_items}")
    print(f"Active Sources: {result.active_sources_count}")
    print(f"Tier 1 Ratio: {result.tier_1_ratio:.1%} (target ≥40%)")
    print(f"Cost per Item: ${result.avg_cost_per_item:.3f}")
    print(f"Total Cost: ${result.total_cost_usd:.2f}")
    print(f"AM Briefing Delivered: {result.am_briefing_delivered}")

    print(
        f"\nQuality Gates ({sum(result.quality_gates_passed.values())}/{len(result.quality_gates_passed)} passed):",
    )
    for gate, passed in result.quality_gates_passed.items():
        status = "✅" if passed else "❌"
        print(f"  {status} {gate}: {passed}")

    print("\nPer-Source Metrics:")
    for source_type, metrics in result.source_metrics.items():
        print(f"\n  {source_type.value.upper()}:")
        print(f"    Items: {metrics.items_ingested}")
        print(f"    Tier 1: {metrics.items_tier_1} ({metrics.tier_1_ratio:.1%})")
        print(f"    Avg Relevance: {metrics.avg_relevance_score:.2f}")
        print(f"    Cost: ${metrics.total_cost_usd:.3f}")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    asyncio.run(example_usage())
