# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Kosmos-pattern autonomous agent system for Google Cloud Platform.

Combines:
- Kosmos principle: Long-horizon autonomous workflows with world-model coordination
- ReAct algorithm: Reason → Act → Observe loop
- AgentOps: Full observability and operational excellence
"""

__version__ = "0.1.0"

from kosmos.core.world_model import KosmosWorldModel, WorkflowPhase
from kosmos.core.orchestrator import ReActOrchestrator
from kosmos.agents.base import BaseAgent

__all__ = [
  "KosmosWorldModel",
  "WorkflowPhase",
  "ReActOrchestrator",
  "BaseAgent",
]
