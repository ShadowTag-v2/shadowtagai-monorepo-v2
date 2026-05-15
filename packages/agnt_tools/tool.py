# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Tool — Base tool protocol and factory for the AGNT runtime.

Ported from src/Tool.ts (Claude Code v2.1.91, 747 lines).

This module defines:
  - ToolUseContext: The execution context threaded through every tool call
  - Tool (Protocol): Structural contract that all tools must satisfy
  - ValidationResult: Union type for input validation
  - buildTool(): Factory that fills safe defaults for commonly-stubbed methods
  - PermissionResult: Result of permission checks

React/JSX rendering methods are omitted — Python has no equivalent.
UI rendering is handled by the terminal layer (agnt_termio).

Usage:
    from agnt_tools.tool import Tool, ToolUseContext, build_tool

    my_tool = build_tool(
        name="ReadFile",
        input_schema={"type": "object", "properties": {"path": {"type": "string"}}},
        call=my_call_fn,
        description=my_desc_fn,
        prompt=my_prompt_fn,
    )
"""

from __future__ import annotations

import asyncio
import copy
import logging
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Protocol, runtime_checkable

try:
  from uuid_extensions import uuid7  # type: ignore[import-untyped]
except ImportError:
  import uuid as _uuid

  def uuid7() -> _uuid.UUID:  # type: ignore[misc]
    """Fallback to uuid4 when uuid7 is unavailable."""
    return _uuid.uuid4()


__all__ = [
  "FileReadingLimits",
  "GlobLimits",
  "PermissionMode",
  "PermissionResult",
  "QueryChainTracking",
  "Tool",
  "ToolDecision",
  "ToolInputSchema",
  "ToolResult",
  "ToolUseContext",
  "ValidationResult",
  "build_tool",
  "find_tool_by_name",
  "tool_matches_name",
]

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class PermissionMode(StrEnum):
  """Permission enforcement mode."""

  DEFAULT = "default"
  PLAN = "plan"
  AUTO = "auto"
  BYPASS = "bypass"


# ---------------------------------------------------------------------------
# Data types — mirrors TypeScript interfaces
# ---------------------------------------------------------------------------

# JSON Schema for tool input (simplified from Zod)
ToolInputSchema = dict[str, Any]


@dataclass(frozen=True, slots=True)
class QueryChainTracking:
  """Tracks query chain depth for nested agent calls."""

  chain_id: str
  depth: int


@dataclass(frozen=True, slots=True)
class FileReadingLimits:
  """Limits for file reading operations."""

  max_tokens: int | None = None
  max_size_bytes: int | None = None


@dataclass(frozen=True, slots=True)
class GlobLimits:
  """Limits for glob/search operations."""

  max_results: int | None = None


@dataclass(frozen=True, slots=True)
class ToolDecision:
  """Recorded decision for a specific tool use."""

  source: str
  decision: str  # "accept" | "reject"
  timestamp: float


@dataclass
class ToolPermissionContext:
  """Permission context for tool execution.

  Mirrors the DeepImmutable<ToolPermissionContext> from Tool.ts.
  """

  mode: PermissionMode = PermissionMode.DEFAULT
  always_allow_rules: dict[str, list[str]] = field(default_factory=dict)
  always_deny_rules: dict[str, list[str]] = field(default_factory=dict)
  always_ask_rules: dict[str, list[str]] = field(default_factory=dict)
  is_bypass_permissions_mode_available: bool = False
  is_auto_mode_available: bool = False
  should_avoid_permission_prompts: bool = False
  await_automated_checks_before_dialog: bool = False
  pre_plan_mode: PermissionMode | None = None


def get_empty_tool_permission_context() -> ToolPermissionContext:
  """Factory for a default-initialized permission context."""
  return ToolPermissionContext()


@dataclass
class ToolUseContext:
  """Execution context threaded through every tool call.

  Mirrors ToolUseContext from src/Tool.ts. Fields that are React/UI-specific
  are omitted. Mutable state fields use appropriate Python types.
  """

  # --- Core options ---
  model: str = ""
  debug: bool = False
  verbose: bool = False
  is_non_interactive_session: bool = False
  max_budget_usd: float | None = None
  custom_system_prompt: str | None = None
  append_system_prompt: str | None = None

  # --- Abort control ---
  # Python equivalent of AbortController: asyncio.Event
  abort_event: asyncio.Event = field(default_factory=asyncio.Event)

  # --- State ---
  messages: list[dict[str, Any]] = field(default_factory=list)
  tool_permission_context: ToolPermissionContext = field(
    default_factory=get_empty_tool_permission_context
  )

  # --- File state (LRU cache of file contents) ---
  file_state_cache: dict[str, Any] = field(default_factory=dict)

  # --- Tracking ---
  query_tracking: QueryChainTracking | None = None
  file_reading_limits: FileReadingLimits | None = None
  glob_limits: GlobLimits | None = None
  tool_decisions: dict[str, ToolDecision] | None = None

  # --- Agent identity ---
  agent_id: str | None = None
  agent_type: str | None = None

  # --- Nested memory ---
  nested_memory_attachment_triggers: set[str] = field(default_factory=set)
  loaded_nested_memory_paths: set[str] = field(default_factory=set)
  dynamic_skill_dir_triggers: set[str] = field(default_factory=set)
  discovered_skill_names: set[str] = field(default_factory=set)

  # --- Flags ---
  user_modified: bool = False
  require_can_use_tool: bool = False
  preserve_tool_use_results: bool = False

  # --- Critical system reminder (experimental) ---
  critical_system_reminder: str | None = None

  def clone_isolated(self) -> ToolUseContext:
    """Create a deep-copy isolated context for subagent execution.

    Mirrors the isolation guarantees of createSubagentContext in
    forkedAgent.ts — all mutable state is cloned to prevent interference.
    """
    ctx = copy.deepcopy(self)
    # Fresh sets for isolation
    ctx.nested_memory_attachment_triggers = set()
    ctx.loaded_nested_memory_paths = set()
    ctx.dynamic_skill_dir_triggers = set()
    ctx.discovered_skill_names = set()
    ctx.tool_decisions = None
    # Fresh abort event (linked to parent via caller)
    ctx.abort_event = asyncio.Event()
    # Force permission prompts off for subagents
    ctx.tool_permission_context = copy.deepcopy(self.tool_permission_context)
    ctx.tool_permission_context.should_avoid_permission_prompts = True
    # New agent ID
    ctx.agent_id = str(uuid7())
    ctx.agent_type = "forked"  # Cloned contexts are always forked subagents
    return ctx


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------


@dataclass
class ValidationResult:
  """Result of tool input validation.

  When ``valid`` is True, the input is accepted.
  When False, ``message`` and ``error_code`` describe the failure.
  """

  valid: bool
  message: str = ""
  error_code: int = 0


@dataclass
class PermissionResult:
  """Result of a tool permission check.

  Mirrors PermissionResult from src/types/permissions.ts.
  """

  behavior: str  # "allow" | "deny" | "ask"
  updated_input: dict[str, Any] | None = None
  message: str | None = None


@dataclass
class ToolResult:
  """Result returned by a tool's ``call()`` method.

  Mirrors ToolResult<T> from Tool.ts.
  """

  data: Any
  new_messages: list[dict[str, Any]] | None = None
  context_modifier: Any | None = None  # Callable[[ToolUseContext], ToolUseContext]


# ---------------------------------------------------------------------------
# Tool Protocol
# ---------------------------------------------------------------------------


@runtime_checkable
class Tool(Protocol):
  """Structural protocol that all AGNT tools must satisfy.

  Mirrors the Tool type from src/Tool.ts. React rendering methods are
  omitted — the Python runtime uses a separate rendering layer.

  Tools should be created via ``build_tool()`` rather than implementing
  this protocol directly.
  """

  name: str
  input_schema: ToolInputSchema
  max_result_size_chars: int

  # Optional fields
  aliases: list[str]
  search_hint: str | None
  should_defer: bool
  always_load: bool
  strict: bool

  async def call(
    self,
    args: dict[str, Any],
    context: ToolUseContext,
  ) -> ToolResult:
    """Execute the tool with the given arguments and context."""
    ...

  async def description(
    self,
    input_args: dict[str, Any],
    *,
    is_non_interactive: bool = False,
  ) -> str:
    """Return a human-readable description of what this tool call will do."""
    ...

  async def prompt(self, *, tools: list[Any] | None = None) -> str:
    """Return the system prompt contribution for this tool."""
    ...

  def is_enabled(self) -> bool:
    """Whether the tool is currently available."""
    ...

  def is_concurrency_safe(self, input_args: dict[str, Any]) -> bool:
    """Whether this tool can run concurrently with other tool calls."""
    ...

  def is_read_only(self, input_args: dict[str, Any]) -> bool:
    """Whether this tool only reads state (no mutations)."""
    ...

  def is_destructive(self, input_args: dict[str, Any]) -> bool:
    """Whether this tool performs irreversible operations."""
    ...

  async def check_permissions(
    self,
    input_args: dict[str, Any],
    context: ToolUseContext,
  ) -> PermissionResult:
    """Check whether the user has granted permission for this operation."""
    ...

  async def validate_input(
    self,
    input_args: dict[str, Any],
    context: ToolUseContext,
  ) -> ValidationResult:
    """Validate the input arguments before execution."""
    ...

  def to_auto_classifier_input(self, input_args: dict[str, Any]) -> Any:
    """Return a compact representation for the auto-mode security classifier."""
    ...

  def user_facing_name(self, input_args: dict[str, Any] | None = None) -> str:
    """Return a human-readable name for display."""
    ...

  def get_path(self, input_args: dict[str, Any]) -> str | None:
    """Return the file path this tool operates on, if applicable."""
    ...


# ---------------------------------------------------------------------------
# Concrete Tool implementation via build_tool
# ---------------------------------------------------------------------------


class _BuiltTool:
  """Concrete tool built by ``build_tool()``.

  Fills safe defaults for commonly-stubbed methods, mirroring the
  ``buildTool`` factory from Tool.ts (L712-746).

  Defaults (fail-closed where it matters):
  - is_enabled → True
  - is_concurrency_safe → False (assume not safe)
  - is_read_only → False (assume writes)
  - is_destructive → False
  - check_permissions → allow (defer to general permission system)
  - to_auto_classifier_input → "" (skip classifier)
  - user_facing_name → name
  """

  def __init__(
    self,
    *,
    name: str,
    input_schema: ToolInputSchema,
    call_fn: Any,
    description_fn: Any,
    prompt_fn: Any,
    max_result_size_chars: int = 100_000,
    aliases: list[str] | None = None,
    search_hint: str | None = None,
    should_defer: bool = False,
    always_load: bool = False,
    strict: bool = False,
    is_enabled_fn: Any | None = None,
    is_concurrency_safe_fn: Any | None = None,
    is_read_only_fn: Any | None = None,
    is_destructive_fn: Any | None = None,
    check_permissions_fn: Any | None = None,
    validate_input_fn: Any | None = None,
    to_auto_classifier_input_fn: Any | None = None,
    user_facing_name_fn: Any | None = None,
    get_path_fn: Any | None = None,
  ) -> None:
    self.name = name
    self.input_schema = input_schema
    self._call_fn = call_fn
    self._description_fn = description_fn
    self._prompt_fn = prompt_fn
    self.max_result_size_chars = max_result_size_chars
    self.aliases = aliases or []
    self.search_hint = search_hint
    self.should_defer = should_defer
    self.always_load = always_load
    self.strict = strict

    # Defaultable methods
    self._is_enabled_fn = is_enabled_fn or (lambda: True)
    self._is_concurrency_safe_fn = is_concurrency_safe_fn or (lambda _: False)
    self._is_read_only_fn = is_read_only_fn or (lambda _: False)
    self._is_destructive_fn = is_destructive_fn or (lambda _: False)
    self._check_permissions_fn = check_permissions_fn
    self._validate_input_fn = validate_input_fn
    self._to_auto_classifier_input_fn = to_auto_classifier_input_fn or (lambda _: "")
    self._user_facing_name_fn = user_facing_name_fn or (lambda _=None: self.name)
    self._get_path_fn = get_path_fn

  async def call(
    self,
    args: dict[str, Any],
    context: ToolUseContext,
  ) -> ToolResult:
    return await self._call_fn(args, context)

  async def description(
    self,
    input_args: dict[str, Any],
    *,
    is_non_interactive: bool = False,
  ) -> str:
    return await self._description_fn(input_args, is_non_interactive=is_non_interactive)

  async def prompt(self, *, tools: list[Any] | None = None) -> str:
    result = self._prompt_fn(tools=tools)
    # Handle both sync (returns str) and async (returns coroutine) prompt fns
    if asyncio.iscoroutine(result):
      return await result
    return result

  def is_enabled(self) -> bool:
    return self._is_enabled_fn()

  def is_concurrency_safe(self, input_args: dict[str, Any]) -> bool:
    return self._is_concurrency_safe_fn(input_args)

  def is_read_only(self, input_args: dict[str, Any]) -> bool:
    return self._is_read_only_fn(input_args)

  def is_destructive(self, input_args: dict[str, Any]) -> bool:
    return self._is_destructive_fn(input_args)

  async def check_permissions(
    self,
    input_args: dict[str, Any],
    context: ToolUseContext,
  ) -> PermissionResult:
    if self._check_permissions_fn:
      return await self._check_permissions_fn(input_args, context)
    # Default: allow (defer to general permission system)
    return PermissionResult(behavior="allow", updated_input=input_args)

  async def validate_input(
    self,
    input_args: dict[str, Any],
    context: ToolUseContext,
  ) -> ValidationResult:
    if self._validate_input_fn:
      return await self._validate_input_fn(input_args, context)
    return ValidationResult(valid=True)

  def to_auto_classifier_input(self, input_args: dict[str, Any]) -> Any:
    return self._to_auto_classifier_input_fn(input_args)

  def user_facing_name(self, input_args: dict[str, Any] | None = None) -> str:
    return self._user_facing_name_fn(input_args)

  def get_path(self, input_args: dict[str, Any]) -> str | None:
    if self._get_path_fn:
      return self._get_path_fn(input_args)
    return None

  def __repr__(self) -> str:
    return f"Tool(name={self.name!r}, aliases={self.aliases!r})"


# ---------------------------------------------------------------------------
# Factory + helpers
# ---------------------------------------------------------------------------


def build_tool(**kwargs: Any) -> _BuiltTool:
  """Build a complete Tool from keyword arguments, filling safe defaults.

  Mirrors ``buildTool`` from src/Tool.ts (L737-746).

  Required kwargs: name, input_schema, call_fn, description_fn, prompt_fn.
  All other kwargs are optional and have fail-closed defaults.
  """
  return _BuiltTool(**kwargs)


def tool_matches_name(tool: _BuiltTool | Any, name: str) -> bool:
  """Check if a tool matches the given name (primary or alias).

  Mirrors ``toolMatchesName`` from Tool.ts (L319-321).
  """
  if tool.name == name:
    return True
  aliases = getattr(tool, "aliases", None)
  return name in aliases if aliases else False


def find_tool_by_name(
  tools: list[_BuiltTool | Any],
  name: str,
) -> _BuiltTool | None:
  """Find a tool by name or alias.

  Mirrors ``findToolByName`` from Tool.ts (L326-328).
  """
  for t in tools:
    if tool_matches_name(t, name):
      return t
  return None
