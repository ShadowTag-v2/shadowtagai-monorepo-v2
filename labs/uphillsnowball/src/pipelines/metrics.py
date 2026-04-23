# labs/uphillsnowball/src/pipelines/metrics.py
"""Prometheus Metrics Exporter for the Senses Pipeline (Item 18).

Exposes operational metrics via prometheus_client for:
  - FPR/FNR (false positive/negative rates)
  - Mitigation latency
  - Pipeline throughput
  - Worker health
"""

from __future__ import annotations

import logging
from typing import Any

from prometheus_client import (
    Counter,
    Gauge,
    Histogram,
    Info,
    start_http_server,
)

logger = logging.getLogger("Senses-Metrics")

# ── Counters ──────────────────────────────────────────────────
PIPELINE_RUNS_TOTAL = Counter(
    "senses_pipeline_runs_total",
    "Total pipeline executions",
    ["pipeline", "status"],
)

CLAIMS_VALIDATED_TOTAL = Counter(
    "senses_claims_validated_total",
    "Total statistical claims validated",
    ["result"],  # verified, rejected, empty_data
)

WATERMARKS_EMBEDDED_TOTAL = Counter(
    "senses_watermarks_embedded_total",
    "Total ShadowTag DCT watermarks embedded",
)

OCC_CONFLICTS_TOTAL = Counter(
    "senses_occ_conflicts_total",
    "Total OCC version conflicts on SwarmWhiteboard",
)

# ── Histograms ────────────────────────────────────────────────
MITIGATION_LATENCY = Histogram(
    "senses_mitigation_latency_seconds",
    "Latency of threat mitigation operations",
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
)

ACTIVITY_DURATION = Histogram(
    "senses_activity_duration_seconds",
    "Duration of Temporal activity executions",
    ["activity_name"],
    buckets=(0.1, 0.5, 1.0, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0),
)

# ── Gauges ────────────────────────────────────────────────────
ACTIVE_AGENTS = Gauge(
    "senses_active_agents",
    "Number of currently active agents",
)

QUEUE_DEPTH = Gauge(
    "senses_task_queue_depth",
    "Current depth of the Temporal task queue",
)

WORKER_HEALTHY = Gauge(
    "senses_worker_healthy",
    "Worker health status (1=healthy, 0=unhealthy)",
)

# ── Info ──────────────────────────────────────────────────────
BUILD_INFO = Info(
    "senses_build",
    "Build information for the senses pipeline",
)


def init_metrics(port: int = 9090, build_version: str = "dev") -> None:
    """Initialize the Prometheus metrics HTTP server.

    Args:
        port: Port to expose metrics on.
        build_version: Build version string.
    """
    BUILD_INFO.info(
        {
            "version": build_version,
            "component": "senses-pipeline",
            "runtime": "pnkln-omega",
        }
    )
    WORKER_HEALTHY.set(1)
    start_http_server(port)
    logger.info("📊 Prometheus metrics server started on port %d", port)


def record_pipeline_run(pipeline: str, status: str) -> None:
    """Record a pipeline execution."""
    PIPELINE_RUNS_TOTAL.labels(pipeline=pipeline, status=status).inc()


def record_claim_validation(result: str) -> None:
    """Record a statistical claim validation result."""
    CLAIMS_VALIDATED_TOTAL.labels(result=result).inc()


def record_watermark() -> None:
    """Record a ShadowTag watermark embedding."""
    WATERMARKS_EMBEDDED_TOTAL.inc()


def record_occ_conflict() -> None:
    """Record an OCC version conflict."""
    OCC_CONFLICTS_TOTAL.inc()
