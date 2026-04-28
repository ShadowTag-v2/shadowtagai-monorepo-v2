#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Locust-based load testing for PNKLN inference endpoint

Usage:
    # Web UI mode
    locust -f load_test.py --host=http://your-endpoint

    # Headless mode
    locust -f load_test.py --host=http://your-endpoint \
        --users 100 --spawn-rate 10 --run-time 5m --headless
"""

import logging

from locust import HttpUser, between, events, task

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Track p99 latency
latencies = []


@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, **kwargs):
    """Track all request latencies"""
    if exception is None:
        latencies.append(response_time)


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Print p99 latency at test end"""
    if latencies:
        sorted_latencies = sorted(latencies)
        p99_index = int(len(sorted_latencies) * 0.99)
        p99_latency = sorted_latencies[p99_index]

        logger.info("=" * 60)
        logger.info(f"P99 Latency: {p99_latency:.2f}ms")
        logger.info(f"Total requests: {len(latencies)}")

        # Check SLA
        sla_target = 90  # ms
        if p99_latency <= sla_target:
            logger.info(f"✓ SLA PASSED (target: {sla_target}ms)")
        else:
            logger.warning(f"✗ SLA FAILED (target: {sla_target}ms)")

        logger.info("=" * 60)


class InferenceUser(HttpUser):
    """Simulated user making inference requests"""

    # Wait between 0.5 and 2 seconds between requests
    wait_time = between(0.5, 2)

    @task(10)
    def infer(self):
        """Make inference request"""
        payload = {"prompt": "Test prompt for load testing", "max_tokens": 100, "temperature": 0.7}

        with self.client.post(
            "/infer",
            json=payload,
            catch_response=True,
            name="inference",
        ) as response:
            if response.status_code == 200:
                # Check if latency exceeds SLA
                if response.elapsed.total_seconds() * 1000 > 90:
                    response.failure(
                        f"Latency {response.elapsed.total_seconds() * 1000:.2f}ms exceeds 90ms SLA",
                    )
                else:
                    response.success()
            else:
                response.failure(f"Status code: {response.status_code}")

    @task(2)
    def health_check(self):
        """Health check request"""
        with self.client.get("/health", catch_response=True, name="health") as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status code: {response.status_code}")

    @task(1)
    def metrics(self):
        """Fetch metrics"""
        with self.client.get("/metrics", catch_response=True, name="metrics") as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status code: {response.status_code}")
