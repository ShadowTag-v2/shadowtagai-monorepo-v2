# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

# Free adapters — no optional deps, always importable
from ingestion.sources.cloudflare_adapter import (
    cf_get,
    get_scraper,
    search_annas_archive,
)
from ingestion.sources.darkweb_adapter import DarkWebAdapter
from ingestion.sources.fourchan_adapter import FourChanAdapter
from ingestion.sources.instagram_adapter import InstagramAdapter
from ingestion.sources.linkedin_adapter import LinkedInAdapter
from ingestion.sources.news_adapter import NewsAdapter
from ingestion.sources.reddit_adapter import RedditAdapter
from ingestion.sources.twitter_bypass_adapter import TwitterBypassAdapter

# Credentialed adapters — optional deps (tweepy, google-api-python-client)
try:
    from ingestion.sources.twitter_adapter import TwitterAdapter

    _HAS_TWITTER = True
except ImportError:
    _HAS_TWITTER = False

try:
    from ingestion.sources.youtube_adapter import YouTubeAdapter

    _HAS_YOUTUBE = True
except ImportError:
    _HAS_YOUTUBE = False

__all__ = [
    # Free / no-key adapters
    "RedditAdapter",
    "FourChanAdapter",
    "DarkWebAdapter",
    "TwitterBypassAdapter",
    "InstagramAdapter",
    "LinkedInAdapter",
    # Cloudflare bypass utilities
    "cf_get",
    "get_scraper",
    "search_annas_archive",
    # Credentialed (conditionally available)
    "NewsAdapter",
    "TwitterAdapter",
    "YouTubeAdapter",
]
