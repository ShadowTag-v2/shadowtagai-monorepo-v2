# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""YouTube Data API v3 collector."""

import os
from datetime import datetime

from src.collectors.base import SourceCollector, rate_limit
from src.models import IngestedItem, Tier


class YouTubeCollector(SourceCollector):
  """Collect intelligence from YouTube using Data API v3."""

  def __init__(self):
    """
    Initialize YouTube collector.

    Ethical compliance:
    - YouTube API has rate limiting built-in (quota system)
    - User-Agent: Set via API key identification
    - No robots.txt needed (using official API)

    """
    super().__init__()
    self.api_key = os.getenv("YOUTUBE_API_KEY")
    self.quota_used = 0
    self.daily_quota_limit = 10000

  @rate_limit(max_per_second=1.0)  # GIL001: Rate limiting required
  async def _fetch_videos(self, query: str, max_results: int = 10) -> list[dict]:
    """
    Fetch videos from YouTube API.

    Cost tracking: Each search costs 100 quota units

    Args:
        query: Search query
        max_results: Maximum results to return

    Returns:
        List of video data dictionaries

    """
    # Simulate API call (replace with actual implementation)
    # import aiohttp
    # async with aiohttp.ClientSession() as session:
    #     async with session.get(url, params=params) as response:
    #         return await response.json()

    # Mock data for demonstration
    self.quota_used += 100  # Search operation costs 100 units
    return [
      {
        "id": f"video_{i}",
        "title": f"Sample Video {i}: {query}",
        "description": f"This is a sample video about {query}",
        "published_at": "2025-11-17T12:00:00Z",
        "channel_title": "Sample Channel",
      }
      for i in range(max_results)
    ]

  async def collect(self) -> list[IngestedItem]:  # GIL002: Tracks source
    """
    Collect videos from YouTube.

    Cost: ~$0 (free tier covers 10,000 quota units/day)
    Expected: 20-30 items/day

    Returns:
        List of ingested items with tier classification

    """
    items = []

    # Search queries for intelligence gathering
    queries = [
      "AI news today",
      "machine learning breakthrough",
      "tech industry update",
    ]

    for query in queries:
      try:
        videos = await self._fetch_videos(query, max_results=10)

        for video in videos:
          # Tier classification based on channel quality
          # (In production, use historical performance data)
          relevance_score = 0.85  # Mock score
          tier = self._classify_tier(relevance_score, source_quality=0.80)

          item = IngestedItem(
            id=video["id"],
            source="youtube",  # GIL002: Source tracked
            tier=tier,  # GIL005: Tier classification required
            relevance_score=relevance_score,
            title=video["title"],
            content=video["description"],
            url=f"https://youtube.com/watch?v={video['id']}",
            published_at=datetime.fromisoformat(
              video["published_at"].replace("Z", "+00:00")
            ),
            cost=0.0,  # Free tier
            metadata={
              "channel": video["channel_title"],
              "quota_used": 100,
            },
          )
          items.append(item)

      except Exception as e:
        self._errors.append(f"YouTube query '{query}' failed: {e}")
        continue

    self._items_collected = len(items)
    return items

  def _classify_tier(self, relevance_score: float, source_quality: float) -> Tier:
    """
    Classify item into tier.

    Args:
        relevance_score: Relevance score from Gemini
        source_quality: Historical source quality (0.0-1.0)

    Returns:
        Tier classification

    """
    combined_score = (relevance_score * 0.7) + (source_quality * 0.3)

    if combined_score >= 0.90:
      return Tier.TIER_1
    if combined_score >= 0.70:
      return Tier.TIER_2
    return Tier.TIER_3

  async def check_health(self) -> bool:
    """Check if YouTube API is accessible and quota is available."""
    if not self.api_key:
      return False
    if self.quota_used >= self.daily_quota_limit:
      return False
    return True

  @property
  def source_name(self) -> str:
    """Return source name."""
    return "youtube"

  @property
  def expected_items_per_day(self) -> int:
    """Expected items per day."""
    return 25
