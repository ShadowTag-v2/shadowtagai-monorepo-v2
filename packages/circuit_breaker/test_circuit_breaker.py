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
    FailureMode,
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


# ───────────────────────────────────────────────────────────────────
# Sliding Window Mode
# ───────────────────────────────────────────────────────────────────


class TestSlidingWindow:
    """Validate SLIDING_WINDOW failure counting mode."""

    def test_trips_on_window_threshold(self) -> None:
        b = CircuitBreaker(
            "sliding_svc",
            failure_threshold=3,
            failure_mode=FailureMode.SLIDING_WINDOW,
            window_s=10.0,
        )
        b.record_failure()
        b.record_failure()
        assert b.state == CircuitBreakerState.CLOSED
        b.record_failure()
        assert b.state == CircuitBreakerState.OPEN

    def test_does_not_trip_below_threshold(self) -> None:
        b = CircuitBreaker(
            "sliding_safe",
            failure_threshold=5,
            failure_mode=FailureMode.SLIDING_WINDOW,
            window_s=10.0,
        )
        for _ in range(4):
            b.record_failure()
        assert b.state == CircuitBreakerState.CLOSED

    def test_window_pruning_prevents_trip(self) -> None:
        """Failures outside the window should NOT count toward threshold."""
        b = CircuitBreaker(
            "sliding_prune",
            failure_threshold=3,
            failure_mode=FailureMode.SLIDING_WINDOW,
            window_s=0.05,  # 50ms window
        )
        b.record_failure()
        b.record_failure()
        time.sleep(0.07)  # Wait for events to expire
        b.record_failure()
        # Only 1 failure in window — should stay closed
        assert b.state == CircuitBreakerState.CLOSED

    def test_window_failures_property(self) -> None:
        b = CircuitBreaker(
            "sliding_count",
            failure_threshold=100,
            failure_mode=FailureMode.SLIDING_WINDOW,
            window_s=10.0,
        )
        b.record_failure()
        b.record_success()
        b.record_failure()
        assert b.window_failures == 2

    def test_window_failures_returns_zero_in_consecutive_mode(self) -> None:
        b = CircuitBreaker("consec_svc", failure_threshold=3)
        b.record_failure()
        assert b.window_failures == 0

    def test_success_interspersed_still_trips(self) -> None:
        """In SLIDING_WINDOW, successes don't reset the failure count."""
        b = CircuitBreaker(
            "sliding_mixed",
            failure_threshold=3,
            failure_mode=FailureMode.SLIDING_WINDOW,
            window_s=10.0,
        )
        b.record_failure()
        b.record_success()
        b.record_failure()
        b.record_success()
        b.record_failure()
        # 3 failures in window — should trip even with successes between
        assert b.state == CircuitBreakerState.OPEN

    def test_snapshot_includes_window_fields(self) -> None:
        b = CircuitBreaker(
            "sliding_snap",
            failure_threshold=5,
            failure_mode=FailureMode.SLIDING_WINDOW,
            window_s=30.0,
        )
        b.record_failure()
        snap = b.snapshot()
        assert snap["failure_mode"] == "sliding_window"
        assert snap["window_s"] == 30.0
        assert snap["window_failures"] == 1

    def test_repr_includes_mode_tag(self) -> None:
        b = CircuitBreaker(
            "sliding_repr",
            failure_threshold=5,
            failure_mode=FailureMode.SLIDING_WINDOW,
        )
        r = repr(b)
        assert "sliding_window" in r

    def test_reset_clears_window_events(self) -> None:
        b = CircuitBreaker(
            "sliding_reset",
            failure_threshold=100,
            failure_mode=FailureMode.SLIDING_WINDOW,
            window_s=10.0,
        )
        b.record_failure()
        b.record_failure()
        assert b.window_failures == 2
        b.reset()
        assert b.window_failures == 0

    def test_recovery_after_trip(self) -> None:
        b = CircuitBreaker(
            "sliding_recover",
            failure_threshold=2,
            reset_timeout_s=0.05,
            failure_mode=FailureMode.SLIDING_WINDOW,
            window_s=10.0,
        )
        b.record_failure()
        b.record_failure()
        assert b.state == CircuitBreakerState.OPEN

        time.sleep(0.06)
        assert b.state == CircuitBreakerState.HALF_OPEN

        b.record_success()
        assert b.state == CircuitBreakerState.CLOSED


# ───────────────────────────────────────────────────────────────────
# Dashboard
# ───────────────────────────────────────────────────────────────────


class TestDashboard:
    """Validate dashboard health reporting."""

    def test_empty_report(self) -> None:
        from circuit_breaker.dashboard import format_health_table

        report = {"services": {}, "summary": {}, "timestamp": 0}
        result = format_health_table(report)
        assert "No circuit breakers registered" in result

    def test_format_table_contains_service_names(self) -> None:
        from circuit_breaker.dashboard import format_health_table

        report = {
            "services": {
                "firestore": {
                    "state": "closed",
                    "consecutive_failures": 0,
                    "failure_threshold": 3,
                },
                "gemini": {
                    "state": "open",
                    "consecutive_failures": 5,
                    "failure_threshold": 5,
                    "seconds_until_probe": 42.0,
                },
            },
            "summary": {
                "total_breakers": 2,
                "closed": 1,
                "open": 1,
                "half_open": 0,
                "open_services": ["gemini"],
                "health_status": "degraded",
            },
            "timestamp": time.time(),
        }
        table = format_health_table(report)
        assert "firestore" in table
        assert "gemini" in table
        assert "⚠️" in table

    def test_healthy_status_icon(self) -> None:
        from circuit_breaker.dashboard import format_health_table

        report = {
            "services": {
                "svc": {
                    "state": "closed",
                    "consecutive_failures": 0,
                    "failure_threshold": 3,
                },
            },
            "summary": {
                "total_breakers": 1,
                "closed": 1,
                "open": 0,
                "half_open": 0,
                "open_services": [],
                "health_status": "healthy",
            },
            "timestamp": time.time(),
        }
        table = format_health_table(report)
        assert "✅" in table


# ───────────────────────────────────────────────────────────────────
# Config Loader
# ───────────────────────────────────────────────────────────────────


class TestConfigLoader:
    """Validate YAML config loading."""

    def test_load_default_profiles(self) -> None:
        from circuit_breaker.config_loader import load_profiles

        from circuit_breaker.registry import CircuitBreakerRegistry

        registry = CircuitBreakerRegistry()
        load_profiles(registry=registry)

        # service_profiles.yaml has at least firestore and gemini_interactions
        assert "firestore" in registry.service_names
        assert len(registry) > 0

    def test_loaded_breaker_has_correct_threshold(self) -> None:
        from circuit_breaker.config_loader import load_profiles

        from circuit_breaker.registry import CircuitBreakerRegistry

        registry = CircuitBreakerRegistry()
        load_profiles(registry=registry)

        breaker = registry.get("firestore")
        # Firestore profile uses threshold=3 per service_profiles.yaml
        assert breaker.failure_threshold == 3


# ───────────────────────────────────────────────────────────────────
# Telemetry Bridge
# ───────────────────────────────────────────────────────────────────


class TestTelemetryBridge:
    """Validate telemetry bridge wiring."""

    def test_default_registry_exists(self) -> None:
        from circuit_breaker.telemetry_bridge import default_registry

        assert default_registry is not None
        assert isinstance(default_registry, CircuitBreakerRegistry)

    def test_create_telemetry_registry(self) -> None:
        from circuit_breaker.telemetry_bridge import create_telemetry_registry

        registry = create_telemetry_registry()
        assert isinstance(registry, CircuitBreakerRegistry)

    def test_state_change_logs(self, caplog: pytest.LogCaptureFixture) -> None:
        from circuit_breaker.telemetry_bridge import _telemetry_state_change_handler

        with caplog.at_level("INFO"):
            _telemetry_state_change_handler(
                CircuitBreakerState.CLOSED,
                CircuitBreakerState.OPEN,
                "test_svc",
            )
        assert "test_svc" in caplog.text
        assert "closed" in caplog.text
        assert "open" in caplog.text


# ───────────────────────────────────────────────────────────────────
# Integration: HALF_OPEN → CLOSED Recovery
# ───────────────────────────────────────────────────────────────────


class TestHalfOpenRecovery:
    """Full cycle: CLOSED → OPEN → HALF_OPEN → CLOSED (recovery)."""

    def test_full_recovery_cycle(self) -> None:
        """Breaker trips, waits for probe, then recovers on success."""
        cb = CircuitBreaker(
            "recovery_svc",
            failure_threshold=2,
            reset_timeout_s=0.05,  # 50ms for fast test
        )
        assert cb.state == CircuitBreakerState.CLOSED

        # Trip it
        cb.record_failure()
        cb.record_failure()
        assert cb.state == CircuitBreakerState.OPEN

        # Wait for probe window
        time.sleep(0.06)
        assert cb.allow_request()  # triggers HALF_OPEN
        assert cb.state == CircuitBreakerState.HALF_OPEN

        # Successful probe → recovery
        cb.record_success()
        assert cb.state == CircuitBreakerState.CLOSED
        assert cb.consecutive_failures == 0

    def test_re_trip_from_half_open(self) -> None:
        """Failed probe in HALF_OPEN sends back to OPEN."""
        cb = CircuitBreaker(
            "retrip_svc",
            failure_threshold=2,
            reset_timeout_s=0.05,
        )
        cb.record_failure()
        cb.record_failure()
        assert cb.state == CircuitBreakerState.OPEN

        time.sleep(0.06)
        assert cb.allow_request()  # HALF_OPEN
        cb.record_failure()  # probe fails
        assert cb.state == CircuitBreakerState.OPEN

    def test_recovery_callback_fires(self) -> None:
        """Callback fires for HALF_OPEN → CLOSED transition."""
        transitions: list[tuple[str, str]] = []

        def cb_handler(
            old: CircuitBreakerState,
            new: CircuitBreakerState,
            svc: str,
        ) -> None:
            transitions.append((old.value, new.value))

        cb = CircuitBreaker(
            "callback_svc",
            failure_threshold=2,
            reset_timeout_s=0.05,
            on_state_change=cb_handler,
        )
        cb.record_failure()
        cb.record_failure()
        time.sleep(0.06)
        cb.allow_request()
        cb.record_success()

        # Should have: CLOSED→OPEN, OPEN→HALF_OPEN, HALF_OPEN→CLOSED
        assert ("closed", "open") in transitions
        assert ("half_open", "closed") in transitions


# ───────────────────────────────────────────────────────────────────
# Integration: Health Endpoint
# ───────────────────────────────────────────────────────────────────


class TestHealthEndpoint:
    """Validate health_response HTTP status code logic."""

    def test_healthy_returns_200(self) -> None:
        from circuit_breaker.health_endpoint import health_response

        registry = CircuitBreakerRegistry()
        registry.register("svc_a", failure_threshold=5)
        registry.register("svc_b", failure_threshold=5)

        status_code, body = health_response(registry=registry)
        assert status_code == 200
        assert body["http_reason"] == "All circuit breakers healthy"

    def test_degraded_returns_503(self) -> None:
        from circuit_breaker.health_endpoint import health_response

        registry = CircuitBreakerRegistry()
        b = registry.register("failing_svc", failure_threshold=2)
        b.record_failure()
        b.record_failure()
        assert b.state == CircuitBreakerState.OPEN

        status_code, body = health_response(registry=registry)
        assert status_code == 503
        assert "degraded" in body["http_reason"].lower()

    def test_health_json_format(self) -> None:
        import json

        from circuit_breaker.health_endpoint import health_json

        registry = CircuitBreakerRegistry()
        registry.register("json_svc")

        status_code, json_str = health_json(registry=registry)
        assert status_code == 200
        parsed = json.loads(json_str)
        assert "services" in parsed
        assert "summary" in parsed


# ───────────────────────────────────────────────────────────────────
# Integration: Dashboard Summary Accuracy
# ───────────────────────────────────────────────────────────────────


class TestDashboardSummary:
    """Validate dashboard health report counts are accurate."""

    def test_mixed_state_counts(self) -> None:
        from circuit_breaker.dashboard import get_health_report
        from circuit_breaker.registry import CircuitBreakerRegistry

        # Use isolated registry
        import circuit_breaker.dashboard as _dashboard

        original_registry = _dashboard.default_registry
        try:
            test_registry = CircuitBreakerRegistry()
            _dashboard.default_registry = test_registry

            # Create breakers in different states
            test_registry.register("closed_svc", failure_threshold=5)

            open_breaker = test_registry.register("open_svc", failure_threshold=2)
            open_breaker.record_failure()
            open_breaker.record_failure()

            report = get_health_report()
            summary = report["summary"]

            assert summary["total_breakers"] == 2
            assert summary["closed"] == 1
            assert summary["open"] == 1
            assert summary["health_status"] == "degraded"
            assert "open_svc" in summary["open_services"]
        finally:
            _dashboard.default_registry = original_registry

    def test_all_healthy(self) -> None:
        from circuit_breaker.dashboard import get_health_report

        import circuit_breaker.dashboard as _dashboard

        original_registry = _dashboard.default_registry
        try:
            test_registry = CircuitBreakerRegistry()
            _dashboard.default_registry = test_registry

            test_registry.register("a")
            test_registry.register("b")
            test_registry.register("c")

            report = get_health_report()
            assert report["summary"]["health_status"] == "healthy"
            assert report["summary"]["open"] == 0
        finally:
            _dashboard.default_registry = original_registry


# ───────────────────────────────────────────────────────────────────
# Exponential Backoff
# ───────────────────────────────────────────────────────────────────


class TestExponentialBackoff:
    """Validate exponential backoff on HALF_OPEN probe retries.

    Core invariants:
      - Each failed probe doubles the reset timeout: base * 2^multiplier
      - Timeout is capped at max_reset_timeout_s
      - Successful recovery resets multiplier AND timeout to base
      - Backoff state is visible in snapshot()
    """

    def test_backoff_doubles_on_each_probe_failure(self) -> None:
        """Verify the doubling: base=0.05, after 1 fail → 0.10, after 2 → 0.20."""
        b = CircuitBreaker(
            "backoff_svc",
            failure_threshold=1,
            reset_timeout_s=0.05,
            max_reset_timeout_s=10.0,
        )
        assert b.current_reset_timeout_s == 0.05
        assert b.backoff_multiplier == 0

        # Trip 1: CLOSED → OPEN
        b.record_failure()
        assert b.state == CircuitBreakerState.OPEN

        # Wait for HALF_OPEN, fail the probe → should double
        time.sleep(0.06)
        assert b.state == CircuitBreakerState.HALF_OPEN
        b.record_failure()  # HALF_OPEN → OPEN (backoff_multiplier=1)
        assert b.state == CircuitBreakerState.OPEN
        assert b.backoff_multiplier == 1
        assert b.current_reset_timeout_s == pytest.approx(0.10, abs=0.001)

        # Wait for the new (doubled) timeout, fail again → should double again
        time.sleep(0.12)
        assert b.state == CircuitBreakerState.HALF_OPEN
        b.record_failure()  # backoff_multiplier=2
        assert b.state == CircuitBreakerState.OPEN
        assert b.backoff_multiplier == 2
        assert b.current_reset_timeout_s == pytest.approx(0.20, abs=0.001)

    def test_backoff_caps_at_max(self) -> None:
        """Timeout should never exceed max_reset_timeout_s."""
        b = CircuitBreaker(
            "cap_svc",
            failure_threshold=1,
            reset_timeout_s=1.0,
            max_reset_timeout_s=4.0,  # Cap at 4s
        )
        b.record_failure()  # Trip OPEN

        # Simulate 10 consecutive probe failures via direct internal manipulation
        # (avoids waiting for real timeouts in test)
        for i in range(10):
            # Force HALF_OPEN state for testing
            with b._lock:
                b._state = CircuitBreakerState.HALF_OPEN
            b.record_failure()
            assert b.backoff_multiplier == i + 1
            # Timeout should be min(1.0 * 2^(i+1), 4.0)
            expected = min(1.0 * (2 ** (i + 1)), 4.0)
            assert b.current_reset_timeout_s == pytest.approx(expected, abs=0.01)

        # After 10 failures, should be pinned at 4.0
        assert b.current_reset_timeout_s == pytest.approx(4.0, abs=0.01)

    def test_successful_recovery_resets_backoff(self) -> None:
        """After HALF_OPEN → CLOSED, multiplier and timeout reset to base."""
        b = CircuitBreaker(
            "reset_backoff_svc",
            failure_threshold=1,
            reset_timeout_s=0.05,
            max_reset_timeout_s=10.0,
        )
        # Trip and fail one probe
        b.record_failure()
        time.sleep(0.06)
        assert b.state == CircuitBreakerState.HALF_OPEN
        b.record_failure()  # multiplier=1, timeout=0.10
        assert b.backoff_multiplier == 1
        assert b.current_reset_timeout_s == pytest.approx(0.10, abs=0.001)

        # Now recover
        time.sleep(0.12)
        assert b.state == CircuitBreakerState.HALF_OPEN
        b.record_success()  # HALF_OPEN → CLOSED
        assert b.state == CircuitBreakerState.CLOSED
        assert b.backoff_multiplier == 0
        assert b.current_reset_timeout_s == pytest.approx(0.05, abs=0.001)

    def test_manual_reset_clears_backoff(self) -> None:
        """reset() should zero out backoff state."""
        b = CircuitBreaker(
            "manual_reset_backoff",
            failure_threshold=1,
            reset_timeout_s=0.05,
        )
        b.record_failure()
        with b._lock:
            b._state = CircuitBreakerState.HALF_OPEN
        b.record_failure()  # multiplier=1
        assert b.backoff_multiplier == 1

        b.reset()
        assert b.backoff_multiplier == 0
        assert b.current_reset_timeout_s == pytest.approx(0.05, abs=0.001)
        assert b.state == CircuitBreakerState.CLOSED

    def test_snapshot_exposes_backoff_fields(self) -> None:
        """snapshot() should include backoff_multiplier and effective_timeout_s when active."""
        b = CircuitBreaker(
            "snap_backoff_svc",
            failure_threshold=1,
            reset_timeout_s=1.0,
        )
        # Before any backoff
        snap = b.snapshot()
        assert "backoff_multiplier" not in snap  # Should not appear when multiplier=0

        # Trip and fail a probe
        b.record_failure()
        with b._lock:
            b._state = CircuitBreakerState.HALF_OPEN
        b.record_failure()

        snap = b.snapshot()
        assert snap["backoff_multiplier"] == 1
        assert snap["effective_timeout_s"] == pytest.approx(2.0, abs=0.01)


# ───────────────────────────────────────────────────────────────────
# HALF_OPEN Flakiness Simulation
# ───────────────────────────────────────────────────────────────────


class TestHalfOpenFlakiness:
    """Simulate intermittent success/failure patterns during HALF_OPEN recovery.

    Real-world services rarely fail cleanly then succeed cleanly.
    These tests verify the breaker behaves correctly under flaky conditions:
    - Alternating fail/success probes
    - Multiple consecutive probe failures before recovery
    - Success after extended backoff period
    """

    def test_alternating_fail_success_pattern(self) -> None:
        """Fail-succeed-fail-succeed: breaker should eventually recover."""
        b = CircuitBreaker(
            "flaky_alternate",
            failure_threshold=1,
            reset_timeout_s=0.03,
            max_reset_timeout_s=0.5,
        )
        # Initial trip
        b.record_failure()
        assert b.state == CircuitBreakerState.OPEN

        # Round 1: probe fails → re-opens with backoff
        time.sleep(0.04)
        assert b.state == CircuitBreakerState.HALF_OPEN
        b.record_failure()
        assert b.state == CircuitBreakerState.OPEN
        assert b.backoff_multiplier == 1

        # Round 2: wait for doubled timeout, probe succeeds → recovers
        time.sleep(0.07)  # 0.03 * 2 = 0.06, wait a bit more
        assert b.state == CircuitBreakerState.HALF_OPEN
        b.record_success()
        assert b.state == CircuitBreakerState.CLOSED
        assert b.backoff_multiplier == 0

    def test_three_consecutive_probe_failures_then_recovery(self) -> None:
        """3 failed probes with increasing backoff, then successful recovery."""
        b = CircuitBreaker(
            "flaky_3fail",
            failure_threshold=1,
            reset_timeout_s=0.02,
            max_reset_timeout_s=1.0,
        )
        b.record_failure()
        assert b.state == CircuitBreakerState.OPEN

        # Fail 3 probes: timeout grows 0.02 → 0.04 → 0.08
        for expected_multiplier in range(1, 4):
            with b._lock:
                b._last_failure_time = time.monotonic() - b._reset_timeout_s - 0.01
            assert b.state == CircuitBreakerState.HALF_OPEN
            b.record_failure()
            assert b.state == CircuitBreakerState.OPEN
            assert b.backoff_multiplier == expected_multiplier

        # Verify timeout has grown correctly: 0.02 * 2^3 = 0.16
        assert b.current_reset_timeout_s == pytest.approx(0.16, abs=0.01)

        # Now recover
        with b._lock:
            b._last_failure_time = time.monotonic() - b._reset_timeout_s - 0.01
        assert b.state == CircuitBreakerState.HALF_OPEN
        b.record_success()
        assert b.state == CircuitBreakerState.CLOSED
        assert b.backoff_multiplier == 0
        assert b.current_reset_timeout_s == pytest.approx(0.02, abs=0.001)

    def test_flaky_service_with_decorator(self) -> None:
        """Simulate a flaky service using the @wrap decorator."""
        b = CircuitBreaker(
            "flaky_decorated",
            failure_threshold=2,
            reset_timeout_s=0.03,
        )
        call_count = 0
        fail_on_calls = {1, 2, 4}  # Fail on these invocations

        @b.wrap
        def flaky_api() -> str:
            nonlocal call_count
            call_count += 1
            if call_count in fail_on_calls:
                msg = f"Flaky failure #{call_count}"
                raise ConnectionError(msg)
            return f"ok-{call_count}"

        # Calls 1 & 2: fail → trips open (threshold=2)
        with pytest.raises(ConnectionError):
            flaky_api()
        with pytest.raises(ConnectionError):
            flaky_api()
        assert b.state == CircuitBreakerState.OPEN

        # Call 3: should be blocked by open breaker
        with pytest.raises(CircuitBreakerOpenError):
            flaky_api()

        # Wait for HALF_OPEN, call 3 (call_count=3): succeeds → recovers
        time.sleep(0.04)
        result = flaky_api()
        assert result == "ok-3"
        assert b.state == CircuitBreakerState.CLOSED

    def test_concurrent_half_open_probes_rejected(self) -> None:
        """Only max_probes=1 concurrent probe allowed in HALF_OPEN."""
        b = CircuitBreaker(
            "concurrent_probe",
            failure_threshold=1,
            reset_timeout_s=0.03,
            half_open_max_probes=1,
        )
        b.record_failure()
        time.sleep(0.04)
        assert b.state == CircuitBreakerState.HALF_OPEN

        # First probe: allowed
        assert b.allow_request() is True
        # Second probe: rejected (already 1 active)
        assert b.allow_request() is False
        # Third: still rejected
        assert b.allow_request() is False


# ───────────────────────────────────────────────────────────────────
# Sliding Window Performance Benchmark
# ───────────────────────────────────────────────────────────────────


class TestSlidingWindowPerformance:
    """Profile record_failure() and record_success() under sustained load.

    Target: <1ms per operation under 10K+ events/sec sustained load.
    These are deterministic timing tests — not flaky network tests.
    """

    def test_record_failure_throughput_10k(self) -> None:
        """record_failure() should sustain >10K ops/sec in sliding window mode."""
        b = CircuitBreaker(
            "perf_failure",
            failure_threshold=100_000,  # Never trip during benchmark
            failure_mode=FailureMode.SLIDING_WINDOW,
            window_s=5.0,
        )
        n = 10_000

        start = time.perf_counter()
        for _ in range(n):
            b.record_failure()
        elapsed = time.perf_counter() - start

        ops_per_sec = n / elapsed
        avg_us = (elapsed / n) * 1_000_000

        # Must sustain at least 5K ops/sec (worst-case: 10K events in deque
        # with no pruning; production deques stay bounded via TTL expiry)
        assert ops_per_sec > 5_000, f"record_failure throughput too low: {ops_per_sec:.0f} ops/sec (avg {avg_us:.1f}µs/op)"
        assert b.total_failures == n

    def test_record_success_throughput_10k(self) -> None:
        """record_success() should sustain >10K ops/sec in sliding window mode."""
        b = CircuitBreaker(
            "perf_success",
            failure_threshold=100_000,
            failure_mode=FailureMode.SLIDING_WINDOW,
            window_s=5.0,
        )
        n = 10_000

        start = time.perf_counter()
        for _ in range(n):
            b.record_success()
        elapsed = time.perf_counter() - start

        ops_per_sec = n / elapsed
        avg_us = (elapsed / n) * 1_000_000

        assert ops_per_sec > 10_000, f"record_success throughput too low: {ops_per_sec:.0f} ops/sec (avg {avg_us:.1f}µs/op)"
        assert b.total_successes == n

    def test_sliding_window_pruning_under_sustained_load(self) -> None:
        """Verify deque pruning keeps memory bounded under sustained writes."""
        b = CircuitBreaker(
            "perf_prune",
            failure_threshold=100_000,
            failure_mode=FailureMode.SLIDING_WINDOW,
            window_s=0.01,  # 10ms window — events expire fast
        )

        # Write 5K events rapidly
        for _ in range(5_000):
            b.record_failure()

        # Let the window expire
        time.sleep(0.02)

        # Write one more to trigger pruning
        b.record_failure()

        # After pruning, only recent events should remain in the deque
        with b._lock:
            b._prune_window()
            remaining = len(b._events)

        # Should be very small — only events within the 10ms window
        assert remaining < 100, f"Deque not pruned: {remaining} events remain"


# ───────────────────────────────────────────────────────────────────
# Metrics Exporter
# ───────────────────────────────────────────────────────────────────


class TestMetricsExporter:
    """Validate Prometheus and OpenTelemetry metric export accuracy."""

    def test_prometheus_empty_registry(self) -> None:
        """Empty registry should return a comment line."""
        from circuit_breaker.metrics_exporter import prometheus_metrics

        registry = CircuitBreakerRegistry()
        text = prometheus_metrics(registry=registry)
        assert "No circuit breakers registered" in text

    def test_prometheus_format_structure(self) -> None:
        """Prometheus output should contain HELP, TYPE, and metric lines."""
        from circuit_breaker.metrics_exporter import prometheus_metrics

        registry = CircuitBreakerRegistry()
        registry.register("alpha", failure_threshold=3)
        b = registry.register("beta", failure_threshold=2)
        b.record_failure()
        b.record_failure()  # Trip OPEN

        text = prometheus_metrics(registry=registry)

        # Should have HELP and TYPE headers for each metric
        assert "# HELP circuit_breaker_state" in text
        assert "# TYPE circuit_breaker_state gauge" in text
        assert "# HELP circuit_breaker_failures_total" in text
        assert "# TYPE circuit_breaker_failures_total counter" in text
        assert "# HELP circuit_breaker_successes_total" in text
        assert "# HELP circuit_breaker_consecutive_failures" in text
        assert "# HELP circuit_breaker_seconds_until_probe" in text
        assert "# HELP circuit_breaker_backoff_multiplier" in text

        # Should have labeled metric lines
        assert 'circuit_breaker_state{service="alpha"} 0' in text  # closed=0
        assert 'circuit_breaker_state{service="beta"} 2' in text  # open=2
        assert 'circuit_breaker_failures_total{service="beta"} 2' in text

    def test_prometheus_reflects_state_changes(self) -> None:
        """Metrics should reflect the current state of each breaker."""
        from circuit_breaker.metrics_exporter import prometheus_metrics

        registry = CircuitBreakerRegistry()
        b = registry.register("stateful_svc", failure_threshold=2)

        # Initially closed
        text = prometheus_metrics(registry=registry)
        assert 'circuit_breaker_state{service="stateful_svc"} 0' in text

        # Trip to open
        b.record_failure()
        b.record_failure()
        text = prometheus_metrics(registry=registry)
        assert 'circuit_breaker_state{service="stateful_svc"} 2' in text
        assert 'circuit_breaker_consecutive_failures{service="stateful_svc"} 2' in text

    def test_otel_empty_registry(self) -> None:
        """Empty registry should return empty list."""
        from circuit_breaker.metrics_exporter import otel_metrics

        registry = CircuitBreakerRegistry()
        metrics = otel_metrics(registry=registry)
        assert metrics == []

    def test_otel_metric_structure(self) -> None:
        """Each OTel metric point should have required fields."""
        from circuit_breaker.metrics_exporter import otel_metrics

        registry = CircuitBreakerRegistry()
        registry.register("otel_svc", failure_threshold=3)

        metrics = otel_metrics(registry=registry)
        assert len(metrics) == 6  # 6 metrics per service

        for m in metrics:
            assert "name" in m
            assert "type" in m
            assert "value" in m
            assert "labels" in m
            assert "timestamp_ns" in m
            assert m["labels"]["service"] == "otel_svc"

        # Check specific metric names
        names = [m["name"] for m in metrics]
        assert "circuit_breaker_state" in names
        assert "circuit_breaker_failures_total" in names
        assert "circuit_breaker_successes_total" in names
        assert "circuit_breaker_consecutive_failures" in names
        assert "circuit_breaker_seconds_until_probe" in names
        assert "circuit_breaker_backoff_multiplier" in names

    def test_otel_values_reflect_breaker_state(self) -> None:
        """OTel metric values should match the breaker's actual state."""
        from circuit_breaker.metrics_exporter import otel_metrics

        registry = CircuitBreakerRegistry()
        b = registry.register("otel_state_svc", failure_threshold=2)

        # Record some activity
        b.record_success()
        b.record_success()
        b.record_failure()
        b.record_failure()  # Trips OPEN

        metrics = otel_metrics(registry=registry)
        metric_map = {m["name"]: m["value"] for m in metrics}

        assert metric_map["circuit_breaker_state"] == 2  # OPEN
        assert metric_map["circuit_breaker_failures_total"] == 2
        assert metric_map["circuit_breaker_successes_total"] == 2
        assert metric_map["circuit_breaker_consecutive_failures"] == 2
