# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Observability module for IT Helpdesk Agent — GEAP Part 5.

Configures OpenTelemetry (OTEL) with Cloud Trace and Cloud Logging
exporters for distributed tracing, structured logging, and metrics
collection. This module integrates with GCP's operations suite for
production-grade observability.

Prerequisites:
  - IAM: roles/logging.logWriter + roles/cloudtrace.agent on
    helpdesk-agent-sa@shadowtag-omega-v4.iam.gserviceaccount.com
  - Packages: opentelemetry-sdk, opentelemetry-exporter-gcp-trace,
    google-cloud-logging

Reference: GEAP Tutorial Series Part 5 — Observability & Evaluation
"""

from __future__ import annotations

import logging
import os
import sys
from contextlib import contextmanager
from typing import Generator

logger = logging.getLogger(__name__)

# --- Feature flags ---
OTEL_ENABLED = os.getenv("GEAP_OTEL_ENABLED", "true").lower() == "true"
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "shadowtag-omega-v4")
SERVICE_NAME = os.getenv("OTEL_SERVICE_NAME", "helpdesk-agent")
SERVICE_VERSION = os.getenv("OTEL_SERVICE_VERSION", "0.1.0")


def configure_cloud_logging() -> None:
    """Configure structured logging to Cloud Logging.

    When running on Agent Runtime / Cloud Run, Cloud Logging is
    available automatically via the google-cloud-logging client.
    Locally, falls back to standard Python logging.
    """
    try:
        import google.cloud.logging as cloud_logging

        client = cloud_logging.Client(project=PROJECT_ID)
        client.setup_logging(log_level=logging.INFO)
        logger.info(
            "Cloud Logging configured for project=%s, service=%s",
            PROJECT_ID,
            SERVICE_NAME,
        )
    except Exception:
        # Local dev fallback — structured console logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            stream=sys.stdout,
        )
        logger.info("Cloud Logging unavailable — using console fallback")


def configure_otel_tracing() -> None:
    """Configure OpenTelemetry with Cloud Trace exporter.

    Sets up the TracerProvider with a BatchSpanProcessor exporting
    to Cloud Trace. Adds resource attributes for service identification.

    The Cloud Trace exporter sends spans to:
      https://cloudtrace.googleapis.com

    IAM requirement:
      roles/cloudtrace.agent on the service account.
    """
    if not OTEL_ENABLED:
        logger.info("OTEL tracing disabled (GEAP_OTEL_ENABLED=false)")
        return

    try:
        from opentelemetry import trace
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        # Resource identifies the service in Cloud Trace
        resource = Resource.create(
            {
                "service.name": SERVICE_NAME,
                "service.version": SERVICE_VERSION,
                "cloud.provider": "gcp",
                "cloud.account.id": PROJECT_ID,
            }
        )

        provider = TracerProvider(resource=resource)

        # Try Cloud Trace exporter first, console fallback for local dev
        try:
            from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter

            exporter = CloudTraceSpanExporter(project_id=PROJECT_ID)
            provider.add_span_processor(BatchSpanProcessor(exporter))
            logger.info("Cloud Trace exporter configured for project=%s", PROJECT_ID)
        except ImportError:
            from opentelemetry.sdk.trace.export import ConsoleSpanExporter

            provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
            logger.info("Cloud Trace exporter unavailable — using console exporter")

        trace.set_tracer_provider(provider)
        logger.info("OpenTelemetry tracing initialized: service=%s", SERVICE_NAME)

    except ImportError:
        logger.warning(
            "OpenTelemetry SDK not installed. Run: "
            "pip install opentelemetry-sdk opentelemetry-exporter-gcp-trace"
        )
    except Exception:
        logger.exception("Failed to initialize OpenTelemetry tracing")


def get_tracer(name: str = __name__):
    """Get an OpenTelemetry tracer instance.

    Args:
        name: Tracer name, typically the module name.

    Returns:
        An OTEL Tracer or a no-op tracer if OTEL is disabled.
    """
    try:
        from opentelemetry import trace

        return trace.get_tracer(name)
    except ImportError:
        # Return a no-op tracer
        return _NoOpTracer()


class _NoOpTracer:
    """Minimal no-op tracer for when OTEL is not installed."""

    @contextmanager
    def start_as_current_span(
        self, name: str, **kwargs
    ) -> Generator[_NoOpSpan, None, None]:
        yield _NoOpSpan()

    def start_span(self, name: str, **kwargs) -> _NoOpSpan:
        return _NoOpSpan()


class _NoOpSpan:
    """Minimal no-op span."""

    def set_attribute(self, key: str, value: object) -> None:
        pass

    def set_status(self, status: object) -> None:
        pass

    def record_exception(self, exception: BaseException) -> None:
        pass

    def end(self) -> None:
        pass

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass


@contextmanager
def trace_tool_call(tool_name: str, **attributes) -> Generator[object, None, None]:
    """Context manager to trace an ADK tool call.

    Usage::

        with trace_tool_call("cmdb_lookup_asset", asset_id="LAPTOP-001"):
            result = cmdb_lookup_asset("LAPTOP-001")

    Args:
        tool_name: The name of the tool being called.
        **attributes: Additional span attributes.

    Yields:
        The active span (or no-op span).
    """
    tracer = get_tracer("helpdesk.tools")
    with tracer.start_as_current_span(
        f"tool.{tool_name}",
        attributes={
            "tool.name": tool_name,
            "agent.name": SERVICE_NAME,
            **{f"tool.param.{k}": str(v) for k, v in attributes.items()},
        },
    ) as span:
        yield span


def configure_genai_instrumentation() -> None:
    """Configure automatic instrumentation for Gemini API calls.

    Uses the opentelemetry-instrumentation-google-genai package to
    automatically trace all google.genai API calls, including:
    - Model invocations (generate_content)
    - Token usage metrics
    - Latency distributions

    This is already declared in pyproject.toml dependencies.
    """
    if not OTEL_ENABLED:
        return

    try:
        from opentelemetry.instrumentation.google_genai import (
            GoogleGenAiInstrumentor,
        )

        GoogleGenAiInstrumentor().instrument()
        logger.info("GenAI instrumentation enabled — tracing all model calls")
    except ImportError:
        logger.info(
            "google-genai instrumentation not available. "
            "Install: pip install opentelemetry-instrumentation-google-genai"
        )
    except Exception:
        logger.exception("Failed to enable GenAI instrumentation")


def initialize_observability() -> None:
    """Initialize all observability components.

    Call this once at application startup (before agent initialization).
    Configures:
    1. Cloud Logging (structured logs → Cloud Logging)
    2. OpenTelemetry tracing (spans → Cloud Trace)
    3. GenAI auto-instrumentation (model call tracing)
    """
    logger.info(
        "Initializing observability stack for %s v%s", SERVICE_NAME, SERVICE_VERSION
    )
    configure_cloud_logging()
    configure_otel_tracing()
    configure_genai_instrumentation()
    logger.info("Observability stack initialized successfully")
