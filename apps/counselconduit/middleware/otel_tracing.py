# apps/counselconduit/middleware/otel_tracing.py
"""OpenTelemetry tracing middleware for sandbox quota enforcement.

Adds distributed tracing spans for:
- Sandbox quota checks
- Request routing decisions
- GDPR endpoint operations
- LLM model invocations
"""

from __future__ import annotations

import logging
import os
import time
from typing import Any

logger = logging.getLogger("counselconduit.otel")

# Only import opentelemetry if available (optional dependency)
_OTEL_AVAILABLE = False
try:
    from opentelemetry import trace  # noqa: F401
    from opentelemetry.trace import StatusCode  # noqa: F401  # vulture: interface contract

    _OTEL_AVAILABLE = True
except ImportError:
    logger.info("OpenTelemetry not installed — tracing disabled")


_TRACER_NAME = "counselconduit.sandbox"
_SERVICE_NAME = os.getenv("OTEL_SERVICE_NAME", "counselconduit")


def get_tracer() -> Any:
    """Get the OpenTelemetry tracer, or a no-op stub."""
    if _OTEL_AVAILABLE:
        return trace.get_tracer(_TRACER_NAME)
    return _NoOpTracer()


class _NoOpSpan:
    """No-op span for when OTel is not installed."""

    def __enter__(self) -> _NoOpSpan:
        return self

    def __exit__(self, *_args: Any) -> None:  # vulture: interface contract
        pass

    def set_attribute(self, key: str, value: Any) -> None:
        pass

    def set_status(self, status: Any, description: str = "") -> None:
        pass

    def add_event(self, name: str, _attributes: dict[str, Any] | None = None) -> None:  # vulture: OTel interface
        pass

    def record_exception(self, exc: Exception) -> None:
        pass


class _NoOpTracer:
    """No-op tracer for when OTel is not installed."""

    def start_as_current_span(self, name: str, **_kwargs: Any) -> _NoOpSpan:  # vulture: OTel interface
        return _NoOpSpan()


def trace_sandbox_quota_check(firm_id: str, tier: str, current_usage: int, limit: int) -> dict[str, Any]:
    """Trace a sandbox quota enforcement check."""
    tracer = get_tracer()
    with tracer.start_as_current_span("sandbox.quota_check") as span:
        span.set_attribute("firm.id", firm_id)
        span.set_attribute("firm.tier", tier)
        span.set_attribute("quota.current_usage", current_usage)
        span.set_attribute("quota.limit", limit)
        span.set_attribute("quota.remaining", max(0, limit - current_usage))

        allowed = current_usage < limit
        span.set_attribute("quota.allowed", allowed)

        if not allowed:
            span.add_event(
                "quota_exceeded",
                {"firm_id": firm_id, "usage": current_usage, "limit": limit},
            )

        return {"allowed": allowed, "remaining": max(0, limit - current_usage)}


def trace_gdpr_operation(operation: str, firm_id: str, attorney_id: str = "") -> dict[str, Any]:
    """Trace a GDPR endpoint operation."""
    tracer = get_tracer()
    start = time.monotonic()
    with tracer.start_as_current_span(f"gdpr.{operation}") as span:
        span.set_attribute("gdpr.operation", operation)
        span.set_attribute("firm.id", firm_id)
        if attorney_id:
            span.set_attribute("attorney.id", attorney_id)
        span.set_attribute("service.name", _SERVICE_NAME)

    duration_ms = (time.monotonic() - start) * 1000
    return {"operation": operation, "duration_ms": round(duration_ms, 2)}


def trace_model_invocation(model_name: str, firm_id: str, input_tokens: int, output_tokens: int) -> dict[str, Any]:
    """Trace an LLM model invocation for billing and monitoring."""
    tracer = get_tracer()
    with tracer.start_as_current_span("llm.invoke") as span:
        span.set_attribute("llm.model", model_name)
        span.set_attribute("firm.id", firm_id)
        span.set_attribute("llm.input_tokens", input_tokens)
        span.set_attribute("llm.output_tokens", output_tokens)
        span.set_attribute("llm.total_tokens", input_tokens + output_tokens)

    return {
        "model": model_name,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
    }


def trace_dispatch_routing(
    firm_id: str,
    tier: str,
    model: str,
    session_pinned: bool,
    latency_ms: float,
    query_length: int,
) -> dict[str, Any]:
    """Trace a NadirClaw dispatch routing decision.

    Item #14: Adds spans for every routing decision so they show up
    in Cloud Trace for latency analysis and debugging.
    """
    tracer = get_tracer()
    with tracer.start_as_current_span("dispatch.route") as span:
        span.set_attribute("dispatch.firm_id", firm_id)
        span.set_attribute("dispatch.tier", tier)
        span.set_attribute("dispatch.model", model)
        span.set_attribute("dispatch.session_pinned", session_pinned)
        span.set_attribute("dispatch.latency_ms", latency_ms)
        span.set_attribute("dispatch.query_length", query_length)
        span.set_attribute("service.name", _SERVICE_NAME)

    return {
        "firm_id": firm_id,
        "tier": tier,
        "model": model,
        "latency_ms": round(latency_ms, 2),
    }


def trace_judge6_evaluation(
    risk_score: int,
    risk_level: str,
    approved: bool,
    flags_count: int,
    pipeline_ms: int,
) -> dict[str, Any]:
    """Trace a Judge 6 governance evaluation."""
    tracer = get_tracer()
    with tracer.start_as_current_span("judge6.evaluate") as span:
        span.set_attribute("judge6.risk_score", risk_score)
        span.set_attribute("judge6.risk_level", risk_level)
        span.set_attribute("judge6.approved", approved)
        span.set_attribute("judge6.flags_count", flags_count)
        span.set_attribute("judge6.pipeline_ms", pipeline_ms)

        if not approved:
            span.add_event(
                "judge6_blocked",
                {"risk_score": risk_score, "risk_level": risk_level},
            )

    return {
        "risk_score": risk_score,
        "approved": approved,
        "pipeline_ms": pipeline_ms,
    }
