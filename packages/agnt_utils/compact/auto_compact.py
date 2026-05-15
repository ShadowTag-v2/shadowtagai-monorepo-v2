# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Auto-compact controller — ported from autoCompact.ts.

Layer 1 of the compaction pipeline: threshold-based detection,
circuit breaker, and orchestration of the compaction paths
(session memory → LLM summarization).

Token thresholds:
  - AUTOCOMPACT_BUFFER_TOKENS = 13,000  (headroom before context limit)
  - WARNING_THRESHOLD_BUFFER_TOKENS = 20,000
  - ERROR_THRESHOLD_BUFFER_TOKENS = 20,000
  - MANUAL_COMPACT_BUFFER_TOKENS = 3,000

Circuit breaker: stop retrying after 3 consecutive failures.
BQ data showed 1,279 sessions with 50+ consecutive failures,
wasting ~250K API calls/day globally.
"""

from __future__ import annotations

import logging
import os

from packages.agnt_utils.compact.post_compact_cleanup import run_post_compact_cleanup
from packages.agnt_utils.compact.session_memory_compact import (
  try_session_memory_compaction,
)
from packages.agnt_utils.compact.types import (
  AutoCompactTrackingState,
  Message,
  TokenWarningState,
)
from packages.agnt_utils.token_estimate import (
  token_count_with_estimation,
)

logger = logging.getLogger(__name__)

# ── Constants ─────────────────────────────────────────────────────────────────

# Reserve these tokens for output during compaction.
# Based on p99.99 of compact summary output being 17,387 tokens.
MAX_OUTPUT_TOKENS_FOR_SUMMARY = 20_000

AUTOCOMPACT_BUFFER_TOKENS = 13_000
WARNING_THRESHOLD_BUFFER_TOKENS = 20_000
ERROR_THRESHOLD_BUFFER_TOKENS = 20_000
MANUAL_COMPACT_BUFFER_TOKENS = 3_000

# Stop trying after this many consecutive failures.
MAX_CONSECUTIVE_AUTOCOMPACT_FAILURES = 3

# ── Model context windows ────────────────────────────────────────────────────
# Default context windows by model family.  In a full integration these
# come from the model registry; here we use sensible defaults.

_DEFAULT_CONTEXT_WINDOWS: dict[str, int] = {
  "claude-3-5-sonnet": 200_000,
  "claude-3-5-haiku": 200_000,
  "claude-sonnet-4": 200_000,
  "claude-4-5-sonnet": 200_000,
  "claude-4-6-sonnet": 200_000,
  "gemini-2.5-pro": 1_000_000,
  "gemini-2.5-flash": 1_000_000,
  "gemini-3-pro": 1_000_000,
  "gemini-3.1-pro": 2_000_000,
}

_DEFAULT_MAX_OUTPUT: dict[str, int] = {
  "claude-3-5-sonnet": 8_192,
  "claude-sonnet-4": 16_384,
  "claude-4-5-sonnet": 16_384,
  "claude-4-6-sonnet": 16_384,
  "gemini-2.5-pro": 65_536,
  "gemini-3-pro": 65_536,
  "gemini-3.1-pro": 65_536,
}

DEFAULT_CONTEXT_WINDOW = 200_000
DEFAULT_MAX_OUTPUT = 8_192


def _get_context_window(model: str) -> int:
  """Return context window for *model*, checking known families."""
  for prefix, window in _DEFAULT_CONTEXT_WINDOWS.items():
    if model.startswith(prefix):
      return window
  return DEFAULT_CONTEXT_WINDOW


def _get_max_output(model: str) -> int:
  """Return max output tokens for *model*."""
  for prefix, output in _DEFAULT_MAX_OUTPUT.items():
    if model.startswith(prefix):
      return output
  return DEFAULT_MAX_OUTPUT


# ── Public API ────────────────────────────────────────────────────────────────


def get_effective_context_window_size(model: str) -> int:
  """Context window minus the max output tokens for the model.

  The effective window is the number of input tokens available before
  we must compact to leave room for the model's output.
  """
  reserved = min(_get_max_output(model), MAX_OUTPUT_TOKENS_FOR_SUMMARY)
  context_window = _get_context_window(model)

  # Allow env override for testing
  env_window = os.environ.get("CLAUDE_CODE_AUTO_COMPACT_WINDOW", "")
  if env_window:
    try:
      parsed = int(env_window)
      if parsed > 0:
        context_window = min(context_window, parsed)
    except ValueError:
      pass

  return context_window - reserved


def get_auto_compact_threshold(model: str) -> int:
  """Token count at which auto-compact should trigger."""
  effective = get_effective_context_window_size(model)
  threshold = effective - AUTOCOMPACT_BUFFER_TOKENS

  # Allow percentage override for testing
  env_pct = os.environ.get("CLAUDE_AUTOCOMPACT_PCT_OVERRIDE", "")
  if env_pct:
    try:
      parsed = float(env_pct)
      if 0 < parsed <= 100:
        pct_threshold = int(effective * (parsed / 100))
        return min(pct_threshold, threshold)
    except ValueError:
      pass

  return threshold


def calculate_token_warning_state(
  token_usage: int,
  model: str,
) -> TokenWarningState:
  """Calculate the current token warning state."""
  auto_threshold = get_auto_compact_threshold(model)
  enabled = is_auto_compact_enabled()
  threshold = auto_threshold if enabled else get_effective_context_window_size(model)

  percent_left = max(0, round(((threshold - token_usage) / threshold) * 100))

  warning_threshold = threshold - WARNING_THRESHOLD_BUFFER_TOKENS
  error_threshold = threshold - ERROR_THRESHOLD_BUFFER_TOKENS

  actual_window = get_effective_context_window_size(model)
  default_blocking = actual_window - MANUAL_COMPACT_BUFFER_TOKENS

  # Allow override for testing
  env_blocking = os.environ.get("CLAUDE_CODE_BLOCKING_LIMIT_OVERRIDE", "")
  try:
    blocking_limit = int(env_blocking) if env_blocking else default_blocking
    if blocking_limit <= 0:
      blocking_limit = default_blocking
  except ValueError:
    blocking_limit = default_blocking

  return TokenWarningState(
    percent_left=percent_left,
    is_above_warning_threshold=token_usage >= warning_threshold,
    is_above_error_threshold=token_usage >= error_threshold,
    is_above_auto_compact_threshold=enabled and token_usage >= auto_threshold,
    is_at_blocking_limit=token_usage >= blocking_limit,
  )


def is_auto_compact_enabled() -> bool:
  """Return whether auto-compact is enabled."""
  if os.environ.get("DISABLE_COMPACT", "").lower() in ("1", "true"):
    return False
  if os.environ.get("DISABLE_AUTO_COMPACT", "").lower() in ("1", "true"):
    return False
  # Default to enabled (matches upstream's autoCompactEnabled default)
  return True


def should_auto_compact(
  messages: list[Message],
  model: str,
  query_source: str | None = None,
  snip_tokens_freed: int = 0,
) -> bool:
  """Return whether auto-compact should trigger for these messages.

  Recursion guards prevent session_memory and compact query sources
  from triggering compaction (would deadlock).
  """
  # Recursion guards
  if query_source in ("session_memory", "compact"):
    return False

  if not is_auto_compact_enabled():
    return False

  token_count = token_count_with_estimation(messages) - snip_tokens_freed
  threshold = get_auto_compact_threshold(model)
  effective = get_effective_context_window_size(model)

  logger.debug(
    "autocompact: tokens=%d threshold=%d effective=%d%s",
    token_count,
    threshold,
    effective,
    f" snipFreed={snip_tokens_freed}" if snip_tokens_freed > 0 else "",
  )

  state = calculate_token_warning_state(token_count, model)
  return state.is_above_auto_compact_threshold


def auto_compact_if_needed(
  messages: list[Message],
  model: str,
  query_source: str | None = None,
  tracking: AutoCompactTrackingState | None = None,
  snip_tokens_freed: int = 0,
) -> dict:
  """Run auto-compact if the context exceeds the threshold.

  Returns a dict with keys:
    - ``was_compacted``: bool
    - ``compaction_result``: CompactionResult | None
    - ``consecutive_failures``: int | None

  This simplified version tries session-memory compaction only.
  The full LLM-based compaction path requires an API integration
  that is outside the scope of the utility library.
  """
  if os.environ.get("DISABLE_COMPACT", "").lower() in ("1", "true"):
    return {"was_compacted": False}

  # Circuit breaker
  if tracking and tracking.consecutive_failures >= MAX_CONSECUTIVE_AUTOCOMPACT_FAILURES:
    return {"was_compacted": False}

  if not should_auto_compact(messages, model, query_source, snip_tokens_freed):
    return {"was_compacted": False}

  threshold = get_auto_compact_threshold(model)

  # Try session memory compaction first
  result = try_session_memory_compaction(
    messages,
    agent_id=None,
    auto_compact_threshold=threshold,
  )
  if result:
    run_post_compact_cleanup(query_source)
    return {
      "was_compacted": True,
      "compaction_result": result,
      "consecutive_failures": 0,
    }

  # LLM-based compaction would go here in a full integration.
  # For the utility library, we only support session-memory compaction.
  prev = tracking.consecutive_failures if tracking else 0
  next_failures = prev + 1
  if next_failures >= MAX_CONSECUTIVE_AUTOCOMPACT_FAILURES:
    logger.warning(
      "autocompact: circuit breaker tripped after %d consecutive failures — skipping future attempts this session",
      next_failures,
    )
  return {"was_compacted": False, "consecutive_failures": next_failures}
