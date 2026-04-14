"""PNKLN Core Stack - Instagram Source Adapter

Uses instagrapi (unofficial Instagram private API client).
No official API key required; uses session cookies.

Install: pip install instagrapi
Auth: Provide IG_USERNAME + IG_PASSWORD in env, or supply a saved session JSON.

Rate limits: Conservative — 1 req / 3 s, max 20 profiles per run.
Legal note: Scrapes public profiles only. Follow Instagram ToS re: automation.
"""

from __future__ import annotations

import asyncio
import os
from collections.abc import AsyncIterator
from datetime import datetime

import structlog

from ingestion.classification.tier_classifier import IngestedItem
from ingestion.sources.base import SourceAdapter

logger = structlog.get_logger(__name__)

# Public AI / tech accounts to monitor
TARGET_ACCOUNTS = [
    "openai",
    "anthropic_ai",
    "deepmind",
    "meta_ai",
    "nvidia",
    "huggingface",
    "googleai",
    "microsoft",
    "tesla",
]

RATE_DELAY = 3.0
MAX_POSTS_PER_ACCOUNT = 12


class InstagramAdapter(SourceAdapter):
    """Instagram ingestion via instagrapi (unofficial private API).
    Targets public tech/AI profiles only.
    Requires IG_USERNAME + IG_PASSWORD [VAPORIZED_PWD] variables.
    """

    def __init__(
        self,
        accounts: list[str] | None = None,
        session_json_path: str | None = None,
    ) -> None:
        self.accounts = accounts or TARGET_ACCOUNTS
        self.session_path = session_json_path or os.environ.get("IG_SESSION_PATH")
        self._cl: instagrapi.Client | None = None  # type: ignore[name-defined]

    def _get_client(self) -> instagrapi.Client:  # type: ignore[name-defined]
        try:
            import instagrapi  # type: ignore[import]
        except ImportError as exc:
            raise ImportError("pip install instagrapi") from exc
        return instagrapi.Client()

    async def authenticate(self) -> None:
        """Log into Instagram (sync call wrapped in executor)."""
        import asyncio

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._sync_login)

    def _sync_login(self) -> None:
        cl = self._get_client()
        if self.session_path and os.path.exists(self.session_path):
            cl.load_settings(self.session_path)
            cl.login(
                os.environ.get("IG_USERNAME", ""),
                os.environ.get("IG_PASSWORD", ""),
            )
            logger.info("instagram_session_loaded", path=self.session_path)
        else:
            username = os.environ.get("IG_USERNAME")
            password = os.environ.get("IG_PASSWORD")
            if not username or not password:
                raise RuntimeError("IG_USERNAME and IG_PASSWORD env vars required")
            cl.login(username, password)
            if self.session_path:
                cl.dump_settings(self.session_path)
            logger.info("instagram_logged_in", user=username)
        self._cl = cl

    def _sync_fetch_account(self, account: str) -> list[dict]:
        if self._cl is None:
            raise RuntimeError("Not authenticated — call authenticate() first")
        try:
            user_id = self._cl.user_id_from_username(account)
            medias = self._cl.user_medias(user_id, amount=MAX_POSTS_PER_ACCOUNT)
            results = []
            for m in medias:
                caption = (m.caption_text or "").strip()
                if len(caption) < 20:
                    continue
                results.append(
                    {
                        "id": str(m.pk),
                        "caption": caption,
                        "url": f"https://www.instagram.com/p/{m.code}/",
                        "like_count": m.like_count or 0,
                        "comment_count": m.comment_count or 0,
                        "taken_at": str(m.taken_at),
                    },
                )
            return results
        except Exception as e:
            logger.warning("instagram_account_failed", account=account, error=str(e))
            return []

    async def fetch_items(self) -> AsyncIterator[IngestedItem]:  # type: ignore[override]
        if self._cl is None:
            await self.authenticate()

        loop = asyncio.get_event_loop()
        for account in self.accounts:
            posts = await loop.run_in_executor(None, self._sync_fetch_account, account)
            logger.info("instagram_fetched", account=account, count=len(posts))
            for p in posts:
                yield IngestedItem(
                    id=f"ig_{p['id']}",
                    source=f"instagram/@{account}",
                    title=p["caption"][:120],
                    content=p["caption"][:8000],
                    url=p["url"],
                    published_at=datetime.utcnow(),
                    author=f"@{account}",
                    metadata={
                        "account": account,
                        "like_count": p["like_count"],
                        "comment_count": p["comment_count"],
                        "taken_at": p["taken_at"],
                    },
                )
            await asyncio.sleep(RATE_DELAY)

    # ── SourceAdapter ABC ──────────────────────────────────────────────────────

    async def validate_credentials(self) -> bool:
        try:
            await self.authenticate()
            return self._cl is not None
        except Exception as e:
            logger.error("instagram_auth_failed", error=str(e))
            return False

    def get_cost_estimate(self, num_items: int) -> float:
        return 0.0  # Free via unofficial API
