# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Performance Benchmarking for Judge #6 HITL System
Comprehensive performance testing and profiling

Usage:
    python tests/performance/benchmark.py
"""

import time
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from src.judges import JudgeFactory, JudgeRequest, JudgeType


class PerformanceBenchmark:
  """Comprehensive performance benchmarking"""

  def __init__(self):
    self.results = {}

  def benchmark_throughput(self, duration_seconds: int = 10, num_workers: int = 10):
    """
    Benchmark throughput (decisions per second)

    Args:
        duration_seconds: Test duration
        num_workers: Number of concurrent workers
    """
    print("Throughput Benchmark")
    print(f"{'=' * 60}")
    print(f"Duration: {duration_seconds}s")
    print(f"Concurrent workers: {num_workers}")
    print()

    decisions_completed = 0
    start_time = time.time()
    end_time = start_time + duration_seconds

    def worker(worker_id: int):
      count = 0
      idx = 0
      while time.time() < end_time:
        judge_type = list(JudgeType)[idx % len(JudgeType)]
        judge = JudgeFactory.get_judge(judge_type)

        request = JudgeRequest(
          request_id=f"throughput_w{worker_id}_i{idx}",
          judge_type=judge_type,
          action_type="test",
          context={"amount_usd": 1000 + idx},
          requested_by="benchmark@example.com",
        )

        judge.judge(request)
        count += 1
        idx += 1

      return count

    with ThreadPoolExecutor(max_workers=num_workers) as executor:
      futures = [executor.submit(worker, i) for i in range(num_workers)]

      for future in as_completed(futures):
        decisions_completed += future.result()

    actual_duration = time.time() - start_time
    throughput = decisions_completed / actual_duration

    print(f"Decisions completed: {decisions_completed}")
    print(f"Actual duration: {actual_duration:.2f}s")
    print(f"Throughput: {throughput:.2f} decisions/second")
    print("Target: 100 decisions/second per vertical")
    print(f"Status: {'✓ PASS' if throughput >= 100 else '✗ FAIL'}")
    print()

    self.results["throughput"] = {
      "decisions_completed": decisions_completed,
      "duration_seconds": actual_duration,
      "throughput_per_second": throughput,
      "target": 100,
      "passed": throughput >= 100,
    }

  def benchmark_memory_usage(self, num_decisions: int = 10000):
    """
    Benchmark memory usage

    Args:
        num_decisions: Number of decisions to process
    """
    print("Memory Usage Benchmark")
    print(f"{'=' * 60}")
    print(f"Decisions: {num_decisions}")
    print()

    import psutil
    import os

    process = psutil.Process(os.getpid())

    # Get baseline memory
    baseline_mb = process.memory_info().rss / 1024 / 1024

    # Process decisions
    for i in range(num_decisions):
      judge_type = list(JudgeType)[i % len(JudgeType)]
      judge = JudgeFactory.get_judge(judge_type)

      request = JudgeRequest(
        request_id=f"memory_test_{i}",
        judge_type=judge_type,
        action_type="test",
        context={"amount_usd": 1000 + i},
        requested_by="benchmark@example.com",
      )

      judge.judge(request)

    # Get final memory
    final_mb = process.memory_info().rss / 1024 / 1024
    increase_mb = final_mb - baseline_mb

    print(f"Baseline memory: {baseline_mb:.2f} MB")
    print(f"Final memory: {final_mb:.2f} MB")
    print(f"Memory increase: {increase_mb:.2f} MB")
    print(f"Per decision: {(increase_mb / num_decisions) * 1024:.2f} KB")
    print()

    self.results["memory"] = {
      "baseline_mb": baseline_mb,
      "final_mb": final_mb,
      "increase_mb": increase_mb,
      "per_decision_kb": (increase_mb / num_decisions) * 1024,
    }

  def benchmark_cold_vs_warm_start(self, num_iterations: int = 100):
    """
    Benchmark cold start vs warm cache performance

    Args:
        num_iterations: Number of iterations per test
    """
    print("Cold Start vs Warm Cache Benchmark")
    print(f"{'=' * 60}")
    print(f"Iterations: {num_iterations}")
    print()

    # Cold start: Reset factory each time
    cold_latencies = []
    for i in range(num_iterations):
      JudgeFactory.reset()
      judge = JudgeFactory.get_judge(JudgeType.FIN)

      request = JudgeRequest(
        request_id=f"cold_{i}",
        judge_type=JudgeType.FIN,
        action_type="test",
        context={"amount_usd": 50000},
        requested_by="benchmark@example.com",
      )

      start = time.perf_counter()
      judge.judge(request)
      end = time.perf_counter()

      cold_latencies.append((end - start) * 1000)

    # Warm cache: Reuse judge instance
    JudgeFactory.reset()
    judge = JudgeFactory.get_judge(JudgeType.FIN)
    warm_latencies = []

    for i in range(num_iterations):
      request = JudgeRequest(
        request_id=f"warm_{i}",
        judge_type=JudgeType.FIN,
        action_type="test",
        context={"amount_usd": 50000},
        requested_by="benchmark@example.com",
      )

      start = time.perf_counter()
      judge.judge(request)
      end = time.perf_counter()

      warm_latencies.append((end - start) * 1000)

    cold_mean = statistics.mean(cold_latencies)
    warm_mean = statistics.mean(warm_latencies)
    speedup = cold_mean / warm_mean

    print(f"Cold start mean: {cold_mean:.2f}ms")
    print(f"Warm cache mean: {warm_mean:.2f}ms")
    print(f"Speedup: {speedup:.2f}x")
    print()

    self.results["cold_vs_warm"] = {
      "cold_mean_ms": cold_mean,
      "warm_mean_ms": warm_mean,
      "speedup_factor": speedup,
    }

  def benchmark_decision_complexity(self):
    """
    Benchmark performance across different decision complexities
    """
    print("Decision Complexity Benchmark")
    print(f"{'=' * 60}")
    print()

    test_cases = [
      (
        "Simple ALLOW",
        JudgeType.FIN,
        {"amount_usd": 1000, "vendor_status": "approved", "purchase_order": "PO-123"},
      ),
      (
        "Simple BLOCK",
        JudgeType.FIN,
        {
          "amount_usd": 75000,
          "vendor_status": "new",
          "purchase_order": None,
          "destination_country": "Unknown",
        },
      ),
      (
        "Complex fraud",
        JudgeType.FRAUD,
        {
          "fraud_score": 0.65,
          "identity_verified": True,
          "geo_location_mismatch": True,
          "velocity_check_failed": False,
          "device_fingerprint_match": True,
          "amount_usd": 10000,
          "account_age_days": 45,
        },
      ),
    ]

    for name, judge_type, context in test_cases:
      latencies = []

      for i in range(100):
        judge = JudgeFactory.get_judge(judge_type)
        request = JudgeRequest(
          request_id=f"complexity_{name}_{i}",
          judge_type=judge_type,
          action_type="test",
          context=context,
          requested_by="benchmark@example.com",
        )

        start = time.perf_counter()
        judge.judge(request)
        end = time.perf_counter()

        latencies.append((end - start) * 1000)

      mean_latency = statistics.mean(latencies)
      print(f"{name:20} mean: {mean_latency:.2f}ms")

    print()

  def run_all_benchmarks(self):
    """Run all benchmarks"""
    print(f"\n{'#' * 60}")
    print("# Judge #6 HITL System - Performance Benchmarks")
    print(f"{'#' * 60}\n")

    self.benchmark_throughput(duration_seconds=10, num_workers=10)
    self.benchmark_cold_vs_warm_start(num_iterations=100)
    self.benchmark_decision_complexity()

    # Skip memory benchmark if psutil not available
    try:
      import psutil

      self.benchmark_memory_usage(num_decisions=1000)
    except ImportError:
      print("Memory benchmark skipped (psutil not installed)")
      print()

    print(f"{'#' * 60}")
    print("# Benchmarks Complete")
    print(f"{'#' * 60}\n")


def main():
  """Run performance benchmarks"""
  benchmark = PerformanceBenchmark()
  benchmark.run_all_benchmarks()


if __name__ == "__main__":
  main()
