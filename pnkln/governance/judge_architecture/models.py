# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Core data structures for the Judge Architecture.

Extracted from the monolithic judge_architecture.py into a standalone
module with zero external dependencies (no kosmos, no numpy).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class DecisionStatus(Enum):
    """Judge verdict status."""

    APPROVED = "APPROVED"
    DEFERRED = "DEFERRED"
    REJECTED = "REJECTED"
    PENDING = "PENDING"


class RiskLevel(Enum):
    """Risk classification (ATP 5-19 aligned)."""

    EXTREMELY_HIGH = "EH"
    HIGH = "H"
    MEDIUM = "M"
    LOW = "L"

    def get_consensus_threshold(self) -> float:
        """Get ATP 5-19 consensus threshold for this risk level."""
        thresholds = {
            RiskLevel.EXTREMELY_HIGH: 0.90,
            RiskLevel.HIGH: 0.75,
            RiskLevel.MEDIUM: 0.60,
            RiskLevel.LOW: 0.50,
        }
        return thresholds.get(self, 0.60)


class RegulatoryFramework(Enum):
    """Supported regulatory frameworks."""

    EU_AI_ACT = "eu_ai_act"
    DSA_VLOP = "dsa_vlop"
    GDPR = "gdpr"
    CPRA = "cpra"
    COPPA = "coppa"
    AADC = "aadc"
    FTC_ENDORSEMENTS = "ftc_endorsements"
    APP_STORE_ATT = "app_store_att"


@dataclass
class Decision:
    """Decision to be validated by Judge Architecture."""

    id: str
    type: str  # "strategic", "tactical", "operational", "procurement"
    description: str
    risk_level: str  # "low", "medium", "high", "extremely_high"

    # Impact flags
    impacts_monetization: bool = False
    impacts_infrastructure: bool = False
    introduces_dependencies: bool = False
    ships_feature: bool = False
    involves_blockchain: bool = False

    # Feature-specific metadata
    feature_name: str | None = None
    variant_id: str | None = None
    metrics: dict[str, Any] = field(default_factory=dict)

    # Context
    submitted_by: str = "system"
    submitted_at: datetime = field(default_factory=datetime.now)


@dataclass
class ComplianceCheck:
    """Result of regulatory compliance check."""

    framework: RegulatoryFramework
    compliant: bool
    gaps: list[str] = field(default_factory=list)
    remediation: list[str] = field(default_factory=list)
    risk_level: RiskLevel = RiskLevel.LOW


@dataclass
class JudgeVerdict:
    """Complete Judge Architecture verdict."""

    decision_id: str
    status: DecisionStatus
    reason: str
    layer_results: dict[str, Any] = field(default_factory=dict)
    blockers: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    next_actions: list[str] = field(default_factory=list)
    valuation_impact: float | None = None
    processing_time_ms: float = 0.0
    iq_level: int = 160


__all__ = [
    "ComplianceCheck",
    "Decision",
    "DecisionStatus",
    "JudgeVerdict",
    "RegulatoryFramework",
    "RiskLevel",
]
