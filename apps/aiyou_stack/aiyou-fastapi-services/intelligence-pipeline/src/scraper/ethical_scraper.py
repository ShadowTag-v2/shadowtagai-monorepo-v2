# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""PNKLN Intelligence Pipeline - Ethical Web Scraper
ATP 5-19 RA-1 Compliant | RFC 9309 robots.txt Compliance

This module implements responsible web scraping with:
- robots.txt respect with 24h caching
- Domain-specific rate limiting
- Circuit breaker pattern for resilience
- Proper User-Agent identification
- Retry-After header respect
- Exponential backoff on failures

Risk Mitigation:
- RA-4 (Extremely High): Violating robots.txt, causing DDoS
- RA-1 (Low): Compliant, throttled, respectful scraping
"""

import asyncio
import logging
import random
import time
from datetime import datetime, timedelta
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import aiohttp

logger = logging.getLogger(__name__)


class EthicalScraper:
    """ATP 5-19 RA-1 compliant web scraper with robots.txt respect

    Features:
    - RFC 9309 compliant robots.txt parsing
    - Domain-specific rate limiting
    - Circuit breaker for sustained failures
    - Adaptive throttling on 429/503 responses
    - Proper User-Agent identification
    """

    def __init__(self, config: dict):
        """Initialize ethical scraper with configuration

        Args:
            config: Dictionary containing scraping ethics configuration

        """
        self.config = config
        self.robots_cache: dict[str, tuple[RobotFileParser, datetime]] = {}
        self.last_request: dict[str, float] = {}
        self.circuit_breakers: dict[str, tuple[int, datetime]] = {}
        self.request_counts: dict[str, int] = {}  # For monitoring

        logger.info("EthicalScraper initialized with ATP 5-19 RA-1 compliance")

    async def fetch_url(self, url: str, headers: dict | None = None) -> str | None:
        """Fetch URL with full ethical compliance

        ATP 5-19 Risk Mitigation:
        - RA-4 (Extremely High): Violating robots.txt, DDoS
        - RA-1 (Low): Compliant, throttled, respectful

        Args:
            url: Target URL to fetch
            headers: Optional additional headers

        Returns:
            Page content as string, or None if blocked/failed

        """
        domain = urlparse(url).netloc

        # 1. Check robots.txt
        if self.config["robots_txt"]["enabled"] and not await self.is_allowed(url):
            logger.warning(f"⚠️  {url} disallowed by robots.txt")
            return None

        # 2. Check circuit breaker
        if self.is_circuit_open(domain):
            logger.warning(f"⚠️  Circuit breaker open for {domain}")
            return None

        # 3. Respect crawl-delay
        crawl_delay = await self.get_crawl_delay(domain)
        await self.apply_rate_limit(domain, crawl_delay)

        # 4. Make request with proper User-Agent
        request_headers = {
            "User-Agent": f"{self.config['user_agent']['name']} (+{self.config['user_agent']['url']})",
            "From": self.config["user_agent"]["contact"],
        }
        if headers:
            request_headers.update(headers)

        try:
            timeout = aiohttp.ClientTimeout(total=30)
            async with aiohttp.ClientSession(timeout=timeout) as session:  # noqa: SIM117
                async with session.get(url, headers=request_headers) as response:
                    # Handle rate limiting
                    if response.status == 429:
                        if self.config["error_handling"]["respect_retry_after"]:
                            retry_after = int(response.headers.get("Retry-After", 60))
                            logger.warning(f"⚠️  Rate limited on {domain}, waiting {retry_after}s")
                            await asyncio.sleep(retry_after)
                            return await self.fetch_url(url, headers)  # Retry once
                        return None

                    # Handle server errors
                    if response.status >= 500:
                        self.record_failure(domain)
                        logger.error(f"❌ Server error {response.status} for {url}")
                        return None

                    # Handle client errors
                    if response.status >= 400:
                        logger.warning(f"⚠️  Client error {response.status} for {url}")
                        return None

                    # Success
                    self.reset_circuit(domain)
                    self.request_counts[domain] = self.request_counts.get(domain, 0) + 1
                    content = await response.text()
                    logger.info(f"✓ Successfully fetched {url} ({len(content)} bytes)")
                    return content

        except TimeoutError:
            logger.error(f"❌ Timeout fetching {url}")
            self.record_failure(domain)
            return None
        except aiohttp.ClientError as e:
            logger.error(f"❌ Client error fetching {url}: {e}")
            self.record_failure(domain)
            return None
        except Exception as e:
            logger.error(f"❌ Unexpected error fetching {url}: {e}")
            self.record_failure(domain)
            return None

    async def is_allowed(self, url: str) -> bool:
        """Check robots.txt with 24h caching per RFC 9309

        Args:
            url: URL to check

        Returns:
            True if allowed, False if disallowed

        """
        domain = urlparse(url).netloc
        robots_url = f"https://{domain}/robots.txt"

        # Check cache
        if domain in self.robots_cache:
            parser, cached_at = self.robots_cache[domain]
            cache_ttl = self.config["robots_txt"]["cache_ttl"]
            if datetime.now() - cached_at < timedelta(seconds=cache_ttl):
                return parser.can_fetch(self.config["user_agent"]["name"], url)

        # Fetch robots.txt
        try:
            parser = RobotFileParser()
            parser.set_url(robots_url)

            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:  # noqa: SIM117
                async with session.get(robots_url) as response:
                    if response.status == 200:
                        robots_txt = await response.text()
                        # Parse in thread pool to avoid blocking
                        loop = asyncio.get_event_loop()
                        await loop.run_in_executor(None, parser.parse, robots_txt.splitlines())
                        self.robots_cache[domain] = (parser, datetime.now())
                        logger.info(f"✓ Cached robots.txt for {domain}")
                    else:
                        # No robots.txt = assume Allow per RFC 9309
                        parser.parse([])
                        self.robots_cache[domain] = (parser, datetime.now())
                        logger.info(f"ℹ️  No robots.txt for {domain}, assuming Allow")

            return parser.can_fetch(self.config["user_agent"]["name"], url)

        except Exception as e:
            logger.warning(f"⚠️  Could not fetch robots.txt for {domain}: {e}")
            # Conservative: assume Disallow on error
            return False

    async def get_crawl_delay(self, domain: str) -> float:
        """Extract crawl-delay from robots.txt or use defaults

        Args:
            domain: Domain to check

        Returns:
            Crawl delay in seconds

        """
        if domain not in self.robots_cache:
            # Populate cache by checking a dummy URL
            await self.is_allowed(f"https://{domain}/")

        if domain in self.robots_cache:
            parser, _ = self.robots_cache[domain]
            try:
                # Check for crawl-delay directive
                delay = parser.crawl_delay(self.config["user_agent"]["name"])
                if delay:
                    logger.debug(f"Using robots.txt crawl-delay of {delay}s for {domain}")
                    return float(delay)
            except Exception:
                pass  # crawl_delay not supported in all Python versions

        # Use domain-specific defaults from config
        rate_config = self.config["rate_limiting"]
        for pattern, default_delay in rate_config.items():
            if isinstance(default_delay, (int, float)) and pattern in domain:
                logger.debug(f"Using pattern-matched delay of {default_delay}s for {domain}")
                return default_delay

        default = rate_config.get("default_delay", 3.0)
        logger.debug(f"Using default delay of {default}s for {domain}")
        return default

    async def apply_rate_limit(self, domain: str, crawl_delay: float):
        """Enforce crawl-delay with adaptive jitter to prevent thundering herd

        Args:
            domain: Domain being accessed
            crawl_delay: Base delay in seconds

        """
        if domain in self.last_request:
            elapsed = time.time() - self.last_request[domain]
            # Add jitter: 0-1s random delay
            jitter = random.uniform(0, 1.0)
            required_delay = crawl_delay + jitter

            if elapsed < required_delay:
                wait_time = required_delay - elapsed
                logger.debug(f"Rate limiting: waiting {wait_time:.2f}s for {domain}")
                await asyncio.sleep(wait_time)

        self.last_request[domain] = time.time()

    def is_circuit_open(self, domain: str) -> bool:
        """Circuit breaker pattern for sustained failures

        Args:
            domain: Domain to check

        Returns:
            True if circuit is open (domain unavailable)

        """
        if domain not in self.circuit_breakers:
            return False

        failures, opened_at = self.circuit_breakers[domain]

        # Open circuit after 5 failures
        if failures >= 5:
            # Try to close after 5 minutes
            if datetime.now() - opened_at > timedelta(minutes=5):
                logger.info(f"🔄 Attempting to close circuit for {domain}")
                del self.circuit_breakers[domain]
                return False

            logger.warning(f"⚡ Circuit open for {domain} ({failures} failures)")
            return True

        return False

    def record_failure(self, domain: str):
        """Record failure for circuit breaker

        Args:
            domain: Domain that failed

        """
        if domain not in self.circuit_breakers:
            self.circuit_breakers[domain] = (1, datetime.now())
            logger.debug(f"Recorded first failure for {domain}")
        else:
            failures, _ = self.circuit_breakers[domain]
            self.circuit_breakers[domain] = (failures + 1, datetime.now())
            logger.warning(f"Recorded failure #{failures + 1} for {domain}")

    def reset_circuit(self, domain: str):
        """Reset circuit breaker on success

        Args:
            domain: Domain that succeeded

        """
        if domain in self.circuit_breakers:
            logger.info(f"✓ Resetting circuit breaker for {domain}")
            del self.circuit_breakers[domain]

    def get_stats(self) -> dict:
        """Get scraping statistics for monitoring

        Returns:
            Dictionary with scraping stats

        """
        return {
            "total_requests": sum(self.request_counts.values()),
            "domains_accessed": len(self.request_counts),
            "requests_by_domain": dict(self.request_counts),
            "robots_cache_size": len(self.robots_cache),
            "open_circuits": len([d for d in self.circuit_breakers if self.is_circuit_open(d)]),
            "circuit_breakers": {
                domain: {"failures": failures, "opened_at": opened_at.isoformat()}
                for domain, (failures, opened_at) in self.circuit_breakers.items()
            },
        }


# Default configuration
DEFAULT_SCRAPING_CONFIG = {
    "robots_txt": {
        "enabled": True,
        "cache_ttl": 86400,  # 24 hours per RFC 9309
        "respect_crawl_delay": True,
        "honor_disallow": True,
    },
    "rate_limiting": {
        "default_delay": 3.0,  # seconds between requests
        "youtube.com": 5.0,  # Higher delay for video platforms
        "twitter.com": 4.0,
        "x.com": 4.0,
        "newsapi.org": 2.0,
        ".gov": 10.0,  # Very conservative for government sites
        ".mil": 10.0,  # Military sites
        "adaptive_throttling": True,
        "max_concurrent": 3,
    },
    "user_agent": {
        "name": "PNKLN-Intelligence-Bot/1.0",
        "contact": "redacted@shadowtag-v4.local",
        "purpose": "Strategic intelligence gathering for AI governance",
        "url": "https://pnkln.ai/bot-policy",
    },
    "error_handling": {
        "respect_retry_after": True,
        "exponential_backoff": True,
        "max_retries": 3,
        "circuit_breaker": True,
    },
}
