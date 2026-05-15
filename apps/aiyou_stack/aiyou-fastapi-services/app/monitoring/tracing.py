"""OpenTelemetry distributed tracing configuration.
Provides end-to-end request tracing across services.
"""

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, SERVICE_VERSION, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from app.config import settings


def setup_tracing() -> TracerProvider | None:
    """Configure OpenTelemetry tracing for the application.

    Returns:
        TracerProvider instance if tracing is enabled, None otherwise

    """
    if not settings.enable_tracing:
        return None

    # Create resource with service information
    resource = Resource.create(
        {
            SERVICE_NAME: settings.otel_service_name,
            SERVICE_VERSION: settings.app_version,
            "environment": settings.environment,
        },
    )

    # Create tracer provider
    provider = TracerProvider(resource=resource)

    # Configure OTLP exporter
    otlp_exporter = OTLPSpanExporter(
        endpoint=settings.otel_exporter_otlp_endpoint,
        insecure=settings.otel_exporter_otlp_insecure,
    )

    # Add span processor
    provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

    # Set global tracer provider
    trace.set_tracer_provider(provider)

    # Instrument logging to include trace context
    LoggingInstrumentor().instrument(set_logging_format=True)

    return provider


def instrument_fastapi(app):
    """Instrument FastAPI application with OpenTelemetry.

    Args:
        app: FastAPI application instance

    """
    if settings.enable_tracing:
        FastAPIInstrumentor.instrument_app(app)


def get_tracer(name: str) -> trace.Tracer:
    """Get a tracer instance for creating spans.

    Args:
        name: Tracer name (typically __name__ of the calling module)

    Returns:
        Tracer instance

    """
    return trace.get_tracer(name)


def create_span(name: str, attributes: dict | None = None):
    """Context manager for creating a custom span.

    Usage:
        with create_span("operation_name", {"key": "value"}):
            # Your code here
            pass

    Args:
        name: Span name
        attributes: Optional attributes to attach to the span

    """
    tracer = trace.get_tracer(__name__)
    span = tracer.start_span(name)

    if attributes:
        for key, value in attributes.items():
            span.set_attribute(key, value)

    return span
