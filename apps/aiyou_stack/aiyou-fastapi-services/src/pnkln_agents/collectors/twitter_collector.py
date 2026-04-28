# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Twitter API v2 Collector
Collects tweets using Twitter API v2
"""

from datetime import datetime
from typing import Any

try:
    import tweepy

    TWEEPY_AVAILABLE = True
except ImportError:
    TWEEPY_AVAILABLE = False

from ..core.gemini_ingestion import IngestedItem, Source
from .base import BaseCollector


class TwitterCollector(BaseCollector):
    """Twitter API v2 collector

    Pricing: Essential ($100/mo for 10K tweets/month), Basic ($100/mo for 50K/month)
    Rate Limits: 180 requests per 15 min window (Essential tier)
    """

    def __init__(self, api_key: str | None = None, config: dict[str, Any] | None = None):
        super().__init__(api_key, config)

        if not TWEEPY_AVAILABLE:
            raise ImportError("tweepy not installed. Run: pip install tweepy")

        bearer_token = self.config.get("bearer_token") or self.api_key
        if not bearer_token:
            raise ValueError("Twitter Bearer Token required")

        self.client = tweepy.Client(bearer_token=bearer_token)
        self.cost_per_tweet = 0.01  # $100/mo for 10K tweets = $0.01/tweet

    def collect(self, source: Source, target_count: int) -> list[IngestedItem]:
        """Collect tweets from Twitter

        Searches for AI-related tweets from past 7 days
        """
        items = []

        try:
            query = self.config.get("search_query", "(AI agents OR LLM OR GPT) lang:en -is:retweet")
            max_results = min(target_count, 100)  # Twitter API limit per request

            tweets = self.client.search_recent_tweets(
                query=query,
                max_results=max_results,
                tweet_fields=["created_at", "public_metrics", "author_id"],
                expansions=["author_id"],
                user_fields=["username", "verified"],
            )

            if not tweets.data:
                return items

            # Create user lookup
            users = {user.id: user for user in tweets.includes.get("users", [])}

            for tweet in tweets.data:
                author = users.get(tweet.author_id)

                # Calculate relevance based on engagement
                metrics = tweet.public_metrics
                engagement = (
                    metrics["like_count"] + metrics["retweet_count"] * 2 + metrics["reply_count"]
                )
                relevance = min(0.5 + (engagement / 100), 1.0)

                # Boost verified authors
                if author and author.verified:
                    relevance = min(relevance + 0.1, 1.0)

                item = IngestedItem(
                    item_id=f"twitter_{tweet.id}",
                    source=source,
                    title=f"Tweet by @{author.username if author else 'unknown'}",
                    content=tweet.text,
                    url=f"https://twitter.com/{author.username}/status/{tweet.id}"
                    if author
                    else f"https://twitter.com/i/status/{tweet.id}",
                    ingested_at=datetime.utcnow(),
                    relevance_score=relevance,
                    timeliness_score=self._calculate_timeliness(tweet.created_at),
                    completeness_score=0.6,  # Tweets are short, limited context
                    cost_usd=self.cost_per_tweet,
                    metadata={
                        "source_url": source.url,
                        "source_type": source.source_type.value,
                        "tier": source.tier.value,
                        "tweet_id": str(tweet.id),
                        "author": author.username if author else None,
                        "verified": author.verified if author else False,
                        "likes": metrics["like_count"],
                        "retweets": metrics["retweet_count"],
                    },
                )
                items.append(item)

            self._respect_rate_limit()

        except tweepy.TweepyException as e:
            print(f"Twitter API error: {e}")

        return items

    def _calculate_timeliness(self, created_at: datetime) -> float:
        """Calculate timeliness score"""
        age_hours = (datetime.utcnow() - created_at.replace(tzinfo=None)).total_seconds() / 3600

        if age_hours <= 6:
            return 1.0
        if age_hours <= 24:
            return 0.9
        if age_hours <= 72:
            return 0.7
        return 0.5
