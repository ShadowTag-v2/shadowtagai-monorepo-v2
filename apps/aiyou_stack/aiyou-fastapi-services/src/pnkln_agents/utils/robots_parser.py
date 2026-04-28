# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""robots.txt Parser
Ethical web crawling compliance checker
"""

from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

import requests


class RobotsParser:
    """robots.txt parser with caching

    Respects website crawling rules as defined in robots.txt
    Caches parsed robots.txt for 24 hours to reduce requests
    """

    def __init__(self, user_agent: str = "PNKLNBot/1.0 (+https://pnkln.ai/bot)"):
        self.user_agent = user_agent
        self.cache: dict[str, tuple[RobotFileParser, datetime]] = {}
        self.cache_ttl = timedelta(hours=24)

    def is_allowed(self, url: str) -> bool:
        """Check if URL is allowed by robots.txt

        Args:
            url: Full URL to check

        Returns:
            True if allowed, False if disallowed

        """
        try:
            parsed = urlparse(url)
            domain = f"{parsed.scheme}://{parsed.netloc}"
            robots_url = urljoin(domain, "/robots.txt")

            # Check cache
            if domain in self.cache:
                parser, cached_at = self.cache[domain]
                if datetime.utcnow() - cached_at < self.cache_ttl:
                    return parser.can_fetch(self.user_agent, url)

            # Fetch and parse robots.txt
            parser = RobotFileParser()
            parser.set_url(robots_url)

            try:
                # Fetch with timeout
                response = requests.get(
                    robots_url,
                    timeout=5,
                    headers={"User-Agent": self.user_agent},
                )

                if response.status_code == 200:
                    parser.parse(response.text.splitlines())
                elif response.status_code == 404:
                    # No robots.txt = allowed (permissive)
                    parser.parse([])
                else:
                    # Other errors = be conservative, allow
                    parser.parse([])

            except requests.RequestException:
                # Network error = be conservative, allow
                parser.parse([])

            # Cache the parser
            self.cache[domain] = (parser, datetime.utcnow())

            return parser.can_fetch(self.user_agent, url)

        except Exception as e:
            # On any error, be permissive (allow)
            print(f"robots.txt parser error for {url}: {e}")
            return True

    def get_crawl_delay(self, url: str) -> float | None:
        """Get crawl delay from robots.txt

        Args:
            url: Full URL to check

        Returns:
            Crawl delay in seconds, or None if not specified

        """
        try:
            parsed = urlparse(url)
            domain = f"{parsed.scheme}://{parsed.netloc}"

            if domain in self.cache:
                parser, _ = self.cache[domain]
                delay = parser.crawl_delay(self.user_agent)
                return float(delay) if delay else None

            return None

        except Exception:
            return None

    def clear_cache(self, domain: str | None = None):
        """Clear robots.txt cache

        Args:
            domain: Specific domain to clear, or None to clear all

        """
        if domain:
            self.cache.pop(domain, None)
        else:
            self.cache.clear()
