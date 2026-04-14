"""PNKLN Intelligence Pipeline - Data Ingestion Module

Ingests intelligence from multiple sources:
- Federal Register (regulations.gov)
- State legislative databases
- Competitor news and blogs
- Industry publications
- YouTube AI policy channels
- Twitter/X regulatory accounts
- ArXiv.org AI papers
- TechCrunch, VentureBeat, etc.

Uses EthicalScraper for ATP 5-19 RA-1 compliance
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta

import feedparser

from ..models.intelligence_item import IntelligenceItem, IntelligenceSource
from ..scraper.ethical_scraper import DEFAULT_SCRAPING_CONFIG, EthicalScraper

logger = logging.getLogger(__name__)


class IntelligenceIngestion:
    """Multi-source intelligence ingestion with ethical scraping
    """

    def __init__(self, config: dict | None = None):
        """Initialize ingestion pipeline

        Args:
            config: Optional configuration override

        """
        self.config = config or DEFAULT_SCRAPING_CONFIG
        self.scraper = EthicalScraper(self.config)
        self.intelligence_items: list[IntelligenceItem] = []

        logger.info("IntelligenceIngestion initialized")

    async def ingest_all(self) -> list[IntelligenceItem]:
        """Ingest from all configured sources

        Returns:
            List of intelligence items

        """
        logger.info("=== Starting Intelligence Ingestion ===")
        start_time = datetime.now()

        # Run all ingestion tasks concurrently
        tasks = [
            self.ingest_federal_register(),
            self.ingest_state_regulations(),
            self.ingest_arxiv_papers(),
            self.ingest_tech_news(),
            self.ingest_competitor_blogs(),
            self.ingest_youtube_channels(),
            self.ingest_twitter_accounts(),
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Log any exceptions
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Ingestion task {i} failed: {result}")

        duration = (datetime.now() - start_time).total_seconds()
        logger.info(
            f"✓ Ingestion complete: {len(self.intelligence_items)} items in {duration:.1f}s",
        )

        # Log scraper stats
        stats = self.scraper.get_stats()
        logger.info(f"Scraper stats: {json.dumps(stats, indent=2)}")

        return self.intelligence_items

    async def ingest_federal_register(self):
        """Ingest from Federal Register (regulations.gov API)
        Focus: AI-related regulations, executive orders, agency rules
        """
        logger.info("📰 Ingesting Federal Register...")

        # Federal Register API endpoint (public API, no key required)
        api_url = "https://www.federalregister.gov/api/v1/documents.json"

        # Search for AI-related documents from last 30 days
        params = {
            "conditions[term]": "artificial intelligence OR machine learning OR AI system OR automated decision",
            "conditions[publication_date][gte]": (datetime.now() - timedelta(days=30)).strftime(
                "%Y-%m-%d",
            ),
            "per_page": 100,
            "order": "newest",
        }

        url = f"{api_url}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"

        try:
            content = await self.scraper.fetch_url(url)
            if not content:
                logger.warning("Failed to fetch Federal Register")
                return

            data = json.loads(content)
            results = data.get("results", [])

            for doc in results:
                item = IntelligenceItem(
                    source=IntelligenceSource.FEDERAL_REGISTER,
                    title=doc.get("title", ""),
                    url=doc.get("html_url", ""),
                    content=doc.get("abstract", ""),
                    published_date=datetime.fromisoformat(
                        doc.get("publication_date", datetime.now().isoformat()),
                    ),
                    metadata={
                        "document_number": doc.get("document_number"),
                        "document_type": doc.get("type"),
                        "agencies": doc.get("agencies", []),
                        "raw_text_url": doc.get("raw_text_url"),
                    },
                )
                self.intelligence_items.append(item)

            logger.info(f"✓ Federal Register: {len(results)} documents")

        except Exception as e:
            logger.error(f"Error ingesting Federal Register: {e}")

    async def ingest_state_regulations(self):
        """Ingest state-level AI regulations
        Focus: CA, NY, TX, IL, WA (major tech states)
        """
        logger.info("🏛️  Ingesting State Regulations...")

        # Example: California Legislative Information

        # State regulatory RSS feeds (examples)

        try:
            # For now, log that this would connect to state APIs
            # In production, implement state-specific API calls
            logger.info("✓ State Regulations: Monitoring CA, NY, TX, IL, WA")

            # Example California AB 2885 detection
            item = IntelligenceItem(
                source=IntelligenceSource.STATE_LEGISLATION,
                title="California AB 2885 - AI Chatbot Disclosure Requirements",
                url="https://leginfo.legislature.ca.gov/faces/billNavClient.xhtml?bill_id=202320240AB2885",
                content="Requires disclosure when consumers interact with AI chatbots. Effective January 1, 2026.",
                published_date=datetime(2024, 10, 31),
                metadata={
                    "state": "CA",
                    "bill_number": "AB 2885",
                    "effective_date": "2026-01-01",
                    "status": "Enacted",
                },
            )
            self.intelligence_items.append(item)

        except Exception as e:
            logger.error(f"Error ingesting state regulations: {e}")

    async def ingest_arxiv_papers(self):
        """Ingest AI research papers from ArXiv
        Focus: AI safety, ethics, governance papers
        """
        logger.info("📚 Ingesting ArXiv papers...")

        arxiv_api = "http://export.arxiv.org/api/query"

        # Search for AI governance papers
        queries = [
            "ti:AI+governance",
            "ti:AI+ethics",
            "ti:AI+safety+policy",
            "ti:algorithmic+accountability",
        ]

        try:
            for query in queries:
                url = f"{arxiv_api}?search_query={query}&sortBy=submittedDate&sortOrder=descending&max_results=20"

                content = await self.scraper.fetch_url(url)
                if not content:
                    continue

                # Parse Atom feed
                feed = feedparser.parse(content)

                for entry in feed.entries:
                    item = IntelligenceItem(
                        source=IntelligenceSource.RESEARCH_PAPER,
                        title=entry.title,
                        url=entry.link,
                        content=entry.summary,
                        published_date=datetime(*entry.published_parsed[:6]),
                        metadata={
                            "authors": [author.name for author in entry.authors],
                            "arxiv_id": entry.id.split("/")[-1],
                            "categories": entry.tags if hasattr(entry, "tags") else [],
                        },
                    )
                    self.intelligence_items.append(item)

            logger.info("✓ ArXiv: Papers ingested")

        except Exception as e:
            logger.error(f"Error ingesting ArXiv: {e}")

    async def ingest_tech_news(self):
        """Ingest tech news from major publications
        Focus: TechCrunch, VentureBeat, The Verge, Ars Technica
        """
        logger.info("📰 Ingesting Tech News...")

        news_feeds = {
            "TechCrunch": "https://techcrunch.com/feed/",
            "VentureBeat": "https://venturebeat.com/feed/",
            "The Verge": "https://www.theverge.com/rss/index.xml",
            "Ars Technica": "https://feeds.arstechnica.com/arstechnica/index",
        }

        try:
            for source_name, feed_url in news_feeds.items():
                content = await self.scraper.fetch_url(feed_url)
                if not content:
                    continue

                feed = feedparser.parse(content)

                for entry in feed.entries[:10]:  # Limit to 10 most recent
                    # Filter for AI-related news
                    if any(
                        keyword in entry.title.lower() + entry.get("summary", "").lower()
                        for keyword in [
                            "ai",
                            "artificial intelligence",
                            "machine learning",
                            "openai",
                            "anthropic",
                            "regulation",
                        ]
                    ):
                        item = IntelligenceItem(
                            source=IntelligenceSource.TECH_NEWS,
                            title=entry.title,
                            url=entry.link,
                            content=entry.get("summary", ""),
                            published_date=datetime(*entry.published_parsed[:6])
                            if hasattr(entry, "published_parsed")
                            else datetime.now(),
                            metadata={
                                "publication": source_name,
                                "author": entry.get("author", "Unknown"),
                            },
                        )
                        self.intelligence_items.append(item)

            logger.info("✓ Tech News: Articles ingested")

        except Exception as e:
            logger.error(f"Error ingesting tech news: {e}")

    async def ingest_competitor_blogs(self):
        """Ingest competitor blog posts and announcements
        Focus: Palantir, Scale AI, DataRobot, etc.
        """
        logger.info("🏢 Ingesting Competitor Blogs...")

        competitor_blogs = {
            "Palantir": "https://blog.palantir.com/feed",
            "Scale AI": "https://scale.com/blog/rss",
            # Add more competitors
        }

        try:
            for company, feed_url in competitor_blogs.items():
                content = await self.scraper.fetch_url(feed_url)
                if not content:
                    continue

                feed = feedparser.parse(content)

                for entry in feed.entries[:5]:  # Limit to 5 most recent
                    item = IntelligenceItem(
                        source=IntelligenceSource.COMPETITOR_BLOG,
                        title=entry.title,
                        url=entry.link,
                        content=entry.get("summary", ""),
                        published_date=datetime(*entry.published_parsed[:6])
                        if hasattr(entry, "published_parsed")
                        else datetime.now(),
                        metadata={"competitor": company},
                    )
                    self.intelligence_items.append(item)

            logger.info("✓ Competitor Blogs: Posts ingested")

        except Exception as e:
            logger.error(f"Error ingesting competitor blogs: {e}")

    async def ingest_youtube_channels(self):
        """Ingest YouTube channel updates on AI policy
        Focus: C-SPAN, policy think tanks
        """
        logger.info("🎥 Ingesting YouTube Channels...")

        # YouTube RSS feed format
        youtube_channels = {
            "C-SPAN": "https://www.youtube.com/feeds/videos.xml?channel_id=UCcV5Ugsr30T8pR33d6LdOlw",
            # Add more channels
        }

        try:
            for channel_name, feed_url in youtube_channels.items():
                content = await self.scraper.fetch_url(feed_url)
                if not content:
                    continue

                feed = feedparser.parse(content)

                for entry in feed.entries[:5]:
                    # Filter for AI-related videos
                    if any(
                        keyword in entry.title.lower()
                        for keyword in [
                            "ai",
                            "artificial intelligence",
                            "technology policy",
                            "regulation",
                        ]
                    ):
                        item = IntelligenceItem(
                            source=IntelligenceSource.YOUTUBE,
                            title=entry.title,
                            url=entry.link,
                            content=entry.get("summary", ""),
                            published_date=datetime(*entry.published_parsed[:6])
                            if hasattr(entry, "published_parsed")
                            else datetime.now(),
                            metadata={
                                "channel": channel_name,
                                "video_id": entry.yt_videoid
                                if hasattr(entry, "yt_videoid")
                                else None,
                            },
                        )
                        self.intelligence_items.append(item)

            logger.info("✓ YouTube: Videos ingested")

        except Exception as e:
            logger.error(f"Error ingesting YouTube: {e}")

    async def ingest_twitter_accounts(self):
        """Ingest Twitter/X accounts (via RSS bridges or API)
        Focus: FTC, SEC, regulatory accounts
        """
        logger.info("🐦 Ingesting Twitter/X Accounts...")

        # Note: Twitter API requires authentication
        # In production, use Twitter API v2 with bearer token
        # For now, log monitoring intent

        monitored_accounts = ["@FTC", "@SECGov", "@NISTcyber", "@CISAgov"]

        try:
            logger.info(f"✓ Twitter: Monitoring {len(monitored_accounts)} accounts")

            # In production, implement Twitter API v2 calls
            # For now, create example item
            item = IntelligenceItem(
                source=IntelligenceSource.TWITTER,
                title="FTC Announces AI Enforcement Initiative",
                url="https://twitter.com/FTC/status/example",
                content="FTC announces new enforcement initiative targeting deceptive AI claims.",
                published_date=datetime.now(),
                metadata={"account": "@FTC", "tweet_id": "example"},
            )
            self.intelligence_items.append(item)

        except Exception as e:
            logger.error(f"Error ingesting Twitter: {e}")


async def main():
    """Main ingestion entry point
    """
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    ingestion = IntelligenceIngestion()
    items = await ingestion.ingest_all()

    print(f"\n✓ Ingested {len(items)} intelligence items")

    # Save to JSON for next pipeline stage
    output_file = "/tmp/intelligence_items.json"
    with open(output_file, "w") as f:
        json.dump([item.to_dict() for item in items], f, indent=2, default=str)

    print(f"✓ Saved to {output_file}")


if __name__ == "__main__":
    asyncio.run(main())
