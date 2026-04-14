"""PNKLN Core Stack - 4chan Source Adapter

Uses the official 4chan JSON API (no auth, no cost).
Targets boards relevant to AI, tech, business, security intel.
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

# Boards to monitor — add/remove as needed
TARGET_BOARDS = [
    "g",  # Technology
    "biz",  # Business & Finance
    "sci",  # Science & Math
    "pol",  # News & Political Discussion (signal extraction)
    "x",  # Paranormal (dark patterns, adversarial signal)
]

BASE = "https://a.4cdn.org"
RATE_DELAY = 1.0  # 4chan ToS: 1 req/sec max


class FourChanAdapter(SourceAdapter):
    """Ingests 4chan threads via official JSON API.
    Free, no credentials required. Rate-limited to 1 req/sec per ToS.
    """

    def __init__(self, boards: list[str] | None = None) -> None:
        self.boards = boards or TARGET_BOARDS
        self.client = httpx.AsyncClient(timeout=15)

    async def authenticate(self) -> None:
        pass  # No auth needed

    async def validate_credentials(self) -> bool:
        return True

    def get_cost_estimate(self, num_items: int) -> float:
        return 0.0

    async def fetch_catalog(self, board: str) -> list[dict]:
        url = f"{BASE}/{board}/catalog.json"
        resp = await self.client.get(url)
        resp.raise_for_status()
        threads = []
        for page in resp.json():
            threads.extend(page.get("threads", []))
        return threads

    async def fetch_thread(self, board: str, thread_no: int) -> list[dict]:
        url = f"{BASE}/{board}/thread/{thread_no}.json"
        try:
            resp = await self.client.get(url)
            resp.raise_for_status()
            return resp.json().get("posts", [])
        except Exception as e:
            logger.warning(
                "fourchan_thread_fetch_failed", board=board, thread=thread_no, error=str(e),
            )
            return []

    async def fetch_items(self) -> AsyncIterator[IngestedItem]:
        for board in self.boards:
            logger.info("fourchan_board_start", board=board)
            try:
                threads = await self.fetch_catalog(board)
                logger.info("fourchan_threads_found", board=board, count=len(threads))
                for thread in threads[:50]:  # Top 50 threads per board
                    thread_no = thread.get("no")
                    subject = thread.get("sub", "") or thread.get("com", "")[:80]
                    posts = await self.fetch_thread(board, thread_no)
                    text = "\n".join(
                        p.get("com", "").replace("<br>", "\n").replace("<wbr>", "")
                        for p in posts
                        if p.get("com")
                    )
                    if len(text) < 100:
                        continue
                    yield IngestedItem(
                        id=f"4chan_{board}_{thread_no}",
                        source=f"4chan/{board}",
                        title=subject[:200],
                        content=text[:8000],
                        url=f"https://boards.4chan.org/{board}/thread/{thread_no}",
                        published_at=datetime.utcfromtimestamp(thread.get("time", 0)),
                        author=None,
                        metadata={"board": board, "replies": thread.get("replies", 0)},
                    )
                    await asyncio.sleep(RATE_DELAY)
            except Exception as e:
                logger.error("fourchan_board_failed", board=board, error=str(e))
