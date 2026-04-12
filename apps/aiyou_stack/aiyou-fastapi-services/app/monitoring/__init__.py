"""
Monitoring and Observability Module

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
from app.monitoring.metrics import metrics_registry, record_error, record_request

__all__ = [
    "setup_logging",
    "get_logger",
    "metrics_registry",
    "record_request",
    "record_error",
    "health_check",
    "readiness_check",
    "AlertManager",
]
