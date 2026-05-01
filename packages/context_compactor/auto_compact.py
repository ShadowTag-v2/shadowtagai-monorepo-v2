# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""AGNT Auto-Compact Middleware — session loop integration.

Ported from: compact/autoCompact.ts
Reference: AGNT STATE B Spec P1.2

This module wires the ContextCompactor into the main session REPL loop.
It implements:
  - Threshold calculations based on effective context window
  - Circuit breaker (MAX_CONSECUTIVE_FAILURES = 3)
  - Session memory compaction fallback (try SM first, then L1-L4)
  - Query source recursion guards (blocks compact-from-compact deadlocks)
  - Token warning state machine (warning → error → blocking)

Usage (in the session loop):
    tracker = AutoCompactTracker()
    middleware = AutoCompactMiddleware(compactor, tracker)

    # Before each model call:
    pre_result = compactor.pre_compact(messages, query_source)

    # After each model response:
    result = await middleware.compact_if_needed(messages, model, query_source)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from context_compactor.layers import (
    AUTOCOMPACT_BUFFER_TOKENS,
    WARNING_THRESHOLD_BUFFER_TOKENS,
    CompactionResult,
)
from context_compactor.post_compact_cleanup import run_post_compact_cleanup
from context_compactor.session_memory_compact import try_session_memory_compact
from context_compactor.token_estimator import rough_token_estimate

logger = logging.getLogger(__name__)

# Reserve tokens for output during compaction.
# Based on p99.99 of compact summary output being 17,387 tokens (upstream BQ).
MAX_OUTPUT_TOKENS_FOR_SUMMARY = 20_000

# Circuit breaker threshold.
# BQ 2026-03-10: 1,279 sessions had 50+ consecutive failures (up to 3,272)
# in a single session, wasting ~250K API calls/day globally.
MAX_CONSECUTIVE_FAILURES = 3

# Manual compact needs less headroom
MANUAL_COMPACT_BUFFER_TOKENS = 3_000

# Error threshold matches warning for simplicity
ERROR_THRESHOLD_BUFFER_TOKENS = 20_000

# Query sources that must NOT trigger auto-compact (recursion guards)
_BLOCKED_SOURCES: frozenset[str] = frozenset(
    {
        "session_memory",
        "compact",
        "marble_origami",  # context-collapse agent
    }
)


@dataclass
class AutoCompactTracker:
    """Tracks auto-compact state across turns.

    Attributes:
        compacted: Whether compaction has occurred this session.
        turn_counter: Number of turns since last compaction.
        turn_id: Unique ID for the current turn.
        consecutive_failures: Circuit breaker counter.
    """

    compacted: bool = False
    turn_counter: int = 0
    turn_id: str = ""
    consecutive_failures: int = 0

    def reset_on_success(self) -> None:
        """Reset failure counter on successful compaction."""
        self.consecutive_failures = 0
        self.compacted = True
        self.turn_counter = 0

    def record_failure(self) -> None:
        """Increment failure counter for circuit breaker."""
        self.consecutive_failures += 1
        if self.consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
            logger.warning(
                "Auto-compact circuit breaker tripped after %d consecutive failures — skipping future attempts this session",
                self.consecutive_failures,
            )


@dataclass
class TokenWarningState:
    """Context window pressure indicators.

    Mirrors calculateTokenWarningState() from autoCompact.ts.
    """

    percent_left: int = 100
    is_above_warning_threshold: bool = False
    is_above_error_threshold: bool = False
    is_above_auto_compact_threshold: bool = False
    is_at_blocking_limit: bool = False


@dataclass
class AutoCompactResult:
    """Result from auto-compact attempt."""

    was_compacted: bool = False
    compaction_result: CompactionResult | None = None
    consecutive_failures: int = 0
    method: str = ""  # "session_memory" | "pipeline" | ""


def get_effective_context_window(
    max_context_tokens: int,
    *,
    auto_compact_window_override: int | None = None,
) -> int:
    """Calculate effective context window after reserving output tokens.

    Args:
        max_context_tokens: Maximum context window size for the model.
        auto_compact_window_override: Optional override (env var equivalent).

    Returns:
        Effective window = min(context, override) - output_reserve.
    """
    window = max_context_tokens
    if auto_compact_window_override and auto_compact_window_override > 0:
        window = min(window, auto_compact_window_override)
    reserve = min(MAX_OUTPUT_TOKENS_FOR_SUMMARY, max_context_tokens // 4)
    return window - reserve


def get_auto_compact_threshold(
    max_context_tokens: int,
    *,
    auto_compact_window_override: int | None = None,
    percent_override: float | None = None,
) -> int:
    """Calculate the token threshold that triggers auto-compaction.

    Args:
        max_context_tokens: Maximum context window size.
        auto_compact_window_override: Optional window override.
        percent_override: Optional percentage override for testing.

    Returns:
        Token count above which auto-compact fires.
    """
    effective = get_effective_context_window(
        max_context_tokens,
        auto_compact_window_override=auto_compact_window_override,
    )
    threshold = effective - AUTOCOMPACT_BUFFER_TOKENS

    if percent_override and 0 < percent_override <= 100:
        pct_threshold = int(effective * (percent_override / 100))
        return min(pct_threshold, threshold)

    return threshold


def calculate_token_warning_state(
    token_usage: int,
    max_context_tokens: int,
    *,
    auto_compact_enabled: bool = True,
) -> TokenWarningState:
    """Compute the current context window pressure state.

    Args:
        token_usage: Current token count.
        max_context_tokens: Maximum context window.
        auto_compact_enabled: Whether auto-compact is active.

    Returns:
        TokenWarningState with all pressure indicators.
    """
    threshold = get_auto_compact_threshold(max_context_tokens) if auto_compact_enabled else get_effective_context_window(max_context_tokens)

    percent_left = max(0, round(((threshold - token_usage) / threshold) * 100))
    warning_threshold = threshold - WARNING_THRESHOLD_BUFFER_TOKENS
    error_threshold = threshold - ERROR_THRESHOLD_BUFFER_TOKENS
    blocking_limit = get_effective_context_window(max_context_tokens) - MANUAL_COMPACT_BUFFER_TOKENS

    return TokenWarningState(
        percent_left=percent_left,
        is_above_warning_threshold=token_usage >= warning_threshold,
        is_above_error_threshold=token_usage >= error_threshold,
        is_above_auto_compact_threshold=(auto_compact_enabled and token_usage >= get_auto_compact_threshold(max_context_tokens)),
        is_at_blocking_limit=token_usage >= blocking_limit,
    )


class AutoCompactMiddleware:
    """Session loop middleware for automatic context compaction.

    Wraps ContextCompactor with session-loop-aware logic:
    - Recursion guards (won't compact from within compact)
    - Circuit breaker (stops after N consecutive failures)
    - Session memory compaction fallback
    - Post-compact cache cleanup
    - Telemetry emission

    Usage:
        from context_compactor.compactor import ContextCompactor
        from context_compactor.auto_compact import AutoCompactMiddleware, AutoCompactTracker

        compactor = ContextCompactor(telemetry_dir=Path(".beads"))
        tracker = AutoCompactTracker()
        middleware = AutoCompactMiddleware(compactor, tracker)

        # In the session loop:
        pre = compactor.pre_compact(messages, query_source)
        messages = pre.messages

        # After model response:
        result = middleware.compact_if_needed(
            messages=messages,
            max_context_tokens=200_000,
            query_source="repl_main_thread",
        )
    """

    def __init__(
        self,
        compactor: Any,  # ContextCompactor
        tracker: AutoCompactTracker,
        *,
        auto_compact_enabled: bool = True,
    ) -> None:
        self._compactor = compactor
        self._tracker = tracker
        self._enabled = auto_compact_enabled

    @property
    def tracker(self) -> AutoCompactTracker:
        """Access the tracking state."""
        return self._tracker

    def should_compact(
        self,
        messages: list[Any],
        max_context_tokens: int,
        query_source: str | None = None,
        *,
        snip_tokens_freed: int = 0,
    ) -> bool:
        """Check if auto-compaction should run.

        Args:
            messages: Current message list.
            max_context_tokens: Maximum context window.
            query_source: Query source for recursion guard.
            snip_tokens_freed: Tokens already freed by snip.

        Returns:
            True if compaction should trigger.
        """
        # Recursion guard
        if query_source and query_source in _BLOCKED_SOURCES:
            return False

        # Global disable
        if not self._enabled:
            return False

        # Circuit breaker
        if self._tracker.consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
            return False

        # Token threshold check
        token_estimate = _estimate_messages_tokens(messages) - snip_tokens_freed
        threshold = get_auto_compact_threshold(max_context_tokens)

        logger.debug(
            "Auto-compact check: tokens=%d threshold=%d snip_freed=%d",
            token_estimate,
            threshold,
            snip_tokens_freed,
        )

        return token_estimate >= threshold

    def compact_if_needed(
        self,
        messages: list[Any],
        max_context_tokens: int,
        query_source: str | None = None,
        *,
        snip_tokens_freed: int = 0,
        target_tokens: int | None = None,
    ) -> AutoCompactResult:
        """Run auto-compaction if thresholds are exceeded.

        This is the main entry point for the session loop.

        Args:
            messages: Current message list.
            max_context_tokens: Maximum context window.
            query_source: Query source identifier.
            snip_tokens_freed: Tokens already freed by snip.
            target_tokens: Override target (defaults to threshold // 2).

        Returns:
            AutoCompactResult with compaction details.
        """
        if not self.should_compact(
            messages,
            max_context_tokens,
            query_source,
            snip_tokens_freed=snip_tokens_freed,
        ):
            return AutoCompactResult(was_compacted=False)

        self._tracker.turn_counter += 1

        # Calculate target
        if target_tokens is None:
            target_tokens = get_auto_compact_threshold(max_context_tokens) // 2

        current_tokens = _estimate_messages_tokens(messages)

        try:
            # Phase 1: Try session memory compaction (lightweight)
            # This avoids the expensive L1→L4 pipeline when session memory
            # already contains a good summary of prior context.
            sm_result = try_session_memory_compact(
                messages,
                auto_compact_threshold=get_auto_compact_threshold(max_context_tokens),
            )
            if sm_result is not None and sm_result.success:
                run_post_compact_cleanup(query_source)
                self._tracker.reset_on_success()

                logger.info(
                    "SM compact succeeded: %d → %d tokens (dropped %d messages)",
                    sm_result.tokens_before,
                    sm_result.tokens_after,
                    sm_result.messages_dropped,
                )

                # Wrap in CompactionResult for API consistency
                return AutoCompactResult(
                    was_compacted=True,
                    compaction_result=CompactionResult(
                        tokens_before=sm_result.tokens_before,
                        tokens_after=sm_result.tokens_after,
                        savings_pct=round(
                            (1 - sm_result.tokens_after / max(sm_result.tokens_before, 1)) * 100,
                            1,
                        ),
                        layer_applied="session_memory",
                    ),
                    consecutive_failures=0,
                    method="session_memory",
                )

            # Phase 2: Full pipeline compaction (L1→L4)
            result = self._compactor.run(
                messages=messages,
                target_tokens=target_tokens,
                current_tokens=current_tokens,
            )

            # Post-compact cleanup
            run_post_compact_cleanup(query_source)
            self._tracker.reset_on_success()

            logger.info(
                "Auto-compact succeeded: %d → %d tokens (%.1f%% saved)",
                result.tokens_before,
                result.tokens_after,
                result.savings_pct,
            )

            return AutoCompactResult(
                was_compacted=True,
                compaction_result=result,
                consecutive_failures=0,
                method="pipeline",
            )

        except Exception:
            logger.warning("Auto-compact failed", exc_info=True)
            self._tracker.record_failure()
            return AutoCompactResult(
                was_compacted=False,
                consecutive_failures=self._tracker.consecutive_failures,
            )


def _estimate_messages_tokens(messages: list[Any]) -> int:
    """Estimate total tokens across all messages."""
    total = 0
    for msg in messages:
        if isinstance(msg, dict):
            content = msg.get("content", "")
            if isinstance(content, str):
                total += rough_token_estimate(content)
            elif isinstance(content, list):
                for block in content:
                    if isinstance(block, dict):
                        text = block.get("text", "")
                        if text:
                            total += rough_token_estimate(str(text))
        elif hasattr(msg, "content"):
            total += rough_token_estimate(str(getattr(msg, "content", "")))
    return total
