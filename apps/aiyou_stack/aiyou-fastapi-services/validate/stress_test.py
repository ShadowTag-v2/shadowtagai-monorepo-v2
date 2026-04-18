#!/usr/bin/env python3
"""PNKLN Stress Test for Judge #6

Progressive load testing to find capacity limits.
Increases load until p99 latency exceeds SLA.

Usage:
    python stress_test.py --endpoint http://judge6.pnkln.svc.cluster.local
"""

import argparse
import asyncio

from test_latency import LatencyTester


async def run_stress_test(
    endpoint: str,
    sla_target_ms: float = 90.0,
    start_qps: int = 10,
    max_qps: int = 200,
    step_qps: int = 10,
    duration_per_step: int = 60,
):
    """Progressive stress test

    Increases load in steps until SLA is violated.
    """
    print("\n" + "=" * 70)
    print("🔥 STRESS TEST - Progressive Load")
    print("=" * 70)
    print(f"Target SLA: p99 ≤ {sla_target_ms}ms")
    print(f"Load range: {start_qps} → {max_qps} QPS")
    print(f"Step size: {step_qps} QPS")
    print(f"Duration per step: {duration_per_step}s")
    print("=" * 70 + "\n")

    results = []
    current_qps = start_qps

    while current_qps <= max_qps:
        print(f"\n📈 Testing at {current_qps} QPS...")
        print("-" * 70)

        # Calculate requests and concurrency
        num_requests = current_qps * duration_per_step
        concurrency = min(current_qps, 100)  # Cap concurrency

        # Run test
        tester = LatencyTester(endpoint=endpoint)
        await tester.run_test(num_requests=num_requests, concurrency=concurrency)

        # Generate report
        report = tester.generate_report(sla_target_ms=sla_target_ms)

        # Print summary
        print(f"\n   p99: {report.p99:.2f}ms (target: ≤{sla_target_ms}ms)")
        print(f"   QPS: {report.qps:.2f}")
        print(f"   Success rate: {report.success_rate:.1f}%")

        results.append(
            {
                "target_qps": current_qps,
                "actual_qps": report.qps,
                "p99": report.p99,
                "sla_pass": report.sla_pass,
                "success_rate": report.success_rate,
            },
        )

        # Check if SLA violated
        if not report.sla_pass:
            print(f"\n   ❌ SLA violated at {current_qps} QPS")
            break
        print("   ✅ SLA met")

        current_qps += step_qps

    # Summary
    print("\n" + "=" * 70)
    print("📊 STRESS TEST SUMMARY")
    print("=" * 70 + "\n")

    passing_results = [r for r in results if r["sla_pass"]]

    if passing_results:
        max_qps_passing = max(r["actual_qps"] for r in passing_results)
        print(f"✅ Maximum QPS within SLA: {max_qps_passing:.1f}")

        print("\n📈 Load vs Latency:")
        print(f"{'QPS':<10} {'p99 (ms)':<12} {'Success %':<12} {'Status'}")
        print("-" * 50)
        for r in results:
            status = "✅" if r["sla_pass"] else "❌"
            print(f"{r['actual_qps']:<10.1f} {r['p99']:<12.2f} {r['success_rate']:<12.1f} {status}")
    else:
        print("❌ No load level passed SLA")

    print("\n" + "=" * 70 + "\n")


async def main():
    parser = argparse.ArgumentParser(description="PNKLN Stress Test - Find capacity limits")
    parser.add_argument(
        "--endpoint",
        default="http://judge6.pnkln.svc.cluster.local",
        help="Inference endpoint URL",
    )
    parser.add_argument(
        "--p99-target-ms",
        type=float,
        default=90.0,
        help="p99 latency SLA target in milliseconds",
    )
    parser.add_argument("--start-qps", type=int, default=10, help="Starting QPS")
    parser.add_argument("--max-qps", type=int, default=200, help="Maximum QPS to test")
    parser.add_argument("--step-qps", type=int, default=10, help="QPS increment per step")
    parser.add_argument("--duration", type=int, default=60, help="Duration per step in seconds")

    args = parser.parse_args()

    await run_stress_test(
        endpoint=args.endpoint,
        sla_target_ms=args.p99_target_ms,
        start_qps=args.start_qps,
        max_qps=args.max_qps,
        step_qps=args.step_qps,
        duration_per_step=args.duration,
    )


if __name__ == "__main__":
    asyncio.run(main())
