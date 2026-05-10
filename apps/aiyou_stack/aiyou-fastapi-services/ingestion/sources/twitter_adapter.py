"""PNKLN Core Stack - Twitter/X Source Adapter

Fetches tweets using the Twitter API v2 via Tweepy.
Supports searching by keywords, hashtags, and filtering by engagement.
"""

from collections.abc import AsyncIterator
from datetime import UTC, datetime, timedelta

import structlog
import tweepy
from tweepy.errors import TweepyException

from ingestion.classification.tier_classifier import IngestedItem
from ingestion.core.config import get_config
from ingestion.sources.base import SourceAdapter

logger = structlog.get_logger(__name__)


class TwitterAdapter(SourceAdapter):
    """Twitter API v2 adapter for ingesting tweets.

    Fetches:
    - Tweet text and metadata
    - Author information
    - Engagement metrics (likes, retweets, replies)
    - Media attachments

    Cost: ~$0.003 per tweet (based on API tier costs)
    """

    def __init__(self):
        super().__init__("twitter")
        self.config = get_config()
        self.bearer_token = self.config.sources.twitter_bearer_token

        if not self.bearer_token:
            raise ValueError("Twitter bearer token not configured")

        # Initialize Tweepy client
        self.client = tweepy.Client(bearer_token=self.bearer_token, wait_on_rate_limit=True)

    async def validate_credentials(self) -> bool:
        """Validate Twitter API credentials."""
        try:
            # Try fetching a single tweet to validate access
            self.client.search_recent_tweets(query="test", max_results=10)
            logger.info("twitter_credentials_valid")
            return True
        except TweepyException as e:
            logger.error("twitter_credentials_invalid", error=str(e))
            return False

    def get_cost_estimate(self, num_items: int) -> float:
        """Estimate cost based on Twitter API usage."""
        return num_items * self.config.ingestion.cost_per_twitter_item

    async def fetch_items(
        self,
        queries: list[str] | None = None,
        max_items: int = 1000,
        since: datetime | None = None,
    ) -> AsyncIterator[IngestedItem]:
        """Fetch tweets from Twitter.

        Args:
            queries: Search queries/hashtags (e.g., ["#AI", "machine learning"])
            max_items: Maximum tweets to fetch
            since: Only fetch tweets newer than this timestamp

        Yields:
            IngestedItem objects representing tweets

        """
        if not queries:
            queries = ["artificial intelligence", "#MachineLearning", "#TechNews", "#AI"]

        # Calculate start_time filter
        start_time = since or (datetime.now(UTC) - timedelta(hours=24))

        items_per_query = max_items // len(queries)

        for query in queries:
            try:
                logger.info("twitter_search_started", query=query, max_results=items_per_query)

                # Twitter API allows max 100 results per request
                tweets_to_fetch = min(items_per_query, 100)

                # Search recent tweets
                response = self.client.search_recent_tweets(
                    query=f"{query} -is:retweet lang:en",  # Exclude RTs, English only
                    max_results=tweets_to_fetch,
                    start_time=start_time,
                    tweet_fields=[
                        "created_at",
                        "public_metrics",
                        "author_id",
                        "entities",
                        "attachments",
                    ],
                    expansions=["author_id", "attachments.media_keys"],
                    user_fields=["username", "name", "verified"],
                    media_fields=["url", "preview_image_url"],
                )

                if not response.data:
                    logger.warning("twitter_no_results", query=query)
                    continue

                # Build user lookup
                users = {user.id: user for user in (response.includes.get("users") or [])}
                media = {m.media_key: m for m in (response.includes.get("media") or [])}

                for tweet in response.data:
                    try:
                        item = self._parse_tweet(tweet, users, media)
                        self._record_item_fetched(self.config.ingestion.cost_per_twitter_item)
                        yield item

                    except Exception as e:
                        self._record_error()
                        logger.error("twitter_parse_error", tweet_id=tweet.id, error=str(e))

            except TweepyException as e:
                self._record_error()
                logger.error("twitter_api_error", query=query, error=str(e))

    def _parse_tweet(self, tweet: tweepy.Tweet, users: dict, media: dict) -> IngestedItem:
        """Parse Twitter API response into IngestedItem."""
        # Get author info
        author = users.get(tweet.author_id)
        author_name = f"@{author.username}" if author else "Unknown"

        # Extract metrics
        metrics = tweet.public_metrics or {}

        # Extract entities (hashtags, mentions, URLs)
        entities = tweet.entities or {}
        hashtags = [tag["tag"] for tag in entities.get("hashtags", [])]
        mentions = [mention["username"] for mention in entities.get("mentions", [])]
        urls = [url["expanded_url"] for url in entities.get("urls", [])]

        # Extract media
        media_urls = []
        if hasattr(tweet, "attachments") and tweet.attachments:
            media_keys = tweet.attachments.get("media_keys", [])
            for key in media_keys:
                if key in media:
                    media_item = media[key]
                    media_urls.append(
                        getattr(media_item, "url", None)
                        or getattr(media_item, "preview_image_url", None),
                    )

        # Build metadata
        metadata = {
            "author_id": str(tweet.author_id),
            "author_verified": author.verified if author else False,
            "retweet_count": metrics.get("retweet_count", 0),
            "reply_count": metrics.get("reply_count", 0),
            "like_count": metrics.get("like_count", 0),
            "quote_count": metrics.get("quote_count", 0),
            "hashtags": hashtags,
            "mentions": mentions,
            "urls": urls,
            "media_urls": media_urls,
            "engagement_score": (
                metrics.get("retweet_count", 0) * 2
                + metrics.get("like_count", 0)
                + metrics.get("reply_count", 0) * 3
            ),
        }

        return IngestedItem(
            id=f"twitter_{tweet.id}",
            source="twitter",
            title=tweet.text[:100] + "..." if len(tweet.text) > 100 else tweet.text,
            content=tweet.text,
            url=f"https://twitter.com/i/status/{tweet.id}",
            published_at=tweet.created_at,
            author=author_name,
            metadata=metadata,
        )
