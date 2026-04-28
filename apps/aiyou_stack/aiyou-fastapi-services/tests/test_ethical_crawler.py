# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Unit tests for Ethical Crawler (robots.txt + rate limiting)."""

import pytest
from shadowtagai.tools.ethical_crawler import (
    CrawlRequest,
    EthicalCrawler,
    RobotsTxtRules,
)


class TestEthicalCrawler:
    """Test suite for Ethical Crawler."""

    def setup_method(self):
        """Initialize ethical crawler for tests."""
        self.crawler = EthicalCrawler()

    @pytest.mark.asyncio
    async def test_robots_txt_compliance_allowed(self):
        """Test robots.txt allows valid paths."""
        # Setup mock robots.txt
        rules = RobotsTxtRules(domain="example.com", disallowed_paths={"/admin", "/private"})
        self.crawler.robots_cache["example.com"] = rules

        allowed, reason = self.crawler.check_robots_txt_compliance(
            "https://example.com/public/page",
        )

        assert allowed is True
        assert "allowed" in reason.lower()

    @pytest.mark.asyncio
    async def test_robots_txt_compliance_disallowed(self):
        """Test robots.txt blocks disallowed paths."""
        rules = RobotsTxtRules(domain="example.com", disallowed_paths={"/admin", "/private"})
        self.crawler.robots_cache["example.com"] = rules

        allowed, reason = self.crawler.check_robots_txt_compliance(
            "https://example.com/admin/users",
        )

        assert allowed is False
        assert "disallowed" in reason.lower()

    @pytest.mark.asyncio
    async def test_rate_limit_compliance_under_limit(self):
        """Test rate limit allows requests under threshold."""
        self.crawler.configure_rate_limit("test_source", requests_per_minute=10)

        # First request should be allowed
        allowed, delay = self.crawler.check_rate_limit_compliance("test_source")

        assert allowed is True
        assert delay >= 0

    @pytest.mark.asyncio
    async def test_rate_limit_compliance_over_limit(self):
        """Test rate limit blocks requests over threshold."""
        self.crawler.configure_rate_limit("test_source", requests_per_minute=5)

        # Simulate 5 requests
        for _ in range(5):
            await self.crawler.record_request("test_source")

        # 6th request should be blocked
        allowed, delay = self.crawler.check_rate_limit_compliance("test_source")

        assert allowed is False
        assert delay > 0

    @pytest.mark.asyncio
    async def test_crawl_allowed_comprehensive(self):
        """Test comprehensive crawl check (robots.txt + rate limit)."""
        request = CrawlRequest(url="https://youtube.com/watch?v=123", source_name="youtube")

        result = await self.crawler.check_crawl_allowed(request)

        assert result.allowed is True
        assert result.robots_txt_compliant is True
        assert result.rate_limit_compliant is True

    @pytest.mark.asyncio
    async def test_record_request_tracking(self):
        """Test that request recording updates rate limit counters."""
        source = "test_tracking"
        self.crawler.configure_rate_limit(source, requests_per_minute=10)

        # Record 3 requests
        for _ in range(3):
            await self.crawler.record_request(source)

        # Check status
        status = self.crawler.get_rate_limit_status(source)

        assert status["requests_last_minute"] == 3
        assert status["limit_per_minute"] == 10

    @pytest.mark.asyncio
    async def test_rate_limit_status_reporting(self):
        """Test rate limit status reporting."""
        source = "test_status"
        self.crawler.configure_rate_limit(source, requests_per_minute=100)

        # Record 25 requests
        for _ in range(25):
            await self.crawler.record_request(source)

        status = self.crawler.get_rate_limit_status(source)

        assert status["requests_last_minute"] == 25
        assert "utilization_minute" in status
        assert status["utilization_minute"] == "25.0%"

    @pytest.mark.asyncio
    async def test_custom_rate_limit_config(self):
        """Test custom rate limit configuration."""
        self.crawler.configure_rate_limit(
            "custom_source",
            requests_per_minute=50,
            requests_per_hour=2000,
        )

        config = self.crawler.rate_limits["custom_source"]

        assert config.requests_per_minute == 50
        assert config.requests_per_hour == 2000


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
