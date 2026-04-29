#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Judge 6 Latency Validation - Enhanced Version v2.0
Target: P99 ≤90ms, P95 ≤65ms, P50 ≤40ms
Features: Adaptive load, degradation detection, results export, warmup
"""

import asyncio
import json
import os
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

import httpx
import numpy as np

# ═══════════════════════════════════════════════════════════════════
# Configuration Management
# ═══════════════════════════════════════════════════════════════════


@dataclass
class TestConfig:
    """Environment-aware configuration"""

    endpoint: str
    iterations: int
    warmup_iterations: int
    concurrency: int
    request_timeout: float
    connect_timeout: float

    @classmethod
    def from_env(cls, prefix: str = "COR_CLAUDE_CODE_6"):
        """Load configuration from environment variables"""
        return cls(
            endpoint=os.getenv(f"{prefix}_ENDPOINT", "https://Cor_Claude_Code_6.pnkln.ai/enforce"),
            iterations=int(os.getenv(f"{prefix}_ITERATIONS", "1000")),
            warmup_iterations=int(os.getenv(f"{prefix}_WARMUP", "50")),
            concurrency=int(os.getenv(f"{prefix}_CONCURRENCY", "50")),
            request_timeout=float(os.getenv(f"{prefix}_REQUEST_TIMEOUT", "5.0")),
            connect_timeout=float(os.getenv(f"{prefix}_CONNECT_TIMEOUT", "2.0")),
        )


config = TestConfig.from_env()

# Test payload
PAYLOAD = {
    "request_id": "val_test",
    "transaction": {
        "from_addr": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bE8",
        "to_addr": "0x5aAeb6053F3E94C9b9A09f33669435E7Ef1BeAed",
        "value": "1000000000000000000",
        "gas_limit": "21000",
        "gas_price": "50000000000",
        "nonce": 42,
        "data": "0x",
    },
    "context": {
        "user_id": "test_user_001",
        "session_id": "sess_12345",
        "ip_address": "192.168.1.100",
        "timestamp": int(time.time()),
    },
    "rules": {"enforce_cost_gate": True, "enforce_compliance": True, "enforce_atp_5_19": True},
}

# SLA Targets
SLA_P99_MS = 90
SLA_P95_MS = 65
SLA_P50_MS = 40

# ═══════════════════════════════════════════════════════════════════
# Adaptive Load Controller
# ═══════════════════════════════════════════════════════════════════


class AdaptiveLoadController:
    """Dynamically adjusts concurrency based on error rates and latency"""

    def __init__(self, initial_concurrency: int, target_error_rate: float = 0.01):
        self.current_concurrency = initial_concurrency
        self.target_error_rate = target_error_rate
        self.history = []

    async def adjust_concurrency(self, error_rate: float, latency_p99: float) -> int:
        """Adjust concurrency based on system health"""
        self.history.append(
            {
                "error_rate": error_rate,
                "latency_p99": latency_p99,
                "concurrency": self.current_concurrency,
            },
        )

        # Reduce load if system is stressed
        if error_rate > self.target_error_rate or latency_p99 > SLA_P99_MS * 1.5:
            self.current_concurrency = max(1, int(self.current_concurrency * 0.8))
        # Increase load if system is healthy
        elif error_rate < self.target_error_rate * 0.5 and latency_p99 < SLA_P99_MS * 0.8:
            self.current_concurrency = min(200, int(self.current_concurrency * 1.2))

        return self.current_concurrency


# ═══════════════════════════════════════════════════════════════════
# Degradation Detection
# ═══════════════════════════════════════════════════════════════════


def detect_degradation(latencies: list[float], window_size: int = 100) -> dict:
    """Detect if response times are degrading over time"""
    if len(latencies) < window_size * 2:
        return {"degradation_detected": False, "message": "Insufficient data"}

    first_window = latencies[:window_size]
    last_window = latencies[-window_size:]

    first_p50 = np.percentile(first_window, 50)
    last_p50 = np.percentile(last_window, 50)
    first_p99 = np.percentile(first_window, 99)
    last_p99 = np.percentile(last_window, 99)

    degradation_p50 = ((last_p50 - first_p50) / first_p50) * 100 if first_p50 > 0 else 0
    degradation_p99 = ((last_p99 - first_p99) / first_p99) * 100 if first_p99 > 0 else 0

    return {
        "degradation_detected": degradation_p50 > 20 or degradation_p99 > 30,
        "p50_change_pct": round(degradation_p50, 2),
        "p99_change_pct": round(degradation_p99, 2),
        "first_window_p50": round(first_p50, 2),
        "last_window_p50": round(last_p50, 2),
        "first_window_p99": round(first_p99, 2),
        "last_window_p99": round(last_p99, 2),
    }


# ═══════════════════════════════════════════════════════════════════
# Results Export
# ═══════════════════════════════════════════════════════════════════


def export_results(results: dict, service_name: str = "Cor_Claude_Code_6"):
    """Export results for historical tracking and analysis"""
    timestamp = datetime.now().isoformat()
    results_dir = Path("test_results")
    results_dir.mkdir(exist_ok=True)

    filename = results_dir / f"{service_name}_{timestamp.replace(':', '-')}.json"

    export_data = {
        "timestamp": timestamp,
        "service": service_name,
        "environment": os.getenv("ENV", "production"),
        "configuration": asdict(config),
        "results": results,
        "sla_compliance": {
            "p99_target_ms": SLA_P99_MS,
            "p95_target_ms": SLA_P95_MS,
            "p50_target_ms": SLA_P50_MS,
            "passed": results.get("sla_pass", False),
        },
        "metadata": {
            "test_version": "2.0.0",
            "hostname": os.uname().nodename,
            "python_version": sys.version,
        },
    }

    with open(filename, "w") as f:
        json.dump(export_data, f, indent=2)

    print(f"\nResults exported to: {filename}")
    return filename


# ═══════════════════════════════════════════════════════════════════
# Core Testing Logic
# ═══════════════════════════════════════════════════════════════════


async def measure_latency(
    client: httpx.AsyncClient,
    request_id: int,
) -> tuple[float | None, bool, str | None]:
    """Measure single request latency"""
    payload = PAYLOAD.copy()
    payload["request_id"] = f"val_test_{request_id}"
    payload["context"]["timestamp"] = int(time.time())

    start = time.perf_counter()
    try:
        response = await client.post(config.endpoint, json=payload, timeout=config.request_timeout)
        latency_ms = (time.perf_counter() - start) * 1000

        if response.status_code == 200:
            return latency_ms, True, None
        return latency_ms, False, f"HTTP_{response.status_code}"

    except httpx.TimeoutException:
        latency_ms = (time.perf_counter() - start) * 1000
        return latency_ms, False, "TIMEOUT"

    except httpx.ConnectError:
        latency_ms = (time.perf_counter() - start) * 1000
        return latency_ms, False, "CONNECT_ERROR"

    except Exception as e:
        latency_ms = (time.perf_counter() - start) * 1000
        return latency_ms, False, f"ERROR: {str(e)[:30]}"


async def run_batch(client: httpx.AsyncClient, start_id: int, batch_size: int, concurrency: int):
    """Run a batch of requests with specified concurrency"""
    semaphore = asyncio.Semaphore(concurrency)

    async def bounded_measure(req_id: int):
        async with semaphore:
            return await measure_latency(client, req_id)

    tasks = [bounded_measure(start_id + i) for i in range(batch_size)]
    return await asyncio.gather(*tasks)


async def run_validation():
    """Main validation function with all enhancements"""
    print("═══════════════════════════════════════════════════════════════════")
    print("  JUDGE #6 LATENCY VALIDATION - ENHANCED v2.0")
    print("═══════════════════════════════════════════════════════════════════")
    print(f"Environment:  {os.getenv('ENV', 'production')}")
    print(f"Endpoint:     {config.endpoint}")
    print(f"Iterations:   {config.iterations} (+ {config.warmup_iterations} warmup)")
    print(f"Concurrency:  {config.concurrency} (adaptive)")
    print(f"Target P99:   ≤{SLA_P99_MS}ms")
    print(f"Target P95:   ≤{SLA_P95_MS}ms")
    print(f"Target P50:   ≤{SLA_P50_MS}ms")
    print()

    limits = httpx.Limits(
        max_keepalive_connections=config.concurrency * 2,
        max_connections=config.concurrency * 3,
        keepalive_expiry=30.0,
    )

    timeout = httpx.Timeout(
        connect=config.connect_timeout,
        read=config.request_timeout,
        write=config.request_timeout,
        pool=config.request_timeout,
    )

    load_controller = AdaptiveLoadController(config.concurrency)
    latencies: list[float] = []
    successes = 0
    errors = {}
    connections_created = 0

    async with httpx.AsyncClient(limits=limits, timeout=timeout) as client:
        # Warmup phase (not counted in results)
        print(f"Warming up with {config.warmup_iterations} requests...")
        warmup_results = await run_batch(
            client,
            -config.warmup_iterations,
            config.warmup_iterations,
            min(10, config.concurrency),
        )
        warmup_success = sum(1 for _, success, _ in warmup_results if success)
        print(f"Warmup complete: {warmup_success}/{config.warmup_iterations} successful\n")

        print("Starting validation...\n")
        start_time = time.perf_counter()

        # Main test with adaptive batching
        batch_size = 100
        num_batches = config.iterations // batch_size
        remaining = config.iterations % batch_size

        current_concurrency = config.concurrency

        for batch_num in range(num_batches + (1 if remaining > 0 else 0)):
            this_batch_size = batch_size if batch_num < num_batches else remaining

            if this_batch_size == 0:
                continue

            batch_results = await run_batch(
                client,
                batch_num * batch_size,
                this_batch_size,
                current_concurrency,
            )

            # Process batch results
            batch_latencies = []
            batch_errors = 0

            for latency_ms, success, error_msg in batch_results:
                if latency_ms is not None:
                    latencies.append(latency_ms)
                    batch_latencies.append(latency_ms)

                if success:
                    successes += 1
                else:
                    batch_errors += 1
                    if error_msg:
                        errors[error_msg] = errors.get(error_msg, 0) + 1

            # Adaptive load adjustment
            if batch_latencies:
                batch_error_rate = batch_errors / len(batch_results)
                batch_p99 = np.percentile(batch_latencies, 99)
                new_concurrency = await load_controller.adjust_concurrency(
                    batch_error_rate,
                    batch_p99,
                )

                if new_concurrency != current_concurrency:
                    print(
                        f"  Batch {batch_num + 1}/{num_batches}: Adjusting concurrency {current_concurrency} → {new_concurrency}",
                    )
                    current_concurrency = new_concurrency

        total_time = time.perf_counter() - start_time

        # Get connection pool stats
        try:
            connections_in_use = len(client._transport._pool._requests)
        except Exception:
            connections_in_use = 0

        pool_stats = {
            "connections_in_use": connections_in_use,
            "max_connections": limits.max_connections,
            "connection_reuse_ratio": round(
                (config.iterations - connections_created) / config.iterations,
                2,
            )
            if config.iterations > 0
            else 0,
        }

    # Calculate statistics
    latencies_np = np.array(latencies)

    p0 = np.percentile(latencies_np, 0)
    p50 = np.percentile(latencies_np, 50)
    p95 = np.percentile(latencies_np, 95)
    p99 = np.percentile(latencies_np, 99)
    p999 = np.percentile(latencies_np, 99.9)
    mean = np.mean(latencies_np)
    std = np.std(latencies_np)
    np.min(latencies_np)
    max_lat = np.max(latencies_np)

    success_rate = (successes / config.iterations) * 100
    error_rate = ((config.iterations - successes) / config.iterations) * 100
    throughput = config.iterations / total_time

    # Check for degradation
    degradation = detect_degradation(latencies)

    # SLA compliance
    p99_pass = p99 <= SLA_P99_MS
    p95_pass = p95 <= SLA_P95_MS
    p50_pass = p50 <= SLA_P50_MS
    all_pass = (
        p99_pass
        and p95_pass
        and p50_pass
        and error_rate < 1.0
        and not degradation["degradation_detected"]
    )

    # Build results dictionary
    results = {
        "sla_pass": bool(all_pass),
        "total_time_sec": round(total_time, 2),
        "throughput_rps": round(throughput, 1),
        "success_rate_pct": round(success_rate, 2),
        "error_rate_pct": round(error_rate, 2),
        "latency_ms": {
            "p0_min": round(p0, 2),
            "p50": round(p50, 2),
            "p95": round(p95, 2),
            "p99": round(p99, 2),
            "p999": round(p999, 2),
            "max": round(max_lat, 2),
            "mean": round(mean, 2),
            "std": round(std, 2),
        },
        "sla_compliance": {
            "p50_pass": bool(p50_pass),
            "p95_pass": bool(p95_pass),
            "p99_pass": bool(p99_pass),
        },
        "degradation": degradation,
        "adaptive_load": load_controller.history,
        "errors": errors,
        "pool_stats": pool_stats,
    }

    # Print results
    print("═══════════════════════════════════════════════════════════════════")
    print("  RESULTS")
    print("═══════════════════════════════════════════════════════════════════")
    print(f"Total Time:       {total_time:.2f}s")
    print(f"Throughput:       {throughput:.1f} req/s")
    print(f"Success Rate:     {success_rate:.2f}%")
    print(f"Error Rate:       {error_rate:.2f}%")
    print()

    print("LATENCY DISTRIBUTION:")
    print(f"  P0 (Min): {p0:7.2f}ms")
    print(f"  Mean:     {mean:7.2f}ms (±{std:.2f}ms)")
    print(f"  P50:      {p50:7.2f}ms  [{'PASS' if p50_pass else 'FAIL'}] (target: ≤{SLA_P50_MS}ms)")
    print(f"  P95:      {p95:7.2f}ms  [{'PASS' if p95_pass else 'FAIL'}] (target: ≤{SLA_P95_MS}ms)")
    print(f"  P99:      {p99:7.2f}ms  [{'PASS' if p99_pass else 'FAIL'}] (target: ≤{SLA_P99_MS}ms)")
    print(f"  P99.9:    {p999:7.2f}ms")
    print(f"  Max:      {max_lat:7.2f}ms")
    print()

    print("DEGRADATION ANALYSIS:")
    if degradation["degradation_detected"]:
        print("  ⚠ DEGRADATION DETECTED")
        print(f"  P50 change: {degradation['p50_change_pct']:+.1f}%")
        print(f"  P99 change: {degradation['p99_change_pct']:+.1f}%")
    else:
        print("  ✓ No significant degradation detected")
    print()

    print("CONNECTION POOL:")
    print(f"  Active connections: {pool_stats['connections_in_use']}")
    print(f"  Max connections:    {pool_stats['max_connections']}")
    print(f"  Reuse ratio:        {pool_stats['connection_reuse_ratio']:.1%}")
    print()

    if errors:
        print("ERRORS:")
        for error_msg, count in sorted(errors.items(), key=lambda x: x[1], reverse=True):
            print(f"  {error_msg}: {count} ({count / config.iterations * 100:.1f}%)")
        print()

    print("═══════════════════════════════════════════════════════════════════")
    if all_pass:
        print("  ✓ SLA COMPLIANCE: PASS")
    else:
        print("  ✗ SLA COMPLIANCE: FAIL")
        if not p99_pass:
            print(
                f"    - P99 latency {p99:.2f}ms exceeds {SLA_P99_MS}ms target by {p99 - SLA_P99_MS:.2f}ms",
            )
        if not p95_pass:
            print(
                f"    - P95 latency {p95:.2f}ms exceeds {SLA_P95_MS}ms target by {p95 - SLA_P95_MS:.2f}ms",
            )
        if not p50_pass:
            print(
                f"    - P50 latency {p50:.2f}ms exceeds {SLA_P50_MS}ms target by {p50 - SLA_P50_MS:.2f}ms",
            )
        if error_rate >= 1.0:
            print(f"    - Error rate {error_rate:.2f}% exceeds 1% threshold")
        if degradation["degradation_detected"]:
            print("    - Performance degradation detected")
    print("═══════════════════════════════════════════════════════════════════")

    # Export results
    export_results(results, "Cor_Claude_Code_6")

    return 0 if all_pass else 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(run_validation())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nValidation interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\nFatal error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
