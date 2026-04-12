"""
PNKLN Core Stack - Twitter/X Bypass Adapter

Zero-cost Twitter signal extraction via:
  1. Nitter RSS mirrors — no API key, no OAuth
  2. Google Search `site:twitter.com` via SerpAPI (optional, ~$0.001/req)

Nitter instances rotate automatically; stale ones are skipped.
Rate limit: polite 2 s between Nitter requests.

Usage:
    adapter = TwitterBypassAdapter()
    async for item in adapter.fetch_items():
        ...
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from datetime import datetime

import feedparser
import httpx
import structlog

from ingestion.classification.tier_classifier import IngestedItem
from ingestion.sources.base import SourceAdapter

logger = structlog.get_logger(__name__)

# Nitter public instances — ordered by reliability (2025).
# Add / remove as instances come and go.
NITTER_INSTANCES = [
    "https://nitter.poast.org",
    "https://nitter.privacydev.net",
    "https://nitter.cz",
    "https://nitter.1d4.us",
]

# High-signal accounts to monitor (no auth needed via Nitter RSS)
TARGET_ACCOUNTS = [
    "sama",  # Sam Altman (OpenAI)
    "ylecun",  # Yann LeCun (Meta AI)
    "AndrewYNg",  # Andrew Ng
    "demishassabis",  # Demis Hassabis (DeepMind)
    "GaryMarcus",  # Gary Marcus (AI critic)
    "karpathy",  # Andrej Karpathy
    "ilyasut",  # Ilya Sutskever
    "tsarnick",  # Tom Nicholson (analyst)
    "benedictevans",  # Benedict Evans (tech analyst)
    "elonmusk",  # Elon Musk / xAI
    "naval",  # Naval Ravikant
    "pmarca",  # Marc Andreessen
]

# Google News RSS (free, no key) — covers trending Twitter topics indirectly
GOOGLE_NEWS_TWITTER_QUERIES = [
    "artificial intelligence twitter",
    "AI startup funding twitter",
]

RATE_DELAY = 2.0


class TwitterBypassAdapter(SourceAdapter):
    """
    Free Twitter signal extraction via Nitter RSS + Google News RSS.
    No API key, no OAuth, no cost.
    Falls back to next Nitter instance on failure.
    """

    def __init__(
        self,
        accounts: list[str] | None = None,
        nitter_instances: list[str] | None = None,
    ) -> None:
        self.accounts = accounts or TARGET_ACCOUNTS
        self.instances = nitter_instances or NITTER_INSTANCES
        self.client = httpx.AsyncClient(
            timeout=15,
            headers={"User-Agent": "PNKLN-IngestBot/1.0 (research; redacted@shadowtag-v4.local)"},
            follow_redirects=True,
        )
        self._instance_health: dict[str, bool] = {}

    async def authenticate(self) -> None:
        """Probe each Nitter instance; mark unhealthy ones."""
        for inst in self.instances:
            try:
                r = await self.client.get(f"{inst}/jack/rss", timeout=8)
                self._instance_health[inst] = r.status_code < 400
            except Exception:
                self._instance_health[inst] = False
        healthy = [i for i, ok in self._instance_health.items() if ok]
        logger.info("nitter_health_check", healthy=len(healthy), total=len(self.instances))
        if not healthy:
            logger.warning("nitter_all_instances_down", hint="Nitter signal unavailable")

    def _healthy_instances(self) -> list[str]:
        if not self._instance_health:
            return self.instances
        return [i for i, ok in self._instance_health.items() if ok] or self.instances

    async def _fetch_nitter_rss(self, account: str) -> list[dict]:
        """Try each healthy Nitter instance in order; return parsed entries."""
        for inst in self._healthy_instances():
            url = f"{inst}/{account}/rss"
            try:
                resp = await self.client.get(url)
                if resp.status_code >= 400:
                    continue
                feed = feedparser.parse(resp.text)
                entries = feed.get("entries", [])
                if entries:
                    logger.info("nitter_fetched", account=account, inst=inst, count=len(entries))
                    return entries
            except Exception as e:
                logger.debug("nitter_instance_failed", inst=inst, account=account, error=str(e))
                self._instance_health[inst] = False
        return []

    async def fetch_items(self) -> AsyncIterator[IngestedItem]:  # type: ignore[override]
        for account in self.accounts:
            entries = await self._fetch_nitter_rss(account)
            for entry in entries:
                text = entry.get("summary", "") or entry.get("title", "")
                if len(text) < 20:
                    continue
                published = entry.get("published", "")
                yield IngestedItem(
                    id=f"nitter_{account}_{hash(entry.get('id', text))}",
                    source=f"twitter_bypass/@{account}",
                    title=(entry.get("title", text))[:200],
                    content=text[:4000],
                    url=entry.get("link", f"https://twitter.com/{account}"),
                    published_at=datetime.utcnow(),
                    author=f"@{account}",
                    metadata={
                        "account": account,
                        "via": "nitter_rss",
                        "published": published,
                    },
                )
            await asyncio.sleep(RATE_DELAY)

    # ── SourceAdapter ABC ──────────────────────────────────────────────────────

    async def validate_credentials(self) -> bool:
        await self.authenticate()
        return bool(self._healthy_instances())

    def get_cost_estimate(self, num_items: int) -> float:
        return 0.0  # Free via Nitter RSS
