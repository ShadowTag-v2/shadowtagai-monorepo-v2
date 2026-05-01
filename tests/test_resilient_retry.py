# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Tests for the resilient_retry package.

Validates the battle-tested retry engine ported from Claude Code v2.1.91.
"""

from __future__ import annotations

import asyncio
import math
import time
from unittest.mock import MagicMock

import pytest

from packages.resilient_retry.retry_engine import (
    BASE_DELAY_MS,
    DEFAULT_MAX_RETRIES,
    FLOOR_OUTPUT_TOKENS,
    CannotRetryError,
    FallbackTriggeredError,
    RetryConfig,
    RetryContext,
    RetryEvent,
    RetryOutcome,
    RetryState,
    _get_header,
    _get_rate_limit_reset_delay_ms,
    _get_retry_after_ms,
    _get_status,
    _should_retry_529,
    _should_retry_error,
    get_retry_delay,
    is_overloaded_error,
    is_retryable_status,
    is_transient_capacity_error,
    parse_context_overflow,
    with_retry,
)


# ── Fixtures ──────────────────────────────────────────────────────────


class FakeAPIError(Exception):
    """Simulates an API error with status and headers."""

    def __init__(
        self,
        status: int,
        message: str = "API error",
        headers: dict | None = None,
    ) -> None:
        self.status = status
        self.headers = headers or {}
        super().__init__(message)


class FakeHTTPError(Exception):
    """Simulates an httpx-style error with response object."""

    def __init__(self, status_code: int, headers: dict | None = None) -> None:
        self.response = MagicMock()
        self.response.status_code = status_code
        self.response.headers = headers or {}
        super().__init__(f"HTTP {status_code}")


# ── get_retry_delay Tests ─────────────────────────────────────────────


class TestGetRetryDelay:
    def test_first_attempt_base_delay(self):
        delay = get_retry_delay(1)
        assert BASE_DELAY_MS <= delay <= BASE_DELAY_MS * 1.25

    def test_exponential_backoff(self):
        d1 = get_retry_delay(1)
        d2 = get_retry_delay(2)
        d3 = get_retry_delay(3)
        # Each should roughly double (within jitter)
        assert d2 > d1 * 1.5
        assert d3 > d2 * 1.5

    def test_max_delay_cap(self):
        delay = get_retry_delay(100, max_delay_ms=5000)
        assert delay <= 5000 * 1.25  # Max + jitter

    def test_retry_after_header_overrides(self):
        delay = get_retry_delay(1, retry_after_header="10")
        assert delay == 10_000

    def test_retry_after_invalid_falls_back(self):
        delay = get_retry_delay(1, retry_after_header="invalid")
        assert BASE_DELAY_MS <= delay <= BASE_DELAY_MS * 1.25

    def test_jitter_varies(self):
        delays = {get_retry_delay(3) for _ in range(20)}
        # With 25% jitter, we should see variation
        assert len(delays) > 1


# ── is_retryable_status Tests ─────────────────────────────────────────


class TestIsRetryableStatus:
    @pytest.mark.parametrize("status", [408, 409, 429, 500, 502, 503, 529])
    def test_retryable_statuses(self, status):
        assert is_retryable_status(status) is True

    @pytest.mark.parametrize("status", [200, 201, 400, 401, 403, 404, 422])
    def test_non_retryable_statuses(self, status):
        assert is_retryable_status(status) is False

    def test_none_status(self):
        assert is_retryable_status(None) is False


# ── is_overloaded_error Tests ─────────────────────────────────────────


class TestIsOverloadedError:
    def test_529_status(self):
        err = FakeAPIError(529)
        assert is_overloaded_error(err) is True

    def test_overloaded_in_message(self):
        err = Exception('{"type":"overloaded_error"}')
        assert is_overloaded_error(err) is True

    def test_non_overloaded(self):
        err = FakeAPIError(500, "Internal error")
        assert is_overloaded_error(err) is False


# ── is_transient_capacity_error Tests ─────────────────────────────────


class TestIsTransientCapacityError:
    def test_429_is_transient(self):
        assert is_transient_capacity_error(FakeAPIError(429)) is True

    def test_529_is_transient(self):
        assert is_transient_capacity_error(FakeAPIError(529)) is True

    def test_500_not_transient(self):
        assert is_transient_capacity_error(FakeAPIError(500)) is False


# ── parse_context_overflow Tests ──────────────────────────────────────


class TestParseContextOverflow:
    def test_valid_overflow_message(self):
        msg = "input length and `max_tokens` exceed context limit: 188059 + 20000 > 200000"
        result = parse_context_overflow(msg)
        assert result is not None
        assert result["input_tokens"] == 188059
        assert result["max_tokens"] == 20000
        assert result["context_limit"] == 200000

    def test_no_match(self):
        assert parse_context_overflow("some other error") is None

    def test_partial_match(self):
        msg = "input length and `max_tokens` exceed context limit: abc"
        assert parse_context_overflow(msg) is None


# ── _get_status Tests ─────────────────────────────────────────────────


class TestGetStatus:
    def test_anthropic_style(self):
        err = FakeAPIError(429)
        assert _get_status(err) == 429

    def test_httpx_style(self):
        err = FakeHTTPError(502)
        assert _get_status(err) == 502

    def test_no_status(self):
        assert _get_status(ValueError("oops")) is None


# ── _get_header Tests ─────────────────────────────────────────────────


class TestGetHeader:
    def test_anthropic_headers(self):
        err = FakeAPIError(429, headers={"retry-after": "5"})
        assert _get_header(err, "retry-after") == "5"

    def test_httpx_headers(self):
        err = FakeHTTPError(429, headers={"retry-after": "10"})
        assert _get_header(err, "retry-after") == "10"

    def test_missing_header(self):
        err = FakeAPIError(429, headers={})
        assert _get_header(err, "retry-after") is None


# ── _get_retry_after_ms Tests ─────────────────────────────────────────


class TestGetRetryAfterMs:
    def test_valid_header(self):
        err = FakeAPIError(429, headers={"retry-after": "5"})
        assert _get_retry_after_ms(err) == 5000

    def test_missing_header(self):
        err = FakeAPIError(429, headers={})
        assert _get_retry_after_ms(err) is None


# ── _should_retry_529 Tests ──────────────────────────────────────────


class TestShouldRetry529:
    def test_foreground_sources(self):
        assert _should_retry_529("repl_main_thread") is True
        assert _should_retry_529("sdk") is True
        assert _should_retry_529("compact") is True

    def test_background_sources(self):
        assert _should_retry_529("speculation") is False
        assert _should_retry_529("background_task") is False

    def test_none_defaults_to_retry(self):
        assert _should_retry_529(None) is True


# ── _should_retry_error Tests ─────────────────────────────────────────


class TestShouldRetryError:
    def test_connection_error(self):
        assert _should_retry_error(ConnectionError("reset")) is True

    def test_timeout_error(self):
        assert _should_retry_error(TimeoutError()) is True

    def test_retryable_status(self):
        assert _should_retry_error(FakeAPIError(502)) is True

    def test_non_retryable_status(self):
        assert _should_retry_error(FakeAPIError(401)) is False

    def test_context_overflow_retryable(self):
        msg = "input length and `max_tokens` exceed context limit: 188059 + 20000 > 200000"
        assert _should_retry_error(FakeAPIError(400, msg)) is True

    def test_persistent_429(self):
        assert _should_retry_error(FakeAPIError(429), persistent_mode=True) is True

    def test_overloaded_in_message(self):
        err = Exception('{"type":"overloaded_error"}')
        assert _should_retry_error(err) is True


# ── RetryConfig Tests ─────────────────────────────────────────────────


class TestRetryConfig:
    def test_defaults(self):
        cfg = RetryConfig()
        assert cfg.max_retries == DEFAULT_MAX_RETRIES
        assert cfg.model == ""
        assert cfg.fallback_model is None
        assert cfg.persistent_mode is False

    def test_custom(self):
        cfg = RetryConfig(max_retries=5, model="claude-4", persistent_mode=True)
        assert cfg.max_retries == 5
        assert cfg.model == "claude-4"


# ── RetryEvent Tests ──────────────────────────────────────────────────


class TestRetryEvent:
    def test_defaults(self):
        ev = RetryEvent()
        assert ev.attempt == 0
        assert ev.outcome == RetryOutcome.RETRIED
        assert ev.timestamp_ms > 0


# ── with_retry Integration Tests ─────────────────────────────────────


class TestWithRetry:
    @pytest.mark.asyncio
    async def test_success_first_attempt(self):
        async def op(attempt, ctx):
            return "ok"

        outcomes = []
        async for outcome, value in with_retry(op, RetryConfig()):
            outcomes.append((outcome, value))

        assert len(outcomes) == 1
        assert outcomes[0] == (RetryOutcome.SUCCESS, "ok")

    @pytest.mark.asyncio
    async def test_success_after_retries(self):
        call_count = 0

        async def op(attempt, ctx):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise FakeAPIError(502, "Bad Gateway")
            return "recovered"

        outcomes = []
        async for outcome, _value in with_retry(op, RetryConfig(max_retries=5)):
            outcomes.append(outcome)

        assert RetryOutcome.RETRIED in outcomes
        assert outcomes[-1] == RetryOutcome.SUCCESS

    @pytest.mark.asyncio
    async def test_exhausted_retries_raises(self):
        async def op(attempt, ctx):
            raise FakeAPIError(502, "Bad Gateway")

        with pytest.raises(CannotRetryError) as exc_info:
            async for _ in with_retry(op, RetryConfig(max_retries=2)):
                pass

        assert isinstance(exc_info.value.original_error, FakeAPIError)

    @pytest.mark.asyncio
    async def test_non_retryable_raises_immediately(self):
        async def op(attempt, ctx):
            raise FakeAPIError(401, "Unauthorized")

        with pytest.raises(CannotRetryError):
            async for _ in with_retry(op, RetryConfig(max_retries=5)):
                pass

    @pytest.mark.asyncio
    async def test_529_circuit_breaker_triggers_fallback(self):
        async def op(attempt, ctx):
            raise FakeAPIError(529, "Overloaded")

        cfg = RetryConfig(
            max_retries=10,
            model="claude-4",
            fallback_model="claude-3.5-sonnet",
            initial_consecutive_529=0,
        )

        with pytest.raises(FallbackTriggeredError) as exc_info:
            async for _ in with_retry(op, cfg):
                pass

        assert exc_info.value.original_model == "claude-4"
        assert exc_info.value.fallback_model == "claude-3.5-sonnet"

    @pytest.mark.asyncio
    async def test_529_circuit_breaker_no_fallback(self):
        async def op(attempt, ctx):
            raise FakeAPIError(529, "Overloaded")

        cfg = RetryConfig(max_retries=10, model="claude-4", fallback_model=None)
        events = []

        with pytest.raises(CannotRetryError):
            async for _outcome, _value in with_retry(op, cfg, on_retry=lambda e: events.append(e)):
                pass

        cb_events = [e for e in events if e.outcome == RetryOutcome.CIRCUIT_BREAKER_TRIPPED]
        assert len(cb_events) >= 1

    @pytest.mark.asyncio
    async def test_529_background_source_bails(self):
        async def op(attempt, ctx):
            raise FakeAPIError(529, "Overloaded")

        cfg = RetryConfig(
            max_retries=10,
            query_source="speculation",
        )

        with pytest.raises(CannotRetryError):
            async for _ in with_retry(op, cfg):
                pass

    @pytest.mark.asyncio
    async def test_context_overflow_adjusts_max_tokens(self):
        call_count = 0

        async def op(attempt, ctx):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise FakeAPIError(
                    400,
                    "input length and `max_tokens` exceed context limit: 188059 + 20000 > 200000",
                )
            return ctx.max_tokens_override

        results = []
        async for outcome, value in with_retry(op, RetryConfig()):
            if outcome == RetryOutcome.SUCCESS:
                results.append(value)

        assert len(results) == 1
        adjusted = results[0]
        assert adjusted is not None
        assert adjusted >= FLOOR_OUTPUT_TOKENS
        # 200000 - 188059 - 1000 = 10941
        assert adjusted == 10941

    @pytest.mark.asyncio
    async def test_context_overflow_below_floor_raises(self):
        async def op(attempt, ctx):
            raise FakeAPIError(
                400,
                "input length and `max_tokens` exceed context limit: 199000 + 20000 > 200000",
            )

        with pytest.raises(CannotRetryError):
            async for _ in with_retry(op, RetryConfig()):
                pass

    @pytest.mark.asyncio
    async def test_abort_event_cancels(self):
        abort = asyncio.Event()
        abort.set()

        async def op(attempt, ctx):
            return "should not reach"

        with pytest.raises(CannotRetryError):
            async for _ in with_retry(op, RetryConfig(abort_event=abort)):
                pass

    @pytest.mark.asyncio
    async def test_on_retry_callback_invoked(self):
        call_count = 0
        events: list[RetryEvent] = []

        async def op(attempt, ctx):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise FakeAPIError(502, "Bad Gateway")
            return "ok"

        async for _ in with_retry(
            op,
            RetryConfig(max_retries=5),
            on_retry=lambda e: events.append(e),
        ):
            pass

        assert len(events) == 2  # Two retries before success
        assert all(e.status_code == 502 for e in events)

    @pytest.mark.asyncio
    async def test_sync_operation_supported(self):
        def op(attempt, ctx):
            return "sync_ok"

        async for outcome, value in with_retry(op, RetryConfig()):
            assert outcome == RetryOutcome.SUCCESS
            assert value == "sync_ok"

    @pytest.mark.asyncio
    async def test_connection_error_retried(self):
        call_count = 0

        async def op(attempt, ctx):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ConnectionError("ECONNRESET")
            return "recovered"

        outcomes = []
        async for outcome, _value in with_retry(op, RetryConfig()):
            outcomes.append(outcome)

        assert RetryOutcome.RETRIED in outcomes
        assert outcomes[-1] == RetryOutcome.SUCCESS

    @pytest.mark.asyncio
    async def test_retry_after_header_honored(self):
        call_count = 0

        async def op(attempt, ctx):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise FakeAPIError(429, "Rate limited", {"retry-after": "1"})
            return "ok"

        events: list[RetryEvent] = []
        start = time.monotonic()
        async for _ in with_retry(
            op,
            RetryConfig(max_retries=3),
            on_retry=lambda e: events.append(e),
        ):
            pass
        elapsed = time.monotonic() - start

        assert len(events) == 1
        assert events[0].delay_ms == 1000
        assert elapsed >= 0.9  # Waited ~1 second


# ── Data Class Tests ──────────────────────────────────────────────────


class TestDataClasses:
    def test_retry_context_defaults(self):
        ctx = RetryContext()
        assert ctx.model == ""
        assert ctx.max_tokens_override is None
        assert ctx.attempt == 0

    def test_retry_state_defaults(self):
        state = RetryState()
        assert state.consecutive_529_errors == 0
        assert state.persistent_attempt == 0
        assert state.last_error is None

    def test_cannot_retry_preserves_error(self):
        original = ValueError("test")
        ctx = RetryContext(model="test-model", attempt=5)
        err = CannotRetryError(original, ctx)
        assert err.original_error is original
        assert err.retry_context.attempt == 5

    def test_fallback_triggered_message(self):
        err = FallbackTriggeredError("claude-4", "claude-3.5-sonnet")
        assert "claude-4" in str(err)
        assert "claude-3.5-sonnet" in str(err)


# ── Rate Limit Reset Delay Tests ──────────────────────────────────────


class TestRateLimitResetDelay:
    def test_valid_future_reset(self):
        future_ts = str(time.time() + 60)  # 60 seconds from now
        err = FakeAPIError(429, headers={"anthropic-ratelimit-unified-reset": future_ts})
        delay = _get_rate_limit_reset_delay_ms(err)
        assert delay is not None
        assert 55_000 <= delay <= 65_000

    def test_past_reset_returns_none(self):
        past_ts = str(time.time() - 60)
        err = FakeAPIError(429, headers={"anthropic-ratelimit-unified-reset": past_ts})
        assert _get_rate_limit_reset_delay_ms(err) is None

    def test_missing_header(self):
        err = FakeAPIError(429, headers={})
        assert _get_rate_limit_reset_delay_ms(err) is None

    def test_invalid_value(self):
        err = FakeAPIError(429, headers={"anthropic-ratelimit-unified-reset": "not-a-number"})
        assert _get_rate_limit_reset_delay_ms(err) is None

    def test_infinity_returns_none(self):
        err = FakeAPIError(429, headers={"anthropic-ratelimit-unified-reset": str(math.inf)})
        assert _get_rate_limit_reset_delay_ms(err) is None
