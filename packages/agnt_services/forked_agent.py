# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Forked Agent — Isolated subagent context with prompt cache sharing.

Ported from src/utils/forkedAgent.ts (690 lines).

Provides machinery for running forked agent query loops where the fork
shares the parent's prompt cache key by threading identical cache-critical
parameters (system prompt, tools, model, messages prefix, thinking config).
"""

from __future__ import annotations

import copy
import logging
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)

try:
  from uuid_extensions import uuid7
except ImportError:
  from uuid import uuid4 as uuid7


@dataclass(frozen=True, slots=True)
class CacheSafeParams:
  """Parameters that must be identical between fork and parent for cache hits."""

  system_prompt: str
  user_context: dict[str, str] = field(default_factory=dict)
  system_context: dict[str, str] = field(default_factory=dict)
  fork_context_messages: list[dict[str, Any]] = field(default_factory=list)
  tool_definitions: list[dict[str, Any]] | None = None
  model: str | None = None


_last_cache_safe_params: CacheSafeParams | None = None


def save_cache_safe_params(params: CacheSafeParams | None) -> None:
  """Store the most recent cache-safe params from the main query loop."""
  global _last_cache_safe_params
  _last_cache_safe_params = params


def get_last_cache_safe_params() -> CacheSafeParams | None:
  """Retrieve the most recent cache-safe params for post-turn forks."""
  return _last_cache_safe_params


@dataclass(slots=True)
class TokenUsage:
  """Accumulated token usage across all API calls in a fork loop."""

  input_tokens: int = 0
  output_tokens: int = 0
  cache_read_input_tokens: int = 0
  cache_creation_input_tokens: int = 0
  service_tier: str = ""

  @property
  def total_input_tokens(self) -> int:
    return (
      self.input_tokens
      + self.cache_read_input_tokens
      + self.cache_creation_input_tokens
    )

  @property
  def cache_hit_rate(self) -> float:
    total = self.total_input_tokens
    return self.cache_read_input_tokens / total if total else 0.0


def accumulate_usage(current: TokenUsage, delta: TokenUsage) -> TokenUsage:
  """Merge delta usage into current, returning a new TokenUsage."""
  return TokenUsage(
    input_tokens=current.input_tokens + delta.input_tokens,
    output_tokens=current.output_tokens + delta.output_tokens,
    cache_read_input_tokens=current.cache_read_input_tokens
    + delta.cache_read_input_tokens,
    cache_creation_input_tokens=current.cache_creation_input_tokens
    + delta.cache_creation_input_tokens,
    service_tier=delta.service_tier or current.service_tier,
  )


@dataclass
class SubagentContextOverrides:
  """Options for creating an isolated subagent context."""

  agent_id: str | None = None
  agent_type: str | None = None
  messages: list[dict[str, Any]] | None = None
  share_abort_controller: bool = False
  share_set_app_state: bool = False
  critical_system_reminder: str | None = None
  require_can_use_tool: bool = False


@dataclass
class SubagentContext:
  """Isolated execution context for a forked subagent."""

  agent_id: str = ""
  agent_type: str | None = None
  messages: list[dict[str, Any]] = field(default_factory=list)
  memory_triggers: set[str] = field(default_factory=set)
  discovered_skill_names: set[str] = field(default_factory=set)
  query_chain_id: str = ""
  query_depth: int = 0

  def __post_init__(self) -> None:
    if not self.agent_id:
      self.agent_id = str(uuid7())
    if not self.query_chain_id:
      self.query_chain_id = str(uuid7())


def create_subagent_context(
  parent_messages: list[dict[str, Any]] | None = None,
  overrides: SubagentContextOverrides | None = None,
  parent_depth: int = -1,
) -> SubagentContext:
  """Create an isolated context for a subagent."""
  overrides = overrides or SubagentContextOverrides()
  messages = (
    overrides.messages
    if overrides.messages is not None
    else copy.deepcopy(parent_messages or [])
  )
  return SubagentContext(
    agent_id=overrides.agent_id or str(uuid7()),
    agent_type=overrides.agent_type,
    messages=messages,
    query_depth=parent_depth + 1,
  )


@dataclass(frozen=True, slots=True)
class ForkedAgentResult:
  """Result from a completed forked agent query loop."""

  messages: list[dict[str, Any]]
  total_usage: TokenUsage


QueryFn = Callable[..., Any]
OnMessageFn = Callable[[dict[str, Any]], None]


async def run_forked_agent(
  *,
  prompt_messages: list[dict[str, Any]],
  cache_safe_params: CacheSafeParams,
  fork_label: str,
  query_source: str,
  query_fn: QueryFn | None = None,
  overrides: SubagentContextOverrides | None = None,
  max_output_tokens: int | None = None,
  max_turns: int | None = None,
  on_message: OnMessageFn | None = None,
  skip_transcript: bool = False,
  skip_cache_write: bool = False,
) -> ForkedAgentResult:
  """Run a forked agent query loop with usage tracking."""
  start_time = time.monotonic()
  output_messages: list[dict[str, Any]] = []
  total_usage = TokenUsage()
  context = create_subagent_context(
    parent_messages=cache_safe_params.fork_context_messages,
    overrides=overrides,
  )
  initial_messages = [*cache_safe_params.fork_context_messages, *prompt_messages]

  try:
    if query_fn is not None:
      async for message in query_fn(
        messages=initial_messages,
        system_prompt=cache_safe_params.system_prompt,
        query_source=query_source,
        max_output_tokens=max_output_tokens,
        max_turns=max_turns,
      ):
        if isinstance(message, dict):
          if message.get("type") == "stream_event":
            event = message.get("event", {})
            if event.get("type") == "message_delta" and "usage" in event:
              delta = TokenUsage(
                input_tokens=event["usage"].get("input_tokens", 0),
                output_tokens=event["usage"].get("output_tokens", 0),
                cache_read_input_tokens=event["usage"].get(
                  "cache_read_input_tokens", 0
                ),
                cache_creation_input_tokens=event["usage"].get(
                  "cache_creation_input_tokens", 0
                ),
              )
              total_usage = accumulate_usage(total_usage, delta)
            continue
          if message.get("type") == "stream_request_start":
            continue
        output_messages.append(message)
        if on_message is not None:
          on_message(message)
  finally:
    initial_messages.clear()
    context.messages.clear()

  duration_ms = (time.monotonic() - start_time) * 1000
  logger.debug(
    "Forked agent [%s] finished: %d messages, %.0fms, cache_hit=%.2f",
    fork_label,
    len(output_messages),
    duration_ms,
    total_usage.cache_hit_rate,
  )
  return ForkedAgentResult(messages=output_messages, total_usage=total_usage)


def extract_result_text(
  messages: list[dict[str, Any]],
  default_text: str = "Execution completed",
) -> str:
  """Extract text from the last assistant message."""
  for msg in reversed(messages):
    if msg.get("type") == "assistant" or msg.get("role") == "assistant":
      content = msg.get("content", "")
      if isinstance(content, str) and content.strip():
        return content
      if isinstance(content, list):
        texts = [
          b.get("text", "")
          for b in content
          if isinstance(b, dict) and b.get("type") == "text"
        ]
        joined = "\n".join(t for t in texts if t)
        if joined:
          return joined
  return default_text


__all__ = [
  "CacheSafeParams",
  "ForkedAgentResult",
  "SubagentContext",
  "SubagentContextOverrides",
  "TokenUsage",
  "accumulate_usage",
  "create_subagent_context",
  "extract_result_text",
  "get_last_cache_safe_params",
  "run_forked_agent",
  "save_cache_safe_params",
]
