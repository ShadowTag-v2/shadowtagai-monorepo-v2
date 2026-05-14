# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Ethical Crawling Module

Implements responsible web scraping practices:
- robots.txt compliance (REP - Robots Exclusion Protocol)
- Rate limiting per domain
- Transparency through proper User-Agent identification
- Request timeout management
"""

from .ethical_crawler import EthicalCrawler, CrawlResult
from .rate_limiter import RateLimiter, DomainRateLimiter

__all__ = ["EthicalCrawler", "CrawlResult", "RateLimiter", "DomainRateLimiter"]
