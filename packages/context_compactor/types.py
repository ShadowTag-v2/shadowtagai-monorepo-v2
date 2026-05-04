# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Shared type definitions for the compact pipeline.

Leaf module — zero internal imports.  Every other compact module
imports from here; this module imports from none of them.

Consolidates types that were in agnt_utils/compact/types.py but missing
from the canonical context_compactor package.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Literal

# ── Message types ─────────────────────────────────────────────────────────────

# Minimal Message dict contract used throughout the compact pipeline.
# Flat format: {role: str, content: str | list, uuid: str, ...}
Message = dict[str, Any]

# Query sources that trigger recursion guards.
QuerySource = str  # e.g. "session_memory", "compact", "repl_main_thread", "sdk"


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


# ── API microcompact types (server-side context editing) ──────────────────────


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
    """Configuration sent to the API for server-side context management.

    Matches the upstream ``ContextEditStrategy`` from apiMicrocompact.ts.
    """

    rules: list[ContextEditRule] = field(default_factory=list)
    enabled: bool = False
