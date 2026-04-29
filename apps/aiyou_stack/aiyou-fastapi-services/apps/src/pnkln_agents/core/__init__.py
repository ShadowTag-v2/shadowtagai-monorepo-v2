# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Core components: Collection and Enforcement"""

from .agent_pattern import (  # noqa: F401
    AgentResult,
    AgentStatus,
    AgentTask,
    PnklnAgent,
    SimpleAgent,
)
from .Claude_Code_6_lite import (
    JudgeSixLite,
    VerificationResult,
    Violation,
    ViolationSeverity,
    ViolationType,
)
from .gemini_ingestion import (
    EthicalComplianceValidator,
    EthicalViolation,
    EthicalViolationType,
    GeminiIngestionLayer,
    IngestedItem,
    IngestionMetrics,
    IngestionResult,
    Source,
    SourceTier,
    SourceType,
    TierClassifier,
)
from .jr_engine import BrakeType, JRDecision, JREngine, Purpose, Reason, RiskLevel

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
    "ShadowTagAiAgent",
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
