"""
AI Agent Business Plan - Thread Rollup & Transfer Package
Generated: 2025-11-17
Context: AI Agent-as-a-Service (Vertical SaaS Model)

This module captures the complete business plan, technical architecture,
and operational framework for productized AI agent solutions.
"""

from .context import CONTEXT_RESTORATION, ContextRestoration, ImmediateActions
from .decision_framework import (
    DECISION_PROTOCOL,
    RISK_ASSESSMENT,
    DecisionProtocol,
    KillSwitches,
    RiskAssessment,
)
from .development import (
    BOOTSTRAP_DISCIPLINE,
    DEV_CONSTRAINTS,
    FRAMEWORKS,
    OPERATING_PRINCIPLES,
    DevelopmentConstraints,
    Frameworks,
)
from .metrics import BUSINESS_METRICS, UNIT_ECONOMICS, BusinessMetrics, UnitEconomics
from .tech_stack import AGENT_DESIGN, TECH_STACK, AgentDesignPattern, TechStack
from .verticals import VERTICALS, VerticalRevenue

__all__ = [
    # Classes
    "BusinessMetrics",
    "UnitEconomics",
    "VerticalRevenue",
    "TechStack",
    "AgentDesignPattern",
    "DecisionProtocol",
    "RiskAssessment",
    "KillSwitches",
    "DevelopmentConstraints",
    "Frameworks",
    "ContextRestoration",
    "ImmediateActions",
    # Singleton instances
    "BUSINESS_METRICS",
    "UNIT_ECONOMICS",
    "VERTICALS",
    "TECH_STACK",
    "AGENT_DESIGN",
    "DECISION_PROTOCOL",
    "RISK_ASSESSMENT",
    "DEV_CONSTRAINTS",
    "FRAMEWORKS",
    "OPERATING_PRINCIPLES",
    "BOOTSTRAP_DISCIPLINE",
    "CONTEXT_RESTORATION",
]

__version__ = "1.0.0"
__generated__ = "2025-11-17"
