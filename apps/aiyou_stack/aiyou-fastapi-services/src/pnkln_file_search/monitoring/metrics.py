"""Metrics collection for file search and enforcement operations"""

from collections import deque

import structlog
from prometheus_client import Counter, Gauge, Histogram

logger = structlog.get_logger(__name__)

# Prometheus metrics
FILE_SEARCH_LATENCY = Histogram(
    "file_search_latency_seconds",
    "File search retrieval latency",
    buckets=[0.1, 0.2, 0.3, 0.5, 0.8, 1.0, 2.0, 5.0],
)

FILE_SEARCH_ERRORS = Counter(
    "file_search_errors_total",
    "Total file search errors",
)

JUDGE_LAYER1_LATENCY = Histogram(
    "judge_layer1_latency_seconds",
    "Judge Layer 1 latency",
    buckets=[0.01, 0.02, 0.03, 0.04, 0.05, 0.08, 0.1],
)

ENFORCEMENT_LATENCY = Histogram(
    "enforcement_total_latency_seconds",
    "Total enforcement latency (Layers 2+3)",
    buckets=[0.02, 0.04, 0.06, 0.08, 0.09, 0.1, 0.15],
)

CORPUS_SYNC_FAILURES = Counter(
    "corpus_sync_failures_total",
    "Total corpus synchronization failures",
)

POLICY_MATCH_ACCURACY = Gauge(
    "policy_match_accuracy",
    "Policy match accuracy score",
)


class MetricsCollector:
    """Collects and tracks metrics for file search and enforcement

    Maintains rolling windows for calculating percentiles and rates.
    """

    def __init__(self, window_size: int = 1000):
        """Initialize metrics collector

        Args:
            window_size: Number of samples to keep for percentile calculations

        """
        self.window_size = window_size

        # Rolling windows for percentile calculations
        self.file_search_latencies: deque[float] = deque(maxlen=window_size)
        self.enforcement_latencies: deque[float] = deque(maxlen=window_size)
        self.layer1_latencies: deque[float] = deque(maxlen=window_size)

        # Error tracking
        self.file_search_errors = 0
        self.corpus_sync_failures = 0

        # Accuracy tracking
        self.policy_matches_total = 0
        self.policy_matches_correct = 0

    def record_file_search_latency(self, latency_ms: float) -> None:
        """Record file search latency

        Args:
            latency_ms: Latency in milliseconds

        """
        latency_sec = latency_ms / 1000.0
        self.file_search_latencies.append(latency_ms)
        FILE_SEARCH_LATENCY.observe(latency_sec)

        logger.debug("file_search_latency_recorded", latency_ms=latency_ms)

    def record_file_search_error(self) -> None:
        """Record a file search error"""
        self.file_search_errors += 1
        FILE_SEARCH_ERRORS.inc()

        logger.warning("file_search_error_recorded", total_errors=self.file_search_errors)

    def record_judge_layer1_latency(self, latency_ms: float) -> None:
        """Record Judge Layer 1 latency

        Args:
            latency_ms: Latency in milliseconds

        """
        latency_sec = latency_ms / 1000.0
        self.layer1_latencies.append(latency_ms)
        JUDGE_LAYER1_LATENCY.observe(latency_sec)

        logger.debug("judge_layer1_latency_recorded", latency_ms=latency_ms)

    def record_enforcement_latency(self, latency_ms: float) -> None:
        """Record total enforcement latency (Layers 2+3)

        Args:
            latency_ms: Latency in milliseconds

        """
        latency_sec = latency_ms / 1000.0
        self.enforcement_latencies.append(latency_ms)
        ENFORCEMENT_LATENCY.observe(latency_sec)

        logger.debug("enforcement_latency_recorded", latency_ms=latency_ms)

    def record_corpus_sync_failure(self) -> None:
        """Record a corpus sync failure"""
        self.corpus_sync_failures += 1
        CORPUS_SYNC_FAILURES.inc()

        logger.warning("corpus_sync_failure_recorded", total_failures=self.corpus_sync_failures)

    def record_policy_match(self, correct: bool) -> None:
        """Record a policy match result for accuracy tracking

        Args:
            correct: Whether the match was correct

        """
        self.policy_matches_total += 1
        if correct:
            self.policy_matches_correct += 1

        if self.policy_matches_total > 0:
            accuracy = self.policy_matches_correct / self.policy_matches_total
            POLICY_MATCH_ACCURACY.set(accuracy)

    def get_percentile(self, values: deque[float], percentile: int) -> float:
        """Calculate percentile from rolling window

        Args:
            values: Deque of values
            percentile: Percentile to calculate (e.g., 99)

        Returns:
            Percentile value

        """
        if not values:
            return 0.0

        sorted_values = sorted(values)
        index = int(len(sorted_values) * (percentile / 100.0))
        return sorted_values[min(index, len(sorted_values) - 1)]

    def get_metrics_summary(self) -> dict:
        """Get summary of all metrics

        Returns:
            Dict with current metrics

        """
        file_search_p99 = self.get_percentile(self.file_search_latencies, 99)
        enforcement_p99 = self.get_percentile(self.enforcement_latencies, 99)
        layer1_p99 = self.get_percentile(self.layer1_latencies, 99)

        corpus_sync_failure_rate = 0.0
        if self.policy_matches_total > 0:
            # Approximate failure rate
            corpus_sync_failure_rate = self.corpus_sync_failures / max(self.policy_matches_total, 1)

        false_positive_rate = 0.0
        if self.policy_matches_total > 0:
            false_positive_rate = 1.0 - (self.policy_matches_correct / self.policy_matches_total)

        return {
            "file_search": {
                "p99_latency_ms": file_search_p99,
                "error_count": self.file_search_errors,
                "sample_count": len(self.file_search_latencies),
            },
            "judge": {
                "layer1_p99_ms": layer1_p99,
                "enforcement_p99_ms": enforcement_p99,
            },
            "corpus": {
                "sync_failures": self.corpus_sync_failures,
                "sync_failure_rate": corpus_sync_failure_rate,
            },
            "accuracy": {
                "total_matches": self.policy_matches_total,
                "correct_matches": self.policy_matches_correct,
                "false_positive_rate": false_positive_rate,
            },
        }
