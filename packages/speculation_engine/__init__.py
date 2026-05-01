# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Speculation Engine — 3-stage predictive pipeline.

Architecture (ported from Claude Code v2.1.91):
  Stage 1: Prompt Suggestion (suggestion.py)
  Stage 2: Speculative Execution (engine.py)
  Stage 3: Accept Flow + Pipelined Recursion (engine.accept + suggestion chaining)

Public API:
  - SpeculationEngine: CoW-isolated speculative execution engine
  - OverlayFS: Copy-on-write filesystem overlay
  - CompletionBoundary / BoundaryType: Why speculation stopped
  - SpeculationState: Engine state machine
  - SuggestionConfig / SuggestionResult / SuggestionOutcome: Suggestion types
  - SuppressReason / FilterReason: Why suggestions were blocked
  - try_generate_suggestion: Stage 1 entry point
  - should_filter_suggestion: 12-rule client-side filter
  - log_suggestion_outcome: RL dataset join point
  - SessionState: Minimal session state for suppression checks
  - log_suggestion_event / log_speculation_event: Telemetry
"""

from speculation_engine.engine import (
    BASH_TOOLS,
    MAX_SPECULATION_MESSAGES,
    MAX_SPECULATION_TURNS,
    SAFE_READ_TOOLS,
    WRITE_TOOLS,
    BoundaryType,
    CompletionBoundary,
    OverlayFS,
    SpeculationEngine,
    SpeculationState,
    prepare_messages_for_injection,
)
from speculation_engine.suggestion import (
    SINGLE_WORD_ALLOWLIST,
    FilterReason,
    SessionState,
    SuggestionConfig,
    SuggestionOutcome,
    SuggestionResult,
    SuppressReason,
    check_enablement_gates,
    get_suggestion_suppress_reason,
    log_suggestion_outcome,
    should_filter_suggestion,
    try_generate_suggestion,
)
from speculation_engine.orchestrator import (
    SpeculativePhaseResult,
    SpeculativeResearchConfig,
    SpeculativeResearchOrchestrator,
)
from speculation_engine.telemetry import (
    log_speculation_event,
    log_suggestion_event,
    read_telemetry_events,
)
from speculation_engine.streaming_executor import (
    AbortReason,
    MessageUpdate,
    ProgressMessage,
    StreamingToolExecutor,
    ToolResult,
    ToolStatus,
    TrackedTool,
)
from speculation_engine.cache_break_detection import (
    CACHE_TTL_1HOUR_S,
    CACHE_TTL_5MIN_S,
    CacheBreakDetector,
    PendingChanges,
    PromptStateSnapshot,
    TrackedState,
)

__all__ = [
    # Engine
    "SpeculationEngine",
    "OverlayFS",
    "CompletionBoundary",
    "BoundaryType",
    "SpeculationState",
    "prepare_messages_for_injection",
    "MAX_SPECULATION_TURNS",
    "MAX_SPECULATION_MESSAGES",
    "SAFE_READ_TOOLS",
    "WRITE_TOOLS",
    "BASH_TOOLS",
    # Suggestion
    "SuggestionConfig",
    "SuggestionResult",
    "SuggestionOutcome",
    "SuppressReason",
    "FilterReason",
    "SessionState",
    "try_generate_suggestion",
    "should_filter_suggestion",
    "check_enablement_gates",
    "get_suggestion_suppress_reason",
    "log_suggestion_outcome",
    "SINGLE_WORD_ALLOWLIST",
    # Orchestrator
    "SpeculativeResearchOrchestrator",
    "SpeculativeResearchConfig",
    "SpeculativePhaseResult",
    # Streaming Executor
    "StreamingToolExecutor",
    "ToolResult",
    "ToolStatus",
    "AbortReason",
    "ProgressMessage",
    "MessageUpdate",
    "TrackedTool",
    # Cache Break Detection
    "CacheBreakDetector",
    "PromptStateSnapshot",
    "PendingChanges",
    "TrackedState",
    "CACHE_TTL_5MIN_S",
    "CACHE_TTL_1HOUR_S",
    # Telemetry
    "log_suggestion_event",
    "log_speculation_event",
    "read_telemetry_events",
]
