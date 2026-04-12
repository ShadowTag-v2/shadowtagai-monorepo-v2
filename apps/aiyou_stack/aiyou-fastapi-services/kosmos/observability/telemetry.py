"""
OpenTelemetry Integration: Cloud Trace integration for distributed tracing.

Provides:
- Automatic span creation for agent operations
- Trace hierarchy for multi-agent workflows
- Integration with Google Cloud Trace
- Custom attributes for agent context
"""

from __future__ import annotations

import logging
from typing import Any

try:
    from opentelemetry import trace
    from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor

    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False
    logging.warning(
        "OpenTelemetry not installed. "
        "Install with: pip install opentelemetry-api opentelemetry-sdk "
        "opentelemetry-exporter-gcp-trace"
    )

logger = logging.getLogger(__name__)


def setup_telemetry(
    project_id: str,
    service_name: str = "kosmos-agents",
    enable_trace: bool = True,
) -> trace.Tracer | None:
    """
    Set up OpenTelemetry with Cloud Trace integration.

    Args:
        project_id: GCP project ID
        service_name: Service name for trace identification
        enable_trace: Whether to enable tracing

    Returns:
        Tracer instance if successful, None otherwise
    """
    if not OTEL_AVAILABLE:
        logger.warning("OpenTelemetry not available - tracing disabled")
        return None

    if not enable_trace:
        logger.info("Tracing disabled by configuration")
        return None

    try:
        # Create resource with service information
        resource = Resource.create(
            {
                "service.name": service_name,
                "service.version": "0.1.0",
            }
        )

        # Create tracer provider
        tracer_provider = TracerProvider(resource=resource)

        # Configure Cloud Trace exporter
        cloud_trace_exporter = CloudTraceSpanExporter(project_id=project_id)

        # Add batch span processor for efficient export
        tracer_provider.add_span_processor(BatchSpanProcessor(cloud_trace_exporter))

        # Set as global tracer provider
        trace.set_tracer_provider(tracer_provider)

        logger.info(f"OpenTelemetry configured with Cloud Trace for project {project_id}")

        return trace.get_tracer(__name__)

    except Exception as e:
        logger.error(f"Failed to setup telemetry: {e}")
        return None


def get_tracer(name: str | None = None) -> trace.Tracer:
    """
    Get a tracer instance.

    Args:
        name: Optional tracer name (defaults to module name)

    Returns:
        Tracer instance
    """
    if not OTEL_AVAILABLE:
        # Return no-op tracer
        return trace.get_tracer(name or __name__)

    return trace.get_tracer(name or __name__)


class TracedOperation:
    """
    Context manager for tracing an operation.

    Example:
        with TracedOperation("agent_execution", agent="literature", goal="search papers"):
            # Perform agent operation
            result = agent.execute_task(goal)
    """

    def __init__(
        self,
        operation_name: str,
        tracer: trace.Tracer | None = None,
        **attributes,
    ):
        """
        Initialize traced operation.

        Args:
            operation_name: Name of the operation (span name)
            tracer: Optional tracer instance (uses default if None)
            **attributes: Additional span attributes
        """
        self.operation_name = operation_name
        self.tracer = tracer or get_tracer()
        self.attributes = attributes
        self.span: trace.Span | None = None

    def __enter__(self) -> trace.Span:
        """Start span on context entry."""
        if not OTEL_AVAILABLE:
            return None

        self.span = self.tracer.start_span(self.operation_name)

        # Set attributes
        if self.span and hasattr(self.span, "set_attribute"):
            for key, value in self.attributes.items():
                try:
                    self.span.set_attribute(key, value)
                except Exception as e:
                    logger.debug(f"Failed to set attribute {key}: {e}")

        return self.span

    def __exit__(self, exc_type, exc_val, exc_tb):
        """End span on context exit."""
        if self.span and hasattr(self.span, "end"):
            # Record exception if present
            if exc_type:
                self.span.set_attribute("error", True)
                self.span.set_attribute("error.type", exc_type.__name__)
                self.span.set_attribute("error.message", str(exc_val))

            self.span.end()


def trace_react_cycle(
    tracer: trace.Tracer | None = None,
) -> callable:
    """
    Decorator for tracing ReAct cycles.

    Example:
        @trace_react_cycle()
        def execute_cycle(self, goal):
            # ReAct loop implementation
            pass
    """
    tracer = tracer or get_tracer()

    def decorator(func):
        def wrapper(*args, **kwargs):
            if not OTEL_AVAILABLE:
                return func(*args, **kwargs)

            with TracedOperation(
                f"react_cycle.{func.__name__}",
                tracer=tracer,
                goal=kwargs.get("goal", "unknown"),
            ):
                return func(*args, **kwargs)

        return wrapper

    return decorator


def add_span_attributes(span: trace.Span | None, **attributes):
    """
    Add attributes to current span.

    Args:
        span: Span instance
        **attributes: Attributes to add
    """
    if not OTEL_AVAILABLE or not span:
        return

    if hasattr(span, "set_attribute"):
        for key, value in attributes.items():
            try:
                # Convert complex types to strings
                if isinstance(value, (dict, list)):
                    value = str(value)
                span.set_attribute(key, value)
            except Exception as e:
                logger.debug(f"Failed to set attribute {key}: {e}")


def trace_agent_execution(
    agent_name: str,
    task: str,
    tracer: trace.Tracer | None = None,
) -> TracedOperation:
    """
    Create a traced operation for agent execution.

    Args:
        agent_name: Name of the agent
        task: Task description
        tracer: Optional tracer instance

    Returns:
        TracedOperation context manager
    """
    return TracedOperation(
        "agent_execution",
        tracer=tracer,
        agent_name=agent_name,
        task=task[:200],  # Truncate long tasks
    )


def trace_tool_invocation(
    tool_name: str,
    tool_input: Any,
    tracer: trace.Tracer | None = None,
) -> TracedOperation:
    """
    Create a traced operation for tool invocation.

    Args:
        tool_name: Name of the tool
        tool_input: Tool input parameters
        tracer: Optional tracer instance

    Returns:
        TracedOperation context manager
    """
    return TracedOperation(
        "tool_invocation",
        tracer=tracer,
        tool_name=tool_name,
        tool_input=str(tool_input)[:200],  # Truncate
    )
