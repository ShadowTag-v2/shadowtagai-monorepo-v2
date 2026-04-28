# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""ShadowTagAi Agents: Collection → Enforcement Pipeline

Provides:
- Gemini Ingestion Layer (Intelligence collection with ethical compliance)
- JR Engine (Purpose/Reasons/Brakes validator)
- Judge 6 Lite (Rule-based enforcement)
- Agent Pattern (Integrated collection → enforcement workflow)
- Intelligence Agent (Complete pipeline)
- Compliance SDR Agent (GDPR/CAN-SPAM lead generation)
"""

# Collection (upstream)
# Agents
from .agents.compliance_sdr import (
    ComplianceSDRAgent,
    Lead,
    LeadGenerationResult,
    LeadStatus,
)
from .agents.intelligence_agent import (
    IntelligenceAgent,
    IntelligenceResult,
    IntelligenceTask,
)

# Config
from .config.constraints import DEFAULT_CONSTRAINTS, BootstrapConstraints
from .config.ingestion_config import (
    DEFAULT_INGESTION_CONFIG,
    DEFAULT_SOURCES,
    SOURCE_TYPE_REQUIREMENTS,
    IngestionConfig,
)
from .config.revenue_model import (
    DEFAULT_REVENUE_MODEL,
    PricingTier,
    RevenueModel,
    TierPricing,
)
from .core.agent_pattern import (
    AgentResult,
    AgentStatus,
    AgentTask,
    PnklnAgent,  # noqa: F401
    SimpleAgent,
)
from .core.gemini_ingestion import (
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

# Enforcement (downstream)
from .core.jr_engine import BrakeType, JRDecision, JREngine, Purpose, Reason, RiskLevel
from .core.judge_six_lite import (
    JudgeSixLite,
    VerificationResult,
    Violation,
    ViolationSeverity,
    ViolationType,
)

__version__ = "0.2.0"  # Updated for dual-layer architecture

__all__ = [
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
    # Agents
    "ComplianceSDRAgent",
    "Lead",
    "LeadStatus",
    "LeadGenerationResult",
    "IntelligenceAgent",
    "IntelligenceTask",
    "IntelligenceResult",
    # Config
    "BootstrapConstraints",
    "DEFAULT_CONSTRAINTS",
    "RevenueModel",
    "PricingTier",
    "TierPricing",
    "DEFAULT_REVENUE_MODEL",
    "IngestionConfig",
    "DEFAULT_INGESTION_CONFIG",
    "DEFAULT_SOURCES",
    "SOURCE_TYPE_REQUIREMENTS",
]
