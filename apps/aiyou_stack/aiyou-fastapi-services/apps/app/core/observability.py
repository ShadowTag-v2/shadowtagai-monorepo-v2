"""Observability setup using OpenTelemetry"""

import logging

from fastapi import FastAPI
from opentelemetry import metrics as otel_metrics
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class Metrics:
    """Application metrics collector"""

    def __init__(self):
        self.meter = None
        self.request_counter = None
        self.request_duration = None
        self.error_counter = None

    def initialize(self):
        """Initialize metrics"""
        try:
            self.meter = otel_metrics.get_meter(__name__)

            self.request_counter = self.meter.create_counter(
                "http_requests_total",
                description="Total HTTP requests",
                unit="1",
            )

            self.request_duration = self.meter.create_histogram(
                "http_request_duration_seconds",
                description="HTTP request duration",
                unit="s",
            )

            self.error_counter = self.meter.create_counter(
                "http_errors_total",
                description="Total HTTP errors",
                unit="1",
            )

            logger.info("Metrics initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize metrics: {e}")

    def record_request(self, method: str, path: str, status_code: int, duration: float):
        """Record HTTP request metrics"""
        if not self.request_counter or not self.request_duration:
            return

        try:
            attributes = {
                "method": method,
                "path": path,
                "status_code": str(status_code),
            }

            self.request_counter.add(1, attributes)
            self.request_duration.record(duration, attributes)

            if status_code >= 400:
                self.error_counter.add(1, attributes)
        except Exception as e:
            logger.debug(f"Failed to record metrics: {e}")

    def record_decision(
        self,
        latency_ms: float,
        cost_usd: float,
        confidence: float,
        risk_tier: int,
        violations_count: int,
        success: bool,
    ):
        """Record decision metrics"""

    def record_kernel_execution(
        self,
        kernel_name: str,
        latency_ms: float,
        success: bool,
        tokens_input: int = None,
        tokens_output: int = None,
    ):
        """Record kernel execution metrics"""


# Global metrics instance
metrics = Metrics()


def setup_observability(app: FastAPI):
    """Setup OpenTelemetry observability"""
    resource = Resource.create(
        {
            "service.name": settings.service_name,
            "service.version": settings.service_version,
            "deployment.environment": settings.environment,
        },
    )

    # Setup tracing
    if settings.enable_tracing:
        try:
            tracer_provider = TracerProvider(resource=resource)
            trace.set_tracer_provider(tracer_provider)

            # Instrument FastAPI
            FastAPIInstrumentor.instrument_app(app)

            logger.info("Tracing enabled")
        except Exception as e:
            logger.warning(f"Failed to setup tracing: {e}")

    # Setup metrics
    if settings.enable_metrics:
        try:
            meter_provider = MeterProvider(resource=resource)
            otel_metrics.set_meter_provider(meter_provider)

            # Initialize custom metrics
            metrics.initialize()

            logger.info("Metrics enabled")
        except Exception as e:
            logger.warning(f"Failed to setup metrics: {e}")
