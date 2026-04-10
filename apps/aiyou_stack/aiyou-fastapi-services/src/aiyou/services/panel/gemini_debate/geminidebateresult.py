import logging
from dataclasses import dataclass
from datetime import datetime


logger = logging.getLogger(__name__)


@dataclass
class GeminiDebateResult:
    """Final result of Gemini panel debate"""

    decision: str
    confidence: float
    reasoning: str
    prosecutor_argument: str
    defender_argument: str
    consensus_score: float
    duration_ms: float
    total_tokens: int
    cost_usd: float
    timestamp: datetime
