# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Prometheus-compatible metrics export — Phase 4 M5.

Bridges the @telemetry_latency decorator data to Prometheus exposition format.
Provides:
    - sandbox_store_operation_duration_seconds (histogram)
    - sandbox_store_operation_errors_total (counter)
    - sandbox_cache_hits_total / sandbox_cache_misses_total (counters)

Design:
    - In-memory metric accumulation (no external dependency)
    - Thread-safe via atomic operations on simple counters
    - Exposition endpoint returns text/plain Prometheus format
    - Compatible with Cloud Run sidecar scrape config

Usage:
    from apps.counselconduit.api.sandbox.metrics import metrics_registry, render_metrics
    # In FastAPI:
    @app.get("/metrics")
    async def prometheus_metrics():
        return Response(content=render_metrics(), media_type="text/plain")
"""

from __future__ import annotations

import math
import threading
import time
from collections import defaultdict
from typing import Any


class MetricsRegistry:
  """Thread-safe in-memory metrics registry for Prometheus exposition.

  Collects histogram and counter metrics from telemetry decorators
  without requiring prometheus_client library dependency.
  """

  def __init__(self) -> None:
    self._lock = threading.Lock()
    # Histogram: operation → list of duration_ms samples
    self._durations: dict[str, list[float]] = defaultdict(list)
    # Counter: operation → error count
    self._errors: dict[str, int] = defaultdict(int)
    # Counter: operation → total invocations
    self._invocations: dict[str, int] = defaultdict(int)
    # Cache-specific counters
    self._cache_hits: int = 0
    self._cache_misses: int = 0
    self._start_time = time.time()

  def record_latency(
    self, operation: str, duration_ms: float, *, error: bool = False
  ) -> None:
    """Record a single operation latency sample."""
    with self._lock:
      self._durations[operation].append(duration_ms)
      self._invocations[operation] += 1
      if error:
        self._errors[operation] += 1

  def record_cache_hit(self) -> None:
    """Increment cache hit counter."""
    with self._lock:
      self._cache_hits += 1

  def record_cache_miss(self) -> None:
    """Increment cache miss counter."""
    with self._lock:
      self._cache_misses += 1

  def get_summary(self) -> dict[str, Any]:
    """Return structured metrics summary (for JSON API)."""
    with self._lock:
      result: dict[str, Any] = {
        "uptime_seconds": round(time.time() - self._start_time, 1),
        "cache_hits": self._cache_hits,
        "cache_misses": self._cache_misses,
        "operations": {},
      }
      for op in sorted(self._invocations.keys()):
        samples = self._durations.get(op, [])
        result["operations"][op] = {
          "count": self._invocations[op],
          "errors": self._errors.get(op, 0),
          **_compute_percentiles(samples),
        }
      return result

  def render_prometheus(self) -> str:
    """Render metrics in Prometheus text exposition format."""
    with self._lock:
      lines: list[str] = []

      # Uptime gauge
      uptime = round(time.time() - self._start_time, 1)
      lines.append("# HELP sandbox_uptime_seconds Time since metrics registry started")
      lines.append("# TYPE sandbox_uptime_seconds gauge")
      lines.append(f"sandbox_uptime_seconds {uptime}")
      lines.append("")

      # Cache counters
      lines.append("# HELP sandbox_cache_hits_total Total cache hits")
      lines.append("# TYPE sandbox_cache_hits_total counter")
      lines.append(f"sandbox_cache_hits_total {self._cache_hits}")
      lines.append("")

      lines.append("# HELP sandbox_cache_misses_total Total cache misses")
      lines.append("# TYPE sandbox_cache_misses_total counter")
      lines.append(f"sandbox_cache_misses_total {self._cache_misses}")
      lines.append("")

      # Per-operation histograms
      lines.append(
        "# HELP sandbox_store_operation_duration_ms Operation duration in milliseconds"
      )
      lines.append("# TYPE sandbox_store_operation_duration_ms summary")
      for op in sorted(self._invocations.keys()):
        samples = self._durations.get(op, [])
        pcts = _compute_percentiles(samples)
        labels = f'operation="{op}"'
        lines.append(
          f'sandbox_store_operation_duration_ms{{quantile="0.5",{labels}}} {pcts["p50_ms"]}'
        )
        lines.append(
          f'sandbox_store_operation_duration_ms{{quantile="0.95",{labels}}} {pcts["p95_ms"]}'
        )
        lines.append(
          f'sandbox_store_operation_duration_ms{{quantile="0.99",{labels}}} {pcts["p99_ms"]}'
        )
        lines.append(
          f"sandbox_store_operation_duration_ms_count{{{labels}}} {self._invocations[op]}"
        )
        lines.append(
          f"sandbox_store_operation_duration_ms_sum{{{labels}}} {pcts['sum_ms']}"
        )
      lines.append("")

      # Per-operation error counters
      lines.append("# HELP sandbox_store_operation_errors_total Total operation errors")
      lines.append("# TYPE sandbox_store_operation_errors_total counter")
      for op in sorted(self._errors.keys()):
        lines.append(
          f'sandbox_store_operation_errors_total{{operation="{op}"}} {self._errors[op]}'
        )
      lines.append("")

      return "\n".join(lines)

  def reset(self) -> None:
    """Reset all metrics (for testing)."""
    with self._lock:
      self._durations.clear()
      self._errors.clear()
      self._invocations.clear()
      self._cache_hits = 0
      self._cache_misses = 0
      self._start_time = time.time()


def _compute_percentiles(samples: list[float]) -> dict[str, float]:
  """Compute p50, p95, p99, avg, and sum from samples."""
  if not samples:
    return {"p50_ms": 0.0, "p95_ms": 0.0, "p99_ms": 0.0, "avg_ms": 0.0, "sum_ms": 0.0}

  sorted_samples = sorted(samples)
  n = len(sorted_samples)
  return {
    "p50_ms": round(sorted_samples[_pct_idx(n, 50)], 2),
    "p95_ms": round(sorted_samples[_pct_idx(n, 95)], 2),
    "p99_ms": round(sorted_samples[_pct_idx(n, 99)], 2),
    "avg_ms": round(sum(sorted_samples) / n, 2),
    "sum_ms": round(sum(sorted_samples), 2),
  }


def _pct_idx(n: int, pct: int) -> int:
  """Compute index for percentile calculation."""
  return min(max(0, math.ceil(n * pct / 100) - 1), n - 1)


# Global singleton registry
metrics_registry = MetricsRegistry()


def render_metrics() -> str:
  """Convenience function: render Prometheus-format metrics."""
  return metrics_registry.render_prometheus()
