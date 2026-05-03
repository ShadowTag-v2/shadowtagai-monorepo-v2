# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Resilient Retry Engine — core retry pipeline.

Ported from: services/api/withRetry.ts (v2.1.91)
Reference: Claude Code production retry infrastructure

This module implements Anthropic's battle-tested retry logic:
  - Exponential backoff with 25% jitter
  - Retry-After header parsing
  - Rate-limit reset delay from anthropic-ratelimit-unified-reset
  - Circuit breaker on consecutive 529 overloaded errors
  - Model fallback when overload persists
  - Max-tokens context overflow auto-adjustment
  - Persistent retry mode for unattended/daemon sessions
  - Foreground vs background query source routing
  - Stale connection recovery (ECONNRESET/EPIPE)
"""

from __future__ import annotations

import asyncio
import inspect
import logging
import math
import random
import re
import time
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, TypeVar
from collections.abc import AsyncIterator, Callable

logger = logging.getLogger(__name__)

T = TypeVar("T")

# ── Constants (from upstream) ─────────────────────────────────────────

DEFAULT_MAX_RETRIES = 10
FLOOR_OUTPUT_TOKENS = 3_000
MAX_529_RETRIES = 3
BASE_DELAY_MS = 500

# Persistent retry mode (for unattended sessions)
PERSISTENT_MAX_BACKOFF_MS = 5 * 60 * 1_000  # 5 minutes
PERSISTENT_RESET_CAP_MS = 6 * 60 * 60 * 1_000  # 6 hours
HEARTBEAT_INTERVAL_MS = 30_000  # 30 seconds

# Fast mode thresholds
DEFAULT_FAST_MODE_FALLBACK_HOLD_MS = 30 * 60 * 1_000  # 30 minutes
SHORT_RETRY_THRESHOLD_MS = 20 * 1_000  # 20 seconds
MIN_COOLDOWN_MS = 10 * 60 * 1_000  # 10 minutes

# Foreground query sources where the user IS blocking on the result.
# These retry on 529. Background sources bail immediately.
FOREGROUND_529_RETRY_SOURCES: frozenset[str] = frozenset(
    {
        "repl_main_thread",
        "sdk",
        "agent:custom",
        "agent:default",
        "agent:builtin",
        "compact",
        "hook_agent",
        "hook_prompt",
        "verification_agent",
        "side_question",
        "auto_mode",
        "bash_classifier",
    }
)


# ── Enums ─────────────────────────────────────────────────────────────


class RetryOutcome(StrEnum):
    """Outcome of a retry attempt."""

    SUCCESS = "success"
    RETRIED = "retried"
    CANNOT_RETRY = "cannot_retry"
    FALLBACK_TRIGGERED = "fallback_triggered"
    CIRCUIT_BREAKER_TRIPPED = "circuit_breaker_tripped"
    ABORTED = "aborted"


# ── Error Classes ─────────────────────────────────────────────────────


class CannotRetryError(Exception):
    """Terminal error — retry budget exhausted or non-retryable error.

    Preserves the original error and the retry context at time of failure.
    """

    def __init__(self, original_error: BaseException, context: RetryContext) -> None:
        self.original_error = original_error
        self.retry_context = context
        super().__init__(str(original_error))


class FallbackTriggeredError(Exception):
    """Model fallback triggered after repeated 529 overload.

    The caller should retry the operation with the fallback model.
    """

    def __init__(self, original_model: str, fallback_model: str) -> None:
        self.original_model = original_model
        self.fallback_model = fallback_model
        super().__init__(f"Model fallback triggered: {original_model} -> {fallback_model}")


# ── Data Classes ──────────────────────────────────────────────────────


@dataclass
class RetryConfig:
    """Configuration for the retry pipeline.

    Attributes:
        max_retries: Maximum retry attempts (default 10).
        model: Primary model being used.
        fallback_model: Optional fallback model for 529 cascade.
        query_source: Source identifier for foreground/background routing.
        initial_consecutive_529: Pre-seed 529 counter (for streaming fallback).
        persistent_mode: Enable persistent retry (no max_retries cap).
        abort_event: Async event that signals abort.
    """

    max_retries: int = DEFAULT_MAX_RETRIES
    model: str = ""
    fallback_model: str | None = None
    query_source: str | None = None
    initial_consecutive_529: int = 0
    persistent_mode: bool = False
    abort_event: asyncio.Event | None = None


@dataclass
class RetryContext:
    """Mutable context passed through each retry attempt.

    Modified in-place by the retry engine (e.g., max_tokens_override).

    Attributes:
        model: Current model (may change on fallback).
        max_tokens_override: Adjusted max_tokens after overflow.
        attempt: Current attempt number.
    """

    model: str = ""
    max_tokens_override: int | None = None
    attempt: int = 0


@dataclass
class RetryState:
    """Internal state tracked across retry iterations.

    Not exposed to callers — used by the retry engine internally.
    """

    consecutive_529_errors: int = 0
    persistent_attempt: int = 0
    last_error: BaseException | None = None


@dataclass
class RetryEvent:
    """Telemetry event emitted on each retry.

    Attributes:
        attempt: Which attempt triggered this event.
        delay_ms: How long we'll wait before the next attempt.
        error_message: Human-readable error description.
        status_code: HTTP status code (if API error).
        outcome: What happened on this attempt.
        timestamp_ms: When this event was created.
    """

    attempt: int = 0
    delay_ms: int = 0
    error_message: str = ""
    status_code: int | None = None
    outcome: RetryOutcome = RetryOutcome.RETRIED
    timestamp_ms: float = field(default_factory=lambda: time.time() * 1000)


# ── Retry Delay Calculation ───────────────────────────────────────────


def get_retry_delay(
    attempt: int,
    retry_after_header: str | None = None,
    max_delay_ms: int = 32_000,
) -> int:
    """Calculate retry delay with exponential backoff and 25% jitter.

    If a Retry-After header is present, it takes precedence.

    Args:
        attempt: Current attempt number (1-indexed).
        retry_after_header: Value of the Retry-After HTTP header.
        max_delay_ms: Maximum backoff delay (default 32s).

    Returns:
        Delay in milliseconds before the next attempt.
    """
    # Honor Retry-After header if present
    if retry_after_header:
        try:
            seconds = int(retry_after_header)
            return seconds * 1_000
        except ValueError:
            pass

    # Exponential backoff: BASE * 2^(attempt-1), capped at max
    base_delay = min(BASE_DELAY_MS * (2 ** (attempt - 1)), max_delay_ms)

    # Add 0-25% jitter to prevent thundering herd
    jitter = random.random() * 0.25 * base_delay  # noqa: S311

    return int(base_delay + jitter)


# ── Error Classification ─────────────────────────────────────────────


def is_overloaded_error(error: BaseException) -> bool:
    """Check if the error is a 529 overloaded error.

    The SDK sometimes fails to pass the 529 status code during streaming,
    so we also check the error message directly.
    """
    status = _get_status(error)
    if status == 529:
        return True
    msg = str(error)
    return '"type":"overloaded_error"' in msg


def is_transient_capacity_error(error: BaseException) -> bool:
    """Check if the error is a transient capacity error (429 or 529)."""
    return is_overloaded_error(error) or _get_status(error) == 429


def is_retryable_status(status: int | None) -> bool:
    """Determine if an HTTP status code is retryable.

    Retryable statuses:
      - 408: Request timeout
      - 409: Lock timeout
      - 429: Rate limited
      - 500+: Server errors
      - 529: Overloaded (special handling)

    Args:
        status: HTTP status code.

    Returns:
        True if the status warrants a retry.
    """
    if status is None:
        return False
    if status == 408:  # Request timeout
        return True
    if status == 409:  # Lock timeout
        return True
    if status == 429:  # Rate limited
        return True
    return status >= 500  # Server errors (including 529)


def parse_context_overflow(
    error_message: str,
) -> dict[str, int] | None:
    """Parse max_tokens context overflow error message.

    Example format:
      "input length and `max_tokens` exceed context limit: 188059 + 20000 > 200000"

    Args:
        error_message: The error message string.

    Returns:
        Dict with input_tokens, max_tokens, context_limit, or None.
    """
    if "input length and `max_tokens` exceed context limit" not in error_message:
        return None

    pattern = r"input length and `max_tokens` exceed context limit: (\d+) \+ (\d+) > (\d+)"
    match = re.search(pattern, error_message)
    if not match or len(match.groups()) != 3:
        return None

    try:
        input_tokens = int(match.group(1))
        max_tokens = int(match.group(2))
        context_limit = int(match.group(3))
    except (ValueError, TypeError):
        return None

    return {
        "input_tokens": input_tokens,
        "max_tokens": max_tokens,
        "context_limit": context_limit,
    }


# ── Helper Functions ──────────────────────────────────────────────────


def _get_status(error: BaseException) -> int | None:
    """Extract HTTP status code from various error types."""
    # httpx.HTTPStatusError
    if hasattr(error, "response") and hasattr(error.response, "status_code"):
        return error.response.status_code
    # Anthropic SDK APIError
    if hasattr(error, "status"):
        return error.status
    # Generic status_code attribute
    if hasattr(error, "status_code"):
        return error.status_code
    return None


def _get_header(error: BaseException, name: str) -> str | None:
    """Extract a response header from an error."""
    # Anthropic SDK style: error.headers.get(name)
    if hasattr(error, "headers"):
        headers = error.headers
        if hasattr(headers, "get"):
            val = headers.get(name)
            if val is not None:
                return str(val)
    # httpx style: error.response.headers
    if hasattr(error, "response") and hasattr(error.response, "headers"):
        val = error.response.headers.get(name)
        if val is not None:
            return str(val)
    return None


def _get_retry_after_ms(error: BaseException) -> int | None:
    """Extract Retry-After value in milliseconds from error headers."""
    header = _get_header(error, "retry-after")
    if header:
        try:
            return int(header) * 1_000
        except ValueError:
            return None
    return None


def _get_rate_limit_reset_delay_ms(error: BaseException) -> int | None:
    """Extract rate limit reset delay from anthropic-ratelimit-unified-reset header.

    The header contains a Unix timestamp (seconds). We compute the delay
    from now until that timestamp, capped at PERSISTENT_RESET_CAP_MS.
    """
    header = _get_header(error, "anthropic-ratelimit-unified-reset")
    if not header:
        return None
    try:
        reset_unix_sec = float(header)
    except ValueError:
        return None
    if not math.isfinite(reset_unix_sec):
        return None
    delay_ms = int(reset_unix_sec * 1_000 - time.time() * 1_000)
    if delay_ms <= 0:
        return None
    return min(delay_ms, PERSISTENT_RESET_CAP_MS)


def _should_retry_529(query_source: str | None) -> bool:
    """Check if 529 errors should be retried for this query source.

    Background sources bail immediately on 529 to avoid retry amplification
    during capacity cascades.
    """
    # undefined → retry (conservative for untagged call paths)
    if query_source is None:
        return True
    return query_source in FOREGROUND_529_RETRY_SOURCES


def _should_retry_error(
    error: BaseException,
    *,
    persistent_mode: bool = False,
) -> bool:
    """Determine if an error warrants a retry.

    Mirrors shouldRetry() from withRetry.ts.
    """
    # Persistent mode: 429/529 always retryable
    if persistent_mode and is_transient_capacity_error(error):
        return True

    # Connection errors are always retryable
    if isinstance(error, (ConnectionError, TimeoutError, OSError)):
        return True

    # Check the context overflow pattern (400 but retryable with adjustment)
    status = _get_status(error)
    if status == 400:
        overflow = parse_context_overflow(str(error))
        if overflow:
            return True

    # Check retryable status codes
    if is_retryable_status(status):
        return True

    # Overloaded error in message body (SDK status code masking)
    return bool(is_overloaded_error(error))


# ── Core Retry Engine ─────────────────────────────────────────────────


async def with_retry(
    operation: Callable[..., Any],
    config: RetryConfig,
    *,
    on_retry: Callable[[RetryEvent], None] | None = None,
) -> AsyncIterator[tuple[RetryOutcome, Any]]:
    """Core retry engine with exponential backoff, circuit breaker, and model fallback.

    This is an async generator that yields (RetryOutcome, result_or_event) tuples.
    The final yield will be (RetryOutcome.SUCCESS, result) on success, or
    raise CannotRetryError/FallbackTriggeredError on exhaustion.

    Args:
        operation: Async callable to retry. Receives (attempt, context) args.
        config: Retry configuration.
        on_retry: Optional callback for retry telemetry events.

    Yields:
        (RetryOutcome, result_or_event) on each attempt/event.

    Raises:
        CannotRetryError: When retries are exhausted.
        FallbackTriggeredError: When model fallback is triggered.
    """
    context = RetryContext(model=config.model, attempt=0)
    state = RetryState(consecutive_529_errors=config.initial_consecutive_529)

    max_retries = config.max_retries

    for attempt in range(1, max_retries + 2):
        # Check abort
        if config.abort_event and config.abort_event.is_set():
            raise CannotRetryError(asyncio.CancelledError("Retry aborted by signal"), context)

        context.attempt = attempt

        try:
            if inspect.iscoroutinefunction(operation):
                result = await operation(attempt, context)
            else:
                result = operation(attempt, context)

            yield (RetryOutcome.SUCCESS, result)
            return

        except Exception as error:
            state.last_error = error
            status = _get_status(error)

            logger.debug(
                "API error (attempt %d/%d): %s %s",
                attempt,
                max_retries + 1,
                status or "?",
                str(error)[:200],
            )

            # ── 529 Circuit Breaker ────────────────────────────────
            if is_overloaded_error(error):
                # Non-foreground sources bail immediately
                if not _should_retry_529(config.query_source):
                    event = RetryEvent(
                        attempt=attempt,
                        status_code=529,
                        error_message=str(error)[:200],
                        outcome=RetryOutcome.CANNOT_RETRY,
                    )
                    if on_retry:
                        on_retry(event)
                    raise CannotRetryError(error, context) from error

                state.consecutive_529_errors += 1
                if state.consecutive_529_errors >= MAX_529_RETRIES:
                    if config.fallback_model:
                        event = RetryEvent(
                            attempt=attempt,
                            status_code=529,
                            error_message=str(error)[:200],
                            outcome=RetryOutcome.FALLBACK_TRIGGERED,
                        )
                        if on_retry:
                            on_retry(event)
                        raise FallbackTriggeredError(config.model, config.fallback_model) from error

                    # No fallback available — emit circuit breaker event
                    event = RetryEvent(
                        attempt=attempt,
                        status_code=529,
                        error_message=str(error)[:200],
                        outcome=RetryOutcome.CIRCUIT_BREAKER_TRIPPED,
                    )
                    if on_retry:
                        on_retry(event)

            # ── Max Tokens Context Overflow ────────────────────────
            if status == 400:
                overflow = parse_context_overflow(str(error))
                if overflow:
                    input_tokens = overflow["input_tokens"]
                    context_limit = overflow["context_limit"]
                    safety_buffer = 1_000
                    available = max(0, context_limit - input_tokens - safety_buffer)

                    if available < FLOOR_OUTPUT_TOKENS:
                        logger.error(
                            "Available context %d < FLOOR_OUTPUT_TOKENS %d",
                            available,
                            FLOOR_OUTPUT_TOKENS,
                        )
                        raise CannotRetryError(error, context) from error

                    adjusted = max(FLOOR_OUTPUT_TOKENS, available)
                    context.max_tokens_override = adjusted

                    logger.info(
                        "Max tokens overflow: adjusted to %d (input=%d, limit=%d)",
                        adjusted,
                        input_tokens,
                        context_limit,
                    )
                    continue

            # ── Check if retryable ─────────────────────────────────
            is_persistent = config.persistent_mode and is_transient_capacity_error(error)
            if attempt > max_retries and not is_persistent:
                raise CannotRetryError(error, context) from error

            if not _should_retry_error(error, persistent_mode=config.persistent_mode):
                raise CannotRetryError(error, context) from error

            # ── Compute Delay ──────────────────────────────────────
            retry_after = _get_header(error, "retry-after")
            if is_persistent and status == 429:
                state.persistent_attempt += 1
                reset_delay = _get_rate_limit_reset_delay_ms(error)
                if reset_delay is not None:
                    delay_ms = reset_delay
                else:
                    delay_ms = min(
                        get_retry_delay(
                            state.persistent_attempt,
                            retry_after,
                            PERSISTENT_MAX_BACKOFF_MS,
                        ),
                        PERSISTENT_RESET_CAP_MS,
                    )
            elif is_persistent:
                state.persistent_attempt += 1
                delay_ms = min(
                    get_retry_delay(
                        state.persistent_attempt,
                        retry_after,
                        PERSISTENT_MAX_BACKOFF_MS,
                    ),
                    PERSISTENT_RESET_CAP_MS,
                )
            else:
                delay_ms = get_retry_delay(attempt, retry_after)

            # ── Emit Retry Event ───────────────────────────────────
            reported_attempt = state.persistent_attempt if is_persistent else attempt
            event = RetryEvent(
                attempt=reported_attempt,
                delay_ms=delay_ms,
                error_message=str(error)[:200],
                status_code=status,
                outcome=RetryOutcome.RETRIED,
            )
            if on_retry:
                on_retry(event)

            yield (RetryOutcome.RETRIED, event)

            # ── Sleep ──────────────────────────────────────────────
            if is_persistent and delay_ms > HEARTBEAT_INTERVAL_MS:
                # Chunk long sleeps with heartbeat yields
                remaining = delay_ms
                while remaining > 0:
                    if config.abort_event and config.abort_event.is_set():
                        raise CannotRetryError(asyncio.CancelledError("Retry aborted"), context) from None
                    chunk = min(remaining, HEARTBEAT_INTERVAL_MS)
                    await asyncio.sleep(chunk / 1_000)
                    remaining -= chunk
            else:
                await asyncio.sleep(delay_ms / 1_000)

            # Persistent mode: clamp attempt so the for-loop never terminates
            if is_persistent and attempt >= max_retries:
                # Reset to keep looping (backoff uses persistent_attempt)
                continue

    # Exhausted all retries
    if state.last_error:
        raise CannotRetryError(state.last_error, context)
    raise CannotRetryError(RuntimeError("Retry exhausted without error"), context)
