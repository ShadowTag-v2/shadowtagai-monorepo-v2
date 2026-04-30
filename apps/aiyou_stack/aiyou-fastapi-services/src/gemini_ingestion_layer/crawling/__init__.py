"""Ethical Crawling Module

Implements responsible web scraping practices:
- robots.txt compliance (REP - Robots Exclusion Protocol)
- Rate limiting per domain
- Transparency through proper User-Agent identification
- Request timeout management
"""

from .ethical_crawler import CrawlResult, EthicalCrawler
from .rate_limiter import DomainRateLimiter, RateLimiter

__all__ = ["CrawlResult", "DomainRateLimiter", "EthicalCrawler", "RateLimiter"]
