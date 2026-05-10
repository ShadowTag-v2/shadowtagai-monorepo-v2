"""Monitoring and Observability Module

Provides comprehensive monitoring capabilities including:
- Structured logging
- Prometheus metrics
- OpenTelemetry tracing
- Health checks
- Alerting
"""

from app.monitoring.alerts import AlertManager
from app.monitoring.health import health_check, readiness_check
from app.monitoring.logger import get_logger, setup_logging
from app.monitoring.metrics import metrics_collector, metrics_registry, record_error, record_request

__all__ = [
    "AlertManager",
    "get_logger",
    "health_check",
    "metrics_collector",
    "metrics_registry",
    "readiness_check",
    "record_error",
    "record_request",
    "setup_logging",
]
