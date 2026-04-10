"""
PNKLN Core Stack - Dark Web / Onion Source Adapter

Routes requests through Tor (localhost:9050 SOCKS5).
Uses Scrapegraph-ai SmartScraperGraph for structured LLM extraction when
GEMINI_API_KEY is set; falls back to minimal HTML stripping otherwise.

Requirements:
  - Tor running locally: `brew install tor && tor`
  - pip install requests[socks] httpx[socks]

Legal note: Only indexes publicly accessible .onion OSINT/news sites.
"""

from __future__ import annotations

import asyncio
import os
import sys
from collections.abc import AsyncIterator
from datetime import datetime
from pathlib import Path

import httpx
import structlog

from ingestion.classification.tier_classifier import IngestedItem
from ingestion.sources.base import SourceAdapter

logger = structlog.get_logger(__name__)

TOR_PROXY = "socks5://127.0.0.1:9050"

# Scrapegraph-ai submodule path — used for LLM-structured extraction
_SCRAPEGRAPH_PATH = Path(__file__).parents[6] / "tools/external_sdks/scrapegraph-ai"
if _SCRAPEGRAPH_PATH.exists() and str(_SCRAPEGRAPH_PATH) not in sys.path:
    sys.path.insert(0, str(_SCRAPEGRAPH_PATH))

try:
    from scrapegraphai.graphs import SmartScraperGraph

    _HAS_SCRAPEGRAPH = True
except ImportError:
    _HAS_SCRAPEGRAPH = False

# Publicly accessible .onion OSINT/news sites (legal, open access)
ONION_SOURCES = [
    {
        "name": "ProPublica",
        "url": "https://www.propub3r6espa33w.onion/",
        "type": "news",
    },
    {
        "name": "BBC Tor Mirror",
        "url": "https://www.bbcnewsd73hkzno2ini43t4gblxvyceuapSystemInternals.onion/",
        "type": "news",
    },
    {
        "name": "DarknetLive (OSINT)",
        "url": "http://darknetlidvrsli6iso7my54rjayjursyw637aypb6qambkoepmyq2yd.onion/",
        "type": "osint",
    },
    {
        "name": "Tor Project",
        "url": "http://2gzyxa5ihm7nsggfxnu52rck2vv4rvmdlkiu3zzui5du4xyclen53wid.onion/",
        "type": "tech",
    },
]


class DarkWebAdapter(SourceAdapter):
    """
    Fetches from open .onion sites via Tor SOCKS5 proxy.
    Only targets publicly accessible OSINT/news sources.
    """

    def __init__(self, tor_proxy: str = TOR_PROXY) -> None:
        self.tor_proxy = tor_proxy
        self._client: httpx.AsyncClient | None = None

    async def validate_credentials(self) -> bool:
        try:
            await self.authenticate()
            return True
        except Exception:
            return False

    def get_cost_estimate(self, num_items: int) -> float:
        return 0.0

    async def authenticate(self) -> None:
        # Verify Tor is reachable
        try:
            async with httpx.AsyncClient(proxies=self.tor_proxy, timeout=30) as c:
                resp = await c.get("https://check.torproject.org/api/ip")
                data = resp.json()
                if data.get("IsTor"):
                    logger.info("darkweb_tor_connected", ip=data.get("IP"))
                else:
                    raise RuntimeError("Tor proxy responding but not routing through Tor")
        except Exception as e:
            raise RuntimeError(f"Tor not available at {self.tor_proxy}: {e}") from e

    def _extract_with_scrapegraph(self, html: str, url: str) -> str:
        """Use SmartScraperGraph to extract structured text from raw HTML."""
        gemini_key = os.environ.get("GEMINI_API_KEY")
        if not gemini_key:
            return ""
        try:
            graph = SmartScraperGraph(
                prompt="Extract the main article title and body text as plain prose. Return only the text content.",
                source=html,
                config={
                    "llm": {"api_key": gemini_key, "model": "gemini-2.0-flash"},
                    "verbose": False,
                },
            )
            result = graph.run()
            if isinstance(result, dict):
                return " ".join(str(v) for v in result.values() if v)
            return str(result)
        except Exception as e:
            logger.warning("darkweb_scrapegraph_failed", url=url, error=str(e))
            return ""

    @staticmethod
    def _strip_html(html: str) -> str:
        text = html
        for tag in ["<script", "<style", "<nav", "<footer", "<header"]:
            start = text.lower().find(tag)
            while start != -1:
                end = text.find(">", start) + 1
                text = text[:start] + text[end:]
                start = text.lower().find(tag)
        return " ".join(text.split())[:8000]

    async def fetch_items(self) -> AsyncIterator[IngestedItem]:
        use_llm = _HAS_SCRAPEGRAPH and bool(os.environ.get("GEMINI_API_KEY"))
        via = "scrapegraph+tor" if use_llm else "tor"
        async with httpx.AsyncClient(proxies=self.tor_proxy, timeout=60, verify=False) as client:
            for source in ONION_SOURCES:
                try:
                    logger.info("darkweb_fetch", name=source["name"], via=via)
                    resp = await client.get(source["url"])
                    resp.raise_for_status()
                    if use_llm:
                        text = await asyncio.get_event_loop().run_in_executor(
                            None, self._extract_with_scrapegraph, resp.text, source["url"]
                        )
                    if not use_llm or len(text) < 200:
                        text = self._strip_html(resp.text)
                    if len(text) < 200:
                        continue
                    yield IngestedItem(
                        id=f"darkweb_{source['name'].lower().replace(' ', '_')}",
                        source=f"darkweb/{source['type']}",
                        title=source["name"],
                        content=text[:8000],
                        url=source["url"],
                        published_at=datetime.utcnow(),
                        author=None,
                        metadata={"type": source["type"], "via": via},
                    )
                    await asyncio.sleep(2.0)
                except Exception as e:
                    logger.warning("darkweb_source_failed", name=source["name"], error=str(e))
