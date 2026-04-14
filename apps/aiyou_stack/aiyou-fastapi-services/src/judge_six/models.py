"""Data models for Judge #6
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class VerdictStatus(Enum):
    """Verdict status for validation results"""

    APPROVED = "approved"
    REJECTED = "rejected"
    FLAGGED = "flagged"
    REQUIRES_REVIEW = "requires_review"


class Severity(Enum):
    """Severity levels for policy violations"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Action:
    """Represents an action to be validated"""

    id: str
    type: str
    payload: dict[str, Any]
    source: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class PurposeVerdict:
    """Verdict for Purpose validation"""

    score: float  # 0.0 to 10.0
    status: VerdictStatus
    alignment_score: float
    clarity_score: float
    mission_fit: bool
    explanation: str


@dataclass
class ReasonsVerdict:
    """Verdict for Reasons validation"""

    score: float  # 0.0 to 10.0
    status: VerdictStatus
    evidence_quality: str  # strong, medium, weak, none
    risk_reward_ratio: float
    stakeholder_impact: str
    explanation: str


@dataclass
class BrakesVerdict:
    """Verdict for Brakes validation"""

    score: float  # 0.0 to 10.0 (higher is riskier)
    status: VerdictStatus
    threats_detected: list[str]
    compliance_violations: list[str]
    risk_level: Severity
    explanation: str


@dataclass
class JRVerdict:
    """Overall Judge #6 Verdict"""

    id: str
    action_id: str
    timestamp: datetime
    status: VerdictStatus
    confidence: float
    purpose: PurposeVerdict
    reasons: ReasonsVerdict
    brakes: BrakesVerdict
    policy_id: str | None = None
    summary: str = ""
