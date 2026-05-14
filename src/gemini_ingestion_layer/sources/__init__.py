# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Multi-Source Ingestion Module

Supports ingestion from multiple platforms:
- YouTube: Video metadata and transcripts
- Twitter: Tweets and threads
- News: RSS feeds and news APIs
- Reddit: Posts and comments
- RSS Feeds: General RSS/Atom feeds

All sources implement ethical crawling with rate limiting.
"""

from .base import BaseSource, IngestionItem
from .youtube import YouTubeSource
from .twitter import TwitterSource
from .news import NewsSource

__all__ = ["BaseSource", "IngestionItem", "YouTubeSource", "TwitterSource", "NewsSource"]
