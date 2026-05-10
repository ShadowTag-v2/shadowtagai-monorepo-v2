"""
DEPRECATED: agents.autoresearch → pnkln.agents

Shim for backwards compatibility. Canonical class is now CorAutoresearch.

All new code:    from pnkln.agents import CorAutoresearch
Legacy code:     from agents.autoresearch import Autoresearch  ← still works
                 from agents.autoresearch import AgentOrchestrator  ← still works
"""

from pnkln.agents import (
    MNFST,
    AgentContainment,
    AgentSpecialization,
    AgentState,
    AgentTier,
    AntigravityRouter,
    CircuitBreaker,
    CircuitState,
    ComputerUseSpawner,
    ContainmentLevel,
    CorAutoresearch,
    LegalReasoningFramework,
    LegalWhiteboard,
    LLMConfig,
    LLMProvider,
    Note,
    SauronsPanorama,
    SelfHealingState,
    ShiftRotation,
    UnitType,
)
from pnkln.agents import (
    AgentState as AgentUnit,  # callers that use AgentUnit
)
from pnkln.agents import (
    CorAutoresearch as AgentOrchestrator,
)
from pnkln.agents import (
    CorAutoresearch as Autoresearch,
)

__all__ = [
    "CorAutoresearch",
    "AgentOrchestrator",
    "Autoresearch",
    "AgentState",
    "AgentUnit",
    "AgentTier",
    "AgentSpecialization",
    "AgentContainment",
    "CircuitBreaker",
    "SelfHealingState",
    "LLMProvider",
    "MNFST",
    "Note",
    "SauronsPanorama",
    "LegalReasoningFramework",
    "CircuitState",
    "ContainmentLevel",
    "UnitType",
    "ShiftRotation",
    "LegalWhiteboard",
    "AntigravityRouter",
    "ComputerUseSpawner",
    "LLMConfig",
]
