# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Unit tests for Circuit Breaker — Core state machine + Registry.

Validates all state transitions, timing behavior, thread safety,
telemetry integration, and edge cases.

Coverage targets:
  - State transitions: CLOSED→OPEN→HALF_OPEN→CLOSED
  - Threshold gating: exact-boundary failure counting
  - Timeout probe: OPEN→HALF_OPEN after reset_timeout_s
  - Recovery: success in HALF_OPEN → CLOSED
  - Re-trip: failure in HALF_OPEN → OPEN
  - Advisory mode: allow_request() returns bool
  - Mandatory mode: wrap() raises CircuitBreakerOpenError
  - Registry: register/get/health/reset_all
  - Thread safety: concurrent record_failure from multiple threads
  - Callback: on_state_change fires with correct arguments
"""

from __future__ import annotations

import asyncio
import time
from unittest.mock import MagicMock

import pytest

from circuit_breaker.breaker import (
    CircuitBreaker,
    CircuitBreakerOpenError,
    CircuitBreakerState,
)
from circuit_breaker.registry import CircuitBreakerRegistry


# ───────────────────────────────────────────────────────────────────
# Fixtures
# ───────────────────────────────────────────────────────────────────


@pytest.fixture
def breaker() -> CircuitBreaker:
    """Standard breaker: threshold=3, timeout=60s."""
    return CircuitBreaker("test_service", failure_threshold=3, reset_timeout_s=60.0)


@pytest.fixture
def fast_breaker() -> CircuitBreaker:
    """Fast-timeout breaker for timing tests: threshold=2, timeout=0.1s."""
    return CircuitBreaker("fast_service", failure_threshold=2, reset_timeout_s=0.1)


@pytest.fixture
def callback_breaker() -> tuple[CircuitBreaker, MagicMock]:
    """Breaker with mocked on_state_change callback."""
    cb = MagicMock()
    b = CircuitBreaker("cb_service", failure_threshold=2, reset_timeout_s=0.5, on_state_change=cb)
    return b, cb


@pytest.fixture
def registry() -> CircuitBreakerRegistry:
    """Empty registry."""
    return CircuitBreakerRegistry()


# ───────────────────────────────────────────────────────────────────
# State Transitions
# ───────────────────────────────────────────────────────────────────


class TestStateTransitions:
    """Validate the CLOSED → OPEN → HALF_OPEN → CLOSED state machine."""

    def test_initial_state_is_closed(self, breaker: CircuitBreaker) -> None:
        assert breaker.state == CircuitBreakerState.CLOSED
        assert breaker.consecutive_failures == 0

    def test_stays_closed_below_threshold(self, breaker: CircuitBreaker) -> None:
        breaker.record_failure()
        breaker.record_failure()
        # 2 failures, threshold is 3 — still closed
        assert breaker.state == CircuitBreakerState.CLOSED
        assert breaker.consecutive_failures == 2

    def test_opens_at_threshold(self, breaker: CircuitBreaker) -> None:
        for _ in range(3):
            breaker.record_failure()
        assert breaker.state == CircuitBreakerState.OPEN
        assert breaker.consecutive_failures == 3

    def test_opens_above_threshold(self, breaker: CircuitBreaker) -> None:
        for _ in range(5):
            breaker.record_failure()
        assert breaker.state == CircuitBreakerState.OPEN
        assert breaker.consecutive_failures == 5

    def test_success_resets_failure_count(self, breaker: CircuitBreaker) -> None:
        breaker.record_failure()
        breaker.record_failure()
        breaker.record_success()
        assert breaker.consecutive_failures == 0
        assert breaker.state == CircuitBreakerState.CLOSED

    def test_open_to_half_open_after_timeout(self, fast_breaker: CircuitBreaker) -> None:
        fast_breaker.record_failure()
        fast_breaker.record_failure()
        assert fast_breaker.state == CircuitBreakerState.OPEN

        # Wait for reset timeout
        time.sleep(0.15)
        assert fast_breaker.state == CircuitBreakerState.HALF_OPEN

    def test_half_open_to_closed_on_success(self, fast_breaker: CircuitBreaker) -> None:
        fast_breaker.record_failure()
        fast_breaker.record_failure()
        time.sleep(0.15)
        assert fast_breaker.state == CircuitBreakerState.HALF_OPEN

        fast_breaker.record_success()
        assert fast_breaker.state == CircuitBreakerState.CLOSED
        assert fast_breaker.consecutive_failures == 0

    def test_half_open_to_open_on_failure(self, fast_breaker: CircuitBreaker) -> None:
        fast_breaker.record_failure()
        fast_breaker.record_failure()
        time.sleep(0.15)
        assert fast_breaker.state == CircuitBreakerState.HALF_OPEN

        fast_breaker.record_failure()
        assert fast_breaker.state == CircuitBreakerState.OPEN

    def test_manual_reset(self, breaker: CircuitBreaker) -> None:
        for _ in range(3):
            breaker.record_failure()
        assert breaker.state == CircuitBreakerState.OPEN

        breaker.reset()
        assert breaker.state == CircuitBreakerState.CLOSED
        assert breaker.consecutive_failures == 0


# ───────────────────────────────────────────────────────────────────
# Advisory Mode (allow_request)
# ───────────────────────────────────────────────────────────────────


class TestAdvisoryMode:
    """Validate allow_request() advisory behavior."""

    def test_allows_when_closed(self, breaker: CircuitBreaker) -> None:
        assert breaker.allow_request() is True

    def test_rejects_when_open(self, breaker: CircuitBreaker) -> None:
        for _ in range(3):
            breaker.record_failure()
        assert breaker.allow_request() is False

    def test_allows_probe_in_half_open(self, fast_breaker: CircuitBreaker) -> None:
        fast_breaker.record_failure()
        fast_breaker.record_failure()
        time.sleep(0.15)
        # First probe should be allowed
        assert fast_breaker.allow_request() is True
        # Second probe should be rejected (max_probes=1)
        assert fast_breaker.allow_request() is False

    def test_seconds_until_probe(self, breaker: CircuitBreaker) -> None:
        assert breaker.seconds_until_probe == 0.0

        for _ in range(3):
            breaker.record_failure()

        remaining = breaker.seconds_until_probe
        assert remaining > 0
        assert remaining <= 60.0


# ───────────────────────────────────────────────────────────────────
# Mandatory Mode (wrap decorator)
# ───────────────────────────────────────────────────────────────────


class TestDecoratorMode:
    """Validate the @breaker.wrap mandatory mode."""

    def test_sync_wrap_success(self, breaker: CircuitBreaker) -> None:
        @breaker.wrap
        def fn() -> str:
            return "ok"

        result = fn()
        assert result == "ok"
        assert breaker.total_successes == 1

    def test_sync_wrap_failure(self, breaker: CircuitBreaker) -> None:
        @breaker.wrap
        def fn() -> str:
            msg = "boom"
            raise ValueError(msg)

        with pytest.raises(ValueError, match="boom"):
            fn()
        assert breaker.consecutive_failures == 1

    def test_sync_wrap_raises_when_open(self, breaker: CircuitBreaker) -> None:
        for _ in range(3):
            breaker.record_failure()

        @breaker.wrap
        def fn() -> str:
            return "should not reach"

        with pytest.raises(CircuitBreakerOpenError) as exc_info:
            fn()

        assert exc_info.value.service_name == "test_service"
        assert exc_info.value.failure_count == 3

    def test_async_wrap_success(self, breaker: CircuitBreaker) -> None:
        @breaker.wrap
        async def fn() -> str:
            return "ok"

        result = asyncio.run(fn())
        assert result == "ok"
        assert breaker.total_successes == 1

    def test_async_wrap_failure(self, breaker: CircuitBreaker) -> None:
        @breaker.wrap
        async def fn() -> str:
            msg = "boom"
            raise ValueError(msg)

        with pytest.raises(ValueError, match="boom"):
            asyncio.run(fn())
        assert breaker.consecutive_failures == 1

    def test_async_wrap_raises_when_open(self, breaker: CircuitBreaker) -> None:
        for _ in range(3):
            breaker.record_failure()

        @breaker.wrap
        async def fn() -> str:
            return "should not reach"

        with pytest.raises(CircuitBreakerOpenError):
            asyncio.run(fn())


# ───────────────────────────────────────────────────────────────────
# Callback / Telemetry Integration
# ───────────────────────────────────────────────────────────────────


class TestCallbacks:
    """Validate on_state_change callback wiring."""

    def test_callback_on_open(self, callback_breaker: tuple[CircuitBreaker, MagicMock]) -> None:
        breaker, cb = callback_breaker
        breaker.record_failure()
        breaker.record_failure()

        cb.assert_called_once_with(
            CircuitBreakerState.CLOSED,
            CircuitBreakerState.OPEN,
            "cb_service",
        )

    def test_callback_on_recovery(self, callback_breaker: tuple[CircuitBreaker, MagicMock]) -> None:
        breaker, cb = callback_breaker
        # Trip it
        breaker.record_failure()
        breaker.record_failure()
        cb.reset_mock()

        # Wait for half-open
        time.sleep(0.55)
        _ = breaker.state  # Trigger transition check
        cb.assert_called_once_with(
            CircuitBreakerState.OPEN,
            CircuitBreakerState.HALF_OPEN,
            "cb_service",
        )
        cb.reset_mock()

        # Recover
        breaker.record_success()
        cb.assert_called_once_with(
            CircuitBreakerState.HALF_OPEN,
            CircuitBreakerState.CLOSED,
            "cb_service",
        )

    def test_callback_exception_does_not_break_breaker(self, breaker: CircuitBreaker) -> None:
        cb = MagicMock(side_effect=RuntimeError("callback crash"))
        b = CircuitBreaker("crash_test", failure_threshold=1, on_state_change=cb)

        # Should not raise despite callback crash
        b.record_failure()
        assert b.state == CircuitBreakerState.OPEN
        cb.assert_called_once()


# ───────────────────────────────────────────────────────────────────
# Snapshot / Diagnostics
# ───────────────────────────────────────────────────────────────────


class TestDiagnostics:
    """Validate snapshot() output and repr."""

    def test_snapshot_closed(self, breaker: CircuitBreaker) -> None:
        snap = breaker.snapshot()
        assert snap["service_name"] == "test_service"
        assert snap["state"] == "closed"
        assert snap["consecutive_failures"] == 0
        assert snap["failure_threshold"] == 3

    def test_snapshot_open(self, breaker: CircuitBreaker) -> None:
        for _ in range(3):
            breaker.record_failure()
        snap = breaker.snapshot()
        assert snap["state"] == "open"
        assert snap["consecutive_failures"] == 3
        assert snap["seconds_until_probe"] > 0

    def test_repr(self, breaker: CircuitBreaker) -> None:
        r = repr(breaker)
        assert "test_service" in r
        assert "closed" in r
        assert "0/3" in r


# ───────────────────────────────────────────────────────────────────
# Thread Safety
# ───────────────────────────────────────────────────────────────────


class TestThreadSafety:
    """Validate concurrent access from multiple threads."""

    def test_concurrent_failures(self) -> None:
        import threading

        breaker = CircuitBreaker("concurrent", failure_threshold=100, reset_timeout_s=60.0)

        def hammer() -> None:
            for _ in range(50):
                breaker.record_failure()

        threads = [threading.Thread(target=hammer) for _ in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # 4 threads × 50 failures = 200 total failures
        assert breaker.total_failures == 200
        assert breaker.state == CircuitBreakerState.OPEN

    def test_concurrent_mixed(self) -> None:
        import threading

        breaker = CircuitBreaker("mixed", failure_threshold=50, reset_timeout_s=60.0)

        def fail_loop() -> None:
            for _ in range(25):
                breaker.record_failure()

        def success_loop() -> None:
            for _ in range(25):
                breaker.record_success()

        threads = [
            threading.Thread(target=fail_loop),
            threading.Thread(target=success_loop),
            threading.Thread(target=fail_loop),
            threading.Thread(target=success_loop),
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Exact state depends on interleaving, but counts should be consistent
        assert breaker.total_failures == 50
        assert breaker.total_successes == 50


# ───────────────────────────────────────────────────────────────────
# Registry
# ───────────────────────────────────────────────────────────────────


class TestRegistry:
    """Validate CircuitBreakerRegistry operations."""

    def test_register_and_get(self, registry: CircuitBreakerRegistry) -> None:
        breaker = registry.register("firestore", failure_threshold=5)
        assert registry.get("firestore") is breaker

    def test_duplicate_register_returns_existing(self, registry: CircuitBreakerRegistry) -> None:
        b1 = registry.register("svc")
        b2 = registry.register("svc")
        assert b1 is b2

    def test_get_unknown_raises(self, registry: CircuitBreakerRegistry) -> None:
        with pytest.raises(KeyError, match="no_such_service"):
            registry.get("no_such_service")

    def test_get_or_create(self, registry: CircuitBreakerRegistry) -> None:
        b1 = registry.get_or_create("auto_svc")
        b2 = registry.get_or_create("auto_svc")
        assert b1 is b2
        assert "auto_svc" in registry.service_names

    def test_health_report(self, registry: CircuitBreakerRegistry) -> None:
        registry.register("a")
        registry.register("b")
        report = registry.health_report()
        assert set(report.keys()) == {"a", "b"}
        assert report["a"]["state"] == "closed"

    def test_open_breakers(self, registry: CircuitBreakerRegistry) -> None:
        b = registry.register("flaky", failure_threshold=1)
        b.record_failure()
        assert registry.open_breakers() == ["flaky"]

    def test_reset_all(self, registry: CircuitBreakerRegistry) -> None:
        b1 = registry.register("s1", failure_threshold=1)
        b2 = registry.register("s2", failure_threshold=1)
        b1.record_failure()
        b2.record_failure()

        count = registry.reset_all()
        assert count == 2
        assert b1.state == CircuitBreakerState.CLOSED
        assert b2.state == CircuitBreakerState.CLOSED

    def test_global_callback(self) -> None:
        cb = MagicMock()
        registry = CircuitBreakerRegistry(global_on_state_change=cb)
        b = registry.register("global_test", failure_threshold=1)
        b.record_failure()

        cb.assert_called_once_with(
            CircuitBreakerState.CLOSED,
            CircuitBreakerState.OPEN,
            "global_test",
        )

    def test_len_and_repr(self, registry: CircuitBreakerRegistry) -> None:
        registry.register("x")
        registry.register("y")
        assert len(registry) == 2
        r = repr(registry)
        assert "x" in r
        assert "y" in r


# ───────────────────────────────────────────────────────────────────
# CircuitBreakerOpenError
# ───────────────────────────────────────────────────────────────────


class TestCircuitBreakerOpenError:
    """Validate error attributes."""

    def test_error_attributes(self) -> None:
        err = CircuitBreakerOpenError("my_svc", failure_count=5, seconds_until_probe=30.5)
        assert err.service_name == "my_svc"
        assert err.failure_count == 5
        assert err.seconds_until_probe == 30.5
        assert "my_svc" in str(err)
        assert "5" in str(err)


# ───────────────────────────────────────────────────────────────────
# Edge Cases
# ───────────────────────────────────────────────────────────────────


class TestEdgeCases:
    """Boundary conditions and degenerate inputs."""

    def test_threshold_one(self) -> None:
        b = CircuitBreaker("fragile", failure_threshold=1)
        b.record_failure()
        assert b.state == CircuitBreakerState.OPEN

    def test_success_on_closed_is_noop(self, breaker: CircuitBreaker) -> None:
        breaker.record_success()
        assert breaker.state == CircuitBreakerState.CLOSED
        assert breaker.total_successes == 1

    def test_multiple_resets(self, breaker: CircuitBreaker) -> None:
        breaker.reset()
        breaker.reset()
        assert breaker.state == CircuitBreakerState.CLOSED

    def test_rapid_open_close_cycle(self) -> None:
        b = CircuitBreaker("rapid", failure_threshold=1, reset_timeout_s=0.05)
        for _ in range(10):
            b.record_failure()
            assert b.state == CircuitBreakerState.OPEN
            time.sleep(0.06)
            assert b.state == CircuitBreakerState.HALF_OPEN
            b.record_success()
            assert b.state == CircuitBreakerState.CLOSED
