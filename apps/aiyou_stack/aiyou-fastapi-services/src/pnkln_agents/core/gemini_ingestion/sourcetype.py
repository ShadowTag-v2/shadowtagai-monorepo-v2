# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from enum import Enum


class SourceType(Enum):
    """Types of data sources"""

    YOUTUBE = "youtube"
    TWITTER = "twitter"
    NEWS = "news"
    RSS = "rss"
    API = "api"
    WEB = "web"
    ACADEMIC = "academic"
    GOVERNMENT = "government"
