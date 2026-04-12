"""Prometheus metrics collection for kernel chain."""

from prometheus_client import Counter, Histogram, Info

from app.config import settings


class MetricsCollector:
    """
    Centralized metrics collector for kernel chain.

    Tracks:
    - Latency per kernel and total chain (p50, p99)
    - Token counts (input/output per kernel)
    - Cost per decision
    - Success/failure rates
    - Confidence scores
    - SLA violations
    """

    def __init__(self):
        # Decision metrics
        self.decisions_total = Counter(
            "shadowtagai_decisions_total",
            "Total number of decisions processed",
            ["status"],  # success, failure
        )

        self.decision_latency = Histogram(
            "shadowtagai_decision_latency_ms",
            "Total decision latency in milliseconds",
            buckets=[10, 25, 50, 75, 90, 120, 150, 200, 300, 500],
        )

        self.decision_cost = Histogram(
            "shadowtagai_decision_cost_usd",
            "Cost per decision in USD",
            buckets=[0.0001, 0.0003, 0.0005, 0.001, 0.002, 0.005],
        )

        # Kernel-specific metrics
        self.kernel_latency = Histogram(
            "shadowtagai_kernel_latency_ms",
            "Kernel execution latency in milliseconds",
            ["kernel_name"],
            buckets=[5, 10, 20, 40, 60, 80, 100, 150],
        )

        self.kernel_executions = Counter(
            "shadowtagai_kernel_executions_total",
            "Total kernel executions",
            ["kernel_name", "status"],
        )

        self.kernel_tokens = Counter(
            "shadowtagai_kernel_tokens_total",
            "Total tokens processed",
            ["kernel_name", "direction"],  # input, output
        )

        # Confidence metrics
        self.decision_confidence = Histogram(
            "shadowtagai_decision_confidence",
            "Decision confidence scores",
            buckets=[0.5, 0.6, 0.7, 0.8, 0.85, 0.9, 0.95, 1.0],
        )

        # Risk tier distribution
        self.risk_tier_distribution = Counter(
            "shadowtagai_risk_tier_total",
            "Distribution of risk tiers",
            ["tier"],
        )

        # Violations
        self.violations_detected = Histogram(
            "shadowtagai_violations_detected",
            "Number of violations detected per decision",
            buckets=[0, 1, 2, 3, 5, 10, 20],
        )

        # SLA violations
        self.sla_violations = Counter(
            "shadowtagai_sla_violations_total",
            "SLA violations",
            ["type"],  # latency, cost, confidence
        )

        # Compression metrics
        self.compression_ratio = Histogram(
            "shadowtagai_compression_ratio",
            "Audit trail compression ratio",
            buckets=[2, 5, 8, 10, 12, 15, 20],
        )

        # System info
        self.system_info = Info(
            "shadowtagai_system",
            "System information",
        )
        self.system_info.info(
            {
                "service_name": settings.service_name,
                "gemini_model": settings.gemini_model,
                "max_latency_p99_ms": str(settings.max_latency_p99_ms),
                "confidence_threshold": str(settings.confidence_threshold),
            }
        )

    def record_decision(
        self,
        latency_ms: float,
        cost_usd: float,
        confidence: float,
        risk_tier: int,
        violations_count: int,
        success: bool,
    ):
        """Record metrics for a completed decision."""
        status = "success" if success else "failure"

        self.decisions_total.labels(status=status).inc()
        self.decision_latency.observe(latency_ms)
        self.decision_cost.observe(cost_usd)
        self.decision_confidence.observe(confidence)
        self.risk_tier_distribution.labels(tier=f"tier_{risk_tier}").inc()
        self.violations_detected.observe(violations_count)

        # Check SLA violations
        if latency_ms > settings.max_latency_p99_ms:
            self.sla_violations.labels(type="latency").inc()
        if cost_usd > settings.max_cost_per_decision:
            self.sla_violations.labels(type="cost").inc()
        if confidence < settings.confidence_threshold:
            self.sla_violations.labels(type="confidence").inc()

    def record_kernel_execution(
        self,
        kernel_name: str,
        latency_ms: float,
        success: bool,
        tokens_input: int | None = None,
        tokens_output: int | None = None,
    ):
        """Record metrics for a kernel execution."""
        status = "success" if success else "failure"

        self.kernel_executions.labels(kernel_name=kernel_name, status=status).inc()
        self.kernel_latency.labels(kernel_name=kernel_name).observe(latency_ms)

        if tokens_input is not None:
            self.kernel_tokens.labels(kernel_name=kernel_name, direction="input").inc(tokens_input)

        if tokens_output is not None:
            self.kernel_tokens.labels(kernel_name=kernel_name, direction="output").inc(
                tokens_output
            )

    def record_compression(self, compression_ratio: float):
        """Record audit trail compression ratio."""
        self.compression_ratio.observe(compression_ratio)


# Global metrics collector instance
metrics_collector = MetricsCollector() if settings.enable_metrics else None
