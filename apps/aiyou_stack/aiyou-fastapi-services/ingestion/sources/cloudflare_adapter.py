"""
PNKLN Core Stack - Cloudflare Bypass Adapter

Wraps cloudscraper (VeNoMouS/cloudscraper) as the default HTTP client
for any source protected by Cloudflare JS challenges.

Used by: Anna's Archive, LinkedIn scraping, and other CF-protected targets.

Install: pip install cloudscraper
Or use bundled: tools/external_sdks/cloudscraper/
"""

from __future__ import annotations

import sys
from pathlib import Path

import structlog

logger = structlog.get_logger(__name__)

# Prefer bundled cloudscraper over system-installed
_BUNDLED = Path(__file__).parents[6] / "tools/external_sdks/cloudscraper"
if _BUNDLED.exists() and str(_BUNDLED) not in sys.path:
    sys.path.insert(0, str(_BUNDLED))

try:
    import cloudscraper  # type: ignore[import]

    _HAS_CLOUDSCRAPER = True
except ImportError:
    _HAS_CLOUDSCRAPER = False
    logger.warning("cloudscraper_not_available", hint="pip install cloudscraper")


def get_scraper(browser: str = "chrome", platform: str = "darwin") -> cloudscraper.CloudScraper:
    """Return a configured CloudScraper session."""
    if not _HAS_CLOUDSCRAPER:
        raise ImportError("cloudscraper not installed. Run: pip install cloudscraper")
    scraper = cloudscraper.create_scraper(
        browser={"browser": browser, "platform": platform, "mobile": False}
    )
    return scraper


def cf_get(url: str, **kwargs) -> str:
    """Simple one-shot GET through Cloudflare bypass. Returns response text."""
    scraper = get_scraper()
    resp = scraper.get(url, timeout=30, **kwargs)
    resp.raise_for_status()
    return resp.text


# ── Anna's Archive adapter ────────────────────────────────────────────────────

ANNAS_SEARCH = "https://annas-archive.org/search?q={query}&ext=pdf&lang=en"


def search_annas_archive(query: str, max_results: int = 10) -> list[dict]:
    """
    Search Anna's Archive for academic/technical PDFs.
    Returns list of {title, url, author, year} dicts.
    """
    from bs4 import BeautifulSoup

    url = ANNAS_SEARCH.format(query=query.replace(" ", "+"))
    logger.info("annas_archive_search", query=query)
    try:
        html = cf_get(url)
        soup = BeautifulSoup(html, "html.parser")
        results = []
        for item in soup.select("div.h-[125px]")[:max_results]:
            title_el = item.select_one("h3")
            link_el = item.select_one("a[href]")
            meta_el = item.select_one("div.text-sm")
            results.append(
                {
                    "title": title_el.get_text(strip=True) if title_el else "",
                    "url": "https://annas-archive.org" + link_el["href"] if link_el else "",
                    "meta": meta_el.get_text(strip=True) if meta_el else "",
                }
            )
        logger.info("annas_archive_results", count=len(results))
        return results
    except Exception as e:
        logger.error("annas_archive_failed", error=str(e))
        return []
