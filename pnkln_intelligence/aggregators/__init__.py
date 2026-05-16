# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Aggregators module for collecting data from various sources"""

from .arxiv_aggregator import ArxivAggregator
from .hackernews_aggregator import HackerNewsAggregator
from .reddit_aggregator import RedditAggregator

__all__ = ["ArxivAggregator", "HackerNewsAggregator", "RedditAggregator"]
