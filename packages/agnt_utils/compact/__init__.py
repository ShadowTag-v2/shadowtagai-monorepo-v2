# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""agnt_utils.compact — SHIM: re-exports from packages.context_compactor.

This package is a backward-compatibility shim.  All implementation has
been migrated to ``packages.context_compactor``.  New code should import
directly from ``context_compactor`` instead.

Migration notice (2026-05-01):
    OLD: from packages.agnt_utils.compact import compact_conversation
    NEW: from context_compactor import compact_conversation
"""

import warnings as _warnings

_warnings.warn(
  "packages.agnt_utils.compact is deprecated — import from context_compactor instead.",
  DeprecationWarning,
  stacklevel=2,
)

# ── Re-exports from context_compactor ─────────────────────────────────────────

from context_compactor import (  # noqa: E402, F401
  AutoCompactMiddleware,
  AutoCompactResult,
  AutoCompactTracker,
  COMPACTABLE_TOOLS,
  CompactDirection,
  ContextManagementConfig,
  ConversationCompactionResult,
  MicrocompactResult,
  PromptTooLongError,
  SessionMemoryCompactConfig,
  SessionMemoryCompactResult,
  TIME_BASED_MC_CLEARED_MESSAGE,
  TOOLS_CLEARABLE_RESULTS,
  TOOLS_CLEARABLE_USES,
  TimeBasedMCConfig,
  TokenWarningState,
  adjust_index_to_preserve_api_invariants,
  build_api_context_management,
  build_post_compact_messages,
  calculate_messages_to_keep_index,
  calculate_token_warning_state,
  collect_read_tool_file_paths,
  compact_conversation,
  estimate_message_tokens,
  format_compact_summary,
  get_assistant_message_text,
  get_auto_compact_threshold,
  get_compact_prompt,
  get_compact_user_summary_message,
  get_effective_context_window,
  get_messages_after_compact_boundary,
  get_partial_compact_prompt,
  group_messages_by_api_round,
  has_text_blocks,
  is_compact_boundary_message,
  merge_hook_instructions,
  microcompact_messages,
  partial_compact_conversation,
  register_cleanup_hook,
  run_post_compact_cleanup,
  should_exclude_from_restore,
  strip_images_from_messages,
  strip_reinjected_attachments,
  truncate_head_for_ptl_retry,
  truncate_to_tokens,
  try_session_memory_compact,
)

__all__ = [
  # ── Auto compact ──────────────────────────────────────────────────
  "AutoCompactMiddleware",
  "AutoCompactResult",
  "AutoCompactTracker",
  "TokenWarningState",
  "calculate_token_warning_state",
  "get_auto_compact_threshold",
  "get_effective_context_window",
  # ── Conversation compact ──────────────────────────────────────────
  "CompactDirection",
  "ConversationCompactionResult",
  "PromptTooLongError",
  "build_post_compact_messages",
  "collect_read_tool_file_paths",
  "compact_conversation",
  "get_assistant_message_text",
  "get_messages_after_compact_boundary",
  "is_compact_boundary_message",
  "merge_hook_instructions",
  "partial_compact_conversation",
  "should_exclude_from_restore",
  "strip_images_from_messages",
  "strip_reinjected_attachments",
  "truncate_head_for_ptl_retry",
  "truncate_to_tokens",
  # ── Microcompaction ────────────────────────────────────────────────
  "COMPACTABLE_TOOLS",
  "MicrocompactResult",
  "TIME_BASED_MC_CLEARED_MESSAGE",
  "TimeBasedMCConfig",
  "estimate_message_tokens",
  "microcompact_messages",
  # ── Grouping ───────────────────────────────────────────────────────
  "group_messages_by_api_round",
  # ── Cleanup ────────────────────────────────────────────────────────
  "register_cleanup_hook",
  "run_post_compact_cleanup",
  # ── API context management ─────────────────────────────────────────
  "TOOLS_CLEARABLE_RESULTS",
  "TOOLS_CLEARABLE_USES",
  "ContextManagementConfig",
  "build_api_context_management",
  # ── Prompts ────────────────────────────────────────────────────────
  "format_compact_summary",
  "get_compact_prompt",
  "get_compact_user_summary_message",
  "get_partial_compact_prompt",
  # ── Session memory compact ─────────────────────────────────────────
  "SessionMemoryCompactConfig",
  "SessionMemoryCompactResult",
  "adjust_index_to_preserve_api_invariants",
  "calculate_messages_to_keep_index",
  "has_text_blocks",
  "try_session_memory_compact",
]
