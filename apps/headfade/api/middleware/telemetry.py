"""
OpenTelemetry instrumentation for HeadFade API.

Provides Cloud Trace-compatible spans for request latency tracking,
HDI quality monitoring, and forensic analysis timing. Automatically
exports to Google Cloud Trace when running on Cloud Run.

Usage:
    from middleware.telemetry import instrument_app
    instrument_app(app)  # Call once after app creation
"""

import logging
import os

logger = logging.getLogger("headfade.telemetry")

_OTEL_ENABLED = os.environ.get("OTEL_ENABLED", "true").lower() == "true"


def instrument_app(app):
  """Instrument a FastAPI app with OpenTelemetry + Cloud Trace exporter.

  Silently degrades if opentelemetry packages are not installed.
  """
  if not _OTEL_ENABLED:
    logger.info("OpenTelemetry instrumentation disabled via OTEL_ENABLED=false")
    return

  try:
    from opentelemetry import trace
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor

    provider = TracerProvider()

    # Cloud Trace exporter for GCP — falls back to console if not on Cloud Run
    try:
      from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter

      exporter = CloudTraceSpanExporter(
        project_id=os.environ.get("GOOGLE_CLOUD_PROJECT", "shadowtag-omega-v4"),
      )
      provider.add_span_processor(BatchSpanProcessor(exporter))
      logger.info(
        "Cloud Trace exporter attached for project %s",
        os.environ.get("GOOGLE_CLOUD_PROJECT", "shadowtag-omega-v4"),
      )
    except ImportError:
      from opentelemetry.sdk.trace.export import ConsoleSpanExporter

      provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
      logger.info("Cloud Trace exporter not available, using console exporter")

    trace.set_tracer_provider(provider)
    FastAPIInstrumentor.instrument_app(app)
    logger.info("OpenTelemetry FastAPI instrumentation active")

  except ImportError as e:
    logger.warning(
      "OpenTelemetry packages not installed, skipping instrumentation: %s", e
    )


def get_tracer(name: str = "headfade-api"):
  """Get a named tracer for manual span creation.

  Usage:
      tracer = get_tracer()
      with tracer.start_as_current_span("hdi_vote_processing") as span:
          span.set_attribute("video_id", video_id)
          ...
  """
  try:
    from opentelemetry import trace

    return trace.get_tracer(name)
  except ImportError:
    return _NoopTracer()


class _NoopTracer:
  """Fallback tracer when OpenTelemetry is not installed."""

  def start_as_current_span(self, name, **kwargs):
    return _NoopSpan()


class _NoopSpan:
  """Fallback span that does nothing."""

  def __enter__(self):
    return self

  def __exit__(self, *args):
    pass

  def set_attribute(self, key, value):
    pass

  def add_event(self, name, attributes=None):
    pass
