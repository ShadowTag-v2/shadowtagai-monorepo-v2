# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""
Real EdgeQueue Integration for Claude_Code_6 Monitor
Connects the TUI to the validated EdgeQueue runtime
"""

import asyncio
import os
import sys

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time

from runtime.edge_queue import EdgeQueue, EdgeSignal, PolicyWASM
from tui.Cor_Claude_Code_6_monitor import DecisionMetric


class EdgeQueueEngine:
  """Real EdgeQueue governance engine adapter"""

  def __init__(self, worker_url: str = "https://Cor_Claude_Code_6-test.workers.dev"):
    self.worker_url = worker_url
    self.decision_count = 0

    # Pre-load policies
    self.pii_policy = PolicyWASM.load_precompiled("pii_check_v1")
    self.rate_policy = PolicyWASM.load_precompiled("rate_limit_v1")
    self.content_policy = PolicyWASM.load_precompiled("content_filter_v1")

  async def make_decision(self) -> DecisionMetric:
    """Execute governance check via EdgeQueue"""

    # Create test context
    context = {
      "text": "Sample request content",
      "user_id": f"test_{self.decision_count}",
      "timestamp": time.time(),
    }

    # Build EdgeQueue
    queue = EdgeQueue()

    EdgeSignal(f"start-{self.decision_count}")
    EdgeSignal(f"end-{self.decision_count}")

    # IMPORTANT: timestamp() creates timestamp commands
    # but for local testing we'll just measure client-side latency
    start_us = time.time() * 1_000_000

    # Batch 3 policies into single request
    queue.exec(self.pii_policy, context)
    queue.exec(self.rate_policy, context)
    queue.exec(self.content_policy, context)

    try:
      # Submit - this is where the real latency happens
      result = await asyncio.to_thread(queue.submit, self.worker_url)

      end_us = time.time() * 1_000_000
      latency_us = int(end_us - start_us)

      # Check if all policies passed
      all_passed = all(
        r.get("result") == 1
        for r in result.get("results", [])
        if r.get("type") == "exec"
      )

      self.decision_count += 1

      return DecisionMetric(
        timestamp=time.time(),
        latency_us=latency_us,
        result="PASS" if all_passed else "FAIL",
        violation_type="" if all_passed else "POLICY_VIOLATION",
      )

    except Exception as e:
      self.decision_count += 1
      return DecisionMetric(
        timestamp=time.time(),
        latency_us=200_000,  # 200ms timeout
        result="ERROR",
        violation_type=f"ERROR: {str(e)}",
      )


# Allow import by Cor_Claude_Code_6_monitor.py with mode=edgequeue
RealCor_Claude_Code_6Engine = EdgeQueueEngine
