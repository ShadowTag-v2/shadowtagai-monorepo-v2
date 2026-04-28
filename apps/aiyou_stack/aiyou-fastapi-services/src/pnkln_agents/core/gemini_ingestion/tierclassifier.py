# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import re
from urllib.parse import urlparse

from .source import Source, SourceTier


class TierClassifier:
    """Classifies data sources into tiers based on quality and authority

    Tier 1: High-value, authoritative sources (e.g., .gov, major news, academic)
    Tier 2: Moderate-value, verified sources (e.g., established blogs, verified accounts)
    Tier 3: Low-value, general sources (e.g., forums, user-generated content)
    """

    def __init__(self):
        self.tier_1_patterns = [
            "\\.gov$",
            "\\.edu$",
            "\\.mil$",
            "nytimes\\.com$",
            "wsj\\.com$",
            "reuters\\.com$",
            "bloomberg\\.com$",
            "nature\\.com$",
            "science\\.org$",
        ]
        self.tier_3_patterns = ["reddit\\.com", "4chan\\.org", "forum", "board"]

    def classify(self, source: Source) -> SourceTier:
        """Classify source into tier"""
        domain = urlparse(source.url).netloc
        for pattern in self.tier_1_patterns:
            if re.search(pattern, domain, re.IGNORECASE):
                return SourceTier.TIER_1
        for pattern in self.tier_3_patterns:
            if re.search(pattern, domain, re.IGNORECASE):
                return SourceTier.TIER_3
        return SourceTier.TIER_2
