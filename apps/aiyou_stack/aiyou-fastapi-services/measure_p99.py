import asyncio
import os
import statistics
import time

import httpx


async def measure_p99(url: str, requests_count: int = 100):
    print(f"///▞ BENCHMARKING :: Target {url} :: Count {requests_count}")

    latencies = []
    async with httpx.AsyncClient() as client:
        for i in range(requests_count):
            start = time.time()
            try:
                # We hit the health endpoint which triggers DB/Cache checks
                await client.get(f"{url}/status")
                latencies.append((time.time() - start) * 1000)
                if i % 10 == 0:
                    print(f"Sample {i}: {latencies[-1]:.2f}ms")
            except Exception as e:
                print(f"Request {i} failed: {e}")

    if not latencies:
        print("❌ All requests failed.")
        return

    p50 = statistics.median(latencies)
    p95 = statistics.quantiles(latencies, n=20)[18]  # 95th percentile
    p99 = statistics.quantiles(latencies, n=100)[98]  # 99th percentile
    avg = sum(latencies) / len(latencies)

    print("\n" + "=" * 40)
    print("///▞ SLA REPORT :: ShadowTagAI")
    print("=" * 40)
    print(f"Avg Latency: {avg:.2f}ms")
    print(f"p50 Latency: {p50:.2f}ms")
    print(f"p95 Latency: {p95:.2f}ms")
    print(f"p99 Latency: {p99:.2f}ms")
    print("=" * 40)

    if p99 <= 90:
        print("✅ SLA MET: p99 ≤ 90ms")
    else:
        print("⚠️ SLA VIOLATED: p99 > 90ms")
    print("=" * 40)


if __name__ == "__main__":
    target_url = os.getenv("API_URL", "http://localhost:8000")
    asyncio.run(measure_p99(target_url))
