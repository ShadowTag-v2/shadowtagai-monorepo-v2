"""PNKLN Core Stack - YouTube Source Adapter

Fetches videos from YouTube using the YouTube Data API v3.
Supports searching by keywords, channels, and filtering by date.
"""

from collections.abc import AsyncIterator
from datetime import datetime, timedelta

import structlog
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from ingestion.classification.tier_classifier import IngestedItem
from ingestion.core.config import get_config
from ingestion.sources.base import SourceAdapter

logger = structlog.get_logger(__name__)


class YouTubeAdapter(SourceAdapter):
    """YouTube Data API v3 adapter for ingesting video content.

    Fetches:
    - Video metadata (title, description, published date)
    - Channel information
    - View counts and engagement metrics

    Cost: ~$0.005 per video (based on quota costs)
    """

    def __init__(self):
        super().__init__("youtube")
        self.config = get_config()
        self.api_key = self.config.sources.youtube_api_key

        if not self.api_key:
            raise ValueError("YouTube API key not configured")

        self.youtube = build("youtube", "v3", developerKey=self.api_key)

    async def validate_credentials(self) -> bool:
        """Validate YouTube API key by making a simple request."""
        try:
            # Try a simple search query
            request = self.youtube.search().list(
                part="snippet",
                q="test",
                maxResults=1,
                type="video",
            )
            request.execute()
            logger.info("youtube_credentials_valid")
            return True
        except HttpError as e:
            logger.error("youtube_credentials_invalid", error=str(e))
            return False

    def get_cost_estimate(self, num_items: int) -> float:
        """Estimate cost based on YouTube quota consumption."""
        return num_items * self.config.ingestion.cost_per_youtube_item

    async def fetch_items(
        self,
        queries: list[str] | None = None,
        max_items: int = 1000,
        since: datetime | None = None,
    ) -> AsyncIterator[IngestedItem]:
        """Fetch videos from YouTube.

        Args:
            queries: Search keywords (e.g., ["AI research", "machine learning"])
            max_items: Maximum videos to fetch
            since: Only fetch videos published after this date

        Yields:
            IngestedItem objects representing YouTube videos

        """
        if not queries:
            queries = ["artificial intelligence", "machine learning", "technology news"]

        # Calculate published_after filter
        published_after = None
        if since:
            published_after = since.isoformat() + "Z"
        else:
            # Default to last 24 hours
            published_after = (datetime.utcnow() - timedelta(hours=24)).isoformat() + "Z"

        items_per_query = max_items // len(queries)

        for query in queries:
            try:
                logger.info("youtube_search_started", query=query, max_results=items_per_query)

                # Search for videos
                request = self.youtube.search().list(
                    part="snippet",
                    q=query,
                    type="video",
                    maxResults=min(items_per_query, 50),  # YouTube API limit
                    order="date",
                    publishedAfter=published_after,
                    relevanceLanguage="en",
                )

                response = request.execute()

                video_ids = [item["id"]["videoId"] for item in response.get("items", [])]

                if not video_ids:
                    logger.warning("youtube_no_results", query=query)
                    continue

                # Fetch detailed video information
                videos_request = self.youtube.videos().list(
                    part="snippet,contentDetails,statistics",
                    id=",".join(video_ids),
                )

                videos_response = videos_request.execute()

                for video_data in videos_response.get("items", []):
                    try:
                        item = self._parse_video(video_data)
                        self._record_item_fetched(self.config.ingestion.cost_per_youtube_item)
                        yield item

                    except Exception as e:
                        self._record_error()
                        logger.error(
                            "youtube_parse_error",
                            video_id=video_data.get("id"),
                            error=str(e),
                        )

            except HttpError as e:
                self._record_error()
                logger.error("youtube_api_error", query=query, error=str(e))

    def _parse_video(self, video_data: dict) -> IngestedItem:
        """Parse YouTube API response into IngestedItem."""
        snippet = video_data["snippet"]
        statistics = video_data.get("statistics", {})

        # Parse published date
        published_at = datetime.fromisoformat(snippet["publishedAt"].replace("Z", "+00:00"))

        # Build metadata
        metadata = {
            "channel_id": snippet["channelId"],
            "channel_title": snippet["channelTitle"],
            "view_count": int(statistics.get("viewCount", 0)),
            "like_count": int(statistics.get("likeCount", 0)),
            "comment_count": int(statistics.get("commentCount", 0)),
            "tags": snippet.get("tags", []),
            "category_id": snippet.get("categoryId"),
            "duration": video_data.get("contentDetails", {}).get("duration"),
            "thumbnail_url": snippet.get("thumbnails", {}).get("high", {}).get("url"),
        }

        return IngestedItem(
            id=f"youtube_{video_data['id']}",
            source="youtube",
            title=snippet["title"],
            content=snippet.get("description"),
            url=f"https://www.youtube.com/watch?v={video_data['id']}",
            published_at=published_at,
            author=snippet["channelTitle"],
            metadata=metadata,
        )
