# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Reddit Collector
Collects posts from AI-related subreddits
"""

from datetime import datetime
from typing import Any

try:
    import praw

    PRAW_AVAILABLE = True
except ImportError:
    PRAW_AVAILABLE = False

from ..core.gemini_ingestion import IngestedItem, Source
from .base import BaseCollector


class RedditCollector(BaseCollector):
    """Reddit API collector via PRAW

    Pricing: FREE (read-only access)
    Rate Limits: 60 requests per minute
    """

    def __init__(self, api_key: str | None = None, config: dict[str, Any] | None = None):
        super().__init__(api_key, config)

        if not PRAW_AVAILABLE:
            raise ImportError("praw not installed. Run: pip install praw")

        client_id = self.config.get("client_id")
        client_secret = self.config.get("client_secret")
        user_agent = self.config.get("user_agent", "PNKLNBot/1.0")

        if not (client_id and client_secret):
            raise ValueError("Reddit client_id and client_secret required")

        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent,
        )
        self.rate_limit_delay = 1.0  # 1 second between requests
        self.cost_per_request = 0.0  # Reddit API is free

    def collect(self, source: Source, target_count: int) -> list[IngestedItem]:
        """Collect posts from AI-related subreddits

        Default subreddits: MachineLearning, artificial, LocalLLaMA, OpenAI
        """
        items = []
        subreddits = self.config.get(
            "subreddits",
            ["MachineLearning", "artificial", "LocalLLaMA", "OpenAI"],
        )

        try:
            posts_per_subreddit = max(target_count // len(subreddits), 10)

            for subreddit_name in subreddits:
                subreddit = self.reddit.subreddit(subreddit_name)

                # Get hot posts from past week
                for post in subreddit.hot(limit=posts_per_subreddit):
                    # Skip stickied posts
                    if post.stickied:
                        continue

                    # Calculate relevance based on upvotes and comments
                    engagement = post.score + (post.num_comments * 2)
                    relevance = min(0.4 + (engagement / 100), 0.8)  # Cap at 0.8 for Reddit

                    item = IngestedItem(
                        item_id=f"reddit_{post.id}",
                        source=source,
                        title=post.title,
                        content=(post.selftext or "")[:500],  # First 500 chars
                        url=f"https://reddit.com{post.permalink}",
                        ingested_at=datetime.utcnow(),
                        relevance_score=relevance,
                        timeliness_score=self._calculate_timeliness(post.created_utc),
                        completeness_score=0.5,  # Reddit posts vary in quality
                        cost_usd=self.cost_per_request,
                        metadata={
                            "source_url": source.url,
                            "source_type": source.source_type.value,
                            "tier": source.tier.value,
                            "post_id": post.id,
                            "subreddit": subreddit_name,
                            "author": str(post.author) if post.author else "[deleted]",
                            "score": post.score,
                            "num_comments": post.num_comments,
                            "created_utc": post.created_utc,
                        },
                    )
                    items.append(item)

                self._respect_rate_limit()

        except Exception as e:
            print(f"Reddit API error: {e}")

        return items

    def _calculate_timeliness(self, created_utc: float) -> float:
        """Calculate timeliness score"""
        age_hours = (datetime.utcnow().timestamp() - created_utc) / 3600

        if age_hours <= 12:
            return 1.0
        if age_hours <= 48:
            return 0.8
        if age_hours <= 168:  # 1 week
            return 0.6
        return 0.4
