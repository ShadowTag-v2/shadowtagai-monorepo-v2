# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Multi-agent framework for Pinkln ecosystem."""

from .base import Agent, AgentConfig, AgentPerformance
from .debate import DebateAgent, DebateOrchestrator, DebateResult, DebateRound

__all__ = [
    "Agent",
    "AgentConfig",
    "AgentPerformance",
    "DebateAgent",
    "DebateOrchestrator",
    "DebateResult",
    "DebateRound",
]
