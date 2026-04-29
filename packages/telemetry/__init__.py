# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""AGNT Telemetry — Structured event catalog for observability.

Ported from: analytics/datadog.ts (34+ tengu_* events)
Reference: AGNT STATE B Spec P3.2

All events are written to .beads/telemetry.jsonl in a structured format
compatible with BigQuery export and Datadog-style dashboarding.
"""

from packages.telemetry.catalog import TelemetryEvent, EventCatalog
from packages.telemetry.sink import TelemetrySink

__all__ = [
    "TelemetryEvent",
    "EventCatalog",
    "TelemetrySink",
]
