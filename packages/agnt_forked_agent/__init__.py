# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Forked Agent — Isolated subagent execution with cache-safe parameter sharing.

Synthesized from Claude Code v2.1.91 production patterns:
  - forkedAgent.ts: CacheSafeParams, SubagentContextOverrides, createSubagentContext
  - forkedAgent.ts L345-414: Isolation of mutable state to prevent parent interference
  - forkedAgent.ts L70-81: Cache-safe parameter slot for prompt cache sharing

Adds typed Python dataclasses, async context manager lifecycle, and deep-copy
isolation that CC's JS object spread doesn't guarantee.

Usage:
    from agnt_forked_agent import (
        ForkedAgent, CacheSafeParams, SubagentContextOverrides,
        ForkedAgentResult,
    )

    # Create cache-safe params from parent context
    params = CacheSafeParams(
        system_prompt="You are a helpful assistant.",
        user_context={"key": "value"},
        system_context={"key": "value"},
        model="gemini-3.1-flash-lite-preview-thinking",
        context_messages=[],
    )

    # Fork with isolation
    agent = ForkedAgent(
        label="session_memory",
        cache_safe_params=params,
        max_turns=5,
    )
    result = await agent.execute(prompt="Summarize the conversation.")

    # Context manager usage
    async with ForkedAgent(label="speculation", cache_safe_params=params) as fork:
        result = await fork.execute(prompt="Predict next action.")
"""

from agnt_forked_agent.core import (
    CacheSafeParams,
    ForkedAgent,
    ForkedAgentResult,
    SubagentContext,
    SubagentContextOverrides,
)

__all__ = [
    "CacheSafeParams",
    "ForkedAgent",
    "ForkedAgentResult",
    "SubagentContext",
    "SubagentContextOverrides",
]
