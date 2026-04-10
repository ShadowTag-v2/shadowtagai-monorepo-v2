"""
Gemini Ingestion Layer - Core Intelligence Collection Pipeline

Nightly CronJob that ingests data from multiple sources for PNKLN Core Stack™
Integrates with V2X mesh for traffic/transportation intelligence enrichment.

Features:
- Ethical web crawling (robots.txt, rate limiting)
- Multi-source coverage (YouTube, Twitter, News, RSS, APIs)
- Tier classification (1=high value, 2=medium, 3=low)
- Gemini API integration for content analysis
- AM Briefing generation
- Cost tracking and optimization

Performance Targets:
- Runtime: ~45 min/night
- Items/day: 500-2000
- Sources: 10-20 diverse
- Cost/item: <$0.05
- Relevance score: >0.7
"""

import asyncio
import time
import hashlib
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SourceType(Enum):
    """Source types for ingestion"""
    YOUTUBE = "youtube"
    TWITTER = "twitter"
    NEWS = "news"
    RSS = "rss"
    API = "api"
    WEB = "web"
    V2X_MESH = "v2x_mesh"  # Integration with V2X mesh


class DataTier(Enum):
    """Data quality/value tiers"""
    TIER_1 = 1  # High value, verified, actionable
    TIER_2 = 2  # Medium value, needs validation
    TIER_3 = 3  # Low value, reference only


class RelevanceCategory(Enum):
    """Content relevance categories"""
    TRAFFIC = "traffic"
    TRANSPORTATION = "transportation"
    URBAN_MOBILITY = "urban_mobility"
    SAFETY = "safety"
    INFRASTRUCTURE = "infrastructure"
    POLICY = "policy"
    TECHNOLOGY = "technology"
    OTHER = "other"


@dataclass
class EthicalCrawlingConfig:
    """Configuration for ethical web crawling"""
    respect_robots_txt: bool = True
    rate_limit_requests_per_minute: int = 60
    user_agent: str = "ShadowTag-v2-Ingestion-Bot/1.0 (+https://ShadowTag-v2.ai/bot)"
    request_timeout_seconds: int = 30
    max_retries: int = 3
    backoff_multiplier: float = 2.0
    respect_crawl_delay: bool = True
    avoid_peak_hours: bool = True  # Don't crawl during 9am-5pm target timezone


@dataclass
class SourceConfig:
    """Configuration for a data source"""
    source_id: str
    source_type: SourceType
    url: str
    tier: DataTier
    relevance_categories: list[RelevanceCategory]
    enabled: bool = True
    crawl_frequency_hours: int = 24
    last_crawled: datetime | None = None
    api_key: str | None = None
    custom_headers: dict[str, str] = field(default_factory=dict)


@dataclass
class IngestedItem:
    """Ingested data item"""
    item_id: str
    source_id: str
    source_type: SourceType
    tier: DataTier
    title: str
    content: str
    url: str
    published_at: datetime
    ingested_at: datetime
    relevance_score: float  # 0.0 - 1.0
    relevance_categories: list[RelevanceCategory]
    metadata: dict[str, Any] = field(default_factory=dict)
    cost_cents: float = 0.0  # Processing cost
    gemini_analysis: dict[str, Any] | None = None


@dataclass
class IngestionMetrics:
    """Metrics for ingestion run"""
    run_id: str
    started_at: datetime
    completed_at: datetime | None = None
    runtime_seconds: float = 0.0

    # Items
    total_items_ingested: int = 0
    items_by_tier: dict[DataTier, int] = field(default_factory=lambda: {
        DataTier.TIER_1: 0,
        DataTier.TIER_2: 0,
        DataTier.TIER_3: 0
    })
    items_by_source: dict[str, int] = field(default_factory=dict)

    # Quality
    avg_relevance_score: float = 0.0
    timeliness_score: float = 0.0  # % items <24hrs old
    completeness_score: float = 0.0  # % items with full metadata

    # Costs
    total_cost_dollars: float = 0.0
    cost_per_item_cents: float = 0.0

    # Sources
    sources_crawled: int = 0
    sources_failed: int = 0

    # Ethical compliance
    robots_txt_violations: int = 0
    rate_limit_violations: int = 0


class EthicalCrawler:
    """Ethical web crawler with robots.txt and rate limiting"""

    def __init__(self, config: EthicalCrawlingConfig):
        self.config = config
        self.last_request_time: dict[str, float] = {}
        self.robots_cache: dict[str, dict] = {}

    async def can_crawl(self, url: str) -> tuple[bool, str]:
        """Check if URL can be crawled ethically"""
        # Check robots.txt if enabled
        if self.config.respect_robots_txt:
            allowed, reason = await self._check_robots_txt(url)
            if not allowed:
                return False, reason

        # Check rate limit
        domain = self._get_domain(url)
        if domain in self.last_request_time:
            time_since_last = time.time() - self.last_request_time[domain]
            min_interval = 60.0 / self.config.rate_limit_requests_per_minute

            if time_since_last < min_interval:
                return False, f"Rate limit: wait {min_interval - time_since_last:.1f}s"

        # Check peak hours if configured
        if self.config.avoid_peak_hours:
            hour = datetime.now().hour
            if 9 <= hour < 17:
                return False, "Avoiding peak hours (9am-5pm)"

        return True, "OK"

    async def _check_robots_txt(self, url: str) -> tuple[bool, str]:
        """Check robots.txt for URL"""
        domain = self._get_domain(url)

        # Check cache
        if domain in self.robots_cache:
            robots = self.robots_cache[domain]
            # TODO: Implement actual robots.txt parsing
            return robots.get("allowed", True), "Checked robots.txt"

        # Mock robots.txt check for now
        self.robots_cache[domain] = {"allowed": True}
        return True, "robots.txt allows crawling"

    def _get_domain(self, url: str) -> str:
        """Extract domain from URL"""
        from urllib.parse import urlparse
        return urlparse(url).netloc

    async def fetch(self, url: str, headers: dict | None = None) -> str | None:
        """Fetch URL with ethical crawling compliance"""
        can_crawl, reason = await self.can_crawl(url)

        if not can_crawl:
            logger.warning(f"Cannot crawl {url}: {reason}")
            return None

        # Record request time
        domain = self._get_domain(url)
        self.last_request_time[domain] = time.time()

        # Mock fetch for now
        logger.info(f"Fetching {url}")
        await asyncio.sleep(0.1)  # Simulate request

        return f"Mock content from {url}"


class GeminiAnalyzer:
    """Gemini API integration for content analysis"""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key

    async def analyze_content(
        self,
        title: str,
        content: str,
        source_type: SourceType
    ) -> dict[str, Any]:
        """
        Analyze content using Gemini API

        Returns:
            - relevance_score: 0.0 - 1.0
            - categories: List[RelevanceCategory]
            - summary: str
            - key_points: List[str]
            - sentiment: str
        """
        # Mock Gemini analysis for now
        # In production, this calls Gemini 2.0 Pro API

        await asyncio.sleep(0.05)  # Simulate API call

        # Simple keyword-based scoring
        content_lower = (title + " " + content).lower()

        relevance_score = 0.5
        categories = []

        if any(kw in content_lower for kw in ["traffic", "congestion", "jam"]):
            relevance_score += 0.2
            categories.append(RelevanceCategory.TRAFFIC)

        if any(kw in content_lower for kw in ["transport", "transit", "metro", "bus"]):
            relevance_score += 0.15
            categories.append(RelevanceCategory.TRANSPORTATION)

        if any(kw in content_lower for kw in ["safety", "accident", "collision", "crash"]):
            relevance_score += 0.2
            categories.append(RelevanceCategory.SAFETY)

        if any(kw in content_lower for kw in ["road", "highway", "infrastructure"]):
            relevance_score += 0.1
            categories.append(RelevanceCategory.INFRASTRUCTURE)

        if not categories:
            categories.append(RelevanceCategory.OTHER)

        relevance_score = min(1.0, relevance_score)

        return {
            "relevance_score": relevance_score,
            "categories": [c.value for c in categories],
            "summary": f"Analysis of {source_type.value} content about {', '.join([c.value for c in categories])}",
            "key_points": ["Point 1", "Point 2", "Point 3"],
            "sentiment": "neutral",
            "cost_cents": 0.02  # Gemini API cost per analysis
        }


class TierClassifier:
    """Classify ingested items into quality tiers"""

    def classify(self, item: IngestedItem) -> DataTier:
        """
        Classify item into tier based on:
        - Source credibility
        - Relevance score
        - Timeliness
        - Completeness
        """
        score = 0

        # Relevance (40% weight)
        if item.relevance_score >= 0.8:
            score += 40
        elif item.relevance_score >= 0.6:
            score += 25
        elif item.relevance_score >= 0.4:
            score += 10

        # Timeliness (30% weight)
        age_hours = (datetime.now() - item.published_at).total_seconds() / 3600
        if age_hours <= 6:
            score += 30
        elif age_hours <= 24:
            score += 20
        elif age_hours <= 168:  # 1 week
            score += 10

        # Source type (20% weight)
        if item.source_type in [SourceType.API, SourceType.V2X_MESH]:
            score += 20
        elif item.source_type in [SourceType.NEWS, SourceType.TWITTER]:
            score += 15
        else:
            score += 10

        # Completeness (10% weight)
        if item.metadata and len(item.metadata) >= 3:
            score += 10
        elif item.metadata:
            score += 5

        # Classify
        if score >= 75:
            return DataTier.TIER_1
        elif score >= 50:
            return DataTier.TIER_2
        else:
            return DataTier.TIER_3


class IngestionPipeline:
    """Main ingestion pipeline orchestrator"""

    def __init__(
        self,
        crawler_config: EthicalCrawlingConfig,
        gemini_api_key: str | None = None
    ):
        self.crawler = EthicalCrawler(crawler_config)
        self.analyzer = GeminiAnalyzer(gemini_api_key)
        self.classifier = TierClassifier()

        self.sources: list[SourceConfig] = []
        self.ingested_items: list[IngestedItem] = []
        self.metrics: IngestionMetrics | None = None

    def add_source(self, source: SourceConfig):
        """Add data source to pipeline"""
        self.sources.append(source)
        logger.info(f"Added source: {source.source_id} ({source.source_type.value})")

    async def run(self) -> IngestionMetrics:
        """Run ingestion pipeline"""
        run_id = hashlib.sha256(str(time.time()).encode()).hexdigest()[:16]
        self.metrics = IngestionMetrics(
            run_id=run_id,
            started_at=datetime.now()
        )

        logger.info(f"Starting ingestion run {run_id}")

        # Process each source
        for source in self.sources:
            if not source.enabled:
                continue

            # Check if source needs crawling
            if source.last_crawled:
                hours_since = (datetime.now() - source.last_crawled).total_seconds() / 3600
                if hours_since < source.crawl_frequency_hours:
                    logger.info(f"Skipping {source.source_id}: crawled {hours_since:.1f}h ago")
                    continue

            try:
                await self._process_source(source)
                self.metrics.sources_crawled += 1
            except Exception as e:
                logger.error(f"Error processing {source.source_id}: {e}")
                self.metrics.sources_failed += 1

        # Finalize metrics
        self.metrics.completed_at = datetime.now()
        self.metrics.runtime_seconds = (
            self.metrics.completed_at - self.metrics.started_at
        ).total_seconds()

        self._calculate_metrics()

        logger.info(f"Ingestion run {run_id} complete: {self.metrics.total_items_ingested} items in {self.metrics.runtime_seconds:.1f}s")

        return self.metrics

    async def _process_source(self, source: SourceConfig):
        """Process a single data source"""
        logger.info(f"Processing source: {source.source_id}")

        # Fetch content (mock for now)
        if source.source_type == SourceType.V2X_MESH:
            items = await self._fetch_v2x_mesh_data(source)
        else:
            items = await self._fetch_web_source(source)

        # Process each item
        for item_data in items:
            item = await self._process_item(item_data, source)
            if item:
                self.ingested_items.append(item)
                self.metrics.total_items_ingested += 1

                # Update tier counts
                self.metrics.items_by_tier[item.tier] += 1

                # Update source counts
                if source.source_id not in self.metrics.items_by_source:
                    self.metrics.items_by_source[source.source_id] = 0
                self.metrics.items_by_source[source.source_id] += 1

        # Update last crawled
        source.last_crawled = datetime.now()

    async def _fetch_web_source(self, source: SourceConfig) -> list[dict]:
        """Fetch items from web source"""
        content = await self.crawler.fetch(source.url, source.custom_headers)

        if not content:
            return []

        # Mock parsing - in production, use proper parsers
        return [
            {
                "title": f"Item from {source.source_id}",
                "content": content[:200],
                "url": source.url,
                "published_at": datetime.now() - timedelta(hours=2)
            }
        ]

    async def _fetch_v2x_mesh_data(self, source: SourceConfig) -> list[dict]:
        """Fetch data from V2X mesh integration"""
        # Integration with V2X mesh service
        # In production, this queries the V2X mesh API

        logger.info("Fetching V2X mesh data...")
        await asyncio.sleep(0.1)

        return [
            {
                "title": "V2X Traffic Event: Hard Brake Detected",
                "content": "Emergency braking event at intersection, 15 vehicles affected",
                "url": f"{source.url}/events/123",
                "published_at": datetime.now() - timedelta(minutes=30),
                "metadata": {
                    "severity": 8,
                    "affected_radius_m": 500,
                    "event_type": "hard_brake"
                }
            }
        ]

    async def _process_item(
        self,
        item_data: dict,
        source: SourceConfig
    ) -> IngestedItem | None:
        """Process individual item"""
        # Analyze with Gemini
        analysis = await self.analyzer.analyze_content(
            title=item_data["title"],
            content=item_data["content"],
            source_type=source.source_type
        )

        # Create item
        item = IngestedItem(
            item_id=hashlib.sha256(
                (item_data["url"] + str(item_data["published_at"])).encode()
            ).hexdigest()[:16],
            source_id=source.source_id,
            source_type=source.source_type,
            tier=source.tier,  # Initial tier from source
            title=item_data["title"],
            content=item_data["content"],
            url=item_data["url"],
            published_at=item_data["published_at"],
            ingested_at=datetime.now(),
            relevance_score=analysis["relevance_score"],
            relevance_categories=[
                RelevanceCategory(c) for c in analysis["categories"]
            ],
            metadata=item_data.get("metadata", {}),
            cost_cents=analysis["cost_cents"],
            gemini_analysis=analysis
        )

        # Reclassify tier based on analysis
        item.tier = self.classifier.classify(item)

        return item

    def _calculate_metrics(self):
        """Calculate final metrics"""
        if not self.ingested_items:
            return

        # Average relevance
        self.metrics.avg_relevance_score = sum(
            i.relevance_score for i in self.ingested_items
        ) / len(self.ingested_items)

        # Timeliness (% items <24hrs old)
        recent = sum(
            1 for i in self.ingested_items
            if (datetime.now() - i.published_at).total_seconds() < 86400
        )
        self.metrics.timeliness_score = recent / len(self.ingested_items)

        # Completeness (% with metadata)
        complete = sum(
            1 for i in self.ingested_items
            if i.metadata and len(i.metadata) >= 3
        )
        self.metrics.completeness_score = complete / len(self.ingested_items)

        # Costs
        self.metrics.total_cost_dollars = sum(
            i.cost_cents for i in self.ingested_items
        ) / 100.0
        self.metrics.cost_per_item_cents = (
            self.metrics.total_cost_dollars * 100
        ) / len(self.ingested_items)

    def get_am_briefing(self) -> dict[str, Any]:
        """Generate AM briefing from ingested data"""
        if not self.metrics or not self.ingested_items:
            return {"status": "No data"}

        # Get Tier 1 items
        tier1_items = [i for i in self.ingested_items if i.tier == DataTier.TIER_1]

        # Group by category
        by_category = {}
        for item in tier1_items:
            for cat in item.relevance_categories:
                if cat not in by_category:
                    by_category[cat] = []
                by_category[cat].append(item)

        briefing = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "summary": {
                "total_items": self.metrics.total_items_ingested,
                "tier1_items": len(tier1_items),
                "avg_relevance": f"{self.metrics.avg_relevance_score:.2f}",
                "sources_used": self.metrics.sources_crawled,
                "runtime_minutes": f"{self.metrics.runtime_seconds / 60:.1f}"
            },
            "highlights": [],
            "by_category": {}
        }

        # Top 5 highlights
        sorted_items = sorted(
            tier1_items,
            key=lambda x: x.relevance_score,
            reverse=True
        )[:5]

        for item in sorted_items:
            briefing["highlights"].append({
                "title": item.title,
                "category": item.relevance_categories[0].value if item.relevance_categories else "other",
                "relevance": f"{item.relevance_score:.2f}",
                "url": item.url
            })

        # Category breakdown
        for cat, items in by_category.items():
            briefing["by_category"][cat.value] = {
                "count": len(items),
                "top_item": items[0].title if items else None
            }

        return briefing


# Example usage
if __name__ == "__main__":
    async def main():
        # Configure ethical crawling
        crawler_config = EthicalCrawlingConfig(
            rate_limit_requests_per_minute=60,
            avoid_peak_hours=False  # For testing
        )

        # Create pipeline
        pipeline = IngestionPipeline(
            crawler_config=crawler_config,
            gemini_api_key="mock-api-key"
        )

        # Add sources
        pipeline.add_source(SourceConfig(
            source_id="v2x-mesh-prod",
            source_type=SourceType.V2X_MESH,
            url="http://v2x-mesh-gateway/v1/events",
            tier=DataTier.TIER_1,
            relevance_categories=[RelevanceCategory.TRAFFIC, RelevanceCategory.SAFETY]
        ))

        pipeline.add_source(SourceConfig(
            source_id="traffic-news-rss",
            source_type=SourceType.RSS,
            url="https://example.com/traffic-news/rss",
            tier=DataTier.TIER_2,
            relevance_categories=[RelevanceCategory.TRAFFIC]
        ))

        # Run ingestion
        metrics = await pipeline.run()

        print("\n=== Ingestion Metrics ===")
        print(f"Runtime: {metrics.runtime_seconds:.1f}s")
        print(f"Items: {metrics.total_items_ingested}")
        print(f"  Tier 1: {metrics.items_by_tier[DataTier.TIER_1]}")
        print(f"  Tier 2: {metrics.items_by_tier[DataTier.TIER_2]}")
        print(f"  Tier 3: {metrics.items_by_tier[DataTier.TIER_3]}")
        print(f"Avg Relevance: {metrics.avg_relevance_score:.2f}")
        print(f"Cost: ${metrics.total_cost_dollars:.2f} (${metrics.cost_per_item_cents:.4f}/item)")

        # Generate AM briefing
        briefing = pipeline.get_am_briefing()
        print("\n=== AM Briefing ===")
        print(json.dumps(briefing, indent=2))

    asyncio.run(main())
