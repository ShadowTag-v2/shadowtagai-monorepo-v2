# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Benchmark: Circuit Breaker allow_request() hot path.

Profiles throughput and latency of allow_request() under three scenarios:
  1. Single-threaded (baseline throughput)
  2. Multi-threaded contention (lock contention overhead)
  3. Sliding window mode (deque pruning overhead)

Run:
    python -m packages.circuit_breaker.benchmarks.bench_allow_request
    # or directly:
    python packages/circuit_breaker/.benchmarks/bench_allow_request.py

Outputs: ops/sec, p50/p95/p99 latency in microseconds.
"""

from __future__ import annotations

import statistics
import sys
import threading
import time
from pathlib import Path

# Ensure the packages dir is importable
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "packages"))

from circuit_breaker.breaker import (
  CircuitBreaker,
  CircuitBreakerState,
  FailureMode,
)


# ───────────────────────────────────────────────────────────────────
# Config
# ───────────────────────────────────────────────────────────────────

ITERATIONS = 100_000
THREADS = 8
WARMUP = 1_000


def _percentile(data: list[float], p: float) -> float:
  """Compute the p-th percentile of a sorted list."""
  k = (len(data) - 1) * p / 100.0
  f = int(k)
  c = f + 1
  if c >= len(data):
    return data[f]
  return data[f] + (data[c] - data[f]) * (k - f)


# ───────────────────────────────────────────────────────────────────
# Bench: Single-threaded baseline
# ───────────────────────────────────────────────────────────────────


def bench_single_thread_closed() -> dict[str, float]:
  """Benchmark allow_request() in CLOSED state (fast path)."""
  breaker = CircuitBreaker("bench_closed", failure_threshold=100)

  # Warmup
  for _ in range(WARMUP):
    breaker.allow_request()

  latencies: list[float] = []
  start = time.perf_counter()
  for _ in range(ITERATIONS):
    t0 = time.perf_counter_ns()
    breaker.allow_request()
    latencies.append(time.perf_counter_ns() - t0)
  elapsed = time.perf_counter() - start

  latencies.sort()
  return {
    "scenario": "single_thread_closed",
    "ops_per_sec": ITERATIONS / elapsed,
    "total_s": elapsed,
    "p50_us": _percentile(latencies, 50) / 1000,
    "p95_us": _percentile(latencies, 95) / 1000,
    "p99_us": _percentile(latencies, 99) / 1000,
    "mean_us": statistics.mean(latencies) / 1000,
  }


def bench_single_thread_open() -> dict[str, float]:
  """Benchmark allow_request() in OPEN state (reject path)."""
  breaker = CircuitBreaker("bench_open", failure_threshold=1, reset_timeout_s=3600)
  breaker.record_failure()  # Trip it
  assert breaker.state == CircuitBreakerState.OPEN

  latencies: list[float] = []
  start = time.perf_counter()
  for _ in range(ITERATIONS):
    t0 = time.perf_counter_ns()
    breaker.allow_request()
    latencies.append(time.perf_counter_ns() - t0)
  elapsed = time.perf_counter() - start

  latencies.sort()
  return {
    "scenario": "single_thread_open",
    "ops_per_sec": ITERATIONS / elapsed,
    "total_s": elapsed,
    "p50_us": _percentile(latencies, 50) / 1000,
    "p95_us": _percentile(latencies, 95) / 1000,
    "p99_us": _percentile(latencies, 99) / 1000,
    "mean_us": statistics.mean(latencies) / 1000,
  }


# ───────────────────────────────────────────────────────────────────
# Bench: Multi-threaded contention
# ───────────────────────────────────────────────────────────────────


def bench_multi_thread_contention() -> dict[str, float]:
  """Benchmark allow_request() under heavy thread contention."""
  breaker = CircuitBreaker("bench_contention", failure_threshold=100)
  per_thread = ITERATIONS // THREADS
  barrier = threading.Barrier(THREADS)

  def worker() -> None:
    barrier.wait()
    for _ in range(per_thread):
      breaker.allow_request()

  start = time.perf_counter()
  threads = [threading.Thread(target=worker) for _ in range(THREADS)]
  for t in threads:
    t.start()
  for t in threads:
    t.join()
  elapsed = time.perf_counter() - start

  total_ops = per_thread * THREADS
  return {
    "scenario": f"multi_thread_{THREADS}t_closed",
    "ops_per_sec": total_ops / elapsed,
    "total_s": elapsed,
    "total_ops": total_ops,
  }


# ───────────────────────────────────────────────────────────────────
# Bench: Sliding window mode
# ───────────────────────────────────────────────────────────────────


def bench_sliding_window_allow() -> dict[str, float]:
  """Benchmark allow_request() in SLIDING_WINDOW mode with populated window."""
  breaker = CircuitBreaker(
    "bench_sliding",
    failure_threshold=100,
    failure_mode=FailureMode.SLIDING_WINDOW,
    window_s=60.0,
  )
  # Pre-populate the window with mixed events
  for i in range(50):
    if i % 3 == 0:
      breaker.record_failure()
    else:
      breaker.record_success()

  latencies: list[float] = []
  start = time.perf_counter()
  for _ in range(ITERATIONS):
    t0 = time.perf_counter_ns()
    breaker.allow_request()
    latencies.append(time.perf_counter_ns() - t0)
  elapsed = time.perf_counter() - start

  latencies.sort()
  return {
    "scenario": "sliding_window_allow",
    "ops_per_sec": ITERATIONS / elapsed,
    "total_s": elapsed,
    "p50_us": _percentile(latencies, 50) / 1000,
    "p95_us": _percentile(latencies, 95) / 1000,
    "p99_us": _percentile(latencies, 99) / 1000,
    "mean_us": statistics.mean(latencies) / 1000,
  }


def bench_sliding_window_record_failure() -> dict[str, float]:
  """Benchmark record_failure() in SLIDING_WINDOW mode (hot write path)."""
  breaker = CircuitBreaker(
    "bench_sliding_fail",
    failure_threshold=1_000_000,  # Never trip
    failure_mode=FailureMode.SLIDING_WINDOW,
    window_s=0.01,  # 10ms window → aggressive pruning
  )

  latencies: list[float] = []
  start = time.perf_counter()
  for _ in range(ITERATIONS):
    t0 = time.perf_counter_ns()
    breaker.record_failure()
    latencies.append(time.perf_counter_ns() - t0)
  elapsed = time.perf_counter() - start

  latencies.sort()
  return {
    "scenario": "sliding_window_record_failure",
    "ops_per_sec": ITERATIONS / elapsed,
    "total_s": elapsed,
    "p50_us": _percentile(latencies, 50) / 1000,
    "p95_us": _percentile(latencies, 95) / 1000,
    "p99_us": _percentile(latencies, 99) / 1000,
    "mean_us": statistics.mean(latencies) / 1000,
  }


# ───────────────────────────────────────────────────────────────────
# Runner
# ───────────────────────────────────────────────────────────────────


def _format_result(result: dict[str, float]) -> str:
  """Format a benchmark result as a human-readable string."""
  lines = [f"  {result['scenario']}:"]
  lines.append(f"    Throughput: {result['ops_per_sec']:,.0f} ops/sec")
  lines.append(f"    Total time: {result['total_s']:.3f}s")
  if "p50_us" in result:
    lines.append(
      f"    Latency: p50={result['p50_us']:.2f}µs  p95={result['p95_us']:.2f}µs  p99={result['p99_us']:.2f}µs  mean={result['mean_us']:.2f}µs"
    )
  if "total_ops" in result:
    lines.append(f"    Total ops: {result['total_ops']:,}")
  return "\n".join(lines)


def main() -> None:
  """Run all benchmarks and print results."""
  print(f"Circuit Breaker Benchmarks ({ITERATIONS:,} iterations, {THREADS} threads)")
  print("=" * 72)

  benchmarks = [
    bench_single_thread_closed,
    bench_single_thread_open,
    bench_multi_thread_contention,
    bench_sliding_window_allow,
    bench_sliding_window_record_failure,
  ]

  for bench_fn in benchmarks:
    result = bench_fn()
    print(_format_result(result))
    print()

  print("=" * 72)
  print("Done.")


if __name__ == "__main__":
  main()
