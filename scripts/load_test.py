#!/usr/bin/env python3
"""load_test.py — Lightweight API load testing script
═══════════════════════════════════════════════════
Uses asyncio + aiohttp for concurrent request testing.
No external dependencies beyond aiohttp (already in pyproject.toml).

Usage:
  python3 scripts/load_test.py --url https://kovelai.web.app --concurrency 10 --requests 100
  python3 scripts/load_test.py --url https://shadowtagai.web.app --concurrency 5 --requests 50
  python3 scripts/load_test.py --targets all  # Test both sites
"""

import argparse
import asyncio
import statistics
import time

import aiohttp

# ─── Default Targets ───
TARGETS = {
    "kovelai": "https://kovelai.web.app",
    "shadowtagai": "https://shadowtagai.web.app",
}

# ─── Icons ───
OK = "✅"
WARN = "⚠️"
FAIL = "❌"


async def fetch(session: aiohttp.ClientSession, url: str) -> tuple[int, float]:
    """Make a single request and return (status_code, latency_ms)."""
    start = time.monotonic()
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            await resp.read()
            elapsed = (time.monotonic() - start) * 1000
            return resp.status, elapsed
    except Exception:
        elapsed = (time.monotonic() - start) * 1000
        return 0, elapsed


async def run_load_test(url: str, concurrency: int, total_requests: int) -> dict:
    """Execute load test against a single URL."""
    results: list[tuple[int, float]] = []
    semaphore = asyncio.Semaphore(concurrency)

    async def bounded_fetch(session: aiohttp.ClientSession) -> None:
        async with semaphore:
            result = await fetch(session, url)
            results.append(result)

    connector = aiohttp.TCPConnector(limit=concurrency, force_close=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        start = time.monotonic()
        tasks = [bounded_fetch(session) for _ in range(total_requests)]
        await asyncio.gather(*tasks)
        wall_time = time.monotonic() - start

    # Compute metrics
    statuses = [r[0] for r in results]
    latencies = [r[1] for r in results]
    success = sum(1 for s in statuses if 200 <= s < 400)
    errors = sum(1 for s in statuses if s == 0 or s >= 400)

    return {
        "url": url,
        "total_requests": total_requests,
        "concurrency": concurrency,
        "wall_time_s": round(wall_time, 2),
        "rps": round(total_requests / wall_time, 1),
        "success": success,
        "errors": errors,
        "success_rate": round(success / total_requests * 100, 1),
        "latency_min_ms": round(min(latencies), 1),
        "latency_max_ms": round(max(latencies), 1),
        "latency_mean_ms": round(statistics.mean(latencies), 1),
        "latency_median_ms": round(statistics.median(latencies), 1),
        "latency_p95_ms": round(sorted(latencies)[int(len(latencies) * 0.95)], 1),
        "latency_p99_ms": round(sorted(latencies)[int(len(latencies) * 0.99)], 1),
    }


def print_report(metrics: dict) -> None:
    """Pretty-print load test results."""
    OK if metrics["success_rate"] >= 99 else (WARN if metrics["success_rate"] >= 95 else FAIL)


async def main() -> None:
    parser = argparse.ArgumentParser(description="API Load Tester")
    parser.add_argument("--url", type=str, help="Target URL")
    parser.add_argument("--targets", type=str, help="'all' to test kovelai + shadowtagai")
    parser.add_argument("--concurrency", type=int, default=10, help="Concurrent connections")
    parser.add_argument("--requests", type=int, default=50, help="Total requests")
    args = parser.parse_args()

    urls = []
    if args.targets == "all":
        urls = list(TARGETS.values())
    elif args.url:
        urls = [args.url]
    else:
        urls = list(TARGETS.values())

    for url in urls:
        metrics = await run_load_test(url, args.concurrency, args.requests)
        print_report(metrics)


if __name__ == "__main__":
    asyncio.run(main())
