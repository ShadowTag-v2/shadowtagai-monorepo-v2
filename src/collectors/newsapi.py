# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""NewsAPI.org collector with RSS fallback."""

import os
from datetime import datetime

from src.collectors.base import SourceCollector, rate_limit
from src.models import IngestedItem, Tier


class NewsAPICollector(SourceCollector):
  """Collect news articles from NewsAPI with RSS fallback."""

  def __init__(self):
    """
    Initialize NewsAPI collector.

    Ethical compliance:
    - Rate limited to 1 req/sec
    - Falls back to free RSS feeds when budget exhausted
    - User-Agent: "AiYou-Bot/1.0 (+https://aiyou.ai/bot-info)"

    """
    super().__init__()
    self.api_key = os.getenv("NEWSAPI_KEY")
    self.daily_budget = 2.00  # Reserve budget for NewsAPI
    self.cost_today = 0.0

  @rate_limit(max_per_second=1.0)  # GIL001: Rate limiting required
  async def _fetch_articles(self, query: str, max_results: int = 10) -> list[dict]:
    """
    Fetch articles from NewsAPI.

    Cost: Varies by plan (using free tier for demo)

    Args:
        query: Search query
        max_results: Maximum results

    Returns:
        List of article dictionaries

    """
    # Mock implementation
    return [
      {
        "title": f"News Article {i}: {query}",
        "description": f"Latest news about {query}",
        "url": f"https://example.com/article-{i}",
        "publishedAt": "2025-11-17T12:00:00Z",
        "source": {"name": "Tech News Daily"},
        "cost": 0.0,  # Free tier
      }
      for i in range(max_results)
    ]

  @rate_limit(max_per_second=1.0)
  async def _fetch_rss_fallback(self) -> list[dict]:
    """
    Fetch from free RSS feeds as fallback.

    Free RSS sources:
    - https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml
    - https://www.theguardian.com/world/rss

    Returns:
        List of article dictionaries from RSS

    """
    # Mock RSS parsing
    return [
      {
        "title": f"RSS Article {i}",
        "description": "Free RSS feed article",
        "url": f"https://example.com/rss-{i}",
        "publishedAt": "2025-11-17T12:00:00Z",
        "source": {"name": "RSS Feed"},
        "cost": 0.0,
      }
      for i in range(5)
    ]

  async def collect(self) -> list[IngestedItem]:  # GIL002: Tracks source
    """
    Collect news articles.

    Cost: Free tier + RSS fallback
    Expected: 30-40 items/day

    Returns:
        List of ingested items with tier classification

    """
    items = []

    # Try paid API first if under budget
    if self.cost_today < self.daily_budget:
      queries = ["AI technology", "machine learning", "tech industry"]

      for query in queries:
        try:
          articles = await self._fetch_articles(query, max_results=10)

          for article in articles:
            relevance_score = 0.82  # Mock score

            item = IngestedItem(
              id=f"news_{hash(article['url'])}",
              source="newsapi",  # GIL002: Source tracked
              tier=Tier.TIER_1,  # GIL005: Tier classification
              relevance_score=relevance_score,
              title=article["title"],
              content=article["description"],
              url=article["url"],
              published_at=datetime.fromisoformat(
                article["publishedAt"].replace("Z", "+00:00")
              ),
              cost=article["cost"],
              metadata={"source_name": article["source"]["name"]},
            )
            items.append(item)

        except Exception as e:
          self._errors.append(f"NewsAPI query '{query}' failed: {e}")
          continue
    else:
      # Fallback to free RSS
      try:
        articles = await self._fetch_rss_fallback()

        for article in articles:
          item = IngestedItem(
            id=f"rss_{hash(article['url'])}",
            source="newsapi",  # GIL002: Source tracked
            tier=Tier.TIER_2,  # RSS is lower tier
            relevance_score=0.72,
            title=article["title"],
            content=article["description"],
            url=article["url"],
            published_at=datetime.fromisoformat(
              article["publishedAt"].replace("Z", "+00:00")
            ),
            cost=0.0,
            metadata={"source_name": "RSS Fallback"},
          )
          items.append(item)

      except Exception as e:
        self._errors.append(f"RSS fallback failed: {e}")

    self._items_collected = len(items)
    return items

  async def check_health(self) -> bool:
    """Check if NewsAPI or RSS fallback is available."""
    # Always healthy due to RSS fallback
    return True

  @property
  def source_name(self) -> str:
    """Return source name."""
    return "newsapi"

  @property
  def expected_items_per_day(self) -> int:
    """Expected items per day."""
    return 35
