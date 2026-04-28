# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""PNKLN Core Stack - LinkedIn Source Adapter

Uses Scrapling StealthyFetcher (Playwright + fingerprint spoofing) as primary,
falls back to cloudscraper on import failure.
Targets public company pages and public post feeds only.

Limitations:
  - LinkedIn aggressively blocks scrapers; sessions may get challenged.
  - Rate limit: 1 req / 5 s, max 10 pages per run.
  - Auth: Optional LI_AT_COOKIE env var for session cookies (improves reliability).

Legal note: Only public profile data. No private message or connection data.
"""

from __future__ import annotations

import asyncio
import os
import sys
from collections.abc import AsyncIterator
from datetime import datetime
from pathlib import Path

import structlog

from ingestion.classification.tier_classifier import IngestedItem
from ingestion.sources.base import SourceAdapter

logger = structlog.get_logger(__name__)

# Scrapling submodule path
_SCRAPLING_PATH = Path(__file__).parents[6] / "tools/external_sdks/scrapling"
if _SCRAPLING_PATH.exists() and str(_SCRAPLING_PATH) not in sys.path:
    sys.path.insert(0, str(_SCRAPLING_PATH))

try:
    from scrapling.fetchers import StealthyFetcher

    _HAS_SCRAPLING = True
except ImportError:
    _HAS_SCRAPLING = False

# Public company pages to monitor
TARGET_COMPANIES = [
    "openai",
    "anthropic",
    "deepmind",
    "meta",
    "microsoft",
    "nvidia",
    "google",
    "hugging-face",
    "tesla-motors",
    "mistral-ai",
]

RATE_DELAY = 5.0
BASE = "https://www.linkedin.com"


class LinkedInAdapter(SourceAdapter):
    """LinkedIn public page scraper.
    Primary: Scrapling StealthyFetcher (Playwright + fingerprint spoofing).
    Fallback: cloudscraper (Cloudflare JS challenge bypass).
    """

    def __init__(self, companies: list[str] | None = None) -> None:
        self.companies = companies or TARGET_COMPANIES
        self._scraper = None  # cloudscraper fallback handle

    def _get_fallback_scraper(self):
        if self._scraper is None:
            from ingestion.sources.cloudflare_adapter import get_scraper

            self._scraper = get_scraper()
            li_at = os.environ.get("LI_AT_COOKIE")
            if li_at:
                self._scraper.cookies.set("li_at", li_at, domain=".linkedin.com")
                logger.info("linkedin_session_cookie_injected")
        return self._scraper

    async def authenticate(self) -> None:
        url = f"{BASE}/company/openai/"
        if _HAS_SCRAPLING:
            page = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: StealthyFetcher.fetch(url, headless=True, network_idle=True),
            )
            if page and page.status < 400:
                logger.info("linkedin_scrapling_reachable", status=page.status)
                return
        # cloudscraper fallback
        loop = asyncio.get_event_loop()
        scraper = self._get_fallback_scraper()
        resp = await loop.run_in_executor(None, lambda: scraper.get(url, timeout=20))
        if resp.status_code >= 400:
            raise RuntimeError(f"LinkedIn blocked via fallback scraper: {resp.status_code}")
        logger.info("linkedin_fallback_reachable", status=resp.status_code)

    def _sync_fetch_scrapling(self, company: str) -> list[dict]:
        """Fetch via Scrapling StealthyFetcher — JS-rendered, fingerprint-safe."""
        url = f"{BASE}/company/{company}/posts/?feedView=all"
        try:
            page = StealthyFetcher.fetch(url, headless=True, network_idle=True)
            posts = []
            for el in page.css("div.feed-shared-update-v2")[:10]:
                text_el = el.css_first("div.feed-shared-text span[dir='ltr']")
                if not text_el:
                    continue
                text = text_el.clean_text
                if not text or len(text) < 40:
                    continue
                link_el = el.css_first("a.app-aware-link[href*='/posts/']")
                post_url = (
                    link_el.attrib.get("href", "").split("?")[0]
                    if link_el
                    else f"{BASE}/company/{company}/"
                )
                posts.append({"text": text, "url": post_url})
            return posts
        except Exception as e:
            logger.warning("linkedin_scrapling_failed", company=company, error=str(e))
            return []

    def _sync_fetch_fallback(self, company: str) -> list[dict]:
        """Fetch via cloudscraper — Cloudflare JS bypass, no JS rendering."""
        from bs4 import BeautifulSoup

        scraper = self._get_fallback_scraper()
        url = f"{BASE}/company/{company}/posts/?feedView=all"
        try:
            resp = scraper.get(url, timeout=30)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            posts = []
            for article in soup.select("div.feed-shared-update-v2")[:10]:
                text_el = article.select_one("div.feed-shared-text span[dir='ltr']")
                if not text_el:
                    continue
                text = text_el.get_text(separator=" ", strip=True)
                if len(text) < 40:
                    continue
                link_el = article.select_one("a.app-aware-link[href*='/posts/']")
                post_url = (
                    link_el["href"].split("?")[0] if link_el else f"{BASE}/company/{company}/"
                )
                posts.append({"text": text, "url": post_url})
            return posts
        except Exception as e:
            logger.warning("linkedin_fallback_failed", company=company, error=str(e))
            return []

    async def fetch_items(self) -> AsyncIterator[IngestedItem]:  # type: ignore[override]
        loop = asyncio.get_event_loop()
        via = "scrapling" if _HAS_SCRAPLING else "cloudscraper"
        fetch_fn = self._sync_fetch_scrapling if _HAS_SCRAPLING else self._sync_fetch_fallback
        for company in self.companies:
            posts = await loop.run_in_executor(None, fetch_fn, company)
            logger.info("linkedin_fetched", company=company, count=len(posts), via=via)
            for p in posts:
                yield IngestedItem(
                    id=f"li_{company}_{hash(p['url'])}",
                    source=f"linkedin/{company}",
                    title=p["text"][:120],
                    content=p["text"][:8000],
                    url=p["url"],
                    published_at=datetime.utcnow(),
                    author=company,
                    metadata={"company": company, "via": via},
                )
            await asyncio.sleep(RATE_DELAY)

    # ── SourceAdapter ABC ──────────────────────────────────────────────────────

    async def validate_credentials(self) -> bool:
        try:
            await self.authenticate()
            return True
        except Exception:
            return False

    def get_cost_estimate(self, num_items: int) -> float:
        return 0.0  # Free via Scrapling / cloudscraper
