# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Pnkln Agents: Collection → Enforcement Pipeline

Provides:
- Gemini Ingestion Layer (Intelligence collection with ethical compliance)
- JR Engine (Purpose/Reasons/Brakes validator)
- Judge #6 Lite (Rule-based enforcement)
- Agent Pattern (Integrated collection → enforcement workflow)
- Intelligence Agent (Complete pipeline)
- Compliance SDR Agent (GDPR/CAN-SPAM lead generation)
"""

# Collection (upstream)
from .core.gemini_ingestion import (
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

# Enforcement (downstream)
from .core.jr_engine import JREngine, Purpose, Reason, JRDecision, BrakeType, RiskLevel
from .core.judge_six_lite import JudgeSixLite, VerificationResult, Violation, ViolationType, ViolationSeverity
from .core.agent_pattern import PnklnAgent, AgentTask, AgentResult, AgentStatus, SimpleAgent

# Agents
from .agents.compliance_sdr import ComplianceSDRAgent, Lead, LeadStatus, LeadGenerationResult
from .agents.intelligence_agent import IntelligenceAgent, IntelligenceTask, IntelligenceResult

# Config
from .config.constraints import BootstrapConstraints, DEFAULT_CONSTRAINTS
from .config.revenue_model import RevenueModel, PricingTier, TierPricing, DEFAULT_REVENUE_MODEL
from .config.ingestion_config import (
    IngestionConfig,
    DEFAULT_INGESTION_CONFIG,
    DEFAULT_SOURCES,
    SOURCE_TYPE_REQUIREMENTS,
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
    "PnklnAgent",
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
