# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Deep Research — Deterministic multi-phase architectural planning engine.

Architecture (inspired by Claude Code autoDream + speculation patterns):
  State Machine:  IDLE → PLANNING → RESEARCHING → SYNTHESIZING → EXECUTING → VERIFYING → COMPLETE
  Research:       MCP-first query routing (google-developer-knowledge, sequential-thinking)
  Integration:    Context compactor token management, telemetry emission
  Safety:         Phase guards, circuit breakers, abort/rollback per phase

Public API:
  - DeepResearchEngine: Main orchestrator (phase transitions + execution)
  - ResearchPhase: Enum of all valid phases
  - ResearchConfig: Configuration dataclass
  - ResearchResult: Phase execution result
  - PhaseTransition: Recorded state transition with metadata
  - ResearchQuery: Typed research query for MCP routing
"""

from deep_research.state_machine import (
    DeepResearchEngine,
    PhaseTransition,
    ResearchConfig,
    ResearchPhase,
    ResearchResult,
)
from deep_research.research_router import (
    ResearchQuery,
    QuerySource,
    route_query,
)
from deep_research.synthesis import (
    SynthesisResult,
    synthesize_findings,
)
from deep_research.telemetry import (
    emit_phase_event,
    emit_research_metric,
)

__all__ = [
    # Core engine
    "DeepResearchEngine",
    # State machine
    "ResearchPhase",
    "ResearchConfig",
    "ResearchResult",
    "PhaseTransition",
    # Research routing
    "ResearchQuery",
    "QuerySource",
    "route_query",
    # Synthesis
    "SynthesisResult",
    "synthesize_findings",
    # Telemetry
    "emit_phase_event",
    "emit_research_metric",
]
