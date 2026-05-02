# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Circuit Breaker — Resilient failure management for service calls.

Synthesized from Claude Code v2.1.91 production patterns:
  - autoCompact.ts: consecutiveFailures counter + threshold trip
  - withRetry.ts: exponential backoff + error-type routing
  - sessionIngress.ts: sequential state recovery from conflicts

Adds HALF_OPEN recovery state that CC's advisory-only pattern lacks.

Usage:
    from circuit_breaker import CircuitBreaker, CircuitBreakerRegistry

    # Direct usage
    breaker = CircuitBreaker("firestore", failure_threshold=3, reset_timeout_s=60)
    if breaker.allow_request():
        try:
            result = await api_call()
            breaker.record_success()
        except Exception as e:
            breaker.record_failure()

    # Decorator usage
    @breaker.wrap
    async def api_call():
        return await external_service()

    # Registry for per-service management
    registry = CircuitBreakerRegistry()
    registry.register("firestore", failure_threshold=3, reset_timeout_s=60)
    registry.register("gemini_api", failure_threshold=5, reset_timeout_s=120)
"""

from circuit_breaker.breaker import (
    CircuitBreaker,
    CircuitBreakerOpenError,
    CircuitBreakerState,
    FailureMode,
    StateChangeCallback,
)
from circuit_breaker.registry import CircuitBreakerRegistry

__all__ = [
    "CircuitBreaker",
    "CircuitBreakerOpenError",
    "CircuitBreakerRegistry",
    "CircuitBreakerState",
    "FailureMode",
    "StateChangeCallback",
]
