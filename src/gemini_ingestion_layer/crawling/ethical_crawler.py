# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Ethical Crawler Implementation

Implements responsible web crawling with:
- robots.txt compliance (REP)
- Rate limiting
- Proper User-Agent identification
- Timeout management
- Transparent crawling practices

Aligned with PNKLN Core Stack 2025 ethical standards.
"""

import asyncio
import aiohttp
from typing import Any
from dataclasses import dataclass
from datetime import datetime, UTC
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

from .rate_limiter import DomainRateLimiter


@dataclass
class CrawlResult:
    """Result from a crawl operation"""

    url: str
    success: bool
    status_code: int | None = None
    content: str | None = None
    content_type: str | None = None
    headers: dict[str, str] | None = None
    error: str | None = None
    timestamp: datetime = None
    response_time_ms: float = 0.0

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(UTC)


class EthicalCrawler:
    """
    Ethical web crawler with robots.txt compliance and rate limiting.

    Follows web crawling best practices:
    - Respects robots.txt directives
    - Implements per-domain rate limiting
    - Uses identifiable User-Agent
    - Handles timeouts gracefully
    - Provides transparency about crawling purpose
    """

    def __init__(
        self,
        user_agent: str = "PNKLN-Gemini-Ingestion/0.1.0 (+https://pnkln.ai/bot)",
        respect_robots_txt: bool = True,
        default_rate_limit_rpm: int = 60,
        request_timeout_seconds: int = 30,
    ):
        """
        Initialize ethical crawler.

        Args:
            user_agent: User-Agent string for transparency
            respect_robots_txt: Whether to check robots.txt (default True)
            default_rate_limit_rpm: Default requests per minute per domain
            request_timeout_seconds: Timeout for HTTP requests
        """
        self.user_agent = user_agent
        self.respect_robots_txt = respect_robots_txt
        self.timeout = aiohttp.ClientTimeout(total=request_timeout_seconds)

        # Rate limiting
        self.rate_limiter = DomainRateLimiter(default_rpm=default_rate_limit_rpm)

        # robots.txt cache
        self.robots_cache: dict[str, RobotFileParser] = {}

        # Statistics
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "robots_blocked": 0,
            "rate_limited": 0,
            "timeouts": 0,
        }

    def _get_domain(self, url: str) -> str:
        """Extract domain from URL"""
        parsed = urlparse(url)
        return parsed.netloc

    async def _get_robots_parser(self, domain: str, session: aiohttp.ClientSession) -> RobotFileParser | None:
        """
        Get or fetch robots.txt parser for domain.

        Args:
            domain: Domain to check
            session: aiohttp client session

        Returns:
            RobotFileParser or None if unavailable
        """
        if not self.respect_robots_txt:
            return None

        if domain in self.robots_cache:
            return self.robots_cache[domain]

        # Fetch robots.txt
        robots_url = f"https://{domain}/robots.txt"
        parser = RobotFileParser()
        parser.set_url(robots_url)

        try:
            async with session.get(robots_url, timeout=self.timeout) as response:
                if response.status == 200:
                    content = await response.text()
                    # Parse robots.txt (RobotFileParser expects file-like object)
                    # We'll use a simple implementation for async
                    parser.parse(content.split("\n"))
                    self.robots_cache[domain] = parser
                    return parser
                else:
                    # If robots.txt not found, allow crawling
                    self.robots_cache[domain] = None
                    return None
        except Exception:
            # On error, be conservative and allow (but cache None)
            self.robots_cache[domain] = None
            return None

    async def _can_fetch(self, url: str, session: aiohttp.ClientSession) -> bool:
        """
        Check if URL can be fetched according to robots.txt.

        Args:
            url: URL to check
            session: aiohttp client session

        Returns:
            True if allowed, False if blocked
        """
        if not self.respect_robots_txt:
            return True

        domain = self._get_domain(url)
        parser = await self._get_robots_parser(domain, session)

        if parser is None:
            # No robots.txt or error fetching - allow
            return True

        # Check if our user agent can fetch this URL
        can_fetch = parser.can_fetch(self.user_agent, url)
        if not can_fetch:
            self.stats["robots_blocked"] += 1

        return can_fetch

    async def fetch(self, url: str, session: aiohttp.ClientSession | None = None, custom_headers: dict[str, str] | None = None) -> CrawlResult:
        """
        Fetch URL with ethical crawling practices.

        Args:
            url: URL to fetch
            session: Optional aiohttp session (will create if not provided)
            custom_headers: Optional custom headers to include

        Returns:
            CrawlResult with fetch outcome
        """
        self.stats["total_requests"] += 1
        start_time = asyncio.get_event_loop().time()

        # Prepare headers
        headers = {"User-Agent": self.user_agent}
        if custom_headers:
            headers.update(custom_headers)

        # Get domain for rate limiting
        domain = self._get_domain(url)

        # Create session if not provided
        close_session = False
        if session is None:
            session = aiohttp.ClientSession(timeout=self.timeout)
            close_session = True

        try:
            # Check robots.txt
            if not await self._can_fetch(url, session):
                return CrawlResult(url=url, success=False, error="Blocked by robots.txt")

            # Apply rate limiting
            await self.rate_limiter.acquire(domain)

            # Make request
            async with session.get(url, headers=headers) as response:
                content = await response.text()
                response_time = (asyncio.get_event_loop().time() - start_time) * 1000

                self.stats["successful_requests"] += 1

                return CrawlResult(
                    url=url,
                    success=True,
                    status_code=response.status,
                    content=content,
                    content_type=response.content_type,
                    headers=dict(response.headers),
                    response_time_ms=response_time,
                )

        except TimeoutError:
            self.stats["failed_requests"] += 1
            self.stats["timeouts"] += 1
            return CrawlResult(url=url, success=False, error="Request timeout")

        except Exception as e:
            self.stats["failed_requests"] += 1
            return CrawlResult(url=url, success=False, error=f"{type(e).__name__}: {str(e)}")

        finally:
            if close_session:
                await session.close()

    async def fetch_batch(self, urls: list[str], max_concurrent: int = 10) -> list[CrawlResult]:
        """
        Fetch multiple URLs concurrently with rate limiting.

        Args:
            urls: List of URLs to fetch
            max_concurrent: Maximum concurrent requests

        Returns:
            List of CrawlResults
        """
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            semaphore = asyncio.Semaphore(max_concurrent)

            async def fetch_with_semaphore(url: str) -> CrawlResult:
                async with semaphore:
                    return await self.fetch(url, session=session)

            tasks = [fetch_with_semaphore(url) for url in urls]
            return await asyncio.gather(*tasks)

    def get_stats(self) -> dict[str, Any]:
        """Get crawler statistics"""
        rate_limiter_stats = self.rate_limiter.get_all_stats()

        return {"crawler_stats": self.stats, "rate_limiter_stats": rate_limiter_stats, "robots_cache_size": len(self.robots_cache)}

    def configure_domain_rate_limit(self, domain: str, rpm: int) -> None:
        """
        Configure custom rate limit for specific domain.

        Args:
            domain: Domain name
            rpm: Requests per minute
        """
        self.rate_limiter.configure_domain(domain, rpm)
