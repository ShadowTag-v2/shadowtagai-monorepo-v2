# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from .debaterole import DebateRole

logger = logging.getLogger(__name__)


@dataclass
class GeminiDebateArgument:
    """Single argument in Gemini debate"""

    role: DebateRole
    argument: str
    confidence: float
    evidence: dict[str, Any]
    tokens_used: int
    latency_ms: float
    timestamp: datetime
