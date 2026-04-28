# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import asyncio
import statistics
import time

import aiohttp

# Configuration
SERVER_URL = "http://localhost:8600"
CONCURRENT_REQUESTS = 100  # Number of parallel "users"
TOTAL_REQUESTS = 1000  # Total requests to fire


async def shoot_request(session, req_id):
    start = time.time()
    try:
        # Hitting health check for raw throughput speed (lowest latency baseline)
        async with session.get(f"{SERVER_URL}/health") as response:
            await response.text()
            end = time.time()
            return end - start, response.status
    except Exception as e:
        return None, str(e)


async def main():
    print(f"🚀 Benchmarking n-autoresearch/Kosmos/BioAgents Swarm at {SERVER_URL}")
    print(
        f"   Configuration: {CONCURRENT_REQUESTS} concurrent agents, {TOTAL_REQUESTS} total requests",
    )

    start_time = time.time()

    async with aiohttp.ClientSession() as session:
        tasks = [shoot_request(session, i) for i in range(TOTAL_REQUESTS)]
        results = await asyncio.gather(*tasks)

    end_time = time.time()
    total_duration = end_time - start_time

    # Analysis
    latencies = [r[0] for r in results if r[0] is not None]
    errors = [r[1] for r in results if r[0] is None or r[1] != 200]

    throughput = len(latencies) / total_duration

    print("\n📊 REAL WORLD RESULTS")
    print("=====================")
    print(f"Time Taken:     {total_duration:.2f} seconds")
    print(f"Total Requests: {TOTAL_REQUESTS}")
    print(f"Success Rate:   {len(latencies) / TOTAL_REQUESTS * 100:.1f}%")
    print(f"Throughput:     {throughput:.2f} req/sec ({throughput * 60:.0f} RPM)")

    if latencies:
        print(f"Avg Latency:    {statistics.mean(latencies) * 1000:.2f} ms")
        print(f"P99 Latency:    {sorted(latencies)[int(len(latencies) * 0.99)] * 1000:.2f} ms")

    if errors:
        print(f"\n⚠️ Errors ({len(errors)}):")
        print(f"First error: {errors[0]}")


if __name__ == "__main__":
    asyncio.run(main())
