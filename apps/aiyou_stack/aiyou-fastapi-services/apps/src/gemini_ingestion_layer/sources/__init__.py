# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Multi-Source Ingestion Module

Supports ingestion from multiple platforms:
- YouTube: Video metadata and transcripts
- Twitter: Tweets and threads
- News: RSS feeds and news APIs
- Reddit: Posts and comments
- RSS Feeds: General RSS/Atom feeds

All sources implement ethical crawling with rate limiting.
"""

from .base import BaseSource, IngestionItem
from .news import NewsSource
from .twitter import TwitterSource
from .youtube import YouTubeSource

__all__ = [
    "BaseSource",
    "IngestionItem",
    "NewsSource",
    "TwitterSource",
    "YouTubeSource",
]
