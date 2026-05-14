# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Core components: Collection and Enforcement"""

from .jr_engine import JREngine, Purpose, Reason, JRDecision, BrakeType, RiskLevel
from .judge_six_lite import JudgeSixLite, VerificationResult, Violation, ViolationType, ViolationSeverity
from .agent_pattern import PnklnAgent, AgentTask, AgentResult, AgentStatus, SimpleAgent
from .gemini_ingestion import (
    GeminiIngestionLayer,
    Source,
    SourceType,
    SourceTier,
    IngestedItem,
    IngestionResult,
    IngestionMetrics,
    EthicalComplianceValidator,
    EthicalViolation,
    EthicalViolationType,
    TierClassifier,
)

__all__ = [
    # Enforcement (downstream)
    "JREngine",
    "Purpose",
    "Reason",
    "JRDecision",
    "BrakeType",
    "RiskLevel",
    "JudgeSixLite",
    "VerificationResult",
    "Violation",
    "ViolationType",
    "ViolationSeverity",
    "PnklnAgent",
    "AgentTask",
    "AgentResult",
    "AgentStatus",
    "SimpleAgent",
    # Collection (upstream)
    "GeminiIngestionLayer",
    "Source",
    "SourceType",
    "SourceTier",
    "IngestedItem",
    "IngestionResult",
    "IngestionMetrics",
    "EthicalComplianceValidator",
    "EthicalViolation",
    "EthicalViolationType",
    "TierClassifier",
]
