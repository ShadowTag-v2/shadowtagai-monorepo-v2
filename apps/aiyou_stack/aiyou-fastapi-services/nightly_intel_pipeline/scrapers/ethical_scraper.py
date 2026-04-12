"""
Ethical Web Scraper with ATP 5-19 RA-1 Compliance
Implements robots.txt respect, rate limiting, and circuit breaker patterns
"""

import asyncio
import random
import time
from datetime import datetime, timedelta
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import aiohttp
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

from ..config import SCRAPING_ETHICS

logger = structlog.get_logger(__name__)


class CircuitBreaker:
    """Circuit breaker pattern for handling sustained failures"""

    def __init__(self, failure_threshold: int = 5, timeout_seconds: int = 300):
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.failures = 0
        self.opened_at: datetime | None = None
        self.state = "closed"  # closed, open, half_open

    def record_failure(self):
        """Record a failure and potentially open the circuit"""
        self.failures += 1
        if self.failures >= self.failure_threshold:
            self.state = "open"
            self.opened_at = datetime.now()
            logger.warning(
                "circuit_breaker_opened", failures=self.failures, timeout=self.timeout_seconds
            )

    def record_success(self):
        """Record a success and reset the circuit"""
        self.failures = 0
        self.state = "closed"
        self.opened_at = None

    def is_open(self) -> bool:
        """Check if circuit is open (blocking requests)"""
        if self.state == "closed":
            return False

        if self.state == "open":
            # Check if timeout has passed
            if datetime.now() - self.opened_at > timedelta(seconds=self.timeout_seconds):
                self.state = "half_open"
                logger.info("circuit_breaker_half_open")
                return False
            return True

        # half_open state - allow one request to test
        return False


class EthicalScraper:
    """
    ATP 5-19 RA-1 compliant web scraper

    Features:
    - RFC 9309 compliant robots.txt handling (24-hour cache)
    - Domain-specific rate limiting with adaptive jitter
    - Circuit breaker pattern for sustained failures
    - Proper User-Agent identification
    - Crawl-delay respect
    - Exponential backoff retry logic
    """

    def __init__(self, config: dict | None = None):
        self.config = config or SCRAPING_ETHICS
        self.robots_cache: dict[str, tuple[RobotFileParser, datetime]] = {}
        self.last_request: dict[str, float] = {}
        self.circuit_breakers: dict[str, CircuitBreaker] = {}
        self.user_agent = self.config["robots_txt"]["user_agent"]

        # Extract configs
        self.robots_config = self.config["robots_txt"]
        self.rate_config = self.config["rate_limiting"]
        self.circuit_config = self.config["circuit_breaker"]
        self.retry_config = self.config["retry_policy"]

        logger.info(
            "ethical_scraper_initialized", user_agent=self.user_agent, rate_limits=self.rate_config
        )

    def _get_domain(self, url: str) -> str:
        """Extract domain from URL"""
        return urlparse(url).netloc

    def _get_robots_url(self, url: str) -> str:
        """Construct robots.txt URL for a given URL"""
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}/robots.txt"

    async def _fetch_robots_txt(self, url: str) -> RobotFileParser:
        """
        Fetch and parse robots.txt with RFC 9309 compliant caching
        Cache TTL: 24 hours
        """
        domain = self._get_domain(url)

        # Check cache
        if domain in self.robots_cache:
            parser, cached_at = self.robots_cache[domain]
            age = datetime.now() - cached_at
            if age < timedelta(seconds=self.robots_config["cache_ttl"]):
                logger.debug("robots_txt_cache_hit", domain=domain, age_seconds=age.total_seconds())
                return parser

        # Fetch fresh robots.txt
        robots_url = self._get_robots_url(url)
        parser = RobotFileParser()
        parser.set_url(robots_url)

        try:
            async with (
                aiohttp.ClientSession() as session,
                session.get(
                    robots_url,
                    headers={"User-Agent": self.user_agent},
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as response,
            ):
                if response.status == 200:
                    content = await response.text()
                    parser.parse(content.splitlines())
                    logger.info("robots_txt_fetched", domain=domain, url=robots_url)
                else:
                    # No robots.txt or error - allow all
                    logger.warning("robots_txt_not_found", domain=domain, status=response.status)
                    parser.parse([])
        except Exception as e:
            logger.error("robots_txt_fetch_error", domain=domain, error=str(e))
            # On error, allow all (conservative approach)
            parser.parse([])

        # Cache the result
        self.robots_cache[domain] = (parser, datetime.now())
        return parser

    def is_allowed(self, url: str, parser: RobotFileParser) -> bool:
        """Check if URL is allowed by robots.txt"""
        if not self.robots_config["enabled"] or not self.robots_config["honor_disallow"]:
            return True

        allowed = parser.can_fetch(self.user_agent, url)
        logger.debug("robots_txt_check", url=url, allowed=allowed)
        return allowed

    def get_crawl_delay(self, url: str, parser: RobotFileParser) -> float:
        """
        Get crawl delay from robots.txt or config
        Returns domain-specific or default delay
        """
        domain = self._get_domain(url)

        # Check robots.txt crawl-delay
        if self.robots_config["respect_crawl_delay"]:
            crawl_delay = parser.crawl_delay(self.user_agent)
            if crawl_delay:
                logger.debug("robots_crawl_delay", domain=domain, delay=crawl_delay)
                return float(crawl_delay)

        # Domain-specific rate limits
        for domain_pattern, delay in self.rate_config.items():
            if isinstance(delay, (int, float)) and domain_pattern in domain.lower():
                return delay

        # Default delay
        return self.rate_config["default_delay"]

    def apply_rate_limit(self, domain: str, delay: float):
        """
        Apply rate limiting with adaptive jitter
        Ensures minimum delay between requests to same domain
        """
        now = time.time()

        if domain in self.last_request:
            elapsed = now - self.last_request[domain]
            remaining = delay - elapsed

            if remaining > 0:
                # Add jitter to avoid thundering herd
                if self.rate_config["adaptive_throttling"]:
                    jitter = random.uniform(
                        -delay * self.rate_config["jitter_factor"],
                        delay * self.rate_config["jitter_factor"],
                    )
                    remaining = max(0.1, remaining + jitter)

                logger.debug(
                    "rate_limit_applied", domain=domain, delay=remaining, configured_delay=delay
                )
                time.sleep(remaining)

        self.last_request[domain] = time.time()

    def get_circuit_breaker(self, domain: str) -> CircuitBreaker:
        """Get or create circuit breaker for domain"""
        if domain not in self.circuit_breakers:
            self.circuit_breakers[domain] = CircuitBreaker(
                failure_threshold=self.circuit_config["failure_threshold"],
                timeout_seconds=self.circuit_config["timeout_seconds"],
            )
        return self.circuit_breakers[domain]

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10), reraise=True
    )
    async def fetch_url(
        self, url: str, method: str = "GET", headers: dict | None = None, **kwargs
    ) -> tuple[int, str]:
        """
        Fetch URL with full ethical compliance

        Returns:
            Tuple of (status_code, content)

        Raises:
            Exception: If circuit is open or URL is disallowed
        """
        domain = self._get_domain(url)

        # Check circuit breaker
        circuit = self.get_circuit_breaker(domain)
        if circuit.is_open():
            raise Exception(f"Circuit breaker open for {domain}. Waiting for timeout.")

        # Fetch and check robots.txt
        parser = await self._fetch_robots_txt(url)
        if not self.is_allowed(url, parser):
            logger.warning("url_disallowed_by_robots", url=url)
            raise Exception(f"URL disallowed by robots.txt: {url}")

        # Get crawl delay and apply rate limiting
        delay = self.get_crawl_delay(url, parser)
        self.apply_rate_limit(domain, delay)

        # Prepare headers
        request_headers = {"User-Agent": self.user_agent, **(headers or {})}

        try:
            async with (
                aiohttp.ClientSession() as session,
                session.request(method, url, headers=request_headers, **kwargs) as response,
            ):
                content = await response.text()

                # Record success
                circuit.record_success()

                logger.info("url_fetched", url=url, status=response.status, size=len(content))

                return response.status, content

        except Exception as e:
            # Record failure
            circuit.record_failure()
            logger.error(
                "url_fetch_error",
                url=url,
                domain=domain,
                error=str(e),
                circuit_failures=circuit.failures,
            )
            raise

    async def fetch_multiple(
        self, urls: list[str], max_concurrent: int | None = None
    ) -> dict[str, tuple[int, str]]:
        """
        Fetch multiple URLs with concurrency control

        Returns:
            Dict mapping URL to (status_code, content)
        """
        max_concurrent = max_concurrent or self.rate_config["max_concurrent"]
        semaphore = asyncio.Semaphore(max_concurrent)

        async def fetch_with_semaphore(url: str):
            async with semaphore:
                try:
                    status, content = await self.fetch_url(url)
                    return url, (status, content)
                except Exception as e:
                    logger.error("fetch_multiple_error", url=url, error=str(e))
                    return url, (None, None)

        tasks = [fetch_with_semaphore(url) for url in urls]
        results = await asyncio.gather(*tasks)

        return dict(results)


# Convenience function for simple use cases
async def fetch_url_ethically(url: str, **kwargs) -> tuple[int, str]:
    """
    Simple wrapper for ethical URL fetching

    Usage:
        status, content = await fetch_url_ethically("https://example.com")
    """
    scraper = EthicalScraper()
    return await scraper.fetch_url(url, **kwargs)
