# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Thread-safe circuit breaker for external service protection.

Implements the standard CLOSED → OPEN → HALF_OPEN state machine
to prevent cascading failures when downstream services are unhealthy.

Complements resilient_retry — retry handles transient errors,
circuit breaker handles sustained outages.
"""

from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass
from enum import StrEnum
from typing import TypeVar
from collections.abc import Callable

logger = logging.getLogger(__name__)

T = TypeVar("T")


class CircuitState(StrEnum):
    """Circuit breaker states."""

    CLOSED = "closed"  # Normal — requests pass through
    OPEN = "open"  # Tripped — requests fail fast
    HALF_OPEN = "half_open"  # Probing — single request allowed


@dataclass(frozen=True, slots=True)
class CircuitStats:
    """Snapshot of circuit breaker statistics."""

    state: CircuitState
    failure_count: int
    success_count: int
    total_calls: int
    last_failure_time: float | None
    last_success_time: float | None
    trip_count: int


class CircuitOpenError(Exception):
    """Raised when a call is rejected because the circuit is open."""

    def __init__(self, name: str, retry_after_seconds: float) -> None:
        super().__init__(f"Circuit '{name}' is OPEN — retry after {retry_after_seconds:.1f}s")
        self.circuit_name = name
        self.retry_after_seconds = retry_after_seconds


@dataclass
class CircuitBreakerConfig:
    """Configuration for a circuit breaker instance."""

    failure_threshold: int = 5  # Failures before tripping
    success_threshold: int = 2  # Successes in HALF_OPEN to close
    timeout_seconds: float = 60.0  # How long to stay OPEN before HALF_OPEN
    # Optional: only count these exception types as failures
    failure_types: tuple[type[Exception], ...] = (Exception,)


class CircuitBreaker:
    """Thread-safe circuit breaker.

    Usage::

        cb = CircuitBreaker("api-gateway")

        try:
            result = cb.call(lambda: requests.get("https://api.example.com"))
        except CircuitOpenError:
            # Fast-fail — circuit is open
            ...
        except Exception:
            # Actual downstream error
            ...
    """

    def __init__(self, name: str, config: CircuitBreakerConfig | None = None) -> None:
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self._lock = threading.Lock()
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._total_calls = 0
        self._last_failure_time: float | None = None
        self._last_success_time: float | None = None
        self._opened_at: float | None = None
        self._trip_count = 0

    @property
    def state(self) -> CircuitState:
        """Current circuit state (may transition OPEN → HALF_OPEN)."""
        with self._lock:
            self._maybe_transition()
            return self._state

    def stats(self) -> CircuitStats:
        """Return a snapshot of circuit statistics."""
        with self._lock:
            self._maybe_transition()
            return CircuitStats(
                state=self._state,
                failure_count=self._failure_count,
                success_count=self._success_count,
                total_calls=self._total_calls,
                last_failure_time=self._last_failure_time,
                last_success_time=self._last_success_time,
                trip_count=self._trip_count,
            )

    def call(self, fn: Callable[[], T]) -> T:
        """Execute fn through the circuit breaker.

        Raises:
            CircuitOpenError: If the circuit is OPEN.
            Exception: Any exception from fn (also recorded as failure).
        """
        with self._lock:
            self._maybe_transition()
            self._total_calls += 1

            if self._state == CircuitState.OPEN:
                remaining = self._time_until_half_open()
                raise CircuitOpenError(self.name, remaining)

        # Execute outside lock
        try:
            result = fn()
        except Exception as e:
            if isinstance(e, self.config.failure_types):
                self._record_failure()
            raise
        else:
            self._record_success()
            return result

    async def call_async(self, fn: Callable[..., T]) -> T:
        """Async variant of call()."""
        with self._lock:
            self._maybe_transition()
            self._total_calls += 1

            if self._state == CircuitState.OPEN:
                remaining = self._time_until_half_open()
                raise CircuitOpenError(self.name, remaining)

        try:
            result = await fn()
        except Exception as e:
            if isinstance(e, self.config.failure_types):
                self._record_failure()
            raise
        else:
            self._record_success()
            return result

    def reset(self) -> None:
        """Manually reset the circuit to CLOSED."""
        with self._lock:
            self._state = CircuitState.CLOSED
            self._failure_count = 0
            self._success_count = 0
            self._opened_at = None
            logger.info("Circuit '%s' manually reset to CLOSED", self.name)

    def _record_failure(self) -> None:
        with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.monotonic()

            if self._state == CircuitState.HALF_OPEN:
                self._trip(reason="half_open_probe_failed")
            elif self._state == CircuitState.CLOSED and self._failure_count >= self.config.failure_threshold:
                self._trip(reason="threshold_exceeded")

    def _record_success(self) -> None:
        with self._lock:
            self._success_count += 1
            self._last_success_time = time.monotonic()

            if self._state == CircuitState.HALF_OPEN:
                self._success_count_half_open = getattr(self, "_success_count_half_open", 0) + 1
                if self._success_count_half_open >= self.config.success_threshold:
                    self._state = CircuitState.CLOSED
                    self._failure_count = 0
                    self._success_count_half_open = 0
                    self._opened_at = None
                    logger.info(
                        "Circuit '%s' CLOSED after %d successful probes",
                        self.name,
                        self.config.success_threshold,
                    )

    def _trip(self, reason: str) -> None:
        """Must be called with _lock held."""
        self._state = CircuitState.OPEN
        self._opened_at = time.monotonic()
        self._trip_count += 1
        self._success_count_half_open = 0
        logger.warning(
            "Circuit '%s' OPENED (reason=%s, failures=%d, trips=%d)",
            self.name,
            reason,
            self._failure_count,
            self._trip_count,
        )

    def _maybe_transition(self) -> None:
        """Transition OPEN → HALF_OPEN if timeout has elapsed. Lock must be held."""
        if self._state == CircuitState.OPEN and self._opened_at is not None:
            elapsed = time.monotonic() - self._opened_at
            if elapsed >= self.config.timeout_seconds:
                self._state = CircuitState.HALF_OPEN
                self._success_count_half_open = 0
                logger.info(
                    "Circuit '%s' moved to HALF_OPEN after %.1fs",
                    self.name,
                    elapsed,
                )

    def _time_until_half_open(self) -> float:
        """Seconds until the circuit transitions to HALF_OPEN. Lock must be held."""
        if self._opened_at is None:
            return 0.0
        elapsed = time.monotonic() - self._opened_at
        return max(0.0, self.config.timeout_seconds - elapsed)


# ── Module-level registry ──
_breakers: dict[str, CircuitBreaker] = {}
_registry_lock = threading.Lock()


def get_breaker(name: str, config: CircuitBreakerConfig | None = None) -> CircuitBreaker:
    """Get or create a named circuit breaker (singleton per name)."""
    with _registry_lock:
        if name not in _breakers:
            _breakers[name] = CircuitBreaker(name, config)
        return _breakers[name]


def reset_all() -> None:
    """Reset all circuit breakers to CLOSED."""
    with _registry_lock:
        for cb in _breakers.values():
            cb.reset()


def all_stats() -> dict[str, CircuitStats]:
    """Return stats for all registered circuit breakers."""
    with _registry_lock:
        return {name: cb.stats() for name, cb in _breakers.items()}
