# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.


class LatencyHistogram:
  """Track p50/p90/p99 latencies"""

  def __init__(self):
    self.samples = []
    self.max_samples = 10_000  # Rolling window

  def record(self, latency_us: int):
    self.samples.append(latency_us)
    if len(self.samples) > self.max_samples:
      self.samples.pop(0)  # Evict oldest

  def percentile(self, p: float) -> float:
    """Get p-th percentile (e.g., p=0.99 for p99)"""
    if not self.samples:
      return 0.0
    sorted_samples = sorted(self.samples)
    index = int(len(sorted_samples) * p)
    if index >= len(sorted_samples):
      index = len(sorted_samples) - 1
    return sorted_samples[index]
