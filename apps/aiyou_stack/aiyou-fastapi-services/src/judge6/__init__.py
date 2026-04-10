"""
Judge #6 Governance Engine - LangGraph Implementation

This module implements what Antigravity promised but didn't deliver:
- LangGraph state machine for governance kill chain
- Mem0 integration for sovereign memory
- PostgreSQL + Redis backend for persistence

Kill Chain: OPA Fast Check → Judge#6 Reasoning → Audit Logger
"""

from .core import GovernanceEngine, create_governance_graph
from .memory import SovereignMemory
from .state import AssessmentState, AuditState, DebateState, GovernanceState

__all__ = [
    "create_governance_graph",
    "GovernanceEngine",
    "GovernanceState",
    "AssessmentState",
    "DebateState",
    "AuditState",
    "SovereignMemory",
]

__version__ = "1.0.0"
