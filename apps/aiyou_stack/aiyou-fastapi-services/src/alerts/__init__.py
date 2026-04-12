"""
Predictive Alerting System - Proactive problem detection and notification.

Features:
- Predictive alerts before failures occur
- Multi-channel notifications (email, webhook, Slack)
- Alert deduplication and grouping
- Escalation policies
- Alert fatigue reduction

Uses ML predictions to alert:
- 24h before projected budget overrun
- 12h before source failure (>70% probability)
- When quality degradation trend detected
- Performance degradation predictions
"""

import asyncio
import json
import logging
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class AlertChannel(Enum):
    """Notification channels."""

    EMAIL = "email"
    WEBHOOK = "webhook"
    SLACK = "slack"
    PAGERDUTY = "pagerduty"
    LOG = "log"


class AlertPriority(Enum):
    """Alert priority levels."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class PredictiveAlert:
    """Predictive alert generated from ML models."""

    id: str
    timestamp: datetime = field(default_factory=datetime.now)

    # Alert details
    title: str
    message: str
    priority: AlertPriority = AlertPriority.WARNING
    category: str = "general"  # cost, performance, quality, source_health

    # Prediction details
    predicted_event: str  # What will happen
    predicted_time: datetime  # When it will happen
    confidence: float  # 0-1
    time_to_event: float  # Seconds until event

    # Context
    current_value: float | None = None
    predicted_value: float | None = None
    threshold: float | None = None

    # Actionable recommendations
    recommendations: list[str] = field(default_factory=list)

    # Alert lifecycle
    acknowledged: bool = False
    resolved: bool = False
    snoozed_until: datetime | None = None


@dataclass
class AlertRule:
    """Rule for generating alerts."""

    name: str
    category: str
    priority: AlertPriority
    condition: Callable  # Function that returns True if alert should fire
    channels: list[AlertChannel]
    cooldown_minutes: int = 60  # Minimum time between duplicate alerts


class PredictiveAlertingSystem:
    """
    ML-powered predictive alerting system.

    Generates alerts before problems occur using:
    - Cost spike predictor (alert 24h before overrun)
    - Source failure predictor (alert when probability >70%)
    - Quality degradation detector
    - Performance trend analysis
    """

    def __init__(
        self,
        ml_detector=None,
        cost_detector=None,
        performance_monitor=None,
    ):
        self.ml_detector = ml_detector
        self.cost_detector = cost_detector
        self.performance_monitor = performance_monitor

        # Alert storage
        self.active_alerts: list[PredictiveAlert] = []
        self.alert_history: list[PredictiveAlert] = []

        # Alert rules
        self.rules: list[AlertRule] = []
        self._init_default_rules()

        # Last alert time by rule (for cooldown)
        self.last_alert_time: dict[str, datetime] = {}

        # Notification handlers
        self.notification_handlers: dict[AlertChannel, Callable] = {
            AlertChannel.LOG: self._notify_log,
        }

    def _init_default_rules(self):
        """Initialize default alerting rules."""
        self.rules = [
            AlertRule(
                name="cost_overrun_predicted",
                category="cost",
                priority=AlertPriority.CRITICAL,
                condition=lambda ctx: self._check_cost_overrun(ctx),
                channels=[AlertChannel.LOG, AlertChannel.EMAIL],
                cooldown_minutes=360,  # 6 hours
            ),
            AlertRule(
                name="source_failure_imminent",
                category="source_health",
                priority=AlertPriority.WARNING,
                condition=lambda ctx: self._check_source_failure(ctx),
                channels=[AlertChannel.LOG, AlertChannel.SLACK],
                cooldown_minutes=120,  # 2 hours
            ),
            AlertRule(
                name="quality_degradation",
                category="quality",
                priority=AlertPriority.WARNING,
                condition=lambda ctx: self._check_quality_degradation(ctx),
                channels=[AlertChannel.LOG],
                cooldown_minutes=180,  # 3 hours
            ),
            AlertRule(
                name="performance_degradation",
                category="performance",
                priority=AlertPriority.WARNING,
                condition=lambda ctx: self._check_performance_degradation(ctx),
                channels=[AlertChannel.LOG],
                cooldown_minutes=60,
            ),
        ]

    async def check_and_alert(self) -> list[PredictiveAlert]:
        """
        Check all rules and generate alerts.

        Returns:
            List of newly generated alerts
        """
        new_alerts = []

        # Build context for rule evaluation
        context = await self._build_context()

        for rule in self.rules:
            # Check cooldown
            if rule.name in self.last_alert_time:
                elapsed = (datetime.now() - self.last_alert_time[rule.name]).total_seconds()
                if elapsed < rule.cooldown_minutes * 60:
                    continue  # Still in cooldown

            # Evaluate condition
            try:
                alert_data = rule.condition(context)

                if alert_data:
                    # Generate alert
                    alert = self._create_alert_from_rule(rule, alert_data)
                    new_alerts.append(alert)

                    # Update last alert time
                    self.last_alert_time[rule.name] = datetime.now()

                    # Send notifications
                    await self._send_notifications(alert, rule.channels)

            except Exception as e:
                logger.error(f"Error evaluating rule {rule.name}: {e}")

        # Store alerts
        self.active_alerts.extend(new_alerts)
        self.alert_history.extend(new_alerts)

        # Cleanup old alerts
        if len(self.alert_history) > 1000:
            self.alert_history = self.alert_history[-1000:]

        return new_alerts

    async def _build_context(self) -> dict:
        """Build context for rule evaluation."""
        context = {}

        # Cost predictions
        if self.cost_detector:
            predicted_cost, confidence = self.cost_detector._project_monthly_cost(), 0.8
            context["cost"] = {
                "current": self.cost_detector.current_cost,
                "predicted": predicted_cost,
                "budget": self.cost_detector.budget,
                "confidence": confidence,
                "utilization": self.cost_detector.current_cost / self.cost_detector.budget,
            }

        # Source health predictions
        if self.ml_detector:
            at_risk_sources = self.ml_detector.failure_predictor.get_at_risk_sources(threshold=0.7)
            context["source_health"] = {
                "at_risk_sources": at_risk_sources,
                "count": len(at_risk_sources),
            }

        # Performance metrics
        if self.performance_monitor:
            bottlenecks = self.performance_monitor.get_bottlenecks()
            context["performance"] = {
                "bottlenecks": bottlenecks,
                "critical_count": len([b for b in bottlenecks if b.get("severity") == "critical"]),
            }

        # ML anomalies
        if self.ml_detector:
            recent_anomalies = self.ml_detector.timeseries_detector.get_anomalies(
                since=datetime.now() - timedelta(hours=1)
            )
            context["anomalies"] = {
                "recent": recent_anomalies,
                "critical": len([a for a in recent_anomalies if a.severity == "critical"]),
            }

        return context

    def _check_cost_overrun(self, context: dict) -> dict | None:
        """Check if cost overrun is predicted."""
        cost_data = context.get("cost", {})
        predicted = cost_data.get("predicted", 0.0)
        budget = cost_data.get("budget", 77.0)
        confidence = cost_data.get("confidence", 0.0)

        if predicted > budget * 0.95 and confidence > 0.7:
            # Predict time to overrun
            current = cost_data.get("current", 0.0)
            cost_data.get("utilization", 0.0)

            # If at 50% now and projected to 100%, ~50% of month left
            # Rough estimate of days until overrun
            day_of_month = datetime.now().day
            days_remaining = 30 - day_of_month
            time_to_overrun = timedelta(days=days_remaining * 0.5)

            return {
                "predicted_event": "Budget overrun",
                "predicted_time": datetime.now() + time_to_overrun,
                "confidence": confidence,
                "current_value": current,
                "predicted_value": predicted,
                "threshold": budget,
                "recommendations": [
                    "Enable auto-throttling to reduce collection frequency",
                    "Review high-cost sources and consider disabling",
                    "Increase budget allocation if ROI justifies",
                    f"Projected overrun by ${predicted - budget:.2f}",
                ],
            }

        return None

    def _check_source_failure(self, context: dict) -> dict | None:
        """Check if source failure is imminent."""
        source_health = context.get("source_health", {})
        at_risk = source_health.get("at_risk_sources", [])

        if at_risk:
            # Get highest risk source
            highest_risk = at_risk[0]  # Already sorted by risk
            probability = highest_risk.get("failure_probability", 0.0)

            if probability > 0.7:
                # Estimate time to failure based on probability
                # Higher probability = sooner failure
                # 70% = ~24h, 90% = ~4h, 100% = immediate
                hours_to_failure = max(1, 24 * (1 - probability))
                time_to_failure = timedelta(hours=hours_to_failure)

                return {
                    "predicted_event": f"Source failure: {highest_risk.get('source')}",
                    "predicted_time": datetime.now() + time_to_failure,
                    "confidence": probability,
                    "current_value": probability * 100,
                    "threshold": 70.0,
                    "recommendations": [
                        highest_risk.get("recommendation", "Enable circuit breaker"),
                        "Review source health logs",
                        "Consider fallback data source",
                        f"{len(at_risk)} total sources at risk",
                    ],
                }

        return None

    def _check_quality_degradation(self, context: dict) -> dict | None:
        """Check for quality degradation trend."""
        # Would check tier 1 percentage trend from historical data
        # For now, simplified version
        return None

    def _check_performance_degradation(self, context: dict) -> dict | None:
        """Check for performance degradation."""
        perf_data = context.get("performance", {})
        critical_count = perf_data.get("critical_count", 0)

        if critical_count > 0:
            bottlenecks = perf_data.get("bottlenecks", [])
            worst = bottlenecks[0] if bottlenecks else {}

            return {
                "predicted_event": f"Performance degradation in {worst.get('component', 'unknown')}",
                "predicted_time": datetime.now() + timedelta(hours=1),
                "confidence": 0.8,
                "current_value": worst.get("avg_duration_ms", 0),
                "recommendations": [
                    "Investigate and optimize bottleneck",
                    f"{critical_count} critical bottlenecks detected",
                    "Review component performance metrics",
                ],
            }

        return None

    def _create_alert_from_rule(self, rule: AlertRule, alert_data: dict) -> PredictiveAlert:
        """Create alert from rule and data."""
        time_to_event = (alert_data["predicted_time"] - datetime.now()).total_seconds()

        # Format time until event
        hours = time_to_event / 3600
        if hours < 1:
            time_str = f"{time_to_event / 60:.0f} minutes"
        elif hours < 24:
            time_str = f"{hours:.1f} hours"
        else:
            time_str = f"{hours / 24:.1f} days"

        title = f"Predicted: {alert_data['predicted_event']} in {time_str}"
        message = f"{alert_data['predicted_event']} predicted with {alert_data['confidence'] * 100:.0f}% confidence"

        if alert_data.get("current_value") is not None:
            message += f"\nCurrent: {alert_data['current_value']:.2f}"

        if alert_data.get("predicted_value") is not None:
            message += f"\nPredicted: {alert_data['predicted_value']:.2f}"

        if alert_data.get("threshold") is not None:
            message += f"\nThreshold: {alert_data['threshold']:.2f}"

        alert_id = f"{rule.name}_{int(datetime.now().timestamp())}"

        return PredictiveAlert(
            id=alert_id,
            title=title,
            message=message,
            priority=rule.priority,
            category=rule.category,
            predicted_event=alert_data["predicted_event"],
            predicted_time=alert_data["predicted_time"],
            confidence=alert_data["confidence"],
            time_to_event=time_to_event,
            current_value=alert_data.get("current_value"),
            predicted_value=alert_data.get("predicted_value"),
            threshold=alert_data.get("threshold"),
            recommendations=alert_data.get("recommendations", []),
        )

    async def _send_notifications(self, alert: PredictiveAlert, channels: list[AlertChannel]):
        """Send alert to notification channels."""
        for channel in channels:
            handler = self.notification_handlers.get(channel)
            if handler:
                try:
                    await handler(alert)
                except Exception as e:
                    logger.error(f"Failed to send notification to {channel.value}: {e}")

    async def _notify_log(self, alert: PredictiveAlert):
        """Send alert to logs."""
        log_level = {
            AlertPriority.INFO: logging.INFO,
            AlertPriority.WARNING: logging.WARNING,
            AlertPriority.CRITICAL: logging.CRITICAL,
        }.get(alert.priority, logging.INFO)

        logger.log(
            log_level,
            f"[PREDICTIVE ALERT] {alert.title}\n{alert.message}\n"
            f"Recommendations: {', '.join(alert.recommendations)}",
        )

    def register_notification_handler(self, channel: AlertChannel, handler: Callable):
        """
        Register custom notification handler.

        Args:
            channel: AlertChannel to handle
            handler: Async function(alert: PredictiveAlert) -> None
        """
        self.notification_handlers[channel] = handler
        logger.info(f"Registered notification handler for {channel.value}")

    def acknowledge_alert(self, alert_id: str):
        """Acknowledge an alert."""
        for alert in self.active_alerts:
            if alert.id == alert_id:
                alert.acknowledged = True
                logger.info(f"Alert {alert_id} acknowledged")
                return True
        return False

    def resolve_alert(self, alert_id: str):
        """Resolve an alert."""
        for alert in self.active_alerts:
            if alert.id == alert_id:
                alert.resolved = True
                self.active_alerts.remove(alert)
                logger.info(f"Alert {alert_id} resolved")
                return True
        return False

    def snooze_alert(self, alert_id: str, minutes: int):
        """Snooze an alert for specified minutes."""
        for alert in self.active_alerts:
            if alert.id == alert_id:
                alert.snoozed_until = datetime.now() + timedelta(minutes=minutes)
                logger.info(f"Alert {alert_id} snoozed for {minutes} minutes")
                return True
        return False

    def get_active_alerts(
        self, category: str | None = None, priority: AlertPriority | None = None
    ) -> list[PredictiveAlert]:
        """Get active alerts with optional filtering."""
        alerts = self.active_alerts

        if category:
            alerts = [a for a in alerts if a.category == category]

        if priority:
            alerts = [a for a in alerts if a.priority == priority]

        # Filter out snoozed alerts
        alerts = [a for a in alerts if not a.snoozed_until or a.snoozed_until <= datetime.now()]

        return sorted(alerts, key=lambda a: (a.priority.value, a.time_to_event))

    def get_alert_stats(self) -> dict:
        """Get alerting statistics."""
        active = self.get_active_alerts()

        return {
            "active_count": len(active),
            "by_priority": {
                "critical": len([a for a in active if a.priority == AlertPriority.CRITICAL]),
                "warning": len([a for a in active if a.priority == AlertPriority.WARNING]),
                "info": len([a for a in active if a.priority == AlertPriority.INFO]),
            },
            "by_category": {
                "cost": len([a for a in active if a.category == "cost"]),
                "performance": len([a for a in active if a.category == "performance"]),
                "quality": len([a for a in active if a.category == "quality"]),
                "source_health": len([a for a in active if a.category == "source_health"]),
            },
            "total_historical": len(self.alert_history),
            "acknowledged_count": len([a for a in active if a.acknowledged]),
        }


# Global alerting system
alerting_system = None


def get_alerting_system() -> PredictiveAlertingSystem:
    """Get or create global alerting system."""
    global alerting_system
    if alerting_system is None:
        alerting_system = PredictiveAlertingSystem()
    return alerting_system


def initialize_alerting(ml_detector=None, cost_detector=None, performance_monitor=None):
    """Initialize global alerting system with component references."""
    global alerting_system
    alerting_system = PredictiveAlertingSystem(
        ml_detector=ml_detector,
        cost_detector=cost_detector,
        performance_monitor=performance_monitor,
    )
    logger.info("Predictive alerting system initialized")
    return alerting_system
