# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Twitter/X API v2 collector."""

import os
from datetime import datetime

from src.collectors.base import SourceCollector, rate_limit
from src.models import IngestedItem, Tier


class TwitterCollector(SourceCollector):
  """Collect intelligence from Twitter/X using API v2."""

  def __init__(self):
    """
    Initialize Twitter collector.

    Ethical compliance:
    - Rate limited to 1 req/sec
    - User-Agent: Set via Bearer token
    - Cost: $20/month (negotiated from $100)

    """
    super().__init__()
    self.bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
    self.monthly_cost = 20.0
    self.requests_made = 0
    self.included_requests_per_month = 10000

  @rate_limit(max_per_second=1.0)  # GIL001: Rate limiting required
  async def _search_tweets(self, query: str, max_results: int = 10) -> list[dict]:
    """
    Search tweets using Twitter API v2.

    Cost tracking: Flat fee of $20/month for 10k requests
    Additional requests: $0.002 per request

    Args:
        query: Search query
        max_results: Maximum results to return

    Returns:
        List of tweet data dictionaries

    """
    # Mock implementation (replace with actual API call)
    self.requests_made += 1

    # Calculate incremental cost
    if self.requests_made <= self.included_requests_per_month:
      cost_per_request = self.monthly_cost / self.included_requests_per_month
    else:
      cost_per_request = 0.002  # Overage cost

    return [
      {
        "id": f"tweet_{i}",
        "text": f"Sample tweet about {query} #{i}",
        "author_id": f"user_{i}",
        "created_at": "2025-11-17T12:00:00.000Z",
        "public_metrics": {"like_count": 10 + i, "retweet_count": 5 + i},
        "cost": cost_per_request,
      }
      for i in range(max_results)
    ]

  async def collect(self) -> list[IngestedItem]:  # GIL002: Tracks source
    """
    Collect tweets from Twitter.

    Cost: $20/month base + overages
    Expected: 40-50 items/day

    Returns:
        List of ingested items with tier classification

    """
    items = []

    # Search queries for intelligence
    queries = [
      "AI research",
      "machine learning",
      "tech news",
      "startup funding",
    ]

    for query in queries:
      try:
        tweets = await self._search_tweets(query, max_results=12)

        for tweet in tweets:
          # Tier classification based on engagement
          engagement = (
            tweet["public_metrics"]["like_count"]
            + tweet["public_metrics"]["retweet_count"] * 2
          )
          relevance_score = min(0.90, 0.60 + (engagement / 100))

          tier = self._classify_tier(relevance_score)

          item = IngestedItem(
            id=tweet["id"],
            source="twitter",  # GIL002: Source tracked
            tier=tier,  # GIL005: Tier classification required
            relevance_score=relevance_score,
            title=f"Tweet by @{tweet['author_id']}",
            content=tweet["text"],
            url=f"https://twitter.com/i/status/{tweet['id']}",
            published_at=datetime.fromisoformat(
              tweet["created_at"].replace("Z", "+00:00")
            ),
            cost=tweet["cost"],  # GIL003: Cost tracking
            metadata={
              "author": tweet["author_id"],
              "likes": tweet["public_metrics"]["like_count"],
              "retweets": tweet["public_metrics"]["retweet_count"],
            },
          )
          items.append(item)

      except Exception as e:
        self._errors.append(f"Twitter query '{query}' failed: {e}")
        continue

    self._items_collected = len(items)
    return items

  def _classify_tier(self, relevance_score: float) -> Tier:
    """Classify tweet into tier based on relevance."""
    if relevance_score >= 0.85:
      return Tier.TIER_1
    if relevance_score >= 0.70:
      return Tier.TIER_2
    return Tier.TIER_3

  async def check_health(self) -> bool:
    """Check if Twitter API is accessible."""
    if not self.bearer_token:
      return False
    return True

  @property
  def source_name(self) -> str:
    """Return source name."""
    return "twitter"

  @property
  def expected_items_per_day(self) -> int:
    """Expected items per day."""
    return 45
