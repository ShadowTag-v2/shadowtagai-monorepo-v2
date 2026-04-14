"""ML-based anomaly detection for intelligence pipelines.

Features:
- Time-series anomaly detection
- Cost spike prediction
- Source failure prediction
- Quality degradation detection
- Predictive alerting
"""

import logging
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class Anomaly:
    """Detected anomaly."""

    timestamp: datetime
    metric_name: str
    observed_value: float
    expected_value: float
    deviation_sigma: float
    severity: str  # low, medium, high, critical
    confidence: float
    message: str


class TimeSeriesAnomalyDetector:
    """Statistical anomaly detection using moving averages and standard deviation.

    Uses Z-score method:
    - Calculate rolling mean and std dev
    - Flag values beyond N standard deviations
    - Adaptive thresholds based on historical patterns
    """

    def __init__(
        self,
        window_size: int = 100,
        zscore_threshold: float = 3.0,
    ):
        self.window_size = window_size
        self.zscore_threshold = zscore_threshold

        # Historical data per metric
        self.history: dict[str, deque] = {}
        self.anomalies: list[Anomaly] = []

    def record_value(self, metric_name: str, value: float) -> Anomaly | None:
        """Record a new value and check for anomalies.

        Args:
            metric_name: Name of the metric
            value: Observed value

        Returns:
            Anomaly if detected, None otherwise

        """
        # Initialize history if needed
        if metric_name not in self.history:
            self.history[metric_name] = deque(maxlen=self.window_size)

        history = self.history[metric_name]
        history.append(value)

        # Need sufficient history for detection
        if len(history) < 20:
            return None

        # Calculate statistics
        values = np.array(history)
        mean = np.mean(values)
        std = np.std(values)

        if std == 0:
            return None  # No variance

        # Calculate Z-score
        zscore = abs((value - mean) / std)

        if zscore > self.zscore_threshold:
            # Anomaly detected
            severity = self._calculate_severity(zscore)
            confidence = min(1.0, zscore / (self.zscore_threshold * 2))

            anomaly = Anomaly(
                timestamp=datetime.now(),
                metric_name=metric_name,
                observed_value=value,
                expected_value=mean,
                deviation_sigma=zscore,
                severity=severity,
                confidence=confidence,
                message=f"{metric_name} anomaly: {value:.2f} (expected {mean:.2f} ± {std:.2f})",
            )

            self.anomalies.append(anomaly)
            logger.warning(f"Anomaly detected: {anomaly.message}")

            # Keep last 100 anomalies
            if len(self.anomalies) > 100:
                self.anomalies = self.anomalies[-100:]

            return anomaly

        return None

    def _calculate_severity(self, zscore: float) -> str:
        """Calculate severity based on Z-score."""
        if zscore > 5.0:
            return "critical"
        if zscore > 4.0:
            return "high"
        if zscore > 3.5:
            return "medium"
        return "low"

    def predict_next_value(self, metric_name: str) -> tuple[float, float]:
        """Predict next value using exponential smoothing.

        Args:
            metric_name: Name of the metric

        Returns:
            (predicted_value, confidence_interval)

        """
        if metric_name not in self.history:
            return (0.0, 0.0)

        history = self.history[metric_name]
        if len(history) < 10:
            return (0.0, 0.0)

        values = np.array(history)

        # Simple exponential smoothing
        alpha = 0.3  # Smoothing factor
        predicted = values[-1]

        for i in range(len(values) - 2, max(0, len(values) - 10), -1):
            predicted = alpha * values[i] + (1 - alpha) * predicted

        # Confidence interval (2 std devs)
        std = np.std(values[-20:]) if len(values) >= 20 else np.std(values)
        confidence_interval = 2 * std

        return (predicted, confidence_interval)

    def get_anomalies(
        self,
        since: datetime | None = None,
        severity: str | None = None,
    ) -> list[Anomaly]:
        """Get detected anomalies with optional filtering.

        Args:
            since: Only return anomalies after this time
            severity: Filter by severity level

        Returns:
            List of anomalies

        """
        anomalies = self.anomalies

        if since:
            anomalies = [a for a in anomalies if a.timestamp >= since]

        if severity:
            anomalies = [a for a in anomalies if a.severity == severity]

        return anomalies


class CostSpikePredictor:
    """Predict cost spikes before they happen.

    Uses trend analysis to forecast when costs will exceed budget.
    """

    def __init__(self, budget: float = 77.0):
        self.budget = budget
        self.cost_history: deque = deque(maxlen=100)

    def record_cost(self, amount: float):
        """Record a cost event."""
        self.cost_history.append({"timestamp": datetime.now(), "amount": amount})

    def predict_end_of_month_cost(self) -> tuple[float, float]:
        """Predict total cost at end of month.

        Returns:
            (predicted_cost, confidence)

        """
        if not self.cost_history:
            return (0.0, 0.0)

        # Get costs from this month
        now = datetime.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0)

        month_costs = [
            entry["amount"] for entry in self.cost_history if entry["timestamp"] >= month_start
        ]

        if not month_costs:
            return (0.0, 0.0)

        # Calculate daily rate
        days_elapsed = (now - month_start).days + 1
        total_so_far = sum(month_costs)
        daily_rate = total_so_far / days_elapsed

        # Project to end of month
        days_in_month = 30  # Approximate
        predicted_cost = daily_rate * days_in_month

        # Confidence based on sample size
        confidence = min(1.0, days_elapsed / 15)  # Full confidence after 15 days

        return (predicted_cost, confidence)

    def will_exceed_budget(self, threshold: float = 0.9) -> tuple[bool, dict]:
        """Check if projected cost will exceed budget.

        Args:
            threshold: Warning threshold (0.9 = 90% of budget)

        Returns:
            (will_exceed, details)

        """
        predicted_cost, confidence = self.predict_end_of_month_cost()

        will_exceed = predicted_cost > (self.budget * threshold)

        return (
            will_exceed,
            {
                "predicted_cost": predicted_cost,
                "budget": self.budget,
                "utilization": (predicted_cost / self.budget * 100) if self.budget > 0 else 0,
                "confidence": confidence,
                "recommendation": "Enable throttling" if will_exceed else "On track",
            },
        )


class SourceFailurePredictor:
    """Predict source failures based on error patterns.

    Tracks error rates and predicts when a source will fail.
    """

    def __init__(self):
        self.source_health: dict[str, deque] = {}

    def record_health_check(self, source_name: str, success: bool):
        """Record health check result."""
        if source_name not in self.source_health:
            self.source_health[source_name] = deque(maxlen=50)

        self.source_health[source_name].append({"timestamp": datetime.now(), "success": success})

    def predict_failure_probability(self, source_name: str) -> tuple[float, str]:
        """Predict probability of source failure.

        Args:
            source_name: Name of source

        Returns:
            (probability, status)

        """
        if source_name not in self.source_health:
            return (0.0, "unknown")

        history = self.source_health[source_name]
        if len(history) < 10:
            return (0.0, "insufficient_data")

        # Calculate recent failure rate
        recent_checks = list(history)[-20:]
        failure_count = sum(1 for check in recent_checks if not check["success"])
        failure_rate = failure_count / len(recent_checks)

        # Weight recent failures more heavily
        very_recent = list(history)[-5:]
        recent_failure_rate = sum(1 for check in very_recent if not check["success"]) / len(
            very_recent,
        )

        # Combined probability
        probability = (failure_rate * 0.6) + (recent_failure_rate * 0.4)

        # Status
        if probability > 0.7:
            status = "critical"
        elif probability > 0.5:
            status = "warning"
        elif probability > 0.3:
            status = "degraded"
        else:
            status = "healthy"

        return (probability, status)

    def get_at_risk_sources(self, threshold: float = 0.5) -> list[dict]:
        """Get sources at risk of failure."""
        at_risk = []

        for source_name in self.source_health:
            probability, status = self.predict_failure_probability(source_name)

            if probability >= threshold:
                at_risk.append(
                    {
                        "source": source_name,
                        "failure_probability": probability,
                        "status": status,
                        "recommendation": "Enable circuit breaker"
                        if probability > 0.7
                        else "Monitor closely",
                    },
                )

        return sorted(at_risk, key=lambda x: -x["failure_probability"])


class MLAnomalyDetectionSystem:
    """Unified ML-based anomaly detection system.

    Combines multiple detectors for comprehensive monitoring.
    """

    def __init__(self, budget: float = 77.0):
        self.timeseries_detector = TimeSeriesAnomalyDetector()
        self.cost_predictor = CostSpikePredictor(budget=budget)
        self.failure_predictor = SourceFailurePredictor()

    async def analyze_metrics(self, metrics: dict) -> dict:
        """Analyze metrics and detect anomalies.

        Args:
            metrics: Current metrics

        Returns:
            Analysis results with anomalies and predictions

        """
        results = {
            "timestamp": datetime.now().isoformat(),
            "anomalies": [],
            "predictions": {},
            "recommendations": [],
        }

        # Check time-series anomalies
        for metric_name, value in metrics.items():
            if isinstance(value, (int, float)):
                anomaly = self.timeseries_detector.record_value(metric_name, value)

                if anomaly:
                    results["anomalies"].append(
                        {
                            "type": "timeseries",
                            "metric": anomaly.metric_name,
                            "severity": anomaly.severity,
                            "message": anomaly.message,
                            "confidence": anomaly.confidence,
                        },
                    )

        # Cost prediction
        will_exceed, cost_details = self.cost_predictor.will_exceed_budget()
        results["predictions"]["cost"] = cost_details

        if will_exceed:
            results["recommendations"].append(
                {
                    "type": "cost_control",
                    "priority": "high",
                    "message": f"Projected to exceed budget: ${cost_details['predicted_cost']:.2f}",
                    "action": "Enable auto-throttling or reduce collection frequency",
                },
            )

        # Source failure prediction
        at_risk_sources = self.failure_predictor.get_at_risk_sources()
        results["predictions"]["source_failures"] = at_risk_sources

        for source in at_risk_sources:
            if source["failure_probability"] > 0.7:
                results["recommendations"].append(
                    {
                        "type": "source_health",
                        "priority": "critical",
                        "message": f"Source '{source['source']}' at high risk of failure ({source['failure_probability'] * 100:.0f}%)",
                        "action": source["recommendation"],
                    },
                )

        return results

    def get_dashboard_data(self) -> dict:
        """Get data for ML dashboard."""
        return {
            "anomaly_count_24h": len(
                self.timeseries_detector.get_anomalies(since=datetime.now() - timedelta(hours=24)),
            ),
            "critical_anomalies": len(self.timeseries_detector.get_anomalies(severity="critical")),
            "cost_prediction": self.cost_predictor.predict_end_of_month_cost(),
            "at_risk_sources": len(self.failure_predictor.get_at_risk_sources()),
        }
