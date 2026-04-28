# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from enum import Enum


class EthicalViolationType(Enum):
    """Types of ethical compliance violations"""

    ROBOTS_TXT = "robots_txt_violation"
    RATE_LIMIT = "rate_limit_exceeded"
    TERMS_OF_SERVICE = "tos_violation"
    COPYRIGHT = "copyright_risk"
    PRIVACY = "privacy_violation"
    ATTRIBUTION = "missing_attribution"
