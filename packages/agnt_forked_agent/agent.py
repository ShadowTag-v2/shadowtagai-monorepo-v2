"""
agnt_forked_agent: Isolated Subagent Execution Environment
Ports the cache-safe and mutable-state-isolated patterns from Claude Code v2.1.91 (Tengu)
"""

import time
from typing import Any


class CacheSafeParams:
    def __init__(self, system_prompt: str, user_context: dict, system_context: dict):
        self.system_prompt = system_prompt
        self.user_context = user_context
        self.system_context = system_context


class ToolUseContext:
    def __init__(self):
        self.read_file_state = {}
        self.abort_controller = None


def create_subagent_context(parent_context: ToolUseContext, overrides: dict | None = None) -> ToolUseContext:
    """
    Creates an isolated ToolUseContext for subagents, preventing parent state mutation.
    """
    ctx = ToolUseContext()
    ctx.read_file_state = dict(parent_context.read_file_state)  # Clone
    # Inherit or override
    return ctx


def run_forked_agent(
    prompt_messages: list[dict], cache_safe_params: CacheSafeParams, fork_label: str, query_source: str, parent_context: ToolUseContext
) -> dict[str, Any]:
    """
    Runs a forked agent query loop and tracks usage/cache hits.
    Shares identical cache-critical params with the parent to guarantee prompt cache hits.
    """
    start_time = time.time()
    create_subagent_context(parent_context)

    # Execution logic omitted for AST brevity
    output_messages = []

    duration_ms = int((time.time() - start_time) * 1000)

    return {"messages": output_messages, "total_usage": {"input_tokens": 0, "output_tokens": 0}, "duration_ms": duration_ms}
