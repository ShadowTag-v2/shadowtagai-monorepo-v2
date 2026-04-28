# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Source Collectors for Gemini Ingestion Layer
Real API integrations for YouTube, Twitter, News, Academic sources
"""

from .academic_collector import AcademicCollector
from .base import BaseCollector
from .news_collector import NewsCollector
from .reddit_collector import RedditCollector
from .twitter_collector import TwitterCollector
from .youtube_collector import YouTubeCollector

__all__ = [
    "AcademicCollector",
    "BaseCollector",
    "NewsCollector",
    "RedditCollector",
    "TwitterCollector",
    "YouTubeCollector",
]
