#!/usr/bin/env python3
"""
PNKLN Judge #6 Latency Validation Harness

Tests p99 latency against 90ms SLA target.
Generates detailed reports with percentile breakdowns.

Usage:
    python test_latency.py --endpoint http://judge6.pnkln.svc.cluster.local --p99-target-ms 90
"""

import argparse
import asyncio
import json
import statistics
import time
from dataclasses import asdict, dataclass
from datetime import datetime

try:
    import aiohttp
    import numpy as np
    from tabulate import tabulate
    from tqdm import tqdm
except ImportError:
    print("ERROR: Missing dependencies. Run: pip install -r requirements.txt")
    exit(1)


@dataclass
class LatencyResult:
    """Single inference request result"""

    request_id: int
    latency_ms: float
    success: bool
    error: str = None
    timestamp: float = None
    status_code: int = None


@dataclass
class LatencyReport:
    """Comprehensive latency test report"""

    total_requests: int
    successful_requests: int
    failed_requests: int
    success_rate: float

    # Latency percentiles (ms)
    p50: float
    p90: float
    p95: float
    p99: float
    p99_9: float
    min: float
    max: float
    mean: float
    median: float
    stddev: float

    # SLA validation
    sla_target_ms: float
    sla_pass: bool
    sla_margin_ms: float

    # Throughput
    duration_seconds: float
    qps: float

    # Metadata
    test_timestamp: str
    endpoint: str


class LatencyTester:
    """Asynchronous latency testing harness"""

    def __init__(self, endpoint: str, api_key: str = None):
        self.endpoint = endpoint.rstrip("/")
        self.api_key = api_key
        self.results: list[LatencyResult] = []

    async def send_request(
        self, session: aiohttp.ClientSession, request_id: int, prompt: str, timeout: float = 30.0
    ) -> LatencyResult:
        """Send single inference request and measure latency"""

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload = {
            "model": "pnkln-judge6-v1",
            "prompt": prompt,
            "max_tokens": 100,
            "temperature": 0.7,
            "stream": False,
        }

        start_time = time.time()

        try:
            async with session.post(
                f"{self.endpoint}/v1/completions",
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=timeout),
            ) as response:
                await response.read()
                latency_ms = (time.time() - start_time) * 1000

                return LatencyResult(
                    request_id=request_id,
                    latency_ms=latency_ms,
                    success=response.status == 200,
                    status_code=response.status,
                    timestamp=start_time,
                )

        except TimeoutError:
            return LatencyResult(
                request_id=request_id,
                latency_ms=(time.time() - start_time) * 1000,
                success=False,
                error="Timeout",
                timestamp=start_time,
            )
        except Exception as e:
            return LatencyResult(
                request_id=request_id,
                latency_ms=(time.time() - start_time) * 1000,
                success=False,
                error=str(e),
                timestamp=start_time,
            )

    async def run_test(
        self, num_requests: int = 100, concurrency: int = 10, prompt: str = None
    ) -> list[LatencyResult]:
        """Run concurrent latency test"""

        if prompt is None:
            prompt = "Analyze the following code for security vulnerabilities: def login(user, pwd): exec(f'SELECT * FROM users WHERE name={user}')"

        print("\n🔬 Starting latency test...")
        print(f"   Endpoint: {self.endpoint}")
        print(f"   Requests: {num_requests}")
        print(f"   Concurrency: {concurrency}")
        print(f"   Prompt length: {len(prompt)} chars\n")

        connector = aiohttp.TCPConnector(limit=concurrency)
        async with aiohttp.ClientSession(connector=connector) as session:
            # Warm-up request
            print("⏳ Warming up endpoint...")
            await self.send_request(session, 0, prompt)

            # Main test
            print(f"🚀 Running {num_requests} requests...\n")

            tasks = []
            for i in range(num_requests):
                tasks.append(self.send_request(session, i + 1, prompt))

            # Execute with progress bar
            results = []
            for coro in tqdm(
                asyncio.as_completed(tasks), total=num_requests, desc="Requests", unit="req"
            ):
                result = await coro
                results.append(result)

            self.results = results
            return results

    def generate_report(self, sla_target_ms: float = 90.0) -> LatencyReport:
        """Generate comprehensive latency report"""

        if not self.results:
            raise ValueError("No test results available. Run test first.")

        successful = [r for r in self.results if r.success]
        failed = [r for r in self.results if not r.success]

        if not successful:
            raise ValueError("All requests failed. Cannot generate latency report.")

        latencies = [r.latency_ms for r in successful]

        # Calculate percentiles
        p50 = np.percentile(latencies, 50)
        p90 = np.percentile(latencies, 90)
        p95 = np.percentile(latencies, 95)
        p99 = np.percentile(latencies, 99)
        p99_9 = np.percentile(latencies, 99.9)

        # Calculate statistics
        min_latency = min(latencies)
        max_latency = max(latencies)
        mean_latency = statistics.mean(latencies)
        median_latency = statistics.median(latencies)
        stddev = statistics.stdev(latencies) if len(latencies) > 1 else 0

        # Calculate throughput
        timestamps = [r.timestamp for r in self.results if r.timestamp]
        duration = max(timestamps) - min(timestamps) if timestamps else 0
        qps = len(successful) / duration if duration > 0 else 0

        # SLA validation
        sla_pass = p99 <= sla_target_ms
        sla_margin = sla_target_ms - p99

        return LatencyReport(
            total_requests=len(self.results),
            successful_requests=len(successful),
            failed_requests=len(failed),
            success_rate=len(successful) / len(self.results) * 100,
            p50=p50,
            p90=p90,
            p95=p95,
            p99=p99,
            p99_9=p99_9,
            min=min_latency,
            max=max_latency,
            mean=mean_latency,
            median=median_latency,
            stddev=stddev,
            sla_target_ms=sla_target_ms,
            sla_pass=sla_pass,
            sla_margin_ms=sla_margin,
            duration_seconds=duration,
            qps=qps,
            test_timestamp=datetime.now().isoformat(),
            endpoint=self.endpoint,
        )

    def print_report(self, report: LatencyReport):
        """Print formatted report to console"""

        print("\n" + "=" * 70)
        print("📊 LATENCY TEST REPORT")
        print("=" * 70)

        # Basic info
        print(f"\n🎯 Target: p99 ≤ {report.sla_target_ms}ms")
        print(f"📍 Endpoint: {report.endpoint}")
        print(f"🕒 Timestamp: {report.test_timestamp}")

        # Request summary
        print("\n📦 Requests:")
        summary_table = [
            ["Total", report.total_requests],
            ["Successful", f"{report.successful_requests} ({report.success_rate:.1f}%)"],
            ["Failed", report.failed_requests],
            ["Duration", f"{report.duration_seconds:.2f}s"],
            ["Throughput", f"{report.qps:.2f} QPS"],
        ]
        print(tabulate(summary_table, tablefmt="simple"))

        # Latency percentiles
        print("\n📈 Latency Percentiles (ms):")
        percentile_table = [
            ["Min", f"{report.min:.2f}"],
            ["p50 (Median)", f"{report.p50:.2f}"],
            ["p90", f"{report.p90:.2f}"],
            ["p95", f"{report.p95:.2f}"],
            ["p99", f"{report.p99:.2f}"],
            ["p99.9", f"{report.p99_9:.2f}"],
            ["Max", f"{report.max:.2f}"],
            ["Mean", f"{report.mean:.2f}"],
            ["Std Dev", f"{report.stddev:.2f}"],
        ]
        print(tabulate(percentile_table, tablefmt="simple"))

        # SLA validation
        print("\n🎯 SLA Validation:")
        sla_status = "✅ PASS" if report.sla_pass else "❌ FAIL"
        sla_table = [
            ["Target", f"p99 ≤ {report.sla_target_ms}ms"],
            ["Actual", f"p99 = {report.p99:.2f}ms"],
            ["Margin", f"{report.sla_margin_ms:+.2f}ms"],
            ["Status", sla_status],
        ]
        print(tabulate(sla_table, tablefmt="simple"))

        # Recommendations
        print("\n💡 Recommendations:")
        if report.sla_pass:
            print("   ✅ SLA target met!")
            if report.sla_margin_ms > 20:
                print(f"   ✨ Excellent margin: {report.sla_margin_ms:.1f}ms headroom")
            elif report.sla_margin_ms > 10:
                print(f"   👍 Good margin: {report.sla_margin_ms:.1f}ms headroom")
            else:
                print(f"   ⚠️  Tight margin: {report.sla_margin_ms:.1f}ms headroom")
                print("   → Consider optimizations to improve stability")
        else:
            print(f"   ❌ SLA violated by {abs(report.sla_margin_ms):.1f}ms")
            print("\n   🔧 Optimization suggestions:")
            print("      1. Enable Flash Attention (if not already enabled)")
            print("      2. Try AWQ quantization for faster inference")
            print("      3. Reduce batch size or max_tokens")
            print("      4. Use H100 GPU instead of L4")
            print("      5. Check for CPU/memory bottlenecks")

        if report.failed_requests > 0:
            fail_rate = (report.failed_requests / report.total_requests) * 100
            print(f"\n   ⚠️  {fail_rate:.1f}% failure rate detected")
            print("      → Check pod logs and resource limits")

        print("\n" + "=" * 70 + "\n")

    def save_report(self, report: LatencyReport, filename: str = None):
        """Save report to JSON file"""

        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"latency_report_{timestamp}.json"

        with open(filename, "w") as f:
            json.dump(asdict(report), f, indent=2)

        print(f"💾 Report saved to: {filename}")


async def main():
    parser = argparse.ArgumentParser(description="PNKLN Judge #6 Latency Validation Harness")
    parser.add_argument(
        "--endpoint", default="http://judge6.pnkln.svc.cluster.local", help="Inference endpoint URL"
    )
    parser.add_argument(
        "--p99-target-ms",
        type=float,
        default=90.0,
        help="p99 latency SLA target in milliseconds (default: 90)",
    )
    parser.add_argument(
        "--num-requests", type=int, default=100, help="Number of requests to send (default: 100)"
    )
    parser.add_argument(
        "--concurrency", type=int, default=10, help="Concurrent requests (default: 10)"
    )
    parser.add_argument("--api-key", default=None, help="API key for authentication (optional)")
    parser.add_argument("--prompt", default=None, help="Custom prompt for testing (optional)")
    parser.add_argument("--output", default=None, help="Output JSON file for results (optional)")

    args = parser.parse_args()

    # Create tester
    tester = LatencyTester(endpoint=args.endpoint, api_key=args.api_key)

    # Run test
    time.time()
    await tester.run_test(
        num_requests=args.num_requests, concurrency=args.concurrency, prompt=args.prompt
    )

    # Generate and print report
    report = tester.generate_report(sla_target_ms=args.p99_target_ms)
    tester.print_report(report)

    # Save report
    if args.output:
        tester.save_report(report, args.output)

    # Exit code based on SLA
    exit_code = 0 if report.sla_pass else 1
    exit(exit_code)


if __name__ == "__main__":
    asyncio.run(main())
