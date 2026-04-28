# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import logging
from enum import StrEnum

logger = logging.getLogger(__name__)


class DebateRole(StrEnum):
    """Roles in panel debate"""

    PROSECUTOR = "prosecutor"
    DEFENDER = "defender"
    JUDGE = "judge"
