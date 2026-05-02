# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Circuit Breaker — Prometheus & OpenTelemetry Metric Exporter.

Exports circuit breaker metrics in two formats:

1. **Prometheus exposition format** — text/plain for ``/metrics`` endpoint
2. **OpenTelemetry-compatible dict** — for OTel SDK collectors

Metrics exported per breaker:
  - ``circuit_breaker_state`` (gauge: 0=closed, 1=half_open, 2=open)
  - ``circuit_breaker_failures_total`` (counter)
  - ``circuit_breaker_successes_total`` (counter)
  - ``circuit_breaker_consecutive_failures`` (gauge)
  - ``circuit_breaker_seconds_until_probe`` (gauge)
  - ``circuit_breaker_backoff_multiplier`` (gauge)

Usage::

    from circuit_breaker.metrics_exporter import prometheus_metrics, otel_metrics

    # Prometheus text format (for /metrics endpoint)
    text = prometheus_metrics()

    # OpenTelemetry dict format (for OTel SDK)
    metrics = otel_metrics()
"""

from __future__ import annotations

import logging
import time
from typing import Any

logger = logging.getLogger(__name__)

# State encoding for Prometheus gauge
_STATE_VALUES = {
    "closed": 0,
    "half_open": 1,
    "open": 2,
}


def _get_snapshots(registry: Any | None = None) -> dict[str, dict[str, Any]]:
    """Get breaker snapshots from registry."""
    if registry is None:
        from circuit_breaker.telemetry_bridge import default_registry

        registry = default_registry
    return registry.health_report()


def prometheus_metrics(registry: Any | None = None) -> str:
    """Generate Prometheus exposition format text.

    Returns metrics in the standard text format consumable by
    Prometheus scrapers and compatible collectors.

    Args:
        registry: CircuitBreakerRegistry to export. Defaults to
            the global ``default_registry``.

    Returns:
        Prometheus text exposition format string.
    """
    snapshots = _get_snapshots(registry)

    if not snapshots:
        return "# No circuit breakers registered\n"

    lines: list[str] = []
    timestamp_ms = int(time.time() * 1000)

    # --- State gauge ---
    lines.append("# HELP circuit_breaker_state Current state of the circuit breaker (0=closed, 1=half_open, 2=open)")
    lines.append("# TYPE circuit_breaker_state gauge")
    for name, snap in sorted(snapshots.items()):
        state_val = _STATE_VALUES.get(snap.get("state", "closed"), 0)
        lines.append(f'circuit_breaker_state{{service="{name}"}} {state_val} {timestamp_ms}')

    # --- Failures total ---
    lines.append("# HELP circuit_breaker_failures_total Total failures recorded by the circuit breaker")
    lines.append("# TYPE circuit_breaker_failures_total counter")
    for name, snap in sorted(snapshots.items()):
        lines.append(f'circuit_breaker_failures_total{{service="{name}"}} {snap.get("total_failures", 0)} {timestamp_ms}')

    # --- Successes total ---
    lines.append("# HELP circuit_breaker_successes_total Total successes recorded by the circuit breaker")
    lines.append("# TYPE circuit_breaker_successes_total counter")
    for name, snap in sorted(snapshots.items()):
        lines.append(f'circuit_breaker_successes_total{{service="{name}"}} {snap.get("total_successes", 0)} {timestamp_ms}')

    # --- Consecutive failures gauge ---
    lines.append("# HELP circuit_breaker_consecutive_failures Current consecutive failure count")
    lines.append("# TYPE circuit_breaker_consecutive_failures gauge")
    for name, snap in sorted(snapshots.items()):
        lines.append(f'circuit_breaker_consecutive_failures{{service="{name}"}} {snap.get("consecutive_failures", 0)} {timestamp_ms}')

    # --- Seconds until probe ---
    lines.append("# HELP circuit_breaker_seconds_until_probe Seconds remaining until HALF_OPEN probe (0 if not OPEN)")
    lines.append("# TYPE circuit_breaker_seconds_until_probe gauge")
    for name, snap in sorted(snapshots.items()):
        lines.append(f'circuit_breaker_seconds_until_probe{{service="{name}"}} {snap.get("seconds_until_probe", 0):.1f} {timestamp_ms}')

    # --- Backoff multiplier ---
    lines.append("# HELP circuit_breaker_backoff_multiplier Exponential backoff multiplier for HALF_OPEN retries")
    lines.append("# TYPE circuit_breaker_backoff_multiplier gauge")
    for name, snap in sorted(snapshots.items()):
        lines.append(f'circuit_breaker_backoff_multiplier{{service="{name}"}} {snap.get("backoff_multiplier", 0)} {timestamp_ms}')

    lines.append("")  # trailing newline
    return "\n".join(lines)


def otel_metrics(registry: Any | None = None) -> list[dict[str, Any]]:
    """Generate OpenTelemetry-compatible metric dicts.

    Returns a list of metric point dicts suitable for consumption by
    OpenTelemetry SDK exporters or custom collectors.

    Args:
        registry: CircuitBreakerRegistry to export. Defaults to
            the global ``default_registry``.

    Returns:
        List of metric point dictionaries.
    """
    snapshots = _get_snapshots(registry)

    if not snapshots:
        return []

    now_ns = int(time.time() * 1e9)
    metrics: list[dict[str, Any]] = []

    for name, snap in sorted(snapshots.items()):
        labels = {"service": name}
        state_val = _STATE_VALUES.get(snap.get("state", "closed"), 0)

        metrics.extend([
            {
                "name": "circuit_breaker_state",
                "type": "gauge",
                "value": state_val,
                "labels": labels,
                "timestamp_ns": now_ns,
                "description": "Circuit breaker state (0=closed, 1=half_open, 2=open)",
            },
            {
                "name": "circuit_breaker_failures_total",
                "type": "counter",
                "value": snap.get("total_failures", 0),
                "labels": labels,
                "timestamp_ns": now_ns,
            },
            {
                "name": "circuit_breaker_successes_total",
                "type": "counter",
                "value": snap.get("total_successes", 0),
                "labels": labels,
                "timestamp_ns": now_ns,
            },
            {
                "name": "circuit_breaker_consecutive_failures",
                "type": "gauge",
                "value": snap.get("consecutive_failures", 0),
                "labels": labels,
                "timestamp_ns": now_ns,
            },
            {
                "name": "circuit_breaker_seconds_until_probe",
                "type": "gauge",
                "value": snap.get("seconds_until_probe", 0),
                "labels": labels,
                "timestamp_ns": now_ns,
            },
            {
                "name": "circuit_breaker_backoff_multiplier",
                "type": "gauge",
                "value": snap.get("backoff_multiplier", 0),
                "labels": labels,
                "timestamp_ns": now_ns,
            },
        ])

    return metrics
