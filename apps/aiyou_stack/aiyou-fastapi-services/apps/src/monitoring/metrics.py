# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Prometheus metrics collection."""

import logging

from prometheus_client import (
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Prometheus metrics collector for LLM serving.

    Tracks:
    - Request counts and latencies
    - Token throughput
    - GPU utilization
    - Model-specific metrics
    """

    def __init__(self, registry: CollectorRegistry = None):
        self.registry = registry or CollectorRegistry()

        # Request metrics
        self.requests_total = Counter(
            "llm_requests_total",
            "Total number of LLM requests",
            ["model", "status"],
            registry=self.registry,
        )

        self.request_duration = Histogram(
            "llm_request_duration_seconds",
            "Request duration in seconds",
            ["model"],
            registry=self.registry,
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0],
        )

        # Token metrics
        self.tokens_generated = Counter(
            "llm_tokens_generated_total",
            "Total tokens generated",
            ["model"],
            registry=self.registry,
        )

        self.tokens_per_second = Gauge(
            "llm_tokens_per_second",
            "Token generation throughput",
            ["model"],
            registry=self.registry,
        )

        # GPU metrics
        self.gpu_utilization = Gauge(
            "gpu_utilization_percent",
            "GPU utilization percentage",
            ["gpu_id"],
            registry=self.registry,
        )

        self.gpu_memory_used = Gauge(
            "gpu_memory_used_bytes",
            "GPU memory used in bytes",
            ["gpu_id"],
            registry=self.registry,
        )

        # Model metrics
        self.models_loaded = Gauge(
            "models_loaded_count",
            "Number of models currently loaded",
            registry=self.registry,
        )

        self.active_requests = Gauge(
            "active_requests_count",
            "Number of active requests",
            ["model"],
            registry=self.registry,
        )

        # Routing metrics
        self.routing_decisions = Counter(
            "routing_decisions_total",
            "Total routing decisions",
            ["strategy", "model"],
            registry=self.registry,
        )

        logger.info("Metrics collector initialized")

    def record_request(
        self,
        model: str,
        duration_seconds: float,
        tokens: int,
        status: str = "success",
    ):
        """Record a completed request."""
        self.requests_total.labels(model=model, status=status).inc()
        self.request_duration.labels(model=model).observe(duration_seconds)
        self.tokens_generated.labels(model=model).inc(tokens)

        # Calculate tokens/sec
        if duration_seconds > 0:
            tps = tokens / duration_seconds
            self.tokens_per_second.labels(model=model).set(tps)

    def update_gpu_metrics(self, gpu_id: int, utilization: float, memory_used: float):
        """Update GPU metrics."""
        self.gpu_utilization.labels(gpu_id=str(gpu_id)).set(utilization * 100)
        self.gpu_memory_used.labels(gpu_id=str(gpu_id)).set(memory_used * 1024**3)

    def update_model_count(self, count: int):
        """Update loaded model count."""
        self.models_loaded.set(count)

    def update_active_requests(self, model: str, count: int):
        """Update active request count for a model."""
        self.active_requests.labels(model=model).set(count)

    def record_routing(self, strategy: str, model: str):
        """Record a routing decision."""
        self.routing_decisions.labels(strategy=strategy, model=model).inc()

    def get_metrics(self) -> bytes:
        """Get Prometheus metrics in text format."""
        return generate_latest(self.registry)

    def get_metrics_dict(self) -> dict:
        """Get metrics as a dictionary (for JSON API)."""
        # This is a simplified version - in production, parse the Prometheus metrics
        return {
            "requests_total": "See /metrics endpoint",
            "tokens_generated": "See /metrics endpoint",
            "models_loaded": "See /metrics endpoint",
        }
