# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Circuit Breaker Registry — Per-service breaker management.

Manages a fleet of CircuitBreaker instances, one per service domain.
Provides centralized configuration, health reporting, and telemetry
integration via the existing TelemetrySink pipeline.

Usage:
    registry = CircuitBreakerRegistry()
    registry.register("firestore", failure_threshold=3, reset_timeout_s=60)
    registry.register("gemini_api", failure_threshold=5, reset_timeout_s=120)

    # Get a registered breaker
    breaker = registry.get("firestore")
    if breaker.allow_request():
        ...

    # Health dashboard
    health = registry.health_report()
    # → {"firestore": {"state": "closed", ...}, "gemini_api": {"state": "open", ...}}
"""

from __future__ import annotations

import logging
import threading
from typing import Any

from circuit_breaker.breaker import (
    CircuitBreaker,
    CircuitBreakerState,
    FailureMode,
    StateChangeCallback,
)

logger = logging.getLogger(__name__)


class CircuitBreakerRegistry:
    """Centralized registry for per-service circuit breakers.

    Thread-safe. Supports:
      - Service registration with custom thresholds
      - Global state change callback (e.g., telemetry emission)
      - Health snapshot for dashboards / health endpoints
      - Bulk reset for administrative recovery

    The registry wires each breaker's on_state_change to a global
    handler that emits telemetry events via the EventCatalog.

    Args:
        global_on_state_change: Optional callback applied to ALL breakers.
    """

    def __init__(
        self,
        global_on_state_change: StateChangeCallback | None = None,
    ) -> None:
        self._breakers: dict[str, CircuitBreaker] = {}
        self._global_on_state_change = global_on_state_change
        self._lock = threading.Lock()

    def register(
        self,
        service_name: str,
        failure_threshold: int = 3,
        reset_timeout_s: float = 60.0,
        on_state_change: StateChangeCallback | None = None,
        half_open_max_probes: int = 1,
        failure_mode: FailureMode = FailureMode.CONSECUTIVE,
        window_s: float = 60.0,
    ) -> CircuitBreaker:
        """Register a new circuit breaker for a service.

        If the service is already registered, returns the existing breaker.

        Args:
            service_name: Unique service identifier.
            failure_threshold: Consecutive failures before tripping.
            reset_timeout_s: Seconds in OPEN before probing.
            on_state_change: Per-service callback (in addition to global).
            half_open_max_probes: Max concurrent HALF_OPEN probes.
            failure_mode: CONSECUTIVE or SLIDING_WINDOW.
            window_s: Sliding window duration in seconds.

        Returns:
            The CircuitBreaker instance for this service.
        """
        with self._lock:
            if service_name in self._breakers:
                logger.debug(
                    "Circuit breaker '%s' already registered — returning existing",
                    service_name,
                )
                return self._breakers[service_name]

            def _combined_callback(
                old: CircuitBreakerState,
                new: CircuitBreakerState,
                svc: str,
            ) -> None:
                """Chain per-service and global callbacks."""
                if on_state_change:
                    on_state_change(old, new, svc)
                if self._global_on_state_change:
                    self._global_on_state_change(old, new, svc)

            breaker = CircuitBreaker(
                service_name=service_name,
                failure_threshold=failure_threshold,
                reset_timeout_s=reset_timeout_s,
                on_state_change=_combined_callback,
                half_open_max_probes=half_open_max_probes,
                failure_mode=failure_mode,
                window_s=window_s,
            )
            self._breakers[service_name] = breaker

            logger.info(
                "Circuit breaker registered: '%s' (threshold=%d, timeout=%.1fs, probes=%d, mode=%s)",
                service_name,
                failure_threshold,
                reset_timeout_s,
                half_open_max_probes,
                failure_mode.value,
            )

            return breaker

    def get(self, service_name: str) -> CircuitBreaker:
        """Get a registered circuit breaker.

        Raises KeyError if the service is not registered.
        """
        with self._lock:
            if service_name not in self._breakers:
                msg = f"No circuit breaker registered for '{service_name}'. Registered: {list(self._breakers.keys())}"
                raise KeyError(msg)
            return self._breakers[service_name]

    def get_or_create(
        self,
        service_name: str,
        failure_threshold: int = 3,
        reset_timeout_s: float = 60.0,
    ) -> CircuitBreaker:
        """Get existing breaker or create with defaults.

        Convenience method for callsites that don't want to pre-register.
        """
        with self._lock:
            if service_name in self._breakers:
                return self._breakers[service_name]

        return self.register(
            service_name=service_name,
            failure_threshold=failure_threshold,
            reset_timeout_s=reset_timeout_s,
        )

    def health_report(self) -> dict[str, dict[str, Any]]:
        """Generate a health snapshot of all registered breakers.

        Returns a dict mapping service_name → breaker snapshot.
        Suitable for health endpoints and dashboard rendering.
        """
        with self._lock:
            return {name: breaker.snapshot() for name, breaker in sorted(self._breakers.items())}

    def open_breakers(self) -> list[str]:
        """List service names with OPEN circuit breakers.

        Useful for alerting and quick health checks.
        """
        with self._lock:
            return [name for name, breaker in self._breakers.items() if breaker.state == CircuitBreakerState.OPEN]

    def reset_all(self) -> int:
        """Reset all breakers to CLOSED. Returns count of breakers reset.

        Administrative recovery — use during planned maintenance windows.
        """
        with self._lock:
            count = 0
            for breaker in self._breakers.values():
                if breaker.state != CircuitBreakerState.CLOSED:
                    breaker.reset()
                    count += 1

            if count > 0:
                logger.info("Reset %d circuit breaker(s) to CLOSED", count)
            return count

    @property
    def service_names(self) -> list[str]:
        """List all registered service names."""
        with self._lock:
            return list(self._breakers.keys())

    def __len__(self) -> int:
        return len(self._breakers)

    def __repr__(self) -> str:
        with self._lock:
            states = {name: breaker.state.value for name, breaker in self._breakers.items()}
        return f"CircuitBreakerRegistry({states})"
