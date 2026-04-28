# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Compaction Circuit Breakers — compaction_engine.py

Context compaction logic with circuit breaker protection.
Hard-halts on 3 consecutive failures to prevent infinite
compaction loops.

Based on CC Leaks Architecture analysis (4-layer model):
  - Microcompact: within-message stale tool result pruning
  - Auto-compact: ~167K token threshold
  - Reactive compact: explicit /compact command
  - History snip: nuclear option (platform-level)
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from datetime import datetime, UTC
from pathlib import Path
from typing import Any


COMPACTION_LOG_PATH = Path(".beads/compaction_log.jsonl")
CIRCUIT_BREAKER_THRESHOLD = 3
AUTOCOMPACT_PCT = 50  # Target reduction percentage


@dataclass
class CompactionResult:
    """Result of a compaction operation."""

    success: bool
    original_tokens: int
    compacted_tokens: int
    reduction_pct: float
    method: str
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    error: str | None = None


@dataclass
class CircuitBreaker:
    """Circuit breaker to prevent infinite compaction loops."""

    consecutive_failures: int = 0
    last_failure_time: float = 0.0
    is_open: bool = False
    cooldown_seconds: float = 300.0  # 5 minutes

    def record_success(self) -> None:
        """Reset failure counter on success."""
        self.consecutive_failures = 0
        self.is_open = False

    def record_failure(self) -> None:
        """Increment failure counter; open circuit if threshold reached."""
        self.consecutive_failures += 1
        self.last_failure_time = time.time()
        if self.consecutive_failures >= CIRCUIT_BREAKER_THRESHOLD:
            self.is_open = True

    def can_attempt(self) -> bool:
        """Check if compaction can be attempted."""
        if not self.is_open:
            return True
        # Allow retry after cooldown
        elapsed = time.time() - self.last_failure_time
        if elapsed >= self.cooldown_seconds:
            self.is_open = False
            self.consecutive_failures = 0
            return True
        return False

    def status(self) -> dict[str, Any]:
        """Return circuit breaker state for diagnostics."""
        return {
            "consecutive_failures": self.consecutive_failures,
            "is_open": self.is_open,
            "cooldown_remaining": max(
                0,
                self.cooldown_seconds - (time.time() - self.last_failure_time),
            )
            if self.is_open
            else 0,
        }


# Module-level circuit breaker instance
_breaker = CircuitBreaker()


def compact_stale_tool_results(
    context: list[dict[str, Any]],
) -> CompactionResult:
    """Layer 0: Microcompact — prune stale tool results.

    Replaces verbose tool outputs with summaries when the
    tool result is no longer needed for reasoning.
    """
    if not _breaker.can_attempt():
        return CompactionResult(
            success=False,
            original_tokens=0,
            compacted_tokens=0,
            reduction_pct=0.0,
            method="microcompact",
            error=f"Circuit breaker OPEN: {_breaker.status()}",
        )

    original_count = sum(len(str(item)) for item in context)
    compacted = []

    for item in context:
        role = item.get("role", "")
        if role == "tool_result":
            # Keep only summary if output is large
            content = str(item.get("content", ""))
            if len(content) > 2000:
                item = {
                    **item,
                    "content": f"[COMPACTED: {len(content)} chars → see MEMORY.md]",
                }
        compacted.append(item)

    compacted_count = sum(len(str(item)) for item in compacted)
    reduction = ((original_count - compacted_count) / original_count * 100) if original_count > 0 else 0.0

    result = CompactionResult(
        success=True,
        original_tokens=original_count,
        compacted_tokens=compacted_count,
        reduction_pct=round(reduction, 1),
        method="microcompact",
    )

    _breaker.record_success()
    _log_result(result)
    return result


def auto_compact(
    context: list[dict[str, Any]],
    token_threshold: int = 167_000,
    retention_files: int = 5,
    summary_budget: int = 50_000,
) -> CompactionResult:
    """Layer 1: Auto-compact at token threshold.

    Triggered when context approaches token_threshold.
    Retains last `retention_files` file contexts + summary_budget
    chars of summarized history.
    """
    if not _breaker.can_attempt():
        return CompactionResult(
            success=False,
            original_tokens=0,
            compacted_tokens=0,
            reduction_pct=0.0,
            method="auto_compact",
            error=f"Circuit breaker OPEN: {_breaker.status()}",
        )

    original_tokens = sum(len(str(item)) for item in context)

    if original_tokens < token_threshold:
        return CompactionResult(
            success=True,
            original_tokens=original_tokens,
            compacted_tokens=original_tokens,
            reduction_pct=0.0,
            method="auto_compact_skipped",
        )

    # Keep last N items + generate summary of older items
    retain_count = min(retention_files * 3, len(context))
    retained = context[-retain_count:]
    older = context[:-retain_count]

    # Summarize older context
    summary_lines = []
    for item in older:
        role = item.get("role", "unknown")
        content = str(item.get("content", ""))[:100]
        summary_lines.append(f"[{role}] {content}...")

    summary_text = "\n".join(summary_lines)[:summary_budget]
    summary_entry = {
        "role": "system",
        "content": f"[AUTO-COMPACTED HISTORY]\n{summary_text}",
    }

    compacted = [summary_entry] + retained
    compacted_tokens = sum(len(str(item)) for item in compacted)
    reduction = ((original_tokens - compacted_tokens) / original_tokens * 100) if original_tokens > 0 else 0.0

    result = CompactionResult(
        success=True,
        original_tokens=original_tokens,
        compacted_tokens=compacted_tokens,
        reduction_pct=round(reduction, 1),
        method="auto_compact",
    )

    _breaker.record_success()
    _log_result(result)
    return result


def get_breaker_status() -> dict[str, Any]:
    """Return current circuit breaker state."""
    return _breaker.status()


def reset_breaker() -> None:
    """Manually reset the circuit breaker."""
    global _breaker
    _breaker = CircuitBreaker()


def _log_result(result: CompactionResult) -> None:
    """Append compaction result to log."""
    COMPACTION_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with COMPACTION_LOG_PATH.open("a") as f:
        f.write(
            json.dumps(
                {
                    "success": result.success,
                    "original_tokens": result.original_tokens,
                    "compacted_tokens": result.compacted_tokens,
                    "reduction_pct": result.reduction_pct,
                    "method": result.method,
                    "timestamp": result.timestamp,
                    "error": result.error,
                },
                default=str,
            )
            + "\n"
        )


if __name__ == "__main__":
    # Self-test
    test_context = [
        {"role": "user", "content": "Fix the login bug"},
        {"role": "tool_result", "content": "x" * 3000},
        {"role": "assistant", "content": "I found the issue"},
    ]
    result = compact_stale_tool_results(test_context)
    print(f"Microcompact: {result}")
    print(f"Breaker: {get_breaker_status()}")
