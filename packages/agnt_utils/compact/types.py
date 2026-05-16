# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Shared type definitions for the compact pipeline.

Leaf module — zero internal imports.  Every other compact module
imports from here; this module imports from none of them.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Literal


# ── Message types ─────────────────────────────────────────────────────────────

# Minimal Message dict contract used throughout the compact pipeline.
# In the Claude Code source this is a discriminated union
# (AssistantMessage | UserMessage | AttachmentMessage) with `type`
# and `message` fields.  We keep it as a plain dict[str, Any] for
# interop with the rest of agnt_utils.
Message = dict[str, Any]

# Query sources that trigger recursion guards.
QuerySource = str  # e.g. "session_memory", "compact", "repl_main_thread", "sdk"


class CompactDirection(StrEnum):
  """Partial-compact direction — which messages to summarize."""

  FROM = "from"  # summarize FROM a point forward (default)
  UP_TO = "up_to"  # summarize everything UP TO a point


# ── Compaction result ─────────────────────────────────────────────────────────


@dataclass
class CompactionResult:
  """Outcome of a compaction attempt.

  Mirrors the upstream ``CompactionResult`` type from compact.ts.
  """

  # The summarized messages that replace the original conversation.
  messages: list[Message] = field(default_factory=list)

  # Human-readable summary text (formatted, analysis stripped).
  summary: str = ""

  # Number of tokens before compaction.
  tokens_before: int = 0

  # Number of tokens after compaction (estimated).
  tokens_after: int = 0

  # Whether the compaction was a partial (preserving recent messages).
  is_partial: bool = False

  # Number of API rounds preserved (for partial compaction).
  rounds_preserved: int = 0


# ── Token warning state ──────────────────────────────────────────────────────


@dataclass(frozen=True)
class TokenWarningState:
  """Token budget status — returned by ``calculate_token_warning_state``.

  Matches the upstream return type of ``calculateTokenWarningState``.
  """

  percent_left: int
  is_above_warning_threshold: bool
  is_above_error_threshold: bool
  is_above_auto_compact_threshold: bool
  is_at_blocking_limit: bool


# ── Recompaction metadata ─────────────────────────────────────────────────────


@dataclass
class RecompactionInfo:
  """Metadata threaded through compaction chains.

  Allows telemetry to distinguish first-compact from re-compact
  and record how many turns elapsed between compaction attempts.
  """

  is_recompaction_in_chain: bool = False
  turns_since_previous_compact: int = -1
  previous_compact_turn_id: str | None = None
  auto_compact_threshold: int = 0
  query_source: QuerySource | None = None


# ── Auto-compact tracking ────────────────────────────────────────────────────


@dataclass
class AutoCompactTrackingState:
  """Per-session tracking state for the auto-compact controller.

  Threaded through the query loop so the controller can detect
  re-compaction chains and apply the circuit breaker.
  """

  compacted: bool = False
  turn_counter: int = 0
  turn_id: str = ""
  consecutive_failures: int = 0


# ── Microcompact types ────────────────────────────────────────────────────────

# Tool names eligible for content clearing.
COMPACTABLE_TOOLS: frozenset[str] = frozenset(
  {
    "Read",
    "Bash",
    "Grep",
    "Glob",
    "WebFetch",
    "UrlScreenshot",
  }
)

# The sentinel string that replaces cleared tool results.
CLEARED_CONTENT_SENTINEL: str = "[Old tool result content cleared]"


# ── API microcompact types ────────────────────────────────────────────────────


class ContextEditRuleType(StrEnum):
  """Types of context-edit rules sent to the API."""

  TOOL_RESULT = "tool_result"
  THINKING = "thinking"


@dataclass
class ContextEditRule:
  """A single context-edit rule for API-side content management."""

  type: Literal["tool_result", "thinking"]
  # For tool_result rules: which tools to clear
  tool_names: list[str] = field(default_factory=list)
  # For thinking rules: what to do with thinking content
  action: str = "clear"
  # Number of recent items to keep
  keep_recent: int = 0


@dataclass
class ContextEditStrategy:
  """Configuration sent to the Anthropic API for server-side
  context management.

  Matches the upstream ``ContextEditStrategy`` from apiMicrocompact.ts.
  """

  rules: list[ContextEditRule] = field(default_factory=list)
  enabled: bool = False
