#!/usr/bin/env python3
"""
Pnkln Judge #6 Synthetic Workload Generator
Purpose: Generate realistic request patterns to validate p99 ≤ 90ms SLA
"""

import asyncio
import json
import logging
import os
import random
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import aiohttp
import numpy as np

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class WorkloadConfig:
    """Configuration for workload generator"""

    judge_endpoint: str = os.getenv(
        "JUDGE_ENDPOINT", "http://judge-6-service.pnkln-core.svc.cluster.local"
    )
    duration_seconds: int = int(os.getenv("WORKLOAD_DURATION_SEC", "3600"))  # 1 hour default

    # Request rate configuration
    base_rps: float = float(os.getenv("BASE_RPS", "10"))
    peak_rps: float = float(os.getenv("PEAK_RPS", "50"))
    burst_rps: float = float(os.getenv("BURST_RPS", "100"))

    # Workload patterns
    enable_ramp_up: bool = True
    enable_steady_state: bool = True
    enable_burst_mode: bool = True
    enable_ramp_down: bool = True

    # Test scenarios
    scenarios: list[str] = field(
        default_factory=lambda: [
            "model_deployment",
            "data_access",
            "api_call",
            "admin_action",
            "batch_job",
        ]
    )

    # SLA tracking
    sla_p99_ms: float = 90.0
    sla_p95_ms: float = 60.0
    sla_p50_ms: float = 30.0

    # Output
    results_file: str = "validation_results.json"


@dataclass
class RequestResult:
    """Result of a single request"""

    request_id: str
    scenario: str
    timestamp: float
    duration_ms: float
    status_code: int
    decision: str
    error: str = ""


class SyntheticWorkloadGenerator:
    """Generates synthetic workload for Judge #6 validation"""

    def __init__(self, config: WorkloadConfig):
        self.config = config
        self.results: list[RequestResult] = []
        self.start_time = time.time()

    def _generate_request(self, scenario: str, request_id: str) -> dict[str, Any]:
        """Generate a synthetic request based on scenario"""
        base_request = {
            "id": request_id,
            "timestamp": datetime.utcnow().isoformat(),
            "scenario": scenario,
        }

        if scenario == "model_deployment":
            return {
                **base_request,
                "action": "deploy_model",
                "user": f"engineer_{random.randint(1, 20)}@pnkln.com",
                "resource": f"production/model-v{random.randint(1, 10)}",
                "metadata": {
                    "model_type": random.choice(["llm", "embedding", "classifier"]),
                    "size_gb": random.uniform(1.0, 50.0),
                    "gpu_required": random.choice([True, False]),
                },
            }

        elif scenario == "data_access":
            return {
                **base_request,
                "action": "access_data",
                "user": f"analyst_{random.randint(1, 50)}@pnkln.com",
                "resource": f"datasets/{random.choice(['pii', 'public', 'internal'])}/data_{random.randint(1, 100)}",
                "metadata": {
                    "access_type": random.choice(["read", "write", "delete"]),
                    "sensitivity": random.choice(["low", "medium", "high", "critical"]),
                },
            }

        elif scenario == "api_call":
            return {
                **base_request,
                "action": "api_call",
                "user": f"service_{random.randint(1, 30)}@pnkln.com",
                "resource": f"/api/v1/{random.choice(['inference', 'embedding', 'classification'])}",
                "metadata": {
                    "method": random.choice(["GET", "POST", "PUT"]),
                    "rate_limit": random.randint(100, 10000),
                },
            }

        elif scenario == "admin_action":
            return {
                **base_request,
                "action": random.choice(
                    ["create_user", "delete_user", "modify_policy", "grant_access"]
                ),
                "user": f"admin_{random.randint(1, 5)}@pnkln.com",
                "resource": f"system/{random.choice(['users', 'policies', 'roles'])}",
                "metadata": {"critical": True, "requires_approval": random.choice([True, False])},
            }

        elif scenario == "batch_job":
            return {
                **base_request,
                "action": "run_batch_job",
                "user": f"pipeline_{random.randint(1, 10)}@pnkln.com",
                "resource": f"jobs/{random.choice(['training', 'inference', 'etl'])}/job_{random.randint(1, 50)}",
                "metadata": {
                    "duration_hours": random.randint(1, 24),
                    "cost_estimate": random.uniform(10.0, 1000.0),
                    "priority": random.choice(["low", "normal", "high"]),
                },
            }

        return base_request

    async def _send_request(
        self, session: aiohttp.ClientSession, request_data: dict[str, Any]
    ) -> RequestResult:
        """Send a single request and measure latency"""
        request_id = request_data["id"]
        scenario = request_data["scenario"]
        start_time = time.time()

        try:
            async with session.post(
                f"{self.config.judge_endpoint}/judge",
                json=request_data,
                timeout=aiohttp.ClientTimeout(total=5.0),
            ) as response:
                response_data = await response.json()
                duration_ms = (time.time() - start_time) * 1000

                return RequestResult(
                    request_id=request_id,
                    scenario=scenario,
                    timestamp=start_time,
                    duration_ms=duration_ms,
                    status_code=response.status,
                    decision=response_data.get("decision", "UNKNOWN"),
                )

        except TimeoutError:
            duration_ms = (time.time() - start_time) * 1000
            return RequestResult(
                request_id=request_id,
                scenario=scenario,
                timestamp=start_time,
                duration_ms=duration_ms,
                status_code=504,
                decision="TIMEOUT",
                error="Request timeout",
            )

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            return RequestResult(
                request_id=request_id,
                scenario=scenario,
                timestamp=start_time,
                duration_ms=duration_ms,
                status_code=500,
                decision="ERROR",
                error=str(e),
            )

    async def _run_workload_phase(
        self, phase_name: str, duration_sec: int, target_rps: float, session: aiohttp.ClientSession
    ):
        """Run a workload phase with specified RPS"""
        logger.info(
            f"Starting phase: {phase_name} (duration={duration_sec}s, target_rps={target_rps})"
        )

        phase_start = time.time()
        request_count = 0

        while (time.time() - phase_start) < duration_sec:
            # Calculate how many requests to send in this second
            requests_per_interval = int(target_rps)
            interval = 1.0 / target_rps if target_rps > 0 else 1.0

            tasks = []
            for _ in range(requests_per_interval):
                request_count += 1
                scenario = random.choice(self.config.scenarios)
                request_id = f"{phase_name}-{request_count}"
                request_data = self._generate_request(scenario, request_id)

                task = self._send_request(session, request_data)
                tasks.append(task)

                # Small delay to spread requests
                await asyncio.sleep(interval)

            # Wait for all requests in this batch
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for result in results:
                if isinstance(result, RequestResult):
                    self.results.append(result)

            # Log progress every 10 seconds
            if request_count % (int(target_rps) * 10) == 0:
                elapsed = time.time() - phase_start
                logger.info(
                    f"Phase {phase_name}: {request_count} requests sent, {elapsed:.1f}s elapsed"
                )

        logger.info(f"Completed phase: {phase_name} ({request_count} requests)")

    async def run(self):
        """Run the complete workload validation"""
        logger.info("=" * 80)
        logger.info("PNKLN JUDGE #6 VALIDATION SPRINT - SYNTHETIC WORKLOAD")
        logger.info("=" * 80)
        logger.info(f"Target SLA: p99 ≤ {self.config.sla_p99_ms}ms")
        logger.info(f"Duration: {self.config.duration_seconds}s")
        logger.info(f"Endpoint: {self.config.judge_endpoint}")
        logger.info("=" * 80)

        async with aiohttp.ClientSession() as session:
            # Phase 1: Ramp-up (25% of duration)
            if self.config.enable_ramp_up:
                ramp_duration = int(self.config.duration_seconds * 0.25)
                await self._run_workload_phase(
                    "ramp-up", ramp_duration, self.config.base_rps, session
                )

            # Phase 2: Steady state (40% of duration)
            if self.config.enable_steady_state:
                steady_duration = int(self.config.duration_seconds * 0.40)
                await self._run_workload_phase(
                    "steady-state", steady_duration, self.config.peak_rps, session
                )

            # Phase 3: Burst mode (20% of duration)
            if self.config.enable_burst_mode:
                burst_duration = int(self.config.duration_seconds * 0.20)
                await self._run_workload_phase(
                    "burst", burst_duration, self.config.burst_rps, session
                )

            # Phase 4: Ramp-down (15% of duration)
            if self.config.enable_ramp_down:
                rampdown_duration = int(self.config.duration_seconds * 0.15)
                await self._run_workload_phase(
                    "ramp-down", rampdown_duration, self.config.base_rps, session
                )

        # Analyze results
        self._analyze_results()

    def _analyze_results(self):
        """Analyze workload results and check SLA compliance"""
        if not self.results:
            logger.error("No results to analyze!")
            return

        logger.info("=" * 80)
        logger.info("VALIDATION RESULTS")
        logger.info("=" * 80)

        # Extract latencies
        latencies = [r.duration_ms for r in self.results if r.status_code == 200]
        errors = [r for r in self.results if r.status_code != 200]

        if not latencies:
            logger.error("No successful requests!")
            return

        # Calculate percentiles
        p50 = np.percentile(latencies, 50)
        p95 = np.percentile(latencies, 95)
        p99 = np.percentile(latencies, 99)
        mean = np.mean(latencies)
        std = np.std(latencies)

        total_requests = len(self.results)
        successful_requests = len(latencies)
        error_rate = (len(errors) / total_requests) * 100 if total_requests > 0 else 0

        # Print summary
        logger.info(f"Total Requests: {total_requests}")
        logger.info(f"Successful: {successful_requests}")
        logger.info(f"Errors: {len(errors)} ({error_rate:.2f}%)")
        logger.info("")
        logger.info("Latency Statistics:")
        logger.info(f"  Mean: {mean:.2f}ms")
        logger.info(f"  Std Dev: {std:.2f}ms")
        logger.info(
            f"  p50: {p50:.2f}ms (SLA: ≤{self.config.sla_p50_ms}ms) {'✓' if p50 <= self.config.sla_p50_ms else '✗ BREACH'}"
        )
        logger.info(
            f"  p95: {p95:.2f}ms (SLA: ≤{self.config.sla_p95_ms}ms) {'✓' if p95 <= self.config.sla_p95_ms else '✗ BREACH'}"
        )
        logger.info(
            f"  p99: {p99:.2f}ms (SLA: ≤{self.config.sla_p99_ms}ms) {'✓' if p99 <= self.config.sla_p99_ms else '✗ BREACH'}"
        )
        logger.info("")

        # SLA verdict
        sla_compliant = p99 <= self.config.sla_p99_ms
        logger.info("=" * 80)
        if sla_compliant:
            logger.info("✓ SLA COMPLIANT - Proceed with architecture")
        else:
            logger.error("✗ SLA BREACH - KILL SWITCH ACTIVATED")
            logger.error("Recommendation: Abort fork, pivot to ground-up architecture")
        logger.info("=" * 80)

        # Save results
        self._save_results(p50, p95, p99, mean, std, error_rate, sla_compliant)

    def _save_results(self, p50, p95, p99, mean, std, error_rate, sla_compliant):
        """Save results to JSON file"""
        summary = {
            "timestamp": datetime.utcnow().isoformat(),
            "config": {
                "duration_seconds": self.config.duration_seconds,
                "base_rps": self.config.base_rps,
                "peak_rps": self.config.peak_rps,
                "burst_rps": self.config.burst_rps,
            },
            "sla": {
                "p50_target_ms": self.config.sla_p50_ms,
                "p95_target_ms": self.config.sla_p95_ms,
                "p99_target_ms": self.config.sla_p99_ms,
            },
            "results": {
                "total_requests": len(self.results),
                "successful_requests": len([r for r in self.results if r.status_code == 200]),
                "error_rate_percent": error_rate,
                "latency_mean_ms": mean,
                "latency_std_ms": std,
                "latency_p50_ms": p50,
                "latency_p95_ms": p95,
                "latency_p99_ms": p99,
            },
            "sla_compliance": {
                "p50_compliant": p50 <= self.config.sla_p50_ms,
                "p95_compliant": p95 <= self.config.sla_p95_ms,
                "p99_compliant": p99 <= self.config.sla_p99_ms,
                "overall_compliant": sla_compliant,
            },
            "recommendation": "PROCEED" if sla_compliant else "ABORT - KILL SWITCH",
        }

        with open(self.config.results_file, "w") as f:
            json.dump(summary, f, indent=2)

        logger.info(f"Results saved to: {self.config.results_file}")


async def main():
    """Main entry point"""
    config = WorkloadConfig()
    generator = SyntheticWorkloadGenerator(config)
    await generator.run()


if __name__ == "__main__":
    asyncio.run(main())
