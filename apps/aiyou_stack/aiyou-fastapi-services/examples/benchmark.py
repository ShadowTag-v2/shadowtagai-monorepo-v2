# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Benchmark script for ShadowTag-v2 LLM serving.

Tests throughput, latency, and GPU utilization under various loads.
"""

import asyncio
import statistics
import time
from dataclasses import dataclass

import httpx


@dataclass
class BenchmarkResult:
    """Results from a benchmark run."""

    total_requests: int
    successful_requests: int
    failed_requests: int
    total_time_seconds: float
    requests_per_second: float
    avg_latency_ms: float
    p50_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    total_tokens: int
    tokens_per_second: float


class LLMBenchmark:
    """Benchmark harness for LLM serving."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=120.0)

    async def run_single_request(self, prompt: str, max_tokens: int = 100) -> dict:
        """Run a single request and return timing info."""
        start = time.time()

        try:
            response = await self.client.post(
                f"{self.base_url}/v1/completions",
                json={
                    "prompt": prompt,
                    "max_tokens": max_tokens,
                    "routing_strategy": "token_aware",
                },
            )
            response.raise_for_status()
            result = response.json()

            elapsed = (time.time() - start) * 1000

            return {
                "success": True,
                "latency_ms": elapsed,
                "tokens": result["tokens"],
                "model": result["model"],
            }

        except Exception as e:
            elapsed = (time.time() - start) * 1000
            return {
                "success": False,
                "latency_ms": elapsed,
                "error": str(e),
            }

    async def benchmark_throughput(
        self,
        num_requests: int = 100,
        concurrency: int = 10,
        prompt: str = "Explain how vLLM achieves high throughput:",
        max_tokens: int = 100,
    ) -> BenchmarkResult:
        """Benchmark request throughput.

        Args:
            num_requests: Total requests to send
            concurrency: Number of concurrent requests
            prompt: Prompt to use
            max_tokens: Tokens to generate per request

        """
        print("\n=== Throughput Benchmark ===")
        print(f"Requests: {num_requests}, Concurrency: {concurrency}")

        latencies = []
        tokens = []
        successes = 0
        failures = 0

        start_time = time.time()

        # Run requests in batches
        for i in range(0, num_requests, concurrency):
            batch_size = min(concurrency, num_requests - i)

            tasks = [self.run_single_request(prompt, max_tokens) for _ in range(batch_size)]

            results = await asyncio.gather(*tasks)

            for result in results:
                if result["success"]:
                    successes += 1
                    latencies.append(result["latency_ms"])
                    tokens.append(result["tokens"])
                else:
                    failures += 1

            # Progress
            completed = i + batch_size
            print(f"Progress: {completed}/{num_requests} ({completed / num_requests * 100:.1f}%)")

        total_time = time.time() - start_time

        # Calculate statistics
        if latencies:
            avg_latency = statistics.mean(latencies)
            p50_latency = statistics.median(latencies)
            sorted_latencies = sorted(latencies)
            p95_latency = sorted_latencies[int(len(sorted_latencies) * 0.95)]
            p99_latency = sorted_latencies[int(len(sorted_latencies) * 0.99)]
        else:
            avg_latency = p50_latency = p95_latency = p99_latency = 0

        total_tokens = sum(tokens)
        requests_per_second = successes / total_time if total_time > 0 else 0
        tokens_per_second = total_tokens / total_time if total_time > 0 else 0

        return BenchmarkResult(
            total_requests=num_requests,
            successful_requests=successes,
            failed_requests=failures,
            total_time_seconds=total_time,
            requests_per_second=requests_per_second,
            avg_latency_ms=avg_latency,
            p50_latency_ms=p50_latency,
            p95_latency_ms=p95_latency,
            p99_latency_ms=p99_latency,
            total_tokens=total_tokens,
            tokens_per_second=tokens_per_second,
        )

    def print_results(self, result: BenchmarkResult):
        """Print benchmark results."""
        print("\n=== Results ===")
        print(f"Total requests: {result.total_requests}")
        print(f"Successful: {result.successful_requests}")
        print(f"Failed: {result.failed_requests}")
        print(f"Success rate: {result.successful_requests / result.total_requests * 100:.2f}%")
        print("\nTiming:")
        print(f"Total time: {result.total_time_seconds:.2f}s")
        print(f"Requests/sec: {result.requests_per_second:.2f}")
        print("\nLatency:")
        print(f"Average: {result.avg_latency_ms:.2f}ms")
        print(f"P50: {result.p50_latency_ms:.2f}ms")
        print(f"P95: {result.p95_latency_ms:.2f}ms")
        print(f"P99: {result.p99_latency_ms:.2f}ms")
        print("\nTokens:")
        print(f"Total tokens: {result.total_tokens}")
        print(f"Tokens/sec: {result.tokens_per_second:.2f}")

    async def close(self):
        """Close the client."""
        await self.client.aclose()


async def main():
    """Run benchmarks."""
    print("=" * 60)
    print("ShadowTag-v2 LLM Serving Benchmark")
    print("Testing Aegaeon-style multi-model pooling performance")
    print("=" * 60)

    benchmark = LLMBenchmark()

    try:
        # Test 1: Low concurrency
        print("\nTest 1: Low concurrency (baseline)")
        result1 = await benchmark.benchmark_throughput(
            num_requests=50,
            concurrency=1,
            max_tokens=100,
        )
        benchmark.print_results(result1)

        # Test 2: Medium concurrency
        print("\n" + "=" * 60)
        print("\nTest 2: Medium concurrency")
        result2 = await benchmark.benchmark_throughput(
            num_requests=100,
            concurrency=5,
            max_tokens=100,
        )
        benchmark.print_results(result2)

        # Test 3: High concurrency (stress test)
        print("\n" + "=" * 60)
        print("\nTest 3: High concurrency (stress test)")
        result3 = await benchmark.benchmark_throughput(
            num_requests=200,
            concurrency=20,
            max_tokens=100,
        )
        benchmark.print_results(result3)

        # Summary comparison
        print("\n" + "=" * 60)
        print("\n=== Comparison ===")
        print(f"{'Test':<20} {'RPS':<15} {'P95 Latency':<15} {'Tokens/sec':<15}")
        print("-" * 60)
        print(
            f"{'Low (1)':<20} {result1.requests_per_second:<15.2f} {result1.p95_latency_ms:<15.2f} {result1.tokens_per_second:<15.2f}",
        )
        print(
            f"{'Medium (5)':<20} {result2.requests_per_second:<15.2f} {result2.p95_latency_ms:<15.2f} {result2.tokens_per_second:<15.2f}",
        )
        print(
            f"{'High (20)':<20} {result3.requests_per_second:<15.2f} {result3.p95_latency_ms:<15.2f} {result3.tokens_per_second:<15.2f}",
        )

        # Speedup analysis
        speedup = result3.requests_per_second / result1.requests_per_second
        print(f"\nSpeedup (High/Low): {speedup:.2f}x")

        if speedup > 1.5:
            print("✓ Good scaling with concurrency!")
        else:
            print("⚠ Limited scaling - check GPU utilization")

    finally:
        await benchmark.close()

    print("\n" + "=" * 60)
    print("Benchmark complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
