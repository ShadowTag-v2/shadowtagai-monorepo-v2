# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Benchmark: SubAgentCoordinator dispatch latency under 100-task workloads.

Measures:
- Total wall time for 100 concurrent dispatches
- Mean, P50, P95, P99 per-task latencies
- Throughput (tasks/second)
- Error rate under contention
"""

from __future__ import annotations

import asyncio
import os
import statistics
import sys
import time

# Bootstrap monorepo imports
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO_ROOT not in sys.path:
  sys.path.insert(0, _REPO_ROOT)
_PKG_DIR = os.path.join(_REPO_ROOT, "packages")
if _PKG_DIR not in sys.path:
  sys.path.insert(0, _PKG_DIR)


async def run_benchmark(n_tasks: int = 100, max_concurrency: int = 8) -> dict:
  """Execute the coordinator benchmark and return metrics."""
  from packages.agnt_coordinator import SubAgentCoordinator

  coordinator = SubAgentCoordinator(
    max_concurrency=max_concurrency,
    timeout_s=30.0,
  )

  # Simulate real-world sub-agent work: light I/O + CPU
  async def mock_sub_agent(task_id: int, delay_ms: float = 5.0) -> dict:
    """Simulate a sub-agent that does a small amount of async work."""
    await asyncio.sleep(delay_ms / 1000.0)
    # Small CPU work to simulate response processing
    _ = sum(range(1000))
    return {"task_id": task_id, "status": "complete"}

  # Build task batch
  tasks = [
    (f"bench_{i}", mock_sub_agent, {"task_id": i, "delay_ms": 5.0})
    for i in range(n_tasks)
  ]

  # Warm up the event loop
  await asyncio.sleep(0.01)

  # Benchmark
  wall_start = time.perf_counter()
  results = await coordinator.dispatch_batch(tasks)
  wall_end = time.perf_counter()

  wall_time = wall_end - wall_start
  latencies = [r.elapsed_s * 1000 for r in results]  # ms
  done = sum(1 for r in results if r.state.value == "done")
  failed = sum(1 for r in results if r.state.value == "failed")

  metrics = {
    "n_tasks": n_tasks,
    "max_concurrency": max_concurrency,
    "wall_time_ms": round(wall_time * 1000, 2),
    "throughput_tasks_per_sec": round(n_tasks / wall_time, 1),
    "done": done,
    "failed": failed,
    "error_rate_pct": round(failed / n_tasks * 100, 2),
    "latency_mean_ms": round(statistics.mean(latencies), 2),
    "latency_p50_ms": round(statistics.median(latencies), 2),
    "latency_p95_ms": round(sorted(latencies)[int(n_tasks * 0.95)], 2),
    "latency_p99_ms": round(sorted(latencies)[int(n_tasks * 0.99)], 2),
    "latency_max_ms": round(max(latencies), 2),
  }

  summary = coordinator.summary()
  metrics["coordinator_summary"] = summary

  return metrics


def main():
  """Run benchmark and print results."""
  import json

  print("=" * 60)
  print("SubAgentCoordinator Dispatch Benchmark")
  print("=" * 60)

  # Test at multiple concurrency levels (Playbook Phase C: C=32, C=64 required)
  for concurrency in [4, 8, 16, 32, 64]:
    print(f"\n--- Concurrency: {concurrency} ---")
    metrics = asyncio.run(run_benchmark(n_tasks=100, max_concurrency=concurrency))
    for key, val in metrics.items():
      if key == "coordinator_summary":
        continue
      print(f"  {key}: {val}")

  # Large workload test
  print("\n--- Stress Test: 500 tasks @ concurrency=32 ---")
  stress_metrics = asyncio.run(run_benchmark(n_tasks=500, max_concurrency=32))
  print(json.dumps(stress_metrics, indent=2))

  # High-ceiling stress test
  print("\n--- Stress Test: 1000 tasks @ concurrency=64 ---")
  stress_64 = asyncio.run(run_benchmark(n_tasks=1000, max_concurrency=64))
  print(json.dumps(stress_64, indent=2))


if __name__ == "__main__":
  main()
