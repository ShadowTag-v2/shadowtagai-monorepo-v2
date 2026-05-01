# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Circuit Breaker — Core state machine.

Implements the three-state circuit breaker pattern:

    CLOSED (normal) ──failure threshold──▶ OPEN (fail-fast)
         ▲                                      │
         │                              reset timeout
         │                                      │
         │                                      ▼
         └──────── probe success ◀──── HALF_OPEN (probe)
                                          │
                                          └── probe failure ──▶ OPEN

Design decisions:
  - Thread-safe via threading.Lock (not asyncio.Lock) for broad compatibility
  - Pure Python — no SDK dependencies — portable across all service domains
  - Advisory mode (caller checks allow_request) AND mandatory mode (wrap decorator)
  - onStateChange callback for telemetry/observability integration
  - Configurable per-service failure_threshold and reset_timeout_s
  - Exponential backoff not embedded here — that belongs in the retry loop
    that WRAPS the breaker (separation of concerns)

Reference patterns:
  - autoCompact.ts L257-265: Circuit breaker check before operation
  - autoCompact.ts L334-349: Failure counting + trip logging
  - withRetry.ts L52-54: MAX_529_RETRIES = 3 threshold
"""

from __future__ import annotations

import inspect
import logging
import threading
import time
from collections.abc import Callable
from enum import StrEnum
from functools import wraps
from typing import Any, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")

# Type alias for state change callbacks
StateChangeCallback = Callable[["CircuitBreakerState", "CircuitBreakerState", str], None]


class CircuitBreakerState(StrEnum):
    """Circuit breaker state machine states."""

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreakerOpenError(Exception):
    """Raised when a request is rejected by an open circuit breaker.

    Callers should catch this to implement fail-fast behavior without
    wasting resources on doomed requests.

    Attributes:
        service_name: The service whose breaker is open.
        failure_count: Number of consecutive failures that tripped the breaker.
        seconds_until_probe: Seconds remaining until HALF_OPEN probe.
    """

    def __init__(
        self,
        service_name: str,
        failure_count: int,
        seconds_until_probe: float,
    ) -> None:
        self.service_name = service_name
        self.failure_count = failure_count
        self.seconds_until_probe = seconds_until_probe
        super().__init__(f"Circuit breaker OPEN for '{service_name}' (failures={failure_count}, probe in {seconds_until_probe:.1f}s)")


class CircuitBreaker:
    """Stateful circuit breaker for protecting service calls.

    Tracks consecutive failures per-service and transitions through
    CLOSED → OPEN → HALF_OPEN → CLOSED states to prevent wasting
    resources on doomed API calls during capacity outages.

    Derived from autoCompact.ts circuit breaker (Claude Code v2.1.91):
      - BQ 2026-03-10: 1,279 sessions had 50+ consecutive failures
        wasting ~250K API calls/day globally.
      - MAX_CONSECUTIVE_AUTOCOMPACT_FAILURES = 3

    Enhanced with HALF_OPEN probing (missing from CC's advisory-only breaker).

    Args:
        service_name: Identifier for the protected service.
        failure_threshold: Consecutive failures before opening circuit.
        reset_timeout_s: Seconds to wait in OPEN before probing (HALF_OPEN).
        on_state_change: Optional callback(old_state, new_state, service_name).
        half_open_max_probes: Max concurrent probes in HALF_OPEN state.

    Example:
        breaker = CircuitBreaker("firestore", failure_threshold=3, reset_timeout_s=60)

        # Advisory mode
        if breaker.allow_request():
            try:
                result = do_work()
                breaker.record_success()
            except ServiceError:
                breaker.record_failure()

        # Mandatory mode (raises CircuitBreakerOpenError)
        @breaker.wrap
        async def do_work():
            return await api_call()
    """

    def __init__(
        self,
        service_name: str,
        failure_threshold: int = 3,
        reset_timeout_s: float = 60.0,
        on_state_change: StateChangeCallback | None = None,
        half_open_max_probes: int = 1,
    ) -> None:
        self._service_name = service_name
        self._failure_threshold = failure_threshold
        self._reset_timeout_s = reset_timeout_s
        self._on_state_change = on_state_change
        self._half_open_max_probes = half_open_max_probes

        self._state = CircuitBreakerState.CLOSED
        self._consecutive_failures: int = 0
        self._total_failures: int = 0
        self._total_successes: int = 0
        self._last_failure_time: float = 0.0
        self._last_state_change_time: float = time.monotonic()
        self._active_half_open_probes: int = 0

        self._lock = threading.Lock()

    # --- Read-only properties ---

    @property
    def service_name(self) -> str:
        """Service identifier this breaker protects."""
        return self._service_name

    @property
    def state(self) -> CircuitBreakerState:
        """Current state of the circuit breaker."""
        with self._lock:
            self._maybe_transition_to_half_open()
            return self._state

    @property
    def consecutive_failures(self) -> int:
        """Current consecutive failure count."""
        return self._consecutive_failures

    @property
    def total_failures(self) -> int:
        """Total lifetime failures recorded."""
        return self._total_failures

    @property
    def total_successes(self) -> int:
        """Total lifetime successes recorded."""
        return self._total_successes

    @property
    def failure_threshold(self) -> int:
        """Failures before tripping open."""
        return self._failure_threshold

    @property
    def seconds_until_probe(self) -> float:
        """Seconds remaining until OPEN → HALF_OPEN transition.

        Returns 0 if not in OPEN state or already eligible.
        """
        with self._lock:
            if self._state != CircuitBreakerState.OPEN:
                return 0.0
            elapsed = time.monotonic() - self._last_failure_time
            remaining = self._reset_timeout_s - elapsed
            return max(0.0, remaining)

    # --- Core API ---

    def allow_request(self) -> bool:
        """Check if a request should be attempted (advisory mode).

        Returns True if:
          - CLOSED: Always allows
          - HALF_OPEN: Allows up to half_open_max_probes concurrent probes
          - OPEN: Rejects (returns False) — check seconds_until_probe

        This is the advisory equivalent of autoCompact.ts L260-264:
            if (tracking?.consecutiveFailures >= MAX_CONSECUTIVE_AUTOCOMPACT_FAILURES) {
                return { wasCompacted: false }
            }
        """
        with self._lock:
            self._maybe_transition_to_half_open()

            if self._state == CircuitBreakerState.CLOSED:
                return True

            if self._state == CircuitBreakerState.HALF_OPEN:
                if self._active_half_open_probes < self._half_open_max_probes:
                    self._active_half_open_probes += 1
                    return True
                return False

            # OPEN
            return False

    def record_success(self) -> None:
        """Record a successful operation.

        Mirrors autoCompact.ts L332: `consecutiveFailures: 0`
        on compaction success.

        Transitions:
          - HALF_OPEN → CLOSED (probe succeeded, circuit recovers)
          - CLOSED → CLOSED (no-op, reset counter)
        """
        with self._lock:
            old_state = self._state
            self._consecutive_failures = 0
            self._total_successes += 1

            if old_state == CircuitBreakerState.HALF_OPEN:
                self._active_half_open_probes = max(0, self._active_half_open_probes - 1)
                self._transition_to(CircuitBreakerState.CLOSED)
                logger.info(
                    "Circuit breaker '%s' recovered: HALF_OPEN → CLOSED (total_successes=%d)",
                    self._service_name,
                    self._total_successes,
                )

    def record_failure(self) -> None:
        """Record a failed operation.

        Mirrors autoCompact.ts L341-348:
            const prevFailures = tracking?.consecutiveFailures ?? 0
            const nextFailures = prevFailures + 1
            if (nextFailures >= MAX_CONSECUTIVE_AUTOCOMPACT_FAILURES) {
                logForDebugging('autocompact: circuit breaker tripped...')
            }

        Transitions:
          - CLOSED → OPEN (threshold reached)
          - HALF_OPEN → OPEN (probe failed, re-open)
        """
        with self._lock:
            old_state = self._state
            self._consecutive_failures += 1
            self._total_failures += 1
            self._last_failure_time = time.monotonic()

            if old_state == CircuitBreakerState.HALF_OPEN:
                self._active_half_open_probes = max(0, self._active_half_open_probes - 1)
                self._transition_to(CircuitBreakerState.OPEN)
                logger.warning(
                    "Circuit breaker '%s' probe failed: HALF_OPEN → OPEN (consecutive_failures=%d)",
                    self._service_name,
                    self._consecutive_failures,
                )
            elif old_state == CircuitBreakerState.CLOSED and self._consecutive_failures >= self._failure_threshold:
                self._transition_to(CircuitBreakerState.OPEN)
                logger.warning(
                    "Circuit breaker '%s' tripped after %d consecutive failures — skipping future attempts for %.1fs",
                    self._service_name,
                    self._consecutive_failures,
                    self._reset_timeout_s,
                )

    def reset(self) -> None:
        """Manually reset the circuit breaker to CLOSED.

        Use for administrative recovery or test setup.
        """
        with self._lock:
            self._consecutive_failures = 0
            self._active_half_open_probes = 0
            if self._state != CircuitBreakerState.CLOSED:
                self._transition_to(CircuitBreakerState.CLOSED)
                logger.info(
                    "Circuit breaker '%s' manually reset to CLOSED",
                    self._service_name,
                )

    # --- Decorator mode ---

    def wrap(self, fn: Callable[..., Any]) -> Callable[..., Any]:
        """Decorator to protect a function with this circuit breaker.

        Raises CircuitBreakerOpenError if the circuit is open.
        Records success/failure automatically.

        Works with both sync and async functions.

        Example:
            @breaker.wrap
            async def call_firestore():
                return await db.get_document(...)
        """

        @wraps(fn)
        async def _async_wrapper(*args: Any, **kwargs: Any) -> Any:
            if not self.allow_request():
                raise CircuitBreakerOpenError(
                    self._service_name,
                    self._consecutive_failures,
                    self.seconds_until_probe,
                )
            try:
                result = await fn(*args, **kwargs)
                self.record_success()
                return result
            except CircuitBreakerOpenError:
                raise
            except Exception:
                self.record_failure()
                raise

        @wraps(fn)
        def _sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            if not self.allow_request():
                raise CircuitBreakerOpenError(
                    self._service_name,
                    self._consecutive_failures,
                    self.seconds_until_probe,
                )
            try:
                result = fn(*args, **kwargs)
                self.record_success()
                return result
            except CircuitBreakerOpenError:
                raise
            except Exception:
                self.record_failure()
                raise

        if inspect.iscoroutinefunction(fn):
            return _async_wrapper
        return _sync_wrapper

    # --- Diagnostics ---

    def snapshot(self) -> dict[str, Any]:
        """Return a serializable snapshot of breaker state.

        Useful for health endpoints and telemetry emission.
        """
        with self._lock:
            self._maybe_transition_to_half_open()
            return {
                "service_name": self._service_name,
                "state": self._state.value,
                "consecutive_failures": self._consecutive_failures,
                "total_failures": self._total_failures,
                "total_successes": self._total_successes,
                "failure_threshold": self._failure_threshold,
                "reset_timeout_s": self._reset_timeout_s,
                "seconds_until_probe": max(
                    0.0,
                    self._reset_timeout_s - (time.monotonic() - self._last_failure_time),
                )
                if self._state == CircuitBreakerState.OPEN
                else 0.0,
            }

    # --- Internal state machine ---

    def _maybe_transition_to_half_open(self) -> None:
        """Check if OPEN → HALF_OPEN transition is due.

        Called under lock. Checks if reset_timeout_s has elapsed since
        the last failure. This is the recovery mechanism that autoCompact.ts
        LACKS — it never re-enables after tripping. We fix that here.
        """
        if self._state != CircuitBreakerState.OPEN:
            return

        elapsed = time.monotonic() - self._last_failure_time
        if elapsed >= self._reset_timeout_s:
            self._transition_to(CircuitBreakerState.HALF_OPEN)
            logger.info(
                "Circuit breaker '%s' cooldown elapsed (%.1fs): OPEN → HALF_OPEN",
                self._service_name,
                elapsed,
            )

    def _transition_to(self, new_state: CircuitBreakerState) -> None:
        """Execute a state transition. Called under lock."""
        old_state = self._state
        if old_state == new_state:
            return

        self._state = new_state
        self._last_state_change_time = time.monotonic()

        if self._on_state_change:
            try:
                self._on_state_change(old_state, new_state, self._service_name)
            except Exception:
                logger.exception(
                    "on_state_change callback failed for '%s'",
                    self._service_name,
                )

    def __repr__(self) -> str:
        return (
            f"CircuitBreaker("
            f"service='{self._service_name}', "
            f"state={self._state.value}, "
            f"failures={self._consecutive_failures}/{self._failure_threshold})"
        )
