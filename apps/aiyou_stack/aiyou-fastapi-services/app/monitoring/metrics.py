# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Prometheus metrics collection for application monitoring.
Tracks requests, errors, latencies, and custom business metrics.
"""

import psutil
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    Info,
    generate_latest,
)

from app.config import settings

# Create metrics registry
metrics_registry = CollectorRegistry()

# Application Info
app_info = Info("app", "Application information", registry=metrics_registry)
app_info.info(
    {
        "name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
    },
)

# Request Metrics
http_requests_total = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "status"],
    registry=metrics_registry,
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0),
    registry=metrics_registry,
)

http_requests_in_progress = Gauge(
    "http_requests_in_progress",
    "Number of HTTP requests currently being processed",
    ["method", "endpoint"],
    registry=metrics_registry,
)

# Error Metrics
http_exceptions_total = Counter(
    "http_exceptions_total",
    "Total number of exceptions raised",
    ["exception_type", "endpoint"],
    registry=metrics_registry,
)

error_responses_total = Counter(
    "error_responses_total",
    "Total number of error responses (4xx, 5xx)",
    ["status_code", "endpoint"],
    registry=metrics_registry,
)

# System Metrics
system_cpu_usage_percent = Gauge(
    "system_cpu_usage_percent",
    "System CPU usage percentage",
    registry=metrics_registry,
)

system_memory_usage_percent = Gauge(
    "system_memory_usage_percent",
    "System memory usage percentage",
    registry=metrics_registry,
)

system_memory_usage_bytes = Gauge(
    "system_memory_usage_bytes",
    "System memory usage in bytes",
    registry=metrics_registry,
)

system_disk_usage_percent = Gauge(
    "system_disk_usage_percent",
    "System disk usage percentage",
    ["mount_point"],
    registry=metrics_registry,
)

# Application Metrics
app_uptime_seconds = Gauge(
    "app_uptime_seconds",
    "Application uptime in seconds",
    registry=metrics_registry,
)

active_connections = Gauge(
    "active_connections",
    "Number of active connections",
    registry=metrics_registry,
)

# Health Check Metrics
health_check_status = Gauge(
    "health_check_status",
    "Health check status (1=healthy, 0=unhealthy)",
    ["check_name"],
    registry=metrics_registry,
)

health_check_duration_seconds = Histogram(
    "health_check_duration_seconds",
    "Health check duration in seconds",
    ["check_name"],
    registry=metrics_registry,
)

# Business Metrics (examples)
business_operations_total = Counter(
    "business_operations_total",
    "Total number of business operations",
    ["operation_type", "status"],
    registry=metrics_registry,
)

business_operation_duration_seconds = Histogram(
    "business_operation_duration_seconds",
    "Business operation duration in seconds",
    ["operation_type"],
    registry=metrics_registry,
)


class MetricsCollector:
    """Utility class for collecting and recording metrics."""

    @staticmethod
    def record_request(method: str, endpoint: str, status_code: int, duration: float):
        """Record HTTP request metrics."""
        http_requests_total.labels(method=method, endpoint=endpoint, status=status_code).inc()
        http_request_duration_seconds.labels(method=method, endpoint=endpoint).observe(duration)

        # Record errors
        if status_code >= 400:
            error_responses_total.labels(status_code=status_code, endpoint=endpoint).inc()

    @staticmethod
    def record_exception(exception_type: str, endpoint: str):
        """Record exception occurrence."""
        http_exceptions_total.labels(exception_type=exception_type, endpoint=endpoint).inc()

    @staticmethod
    def update_system_metrics():
        """Update system resource metrics."""
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=0.1)
        system_cpu_usage_percent.set(cpu_percent)

        # Memory usage
        memory = psutil.virtual_memory()
        system_memory_usage_percent.set(memory.percent)
        system_memory_usage_bytes.set(memory.used)

        # Disk usage
        disk = psutil.disk_usage("/")
        system_disk_usage_percent.labels(mount_point="/").set(disk.percent)

    @staticmethod
    def record_business_operation(operation_type: str, status: str, duration: float | None = None):
        """Record custom business operation metrics.

        Args:
            operation_type: Type of operation (e.g., "payment", "user_registration")
            status: Operation status (e.g., "success", "failure")
            duration: Operation duration in seconds (optional)

        """
        business_operations_total.labels(operation_type=operation_type, status=status).inc()

        if duration is not None:
            business_operation_duration_seconds.labels(operation_type=operation_type).observe(
                duration,
            )

    @staticmethod
    def record_health_check(check_name: str, is_healthy: bool, duration: float):
        """Record health check result."""
        health_check_status.labels(check_name=check_name).set(1 if is_healthy else 0)
        health_check_duration_seconds.labels(check_name=check_name).observe(duration)


# Convenience functions
def record_request(method: str, endpoint: str, status_code: int, duration: float):
    """Record HTTP request metrics."""
    MetricsCollector.record_request(method, endpoint, status_code, duration)


def record_error(exception_type: str, endpoint: str):
    """Record exception occurrence."""
    MetricsCollector.record_exception(exception_type, endpoint)


def update_system_metrics():
    """Update system resource metrics."""
    MetricsCollector.update_system_metrics()


def get_metrics() -> bytes:
    """Get current metrics in Prometheus format."""
    return generate_latest(metrics_registry)


def get_metrics_content_type() -> str:
    """Get the content type for Prometheus metrics."""
    return CONTENT_TYPE_LATEST
