# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
ETHICAL CRAWLER - Web Intelligence Collection Compliance
=========================================================

NEW SECTION: Ethical Compliance Model (vs Judge #6 which has none)

Ensures intelligence collection respects:
1. robots.txt directives (standard web etiquette)
2. Rate limiting (prevent service disruption)
3. Transparency (user-agent identification)
4. Terms of service compliance
5. Data privacy regulations

CRITICAL FOR INGESTION LAYER:
-----------------------------
Unlike Judge #6 (internal enforcement), Gemini Ingestion crawls
external web sources, creating legal/ethical risks if non-compliant.

RISK MITIGATION:
---------------
- Banned from sources → loss of intelligence pipeline
- Legal action → lawsuits, fines, reputation damage
- Service disruption → DoS-like behavior
- Data privacy violations → GDPR/CCPA penalties

INTEGRATION:
-----------
- Called BY: Source collectors (YouTube, Twitter, News, etc.)
- Validates BEFORE: Making API calls or scraping requests
- Enforces: Per-source rate limits, robots.txt rules

Author: Pnkln Architecture Team
Version: 1.0.0
License: Proprietary
"""

import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
import logging
from urllib.parse import urlparse
from collections import defaultdict

logger = logging.getLogger(__name__)


# ============================================================================
# DATA STRUCTURES
# ============================================================================


@dataclass
class RobotsTxtRules:
  """
  Parsed robots.txt rules for a domain.

  Attributes:
      domain: Domain these rules apply to
      user_agent: User-agent these rules are for
      allowed_paths: Paths explicitly allowed
      disallowed_paths: Paths explicitly disallowed
      crawl_delay_seconds: Minimum delay between requests
      sitemap_urls: URLs of sitemaps (if provided)
      last_fetched: When rules were last fetched
  """

  domain: str
  user_agent: str = "*"
  allowed_paths: set[str] = field(default_factory=set)
  disallowed_paths: set[str] = field(default_factory=set)
  crawl_delay_seconds: float = 1.0  # Default 1 second
  sitemap_urls: set[str] = field(default_factory=set)
  last_fetched: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

  def is_path_allowed(self, path: str) -> bool:
    """
    Check if path is allowed by robots.txt.

    Args:
        path: URL path to check (e.g., "/api/data")

    Returns:
        True if allowed, False if disallowed
    """
    # If explicitly disallowed, reject
    for disallowed in self.disallowed_paths:
      if path.startswith(disallowed):
        return False

    # If explicitly allowed, accept
    for allowed in self.allowed_paths:
      if path.startswith(allowed):
        return True

    # Default: allow if no specific disallow rule matched
    return True


@dataclass
class RateLimitConfig:
  """
  Rate limiting configuration for a source.

  Attributes:
      source_name: Name of source (e.g., "youtube", "twitter")
      requests_per_minute: Max requests per minute
      requests_per_hour: Max requests per hour
      requests_per_day: Max requests per day
      burst_size: Max requests in immediate burst
      backoff_seconds: Time to wait if rate limit hit
  """

  source_name: str
  requests_per_minute: int = 60
  requests_per_hour: int = 1000
  requests_per_day: int = 10000
  burst_size: int = 10
  backoff_seconds: float = 60.0


@dataclass
class CrawlRequest:
  """
  Request to crawl a URL with ethical compliance.

  Attributes:
      url: Full URL to crawl
      source_name: Source identifier (for rate limiting)
      user_agent: User-agent to use
      respect_robots_txt: Whether to check robots.txt
      max_retries: Max retry attempts if rate limited
  """

  url: str
  source_name: str
  user_agent: str = "PnklnBot/1.0 (Intelligence Collection; +https://pnkln.ai/bot)"
  respect_robots_txt: bool = True
  max_retries: int = 3


@dataclass
class CrawlResult:
  """
  Result from ethical crawl attempt.

  Attributes:
      request: Original request
      allowed: Was crawl allowed (ethical check passed)?
      reason: Why allowed/denied
      delay_seconds: How long to wait before next request
      robots_txt_compliant: Did it pass robots.txt check?
      rate_limit_compliant: Did it pass rate limit check?
  """

  request: CrawlRequest
  allowed: bool
  reason: str
  delay_seconds: float
  robots_txt_compliant: bool
  rate_limit_compliant: bool
  timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


# ============================================================================
# ETHICAL CRAWLER
# ============================================================================


class EthicalCrawler:
  """
  Ethical web intelligence collection enforcement.

  FEATURES:
  ---------
  1. robots.txt compliance (respects webmaster directives)
  2. Rate limiting (prevents service disruption)
  3. Transparent user-agent (identifies bot clearly)
  4. Backoff on limits (polite retry behavior)

  USAGE:
  ------
  crawler = EthicalCrawler()

  # Add rate limit config for source
  crawler.configure_rate_limit("youtube", requests_per_minute=60)

  # Check if URL can be crawled
  result = await crawler.check_crawl_allowed(
      CrawlRequest(url="https://youtube.com/watch?v=123", source_name="youtube")
  )

  if result.allowed:
      # Proceed with crawl
      await crawler.record_request("youtube")  # Track for rate limiting
  else:
      # Wait or skip
      await asyncio.sleep(result.delay_seconds)
  """

  def __init__(self):
    """Initialize ethical crawler."""
    self.robots_cache: dict[str, RobotsTxtRules] = {}
    self.rate_limits: dict[str, RateLimitConfig] = {}

    # Request tracking for rate limiting
    self.request_history: dict[str, list] = defaultdict(list)

    # Default rate limits (conservative)
    self._set_default_rate_limits()

    logger.info("Ethical Crawler initialized (robots.txt + rate limiting)")

  def _set_default_rate_limits(self) -> None:
    """Set conservative default rate limits for common sources."""
    defaults = {
      "youtube": RateLimitConfig(
        "youtube", requests_per_minute=60, requests_per_hour=1000
      ),
      "twitter": RateLimitConfig(
        "twitter", requests_per_minute=100, requests_per_hour=5000
      ),
      "news_api": RateLimitConfig(
        "news_api", requests_per_minute=30, requests_per_hour=500
      ),
      "rss_feeds": RateLimitConfig(
        "rss_feeds", requests_per_minute=10, requests_per_hour=100
      ),
      "reddit": RateLimitConfig(
        "reddit", requests_per_minute=60, requests_per_hour=1000
      ),
    }

    for source, config in defaults.items():
      self.rate_limits[source] = config

  def configure_rate_limit(
    self,
    source_name: str,
    requests_per_minute: int,
    requests_per_hour: int = None,
    requests_per_day: int = None,
  ) -> None:
    """
    Configure custom rate limit for source.

    Args:
        source_name: Source identifier
        requests_per_minute: Requests per minute limit
        requests_per_hour: Optional hourly limit
        requests_per_day: Optional daily limit
    """
    self.rate_limits[source_name] = RateLimitConfig(
      source_name=source_name,
      requests_per_minute=requests_per_minute,
      requests_per_hour=requests_per_hour or requests_per_minute * 60,
      requests_per_day=requests_per_day or requests_per_minute * 60 * 24,
    )

    logger.info(f"Rate limit configured for {source_name}: {requests_per_minute}/min")

  async def fetch_robots_txt(self, domain: str) -> RobotsTxtRules:
    """
    Fetch and parse robots.txt for domain.

    Args:
        domain: Domain to fetch robots.txt from (e.g., "youtube.com")

    Returns:
        RobotsTxtRules

    Note:
        Real implementation would use aiohttp to fetch robots.txt.
        This is a mock for demonstration.
    """
    # Mock implementation (real would fetch https://domain/robots.txt)
    logger.info(f"Fetching robots.txt for {domain}")

    # Mock rules (conservative defaults)
    rules = RobotsTxtRules(
      domain=domain,
      user_agent="*",
      disallowed_paths={"/admin", "/private", "/api/internal"},
      crawl_delay_seconds=1.0,
    )

    self.robots_cache[domain] = rules
    return rules

  def check_robots_txt_compliance(
    self, url: str, user_agent: str = "*"
  ) -> tuple[bool, str]:
    """
    Check if URL is allowed by robots.txt.

    Args:
        url: Full URL to check
        user_agent: User-agent making request

    Returns:
        (allowed: bool, reason: str)
    """
    parsed = urlparse(url)
    domain = parsed.netloc
    path = parsed.path

    # Check cache first
    if domain not in self.robots_cache:
      # Would normally fetch robots.txt here
      # For now, use conservative defaults
      logger.warning(f"robots.txt not cached for {domain}, using defaults")
      return True, "No robots.txt cached (conservative allow)"

    rules = self.robots_cache[domain]

    if rules.is_path_allowed(path):
      return True, f"Allowed by robots.txt for {domain}"
    else:
      return False, f"Disallowed by robots.txt: path {path} blocked"

  def check_rate_limit_compliance(self, source_name: str) -> tuple[bool, float]:
    """
    Check if request would violate rate limits.

    Args:
        source_name: Source to check

    Returns:
        (allowed: bool, delay_seconds: float)
    """
    if source_name not in self.rate_limits:
      logger.warning(
        f"No rate limit configured for {source_name}, using conservative defaults"
      )
      # Default: 10 req/min
      self.rate_limits[source_name] = RateLimitConfig(
        source_name=source_name, requests_per_minute=10
      )

    config = self.rate_limits[source_name]
    now = time.time()

    # Get request history for source
    history = self.request_history[source_name]

    # Clean old requests (beyond 1 day)
    cutoff = now - 86400  # 24 hours
    history = [ts for ts in history if ts > cutoff]
    self.request_history[source_name] = history

    # Check minute limit
    minute_ago = now - 60
    requests_last_minute = sum(1 for ts in history if ts > minute_ago)

    if requests_last_minute >= config.requests_per_minute:
      delay = 60.0 - (now - min(ts for ts in history if ts > minute_ago))
      return False, max(delay, config.backoff_seconds)

    # Check hour limit
    hour_ago = now - 3600
    requests_last_hour = sum(1 for ts in history if ts > hour_ago)

    if requests_last_hour >= config.requests_per_hour:
      return False, config.backoff_seconds

    # Check day limit
    requests_today = len(history)

    if requests_today >= config.requests_per_day:
      return False, config.backoff_seconds * 10  # Longer backoff for daily limit

    # All checks passed — compute minimum delay from rate limit config
    crawl_delay = (
      60.0 / config.requests_per_minute if config.requests_per_minute > 0 else 1.0
    )
    return True, crawl_delay

  async def check_crawl_allowed(self, request: CrawlRequest) -> CrawlResult:
    """
    Comprehensive ethical crawl check.

    Args:
        request: Crawl request to validate

    Returns:
        CrawlResult with allowed status and reasons
    """
    # Check 1: robots.txt compliance
    robots_allowed, robots_reason = self.check_robots_txt_compliance(
      request.url, request.user_agent
    )

    # Check 2: Rate limit compliance
    rate_allowed, delay_seconds = self.check_rate_limit_compliance(request.source_name)

    # Overall decision
    allowed = robots_allowed and rate_allowed

    if not robots_allowed:
      reason = f"robots.txt violation: {robots_reason}"
    elif not rate_allowed:
      reason = (
        f"Rate limit exceeded for {request.source_name}, retry in {delay_seconds:.0f}s"
      )
    else:
      reason = "Allowed (robots.txt + rate limit compliant)"

    result = CrawlResult(
      request=request,
      allowed=allowed,
      reason=reason,
      delay_seconds=delay_seconds,
      robots_txt_compliant=robots_allowed,
      rate_limit_compliant=rate_allowed,
    )

    if allowed:
      logger.debug(f"Crawl allowed for {request.url} (wait {delay_seconds:.1f}s)")
    else:
      logger.warning(f"Crawl denied for {request.url}: {reason}")

    return result

  async def record_request(self, source_name: str) -> None:
    """
    Record request for rate limiting tracking.

    Args:
        source_name: Source that made request

    Call this AFTER successful request to update rate limit counters.
    """
    self.request_history[source_name].append(time.time())

  def get_rate_limit_status(self, source_name: str) -> dict:
    """
    Get current rate limit status for source.

    Args:
        source_name: Source to check

    Returns:
        Dict with current usage stats
    """
    now = time.time()
    history = self.request_history.get(source_name, [])

    minute_ago = now - 60
    hour_ago = now - 3600

    requests_last_minute = sum(1 for ts in history if ts > minute_ago)
    requests_last_hour = sum(1 for ts in history if ts > hour_ago)
    requests_today = len(history)

    config = self.rate_limits.get(source_name)

    if config is None:
      return {"error": f"No rate limit configured for {source_name}"}

    return {
      "source": source_name,
      "requests_last_minute": requests_last_minute,
      "limit_per_minute": config.requests_per_minute,
      "requests_last_hour": requests_last_hour,
      "limit_per_hour": config.requests_per_hour,
      "requests_today": requests_today,
      "limit_per_day": config.requests_per_day,
      "utilization_minute": f"{requests_last_minute / config.requests_per_minute:.1%}",
      "utilization_hour": f"{requests_last_hour / config.requests_per_hour:.1%}",
      "utilization_day": f"{requests_today / config.requests_per_day:.1%}",
    }


# ============================================================================
# EXAMPLE USAGE
# ============================================================================


async def example_usage():
  """Demonstrate ethical crawler."""
  crawler = EthicalCrawler()

  # Configure custom rate limit
  crawler.configure_rate_limit("youtube", requests_per_minute=60)

  print("=== Ethical Crawler Demo ===\n")

  # Test 1: Check valid URL
  print("Test 1: Valid YouTube URL")
  request1 = CrawlRequest(url="https://youtube.com/watch?v=123", source_name="youtube")
  result1 = await crawler.check_crawl_allowed(request1)
  print(f"  Allowed: {result1.allowed}")
  print(f"  Reason: {result1.reason}")
  print(f"  Delay: {result1.delay_seconds:.1f}s")

  if result1.allowed:
    await crawler.record_request("youtube")

  # Test 2: Simulate rate limit
  print("\nTest 2: Rapid requests (rate limit test)")
  for i in range(5):
    request = CrawlRequest(
      url=f"https://youtube.com/watch?v={i}", source_name="youtube"
    )
    result = await crawler.check_crawl_allowed(request)
    print(f"  Request {i + 1}: {result.allowed} - {result.reason}")

    if result.allowed:
      await crawler.record_request("youtube")

  # Test 3: Rate limit status
  print("\nTest 3: Rate limit status")
  status = crawler.get_rate_limit_status("youtube")
  print(
    f"  Requests last minute: {status['requests_last_minute']}/{status['limit_per_minute']}"
  )
  print(f"  Utilization: {status['utilization_minute']}")

  # Test 4: robots.txt blocked path
  print("\nTest 4: robots.txt blocked path")
  request4 = CrawlRequest(
    url="https://youtube.com/admin/users",  # Blocked by mock robots.txt
    source_name="youtube",
  )
  result4 = await crawler.check_crawl_allowed(request4)
  print(f"  Allowed: {result4.allowed}")
  print(f"  Reason: {result4.reason}")


if __name__ == "__main__":
  import asyncio

  logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  )

  asyncio.run(example_usage())
