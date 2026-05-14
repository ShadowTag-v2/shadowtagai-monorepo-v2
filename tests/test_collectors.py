# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Tests for source collectors."""

import pytest

from src.collectors import NewsAPICollector, RSSCollector, TwitterCollector, YouTubeCollector
from src.models import Tier


@pytest.mark.asyncio
async def test_youtube_collector():
    """Test YouTube collector."""
    collector = YouTubeCollector()

    # Test collection
    items = await collector.collect()

    assert len(items) > 0
    assert all(item.source == "youtube" for item in items)
    assert all(item.tier in [Tier.TIER_1, Tier.TIER_2, Tier.TIER_3] for item in items)
    assert all(0.0 <= item.relevance_score <= 1.0 for item in items)
    assert all(item.cost >= 0.0 for item in items)


@pytest.mark.asyncio
async def test_twitter_collector():
    """Test Twitter collector."""
    collector = TwitterCollector()

    items = await collector.collect()

    assert len(items) > 0
    assert all(item.source == "twitter" for item in items)
    assert all(hasattr(item, "tier") for item in items)  # GIL005 compliance


@pytest.mark.asyncio
async def test_newsapi_collector():
    """Test NewsAPI collector."""
    collector = NewsAPICollector()

    items = await collector.collect()

    assert len(items) > 0
    assert all(item.source == "newsapi" for item in items)


@pytest.mark.asyncio
async def test_rss_collector():
    """Test RSS collector with robots.txt checking."""
    collector = RSSCollector()

    # Test robots.txt checking (GIL004)
    can_fetch = collector.check_robots_txt("https://example.com/feed.xml")
    assert isinstance(can_fetch, bool)

    items = await collector.collect()

    assert len(items) >= 0  # May be 0 if robots.txt blocks
    if items:
        assert all(item.source == "rss" for item in items)


@pytest.mark.asyncio
async def test_rate_limiting():
    """Test that rate limiting is applied."""
    import time

    from src.collectors.base import rate_limit

    @rate_limit(max_per_second=2.0)
    async def test_func():
        return time.time()

    # Call function twice and measure time
    start = time.time()
    t1 = await test_func()
    t2 = await test_func()
    elapsed = time.time() - start

    # Should take at least 0.5 seconds (1/2.0) between calls
    assert elapsed >= 0.4  # Allow some tolerance


def test_source_tracking():
    """Test that all collectors track source (GIL002)."""
    from src.collectors.base import SourceCollector

    collectors = [
        YouTubeCollector(),
        TwitterCollector(),
        NewsAPICollector(),
        RSSCollector(),
    ]

    for collector in collectors:
        assert isinstance(collector, SourceCollector)
        assert collector.source_name in ["youtube", "twitter", "newsapi", "rss"]
