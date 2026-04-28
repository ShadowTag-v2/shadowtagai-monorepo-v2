#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Corrected Async Latency Validator for Judge6 Service

CRITICAL FIXES APPLIED:
1. Changed from ThreadPoolExecutor to async/await with httpx
2. Added proper request timeouts (connect and read)
3. Added session/connection reuse for better performance
4. Fixed result collection to use asyncio.gather
5. Added guard against empty latency samples
6. Improved error handling and reporting
7. Added retry logic for transient failures
8. Added percentile calculations with edge case handling

IMPROVEMENTS:
- Uses httpx.AsyncClient for high concurrency
- Connection pooling and reuse
- Semaphore for controlled concurrency
- Detailed error categorization
- Progress reporting
- Summary statistics (p50, p95, p99, max, min)
"""

import asyncio
import logging
import sys
import time
from dataclasses import dataclass, field
from enum import Enum

try:
    import httpx
    import numpy as np
except ImportError:
    print("ERROR: Missing required packages. Install with:")
    print("pip install httpx numpy")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class ErrorType(Enum):
    """Error categorization"""

    TIMEOUT = "timeout"
    CONNECTION = "connection"
    HTTP_ERROR = "http_error"
    INVALID_RESPONSE = "invalid_response"
    UNKNOWN = "unknown"


@dataclass
class ValidationConfig:
    """Configuration for latency validation"""

    endpoint: str = "https://judge6.shadowtagai.ai/enforce"
    iterations: int = 1000
    concurrency: int = 50
    connect_timeout: float = 5.0
    read_timeout: float = 10.0
    retry_attempts: int = 2
    retry_delay: float = 0.1
    p99_threshold_ms: float = 50.0
    error_rate_threshold: float = 0.05


@dataclass
class LatencyResult:
    """Single request result"""

    latency_ms: float | None = None
    status_code: int | None = None
    error: str | None = None
    error_type: ErrorType | None = None
    retries: int = 0


@dataclass
class ValidationReport:
    """Validation results summary"""

    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    error_breakdown: dict[str, int] = field(default_factory=dict)
    latencies_ms: list[float] = field(default_factory=list)
    p50: float | None = None
    p95: float | None = None
    p99: float | None = None
    min: float | None = None
    max: float | None = None
    mean: float | None = None
    success_rate: float = 0.0
    error_rate: float = 0.0
    p99_pass: bool = False
    error_rate_pass: bool = False
    duration_seconds: float = 0.0


class LatencyValidator:
    """Async latency validator using httpx"""

    def __init__(self, config: ValidationConfig):
        self.config = config
        self.semaphore = asyncio.Semaphore(config.concurrency)
        self.results: list[LatencyResult] = []

    async def validate(self) -> ValidationReport:
        """Run latency validation"""
        logger.info("=" * 60)
        logger.info("Starting latency validation")
        logger.info(f"Endpoint: {self.config.endpoint}")
        logger.info(f"Total requests: {self.config.iterations}")
        logger.info(f"Concurrency: {self.config.concurrency}")
        logger.info(f"P99 threshold: {self.config.p99_threshold_ms}ms")
        logger.info("=" * 60)

        start_time = time.perf_counter()

        # Create async client with connection pooling
        timeout = httpx.Timeout(
            connect=self.config.connect_timeout,
            read=self.config.read_timeout,
            write=5.0,
            pool=5.0,
        )

        limits = httpx.Limits(
            max_connections=self.config.concurrency * 2,
            max_keepalive_connections=self.config.concurrency,
        )

        async with httpx.AsyncClient(
            timeout=timeout,
            limits=limits,
            http2=True,  # Enable HTTP/2 for better performance
        ) as client:
            # Create tasks
            tasks = [self._make_request(client, i) for i in range(self.config.iterations)]

            # Run with progress reporting
            await self._run_with_progress(tasks)

        duration = time.perf_counter() - start_time

        # Generate report
        report = self._generate_report(duration)
        self._print_report(report)

        return report

    async def _run_with_progress(self, tasks: list):
        """Run tasks with progress reporting"""
        completed = 0
        report_interval = max(1, self.config.iterations // 10)  # Report every 10%

        for coro in asyncio.as_completed(tasks):
            await coro
            completed += 1  # noqa: SIM113

            if completed % report_interval == 0:
                logger.info(
                    f"Progress: {completed}/{self.config.iterations} "
                    f"({100 * completed // self.config.iterations}%)",
                )

    async def _make_request(self, client: httpx.AsyncClient, request_id: int) -> LatencyResult:
        """Make a single request with retry logic"""
        async with self.semaphore:  # Control concurrency
            for attempt in range(self.config.retry_attempts + 1):
                result = await self._try_request(client, request_id, attempt)

                # Return immediately on success
                if result.latency_ms is not None:
                    self.results.append(result)
                    return result

                # Retry on transient errors
                if attempt < self.config.retry_attempts:
                    await asyncio.sleep(self.config.retry_delay * (2**attempt))
                    result.retries += 1

            # All retries exhausted
            self.results.append(result)
            return result

    async def _try_request(
        self,
        client: httpx.AsyncClient,
        request_id: int,
        attempt: int,
    ) -> LatencyResult:
        """Try a single request (single attempt)"""
        result = LatencyResult()
        payload = self._build_payload(request_id)

        try:
            start = time.perf_counter()

            response = await client.post(
                self.config.endpoint,
                json=payload,
            )

            latency_ms = (time.perf_counter() - start) * 1000

            # Record successful request
            result.latency_ms = latency_ms
            result.status_code = response.status_code

            # Check for HTTP errors
            if response.status_code != 200:
                result.error = f"HTTP {response.status_code}"
                result.error_type = ErrorType.HTTP_ERROR
                result.latency_ms = None  # Don't count error latencies

            return result

        except httpx.TimeoutException as e:
            result.error = f"Timeout: {e!s}"
            result.error_type = ErrorType.TIMEOUT
            return result

        except httpx.ConnectError as e:
            result.error = f"Connection error: {e!s}"
            result.error_type = ErrorType.CONNECTION
            return result

        except httpx.HTTPError as e:
            result.error = f"HTTP error: {e!s}"
            result.error_type = ErrorType.HTTP_ERROR
            return result

        except Exception as e:
            result.error = f"Unknown error: {e!s}"
            result.error_type = ErrorType.UNKNOWN
            return result

    def _build_payload(self, request_id: int) -> dict:
        """Build request payload"""
        return {
            "request_id": f"val-{request_id}",
            "model": "judge6-gemini",
            "prompt": "Validate this request for ATP519 compliance.",
            "max_tokens": 100,
            "temperature": 0.0,
            "metadata": {"validation_run": True, "timestamp": time.time()},
        }

    def _generate_report(self, duration: float) -> ValidationReport:
        """Generate validation report from results"""
        report = ValidationReport()
        report.total_requests = len(self.results)
        report.duration_seconds = duration

        # Collect successful latencies
        latencies = []
        error_counts: dict[str, int] = {}

        for result in self.results:
            if result.latency_ms is not None:
                latencies.append(result.latency_ms)
                report.successful_requests += 1
            else:
                report.failed_requests += 1
                error_type = result.error_type.value if result.error_type else "unknown"
                error_counts[error_type] = error_counts.get(error_type, 0) + 1

        report.latencies_ms = latencies
        report.error_breakdown = error_counts

        # Calculate metrics
        if latencies:
            report.p50 = float(np.percentile(latencies, 50))
            report.p95 = float(np.percentile(latencies, 95))
            report.p99 = float(np.percentile(latencies, 99))
            report.min = float(np.min(latencies))
            report.max = float(np.max(latencies))
            report.mean = float(np.mean(latencies))
        else:
            logger.warning("No successful requests - cannot compute percentiles")

        # Calculate rates
        if report.total_requests > 0:
            report.success_rate = report.successful_requests / report.total_requests
            report.error_rate = report.failed_requests / report.total_requests

        # Validate thresholds
        if report.p99 is not None:
            report.p99_pass = report.p99 <= self.config.p99_threshold_ms
        report.error_rate_pass = report.error_rate <= self.config.error_rate_threshold

        return report

    def _print_report(self, report: ValidationReport):
        """Print validation report"""
        logger.info("\n" + "=" * 60)
        logger.info("VALIDATION REPORT")
        logger.info("=" * 60)

        logger.info("\nRequests:")
        logger.info(f"  Total:      {report.total_requests}")
        logger.info(
            f"  Successful: {report.successful_requests} ({report.success_rate * 100:.2f}%)",
        )
        logger.info(f"  Failed:     {report.failed_requests} ({report.error_rate * 100:.2f}%)")

        if report.error_breakdown:
            logger.info("\nError Breakdown:")
            for error_type, count in sorted(report.error_breakdown.items()):
                pct = (count / report.total_requests) * 100
                logger.info(f"  {error_type:20s}: {count:4d} ({pct:5.2f}%)")

        if report.latencies_ms:
            logger.info("\nLatency Statistics:")
            logger.info(f"  Min:  {report.min:7.2f} ms")
            logger.info(f"  Mean: {report.mean:7.2f} ms")
            logger.info(f"  P50:  {report.p50:7.2f} ms")
            logger.info(f"  P95:  {report.p95:7.2f} ms")
            logger.info(f"  P99:  {report.p99:7.2f} ms")
            logger.info(f"  Max:  {report.max:7.2f} ms")

        logger.info("\nPerformance:")
        logger.info(f"  Duration:   {report.duration_seconds:.2f}s")
        logger.info(f"  Throughput: {report.total_requests / report.duration_seconds:.2f} req/s")

        logger.info("\nValidation Results:")
        p99_status = "✓ PASS" if report.p99_pass else "✗ FAIL"
        err_status = "✓ PASS" if report.error_rate_pass else "✗ FAIL"

        logger.info(
            f"  P99 < {self.config.p99_threshold_ms}ms:  {p99_status} (actual: {report.p99:.2f}ms)"
            if report.p99
            else "  P99: N/A (no successful requests)",
        )
        logger.info(
            f"  Error rate < {self.config.error_rate_threshold * 100}%: {err_status} "
            f"(actual: {report.error_rate * 100:.2f}%)",
        )

        logger.info("=" * 60)

        # Overall pass/fail
        overall_pass = report.p99_pass and report.error_rate_pass
        if overall_pass:
            logger.info("✓ VALIDATION PASSED")
        else:
            logger.error("✗ VALIDATION FAILED")

        logger.info("=" * 60 + "\n")


async def main():
    """Main execution"""
    # Configuration
    config = ValidationConfig(
        endpoint="https://judge6.shadowtagai.ai/enforce",
        iterations=1000,
        concurrency=50,
        connect_timeout=5.0,
        read_timeout=10.0,
        p99_threshold_ms=50.0,
        error_rate_threshold=0.05,
    )

    # Run validation
    validator = LatencyValidator(config)
    report = await validator.validate()

    # Exit with appropriate code
    overall_pass = report.p99_pass and report.error_rate_pass
    sys.exit(0 if overall_pass else 1)


if __name__ == "__main__":
    asyncio.run(main())
