# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""MCP Tool Wrappers — Gemini API integration for agent orchestration.

Exposes:
    - InteractionsTool: Multi-turn stateful Gemini conversations
    - DeepResearchTool: Autonomous long-form research sweeps (Phase 2)
"""

from __future__ import annotations

from mcp_tools.interactions_wrapper import (
  InteractionsModel,
  InteractionsSession,
  InteractionsTool,
  SessionState,
  TurnResult,
)

__all__ = [
  "InteractionsModel",
  "InteractionsSession",
  "InteractionsTool",
  "SessionState",
  "TurnResult",
]
