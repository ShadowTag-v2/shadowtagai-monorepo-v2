# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Generic async retry with exponential backoff and circuit breaker integration.

Ported from src/services/api/withRetry.ts (Claude Code v2.1.91).

Core patterns extracted:
  - Exponential backoff with jitter
  - Retry-After header parsing
  - 529 overload detection
  - Configurable max retries
  - Abort signal support
  - Persistent (unattended) retry mode

Provider-specific SDK types (Anthropic, Bedrock, Vertex) are stripped.
This is a generic retry decorator usable with any async callable.
"""

from __future__ import annotations

import asyncio
import logging
import os
import random
import time
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Callable, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")

# ── Constants (from withRetry.ts) ──
DEFAULT_MAX_RETRIES: int = 10
BASE_DELAY_MS: int = 500
MAX_529_RETRIES: int = 3
PERSISTENT_MAX_BACKOFF_MS: int = 5 * 60 * 1000  # 5 min
PERSISTENT_RESET_CAP_MS: int = 6 * 60 * 60 * 1000  # 6 hours
HEARTBEAT_INTERVAL_MS: int = 30_000


class RetryOutcome(StrEnum):
    """Outcome of a single retry attempt."""
    SUCCESS = "success"
    RETRIED = "retried"
    EXHAUSTED = "exhausted"
    ABORTED = "aborted"
    FALLEN_BACK = "fallen_back"


@dataclass(frozen=True, slots=True)
class RetryStats:
    """Statistics from a completed retry loop."""
    total_attempts: int
    total_delay_ms: float
    outcome: RetryOutcome
    last_error: str | None = None
    consecutive_529s: int = 0


class CannotRetryError(Exception):
    """Raised when retries are exhausted or the error is non-retryable."""

    def __init__(self, original: Exception, *, attempts: int = 0) -> None:
        super().__init__(str(original))
        self.original = original
        self.attempts = attempts


class FallbackTriggeredError(Exception):
    """Raised when a model fallback is triggered after repeated 529s."""

    def __init__(self, original_model: str, fallback_model: str) -> None:
        super().__init__(f"Model fallback: {original_model} -> {fallback_model}")
        self.original_model = original_model
        self.fallback_model = fallback_model


# ── Core retry functions ──

def get_retry_delay(
    attempt: int,
    retry_after_header: str | None = None,
    max_delay_ms: float = 32_000,
) -> float:
    """Calculate retry delay with exponential backoff + jitter.

    If a Retry-After header is present and parseable, use it directly.
    Otherwise: min(BASE_DELAY_MS * 2^(attempt-1), max_delay_ms) + jitter.
    """
    if retry_after_header:
        try:
            seconds = int(retry_after_header)
            return seconds * 1000
        except ValueError:
            pass

    base_delay = min(BASE_DELAY_MS * (2 ** (attempt - 1)), max_delay_ms)
    jitter = random.random() * 0.25 * base_delay  # noqa: S311
    return base_delay + jitter


def is_retryable_status(status: int) -> bool:
    """Return True if the HTTP status code should trigger a retry."""
    if status == 408:  # Request timeout
        return True
    if status == 409:  # Lock timeout
        return True
    if status == 429:  # Rate limit
        return True
    if status == 529:  # Overloaded
        return True
    if status >= 500:  # Server errors
        return True
    return False


def is_529_error(status: int | None, message: str = "") -> bool:
    """Detect 529 overloaded errors (status code or message sniffing)."""
    if status == 529:
        return True
    return '"type":"overloaded_error"' in message


def get_max_retries() -> int:
    """Get max retries from env or default."""
    env_val = os.environ.get("CLAUDE_CODE_MAX_RETRIES")
    if env_val:
        try:
            return int(env_val)
        except ValueError:
            pass
    return DEFAULT_MAX_RETRIES


def is_persistent_retry_enabled() -> bool:
    """Check if persistent (unattended) retry mode is active."""
    val = os.environ.get("CLAUDE_CODE_UNATTENDED_RETRY", "")
    return val.lower() in ("1", "true", "yes")


@dataclass
class RetryConfig:
    """Configuration for a retry loop."""
    max_retries: int = field(default_factory=get_max_retries)
    base_delay_ms: float = BASE_DELAY_MS
    max_delay_ms: float = 32_000
    max_529_retries: int = MAX_529_RETRIES
    fallback_model: str | None = None
    persistent: bool = field(default_factory=is_persistent_retry_enabled)


async def with_retry(
    operation: Callable[..., Any],
    config: RetryConfig | None = None,
    *,
    abort_event: asyncio.Event | None = None,
    on_retry: Callable[[int, float, Exception], None] | None = None,
) -> tuple[Any, RetryStats]:
    """Execute an async operation with retry logic.

    Args:
        operation: Async callable to execute. Should raise on failure.
        config: Retry configuration. Uses defaults if None.
        abort_event: If set, abort when this event fires.
        on_retry: Optional callback(attempt, delay_ms, error) on each retry.

    Returns:
        Tuple of (result, RetryStats).

    Raises:
        CannotRetryError: When retries are exhausted.
        FallbackTriggeredError: When too many 529s trigger a model fallback.
    """
    cfg = config or RetryConfig()
    consecutive_529s = 0
    total_delay_ms = 0.0
    last_error: Exception | None = None

    max_attempts = cfg.max_retries + 1

    for attempt in range(1, max_attempts + 1):
        if abort_event and abort_event.is_set():
            raise CannotRetryError(
                last_error or Exception("Aborted"), attempts=attempt
            )

        try:
            result = await operation()
            return result, RetryStats(
                total_attempts=attempt,
                total_delay_ms=total_delay_ms,
                outcome=RetryOutcome.SUCCESS,
            )
        except Exception as e:
            last_error = e

            # Extract status code if available
            status = getattr(e, "status", getattr(e, "status_code", None))
            message = str(e)

            logger.debug(
                "Retry attempt %d/%d failed: %s (status=%s)",
                attempt, max_attempts, message[:200], status,
            )

            # Track 529s for fallback
            if is_529_error(status, message):
                consecutive_529s += 1
                if consecutive_529s >= cfg.max_529_retries and cfg.fallback_model:
                    raise FallbackTriggeredError("primary", cfg.fallback_model) from e

            # Check if we should retry
            is_persistent = cfg.persistent and status in (429, 529)
            if attempt >= max_attempts and not is_persistent:
                raise CannotRetryError(e, attempts=attempt) from e

            if status is not None and not is_retryable_status(status):
                raise CannotRetryError(e, attempts=attempt) from e

            # Calculate delay
            retry_after = None
            headers = getattr(e, "headers", None)
            if headers:
                if hasattr(headers, "get"):
                    retry_after = headers.get("retry-after")
                elif isinstance(headers, dict):
                    retry_after = headers.get("retry-after")

            delay_ms = get_retry_delay(attempt, retry_after, cfg.max_delay_ms)
            total_delay_ms += delay_ms

            if on_retry:
                on_retry(attempt, delay_ms, e)

            # Sleep
            delay_seconds = delay_ms / 1000
            if abort_event:
                try:
                    await asyncio.wait_for(
                        abort_event.wait(), timeout=delay_seconds
                    )
                    raise CannotRetryError(e, attempts=attempt) from e
                except asyncio.TimeoutError:
                    pass  # Normal — event didn't fire during sleep
            else:
                await asyncio.sleep(delay_seconds)

    raise CannotRetryError(
        last_error or Exception("All retries exhausted"),
        attempts=max_attempts,
    )


# ── Synchronous variant ──

def with_retry_sync(
    operation: Callable[..., T],
    config: RetryConfig | None = None,
    *,
    on_retry: Callable[[int, float, Exception], None] | None = None,
) -> tuple[T, RetryStats]:
    """Synchronous retry wrapper.

    Same logic as with_retry but for sync callables.
    """
    cfg = config or RetryConfig()
    consecutive_529s = 0
    total_delay_ms = 0.0
    last_error: Exception | None = None

    max_attempts = cfg.max_retries + 1

    for attempt in range(1, max_attempts + 1):
        try:
            result = operation()
            return result, RetryStats(
                total_attempts=attempt,
                total_delay_ms=total_delay_ms,
                outcome=RetryOutcome.SUCCESS,
            )
        except Exception as e:
            last_error = e
            status = getattr(e, "status", getattr(e, "status_code", None))
            message = str(e)

            if is_529_error(status, message):
                consecutive_529s += 1
                if consecutive_529s >= cfg.max_529_retries and cfg.fallback_model:
                    raise FallbackTriggeredError("primary", cfg.fallback_model) from e

            is_persistent = cfg.persistent and status in (429, 529)
            if attempt >= max_attempts and not is_persistent:
                raise CannotRetryError(e, attempts=attempt) from e

            if status is not None and not is_retryable_status(status):
                raise CannotRetryError(e, attempts=attempt) from e

            delay_ms = get_retry_delay(attempt, max_delay_ms=cfg.max_delay_ms)
            total_delay_ms += delay_ms

            if on_retry:
                on_retry(attempt, delay_ms, e)

            time.sleep(delay_ms / 1000)

    raise CannotRetryError(
        last_error or Exception("All retries exhausted"),
        attempts=max_attempts,
    )
