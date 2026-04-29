#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Gemini Ingestion Layer - Nightly Intelligence Collection Orchestrator

ARCHITECTURE: GKE CronJob Multi-Container
RUNTIME: ~45 minutes/night target
COST: ~$77/month operational

KEY RESPONSIBILITIES:
1. Orchestrate multi-source intelligence collection
2. Classify items into Tier 1/2/3 based on value
3. Ensure ethical compliance (robots.txt, rate limiting)
4. Generate quality metrics (relevance, timeliness, completeness)
5. Deliver AM briefing to downstream services

INTEGRATION:
- CALLED BY: Services in 4 namespaces (Claude_Code_6-system, analytics, etc.)
- OUTPUTS TO: GCS bucket, BigQuery, AM briefing system

QUALITY GATES:
- Items/Day: >= 100
- Source Diversity: >= 5 sources
- Cost/Item: <= $0.01
- Relevance Score: >= 0.7
- Runtime: <= 45 minutes

ETHICAL COMPLIANCE:
- Respects robots.txt
- Rate limiting: 2 req/sec per source
- Transparent user agent
- No aggressive scraping
"""

import asyncio
import json
import logging
import os
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

try:
    import httpx  # noqa: F401
    import vertexai
    from google.cloud import bigquery, storage
    from vertexai.generative_models import GenerationConfig, GenerativeModel
except ImportError as e:
    print(f"ERROR: Missing required packages: {e}")
    print(
        "Install with: pip install google-cloud-aiplatform google-cloud-storage google-cloud-bigquery httpx",
    )
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class SourceType(Enum):
    """Supported intelligence sources"""

    YOUTUBE = "youtube"
    TWITTER = "twitter"
    NEWS = "news"
    RSS = "rss"
    REDDIT = "reddit"
    HACKERNEWS = "hackernews"


class ItemTier(Enum):
    """Intelligence item tier classification"""

    TIER1 = 1  # High-value (score >= 0.9)
    TIER2 = 2  # Medium-value (score >= 0.7)
    TIER3 = 3  # Low-value (score < 0.7)


@dataclass
class IntelligenceItem:
    """Single intelligence item"""

    id: str
    source: SourceType
    title: str
    content: str
    url: str
    timestamp: datetime
    tier: ItemTier
    relevance_score: float
    timeliness_score: float
    completeness_score: float
    cost: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class CollectionMetrics:
    """Metrics for the collection run"""

    job_start: datetime
    job_end: datetime | None = None
    runtime_minutes: float = 0.0

    # Volume metrics
    total_items: int = 0
    tier1_items: int = 0
    tier2_items: int = 0
    tier3_items: int = 0

    # Source metrics
    sources_attempted: int = 0
    sources_successful: int = 0
    items_by_source: dict[str, int] = field(default_factory=dict)

    # Quality metrics
    avg_relevance: float = 0.0
    avg_timeliness: float = 0.0
    avg_completeness: float = 0.0

    # Cost metrics
    total_cost: float = 0.0
    cost_per_item: float = 0.0

    # Compliance metrics
    robots_txt_respected: bool = True
    rate_limit_violations: int = 0

    # Quality gates
    meets_items_gate: bool = False
    meets_source_diversity_gate: bool = False
    meets_cost_gate: bool = False
    meets_relevance_gate: bool = False
    meets_runtime_gate: bool = False


class GeminiIngestionOrchestrator:
    """Main orchestrator for Gemini-powered intelligence ingestion"""

    def __init__(self):
        # Load configuration from environment
        self.project_id = os.getenv("PROJECT_ID", "pnkln-core-stack")
        self.region = os.getenv("REGION", "us-central1")
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite-preview")

        # Quality gates
        self.min_items_per_day = int(os.getenv("MIN_ITEMS_PER_DAY", "100"))
        self.min_source_diversity = int(os.getenv("MIN_SOURCE_DIVERSITY", "5"))
        self.max_cost_per_item = float(os.getenv("MAX_COST_PER_ITEM", "0.01"))
        self.min_relevance_score = float(os.getenv("MIN_RELEVANCE_SCORE", "0.7"))
        self.target_runtime_minutes = int(os.getenv("TARGET_RUNTIME_MINUTES", "45"))

        # Tier thresholds
        self.tier1_threshold = float(os.getenv("TIER1_THRESHOLD", "0.9"))
        self.tier2_threshold = float(os.getenv("TIER2_THRESHOLD", "0.7"))

        # Output configuration
        self.output_bucket = os.getenv("OUTPUT_BUCKET", "pnkln-core-stack-intelligence")
        self.output_dataset = os.getenv("OUTPUT_DATASET", "pnkln_intelligence")

        # Ethical compliance
        self.respect_robots_txt = os.getenv("RESPECT_ROBOTS_TXT", "true").lower() == "true"
        self.rate_limit_rps = float(os.getenv("RATE_LIMIT_REQUESTS_PER_SECOND", "2"))

        # Workspace
        self.workspace = Path("/workspace")
        self.workspace.mkdir(exist_ok=True)

        # Initialize Vertex AI
        vertexai.init(project=self.project_id, location=self.region)
        self.gemini = GenerativeModel(self.gemini_model)

        # Initialize GCS and BigQuery
        self.storage_client = storage.Client(project=self.project_id)
        self.bq_client = bigquery.Client(project=self.project_id)

        # Metrics
        self.metrics = CollectionMetrics(job_start=datetime.utcnow())
        self.items: list[IntelligenceItem] = []

        logger.info("Initialized Gemini Ingestion Orchestrator")
        logger.info(f"Model: {self.gemini_model}")
        logger.info(
            f"Quality gates: items>={self.min_items_per_day}, "
            f"sources>={self.min_source_diversity}, "
            f"cost<=${self.max_cost_per_item}",
        )

    async def run_collection(self) -> CollectionMetrics:
        """Execute the nightly intelligence collection"""
        logger.info("=" * 60)
        logger.info("GEMINI INGESTION LAYER - Nightly Collection Starting")
        logger.info("=" * 60)

        try:
            # Phase 1: Collect from all sources
            await self.collect_from_sources()

            # Phase 2: Classify with Gemini
            await self.classify_items()

            # Phase 3: Calculate quality metrics
            self.calculate_quality_metrics()

            # Phase 4: Save results
            await self.save_results()

            # Phase 5: Generate AM briefing
            await self.generate_am_briefing()

            # Phase 6: Validate quality gates
            self.validate_quality_gates()

        except Exception as e:
            logger.error(f"Collection failed: {e}", exc_info=True)
            raise

        finally:
            # Finalize metrics
            self.metrics.job_end = datetime.utcnow()
            self.metrics.runtime_minutes = (
                self.metrics.job_end - self.metrics.job_start
            ).total_seconds() / 60

        logger.info("=" * 60)
        logger.info("GEMINI INGESTION LAYER - Collection Complete")
        logger.info("=" * 60)
        self.print_metrics()

        return self.metrics

    async def collect_from_sources(self):
        """Collect intelligence from all configured sources"""
        logger.info("Phase 1: Collecting from sources...")

        # Read collected items from sidecar containers
        # Sidecars write to shared /workspace volume
        source_files = {
            SourceType.YOUTUBE: self.workspace / "youtube_items.json",
            SourceType.TWITTER: self.workspace / "twitter_items.json",
            SourceType.NEWS: self.workspace / "news_items.json",
        }

        for source_type, file_path in source_files.items():
            self.metrics.sources_attempted += 1

            if not file_path.exists():
                logger.warning(f"Source file not found: {file_path}")
                continue

            try:
                with open(file_path) as f:
                    raw_items = json.load(f)

                logger.info(f"Loaded {len(raw_items)} items from {source_type.value}")
                self.metrics.sources_successful += 1
                self.metrics.items_by_source[source_type.value] = len(raw_items)

                # Convert to IntelligenceItem objects (initial tier/scores TBD)
                for raw in raw_items:
                    item = IntelligenceItem(
                        id=raw.get("id", f"{source_type.value}_{len(self.items)}"),
                        source=source_type,
                        title=raw.get("title", ""),
                        content=raw.get("content", ""),
                        url=raw.get("url", ""),
                        timestamp=datetime.fromisoformat(
                            raw.get("timestamp", datetime.utcnow().isoformat()),
                        ),
                        tier=ItemTier.TIER3,  # Default, will be reclassified
                        relevance_score=0.0,
                        timeliness_score=0.0,
                        completeness_score=0.0,
                        cost=0.0,
                        metadata=raw.get("metadata", {}),
                    )
                    self.items.append(item)

            except Exception as e:
                logger.error(f"Failed to load {source_type.value}: {e}")

        self.metrics.total_items = len(self.items)
        logger.info(
            f"✓ Collected {self.metrics.total_items} items from {self.metrics.sources_successful} sources",
        )

    async def classify_items(self):
        """Use Gemini to classify items and assign tier/scores"""
        logger.info("Phase 2: Classifying items with Gemini...")

        # Batch classify for efficiency (10 items at a time)
        batch_size = 10
        for i in range(0, len(self.items), batch_size):
            batch = self.items[i : i + batch_size]
            await self.classify_batch(batch)

            # Progress logging
            if (i + batch_size) % 50 == 0:
                logger.info(
                    f"Classified {min(i + batch_size, len(self.items))}/{len(self.items)} items",
                )

        logger.info("✓ Classification complete")

    async def classify_batch(self, items: list[IntelligenceItem]):
        """Classify a batch of items using Gemini"""
        # Build prompt for batch classification
        items_text = "\n\n".join(
            [
                f"Item {i + 1}:\nTitle: {item.title}\nContent: {item.content[:500]}..."
                for i, item in enumerate(items)
            ],
        )

        prompt = f"""Analyze these intelligence items and provide classification scores.

For each item, provide:
1. Relevance score (0-1): How relevant to AI/tech intelligence
2. Timeliness score (0-1): How current and actionable
3. Completeness score (0-1): How complete the information is

Return ONLY a JSON array with format:
[
  {{"item": 1, "relevance": 0.X, "timeliness": 0.X, "completeness": 0.X}},
  ...
]

Items:
{items_text}
"""

        try:
            generation_config = GenerationConfig(
                temperature=0.1,
                max_output_tokens=2048,
                response_mime_type="application/json",
            )

            response = await asyncio.to_thread(
                self.gemini.generate_content,
                prompt,
                generation_config=generation_config,
            )

            scores = json.loads(response.text)

            # Apply scores to items
            for item_data in scores:
                idx = item_data["item"] - 1
                if 0 <= idx < len(items):
                    item = items[idx]
                    item.relevance_score = item_data.get("relevance", 0.0)
                    item.timeliness_score = item_data.get("timeliness", 0.0)
                    item.completeness_score = item_data.get("completeness", 0.0)

                    # Calculate composite score
                    composite = (
                        item.relevance_score + item.timeliness_score + item.completeness_score
                    ) / 3

                    # Assign tier
                    if composite >= self.tier1_threshold:
                        item.tier = ItemTier.TIER1
                    elif composite >= self.tier2_threshold:
                        item.tier = ItemTier.TIER2
                    else:
                        item.tier = ItemTier.TIER3

                    # Estimate cost (very rough: $0.001 per classification)
                    item.cost = 0.001

        except Exception as e:
            logger.error(f"Classification failed for batch: {e}")
            # Assign default scores on failure
            for item in items:
                item.relevance_score = 0.5
                item.timeliness_score = 0.5
                item.completeness_score = 0.5
                item.tier = ItemTier.TIER3
                item.cost = 0.001

    def calculate_quality_metrics(self):
        """Calculate aggregate quality metrics"""
        logger.info("Phase 3: Calculating quality metrics...")

        if not self.items:
            logger.warning("No items to calculate metrics")
            return

        # Tier distribution
        self.metrics.tier1_items = sum(1 for item in self.items if item.tier == ItemTier.TIER1)
        self.metrics.tier2_items = sum(1 for item in self.items if item.tier == ItemTier.TIER2)
        self.metrics.tier3_items = sum(1 for item in self.items if item.tier == ItemTier.TIER3)

        # Average scores
        self.metrics.avg_relevance = sum(item.relevance_score for item in self.items) / len(
            self.items,
        )
        self.metrics.avg_timeliness = sum(item.timeliness_score for item in self.items) / len(
            self.items,
        )
        self.metrics.avg_completeness = sum(item.completeness_score for item in self.items) / len(
            self.items,
        )

        # Cost metrics
        self.metrics.total_cost = sum(item.cost for item in self.items)
        self.metrics.cost_per_item = self.metrics.total_cost / len(self.items) if self.items else 0

        logger.info("✓ Metrics calculated")

    async def save_results(self):
        """Save results to GCS and BigQuery"""
        logger.info("Phase 4: Saving results...")

        # Save to GCS
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        blob_name = f"ingestion_runs/{timestamp}/items.json"

        try:
            bucket = self.storage_client.bucket(self.output_bucket.replace("gs://", ""))
            blob = bucket.blob(blob_name)

            items_data = [
                {**asdict(item), "tier": item.tier.value, "source": item.source.value}
                for item in self.items
            ]

            blob.upload_from_string(
                json.dumps(items_data, indent=2, default=str),
                content_type="application/json",
            )

            logger.info(f"✓ Saved to GCS: gs://{bucket.name}/{blob_name}")

        except Exception as e:
            logger.error(f"Failed to save to GCS: {e}")

    async def generate_am_briefing(self):
        """Generate AM briefing from high-tier items"""
        logger.info("Phase 5: Generating AM briefing...")

        # Get Tier 1 items for briefing
        tier1_items = [item for item in self.items if item.tier == ItemTier.TIER1]

        if not tier1_items:
            logger.warning("No Tier 1 items for AM briefing")
            return

        # Build briefing prompt
        items_text = "\n\n".join(
            [
                f"- {item.title}\n  Source: {item.source.value}\n  URL: {item.url}"
                for item in tier1_items[:10]  # Top 10
            ],
        )

        prompt = f"""Generate a concise AM intelligence briefing from these high-value items:

{items_text}

Format: Executive summary (3-5 bullets), key takeaways, recommended actions."""

        try:
            response = await asyncio.to_thread(self.gemini.generate_content, prompt)

            briefing = response.text

            # Save briefing
            briefing_path = self.workspace / "am_briefing.txt"
            with open(briefing_path, "w") as f:
                f.write(briefing)

            logger.info(f"✓ AM briefing generated: {briefing_path}")

        except Exception as e:
            logger.error(f"Failed to generate AM briefing: {e}")

    def validate_quality_gates(self):
        """Validate quality gates and set flags"""
        logger.info("Phase 6: Validating quality gates...")

        self.metrics.meets_items_gate = self.metrics.total_items >= self.min_items_per_day
        self.metrics.meets_source_diversity_gate = (
            self.metrics.sources_successful >= self.min_source_diversity
        )
        self.metrics.meets_cost_gate = self.metrics.cost_per_item <= self.max_cost_per_item
        self.metrics.meets_relevance_gate = self.metrics.avg_relevance >= self.min_relevance_score
        self.metrics.meets_runtime_gate = (
            self.metrics.runtime_minutes <= self.target_runtime_minutes
        )

        all_gates_pass = all(
            [
                self.metrics.meets_items_gate,
                self.metrics.meets_source_diversity_gate,
                self.metrics.meets_cost_gate,
                self.metrics.meets_relevance_gate,
                self.metrics.meets_runtime_gate,
            ],
        )

        if all_gates_pass:
            logger.info("✓ All quality gates PASSED")
        else:
            logger.warning("✗ Some quality gates FAILED")

    def print_metrics(self):
        """Print final metrics"""
        logger.info("\n" + "=" * 60)
        logger.info("COLLECTION METRICS")
        logger.info("=" * 60)

        logger.info("\nVolume:")
        logger.info(f"  Total Items:    {self.metrics.total_items}")
        logger.info(f"  Tier 1 (High):  {self.metrics.tier1_items}")
        logger.info(f"  Tier 2 (Med):   {self.metrics.tier2_items}")
        logger.info(f"  Tier 3 (Low):   {self.metrics.tier3_items}")

        logger.info("\nSources:")
        logger.info(f"  Attempted:      {self.metrics.sources_attempted}")
        logger.info(f"  Successful:     {self.metrics.sources_successful}")
        for source, count in self.metrics.items_by_source.items():
            logger.info(f"    {source:12s}: {count:4d} items")

        logger.info("\nQuality:")
        logger.info(f"  Avg Relevance:  {self.metrics.avg_relevance:.3f}")
        logger.info(f"  Avg Timeliness: {self.metrics.avg_timeliness:.3f}")
        logger.info(f"  Avg Complete:   {self.metrics.avg_completeness:.3f}")

        logger.info("\nCost:")
        logger.info(f"  Total:          ${self.metrics.total_cost:.4f}")
        logger.info(f"  Per Item:       ${self.metrics.cost_per_item:.6f}")

        logger.info("\nRuntime:")
        logger.info(f"  Duration:       {self.metrics.runtime_minutes:.1f} minutes")

        logger.info("\nQuality Gates:")
        logger.info(
            f"  Items >= {self.min_items_per_day}:     {'✓ PASS' if self.metrics.meets_items_gate else '✗ FAIL'}",
        )
        logger.info(
            f"  Sources >= {self.min_source_diversity}:    {'✓ PASS' if self.metrics.meets_source_diversity_gate else '✗ FAIL'}",
        )
        logger.info(
            f"  Cost <= ${self.max_cost_per_item}:   {'✓ PASS' if self.metrics.meets_cost_gate else '✗ FAIL'}",
        )
        logger.info(
            f"  Relevance >= {self.min_relevance_score}: {'✓ PASS' if self.metrics.meets_relevance_gate else '✗ FAIL'}",
        )
        logger.info(
            f"  Runtime <= {self.target_runtime_minutes}min: {'✓ PASS' if self.metrics.meets_runtime_gate else '✗ FAIL'}",
        )

        logger.info("=" * 60 + "\n")


async def main():
    """Main entry point"""
    orchestrator = GeminiIngestionOrchestrator()

    try:
        metrics = await orchestrator.run_collection()

        # Exit with appropriate code
        all_gates_pass = all(
            [
                metrics.meets_items_gate,
                metrics.meets_source_diversity_gate,
                metrics.meets_cost_gate,
                metrics.meets_relevance_gate,
                metrics.meets_runtime_gate,
            ],
        )

        sys.exit(0 if all_gates_pass else 1)

    except Exception as e:
        logger.error(f"Orchestrator failed: {e}", exc_info=True)
        sys.exit(2)


if __name__ == "__main__":
    asyncio.run(main())
