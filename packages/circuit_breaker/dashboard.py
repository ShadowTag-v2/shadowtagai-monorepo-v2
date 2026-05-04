# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Circuit Breaker Dashboard — Health reporting for KAIROS integration.

Provides structured health reports for all registered circuit breakers,
formatted for consumption by the KAIROS daemon heartbeat system and
any HTTP health endpoints.

Usage::

    from circuit_breaker.dashboard import get_health_report, format_health_table

    report = get_health_report()
    print(format_health_table(report))

    # For KAIROS heartbeat integration:
    heartbeat_data["circuit_breakers"] = get_health_report()
"""

from __future__ import annotations

import logging
import time
from typing import Any

from circuit_breaker.telemetry_bridge import default_registry

logger = logging.getLogger(__name__)


def get_health_report() -> dict[str, Any]:
    """Generate a comprehensive health report for all circuit breakers.

    Returns a dict with:
        - ``services``: Per-service breaker snapshots
        - ``summary``: Aggregate health metrics
        - ``timestamp``: Report generation time (epoch)
    """
    snapshots = default_registry.health_report()
    open_breakers = default_registry.open_breakers()

    total = len(snapshots)
    open_count = len(open_breakers)
    closed_count = sum(1 for s in snapshots.values() if s.get("state") == "closed")
    half_open_count = total - open_count - closed_count

    return {
        "services": snapshots,
        "summary": {
            "total_breakers": total,
            "closed": closed_count,
            "open": open_count,
            "half_open": half_open_count,
            "open_services": open_breakers,
            "health_status": "degraded" if open_count > 0 else "healthy",
        },
        "timestamp": time.time(),
    }


def format_health_table(report: dict[str, Any]) -> str:
    """Format a health report as a human-readable ASCII table.

    Suitable for CLI output and log messages.

    Example output::

        ┌──────────────────────┬────────┬───────────┬──────────┐
        │ Service              │ State  │ Failures  │ Probe In │
        ├──────────────────────┼────────┼───────────┼──────────┤
        │ firestore            │ CLOSED │ 0/3       │ —        │
        │ gemini_interactions  │ OPEN   │ 5/5       │ 42.3s    │
        │ gemini_deep_research │ CLOSED │ 1/3       │ —        │
        └──────────────────────┴────────┴───────────┴──────────┘
    """
    services = report.get("services", {})
    if not services:
        return "No circuit breakers registered."

    # Column widths
    name_w = max(len(name) for name in services) + 2
    name_w = max(name_w, 22)

    lines: list[str] = []
    header = f"{'Service':<{name_w}} {'State':<10} {'Failures':<10} {'Probe In':<10}"
    separator = "─" * len(header)

    lines.append(separator)
    lines.append(header)
    lines.append(separator)

    for name, snap in sorted(services.items()):
        state = snap.get("state", "unknown").upper()
        failures = f"{snap.get('consecutive_failures', 0)}/{snap.get('failure_threshold', '?')}"
        probe = f"{snap.get('seconds_until_probe', 0):.1f}s" if snap.get("state") == "open" else "—"

        # Color state for terminals that support ANSI
        if state == "OPEN":
            state_display = f"\033[91m{state}\033[0m"  # Red
        elif state == "HALF_OPEN":
            state_display = f"\033[93m{state}\033[0m"  # Yellow
        else:
            state_display = f"\033[92m{state}\033[0m"  # Green

        lines.append(f"{name:<{name_w}} {state_display:<20} {failures:<10} {probe:<10}")

    lines.append(separator)

    # Summary line
    summary = report.get("summary", {})
    status = summary.get("health_status", "unknown")
    status_icon = "✅" if status == "healthy" else "⚠️"
    lines.append(f"{status_icon} {summary.get('closed', 0)} healthy, {summary.get('open', 0)} open, {summary.get('half_open', 0)} probing")

    return "\n".join(lines)
