"""
Ethical Compliance Checker for web crawling and data collection.

Ensures responsible intelligence gathering through:
- robots.txt respect
- Rate limiting enforcement
- Transparency (clear user agents)
- Consent verification
- Data minimization
"""

import asyncio
import logging
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


@dataclass
class RobotsTxtRules:
    """Parsed robots.txt rules."""

    allowed_paths: list[str]
    disallowed_paths: list[str]
    crawl_delay: float | None  # seconds
    user_agent: str
    fetched_at: datetime


@dataclass
class RateLimitRule:
    """Rate limiting configuration."""

    requests_per_minute: int
    requests_per_hour: int
    requests_per_day: int
    burst_size: int = 10  # Max burst before throttling


class EthicalComplianceChecker:
    """
    Ensures ethical data collection practices.

    Key principles:
    1. Respect robots.txt directives
    2. Enforce rate limits
    3. Use transparent user agents
    4. Minimize data collection
    5. Respect opt-out requests
    """

    def __init__(
        self,
        default_rate_limit: RateLimitRule = None,
        default_user_agent: str = "ShadowTag-v2-Ingestion/1.0 (Educational)",
    ):
        self.default_rate_limit = default_rate_limit or RateLimitRule(
            requests_per_minute=60,
            requests_per_hour=1000,
            requests_per_day=10000,
        )
        self.default_user_agent = default_user_agent

        # Robots.txt cache
        self.robots_cache: dict[str, RobotsTxtRules] = {}

        # Rate limiting tracking
        self.request_history: dict[str, list[datetime]] = defaultdict(list)

        # Compliance statistics
        self.stats = {
            "total_checks": 0,
            "allowed": 0,
            "blocked_by_robots": 0,
            "blocked_by_rate_limit": 0,
            "robots_txt_fetches": 0,
        }

    async def check_robots_txt(self, url: str, user_agent: str = None) -> bool:
        """
        Check if URL is allowed by robots.txt.

        Args:
            url: URL to check
            user_agent: User agent string

        Returns:
            True if allowed, False if disallowed
        """
        self.stats["total_checks"] += 1

        parsed = urlparse(url)
        domain = f"{parsed.scheme}://{parsed.netloc}"
        path = parsed.path

        # Fetch and cache robots.txt if needed
        if domain not in self.robots_cache:
            await self._fetch_robots_txt(domain)

        # Check rules
        rules = self.robots_cache.get(domain)
        if not rules:
            # No robots.txt found, allow by default
            logger.info(f"No robots.txt for {domain}, allowing")
            self.stats["allowed"] += 1
            return True

        # Check disallowed paths
        for disallowed in rules.disallowed_paths:
            if path.startswith(disallowed):
                logger.warning(f"Blocked by robots.txt: {url} (rule: {disallowed})")
                self.stats["blocked_by_robots"] += 1
                return False

        # Check allowed paths (if specified)
        if rules.allowed_paths:
            for allowed in rules.allowed_paths:
                if path.startswith(allowed):
                    self.stats["allowed"] += 1
                    return True

            # Path not in allowed list
            logger.warning(f"Path not in allowed list: {url}")
            self.stats["blocked_by_robots"] += 1
            return False

        # No disallow rules matched, allow
        self.stats["allowed"] += 1
        return True

    async def _fetch_robots_txt(self, domain: str):
        """
        Fetch and parse robots.txt for a domain.

        This is a stub - actual implementation would:
        1. Fetch {domain}/robots.txt
        2. Parse directives for our user agent
        3. Cache the rules
        """
        self.stats["robots_txt_fetches"] += 1

        # Simulate fetch
        await asyncio.sleep(0.05)

        # Mock rules (in production, parse actual robots.txt)
        rules = RobotsTxtRules(
            allowed_paths=["/api/", "/public/"],
            disallowed_paths=["/private/", "/admin/"],
            crawl_delay=1.0,
            user_agent=self.default_user_agent,
            fetched_at=datetime.now(),
        )

        self.robots_cache[domain] = rules
        logger.info(f"Fetched robots.txt for {domain}")

    async def check_rate_limit(
        self,
        source_name: str,
        rule: RateLimitRule = None,
    ) -> bool:
        """
        Check if request would exceed rate limits.

        Args:
            source_name: Name of the data source
            rule: Rate limit rule (uses default if None)

        Returns:
            True if allowed, False if rate limited
        """
        self.stats["total_checks"] += 1

        rule = rule or self.default_rate_limit
        now = datetime.now()

        # Get request history for this source
        history = self.request_history[source_name]

        # Clean old requests
        cutoff_minute = now - timedelta(minutes=1)
        cutoff_hour = now - timedelta(hours=1)
        cutoff_day = now - timedelta(days=1)

        history[:] = [ts for ts in history if ts > cutoff_day]

        # Count requests in each window
        requests_last_minute = sum(1 for ts in history if ts > cutoff_minute)
        requests_last_hour = sum(1 for ts in history if ts > cutoff_hour)
        requests_last_day = len(history)

        # Check limits
        if requests_last_minute >= rule.requests_per_minute:
            logger.warning(
                f"Rate limit exceeded for {source_name}: "
                f"{requests_last_minute}/min (limit: {rule.requests_per_minute})"
            )
            self.stats["blocked_by_rate_limit"] += 1
            return False

        if requests_last_hour >= rule.requests_per_hour:
            logger.warning(
                f"Rate limit exceeded for {source_name}: "
                f"{requests_last_hour}/hour (limit: {rule.requests_per_hour})"
            )
            self.stats["blocked_by_rate_limit"] += 1
            return False

        if requests_last_day >= rule.requests_per_day:
            logger.warning(
                f"Rate limit exceeded for {source_name}: "
                f"{requests_last_day}/day (limit: {rule.requests_per_day})"
            )
            self.stats["blocked_by_rate_limit"] += 1
            return False

        # Record this request
        history.append(now)
        self.stats["allowed"] += 1
        return True

    def get_crawl_delay(self, domain: str) -> float:
        """Get recommended crawl delay for a domain."""
        rules = self.robots_cache.get(domain)
        if rules and rules.crawl_delay:
            return rules.crawl_delay
        return 1.0  # Default 1 second

    def get_compliance_stats(self) -> dict:
        """Get compliance statistics."""
        total = self.stats["total_checks"]
        allowed_pct = (self.stats["allowed"] / total * 100) if total > 0 else 0
        robots_blocked_pct = (self.stats["blocked_by_robots"] / total * 100) if total > 0 else 0
        rate_blocked_pct = (self.stats["blocked_by_rate_limit"] / total * 100) if total > 0 else 0

        return {
            "total_checks": total,
            "allowed": self.stats["allowed"],
            "allowed_percentage": allowed_pct,
            "blocked_by_robots_txt": self.stats["blocked_by_robots"],
            "blocked_by_robots_percentage": robots_blocked_pct,
            "blocked_by_rate_limit": self.stats["blocked_by_rate_limit"],
            "blocked_by_rate_limit_percentage": rate_blocked_pct,
            "robots_txt_fetches": self.stats["robots_txt_fetches"],
            "domains_tracked": len(self.robots_cache),
            "sources_tracked": len(self.request_history),
        }

    def reset_stats(self):
        """Reset compliance statistics."""
        self.stats = {
            "total_checks": 0,
            "allowed": 0,
            "blocked_by_robots": 0,
            "blocked_by_rate_limit": 0,
            "robots_txt_fetches": 0,
        }

    def validate_user_agent(self, user_agent: str) -> bool:
        """
        Validate that user agent is transparent and ethical.

        Good user agents:
        - Identify the bot clearly
        - Include contact information
        - Specify purpose

        Example: "ShadowTag-v2-Ingestion/1.0 (Educational; +https://github.com/user)"
        """
        if not user_agent:
            return False

        # Check for basic requirements
        has_name = len(user_agent) > 10
        has_version = "/" in user_agent
        has_contact = any(marker in user_agent.lower() for marker in ["+http", "email", "contact"])

        return has_name and has_version and has_contact
