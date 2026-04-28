# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Industry & Manufacturer Blog Crawler
Discovers and ingests content from tech industry sources aligned with PNKLN verticals
"""

import asyncio
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import feedparser
import httpx
import structlog

from ..config import SCRAPING_ETHICS, STORAGE_CONFIG
from .ethical_scraper import EthicalScraper

logger = structlog.get_logger(__name__)


@dataclass
class IndustryArticle:
    """Represents a scraped industry article"""

    title: str
    url: str
    source: str
    published: datetime
    summary: str
    content: str | None = None
    vertical: str | None = None
    relevance_score: float = 0.5


# Industry source registry - organized by PNKLN vertical
INDUSTRY_SOURCES = {
    # === LAYER 2: Core Stack ($6.4B) ===
    "core_stack": [
        {
            "name": "Google AI Blog",
            "url": "https://blog.google/technology/ai/",
            "rss": "https://blog.google/rss/",
            "type": "manufacturer",
            "keywords": ["llm", "gemini", "transformer", "tpu", "vertex"],
        },
        {
            "name": "OpenAI Blog",
            "url": "https://openai.com/blog",
            "rss": None,  # No RSS, scrape HTML
            "type": "manufacturer",
            "keywords": ["gpt", "rlhf", "alignment", "safety", "api"],
        },
        {
            "name": "Anthropic Research",
            "url": "https://www.anthropic.com/research",
            "rss": None,
            "type": "manufacturer",
            "keywords": ["claude", "constitutional", "alignment", "safety"],
        },
        {
            "name": "NVIDIA Developer Blog",
            "url": "https://developer.nvidia.com/blog",
            "rss": "https://developer.nvidia.com/blog/feed/",
            "type": "manufacturer",
            "keywords": ["cuda", "tensorrt", "triton", "gpu", "inference"],
        },
        {
            "name": "Hugging Face Blog",
            "url": "https://huggingface.co/blog",
            "rss": "https://huggingface.co/blog/feed.xml",
            "type": "platform",
            "keywords": ["transformers", "diffusers", "datasets", "spaces"],
        },
        {
            "name": "Weights & Biases",
            "url": "https://wandb.ai/fully-connected",
            "rss": None,
            "type": "vendor",
            "keywords": ["mlops", "experiment", "tracking", "sweep"],
        },
        {
            "name": "LangChain Blog",
            "url": "https://blog.langchain.dev/",
            "rss": "https://blog.langchain.dev/rss/",
            "type": "platform",
            "keywords": ["agents", "rag", "chains", "langsmith"],
        },
        {
            "name": "Ray Blog",
            "url": "https://www.ray.io/blog",
            "rss": None,
            "type": "platform",
            "keywords": ["distributed", "serve", "tune", "train"],
        },
        # === NEW: Phase 5 Additions ===
        {
            "name": "Mistral AI Blog",
            "url": "https://mistral.ai/news/",
            "rss": None,
            "type": "manufacturer",
            "keywords": ["mistral", "mixtral", "moe", "open-source", "inference"],
        },
        {
            "name": "DeepMind Blog",
            "url": "https://deepmind.google/discover/blog/",
            "rss": None,
            "type": "manufacturer",
            "keywords": ["deepmind", "gemini", "alphafold", "research", "agi"],
        },
    ],
    # === LAYER 3: Digital Mall ($7.7B) ===
    "digital_mall": [
        {
            "name": "AWS Machine Learning Blog",
            "url": "https://aws.amazon.com/blogs/machine-learning/",
            "rss": "https://aws.amazon.com/blogs/machine-learning/feed/",
            "type": "cloud",
            "keywords": ["sagemaker", "bedrock", "inference", "training"],
        },
        {
            "name": "Google Cloud AI Blog",
            "url": "https://cloud.google.com/blog/products/ai-machine-learning",
            "rss": None,
            "type": "cloud",
            "keywords": ["vertex", "automl", "bigquery", "dataflow"],
        },
        {
            "name": "Azure AI Blog",
            "url": "https://azure.microsoft.com/en-us/blog/tag/ai/",
            "rss": None,
            "type": "cloud",
            "keywords": ["azure", "openai", "cognitive", "copilot"],
        },
        {
            "name": "Replicate Blog",
            "url": "https://replicate.com/blog",
            "rss": None,
            "type": "marketplace",
            "keywords": ["api", "models", "inference", "cog"],
        },
        # === NEW: Phase 5 Additions ===
        {
            "name": "Modal Blog",
            "url": "https://modal.com/blog",
            "rss": None,
            "type": "platform",
            "keywords": ["modal", "serverless", "gpu", "inference", "training"],
        },
        {
            "name": "Together AI Blog",
            "url": "https://www.together.ai/blog",
            "rss": None,
            "type": "platform",
            "keywords": ["together", "inference", "fine-tuning", "llama", "open-source"],
        },
    ],
    # === LAYER 4: RoadMesh ($9.6B) ===
    "roadmesh": [
        {
            "name": "Waymo Blog",
            "url": "https://waymo.com/blog/",
            "rss": None,
            "type": "manufacturer",
            "keywords": ["autonomous", "waymo", "driver", "robotaxi"],
        },
        {
            "name": "NVIDIA DRIVE Blog",
            "url": "https://blogs.nvidia.com/blog/category/automotive/",
            "rss": None,
            "type": "manufacturer",
            "keywords": ["drive", "orin", "hyperion", "av"],
        },
        {
            "name": "Aurora Innovation",
            "url": "https://aurora.tech/blog",
            "rss": None,
            "type": "manufacturer",
            "keywords": ["aurora", "driver", "trucking", "lidar"],
        },
        {
            "name": "Mobileye Blog",
            "url": "https://www.mobileye.com/blog/",
            "rss": None,
            "type": "manufacturer",
            "keywords": ["eyeq", "supervision", "chauffeur", "adas"],
        },
        {
            "name": "Cruise Blog",
            "url": "https://getcruise.com/news/",
            "rss": None,
            "type": "manufacturer",
            "keywords": ["cruise", "origin", "robotaxi", "av"],
        },
        # === NEW: Phase 5 Additions ===
        {
            "name": "Comma.ai Blog",
            "url": "https://blog.comma.ai/",
            "rss": None,
            "type": "manufacturer",
            "keywords": ["comma", "openpilot", "adas", "driving", "open-source"],
        },
        {
            "name": "Applied Intuition Blog",
            "url": "https://www.appliedintuition.com/blog",
            "rss": None,
            "type": "platform",
            "keywords": ["simulation", "adas", "autonomy", "testing", "validation"],
        },
    ],
    # === LAYER 5: Orbital ($17.3B) ===
    "orbital": [
        {
            "name": "SpaceX Updates",
            "url": "https://www.spacex.com/updates/",
            "rss": None,
            "type": "manufacturer",
            "keywords": ["starlink", "falcon", "starship", "dragon"],
        },
        {
            "name": "Planet Labs Blog",
            "url": "https://www.planet.com/pulse/",
            "rss": None,
            "type": "manufacturer",
            "keywords": ["satellite", "imagery", "earth", "observation"],
        },
        {
            "name": "AWS Ground Station",
            "url": "https://aws.amazon.com/ground-station/",
            "rss": None,
            "type": "cloud",
            "keywords": ["ground station", "satellite", "downlink"],
        },
        {
            "name": "Spire Global Blog",
            "url": "https://spire.com/blog/",
            "rss": None,
            "type": "manufacturer",
            "keywords": ["nanosatellite", "maritime", "weather", "aviation"],
        },
        # === NEW: Phase 5 Additions ===
        {
            "name": "Satellite Industry Association",
            "url": "https://sia.org/news/",
            "rss": None,
            "type": "industry_association",
            "keywords": ["satellite", "sia", "policy", "spectrum", "orbital"],
        },
        {
            "name": "Space Force News",
            "url": "https://www.spaceforce.mil/News/",
            "rss": None,
            "type": "government",
            "keywords": ["space force", "ussf", "guardian", "orbital", "defense"],
        },
    ],
    # === LAYER 6: Gov & Defense ($31.4B) ===
    "gov_defense": [
        {
            "name": "Defense Innovation Unit",
            "url": "https://www.diu.mil/latest",
            "rss": None,
            "type": "government",
            "keywords": ["diu", "defense", "prototype", "commercial"],
        },
        {
            "name": "DARPA News",
            "url": "https://www.darpa.mil/news",
            "rss": "https://www.darpa.mil/rss",
            "type": "government",
            "keywords": ["darpa", "research", "program", "innovation"],
        },
        {
            "name": "FDA Digital Health",
            "url": "https://www.fda.gov/medical-devices/digital-health-center-excellence",
            "rss": None,
            "type": "regulatory",
            "keywords": ["fda", "samd", "cleared", "510k"],
        },
        {
            "name": "NIST AI",
            "url": "https://www.nist.gov/artificial-intelligence",
            "rss": None,
            "type": "standards",
            "keywords": ["nist", "rmf", "trustworthy", "standards"],
        },
        {
            "name": "AI.gov",
            "url": "https://www.ai.gov/",
            "rss": None,
            "type": "government",
            "keywords": ["federal", "policy", "strategy", "initiative"],
        },
        # === NEW: Phase 5 Additions ===
        {
            "name": "GAO Science & Tech",
            "url": "https://www.gao.gov/topics/science-technology",
            "rss": "https://www.gao.gov/rss/topic/science-technology.xml",
            "type": "government",
            "keywords": ["gao", "audit", "technology", "ai", "oversight"],
        },
        {
            "name": "CBO Budget Analysis",
            "url": "https://www.cbo.gov/topics/defense-and-national-security",
            "rss": None,
            "type": "government",
            "keywords": ["cbo", "budget", "defense", "spending", "analysis"],
        },
    ],
    # === LAYER 1: Energy ($5.1B) ===
    "energy": [
        {
            "name": "NREL News",
            "url": "https://www.nrel.gov/news/",
            "rss": "https://www.nrel.gov/news/rss.xml",
            "type": "research",
            "keywords": ["renewable", "solar", "wind", "grid"],
        },
        {
            "name": "DOE Office of Electricity",
            "url": "https://www.energy.gov/oe/office-electricity",
            "rss": None,
            "type": "government",
            "keywords": ["grid", "storage", "transmission", "resilience"],
        },
        {
            "name": "CAISO News",
            "url": "http://www.caiso.com/about/Pages/News/default.aspx",
            "rss": None,
            "type": "operator",
            "keywords": ["caiso", "california", "iso", "market"],
        },
    ],
    # === Industry Analysts ===
    "analysts": [
        {
            "name": "Stanford HAI",
            "url": "https://hai.stanford.edu/news",
            "rss": None,
            "type": "academic",
            "keywords": ["stanford", "hai", "research", "policy"],
        },
        {
            "name": "MIT Tech Review AI",
            "url": "https://www.technologyreview.com/topic/artificial-intelligence/",
            "rss": "https://www.technologyreview.com/feed/",
            "type": "media",
            "keywords": ["mit", "review", "ai", "technology"],
        },
        {
            "name": "a16z AI Blog",
            "url": "https://a16z.com/ai/",
            "rss": None,
            "type": "vc",
            "keywords": ["a16z", "andreessen", "investment", "startup"],
        },
        {
            "name": "Sequoia AI Blog",
            "url": "https://www.sequoiacap.com/article/",
            "rss": None,
            "type": "vc",
            "keywords": ["sequoia", "ai", "generative", "startup"],
        },
        # === NEW: Phase 5 Additions - Top ML Practitioners ===
        {
            "name": "Chip Huyen Blog",
            "url": "https://huyenchip.com/blog/",
            "rss": "https://huyenchip.com/feed.xml",
            "type": "practitioner",
            "keywords": ["mlops", "production", "inference", "systems", "real-time"],
        },
        {
            "name": "Lilian Weng Blog",
            "url": "https://lilianweng.github.io/",
            "rss": "https://lilianweng.github.io/feed.xml",
            "type": "practitioner",
            "keywords": ["llm", "rlhf", "agents", "transformers", "research"],
        },
    ],
}


class IndustryCrawler:
    """Ethical industry blog and manufacturer site crawler

    Features:
    - RSS feed parsing where available
    - HTML scraping with rate limiting
    - Vertical relevance scoring
    - robots.txt compliance
    """

    def __init__(self):
        self.storage_path = Path(
            STORAGE_CONFIG.get("industry_articles", {}).get(
                "path",
                str(Path(STORAGE_CONFIG["briefing_output"]["path"]).parent / "industry"),
            ),
        )
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.scraper = EthicalScraper()
        self.rate_limits = SCRAPING_ETHICS["rate_limiting"]

        logger.info(
            "industry_crawler_initialized",
            storage_path=str(self.storage_path),
            source_count=sum(len(sources) for sources in INDUSTRY_SOURCES.values()),
        )

    def _get_rate_limit(self, url: str) -> float:
        """Get appropriate rate limit for domain"""
        domain = urlparse(url).netloc.lower()

        if ".gov" in domain or ".mil" in domain:
            return self.rate_limits.get("regulatory", 10.0)
        if "github" in domain:
            return self.rate_limits.get("github", 2.0)
        return self.rate_limits.get("default_delay", 3.0)

    def _calculate_relevance(
        self,
        article: IndustryArticle,
        source_keywords: list[str],
        vertical: str,
    ) -> float:
        """Calculate article relevance to PNKLN business"""
        text = f"{article.title} {article.summary}".lower()

        # Base score from vertical weight
        vertical_weights = {
            "core_stack": 1.0,
            "digital_mall": 0.9,
            "roadmesh": 0.85,
            "orbital": 0.8,
            "gov_defense": 0.95,
            "energy": 0.7,
            "analysts": 0.75,
        }
        base_score = vertical_weights.get(vertical, 0.5)

        # Keyword match bonus
        keyword_matches = sum(1 for kw in source_keywords if kw.lower() in text)
        keyword_bonus = min(keyword_matches * 0.05, 0.2)  # Max 20% bonus

        # Recency bonus (articles from last 7 days)
        days_old = (datetime.now() - article.published).days
        recency_bonus = 0.1 if days_old <= 7 else 0

        return min(base_score + keyword_bonus + recency_bonus, 1.0)

    async def fetch_rss_feed(
        self,
        source: dict[str, Any],
        vertical: str,
        days_back: int = 30,
    ) -> list[IndustryArticle]:
        """Fetch articles from RSS feed"""
        articles = []
        rss_url = source.get("rss")

        if not rss_url:
            return articles

        try:
            feed = feedparser.parse(rss_url)
            cutoff_date = datetime.now() - timedelta(days=days_back)

            for entry in feed.entries[:20]:  # Limit per source
                # Parse published date
                published = datetime.now()
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    published = datetime(*entry.published_parsed[:6])
                elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
                    published = datetime(*entry.updated_parsed[:6])

                if published < cutoff_date:
                    continue

                article = IndustryArticle(
                    title=entry.get("title", "Untitled"),
                    url=entry.get("link", ""),
                    source=source["name"],
                    published=published,
                    summary=entry.get("summary", "")[:500],
                    vertical=vertical,
                )

                article.relevance_score = self._calculate_relevance(
                    article,
                    source.get("keywords", []),
                    vertical,
                )

                articles.append(article)

            logger.info("rss_feed_fetched", source=source["name"], articles=len(articles))

        except Exception as e:
            logger.error("rss_fetch_error", source=source["name"], error=str(e))

        return articles

    async def scrape_html_source(
        self,
        source: dict[str, Any],
        vertical: str,
        days_back: int = 30,
    ) -> list[IndustryArticle]:
        """Scrape articles from HTML page (when no RSS available)"""
        articles = []
        url = source.get("url")

        if not url:
            return articles

        try:
            # Check robots.txt compliance
            can_fetch = await self.scraper.check_robots_txt(url)
            if not can_fetch:
                logger.warning("robots_txt_blocked", source=source["name"], url=url)
                return articles

            # Rate limiting
            rate_limit = self._get_rate_limit(url)
            await asyncio.sleep(rate_limit)

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers={"User-Agent": SCRAPING_ETHICS["robots_txt"]["user_agent"]},
                    timeout=30.0,
                    follow_redirects=True,
                )

                if response.status_code == 200:
                    # Basic HTML parsing - extract article links
                    # In production, use BeautifulSoup or similar

                    # Create placeholder article for the source
                    # Full HTML parsing would extract individual articles
                    article = IndustryArticle(
                        title=f"Latest from {source['name']}",
                        url=url,
                        source=source["name"],
                        published=datetime.now(),
                        summary=f"Industry updates from {source['name']} ({source['type']})",
                        vertical=vertical,
                    )

                    article.relevance_score = self._calculate_relevance(
                        article,
                        source.get("keywords", []),
                        vertical,
                    )

                    articles.append(article)

                    logger.info(
                        "html_source_scraped",
                        source=source["name"],
                        status=response.status_code,
                    )
                else:
                    logger.warning(
                        "html_scrape_failed",
                        source=source["name"],
                        status=response.status_code,
                    )

        except Exception as e:
            logger.error("html_scrape_error", source=source["name"], error=str(e))

        return articles

    async def crawl_vertical(self, vertical: str, days_back: int = 30) -> list[IndustryArticle]:
        """Crawl all sources for a specific PNKLN vertical"""
        sources = INDUSTRY_SOURCES.get(vertical, [])
        all_articles = []

        for source in sources:
            if source.get("rss"):
                articles = await self.fetch_rss_feed(source, vertical, days_back)
            else:
                articles = await self.scrape_html_source(source, vertical, days_back)

            all_articles.extend(articles)

            # Rate limiting between sources
            await asyncio.sleep(1.0)

        logger.info(
            "vertical_crawl_complete",
            vertical=vertical,
            sources=len(sources),
            articles=len(all_articles),
        )

        return all_articles

    async def crawl_all_verticals(
        self,
        days_back: int = 30,
        min_relevance: float = 0.5,
    ) -> list[IndustryArticle]:
        """Crawl all industry sources across all PNKLN verticals"""
        all_articles = []

        for vertical in INDUSTRY_SOURCES:
            articles = await self.crawl_vertical(vertical, days_back)
            all_articles.extend(articles)

        # Filter by relevance
        filtered = [a for a in all_articles if a.relevance_score >= min_relevance]

        # Sort by relevance
        filtered.sort(key=lambda x: x.relevance_score, reverse=True)

        logger.info(
            "full_crawl_complete",
            total_articles=len(all_articles),
            filtered_articles=len(filtered),
            min_relevance=min_relevance,
        )

        return filtered

    def format_article_markdown(self, article: IndustryArticle) -> str:
        """Format article as markdown"""
        return f"""
# {article.title}

**Source:** {article.source}
**URL:** {article.url}
**Published:** {article.published.strftime("%Y-%m-%d")}
**Vertical:** {article.vertical}
**Relevance Score:** {article.relevance_score:.2f}

## Summary

{article.summary}

---
"""

    def save_articles(self, articles: list[IndustryArticle]) -> list[str]:
        """Save articles to storage"""
        saved_files = []

        for article in articles:
            # Create safe filename
            safe_name = "".join(
                c if c.isalnum() or c in "._- " else "_" for c in article.title[:50]
            ).strip()
            filename = f"{article.published.strftime('%Y%m%d')}_{safe_name}.md"
            filepath = self.storage_path / filename

            try:
                markdown = self.format_article_markdown(article)
                filepath.write_text(markdown, encoding="utf-8")
                saved_files.append(str(filepath))

                logger.debug("article_saved", title=article.title, file=str(filepath))
            except Exception as e:
                logger.error("article_save_error", title=article.title, error=str(e))

        logger.info("articles_saved", count=len(saved_files))

        return saved_files

    def generate_industry_summary(self, articles: list[IndustryArticle]) -> str:
        """Generate summary report of industry intel"""
        summary_parts = [
            "# Industry Intel Summary",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Total Articles:** {len(articles)}",
            "",
        ]

        # Group by vertical
        by_vertical: dict[str, list[IndustryArticle]] = {}
        for article in articles:
            vertical = article.vertical or "other"
            if vertical not in by_vertical:
                by_vertical[vertical] = []
            by_vertical[vertical].append(article)

        for vertical, vert_articles in sorted(by_vertical.items()):
            summary_parts.append(
                f"## {vertical.replace('_', ' ').title()} ({len(vert_articles)} articles)",
            )
            summary_parts.append("")

            for article in vert_articles[:5]:  # Top 5 per vertical
                summary_parts.append(
                    f"- **{article.title}** - {article.source} "
                    f"({article.published.strftime('%Y-%m-%d')}) "
                    f"[{article.relevance_score:.0%}]",
                )

            if len(vert_articles) > 5:
                summary_parts.append(f"- ... and {len(vert_articles) - 5} more")
            summary_parts.append("")

        return "\n".join(summary_parts)


# Convenience functions
async def crawl_industry_intel(days_back: int = 30) -> list[str]:
    """Crawl all industry sources for PNKLN-relevant intel

    Usage:
        files = await crawl_industry_intel(days_back=30)
    """
    crawler = IndustryCrawler()
    articles = await crawler.crawl_all_verticals(days_back=days_back)
    return crawler.save_articles(articles)


async def crawl_vertical_intel(vertical: str, days_back: int = 30) -> list[str]:
    """Crawl specific vertical's industry sources

    Usage:
        files = await crawl_vertical_intel("core_stack", days_back=7)
    """
    crawler = IndustryCrawler()
    articles = await crawler.crawl_vertical(vertical, days_back)
    return crawler.save_articles(articles)
