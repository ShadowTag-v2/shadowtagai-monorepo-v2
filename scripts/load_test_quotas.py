#!/usr/bin/env python3
"""Load test script for sandbox quota enforcement.

Validates that the SandboxMiddleware correctly enforces per-tier quotas
by simulating rapid-fire requests from multiple firms.

Usage:
    python scripts/load_test_quotas.py [--url URL] [--tier TIER] [--count N]
"""

from __future__ import annotations

import argparse
import asyncio
import sys
import time
from dataclasses import dataclass


@dataclass
class LoadTestResult:
    """Results from a single load test run."""
    firm_id: str
    tier: str
    total_requests: int
    accepted: int
    rejected_429: int
    errors: int
    duration_ms: int
    rps: float


async def run_load_test(
    url: str,
    firm_id: str,
    tier: str,
    count: int,
    concurrency: int = 10,
) -> LoadTestResult:
    """Run a load test against the API with specified parameters."""
    import httpx

    accepted = 0
    rejected = 0
    errors = 0
    start = time.monotonic()

    semaphore = asyncio.Semaphore(concurrency)

    async def make_request(client: httpx.AsyncClient, i: int):
        nonlocal accepted, rejected, errors
        async with semaphore:
            try:
                resp = await client.get(
                    f"{url}/health",
                    headers={
                        "X-Firm-ID": firm_id,
                        "X-Attorney-ID": f"atty_{i}",
                    },
                    timeout=5,
                )
                if resp.status_code == 429:
                    rejected += 1
                elif resp.status_code < 400:
                    accepted += 1
                else:
                    errors += 1
            except Exception:
                errors += 1

    async with httpx.AsyncClient() as client:
        tasks = [make_request(client, i) for i in range(count)]
        await asyncio.gather(*tasks)

    elapsed = int((time.monotonic() - start) * 1000)
    rps = count / (elapsed / 1000) if elapsed > 0 else 0

    return LoadTestResult(
        firm_id=firm_id,
        tier=tier,
        total_requests=count,
        accepted=accepted,
        rejected_429=rejected,
        errors=errors,
        duration_ms=elapsed,
        rps=round(rps, 1),
    )


def _print_results(results: list[LoadTestResult]):
    """Print load test results as a formatted table."""
    print("\n" + "=" * 80)
    print("LOAD TEST RESULTS — Sandbox Quota Enforcement")
    print("=" * 80)
    print(f"{'Firm':<15} {'Tier':<12} {'Total':<8} {'Accepted':<10} {'429s':<8} {'Errors':<8} {'RPS':<8} {'Time':<8}")
    print("-" * 80)
    for r in results:
        print(f"{r.firm_id:<15} {r.tier:<12} {r.total_requests:<8} {r.accepted:<10} {r.rejected_429:<8} {r.errors:<8} {r.rps:<8} {r.duration_ms}ms")
    print("=" * 80)

    # Validate quotas
    for r in results:
        expected_max = {
            "trial": 50,
            "solo": 200,
            "practice": 1000,
            "enterprise": 10000,
        }.get(r.tier, 50)

        if r.total_requests > expected_max and r.rejected_429 == 0:
            print(f"⚠️  FAIL: {r.firm_id} ({r.tier}) sent {r.total_requests} but got 0 rejections!")
        elif r.rejected_429 > 0:
            print(f"✅ PASS: {r.firm_id} ({r.tier}) correctly rejected {r.rejected_429}/{r.total_requests} requests")
        else:
            print(f"✅ PASS: {r.firm_id} ({r.tier}) all {r.accepted} requests within quota")


async def main():
    parser = argparse.ArgumentParser(description="Load test for sandbox quota enforcement")
    parser.add_argument("--url", default="http://localhost:8080", help="Base URL")
    parser.add_argument("--tier", default="all", choices=["trial", "solo", "practice", "enterprise", "all"])
    parser.add_argument("--count", type=int, default=100, help="Requests per tier")
    parser.add_argument("--concurrency", type=int, default=10, help="Concurrent requests")
    args = parser.parse_args()

    tiers = ["trial", "solo", "practice", "enterprise"] if args.tier == "all" else [args.tier]
    results = []

    for tier in tiers:
        print(f"🔥 Testing {tier} tier with {args.count} requests...")
        result = await run_load_test(
            url=args.url,
            firm_id=f"loadtest-{tier}",
            tier=tier,
            count=args.count,
            concurrency=args.concurrency,
        )
        results.append(result)

    _print_results(results)


if __name__ == "__main__":
    asyncio.run(main())
