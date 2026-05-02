# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Circuit Breaker ↔ Telemetry Bridge.

Wires the circuit breaker registry's global state-change callback to the
existing TelemetrySink pipeline via EventCatalog. This is the ONLY module
that couples the circuit_breaker package to the telemetry package —
keeping the breaker itself dependency-free.

Usage:
    from circuit_breaker.telemetry_bridge import create_telemetry_registry

    registry = create_telemetry_registry()
    registry.register("firestore", failure_threshold=3, reset_timeout_s=60)
    # State changes now auto-emit to .beads/telemetry.jsonl
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from circuit_breaker.breaker import CircuitBreakerState
from circuit_breaker.registry import CircuitBreakerRegistry

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


def _telemetry_state_change_handler(
    old_state: CircuitBreakerState,
    new_state: CircuitBreakerState,
    service_name: str,
) -> None:
    """Global callback that emits telemetry events on circuit breaker transitions.

    Only emits for transitions TO open state (matching EventCatalog.circuit_breaker_open).
    All other transitions are logged at INFO level for observability.
    """
    # Always log the transition for structured observability
    logger.info(
        "Circuit breaker '%s' transition: %s → %s",
        service_name,
        old_state.value,
        new_state.value,
    )

    # Only emit telemetry event when breaker OPENS (error condition)
    if new_state == CircuitBreakerState.OPEN:
        try:
            from telemetry.catalog import EventCatalog
            from telemetry.sink import TelemetrySink

            sink = TelemetrySink()

            # Enrich with live breaker snapshot metadata
            failure_count = 0
            try:
                breaker = default_registry.get(service_name)
                snap = breaker.snapshot()
                failure_count = snap.get("consecutive_failures", 0)
            except (KeyError, Exception):
                pass  # Fallback to 0 if breaker not yet accessible

            event = EventCatalog.circuit_breaker_open(
                subsystem=service_name,
                failure_count=failure_count,
            )
            sink.emit(event)
            sink.flush()

            logger.warning(
                "Telemetry emitted: agnt_circuit_breaker_open (subsystem=%s)",
                service_name,
            )
        except ImportError:
            logger.debug(
                "Telemetry package not available — circuit breaker event not emitted"
            )
        except Exception:
            logger.exception(
                "Failed to emit circuit breaker telemetry for '%s'",
                service_name,
            )


def create_telemetry_registry() -> CircuitBreakerRegistry:
    """Create a CircuitBreakerRegistry wired to the telemetry pipeline.

    Returns a registry whose global_on_state_change callback emits
    EventCatalog.circuit_breaker_open events to TelemetrySink.
    """
    return CircuitBreakerRegistry(
        global_on_state_change=_telemetry_state_change_handler,
    )


# Singleton registry for the application — import this to share breakers
# across the sandbox API, TTL worker, and any other consumer.
default_registry = create_telemetry_registry()
