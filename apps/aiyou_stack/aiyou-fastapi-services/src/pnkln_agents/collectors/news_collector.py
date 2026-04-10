"""
News API Collector
Collects news articles using NewsAPI.org
"""

import hashlib
from datetime import datetime, timedelta
from typing import Any

try:
    from newsapi import NewsApiClient

    NEWSAPI_AVAILABLE = True
except ImportError:
    NEWSAPI_AVAILABLE = False

from ..core.gemini_ingestion import IngestedItem, Source
from .base import BaseCollector


class NewsCollector(BaseCollector):
    """
    NewsAPI.org collector

    Pricing: Free for 100 requests/day, Developer plan $449/mo for 250K requests
    Rate Limits: 100 requests/day (free), 1000 requests/day (paid)
    """

    def __init__(self, api_key: str | None = None, config: dict[str, Any] | None = None):
        super().__init__(api_key, config)

        if not NEWSAPI_AVAILABLE:
            raise ImportError("newsapi-python not installed. Run: pip install newsapi-python")

        if not self.api_key:
            raise ValueError("NewsAPI key required")

        self.client = NewsApiClient(api_key=self.api_key)
        self.cost_per_request = 0.002  # $449/mo for 250K = $0.0018/request

    def collect(self, source: Source, target_count: int) -> list[IngestedItem]:
        """
        Collect news articles from NewsAPI

        Searches for AI-related news from past 7 days
        """
        items = []

        try:
            query = self.config.get(
                "search_query", 'AI OR "artificial intelligence" OR "machine learning"'
            )
            from_date = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d")
            page_size = min(target_count, 100)  # NewsAPI limit

            response = self.client.get_everything(
                q=query,
                from_param=from_date,
                language="en",
                sort_by="relevancy",
                page_size=page_size,
            )

            for article in response.get("articles", []):
                # Calculate relevance based on source and engagement indicators
                relevance = self._calculate_relevance(article)

                item = IngestedItem(
                    item_id=f"news_{hashlib.md5(article['url'].encode()).hexdigest()[:16]}",
                    source=source,
                    title=article["title"],
                    content=article.get("description", "") or article.get("content", "")[:500],
                    url=article["url"],
                    ingested_at=datetime.utcnow(),
                    relevance_score=relevance,
                    timeliness_score=self._calculate_timeliness(article.get("publishedAt", "")),
                    completeness_score=0.9,  # News articles generally complete
                    cost_usd=self.cost_per_request,
                    metadata={
                        "source_url": source.url,
                        "source_type": source.source_type.value,
                        "tier": source.tier.value,
                        "author": article.get("author"),
                        "source_name": article["source"]["name"],
                        "published_at": article.get("publishedAt"),
                        "url_to_image": article.get("urlToImage"),
                    },
                )
                items.append(item)

            self._respect_rate_limit()

        except Exception as e:
            print(f"NewsAPI error: {e}")

        return items

    def _calculate_relevance(self, article: dict[str, Any]) -> float:
        """Calculate relevance based on source tier and content"""
        # Tier 1 sources (major news outlets)
        tier1_sources = [
            "bbc",
            "reuters",
            "bloomberg",
            "wall street journal",
            "new york times",
            "washington post",
            "associated press",
        ]

        source_name = article["source"]["name"].lower()
        relevance = 0.6  # Base relevance

        # Boost for tier 1 sources
        if any(t1 in source_name for t1 in tier1_sources):
            relevance += 0.2

        # Boost for AI keywords in title
        title_lower = article["title"].lower()
        if "ai" in title_lower or "artificial intelligence" in title_lower:
            relevance += 0.1

        return min(relevance, 1.0)

    def _calculate_timeliness(self, published_at: str) -> float:
        """Calculate timeliness score"""
        if not published_at:
            return 0.5

        try:
            published = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
            age_days = (datetime.now(published.tzinfo) - published).days

            if age_days <= 1:
                return 1.0
            elif age_days <= 3:
                return 0.9
            elif age_days <= 7:
                return 0.7
            else:
                return 0.5
        except:
            return 0.5
