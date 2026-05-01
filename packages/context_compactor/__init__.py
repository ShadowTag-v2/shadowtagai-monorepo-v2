# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Context compactor package — 4-layer compaction pipeline with microcompaction.

Architecture (ported from Claude Code v2.1.91 compact/):
  Proactive:  pre_compact() → microcompact_messages() → time-based clearing
  Reactive:   run() → L1 → L2 → L3 → L4 pipeline
  Middleware:  AutoCompactMiddleware → session loop integration
  Cleanup:    run_post_compact_cleanup() → cache/state invalidation
  API:        build_api_context_management() → server-side editing (stubbed)
  Prompts:    get_compact_prompt() → 9-section summarization template

Public API:
  - ContextCompactor: Main orchestrator (L1→L4 pipeline + pre_compact)
  - AutoCompactMiddleware: Session loop auto-compact integration
  - AutoCompactTracker: Circuit breaker + turn tracking state
  - microcompact_messages: Pre-request microcompaction entry point
  - group_messages_by_api_round: API-round message grouping
  - estimate_message_tokens: Conservative token estimation
  - run_post_compact_cleanup: Post-compaction cache invalidation
  - build_api_context_management: Server-side context editing config
  - get_compact_prompt: Full compaction prompt template
  - format_compact_summary: Strip <analysis> from raw summaries
"""

from context_compactor.api_context_management import (
    TOOLS_CLEARABLE_RESULTS,
    TOOLS_CLEARABLE_USES,
    ContextManagementConfig,
    build_api_context_management,
)
from context_compactor.auto_compact import (
    AutoCompactMiddleware,
    AutoCompactTracker,
    AutoCompactResult,
    TokenWarningState,
    calculate_token_warning_state,
    get_auto_compact_threshold,
    get_effective_context_window,
)
from context_compactor.compact_prompts import (
    format_compact_summary,
    get_compact_prompt,
    get_compact_user_summary_message,
    get_partial_compact_prompt,
)
from context_compactor.grouping import group_messages_by_api_round
from context_compactor.micro_compact import (
    COMPACTABLE_TOOLS,
    TIME_BASED_MC_CLEARED_MESSAGE,
    MicrocompactResult,
    TimeBasedMCConfig,
    estimate_message_tokens,
    microcompact_messages,
)
from context_compactor.post_compact_cleanup import (
    register_cleanup_hook,
    run_post_compact_cleanup,
)
from context_compactor.session_memory_compact import (
    SessionMemoryCompactConfig,
    SessionMemoryCompactResult,
    adjust_index_to_preserve_api_invariants,
    calculate_messages_to_keep_index,
    has_text_blocks,
    try_session_memory_compact,
)

__all__ = [
    # Core orchestrator
    "ContextCompactor",
    # Session loop middleware
    "AutoCompactMiddleware",
    "AutoCompactTracker",
    "AutoCompactResult",
    # Token warning
    "TokenWarningState",
    "calculate_token_warning_state",
    "get_auto_compact_threshold",
    "get_effective_context_window",
    # Microcompaction
    "COMPACTABLE_TOOLS",
    "MicrocompactResult",
    "TIME_BASED_MC_CLEARED_MESSAGE",
    "TimeBasedMCConfig",
    "estimate_message_tokens",
    "microcompact_messages",
    # Grouping
    "group_messages_by_api_round",
    # Cleanup
    "register_cleanup_hook",
    "run_post_compact_cleanup",
    # API context management
    "TOOLS_CLEARABLE_RESULTS",
    "TOOLS_CLEARABLE_USES",
    "ContextManagementConfig",
    "build_api_context_management",
    # Prompts
    "format_compact_summary",
    "get_compact_prompt",
    "get_compact_user_summary_message",
    "get_partial_compact_prompt",
    # Session memory compact
    "SessionMemoryCompactConfig",
    "SessionMemoryCompactResult",
    "adjust_index_to_preserve_api_invariants",
    "calculate_messages_to_keep_index",
    "has_text_blocks",
    "try_session_memory_compact",
]
