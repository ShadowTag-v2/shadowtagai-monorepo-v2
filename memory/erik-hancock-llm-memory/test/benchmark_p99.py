# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
import os
import random
import sys
import time

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from judge6.runtime.ops_edge import EdgeDevice
from judge6.runtime.profiling import LatencyHistogram


def benchmark():
  print("Starting p99 Latency Benchmark...")

  # Setup
  EdgeDevice("worker-local")
  histogram = LatencyHistogram()

  # Mock workload
  # Simulate 10,000 requests with varying latency
  # Normal distribution centered at 12ms, with occasional spikes

  start_time = time.time()

  print("Simulating 10,000 requests...")
  for i in range(10000):
    req_start = time.perf_counter()

    # Simulate processing
    base_latency = random.normalvariate(0.012, 0.002)  # 12ms +/- 2ms
    if base_latency < 0.001:
      base_latency = 0.001

    # 1% chance of spike (GC, cold start, etc)
    if random.random() < 0.01:
      base_latency += random.uniform(0.050, 0.100)  # +50-100ms

    time.sleep(base_latency)

    req_end = time.perf_counter()
    latency_us = int((req_end - req_start) * 1_000_000)

    histogram.record(latency_us)

    if i > 0 and i % 1000 == 0:
      print(f"Processed {i} requests...")

  total_time = time.time() - start_time
  print(f"\nBenchmark complete in {total_time:.2f}s")

  # Report
  p50 = histogram.percentile(0.50) / 1000
  p90 = histogram.percentile(0.90) / 1000
  p99 = histogram.percentile(0.99) / 1000

  print("Latencies (ms):")
  print(f"  p50: {p50:.2f}ms")
  print(f"  p90: {p90:.2f}ms")
  print(f"  p99: {p99:.2f}ms")

  # Note: Since this is a simulation with random spikes, it might fail occasionally
  # But it verifies the measurement infrastructure works
  if p99 <= 90.0:
    print("✅ SLA MET: p99 <= 90ms")
  else:
    print("❌ SLA VIOLATED: p99 > 90ms (Expected for simulation with spikes)")


if __name__ == "__main__":
  benchmark()
