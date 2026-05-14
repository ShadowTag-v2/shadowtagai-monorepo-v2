# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Reddit Aggregator
Collects AI/ML discussions from targeted subreddits using PRAW
"""

import logging
from datetime import datetime
from typing import Any
from dataclasses import dataclass
import praw
from praw.models import Submission

from pnkln_intelligence.config import RedditSettings

logger = logging.getLogger(__name__)


@dataclass
class RedditPost:
    """Represents a Reddit post"""

    post_id: str
    subreddit: str
    title: str
    author: str
    score: int
    num_comments: int
    created_utc: datetime
    url: str
    selftext: str
    permalink: str
    is_self: bool
    link_flair_text: str | None = None
    upvote_ratio: float = 0.0


class RedditAggregator:
    """
    Aggregates AI/ML discussions from Reddit

    Uses PRAW (Python Reddit API Wrapper) to access Reddit API.
    Supports:
    - Multi-subreddit monitoring
    - Time-based filtering (hot, new, top, rising)
    - Score/comment thresholds
    - Full post content extraction
    """

    def __init__(self, settings: RedditSettings | None = None):
        self.settings = settings or RedditSettings()

        # Initialize PRAW client
        self.reddit = praw.Reddit(client_id=self.settings.client_id, client_secret=self.settings.client_secret, user_agent=self.settings.user_agent)

        # Set read-only mode
        self.reddit.read_only = True

    def _submission_to_post(self, submission: Submission) -> RedditPost:
        """Convert PRAW Submission to RedditPost dataclass"""
        return RedditPost(
            post_id=submission.id,
            subreddit=submission.subreddit.display_name,
            title=submission.title,
            author=str(submission.author) if submission.author else "[deleted]",
            score=submission.score,
            num_comments=submission.num_comments,
            created_utc=datetime.fromtimestamp(submission.created_utc),
            url=submission.url,
            selftext=submission.selftext,
            permalink=f"https://reddit.com{submission.permalink}",
            is_self=submission.is_self,
            link_flair_text=submission.link_flair_text,
            upvote_ratio=submission.upvote_ratio,
        )

    async def get_hot_posts(self, subreddit: str, limit: int = 25) -> list[RedditPost]:
        """
        Get hot posts from a subreddit

        Args:
            subreddit: Subreddit name
            limit: Number of posts to retrieve

        Returns:
            List of RedditPost objects
        """
        try:
            sub = self.reddit.subreddit(subreddit)
            posts = []

            for submission in sub.hot(limit=limit):
                posts.append(self._submission_to_post(submission))

            logger.info(f"Retrieved {len(posts)} hot posts from r/{subreddit}")
            return posts

        except Exception as e:
            logger.error(f"Error fetching hot posts from r/{subreddit}: {e}", exc_info=True)
            return []

    async def get_new_posts(self, subreddit: str, limit: int = 25) -> list[RedditPost]:
        """
        Get new posts from a subreddit

        Args:
            subreddit: Subreddit name
            limit: Number of posts to retrieve

        Returns:
            List of RedditPost objects
        """
        try:
            sub = self.reddit.subreddit(subreddit)
            posts = []

            for submission in sub.new(limit=limit):
                posts.append(self._submission_to_post(submission))

            logger.info(f"Retrieved {len(posts)} new posts from r/{subreddit}")
            return posts

        except Exception as e:
            logger.error(f"Error fetching new posts from r/{subreddit}: {e}", exc_info=True)
            return []

    async def get_top_posts(self, subreddit: str, time_filter: str = "week", limit: int = 25) -> list[RedditPost]:
        """
        Get top posts from a subreddit

        Args:
            subreddit: Subreddit name
            time_filter: Time filter (hour, day, week, month, year, all)
            limit: Number of posts to retrieve

        Returns:
            List of RedditPost objects
        """
        try:
            sub = self.reddit.subreddit(subreddit)
            posts = []

            for submission in sub.top(time_filter=time_filter, limit=limit):
                posts.append(self._submission_to_post(submission))

            logger.info(f"Retrieved {len(posts)} top posts from r/{subreddit}")
            return posts

        except Exception as e:
            logger.error(f"Error fetching top posts from r/{subreddit}: {e}", exc_info=True)
            return []

    async def search_subreddit(self, subreddit: str, query: str, time_filter: str = "week", limit: int = 25) -> list[RedditPost]:
        """
        Search within a subreddit

        Args:
            subreddit: Subreddit name
            query: Search query
            time_filter: Time filter
            limit: Number of results

        Returns:
            List of RedditPost objects
        """
        try:
            sub = self.reddit.subreddit(subreddit)
            posts = []

            for submission in sub.search(query, time_filter=time_filter, limit=limit):
                posts.append(self._submission_to_post(submission))

            logger.info(f"Retrieved {len(posts)} search results from r/{subreddit} for query: {query}")
            return posts

        except Exception as e:
            logger.error(f"Error searching r/{subreddit}: {e}", exc_info=True)
            return []

    async def aggregate_from_multiple_subreddits(
        self, subreddits: list[str] | None = None, sort_by: str = "hot", limit_per_subreddit: int | None = None
    ) -> list[dict[str, Any]]:
        """
        Aggregate posts from multiple subreddits

        Args:
            subreddits: List of subreddit names
            sort_by: Sorting method (hot, new, top)
            limit_per_subreddit: Posts per subreddit

        Returns:
            List of post dictionaries
        """
        subreddits = subreddits or self.settings.subreddits
        limit = limit_per_subreddit or self.settings.posts_limit

        all_posts = []
        for subreddit in subreddits:
            if sort_by == "hot":
                posts = await self.get_hot_posts(subreddit, limit)
            elif sort_by == "new":
                posts = await self.get_new_posts(subreddit, limit)
            elif sort_by == "top":
                posts = await self.get_top_posts(subreddit, limit=limit)
            else:
                logger.warning(f"Unknown sort_by: {sort_by}, defaulting to hot")
                posts = await self.get_hot_posts(subreddit, limit)

            all_posts.extend(posts)

        # Convert to dictionaries
        results = []
        for post in all_posts:
            results.append(
                {
                    "post_id": post.post_id,
                    "subreddit": post.subreddit,
                    "title": post.title,
                    "author": post.author,
                    "score": post.score,
                    "num_comments": post.num_comments,
                    "created_utc": post.created_utc.isoformat(),
                    "url": post.url,
                    "selftext": post.selftext,
                    "permalink": post.permalink,
                    "is_self": post.is_self,
                    "link_flair_text": post.link_flair_text,
                    "upvote_ratio": post.upvote_ratio,
                }
            )

        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)

        logger.info(f"Aggregated {len(results)} posts from {len(subreddits)} subreddits")
        return results

    async def aggregate_ml_discussions(self, time_filter: str = "week", min_score: int = 10) -> list[dict[str, Any]]:
        """
        Aggregate ML-related discussions across configured subreddits

        Args:
            time_filter: Time filter for top posts
            min_score: Minimum score threshold

        Returns:
            List of post dictionaries filtered by score
        """
        posts = await self.aggregate_from_multiple_subreddits(sort_by="top", limit_per_subreddit=self.settings.posts_limit)

        # Filter by minimum score
        filtered_posts = [p for p in posts if p["score"] >= min_score]

        logger.info(f"Filtered to {len(filtered_posts)} posts with score >= {min_score}")
        return filtered_posts

    async def search_across_subreddits(
        self, query: str, subreddits: list[str] | None = None, time_filter: str = "week", limit_per_subreddit: int = 25
    ) -> list[dict[str, Any]]:
        """
        Search for a query across multiple subreddits

        Args:
            query: Search query
            subreddits: List of subreddit names
            time_filter: Time filter
            limit_per_subreddit: Results per subreddit

        Returns:
            List of post dictionaries
        """
        subreddits = subreddits or self.settings.subreddits

        all_posts = []
        for subreddit in subreddits:
            posts = await self.search_subreddit(subreddit=subreddit, query=query, time_filter=time_filter, limit=limit_per_subreddit)
            all_posts.extend(posts)

        # Convert to dictionaries and sort by score
        results = [
            {
                "post_id": p.post_id,
                "subreddit": p.subreddit,
                "title": p.title,
                "author": p.author,
                "score": p.score,
                "num_comments": p.num_comments,
                "created_utc": p.created_utc.isoformat(),
                "url": p.url,
                "selftext": p.selftext,
                "permalink": p.permalink,
                "is_self": p.is_self,
                "link_flair_text": p.link_flair_text,
                "upvote_ratio": p.upvote_ratio,
            }
            for p in all_posts
        ]

        results.sort(key=lambda x: x["score"], reverse=True)

        logger.info(f"Found {len(results)} posts across subreddits for query: {query}")
        return results


# Example usage
if __name__ == "__main__":
    import asyncio

    async def main():
        # Note: You need to set environment variables or pass credentials
        # REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET
        aggregator = RedditAggregator()

        # Get top ML posts
        posts = await aggregator.aggregate_ml_discussions(time_filter="week", min_score=10)
        print(f"\nFound {len(posts)} ML discussions from the last week")

        for post in posts[:5]:
            print(f"\nr/{post['subreddit']}: {post['title']}")
            print(f"Score: {post['score']} | Comments: {post['num_comments']}")
            print(f"URL: {post['permalink']}")

    asyncio.run(main())
