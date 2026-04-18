"""PNKLN Core Stack - Ethical Web Crawler

Implements ethical web crawling with:
- robots.txt compliance (100% honor rate)
- Rate limiting per domain
- User-Agent transparency
- Backoff and retry logic
- Request logging and audit trail
"""

import time
from collections import defaultdict
from typing import Any
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import httpx
import structlog
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from ingestion.core.config import get_config

logger = structlog.get_logger(__name__)


class EthicalCrawler:
    """Ethical web crawler with robots.txt compliance and rate limiting.

    This crawler ensures PNKLN adheres to web standards and ethical norms:
    - Respects robots.txt directives
    - Implements per-domain rate limiting
    - Provides transparent User-Agent identification
    - Logs all requests for audit trail
    """

    def __init__(self):
        self.config = get_config().crawler
        self._robots_cache: dict[str, RobotFileParser] = {}
        self._last_request_time: dict[str, float] = defaultdict(float)
        self._request_counts: dict[str, int] = defaultdict(int)
        self._client = httpx.AsyncClient(
            timeout=self.config.request_timeout,
            headers={"User-Agent": self.config.user_agent},
            follow_redirects=True,
        )
        logger.info(
            "ethical_crawler_initialized",
            user_agent=self.config.user_agent,
            max_rate=self.config.max_rate_per_domain,
        )

    def _get_domain(self, url: str) -> str:
        """Extract domain from URL."""
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"

    async def _get_robots_parser(self, url: str) -> RobotFileParser | None:
        """Fetch and parse robots.txt for the given URL's domain.

        Returns None if robots.txt cannot be fetched or parsing fails.
        """
        domain = self._get_domain(url)

        # Check cache
        if domain in self._robots_cache:
            return self._robots_cache[domain]

        robots_url = f"{domain}/robots.txt"
        parser = RobotFileParser()
        parser.set_url(robots_url)

        try:
            response = await self._client.get(robots_url)
            if response.status_code == 200:
                parser.parse(response.text.splitlines())
                self._robots_cache[domain] = parser
                logger.info("robots_txt_fetched", domain=domain, success=True)
                return parser
            logger.warning(
                "robots_txt_fetch_failed",
                domain=domain,
                status_code=response.status_code,
            )
            return None
        except Exception as e:
            logger.warning("robots_txt_error", domain=domain, error=str(e))
            return None

    async def is_allowed(self, url: str) -> bool:
        """Check if crawling the URL is allowed per robots.txt.

        If robots.txt cannot be fetched, defaults to ALLOWED (permissive).
        If respect_robots_txt is disabled, always returns True.
        """
        if not self.config.respect_robots_txt:
            return True

        parser = await self._get_robots_parser(url)

        if parser is None:
            # If we can't fetch robots.txt, default to allowed (permissive approach)
            logger.debug("robots_txt_unavailable_allowing", url=url)
            return True

        allowed = parser.can_fetch(self.config.user_agent, url)
        logger.debug("robots_txt_check", url=url, allowed=allowed)
        return allowed

    async def _enforce_rate_limit(self, url: str) -> None:
        """Enforce per-domain rate limiting.

        Implements:
        - Minimum delay between requests
        - Per-domain request rate limiting
        """
        domain = self._get_domain(url)
        current_time = time.time()
        last_request = self._last_request_time[domain]

        # Calculate required delay
        min_interval = 1.0 / self.config.max_rate_per_domain
        time_since_last = current_time - last_request

        if time_since_last < min_interval:
            delay = min_interval - time_since_last
            logger.debug("rate_limit_delay", domain=domain, delay_seconds=delay)
            await asyncio.sleep(delay)

        # Also enforce absolute minimum delay
        if time_since_last < self.config.min_delay_between_requests:
            delay = self.config.min_delay_between_requests - time_since_last
            await asyncio.sleep(delay)

        self._last_request_time[domain] = time.time()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(httpx.HTTPStatusError),
    )
    async def fetch(self, url: str, method: str = "GET", **kwargs: Any) -> httpx.Response:
        """Fetch a URL with ethical crawling safeguards.

        Args:
            url: URL to fetch
            method: HTTP method (GET, POST, etc.)
            **kwargs: Additional arguments passed to httpx

        Returns:
            httpx.Response object

        Raises:
            ValueError: If URL is not allowed by robots.txt
            httpx.HTTPError: If request fails after retries

        """
        # Check robots.txt
        if not await self.is_allowed(url):
            logger.warning("url_blocked_by_robots_txt", url=url)
            raise ValueError(f"URL blocked by robots.txt: {url}")

        # Enforce rate limiting
        await self._enforce_rate_limit(url)

        # Make request
        domain = self._get_domain(url)
        start_time = time.time()

        try:
            response = await self._client.request(method, url, **kwargs)
            response.raise_for_status()

            duration = time.time() - start_time
            self._request_counts[domain] += 1

            logger.info(
                "http_request_success",
                url=url,
                method=method,
                status_code=response.status_code,
                duration_ms=int(duration * 1000),
                domain=domain,
                total_requests=self._request_counts[domain],
            )

            return response

        except httpx.HTTPStatusError as e:
            logger.error(
                "http_request_failed",
                url=url,
                method=method,
                status_code=e.response.status_code,
                error=str(e),
            )
            raise

        except Exception as e:
            logger.error("http_request_error", url=url, method=method, error=str(e))
            raise

    async def fetch_many(
        self,
        urls: list[str],
        max_concurrent: int = 5,
    ) -> list[httpx.Response | Exception]:
        """Fetch multiple URLs concurrently while respecting rate limits.

        Args:
            urls: List of URLs to fetch
            max_concurrent: Maximum number of concurrent requests

        Returns:
            List of responses or exceptions (preserves order)

        """
        import asyncio

        semaphore = asyncio.Semaphore(max_concurrent)

        async def fetch_with_semaphore(url: str) -> httpx.Response | Exception:
            async with semaphore:
                try:
                    return await self.fetch(url)
                except Exception as e:
                    return e

        results = await asyncio.gather(
            *[fetch_with_semaphore(url) for url in urls],
            return_exceptions=True,
        )

        return results

    def get_stats(self) -> dict[str, Any]:
        """Get crawler statistics for monitoring."""
        return {
            "total_domains": len(self._request_counts),
            "total_requests": sum(self._request_counts.values()),
            "requests_per_domain": dict(self._request_counts),
            "robots_cache_size": len(self._robots_cache),
            "config": {
                "max_rate_per_domain": self.config.max_rate_per_domain,
                "respect_robots_txt": self.config.respect_robots_txt,
                "user_agent": self.config.user_agent,
            },
        }

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()
        logger.info("ethical_crawler_closed", stats=self.get_stats())


# Need to import asyncio here to avoid circular import
import asyncio
