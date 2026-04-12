"""
PNKLN Core Stack - Reddit Source Adapter

Uses Reddit's public JSON API (no auth, free).
Append .json to any Reddit URL — no OAuth needed for read-only.
Rate limit: 1 req/sec unauthenticated, 60 req/min with OAuth.
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from datetime import datetime

import httpx
import structlog

from ingestion.classification.tier_classifier import IngestedItem
from ingestion.sources.base import SourceAdapter

logger = structlog.get_logger(__name__)

TARGET_SUBREDDITS = [
    "artificial",
    "MachineLearning",
    "LocalLLaMA",
    "ChatGPT",
    "startups",
    "technology",
    "investing",
    "StocksAndTrading",
    "cybersecurity",
    "netsec",
    "hacking",
    "singularity",
    "Futurology",
    "programming",
    "softwareengineering",
]

BASE = "https://www.reddit.com"
HEADERS = {"User-Agent": "PNKLN-IngestBot/1.0 (research; redacted@shadowtag-v4.local)"}


class RedditAdapter(SourceAdapter):
    """Free Reddit ingestion via public JSON API. No credentials needed."""

    def __init__(self, subreddits: list[str] | None = None, limit: int = 25) -> None:
        self.subreddits = subreddits or TARGET_SUBREDDITS
        self.limit = limit
        self.client = httpx.AsyncClient(headers=HEADERS, timeout=15, follow_redirects=True)

    async def authenticate(self) -> None:
        pass  # No auth for public read

    async def validate_credentials(self) -> bool:
        return True  # No credentials required

    def get_cost_estimate(self, num_items: int) -> float:
        return 0.0  # Free public API

    async def fetch_items(self) -> AsyncIterator[IngestedItem]:
        for sub in self.subreddits:
            for sort in ["hot", "top"]:
                url = f"{BASE}/r/{sub}/{sort}.json?limit={self.limit}"
                try:
                    resp = await self.client.get(url)
                    resp.raise_for_status()
                    posts = resp.json()["data"]["children"]
                    logger.info("reddit_fetched", sub=sub, sort=sort, count=len(posts))
                    for post in posts:
                        d = post["data"]
                        text = d.get("selftext", "") or d.get("title", "")
                        if len(text) < 50:
                            text = d.get("title", "")
                        yield IngestedItem(
                            id=f"reddit_{d['id']}",
                            source=f"reddit/r/{sub}",
                            title=d.get("title", "")[:200],
                            content=text[:8000],
                            url=f"https://reddit.com{d.get('permalink', '')}",
                            published_at=datetime.utcfromtimestamp(d.get("created_utc", 0)),
                            author=d.get("author"),
                            metadata={
                                "score": d.get("score", 0),
                                "comments": d.get("num_comments", 0),
                                "subreddit": sub,
                                "sort": sort,
                            },
                        )
                    await asyncio.sleep(1.0)
                except Exception as e:
                    logger.warning("reddit_fetch_failed", sub=sub, error=str(e))
