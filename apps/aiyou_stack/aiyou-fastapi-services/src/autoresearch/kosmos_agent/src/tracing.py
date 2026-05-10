import os

from opentelemetry import trace
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter


def setup_tracing(service_name: str = "kosmos-agent"):
    """Configures OpenTelemetry tracing with Google Cloud Trace.
    If GOOGLE_CLOUD_PROJECT is not set, falls back to Console exporter.
    """
    resource = Resource.create(
        {
            "service.name": service_name,
        },
    )

    provider = TracerProvider(resource=resource)

    # Check if running in GCP context
    if os.getenv("GOOGLE_CLOUD_PROJECT"):
        try:
            exporter = CloudTraceSpanExporter()
            processor = BatchSpanProcessor(exporter)
            provider.add_span_processor(processor)
        except Exception as e:
            print(f"Failed to initialize Cloud Trace exporter: {e}")
            # Fallback
            provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
    else:
        # Local development fallback
        provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

    trace.set_tracer_provider(provider)
    return trace.get_tracer(service_name)


tracer = setup_tracing()
