# Free adapters — no optional deps, always importable
from ingestion.sources.cloudflare_adapter import (  # noqa: F401
    cf_get,
    get_scraper,
    search_annas_archive,
)
from ingestion.sources.darkweb_adapter import DarkWebAdapter  # noqa: F401
from ingestion.sources.fourchan_adapter import FourChanAdapter  # noqa: F401
from ingestion.sources.instagram_adapter import InstagramAdapter  # noqa: F401
from ingestion.sources.linkedin_adapter import LinkedInAdapter  # noqa: F401
from ingestion.sources.news_adapter import NewsAdapter  # noqa: F401
from ingestion.sources.reddit_adapter import RedditAdapter  # noqa: F401
from ingestion.sources.twitter_bypass_adapter import TwitterBypassAdapter  # noqa: F401

# Credentialed adapters — optional deps (tweepy, google-api-python-client)
try:
    from ingestion.sources.twitter_adapter import TwitterAdapter  # noqa: F401

    _HAS_TWITTER = True
except ImportError:
    _HAS_TWITTER = False

try:
    from ingestion.sources.youtube_adapter import YouTubeAdapter  # noqa: F401

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
