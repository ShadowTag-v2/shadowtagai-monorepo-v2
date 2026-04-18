# apps/counselconduit/api/telemetry.py
"""OpenTelemetry Cloud Trace integration for CounselConduit.

Configures the OTLP exporter to send traces to Google Cloud Trace.
Auto-instruments FastAPI with request spans.

Usage:
    from api.telemetry import setup_telemetry
    setup_telemetry(app)
"""

from __future__ import annotations

import logging
import os

logger = logging.getLogger("counselconduit.telemetry")


def setup_telemetry(app: object) -> None:
    """Initialize OpenTelemetry with Cloud Trace exporter.

    Args:
        app: FastAPI application instance.
    """
    service_name = os.getenv("OTEL_SERVICE_NAME", "counselconduit")
    otel_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "")

    if not otel_endpoint:
        logger.info("OTEL_EXPORTER_OTLP_ENDPOINT not set — tracing disabled")
        return

    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
            OTLPSpanExporter,
        )
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        resource = Resource.create({
            "service.name": service_name,
            "service.version": "3.1.0",
            "deployment.environment": os.getenv("ENVIRONMENT", "production"),
        })

        provider = TracerProvider(resource=resource)
        exporter = OTLPSpanExporter(endpoint=otel_endpoint, insecure=False)
        provider.add_span_processor(BatchSpanProcessor(exporter))
        trace.set_tracer_provider(provider)

        FastAPIInstrumentor.instrument_app(app)  # type: ignore[arg-type]

        logger.info(
            "OTEL initialized: service=%s endpoint=%s",
            service_name,
            otel_endpoint,
        )

    except ImportError as e:
        logger.warning("OTEL instrumentation unavailable: %s", e)
    except Exception as e:
        logger.error("OTEL setup failed: %s", e)
