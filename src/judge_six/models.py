# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Data models for Judge #6
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone


class VerdictStatus(Enum):
    """Verdict status for validation results"""

    APPROVED = "approved"
    REJECTED = "rejected"
    FLAGGED = "flagged"
    REQUIRES_REVIEW = "requires_review"


class Severity(Enum):
    """Severity levels for policy violations"""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class Action:
    """
    Represents an action to be validated by Judge #6
    """

    action_id: str
    action_type: str  # e.g., "api_call", "data_access", "model_inference"
    description: str
    context: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    user_id: str | None = None
    source: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert action to dictionary"""
        return {
            "action_id": self.action_id,
            "action_type": self.action_type,
            "description": self.description,
            "context": self.context,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
            "user_id": self.user_id,
            "source": self.source,
        }


@dataclass
class PurposeVerdict:
    """
    Result of Purpose validation
    """

    status: VerdictStatus
    score: float  # 0-10 alignment score
    business_objective: str | None = None
    mission_alignment: str | None = None
    value_proposition: str | None = None
    explanation: str | None = None
    confidence: float = 0.0  # 0-1 confidence in verdict

    def passed(self) -> bool:
        """Check if purpose validation passed"""
        return self.status == VerdictStatus.APPROVED


@dataclass
class ReasonsVerdict:
    """
    Result of Reasons validation
    """

    status: VerdictStatus
    score: float  # 0-10 justification score
    evidence_quality: str | None = None  # "strong", "medium", "weak"
    risk_reward_ratio: float | None = None
    stakeholder_impact: str | None = None
    explanation: str | None = None
    confidence: float = 0.0

    def passed(self) -> bool:
        """Check if reasons validation passed"""
        return self.status == VerdictStatus.APPROVED


@dataclass
class BrakesVerdict:
    """
    Result of Brakes validation (risk detection)
    """

    status: VerdictStatus
    score: float  # 0-10 risk score (higher = more risky)
    threats_detected: list[str] = field(default_factory=list)
    severity: Severity = Severity.INFO
    compliance_violations: list[str] = field(default_factory=list)
    performance_concerns: list[str] = field(default_factory=list)
    ethical_concerns: list[str] = field(default_factory=list)
    explanation: str | None = None
    confidence: float = 0.0

    def blocked(self) -> bool:
        """Check if brakes blocked the action"""
        return self.status == VerdictStatus.REJECTED


@dataclass
class JRVerdict:
    """
    Complete JR Engine verdict (Purpose + Reasons + Brakes)
    """

    action_id: str
    purpose: PurposeVerdict
    reasons: ReasonsVerdict
    brakes: BrakesVerdict
    overall_status: VerdictStatus
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    latency_ms: float | None = None
    policy_ids: list[str] = field(default_factory=list)

    def approved(self) -> bool:
        """Check if overall verdict is approved"""
        return self.purpose.passed() and self.reasons.passed() and not self.brakes.blocked() and self.overall_status == VerdictStatus.APPROVED

    def to_dict(self) -> dict[str, Any]:
        """Convert verdict to dictionary"""
        return {
            "action_id": self.action_id,
            "purpose": {
                "status": self.purpose.status.value,
                "score": self.purpose.score,
                "business_objective": self.purpose.business_objective,
                "mission_alignment": self.purpose.mission_alignment,
                "explanation": self.purpose.explanation,
                "confidence": self.purpose.confidence,
            },
            "reasons": {
                "status": self.reasons.status.value,
                "score": self.reasons.score,
                "evidence_quality": self.reasons.evidence_quality,
                "risk_reward_ratio": self.reasons.risk_reward_ratio,
                "explanation": self.reasons.explanation,
                "confidence": self.reasons.confidence,
            },
            "brakes": {
                "status": self.brakes.status.value,
                "score": self.brakes.score,
                "threats_detected": self.brakes.threats_detected,
                "severity": self.brakes.severity.value,
                "compliance_violations": self.brakes.compliance_violations,
                "performance_concerns": self.brakes.performance_concerns,
                "ethical_concerns": self.brakes.ethical_concerns,
                "explanation": self.brakes.explanation,
                "confidence": self.brakes.confidence,
            },
            "overall_status": self.overall_status.value,
            "approved": self.approved(),
            "timestamp": self.timestamp.isoformat(),
            "latency_ms": self.latency_ms,
            "policy_ids": self.policy_ids,
        }


@dataclass
class Policy:
    """
    ATP 5-19 policy definition
    """

    policy_id: str
    category: str  # e.g., "injection", "xss", "auth_bypass"
    severity: Severity
    description: str
    detection_pattern: str | None = None  # Regex pattern
    action: str = "block"  # "block", "flag", "allow"
    atp_5_19_mapping: str | None = None  # e.g., "3.2.1.a"
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert policy to dictionary"""
        return {
            "policy_id": self.policy_id,
            "category": self.category,
            "severity": self.severity.value,
            "description": self.description,
            "detection_pattern": self.detection_pattern,
            "action": self.action,
            "atp_5_19_mapping": self.atp_5_19_mapping,
            "metadata": self.metadata,
        }
