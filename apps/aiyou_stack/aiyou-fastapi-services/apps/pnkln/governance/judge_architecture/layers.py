# ruff: noqa: F401, F403
"""
Judge Architecture: Backward-Compatibility Barrel File
=======================================================

Original monolith (1192 lines) decomposed into domain-specific modules:
- models.py        → Decision, JudgeVerdict, DecisionStatus, RiskLevel
- regulatory.py    → RegulatoryComplianceEngine, AdtechStandardsValidator
- infrastructure.py → InfrastructureOptimizer, SupplyChainSecurityGate
- product.py       → ProductDeliveryGate, BlockchainIntegrationEvaluator
- analytics.py     → CompetitiveRealityCheck, MilestoneTracker, QuantifiedImpactModel
- monitor.py       → JudgeArchitectureMonitor
- judge.py         → JudgeArchitecture (thin orchestrator)
- formatter.py     → JudgeVerdictFormatter

This file re-exports ALL public symbols for backward compatibility.
New code should import from the specific submodules directly.

Author: Pinkln Ultrathink Architecture Team
Date: 2025-11-17
Status: v2.0.0 — Rich Hickey Refactor (barrel re-export)
"""

# Core data models
# Analytics and tracking
from .analytics import (
    CompetitiveRealityCheck,
    MilestoneTracker,
    QuantifiedImpactModel,
)

# Output formatting
from .formatter import JudgeVerdictFormatter

# Infrastructure optimization
from .infrastructure import (
    InfrastructureOptimizer,
    SupplyChainSecurityGate,
)

# Main orchestrator
from .judge import JudgeArchitecture
from .models import (
    Decision,
    DecisionStatus,
    JudgeVerdict,
    RiskLevel,
)

# System monitoring
from .monitor import JudgeArchitectureMonitor

# Product delivery gates
from .product import (
    BlockchainIntegrationEvaluator,
    ProductDeliveryGate,
)

# Regulatory compliance
from .regulatory import (
    AdtechStandardsValidator,
    RegulatoryComplianceEngine,
)

__all__ = [
    # Models
    "Decision",
    "DecisionStatus",
    "JudgeVerdict",
    "RiskLevel",
    # Regulatory
    "RegulatoryComplianceEngine",
    "AdtechStandardsValidator",
    # Infrastructure
    "InfrastructureOptimizer",
    "SupplyChainSecurityGate",
    # Product
    "ProductDeliveryGate",
    "BlockchainIntegrationEvaluator",
    # Analytics
    "CompetitiveRealityCheck",
    "MilestoneTracker",
    "QuantifiedImpactModel",
    # Monitor
    "JudgeArchitectureMonitor",
    # Judge
    "JudgeArchitecture",
    # Formatter
    "JudgeVerdictFormatter",
]
