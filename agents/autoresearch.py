"""
DEPRECATED: agents.autoresearch → pnkln.agents

Shim for backwards compatibility. Canonical class is now CorAutoresearch.

All new code:    from pnkln.agents import CorAutoresearch
Legacy code:     from agents.autoresearch import Autoresearch  ← still works
                 from agents.autoresearch import AgentOrchestrator  ← still works
"""
from pnkln.agents import (
    CorAutoresearch,
    CorAutoresearch as AgentOrchestrator,
    CorAutoresearch as Autoresearch,
    AgentState,
    AgentState as AgentUnit,  # callers that use AgentUnit
    AgentTier,
    AgentSpecialization,
    AgentContainment,
    CircuitBreaker,
    SelfHealingState,
    LLMProvider,
    MNFST,
    Note,
    SauronsPanorama,
    LegalReasoningFramework,
    CircuitState,
    ContainmentLevel,
    UnitType,
    ShiftRotation,
    LegalWhiteboard,
    AntigravityRouter,
    ComputerUseSpawner,
    LLMConfig,
)

__all__ = [
    "CorAutoresearch", "AgentOrchestrator", "Autoresearch",
    "AgentState", "AgentUnit",
    "AgentTier", "AgentSpecialization", "AgentContainment",
    "CircuitBreaker", "SelfHealingState", "LLMProvider",
    "MNFST", "Note", "SauronsPanorama", "LegalReasoningFramework",
    "CircuitState", "ContainmentLevel", "UnitType", "ShiftRotation",
    "LegalWhiteboard", "AntigravityRouter", "ComputerUseSpawner", "LLMConfig",
]
