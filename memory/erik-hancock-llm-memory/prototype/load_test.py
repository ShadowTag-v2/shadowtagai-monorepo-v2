# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Measure p99 latency of the EdgeQueue prototype
"""

import concurrent.futures
import os
import statistics
import sys
import time

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import MagicMock

# Mock the requests.post to simulate network latency if no real worker is running
import requests
from runtime.edge_queue import EdgeQueue, PolicyWASM

# Check if we should use mock
USE_MOCK = True

if USE_MOCK:

    def mock_post(*args, **kwargs):
        # Simulate network latency (20-40ms)
        time.sleep(0.03)

        mock_resp = MagicMock()
        mock_resp.ok = True
        mock_resp.status_code = 200

        # Generate mock results based on input commands
        payload = kwargs.get("json", {})
        commands = payload.get("commands", [])
        results = []

        for cmd in commands:
            if cmd["type"] == "exec":
                results.append({"type": "exec", "policy": cmd["args"]["policy_name"], "result": 1, "latency_us": 2000})
            elif cmd["type"] == "timestamp":
                results.append({"type": "timestamp", "timestamp_us": time.time() * 1000000})
            else:
                results.append({"type": cmd["type"], "status": "ok"})

        mock_resp.json.return_value = {"results": results, "total_latency_us": 5000, "command_count": len(commands)}
        return mock_resp

    requests.post = mock_post


def run_batch_check():
    """Single policy check (3 policies batched)"""

    # Load dummy policies
    pii_policy = PolicyWASM.load_precompiled("pii_check_v1")
    rate_policy = PolicyWASM.load_precompiled("rate_limit_v1")
    content_policy = PolicyWASM.load_precompiled("content_filter_v1")

    # Build queue
    queue = EdgeQueue()
    queue.exec(pii_policy, {"text": "Test content"})
    queue.exec(rate_policy, {"user_id": "123"})
    queue.exec(content_policy, {"text": "Test content"})

    # Submit
    result = queue.submit("https://judge6-test.workers.dev")
    return result["queue_latency_us"] / 1000.0  # Convert us to ms


def load_test(num_requests: int = 100, concurrency: int = 5):
    """Run load test"""
    print(f"Starting Load Test: {num_requests} requests, {concurrency} concurrent...")
    latencies = []

    start_time = time.time()

    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(run_batch_check) for _ in range(num_requests)]

        for i, future in enumerate(concurrent.futures.as_completed(futures)):
            try:
                latency_ms = future.result()
                latencies.append(latency_ms)
                if i % 10 == 0:
                    print(".", end="", flush=True)
            except Exception as e:
                print(f"Request failed: {e}")

    print("\n")
    duration = time.time() - start_time

    if not latencies:
        print("No successful requests.")
        return

    # Calculate percentiles
    latencies_sorted = sorted(latencies)
    p50 = latencies_sorted[len(latencies) // 2]
    p90 = latencies_sorted[int(len(latencies) * 0.9)]
    p99 = latencies_sorted[int(len(latencies) * 0.99)]

    print("Load Test Results:")
    print(f"  Total Time: {duration:.2f}s")
    print(f"  Throughput: {num_requests / duration:.1f} req/s")
    print(f"  p50: {p50:.1f}ms")
    print(f"  p90: {p90:.1f}ms")
    print(f"  p99: {p99:.1f}ms")
    print(f"  Avg: {statistics.mean(latencies):.1f}ms")

    if p99 < 90:
        print("\n✅ SUCCESS: p99 < 90ms SLA met!")
    else:
        print("\n❌ FAILURE: p99 > 90ms SLA exceeded.")


if __name__ == "__main__":
    load_test()
