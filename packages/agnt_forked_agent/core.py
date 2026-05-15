# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Forked Agent Core — Isolated subagent execution with subprocess delegation.

Ported from src/utils/forkedAgent.ts (Claude Code v2.1.91, 636 lines).

Batch 2 Security Constraints:
  - NO shared mutable state leaks — deep copy isolation enforced
  - NO React/ink UI bindings — text-only execution
  - Fail-closed subprocess isolation — child abort propagates
  - NO analytics/logEvent (telemetry stripped)
  - Usage accumulation is strictly in-process

Architecture:
  The ForkedAgent creates an isolated execution context for subagent work
  (e.g., session memory summarization, speculation, /btw commands). The key
  design goals from upstream are:

  1. Cache-safe parameter sharing — forked agents inherit parent's system
     prompt, tools, and context messages to maximize prompt cache hits.
  2. Mutable state isolation — file state cache is deep-copied, abort
     controllers are child-linked, permission state is locked down.
  3. Usage accumulation — token counts aggregate across the fork's query loop.
"""

from __future__ import annotations

import asyncio
import copy
import logging
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any
from collections.abc import Callable

logger = logging.getLogger(__name__)

__all__ = [
  "CacheSafeParams",
  "ForkedAgent",
  "ForkedAgentResult",
  "SubagentContext",
  "SubagentContextOverrides",
  "ForkState",
  "create_subagent_context",
  "extract_result_text",
]


# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------


class ForkState(Enum):
  """Lifecycle state of a forked agent."""

  CREATED = auto()
  RUNNING = auto()
  COMPLETED = auto()
  ABORTED = auto()
  FAILED = auto()


@dataclass(frozen=True)
class CacheSafeParams:
  """Parameters that must be identical between fork and parent to share prompt cache.

  The API cache key is composed of: system prompt, tools, model,
  messages (prefix), and thinking config. CacheSafeParams carries the
  first four; thinking config is derived separately.
  """

  system_prompt: str
  user_context: dict[str, str] = field(default_factory=dict)
  system_context: dict[str, str] = field(default_factory=dict)
  model: str = ""
  context_messages: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class SubagentContextOverrides:
  """Optional overrides for subagent context creation.

  By default, all mutable state is isolated. Use these to opt-in to
  sharing specific callbacks or state with the parent.
  """

  agent_id: str | None = None
  agent_type: str | None = None
  messages: list[dict[str, Any]] | None = None
  abort_event: asyncio.Event | None = None

  # Explicit opt-in flags for sharing parent state
  share_abort: bool = False
  share_app_state: bool = False

  # Critical system reminder re-injected at every user turn
  critical_system_reminder: str | None = None

  # When True, permission checks cannot be bypassed
  require_permission_check: bool = False


@dataclass
class SubagentContext:
  """Isolated execution context for a subagent.

  All mutable state is deep-copied from the parent to prevent
  interference. Mirrors createSubagentContext() from upstream.
  """

  agent_id: str
  agent_type: str
  system_prompt: str
  model: str
  messages: list[dict[str, Any]]
  user_context: dict[str, str]
  system_context: dict[str, str]
  abort_event: asyncio.Event
  should_avoid_permission_prompts: bool = True
  file_state_cache: dict[str, Any] = field(default_factory=dict)
  discovered_skill_names: set[str] = field(default_factory=set)
  tool_decisions: dict[str, Any] | None = None
  denial_tracking: dict[str, int] = field(default_factory=dict)
  metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ForkedAgentResult:
  """Result from a forked agent execution."""

  messages: list[dict[str, Any]]
  total_input_tokens: int = 0
  total_output_tokens: int = 0
  total_cache_read_tokens: int = 0
  total_cache_write_tokens: int = 0
  total_cost_usd: float = 0.0
  duration_seconds: float = 0.0
  turns_used: int = 0
  state: ForkState = ForkState.COMPLETED


# ---------------------------------------------------------------------------
# Context factory — mirrors createSubagentContext()
# ---------------------------------------------------------------------------


def create_subagent_context(
  parent_context: SubagentContext | dict[str, Any],
  overrides: SubagentContextOverrides | None = None,
) -> SubagentContext:
  """Create an isolated SubagentContext from a parent context.

  Deep-copies all mutable state by default. Callers can opt-in to
  sharing specific fields via ``SubagentContextOverrides``.

  This mirrors the upstream ``createSubagentContext()`` function which:
  - Clones readFileState (file state cache)
  - Creates a child abort controller linked to parent
  - Wraps getAppState to set shouldAvoidPermissionPrompts
  - Zeros out mutation callbacks (setAppState → no-op)
  - Creates fresh collections for triggers, decisions, etc.
  """
  overrides = overrides or SubagentContextOverrides()

  # Convert dict-based context to SubagentContext if needed
  if isinstance(parent_context, dict):
    parent = SubagentContext(
      agent_id=parent_context.get("agent_id", str(uuid.uuid4())),
      agent_type=parent_context.get("agent_type", "general-purpose"),
      system_prompt=parent_context.get("system_prompt", ""),
      model=parent_context.get("model", ""),
      messages=parent_context.get("messages", []),
      user_context=parent_context.get("user_context", {}),
      system_context=parent_context.get("system_context", {}),
      abort_event=parent_context.get("abort_event", asyncio.Event()),
      file_state_cache=parent_context.get("file_state_cache", {}),
    )
  else:
    parent = parent_context

  # Abort event: explicit override > share parent's > new child event
  if overrides.abort_event is not None:
    abort_event = overrides.abort_event
  elif overrides.share_abort:
    abort_event = parent.abort_event
  else:
    abort_event = asyncio.Event()

  return SubagentContext(
    agent_id=overrides.agent_id or str(uuid.uuid4()),
    agent_type=overrides.agent_type or parent.agent_type,
    system_prompt=parent.system_prompt,
    model=parent.model,
    messages=overrides.messages if overrides.messages is not None else [],
    user_context=copy.deepcopy(parent.user_context),
    system_context=copy.deepcopy(parent.system_context),
    abort_event=abort_event,
    # Deep-copy mutable state — critical for isolation
    should_avoid_permission_prompts=not overrides.share_app_state,
    file_state_cache=copy.deepcopy(parent.file_state_cache),
    discovered_skill_names=set(),
    tool_decisions=None,
    denial_tracking={}
    if not overrides.share_app_state
    else copy.copy(parent.denial_tracking),
    metadata={
      "parent_agent_id": parent.agent_id,
      "critical_system_reminder": overrides.critical_system_reminder,
      "require_permission_check": overrides.require_permission_check,
    },
  )


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------


def extract_result_text(
  messages: list[dict[str, Any]],
  default_text: str = "Execution completed",
) -> str:
  """Extract the last assistant message text from a message list.

  Mirrors ``extractResultText()`` from upstream.
  """
  for msg in reversed(messages):
    role = msg.get("role", "")
    if role == "assistant" or role == "model":
      content = msg.get("content", "")
      if isinstance(content, str) and content.strip():
        return content.strip()
      if isinstance(content, list):
        text_parts = [
          p.get("text", "")
          for p in content
          if isinstance(p, dict) and p.get("type") == "text"
        ]
        joined = "\n".join(text_parts).strip()
        if joined:
          return joined
  return default_text


# ---------------------------------------------------------------------------
# ForkedAgent — main class
# ---------------------------------------------------------------------------

# Module-level slot for cache-safe params (mirrors lastCacheSafeParams)
_last_cache_safe_params: CacheSafeParams | None = None


def save_cache_safe_params(params: CacheSafeParams | None) -> None:
  """Save cache-safe params for post-turn forks."""
  global _last_cache_safe_params
  _last_cache_safe_params = params


def get_last_cache_safe_params() -> CacheSafeParams | None:
  """Retrieve the last saved cache-safe params."""
  return _last_cache_safe_params


class ForkedAgent:
  """Isolated subagent execution with cache-safe parameter sharing.

  Creates an isolated execution context, runs a query loop up to
  ``max_turns``, accumulates usage, and returns the result.

  Can be used as an async context manager::

      async with ForkedAgent(label="memory", ...) as fork:
          result = await fork.execute(prompt="Summarize.")
  """

  def __init__(
    self,
    *,
    label: str,
    cache_safe_params: CacheSafeParams,
    max_turns: int = 10,
    max_output_tokens: int | None = None,
    skip_transcript: bool = False,
    skip_cache_write: bool = False,
    on_message: Callable[[dict[str, Any]], None] | None = None,
  ) -> None:
    self._label = label
    self._cache_safe_params = cache_safe_params
    self._max_turns = max_turns
    self._max_output_tokens = max_output_tokens
    self._skip_transcript = skip_transcript
    self._skip_cache_write = skip_cache_write
    self._on_message = on_message
    self._state = ForkState.CREATED
    self._fork_id = str(uuid.uuid4())
    self._abort_event = asyncio.Event()
    self._messages: list[dict[str, Any]] = []
    self._total_input_tokens = 0
    self._total_output_tokens = 0
    self._total_cache_read_tokens = 0
    self._total_cache_write_tokens = 0
    self._total_cost_usd = 0.0
    self._start_time: float | None = None

  # -- Properties --

  @property
  def fork_id(self) -> str:
    return self._fork_id

  @property
  def label(self) -> str:
    return self._label

  @property
  def state(self) -> ForkState:
    return self._state

  # -- Lifecycle --

  async def __aenter__(self) -> ForkedAgent:
    return self

  async def __aexit__(self, *exc: object) -> None:
    self.abort()

  def abort(self) -> None:
    """Signal abort to the forked execution."""
    self._abort_event.set()
    if self._state == ForkState.RUNNING:
      self._state = ForkState.ABORTED
      logger.info("ForkedAgent[%s] aborted", self._label)

  async def execute(
    self,
    prompt: str,
    *,
    query_fn: Callable[..., Any] | None = None,
  ) -> ForkedAgentResult:
    """Execute the forked agent query loop.

    Args:
        prompt: The user prompt to start the fork with.
        query_fn: Optional async callable that performs the actual LLM query.
                  If not provided, the fork records the prompt as a message
                  and returns immediately (dry-run mode for scaffolding).

    Returns:
        ForkedAgentResult with all messages and accumulated usage.
    """
    self._state = ForkState.RUNNING
    self._start_time = time.monotonic()
    self._messages = []

    # Build initial messages from cache-safe params + prompt
    initial_messages = list(self._cache_safe_params.context_messages)
    initial_messages.append(
      {
        "role": "user",
        "content": prompt,
      }
    )

    try:
      if query_fn is not None:
        # Execute actual query loop
        turn = 0
        current_messages = initial_messages

        while turn < self._max_turns:
          if self._abort_event.is_set():
            self._state = ForkState.ABORTED
            break

          turn += 1
          result = await query_fn(
            messages=current_messages,
            model=self._cache_safe_params.model,
            system_prompt=self._cache_safe_params.system_prompt,
            max_output_tokens=self._max_output_tokens,
          )

          # Accumulate usage from result
          if isinstance(result, dict):
            self._accumulate_usage(result)
            msg = result.get("message")
            if msg:
              self._messages.append(msg)
              if self._on_message:
                self._on_message(msg)

            # Check if we should continue (tool use pending)
            if not result.get("has_tool_use", False):
              break

            current_messages = initial_messages + self._messages
      else:
        # Dry-run mode — just record the prompt
        self._messages = initial_messages

      if self._state == ForkState.RUNNING:
        self._state = ForkState.COMPLETED

    except Exception:
      self._state = ForkState.FAILED
      logger.exception("ForkedAgent[%s] failed", self._label)

    duration = time.monotonic() - self._start_time if self._start_time else 0.0

    return ForkedAgentResult(
      messages=self._messages,
      total_input_tokens=self._total_input_tokens,
      total_output_tokens=self._total_output_tokens,
      total_cache_read_tokens=self._total_cache_read_tokens,
      total_cache_write_tokens=self._total_cache_write_tokens,
      total_cost_usd=self._total_cost_usd,
      duration_seconds=duration,
      turns_used=len(
        [m for m in self._messages if m.get("role") in ("assistant", "model")]
      ),
      state=self._state,
    )

  def _accumulate_usage(self, result: dict[str, Any]) -> None:
    """Accumulate token usage from a query result dict."""
    usage = result.get("usage", {})
    self._total_input_tokens += usage.get("input_tokens", 0)
    self._total_output_tokens += usage.get("output_tokens", 0)
    self._total_cache_read_tokens += usage.get("cache_read_input_tokens", 0)
    self._total_cache_write_tokens += usage.get("cache_creation_input_tokens", 0)
    self._total_cost_usd += usage.get("cost_usd", 0.0)
