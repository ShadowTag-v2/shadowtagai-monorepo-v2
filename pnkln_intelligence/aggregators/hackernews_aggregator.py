# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Hacker News Aggregator
Collects AI/ML related stories and discussions from Hacker News using Algolia API
"""

import logging
from datetime import datetime, timedelta
from typing import Any
import httpx
from dataclasses import dataclass

from pnkln_intelligence.config import HackerNewsSettings

logger = logging.getLogger(__name__)


@dataclass
class HNStory:
    """Represents a Hacker News story"""

    object_id: str
    title: str
    url: str | None
    author: str
    points: int
    num_comments: int
    created_at: datetime
    created_at_i: int
    story_text: str | None = None
    tags: list[str] = None


class HackerNewsAggregator:
    """
    Aggregates AI/ML related stories from Hacker News

    Uses Algolia HN Search API for efficient filtering and searching.
    Supports:
    - Keyword-based searches
    - Time-range filtering
    - Point/comment thresholds
    - Story type filtering
    """

    def __init__(self, settings: HackerNewsSettings | None = None):
        self.settings = settings or HackerNewsSettings()
        self.base_url = self.settings.api_base_url
        self.client = httpx.AsyncClient(timeout=30.0)

    async def search_stories(self, query: str, tags: str = "story", numeric_filters: str | None = None, max_results: int = 100) -> list[HNStory]:
        """
        Search for stories using Algolia API

        Args:
            query: Search query string
            tags: Filter by tags (e.g., "story", "comment")
            numeric_filters: Numeric filters (e.g., "points>10")
            max_results: Maximum number of results

        Returns:
            List of HNStory objects
        """
        url = f"{self.base_url}/search"
        params = {"query": query, "tags": tags, "hitsPerPage": min(max_results, 1000)}

        if numeric_filters:
            params["numericFilters"] = numeric_filters

        try:
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            stories = []
            for hit in data.get("hits", []):
                story = HNStory(
                    object_id=hit.get("objectID"),
                    title=hit.get("title", ""),
                    url=hit.get("url"),
                    author=hit.get("author", ""),
                    points=hit.get("points", 0),
                    num_comments=hit.get("num_comments", 0),
                    created_at=datetime.fromtimestamp(hit.get("created_at_i", 0)),
                    created_at_i=hit.get("created_at_i", 0),
                    story_text=hit.get("story_text"),
                    tags=hit.get("_tags", []),
                )
                stories.append(story)

            logger.info(f"Retrieved {len(stories)} HN stories for query: {query}")
            return stories

        except Exception as e:
            logger.error(f"Error searching HN: {e}", exc_info=True)
            raise

    async def search_by_date(
        self, query: str, tags: str = "story", start_timestamp: int | None = None, end_timestamp: int | None = None, max_results: int = 100
    ) -> list[HNStory]:
        """
        Search stories by date range using search_by_date endpoint

        Args:
            query: Search query
            tags: Filter by tags
            start_timestamp: Start timestamp (Unix)
            end_timestamp: End timestamp (Unix)
            max_results: Maximum results

        Returns:
            List of HNStory objects
        """
        url = f"{self.base_url}/search_by_date"
        params = {"query": query, "tags": tags, "hitsPerPage": min(max_results, 1000)}

        # Build numeric filters for time range
        filters = []
        if start_timestamp:
            filters.append(f"created_at_i>{start_timestamp}")
        if end_timestamp:
            filters.append(f"created_at_i<{end_timestamp}")

        if filters:
            params["numericFilters"] = ",".join(filters)

        try:
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            stories = []
            for hit in data.get("hits", []):
                story = HNStory(
                    object_id=hit.get("objectID"),
                    title=hit.get("title", ""),
                    url=hit.get("url"),
                    author=hit.get("author", ""),
                    points=hit.get("points", 0),
                    num_comments=hit.get("num_comments", 0),
                    created_at=datetime.fromtimestamp(hit.get("created_at_i", 0)),
                    created_at_i=hit.get("created_at_i", 0),
                    story_text=hit.get("story_text"),
                    tags=hit.get("_tags", []),
                )
                stories.append(story)

            logger.info(f"Retrieved {len(stories)} HN stories by date for query: {query}")
            return stories

        except Exception as e:
            logger.error(f"Error searching HN by date: {e}", exc_info=True)
            raise

    async def aggregate_ai_ml_stories(self, days_back: int = 7, min_points: int | None = None) -> list[dict[str, Any]]:
        """
        Aggregate AI/ML related stories from the last N days

        Args:
            days_back: Number of days to look back
            min_points: Minimum points threshold

        Returns:
            List of story dictionaries
        """
        min_points = min_points or self.settings.min_points
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days_back)

        start_timestamp = int(start_time.timestamp())
        end_timestamp = int(end_time.timestamp())

        all_stories = []
        for keyword in self.settings.search_keywords:
            stories = await self.search_by_date(
                query=keyword, tags="story", start_timestamp=start_timestamp, end_timestamp=end_timestamp, max_results=self.settings.max_results
            )

            # Filter by points
            filtered_stories = [s for s in stories if s.points >= min_points]
            all_stories.extend(filtered_stories)

        # Deduplicate by object_id
        unique_stories = {s.object_id: s for s in all_stories}
        stories_list = list(unique_stories.values())

        # Sort by points descending
        stories_list.sort(key=lambda x: x.points, reverse=True)

        results = []
        for story in stories_list:
            results.append(
                {
                    "object_id": story.object_id,
                    "title": story.title,
                    "url": story.url,
                    "author": story.author,
                    "points": story.points,
                    "num_comments": story.num_comments,
                    "created_at": story.created_at.isoformat(),
                    "story_text": story.story_text,
                    "tags": story.tags,
                    "hn_url": f"https://news.ycombinator.com/item?id={story.object_id}",
                }
            )

        logger.info(f"Aggregated {len(results)} unique AI/ML stories from HN")
        return results

    async def get_top_stories(self, keyword: str, max_results: int = 25, min_points: int = 10) -> list[HNStory]:
        """
        Get top stories for a specific keyword

        Args:
            keyword: Search keyword
            max_results: Maximum results
            min_points: Minimum points threshold

        Returns:
            List of HNStory objects
        """
        numeric_filters = f"points>{min_points}"
        stories = await self.search_stories(query=keyword, tags="story", numeric_filters=numeric_filters, max_results=max_results)

        # Sort by points
        stories.sort(key=lambda x: x.points, reverse=True)
        return stories

    async def aggregate_trending_topics(self, days_back: int = 1) -> dict[str, list[dict[str, Any]]]:
        """
        Aggregate trending topics across all keywords

        Args:
            days_back: Number of days to look back

        Returns:
            Dictionary mapping keywords to stories
        """
        results = {}
        for keyword in self.settings.search_keywords:
            stories = await self.get_top_stories(keyword=keyword, max_results=25, min_points=self.settings.min_points)

            results[keyword] = [
                {
                    "object_id": s.object_id,
                    "title": s.title,
                    "url": s.url,
                    "author": s.author,
                    "points": s.points,
                    "num_comments": s.num_comments,
                    "created_at": s.created_at.isoformat(),
                    "hn_url": f"https://news.ycombinator.com/item?id={s.object_id}",
                }
                for s in stories
            ]

        return results

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


# Example usage
if __name__ == "__main__":
    import asyncio

    async def main():
        aggregator = HackerNewsAggregator()

        try:
            # Get recent AI/ML stories
            stories = await aggregator.aggregate_ai_ml_stories(days_back=7, min_points=10)
            print(f"\nFound {len(stories)} AI/ML stories from the last 7 days")

            for story in stories[:5]:
                print(f"\n{story['title']}")
                print(f"Points: {story['points']} | Comments: {story['num_comments']}")
                print(f"URL: {story['hn_url']}")

        finally:
            await aggregator.close()

    asyncio.run(main())
