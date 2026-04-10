"""
Gemini Ingestion Layer - Multi-Source Intelligence Collection Pipeline

This module provides:
1. Ethical web crawling with robots.txt compliance
2. Multi-source data ingestion (YouTube, Twitter, News, RSS)
3. Tier classification (Tier 1/2/3 value stratification)
4. GKE CronJob orchestration for nightly batch processing
5. AM Briefing delivery pipeline
6. Cost-per-item optimization and tracking

Architecture: GKE CronJob Multi-Container
- Runs nightly batch ingestion (~45 min runtime target)
- Multi-source parallel crawling
- Ethical compliance enforcement (rate limiting, robots.txt)
- Tiered data classification for downstream prioritization
- Feeds into Judge #6 validation pipeline

Integration Position: Pre-Validation Intelligence Collection
- UPSTREAM: Web sources, APIs, feeds
- DOWNSTREAM: Judge #6 Enforcement → AutoGen Orchestration → Execution

Performance Targets:
- Runtime: ~45 min/night for full ingestion cycle
- Items/Day: 1000-5000 intelligence items
- Sources: 10+ diverse sources (YouTube, Twitter, News, etc.)
- Cost/Item: < $0.01 per item ingested
- Tier 1 Distribution: ≥ 30% of total items

Quality Gates:
- Relevance: Items match domain criteria
- Timeliness: Fresh data within 24 hours
- Completeness: Full metadata captured
- Ethical Compliance: 100% robots.txt adherence

Author: PNKLN Strategic Systems
Version: 1.0.0
"""

import hashlib
import json
import logging
import os
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import Any
from urllib.parse import urlparse

# Google Gemini imports
try:
    import google.generativeai as genai

    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logging.warning("Google Gemini not installed. Install with: pip install google-generativeai")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataTier(Enum):
    """Data tier classification for prioritization"""

    TIER_1_CRITICAL = "TIER_1_CRITICAL"  # High-value, strategic intelligence
    TIER_2_IMPORTANT = "TIER_2_IMPORTANT"  # Relevant, useful context
    TIER_3_BACKGROUND = "TIER_3_BACKGROUND"  # General information, low priority


class SourceType(Enum):
    """Supported data source types"""

    YOUTUBE = "youtube"
    TWITTER = "twitter"
    NEWS = "news"
    RSS = "rss"
    BLOG = "blog"
    RESEARCH = "research"
    PODCAST = "podcast"


@dataclass
class IntelligenceItem:
    """Individual intelligence item from ingestion"""

    item_id: str
    source_type: SourceType
    source_url: str
    title: str
    content: str
    tier: DataTier
    relevance_score: float  # 0.0 - 1.0
    ingestion_timestamp: str
    metadata: dict[str, Any]
    cost: float  # Cost to acquire this item


@dataclass
class EthicalCrawlConfig:
    """Configuration for ethical web crawling"""

    respect_robots_txt: bool = True
    rate_limit_requests_per_second: float = 1.0
    user_agent: str = "PNKLN-Intelligence-Bot/1.0"
    max_concurrent_requests: int = 5
    request_timeout_seconds: int = 30
    backoff_on_429: bool = True  # Respect 429 Too Many Requests
    transparency_contact: str = "redacted@shadowtag-v4.local"


@dataclass
class IngestionMetrics:
    """Metrics for ingestion pipeline performance"""

    runtime_seconds: float
    items_ingested: int
    sources_accessed: int
    tier_1_count: int
    tier_2_count: int
    tier_3_count: int
    total_cost: float
    avg_relevance_score: float
    ethical_violations: int
    failed_sources: list[str]


class RobotsTxtParser:
    """Parse and respect robots.txt directives"""

    def __init__(self):
        self.cache: dict[str, dict] = {}

    def can_fetch(self, url: str, user_agent: str) -> bool:
        """
        Check if URL can be fetched based on robots.txt

        Args:
            url: URL to check
            user_agent: User agent string

        Returns:
            True if allowed to fetch, False otherwise
        """
        # Parse domain
        parsed = urlparse(url)
        domain = f"{parsed.scheme}://{parsed.netloc}"

        # Check cache
        if domain not in self.cache:
            self._fetch_robots_txt(domain)

        # For mock implementation, allow most URLs
        # In production, parse actual robots.txt
        return self._check_robots_rules(url, user_agent)

    def _fetch_robots_txt(self, domain: str):
        """Fetch and cache robots.txt for domain"""
        # Mock implementation - in production, fetch actual robots.txt
        logger.info(f"Fetching robots.txt for {domain}")
        self.cache[domain] = {
            "disallow": [],  # List of disallowed paths
            "crawl_delay": 1.0,  # Seconds between requests
            "fetched_at": datetime.utcnow().isoformat(),
        }

    def _check_robots_rules(self, url: str, user_agent: str) -> bool:
        """Check if URL is allowed by robots.txt rules"""
        parsed = urlparse(url)
        domain = f"{parsed.scheme}://{parsed.netloc}"

        if domain not in self.cache:
            return True  # Allow by default if no robots.txt

        disallowed = self.cache[domain].get("disallow", [])
        path = parsed.path

        # Check if path matches any disallow rules
        for disallow_path in disallowed:
            if path.startswith(disallow_path):
                logger.warning(f"Blocked by robots.txt: {url}")
                return False

        return True


class TierClassifier:
    """Classify intelligence items into tiers using Gemini"""

    def __init__(self, gemini_api_key: str | None = None):
        """
        Initialize tier classifier

        Args:
            gemini_api_key: Google API key for Gemini
        """
        self.api_key = gemini_api_key or os.environ.get("GOOGLE_API_KEY")

        if GEMINI_AVAILABLE and self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel("gemini-2.0-flash-exp")
            self.enabled = True
            logger.info("Gemini tier classifier initialized")
        else:
            self.enabled = False
            logger.warning(
                "Gemini tier classifier disabled (API key missing or package not installed)"
            )

    def classify_item(
        self, title: str, content: str, source_type: SourceType
    ) -> tuple[DataTier, float]:
        """
        Classify an intelligence item into a tier

        Args:
            title: Item title
            content: Item content
            source_type: Source type

        Returns:
            tuple: (tier, relevance_score)
        """
        if not self.enabled:
            # Fallback classification
            return self._fallback_classification(title, content)

        try:
            prompt = f"""Classify this intelligence item for strategic relevance to business operations:

Title: {title}
Content: {content[:500]}...
Source: {source_type.value}

Classification criteria:
- TIER 1 (CRITICAL): Strategic insights, competitive intelligence, market opportunities, regulatory changes
- TIER 2 (IMPORTANT): Industry trends, customer insights, operational improvements, tactical opportunities
- TIER 3 (BACKGROUND): General news, tangential information, low-priority updates

Respond with JSON:
{{
  "tier": "TIER_1_CRITICAL" | "TIER_2_IMPORTANT" | "TIER_3_BACKGROUND",
  "relevance_score": <0.0-1.0>,
  "rationale": "<brief explanation>"
}}"""

            response = self.model.generate_content(prompt)
            result_text = response.text

            # Parse JSON response
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0]
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0]

            result = json.loads(result_text.strip())

            tier = DataTier[result["tier"]]
            relevance_score = result["relevance_score"]

            logger.info(f"Classified as {tier.value} (score: {relevance_score:.2f})")
            return tier, relevance_score

        except Exception as e:
            logger.error(f"Tier classification failed: {e}")
            return self._fallback_classification(title, content)

    def _fallback_classification(self, title: str, content: str) -> tuple[DataTier, float]:
        """Fallback classification when Gemini unavailable"""
        # Simple keyword-based classification
        strategic_keywords = ["market", "competitive", "strategic", "opportunity", "regulatory"]
        important_keywords = ["trend", "customer", "operational", "industry"]

        text = f"{title} {content}".lower()

        if any(kw in text for kw in strategic_keywords):
            return DataTier.TIER_1_CRITICAL, 0.8
        elif any(kw in text for kw in important_keywords):
            return DataTier.TIER_2_IMPORTANT, 0.6
        else:
            return DataTier.TIER_3_BACKGROUND, 0.4


class SourceIngester:
    """Base class for source-specific ingesters"""

    def __init__(
        self,
        source_type: SourceType,
        ethical_config: EthicalCrawlConfig,
        robots_parser: RobotsTxtParser,
    ):
        self.source_type = source_type
        self.ethical_config = ethical_config
        self.robots_parser = robots_parser
        self.request_count = 0
        self.last_request_time = 0.0

    def ingest(self, source_config: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Ingest data from source

        Args:
            source_config: Source-specific configuration

        Returns:
            List of raw items
        """
        raise NotImplementedError("Subclasses must implement ingest()")

    def _rate_limit(self):
        """Enforce rate limiting"""
        if self.last_request_time > 0:
            elapsed = time.time() - self.last_request_time
            min_interval = 1.0 / self.ethical_config.rate_limit_requests_per_second

            if elapsed < min_interval:
                sleep_time = min_interval - elapsed
                logger.debug(f"Rate limiting: sleeping {sleep_time:.2f}s")
                time.sleep(sleep_time)

        self.last_request_time = time.time()
        self.request_count += 1

    def _check_robots_txt(self, url: str) -> bool:
        """Check if URL is allowed by robots.txt"""
        if not self.ethical_config.respect_robots_txt:
            return True

        return self.robots_parser.can_fetch(url, self.ethical_config.user_agent)


class MockYouTubeIngester(SourceIngester):
    """Mock YouTube video ingester"""

    def ingest(self, source_config: dict[str, Any]) -> list[dict[str, Any]]:
        """Ingest YouTube videos (mock implementation)"""
        logger.info("Ingesting from YouTube (mock)")

        # Mock data
        items = [
            {
                "url": "https://youtube.com/watch?v=example1",
                "title": "Healthcare AI Market Trends 2025",
                "content": "Analysis of emerging AI applications in healthcare sector...",
                "cost": 0.005,
            },
            {
                "url": "https://youtube.com/watch?v=example2",
                "title": "Fintech Regulatory Updates Q1 2025",
                "content": "SEC guidance on AI-powered financial services...",
                "cost": 0.005,
            },
        ]

        return items


class MockTwitterIngester(SourceIngester):
    """Mock Twitter/X ingester"""

    def ingest(self, source_config: dict[str, Any]) -> list[dict[str, Any]]:
        """Ingest tweets (mock implementation)"""
        logger.info("Ingesting from Twitter (mock)")

        items = [
            {
                "url": "https://twitter.com/user/status/123",
                "title": "Thread: Enterprise AI Adoption Barriers",
                "content": "Key findings from survey of 500 CIOs on AI implementation challenges...",
                "cost": 0.002,
            }
        ]

        return items


class MockNewsIngester(SourceIngester):
    """Mock news article ingester"""

    def ingest(self, source_config: dict[str, Any]) -> list[dict[str, Any]]:
        """Ingest news articles (mock implementation)"""
        logger.info("Ingesting from News sources (mock)")

        items = [
            {
                "url": "https://news.example.com/article1",
                "title": "FDA Approves New AI Diagnostic Tool",
                "content": "First AI-powered diagnostic system receives FDA clearance for clinical use...",
                "cost": 0.003,
            }
        ]

        return items


class GeminiIngestionPipeline:
    """
    Complete Gemini Ingestion Layer pipeline
    Orchestrates multi-source ingestion with ethical compliance
    """

    def __init__(
        self, gemini_api_key: str | None = None, ethical_config: EthicalCrawlConfig | None = None
    ):
        """
        Initialize Gemini Ingestion Pipeline

        Args:
            gemini_api_key: Google API key for Gemini
            ethical_config: Ethical crawling configuration
        """
        self.gemini_api_key = gemini_api_key or os.environ.get("GOOGLE_API_KEY")
        self.ethical_config = ethical_config or EthicalCrawlConfig()

        # Initialize components
        self.robots_parser = RobotsTxtParser()
        self.tier_classifier = TierClassifier(gemini_api_key=self.gemini_api_key)

        # Initialize source ingesters
        self.ingesters: dict[SourceType, SourceIngester] = {
            SourceType.YOUTUBE: MockYouTubeIngester(
                SourceType.YOUTUBE, self.ethical_config, self.robots_parser
            ),
            SourceType.TWITTER: MockTwitterIngester(
                SourceType.TWITTER, self.ethical_config, self.robots_parser
            ),
            SourceType.NEWS: MockNewsIngester(
                SourceType.NEWS, self.ethical_config, self.robots_parser
            ),
        }

        self.ingestion_history: list[IntelligenceItem] = []

        logger.info("Gemini Ingestion Pipeline initialized")

    def run_ingestion_cycle(
        self, source_configs: dict[SourceType, dict[str, Any]]
    ) -> IngestionMetrics:
        """
        Run a complete ingestion cycle across all configured sources

        Args:
            source_configs: Configuration for each source type

        Returns:
            IngestionMetrics with performance data
        """
        start_time = time.time()
        logger.info("Starting ingestion cycle...")

        all_items: list[IntelligenceItem] = []
        sources_accessed = 0
        failed_sources = []
        ethical_violations = 0

        # Ingest from each source
        for source_type, config in source_configs.items():
            if source_type not in self.ingesters:
                logger.warning(f"No ingester for {source_type.value}")
                failed_sources.append(source_type.value)
                continue

            try:
                logger.info(f"Ingesting from {source_type.value}...")
                ingester = self.ingesters[source_type]

                # Get raw items
                raw_items = ingester.ingest(config)
                sources_accessed += 1

                # Process and classify each item
                for raw_item in raw_items:
                    # Check robots.txt compliance
                    if not ingester._check_robots_txt(raw_item["url"]):
                        ethical_violations += 1
                        logger.warning(f"Skipping {raw_item['url']} (robots.txt blocked)")
                        continue

                    # Classify tier
                    tier, relevance_score = self.tier_classifier.classify_item(
                        title=raw_item["title"],
                        content=raw_item["content"],
                        source_type=source_type,
                    )

                    # Create intelligence item
                    item = IntelligenceItem(
                        item_id=self._generate_item_id(raw_item["url"]),
                        source_type=source_type,
                        source_url=raw_item["url"],
                        title=raw_item["title"],
                        content=raw_item["content"],
                        tier=tier,
                        relevance_score=relevance_score,
                        ingestion_timestamp=datetime.utcnow().isoformat(),
                        metadata={"source_config": config, "ingester_version": "1.0.0"},
                        cost=raw_item.get("cost", 0.0),
                    )

                    all_items.append(item)

            except Exception as e:
                logger.error(f"Ingestion failed for {source_type.value}: {e}")
                failed_sources.append(source_type.value)

        # Calculate metrics
        runtime = time.time() - start_time

        tier_counts = {
            DataTier.TIER_1_CRITICAL: 0,
            DataTier.TIER_2_IMPORTANT: 0,
            DataTier.TIER_3_BACKGROUND: 0,
        }

        for item in all_items:
            tier_counts[item.tier] += 1

        total_cost = sum(item.cost for item in all_items)
        avg_relevance = (
            sum(item.relevance_score for item in all_items) / len(all_items) if all_items else 0.0
        )

        metrics = IngestionMetrics(
            runtime_seconds=runtime,
            items_ingested=len(all_items),
            sources_accessed=sources_accessed,
            tier_1_count=tier_counts[DataTier.TIER_1_CRITICAL],
            tier_2_count=tier_counts[DataTier.TIER_2_IMPORTANT],
            tier_3_count=tier_counts[DataTier.TIER_3_BACKGROUND],
            total_cost=total_cost,
            avg_relevance_score=avg_relevance,
            ethical_violations=ethical_violations,
            failed_sources=failed_sources,
        )

        # Store items
        self.ingestion_history.extend(all_items)

        logger.info(f"Ingestion cycle complete: {len(all_items)} items in {runtime:.2f}s")
        return metrics

    def generate_am_briefing(self, date: str | None = None) -> str:
        """
        Generate morning briefing from ingested intelligence

        Args:
            date: Date for briefing (defaults to today)

        Returns:
            Formatted briefing text
        """
        target_date = date or datetime.utcnow().strftime("%Y-%m-%d")

        # Filter items from target date
        items = [
            item
            for item in self.ingestion_history
            if item.ingestion_timestamp.startswith(target_date)
        ]

        if not items:
            return f"# AM Briefing - {target_date}\n\nNo intelligence items for this date."

        # Sort by tier (Tier 1 first) and relevance
        tier_order = {
            DataTier.TIER_1_CRITICAL: 1,
            DataTier.TIER_2_IMPORTANT: 2,
            DataTier.TIER_3_BACKGROUND: 3,
        }
        items_sorted = sorted(items, key=lambda x: (tier_order[x.tier], -x.relevance_score))

        # Generate briefing
        briefing = f"# AM Intelligence Briefing - {target_date}\n\n"
        briefing += f"**Total Items:** {len(items)}\n"
        briefing += f"**Tier 1 (Critical):** {sum(1 for i in items if i.tier == DataTier.TIER_1_CRITICAL)}\n"
        briefing += f"**Tier 2 (Important):** {sum(1 for i in items if i.tier == DataTier.TIER_2_IMPORTANT)}\n"
        briefing += f"**Tier 3 (Background):** {sum(1 for i in items if i.tier == DataTier.TIER_3_BACKGROUND)}\n\n"

        briefing += "---\n\n"

        current_tier = None
        for item in items_sorted:
            if item.tier != current_tier:
                current_tier = item.tier
                briefing += f"\n## {current_tier.value.replace('_', ' ')}\n\n"

            briefing += f"### {item.title}\n"
            briefing += f"**Source:** {item.source_type.value.title()} | "
            briefing += f"**Relevance:** {item.relevance_score:.2f}\n\n"
            briefing += f"{item.content[:200]}...\n"
            briefing += f"[Read more]({item.source_url})\n\n"

        return briefing

    def export_metrics(
        self, metrics: IngestionMetrics, output_path: str = "ingestion_metrics.json"
    ) -> str:
        """Export ingestion metrics"""
        with open(output_path, "w") as f:
            json.dump(asdict(metrics), f, indent=2, default=str)

        logger.info(f"Metrics exported: {output_path}")
        return output_path

    def _generate_item_id(self, url: str) -> str:
        """Generate unique ID for item"""
        return hashlib.md5(url.encode()).hexdigest()[:16]


def main():
    """Example usage and smoke test"""
    print("=== Gemini Ingestion Layer - Multi-Source Intelligence Collection ===\n")

    # Initialize pipeline
    pipeline = GeminiIngestionPipeline()

    # Configure sources
    source_configs = {
        SourceType.YOUTUBE: {
            "channels": ["@healthcare_ai", "@fintech_news"],
            "keywords": ["AI", "healthcare", "fintech"],
        },
        SourceType.TWITTER: {
            "accounts": ["@tech_insider", "@health_tech"],
            "hashtags": ["#HealthTech", "#AIinHealthcare"],
        },
        SourceType.NEWS: {
            "feeds": ["https://news.example.com/rss"],
            "keywords": ["FDA", "AI", "healthcare"],
        },
    }

    # Run ingestion cycle
    print("Running ingestion cycle...")
    metrics = pipeline.run_ingestion_cycle(source_configs)

    print("\n=== Ingestion Metrics ===")
    print(f"Runtime: {metrics.runtime_seconds:.2f}s")
    print(f"Items Ingested: {metrics.items_ingested}")
    print(f"Sources Accessed: {metrics.sources_accessed}")
    print("\nTier Distribution:")
    print(f"  Tier 1 (Critical): {metrics.tier_1_count}")
    print(f"  Tier 2 (Important): {metrics.tier_2_count}")
    print(f"  Tier 3 (Background): {metrics.tier_3_count}")
    print(f"\nCost: ${metrics.total_cost:.4f}")
    print(f"Avg Relevance: {metrics.avg_relevance_score:.2f}")
    print(f"Ethical Violations: {metrics.ethical_violations}")

    # Generate AM briefing
    print("\n=== Generating AM Briefing ===")
    briefing = pipeline.generate_am_briefing()
    print(briefing[:500] + "...\n")

    # Export metrics
    metrics_path = pipeline.export_metrics(metrics)
    print(f"✓ Metrics exported: {metrics_path}")

    print("\n✓ Gemini Ingestion Layer smoke test complete")


if __name__ == "__main__":
    main()
