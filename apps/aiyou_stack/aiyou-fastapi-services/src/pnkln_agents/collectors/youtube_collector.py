# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""YouTube Data API Collector
Collects videos using YouTube Data API v3
"""

from datetime import datetime, timedelta
from typing import Any

try:
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError

    YOUTUBE_AVAILABLE = True
except ImportError:
    YOUTUBE_AVAILABLE = False

from ..core.gemini_ingestion import IngestedItem, Source
from .base import BaseCollector


class YouTubeCollector(BaseCollector):
    """YouTube Data API v3 collector

    Pricing: $0 for first 10K requests/day, then $0.20/1K requests
    Quota: 10,000 units/day (search = 100 units, video details = 1 unit)
    """

    def __init__(self, api_key: str | None = None, config: dict[str, Any] | None = None):
        super().__init__(api_key, config)

        if not YOUTUBE_AVAILABLE:
            raise ImportError(
                "google-api-python-client not installed. Run: pip install google-api-python-client",
            )

        if not self.api_key:
            raise ValueError("YouTube API key required")

        self.youtube = build("youtube", "v3", developerKey=self.api_key)
        self.quota_cost_per_search = 100  # YouTube quota units
        self.quota_cost_per_video = 1

    def collect(self, source: Source, target_count: int) -> list[IngestedItem]:
        """Collect videos from YouTube

        Uses search API to find recent AI/tech videos
        """
        items = []

        try:
            # Search for recent videos (last 7 days)
            published_after = (datetime.utcnow() - timedelta(days=7)).isoformat() + "Z"

            search_query = self.config.get("search_query", "AI agents OR artificial intelligence")
            max_results = min(target_count, 50)  # YouTube API limit per request

            request = self.youtube.search().list(
                part="snippet",
                q=search_query,
                type="video",
                publishedAfter=published_after,
                maxResults=max_results,
                order="relevance",
                relevanceLanguage="en",
                safeSearch="moderate",
            )

            response = request.execute()

            for video in response.get("items", []):
                video_id = video["id"]["videoId"]
                snippet = video["snippet"]

                # Calculate relevance score based on title/description match
                relevance = self._calculate_relevance(snippet["title"], snippet["description"])

                item = IngestedItem(
                    item_id=f"youtube_{video_id}",
                    source=source,
                    title=snippet["title"],
                    content=snippet["description"][:500],  # First 500 chars
                    url=f"https://www.youtube.com/watch?v={video_id}",
                    ingested_at=datetime.utcnow(),
                    relevance_score=relevance,
                    timeliness_score=self._calculate_timeliness(snippet["publishedAt"]),
                    completeness_score=0.8,  # Videos generally have good metadata
                    cost_usd=self._calculate_cost(1, self.quota_cost_per_search),
                    metadata={
                        "source_url": source.url,
                        "source_type": source.source_type.value,
                        "tier": source.tier.value,
                        "video_id": video_id,
                        "channel_title": snippet.get("channelTitle"),
                        "published_at": snippet["publishedAt"],
                    },
                )
                items.append(item)

            self._respect_rate_limit()

        except HttpError as e:
            print(f"YouTube API error: {e}")
            # Return empty list on error (graceful degradation)

        return items

    def _calculate_relevance(self, title: str, description: str) -> float:
        """Calculate relevance score based on keyword matching"""
        keywords = [
            "AI",
            "agent",
            "LLM",
            "GPT",
            "machine learning",
            "deep learning",
            "neural network",
            "transformer",
            "Claude",
            "ChatGPT",
        ]

        text = (title + " " + description).lower()
        matches = sum(1 for kw in keywords if kw.lower() in text)

        return min(0.5 + (matches * 0.1), 1.0)

    def _calculate_timeliness(self, published_at: str) -> float:
        """Calculate timeliness score (newer = better)"""
        published = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
        age_days = (datetime.now(published.tzinfo) - published).days

        if age_days <= 1:
            return 1.0
        if age_days <= 3:
            return 0.9
        if age_days <= 7:
            return 0.7
        return 0.5

    def _calculate_cost(self, api_calls: int, quota_units: int) -> float:
        """YouTube pricing: $0.20 per 1K quota units after free tier (10K/day)
        For simplicity, assume average cost across free+paid
        """
        if quota_units <= 10000:  # Within free tier
            return 0.0
        paid_units = quota_units - 10000
        return (paid_units / 1000) * 0.20
