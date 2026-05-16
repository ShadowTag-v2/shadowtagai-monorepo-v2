# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Telemetry — OpenTelemetry event logging and bootstrap.

Ported from src/utils/telemetry/ (Claude Code v2.1.91).
Covers: events.ts (75 lines), instrumentation.ts (767 lines) patterns.

This module provides a Python-native OTel event pipeline that mirrors
the CC architecture: sequence-numbered events, prompt redaction, and
lazy provider initialization. The actual OTLP exporter wiring is
deferred to runtime configuration (env vars or explicit setup).
"""

from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

logger = logging.getLogger(__name__)

# Monotonically increasing counter for ordering events within a session
_event_sequence: int = 0
_warned_no_logger: bool = False


class ExporterProtocol(StrEnum):
  """Supported OTLP exporter protocols."""

  GRPC = "grpc"
  HTTP_PROTOBUF = "http/protobuf"
  HTTP_JSON = "http/json"
  CONSOLE = "console"
  NONE = "none"


@dataclass
class TelemetryConfig:
  """Configuration for the telemetry subsystem."""

  service_name: str = "agnt-services"
  service_version: str = "2.2.0"
  metrics_export_interval_ms: int = 60_000
  logs_export_interval_ms: int = 5_000
  traces_export_interval_ms: int = 5_000
  exporter_protocol: ExporterProtocol = ExporterProtocol.NONE
  endpoint: str | None = None
  log_user_prompts: bool = False
  attributes: dict[str, str] = field(default_factory=dict)


# Global singleton config
_config: TelemetryConfig = TelemetryConfig()
_initialized: bool = False


def configure_telemetry(config: TelemetryConfig) -> None:
  """Set the global telemetry configuration.

  Should be called once at process startup before any events are emitted.
  """
  global _config, _initialized
  _config = config
  _initialized = True
  logger.debug(
    "Telemetry configured: service=%s, protocol=%s",
    config.service_name,
    config.exporter_protocol,
  )


def get_telemetry_config() -> TelemetryConfig:
  """Get the current telemetry configuration."""
  return _config


def is_telemetry_initialized() -> bool:
  """Check if telemetry has been explicitly configured."""
  return _initialized


# ─── Event Logging ────────────────────────────────────────────────────


def redact_if_disabled(content: str) -> str:
  """Redact content unless user prompt logging is explicitly enabled."""
  return content if _config.log_user_prompts else "<REDACTED>"


def _get_base_attributes() -> dict[str, Any]:
  """Build base telemetry attributes for every event."""
  attrs: dict[str, Any] = {
    "service.name": _config.service_name,
    "service.version": _config.service_version,
  }
  # Merge any custom attributes from config
  attrs.update(_config.attributes)
  return attrs


def log_otel_event(
  event_name: str,
  metadata: dict[str, str | None] | None = None,
  *,
  prompt_id: str | None = None,
) -> None:
  """Log a telemetry event with standard attributes.

  Events are sequence-numbered for ordering within a session.
  In test environments (PYTEST_CURRENT_TEST set), events are silently dropped.

  Args:
      event_name: The event name (will be prefixed with 'agnt.')
      metadata: Optional key-value pairs to include as attributes
      prompt_id: Optional prompt ID (excluded from metrics to avoid cardinality)
  """
  global _event_sequence, _warned_no_logger

  # Skip in test environment
  if os.environ.get("PYTEST_CURRENT_TEST"):
    return

  if not _initialized:
    if not _warned_no_logger:
      _warned_no_logger = True
      logger.debug("Event dropped (telemetry not initialized): %s", event_name)
    return

  attrs = _get_base_attributes()
  attrs["event.name"] = event_name
  attrs["event.timestamp"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
  attrs["event.sequence"] = _event_sequence
  _event_sequence += 1

  if prompt_id:
    attrs["prompt.id"] = prompt_id

  # Workspace paths (events only — too high-cardinality for metrics)
  workspace = os.environ.get("WORKSPACE_HOST_PATHS")
  if workspace:
    attrs["workspace.host_paths"] = workspace.split("|")

  if metadata:
    for key, value in metadata.items():
      if value is not None:
        attrs[key] = value

  # Emit via logging (can be intercepted by OTel log bridge)
  logger.info(
    "agnt.%s",
    event_name,
    extra={"otel_attributes": attrs},
  )


# ─── Convenience Event Helpers ────────────────────────────────────────


def log_tool_use(
  tool_name: str,
  duration_ms: float,
  success: bool,
  *,
  error: str | None = None,
) -> None:
  """Log a tool invocation event."""
  meta: dict[str, str | None] = {
    "tool.name": tool_name,
    "tool.duration_ms": str(round(duration_ms, 2)),
    "tool.success": str(success).lower(),
  }
  if error:
    meta["tool.error"] = error
  log_otel_event("tool_use", meta)


def log_model_request(
  model: str,
  input_tokens: int,
  output_tokens: int,
  duration_ms: float,
  *,
  cache_hit: bool = False,
) -> None:
  """Log a model inference request event."""
  log_otel_event(
    "model_request",
    {
      "model.name": model,
      "model.input_tokens": str(input_tokens),
      "model.output_tokens": str(output_tokens),
      "model.duration_ms": str(round(duration_ms, 2)),
      "model.cache_hit": str(cache_hit).lower(),
    },
  )


def log_session_event(
  event_type: str,
  *,
  session_id: str | None = None,
  details: str | None = None,
) -> None:
  """Log a session lifecycle event."""
  meta: dict[str, str | None] = {"session.event_type": event_type}
  if session_id:
    meta["session.id"] = session_id
  if details:
    meta["session.details"] = details
  log_otel_event("session", meta)


# ─── Bootstrap (OTel SDK wiring) ─────────────────────────────────────


def bootstrap_telemetry_from_env() -> TelemetryConfig:
  """Initialize telemetry from environment variables.

  Reads OTEL_* env vars matching the CC v2.1.91 pattern:
    - OTEL_EXPORTER_OTLP_PROTOCOL
    - OTEL_EXPORTER_OTLP_ENDPOINT
    - OTEL_LOG_USER_PROMPTS
    - OTEL_SERVICE_NAME / OTEL_SERVICE_VERSION
  """
  protocol_str = os.environ.get("OTEL_EXPORTER_OTLP_PROTOCOL", "none")
  try:
    protocol = ExporterProtocol(protocol_str)
  except ValueError:
    protocol = ExporterProtocol.NONE

  config = TelemetryConfig(
    service_name=os.environ.get("OTEL_SERVICE_NAME", "agnt-services"),
    service_version=os.environ.get("OTEL_SERVICE_VERSION", "2.2.0"),
    exporter_protocol=protocol,
    endpoint=os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT"),
    log_user_prompts=os.environ.get("OTEL_LOG_USER_PROMPTS", "").lower()
    in ("1", "true"),
  )

  configure_telemetry(config)
  return config
