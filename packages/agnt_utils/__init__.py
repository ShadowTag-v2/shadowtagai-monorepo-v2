# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""agnt_utils — ported infrastructure utilities from Claude Code v2.1.91.

Modules (original 6):
    token_budget:      Parse "+500k" / "use 2M tokens" budget directives
    circular_buffer:   Fixed-size ring buffer with O(1) add / O(k) get_recent
    activity_manager:  CLI/user activity tracking with timeout-based dedup
    memoize:           TTL + LRU memoization with write-through refresh
    token_estimate:    Heuristic token counting for context window management
    truncate:          Width-aware text truncation for terminal UI

Batch 2 modules (7):
    sequential:        Async sequential execution wrapper (race condition guard)
    sanitization:      Unicode smuggling defense (HackerOne #3086545)
    errors:            Structured error hierarchy + stack truncation
    string_utils:      String accumulators, truncation, formatting helpers
    hash_utils:        Deterministic djb2 + SHA-256 hashing
    xml_escape:        XML/HTML entity escaping for prompt safety
    sleep_utils:       Cancellable async sleep + timeout guards

Batch 3 modules (8):
    json_utils:        Safe JSON/JSONL parsing with LRU-bounded caching
    set_ops:           Hot-path optimized set operations
    signal:            Tiny listener-set primitive for pure event signals
    diff_utils:        Hunk-based structured diff processing
    treeify:           Recursive tree visualization for CLI output
    combined_abort:    Combined cancellation signal with timeout cleanup
    generators:        Async generator manipulation utilities
    format_utils:      Human-readable display formatters
    array_utils:       Functional array utilities (intersperse, count, group_by)

Batch 4 modules (2):
    throttle:          Rate-limiting decorator with leading/trailing edge control
    debounce:          Delayed execution until activity settles

Batch 5 modules (3):
    context_visualizer: Context window analysis, token breakdown, grid visualization
    effort:            4-tier effort system for reasoning compute control
    cli_diagnostics:   Tree-based diagnostic output for CLI reporting
"""

from packages.agnt_utils.array_utils import count, group_by, intersperse, uniq
from packages.agnt_utils.circular_buffer import CircularBuffer
from packages.agnt_utils.combined_abort import CombinedAbort, create_combined_abort
from packages.agnt_utils.debounce import DebouncedFunction, debounce
from packages.agnt_utils.diff_utils import (
  Hunk,
  LinesChanged,
  adjust_hunk_line_numbers,
  apply_edits,
  count_lines_changed,
  get_patch_from_contents,
  get_unified_diff,
)
from packages.agnt_utils.errors import (
  AbortError,
  AgntError,
  ConfigParseError,
  ShellError,
  TelemetrySafeError,
  classify_http_error,
  error_message,
  get_errno_code,
  has_exact_message,
  is_abort_error,
  is_enoent,
  is_fs_inaccessible,
  short_error_stack,
  to_error,
)
from packages.agnt_utils.format_utils import (
  format_duration,
  format_file_size,
  format_number,
  format_relative_time,
  format_relative_time_ago,
  format_seconds_short,
  format_tokens,
)
from packages.agnt_utils.generators import (
  from_array,
  last,
  merge_concurrent,
  to_array,
)
from packages.agnt_utils.hash_utils import djb2_hash, hash_content, hash_pair
from packages.agnt_utils.json_utils import (
  add_item_to_jsonc_array,
  clear_parse_cache,
  parse_jsonl,
  read_jsonl_file,
  safe_parse_json,
  safe_parse_jsonc,
  strip_bom,
)
from packages.agnt_utils.memoize import memoize_with_lru, memoize_with_ttl
from packages.agnt_utils.sanitization import (
  partially_sanitize_unicode,
  recursively_sanitize_unicode,
)
from packages.agnt_utils.sequential import sequential
from packages.agnt_utils.set_ops import (
  difference,
  every,
  intersection,
  intersects,
  symmetric_difference,
  union,
  unique,
)
from packages.agnt_utils.signal import Signal, create_signal
from packages.agnt_utils.sleep_utils import cancellable_sleep, with_timeout
from packages.agnt_utils.string_utils import (
  EndTruncatingAccumulator,
  capitalize_first,
  count_char,
  first_line_of,
  normalize_fullwidth_digits,
  normalize_fullwidth_space,
  plural,
  safe_join_lines,
  truncate_to_lines,
)
from packages.agnt_utils.throttle import CooldownThrottle, ThrottledFunction, throttle
from packages.agnt_utils.token_budget import (
  get_budget_continuation_message,
  parse_token_budget,
)
from packages.agnt_utils.token_estimate import (
  rough_token_estimate,
  rough_token_estimate_for_block,
  rough_token_estimate_for_content,
  rough_token_estimate_for_message,
  rough_token_estimate_for_messages,
  token_count_with_estimation,
)
from packages.agnt_utils.treeify import treeify
from packages.agnt_utils.truncate import (
  smart_truncate,
  string_width,
  truncate,
  truncate_path_middle,
  truncate_to_width,
  wrap_text,
)
from packages.agnt_utils.xml_escape import escape_xml, escape_xml_attr

# ── Batch 5 imports ────────────────────────────────────────────────────────────
from packages.agnt_utils.cli_diagnostics import (
  render_diagnostic_report,
  render_mcp_status,
  render_package_tree,
  render_telemetry_health,
  render_test_summary,
)
from packages.agnt_utils.context_visualizer import (
  AUTOCOMPACT_BUFFER_TOKENS,
  MODEL_CONTEXT_WINDOW_DEFAULT,
  ContextCategory,
  ContextData,
  GridSquare,
  MessageBreakdown,
  analyze_context_usage,
  approximate_message_tokens,
  calculate_context_percentages,
  generate_grid,
  get_context_window_for_model,
)
from packages.agnt_utils.effort import (
  EFFORT_DESCRIPTIONS,
  EFFORT_LEVELS,
  EFFORT_SYMBOLS,
  EffortLevel,
  EffortValue,
  convert_effort_value_to_level,
  effort_level_to_symbol,
  get_default_effort_for_model,
  get_displayed_effort_level,
  get_effort_description,
  get_effort_env_override,
  get_effort_notification_text,
  get_effort_suffix,
  is_effort_level,
  is_valid_numeric_effort,
  model_supports_effort,
  model_supports_max_effort,
  parse_effort_value,
  resolve_applied_effort,
  to_persistable_effort,
)

__all__ = [
  # ── Original batch ────────────────────────────────────────────────
  "CircularBuffer",
  "get_budget_continuation_message",
  "memoize_with_lru",
  "memoize_with_ttl",
  "parse_token_budget",
  "rough_token_estimate",
  "rough_token_estimate_for_block",
  "rough_token_estimate_for_content",
  "rough_token_estimate_for_message",
  "rough_token_estimate_for_messages",
  "smart_truncate",
  "string_width",
  "token_count_with_estimation",
  "truncate",
  "truncate_path_middle",
  "truncate_to_width",
  "wrap_text",
  # ── Batch 2: sequential ───────────────────────────────────────────
  "sequential",
  # ── Batch 2: sanitization ─────────────────────────────────────────
  "partially_sanitize_unicode",
  "recursively_sanitize_unicode",
  # ── Batch 2: errors ───────────────────────────────────────────────
  "AbortError",
  "AgntError",
  "ConfigParseError",
  "ShellError",
  "TelemetrySafeError",
  "classify_http_error",
  "error_message",
  "get_errno_code",
  "has_exact_message",
  "is_abort_error",
  "is_enoent",
  "is_fs_inaccessible",
  "short_error_stack",
  "to_error",
  # ── Batch 2: string_utils ─────────────────────────────────────────
  "EndTruncatingAccumulator",
  "capitalize_first",
  "count_char",
  "first_line_of",
  "normalize_fullwidth_digits",
  "normalize_fullwidth_space",
  "plural",
  "safe_join_lines",
  "truncate_to_lines",
  # ── Batch 2: hash_utils ───────────────────────────────────────────
  "djb2_hash",
  "hash_content",
  "hash_pair",
  # ── Batch 2: xml_escape ───────────────────────────────────────────
  "escape_xml",
  "escape_xml_attr",
  # ── Batch 2: sleep_utils ──────────────────────────────────────────
  "cancellable_sleep",
  "with_timeout",
  # ── Batch 3: json_utils ───────────────────────────────────────────
  "add_item_to_jsonc_array",
  "clear_parse_cache",
  "parse_jsonl",
  "read_jsonl_file",
  "safe_parse_json",
  "safe_parse_jsonc",
  "strip_bom",
  # ── Batch 3: set_ops ──────────────────────────────────────────────
  "difference",
  "every",
  "intersection",
  "intersects",
  "symmetric_difference",
  "union",
  "unique",
  # ── Batch 3: signal ───────────────────────────────────────────────
  "Signal",
  "create_signal",
  # ── Batch 3: diff_utils ───────────────────────────────────────────
  "Hunk",
  "LinesChanged",
  "adjust_hunk_line_numbers",
  "apply_edits",
  "count_lines_changed",
  "get_patch_from_contents",
  "get_unified_diff",
  # ── Batch 3: treeify ──────────────────────────────────────────────
  "treeify",
  # ── Batch 3: combined_abort ───────────────────────────────────────
  "CombinedAbort",
  "create_combined_abort",
  # ── Batch 3: generators ───────────────────────────────────────────
  "from_array",
  "last",
  "merge_concurrent",
  "to_array",
  # ── Batch 3: format_utils ─────────────────────────────────────────
  "format_duration",
  "format_file_size",
  "format_number",
  "format_relative_time",
  "format_relative_time_ago",
  "format_seconds_short",
  "format_tokens",
  # ── Batch 3: array_utils ──────────────────────────────────────────
  "count",
  "group_by",
  "intersperse",
  "uniq",
  # ── Batch 4: throttle ─────────────────────────────────────────────
  "CooldownThrottle",
  "DebouncedFunction",
  "ThrottledFunction",
  "debounce",
  "throttle",
  # ── Batch 5: context_visualizer ────────────────────────────────────
  "AUTOCOMPACT_BUFFER_TOKENS",
  "MODEL_CONTEXT_WINDOW_DEFAULT",
  "ContextCategory",
  "ContextData",
  "GridSquare",
  "MessageBreakdown",
  "analyze_context_usage",
  "approximate_message_tokens",
  "calculate_context_percentages",
  "generate_grid",
  "get_context_window_for_model",
  # ── Batch 5: effort ───────────────────────────────────────────────
  "EFFORT_DESCRIPTIONS",
  "EFFORT_LEVELS",
  "EFFORT_SYMBOLS",
  "EffortLevel",
  "EffortValue",
  "convert_effort_value_to_level",
  "effort_level_to_symbol",
  "get_default_effort_for_model",
  "get_displayed_effort_level",
  "get_effort_description",
  "get_effort_env_override",
  "get_effort_notification_text",
  "get_effort_suffix",
  "is_effort_level",
  "is_valid_numeric_effort",
  "model_supports_effort",
  "model_supports_max_effort",
  "parse_effort_value",
  "resolve_applied_effort",
  "to_persistable_effort",
  # ── Batch 5: cli_diagnostics ──────────────────────────────────────
  "render_diagnostic_report",
  "render_mcp_status",
  "render_package_tree",
  "render_telemetry_health",
  "render_test_summary",
]
