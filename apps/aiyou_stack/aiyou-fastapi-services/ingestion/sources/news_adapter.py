"""PNKLN Core Stack - News/RSS Source Adapter

Fetches news articles from RSS feeds and news APIs.
Supports major tech and business news sources.

When GEMINI_API_KEY is set and an RSS entry has only a short summary
(<300 chars), Scrapegraph-ai SmartScraperGraph fetches the full article
body from the entry URL. Falls back to the RSS summary otherwise.
"""

import contextlib
import os
import sys
from collections.abc import AsyncIterator
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime
from pathlib import Path

import feedparser
import structlog
from bs4 import BeautifulSoup

from ingestion.classification.tier_classifier import IngestedItem
from ingestion.core.config import get_config
from ingestion.ethics.crawler import EthicalCrawler
from ingestion.sources.base import SourceAdapter

# Scrapegraph-ai submodule — full article body enrichment
_SCRAPEGRAPH_PATH = Path(__file__).parents[6] / "tools/external_sdks/scrapegraph-ai"
if _SCRAPEGRAPH_PATH.exists() and str(_SCRAPEGRAPH_PATH) not in sys.path:
    sys.path.insert(0, str(_SCRAPEGRAPH_PATH))

try:
    from scrapegraphai.graphs import SmartScraperGraph

    _HAS_SCRAPEGRAPH = True
except ImportError:
    _HAS_SCRAPEGRAPH = False

_FULL_BODY_THRESHOLD = 300  # chars — only enrich if RSS body is shorter than this

logger = structlog.get_logger(__name__)


class NewsAdapter(SourceAdapter):
    """News/RSS feed adapter for ingesting news articles.

    Fetches from:
    - RSS/Atom feeds from major news sources
    - Tech news sites (TechCrunch, Ars Technica, Wired, etc.)
    - Business news (Bloomberg, Reuters, WSJ)

    Uses ethical crawler for respecting robots.txt and rate limiting.

    Cost: ~$0.002 per article (minimal API costs)
    """

    # Curated list of high-quality news sources
    DEFAULT_FEEDS = [
        # Tech News
        "https://techcrunch.com/feed/",
        "https://arstechnica.com/feed/",
        "https://www.wired.com/feed/rss",
        "https://www.theverge.com/rss/index.xml",
        "https://venturebeat.com/feed/",
        # AI/ML Specific
        "https://ai.googleblog.com/feeds/posts/default",
        "https://openai.com/blog/rss/",
        "https://blog.anthropic.com/rss/",
        # Business/Finance
        "https://www.reuters.com/technology",
        "https://www.bloomberg.com/feed/technology",
        # Security
        "https://krebsonsecurity.com/feed/",
        "https://feeds.feedburner.com/TheHackersNews",
        # Major News Networks (free RSS)
        "http://rss.cnn.com/rss/cnn_tech.rss",
        "https://feeds.bbci.co.uk/news/technology/rss.xml",
        "https://feeds.apnews.com/apnews/technology",
        "https://feeds.apnews.com/apnews/business",
        "https://feeds.apnews.com/apnews/science",
        # Google News Topics (free RSS — no key)
        "https://news.google.com/rss/search?q=artificial+intelligence&hl=en-US&gl=US&ceid=US:en",
        "https://news.google.com/rss/search?q=machine+learning+LLM&hl=en-US&gl=US&ceid=US:en",
        "https://news.google.com/rss/search?q=AI+startup+funding&hl=en-US&gl=US&ceid=US:en",
        "https://news.google.com/rss/search?q=cybersecurity+breach&hl=en-US&gl=US&ceid=US:en",
        # Science / Research
        "https://www.sciencedaily.com/rss/computers_math/artificial_intelligence.xml",
        "https://www.nature.com/subjects/machine-learning.rss",
        # Finance / Markets
        "https://feeds.finance.yahoo.com/rss/2.0/headline?s=^GSPC&region=US&lang=en-US",
        "https://www.cnbc.com/id/10001147/device/rss/rss.html",
    ]

    def __init__(self):
        super().__init__("news")
        self.config = get_config()
        self.crawler = EthicalCrawler()
        self.feeds = self.DEFAULT_FEEDS
        self._use_enrichment = _HAS_SCRAPEGRAPH and bool(os.environ.get("GEMINI_API_KEY"))

    def _enrich_body(self, url: str) -> str:
        """Fetch full article body via Scrapegraph SmartScraperGraph."""
        try:
            graph = SmartScraperGraph(
                prompt="Extract the full article body as plain prose. Return only the article text.",
                source=url,
                config={
                    "llm": {"api_key": os.environ["GEMINI_API_KEY"], "model": "gemini-2.0-flash"},
                    "verbose": False,
                },
            )
            result = graph.run()
            if isinstance(result, dict):
                return " ".join(str(v) for v in result.values() if v)
            return str(result) if result else ""
        except Exception as e:
            logger.debug("news_enrich_failed", url=url, error=str(e))
            return ""

    async def validate_credentials(self) -> bool:
        """No credentials needed for RSS feeds."""
        logger.info("news_adapter_ready", feed_count=len(self.feeds))
        return True

    def get_cost_estimate(self, num_items: int) -> float:
        """Estimate cost for fetching news articles."""
        return num_items * self.config.ingestion.cost_per_news_item

    def add_feed(self, feed_url: str) -> None:
        """Add a custom RSS feed to the list."""
        if feed_url not in self.feeds:
            self.feeds.append(feed_url)
            logger.info("feed_added", url=feed_url)

    async def fetch_items(
        self, queries: list[str] | None = None, max_items: int = 1000, since: datetime | None = None,
    ) -> AsyncIterator[IngestedItem]:
        """Fetch news articles from RSS feeds.

        Args:
            queries: Topic filters (optional, used for filtering)
            max_items: Maximum articles to fetch
            since: Only fetch articles newer than this timestamp

        Yields:
            IngestedItem objects representing news articles

        """
        since = since or (datetime.utcnow() - timedelta(hours=24))
        items_fetched = 0

        for feed_url in self.feeds:
            if items_fetched >= max_items:
                break

            try:
                logger.info("news_feed_fetching", url=feed_url)

                # Fetch RSS feed using ethical crawler
                response = await self.crawler.fetch(feed_url)
                feed_content = response.text

                # Parse RSS feed
                feed = feedparser.parse(feed_content)

                for entry in feed.entries:
                    if items_fetched >= max_items:
                        break

                    try:
                        item = self._parse_entry(entry, feed_url)

                        # Filter by date
                        if item.published_at < since:
                            continue

                        # Filter by query keywords if provided
                        if queries:
                            if not self._matches_queries(item, queries):
                                continue

                        self._record_item_fetched(self.config.ingestion.cost_per_news_item)
                        items_fetched += 1
                        yield item

                    except Exception as e:
                        self._record_error()
                        logger.error(
                            "news_parse_error",
                            feed_url=feed_url,
                            entry_id=entry.get("id"),
                            error=str(e),
                        )

            except Exception as e:
                self._record_error()
                logger.error("news_feed_error", url=feed_url, error=str(e))

    def _parse_entry(self, entry: dict, feed_url: str) -> IngestedItem:
        """Parse RSS feed entry into IngestedItem."""
        # Parse published date
        published_at = None
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            published_at = datetime(*entry.published_parsed[:6])
        elif hasattr(entry, "published"):
            with contextlib.suppress(BaseException):
                published_at = parsedate_to_datetime(entry.published)

        if not published_at:
            published_at = datetime.utcnow()

        # Extract content
        content = None
        if hasattr(entry, "content") and entry.content:
            content = entry.content[0].value
        elif hasattr(entry, "summary"):
            content = entry.summary
        elif hasattr(entry, "description"):
            content = entry.description

        # Clean HTML from content
        if content:
            soup = BeautifulSoup(content, "lxml")
            content = soup.get_text().strip()

        # Enrich short summaries with full article body via Scrapegraph
        article_url = entry.get("link", feed_url)
        via = "rss"
        if self._use_enrichment and len(content or "") < _FULL_BODY_THRESHOLD and article_url:
            enriched = self._enrich_body(article_url)
            if len(enriched) > len(content or ""):
                content = enriched
                via = "scrapegraph"

        # Extract author
        author = entry.get("author") or entry.get("dc:creator") or feed_url

        # Build metadata
        metadata = {
            "feed_url": feed_url,
            "via": via,
            "tags": [tag.term for tag in entry.get("tags", [])],
            "categories": entry.get("categories", []),
            "media": [],
        }

        # Extract media/images
        if hasattr(entry, "media_content"):
            metadata["media"] = [m.get("url") for m in entry.media_content if m.get("url")]
        elif hasattr(entry, "links"):
            metadata["media"] = [
                link["href"] for link in entry.links if link.get("type", "").startswith("image/")
            ]

        return IngestedItem(
            id=f"news_{hash(entry.get('id', entry.get('link', '')))}",
            source="news",
            title=entry.get("title", "Untitled"),
            content=content,
            url=entry.get("link", feed_url),
            published_at=published_at,
            author=author,
            metadata=metadata,
        )

    def _matches_queries(self, item: IngestedItem, queries: list[str]) -> bool:
        """Check if item matches any of the query keywords."""
        search_text = f"{item.title} {item.content or ''}".lower()

        return any(query.lower() in search_text for query in queries)

    async def close(self) -> None:
        """Close crawler and cleanup."""
        await self.crawler.close()
        await super().close()
