"""Monitoring middleware for FastAPI.
Automatically tracks requests, errors, and performance metrics.
"""

import time
import uuid
from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.monitoring.alerts import AlertSeverity, trigger_alert
from app.monitoring.health import health_checker
from app.monitoring.logger import correlation_processor, get_logger
from app.monitoring.metrics import (
    MetricsCollector,
    app_uptime_seconds,
    http_requests_in_progress,
    update_system_metrics,
)

logger = get_logger(__name__)


class MonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware for comprehensive request monitoring.

    Tracks:
    - Request/response metrics
    - Request duration
    - Error rates
    - Correlation IDs
    - System metrics
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with monitoring."""
        # Generate correlation ID
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        correlation_processor.set_correlation_id(correlation_id)

        # Extract request info
        method = request.method
        path = request.url.path
        endpoint = self._normalize_endpoint(path)

        # Track in-progress requests
        http_requests_in_progress.labels(method=method, endpoint=endpoint).inc()

        # Start timing
        start_time = time.time()

        # Log request start
        logger.info(
            "Request started",
            method=method,
            path=path,
            endpoint=endpoint,
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )

        response = None
        status_code = 500
        exception_type = None

        try:
            # Process request
            response = await call_next(request)
            status_code = response.status_code

            # Add correlation ID to response headers
            response.headers["X-Correlation-ID"] = correlation_id

            return response

        except Exception as e:
            # Record exception
            exception_type = type(e).__name__
            MetricsCollector.record_exception(exception_type, endpoint)

            logger.error(
                "Request failed with exception",
                method=method,
                path=path,
                endpoint=endpoint,
                exception_type=exception_type,
                error=str(e),
                exc_info=True,
            )

            # Trigger alert for critical errors
            if status_code >= 500:
                await trigger_alert(
                    name="http_server_error",
                    severity=AlertSeverity.CRITICAL,
                    message=f"Server error on {method} {path}",
                    details={
                        "method": method,
                        "path": path,
                        "status_code": status_code,
                        "exception": exception_type,
                        "error": str(e),
                    },
                )

            raise

        finally:
            # Calculate duration
            duration = time.time() - start_time

            # Record metrics
            MetricsCollector.record_request(method, endpoint, status_code, duration)

            # Update in-progress counter
            http_requests_in_progress.labels(method=method, endpoint=endpoint).dec()

            # Update system metrics periodically
            update_system_metrics()

            # Update uptime
            app_uptime_seconds.set(health_checker.get_uptime_seconds())

            # Log request completion
            log_level = (
                "error" if status_code >= 500 else "warning" if status_code >= 400 else "info"
            )
            log_method = getattr(logger, log_level)

            log_method(
                "Request completed",
                method=method,
                path=path,
                endpoint=endpoint,
                status_code=status_code,
                duration_seconds=round(duration, 3),
                exception_type=exception_type,
            )

            # Clear correlation ID
            correlation_processor.clear_correlation_id()

            # Alert on slow requests
            if duration > 5.0:  # 5 seconds threshold
                await trigger_alert(
                    name="slow_request",
                    severity=AlertSeverity.WARNING,
                    message=f"Slow request detected: {method} {path}",
                    details={
                        "method": method,
                        "path": path,
                        "duration_seconds": round(duration, 3),
                    },
                    metric_value=duration,
                    threshold=5.0,
                )

    @staticmethod
    def _normalize_endpoint(path: str) -> str:
        """Normalize endpoint path for metrics.
        Converts dynamic path parameters to placeholders.

        Example: /users/123 -> /users/{id}
        """
        # Skip normalization for health/metrics endpoints
        if path in ["/health", "/ready", "/metrics", "/docs", "/redoc", "/openapi.json"]:
            return path

        # Simple normalization - replace UUIDs and numeric IDs
        import re

        # Replace UUIDs
        path = re.sub(
            r"/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
            "/{uuid}",
            path,
            flags=re.IGNORECASE,
        )
        # Replace numeric IDs
        path = re.sub(r"/\d+", "/{id}", path)

        return path


class ErrorTrackingMiddleware(BaseHTTPMiddleware):
    """Middleware for error tracking and reporting."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with error tracking."""
        try:
            return await call_next(request)
        except Exception as e:
            # Log error with full context
            logger.error(
                "Unhandled exception",
                path=request.url.path,
                method=request.method,
                error=str(e),
                exc_info=True,
            )

            # Re-raise for proper error handling
            raise
