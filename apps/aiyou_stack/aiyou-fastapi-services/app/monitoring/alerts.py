# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Alert management system for proactive incident detection.
Supports multiple notification channels (webhook, email, Slack).
"""

import asyncio
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

import httpx

from app.config import settings
from app.monitoring.logger import get_logger

logger = get_logger(__name__)


class AlertSeverity(StrEnum):
    """Alert severity levels."""

    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


class Alert:
    """Represents an alert."""

    def __init__(
        self,
        name: str,
        severity: AlertSeverity,
        message: str,
        details: dict[str, Any] | None = None,
        metric_value: float | None = None,
        threshold: float | None = None,
    ):
        self.name = name
        self.severity = severity
        self.message = message
        self.details = details or {}
        self.metric_value = metric_value
        self.threshold = threshold
        self.timestamp = datetime.now(UTC)

    def to_dict(self) -> dict:
        """Convert alert to dictionary."""
        return {
            "name": self.name,
            "severity": self.severity.value,
            "message": self.message,
            "details": self.details,
            "metric_value": self.metric_value,
            "threshold": self.threshold,
            "timestamp": self.timestamp.isoformat(),
            "service": settings.app_name,
            "environment": settings.environment,
        }

    def format_slack_message(self) -> dict:
        """Format alert for Slack webhook."""
        color_map = {
            AlertSeverity.CRITICAL: "danger",
            AlertSeverity.WARNING: "warning",
            AlertSeverity.INFO: "good",
        }

        fields = [
            {"title": "Service", "value": settings.app_name, "short": True},
            {"title": "Environment", "value": settings.environment, "short": True},
            {"title": "Severity", "value": self.severity.value.upper(), "short": True},
        ]

        if self.metric_value is not None and self.threshold is not None:
            fields.append(
                {
                    "title": "Metric Value / Threshold",
                    "value": f"{self.metric_value} / {self.threshold}",
                    "short": True,
                },
            )

        return {
            "attachments": [
                {
                    "color": color_map[self.severity],
                    "title": f"Alert: {self.name}",
                    "text": self.message,
                    "fields": fields,
                    "footer": "ShadowTag-v2 Monitoring",
                    "ts": int(self.timestamp.timestamp()),
                },
            ],
        }


class AlertManager:
    """Manages alert routing and delivery."""

    def __init__(self):
        self.alert_history: list[Alert] = []
        self.max_history = 1000
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self):
        self._client = httpx.AsyncClient(timeout=10.0)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            await self._client.aclose()

    async def send_alert(self, alert: Alert):
        """Send alert through configured channels.

        Args:
            alert: Alert to send

        """
        # Add to history
        self.alert_history.append(alert)
        if len(self.alert_history) > self.max_history:
            self.alert_history.pop(0)

        logger.warning(
            f"Alert triggered: {alert.name}",
            extra={
                "alert_name": alert.name,
                "severity": alert.severity.value,
                "message": alert.message,
                "details": alert.details,
            },
        )

        # Send to configured channels
        tasks = []

        if settings.alert_webhook_url:
            tasks.append(self._send_webhook(alert))

        if settings.alert_slack_webhook:
            tasks.append(self._send_slack(alert))

        if settings.alert_email_enabled:
            tasks.append(self._send_email(alert))

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _send_webhook(self, alert: Alert):
        """Send alert to generic webhook."""
        try:
            if not self._client:
                self._client = httpx.AsyncClient(timeout=10.0)

            response = await self._client.post(
                settings.alert_webhook_url,
                json=alert.to_dict(),
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()

            logger.info(f"Alert sent to webhook: {alert.name}")
        except Exception as e:
            logger.error(f"Failed to send alert to webhook: {e!s}")

    async def _send_slack(self, alert: Alert):
        """Send alert to Slack webhook."""
        try:
            if not self._client:
                self._client = httpx.AsyncClient(timeout=10.0)

            response = await self._client.post(
                settings.alert_slack_webhook,
                json=alert.format_slack_message(),
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()

            logger.info(f"Alert sent to Slack: {alert.name}")
        except Exception as e:
            logger.error(f"Failed to send alert to Slack: {e!s}")

    async def _send_email(self, alert: Alert):
        """Send alert via email.
        This is a placeholder - implement with your email service.
        """
        try:
            # TODO: Implement email sending
            # Example using SendGrid, SES, or SMTP
            logger.info(f"Email alert (placeholder): {alert.name}")
        except Exception as e:
            logger.error(f"Failed to send email alert: {e!s}")

    def get_recent_alerts(self, limit: int = 100) -> list[dict]:
        """Get recent alerts."""
        return [alert.to_dict() for alert in self.alert_history[-limit:]]


# Global alert manager instance
alert_manager = AlertManager()


async def trigger_alert(
    name: str,
    severity: AlertSeverity,
    message: str,
    details: dict[str, Any] | None = None,
    metric_value: float | None = None,
    threshold: float | None = None,
):
    """Convenience function to trigger an alert.

    Args:
        name: Alert name
        severity: Alert severity
        message: Alert message
        details: Additional details
        metric_value: Current metric value
        threshold: Alert threshold

    """
    alert = Alert(
        name=name,
        severity=severity,
        message=message,
        details=details,
        metric_value=metric_value,
        threshold=threshold,
    )

    async with AlertManager() as manager:
        await manager.send_alert(alert)
