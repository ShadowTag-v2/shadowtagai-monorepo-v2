"""Multi-source data collection manager.

Handles intelligence gathering from diverse sources:
- YouTube (videos, transcripts, comments)
- Twitter/X (tweets, threads, trends)
- News (RSS, APIs, web scraping)
- Reddit (posts, comments, subreddits)
- Academic (arXiv, papers, citations)
"""

import asyncio
import logging
import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)


class SourceType(Enum):
    """Types of data sources."""

    YOUTUBE = "youtube"
    TWITTER = "twitter"
    NEWS = "news"
    REDDIT = "reddit"
    ACADEMIC = "academic"
    WEB = "web"
    RSS = "rss"
    DRIVE = "drive"


@dataclass
class DataSource:
    """Configuration for a data source."""

    name: str
    source_type: SourceType
    url: str
    enabled: bool = True
    rate_limit: int = 60  # requests per minute
    priority: int = 1  # 1=highest, 3=lowest

    # Ethical settings
    respect_robots_txt: bool = True
    user_agent: str = "ShadowTag-v2-Ingestion/1.0 (Educational; +https://github.com/ShadowTag-v2)"

    # Quality settings
    min_quality_score: float = 0.5

    # Metadata
    last_crawl: datetime | None = None
    items_collected: int = 0
    errors: int = 0


class SourceManager:
    """Manages multiple data sources for intelligence collection.

    Features:
    - Multi-source coverage (YouTube, Twitter, News, etc.)
    - Rate limiting per source
    - Priority-based collection
    - Error tracking and retry logic
    """

    def __init__(
        self,
        sources: list[DataSource] = None,
        max_concurrent: int = 5,
    ):
        self.sources: dict[str, DataSource] = {}
        self.max_concurrent = max_concurrent
        self._semaphore = asyncio.Semaphore(max_concurrent)

        # Statistics
        self.total_items_collected = 0
        self.total_sources_crawled = 0
        self.errors_by_source: dict[str, int] = {}

        if sources:
            for source in sources:
                self.register_source(source)

    def register_source(self, source: DataSource):
        """Register a new data source."""
        self.sources[source.name] = source
        logger.info(f"Registered source: {source.name} ({source.source_type.value})")

    def get_source(self, name: str) -> DataSource | None:
        """Get a source by name."""
        return self.sources.get(name)

    def list_sources(
        self,
        source_type: SourceType | None = None,
        enabled_only: bool = True,
    ) -> list[DataSource]:
        """List sources, optionally filtered."""
        sources = list(self.sources.values())

        if source_type:
            sources = [s for s in sources if s.source_type == source_type]

        if enabled_only:
            sources = [s for s in sources if s.enabled]

        return sorted(sources, key=lambda s: s.priority)

    async def collect_from_source(
        self,
        source: DataSource,
        max_items: int = 100,
    ) -> list[dict]:
        """Collect data from a single source.

        Args:
            source: Data source to collect from
            max_items: Maximum items to collect

        Returns:
            List of collected items

        """
        async with self._semaphore:
            logger.info(f"Collecting from {source.name} (max={max_items})...")

            try:
                # Implement source-specific collection
                # This is a placeholder - actual implementation would call APIs
                items = await self._collect_items(source, max_items)

                # Update statistics
                source.last_crawl = datetime.now()
                source.items_collected += len(items)
                self.total_items_collected += len(items)

                logger.info(f"✓ Collected {len(items)} items from {source.name}")
                return items

            except Exception as e:
                source.errors += 1
                self.errors_by_source[source.name] = self.errors_by_source.get(source.name, 0) + 1
                logger.error(f"✗ Failed to collect from {source.name}: {e}")
                return []

    async def _collect_items(
        self,
        source: DataSource,
        max_items: int,
    ) -> list[dict]:
        """Source-specific collection logic."""
        # Handle Google Drive Extraction
        if source.source_type == SourceType.DRIVE:
            items = []
            try:
                # Path relative to project root (where script ran)
                file_path = Path("biz_plan_raw.txt")
                if not file_path.exists():
                    logger.warning(f"Drive extraction file not found: {file_path}")
                    return []

                content = file_path.read_text(encoding="utf-8", errors="ignore")

                # Parse delimited text
                # === SOURCE: Label / Filename ===
                pattern = re.compile(
                    r"=== SOURCE: (.*?) / (.*?) ===\n\n(.*?)(?=\n=== SOURCE:|\Z)",
                    re.DOTALL,
                )

                matches = pattern.findall(content)
                logger.info(f"Drive: Found {len(matches)} files in extraction.")

                for i, (label, filename, text) in enumerate(matches):
                    if i >= max_items:
                        break

                    items.append(
                        {
                            "id": f"drive_{filename}_{i}",
                            "source": f"Drive: {label}",
                            "type": "document",
                            "title": filename,
                            "content": text.strip(),
                            "timestamp": datetime.now().isoformat(),
                            "url": f"gdrive://{filename}",  # Pseudo-URI
                            "metadata": {"folder": label, "filename": filename},
                        },
                    )
                return items

            except Exception as e:
                logger.error(f"Error parsing Drive content: {e}")
                return []

        # Simulate collection for other sources
        await asyncio.sleep(0.1)

        # Mock items
        items = [
            {
                "id": f"{source.name}_{i}",
                "source": source.name,
                "type": source.source_type.value,
                "content": f"Mock content from {source.name}",
                "timestamp": datetime.now().isoformat(),
                "url": f"{source.url}/item/{i}",
            }
            for i in range(min(max_items, 10))  # Mock: return up to 10 items
        ]

        return items

    async def collect_all(
        self,
        max_items_per_source: int = 100,
        priority_only: bool = False,
    ) -> dict[str, list[dict]]:
        """Collect from all enabled sources.

        Args:
            max_items_per_source: Max items per source
            priority_only: Only collect from priority=1 sources

        Returns:
            Dictionary mapping source names to collected items

        """
        sources = self.list_sources(enabled_only=True)

        if priority_only:
            sources = [s for s in sources if s.priority == 1]

        logger.info(f"Collecting from {len(sources)} source(s)...")

        # Collect concurrently
        tasks = [self.collect_from_source(source, max_items_per_source) for source in sources]

        results = await asyncio.gather(*tasks)

        # Map results to source names
        collected = {source.name: items for source, items in zip(sources, results, strict=False)}

        self.total_sources_crawled = len([items for items in results if items])

        return collected

    def get_coverage_stats(self) -> dict:
        """Get multi-source coverage statistics."""
        by_type = {}
        for source in self.sources.values():
            source_type = source.source_type.value
            if source_type not in by_type:
                by_type[source_type] = {
                    "count": 0,
                    "enabled": 0,
                    "items_collected": 0,
                    "errors": 0,
                }

            by_type[source_type]["count"] += 1
            if source.enabled:
                by_type[source_type]["enabled"] += 1
            by_type[source_type]["items_collected"] += source.items_collected
            by_type[source_type]["errors"] += source.errors

        return {
            "total_sources": len(self.sources),
            "enabled_sources": len([s for s in self.sources.values() if s.enabled]),
            "total_items_collected": self.total_items_collected,
            "sources_crawled_today": self.total_sources_crawled,
            "coverage_by_type": by_type,
            "errors_by_source": dict(self.errors_by_source),
        }


# Default sources configuration
DEFAULT_SOURCES = [
    # YouTube sources
    DataSource(
        name="youtube-tech",
        source_type=SourceType.YOUTUBE,
        url="https://www.youtube.com",
        rate_limit=30,
        priority=1,
    ),
    # Twitter/X sources
    DataSource(
        name="twitter-ai",
        source_type=SourceType.TWITTER,
        url="https://api.twitter.com/2",
        rate_limit=100,
        priority=1,
    ),
    # News sources
    DataSource(
        name="hackernews",
        source_type=SourceType.NEWS,
        url="https://hacker-news.firebaseio.com/v0",
        rate_limit=60,
        priority=1,
    ),
    DataSource(
        name="techcrunch-rss",
        source_type=SourceType.RSS,
        url="https://techcrunch.com/feed/",
        rate_limit=10,
        priority=2,
    ),
    # Reddit sources
    DataSource(
        name="reddit-machinelearning",
        source_type=SourceType.REDDIT,
        url="https://www.reddit.com/r/MachineLearning",
        rate_limit=30,
        priority=2,
    ),
    # Academic sources
    DataSource(
        name="arxiv-cs-ai",
        source_type=SourceType.ACADEMIC,
        url="https://export.arxiv.org/api/query",
        rate_limit=10,
        priority=1,
    ),
    DataSource(
        name="google-drive-biz-plan",
        source_type=SourceType.DRIVE,
        url="file:///biz_plan_raw.txt",
        priority=1,
        respect_robots_txt=False,
    ),
]
