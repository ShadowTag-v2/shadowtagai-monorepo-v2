# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Tests for packages.agnt_services.telemetry_events (port of src/utils/telemetry/)."""

from __future__ import annotations

import os
from unittest.mock import patch

import pytest

from packages.agnt_services.telemetry_events import (
  ExporterProtocol,
  TelemetryConfig,
  bootstrap_telemetry_from_env,
  configure_telemetry,
  get_telemetry_config,
  is_telemetry_initialized,
  log_model_request,
  log_otel_event,
  log_session_event,
  log_tool_use,
  redact_if_disabled,
)


@pytest.fixture(autouse=True)
def _reset_telemetry():
  """Reset telemetry state before each test."""
  import packages.agnt_services.telemetry_events as mod

  mod._config = TelemetryConfig()
  mod._initialized = False
  mod._event_sequence = 0
  mod._warned_no_logger = False
  yield


# ─── Configuration ────────────────────────────────────────────────────


class TestTelemetryConfig:
  def test_defaults(self):
    cfg = TelemetryConfig()
    assert cfg.service_name == "agnt-services"
    assert cfg.exporter_protocol == ExporterProtocol.NONE
    assert cfg.log_user_prompts is False

  def test_custom_config(self):
    cfg = TelemetryConfig(
      service_name="test-svc",
      exporter_protocol=ExporterProtocol.GRPC,
      endpoint="http://localhost:4317",
    )
    assert cfg.service_name == "test-svc"
    assert cfg.exporter_protocol == ExporterProtocol.GRPC
    assert cfg.endpoint == "http://localhost:4317"

  def test_configure_sets_global(self):
    cfg = TelemetryConfig(service_name="configured")
    configure_telemetry(cfg)
    assert get_telemetry_config().service_name == "configured"
    assert is_telemetry_initialized() is True

  def test_not_initialized_by_default(self):
    assert is_telemetry_initialized() is False


# ─── Redaction ────────────────────────────────────────────────────────


class TestRedaction:
  def test_redacts_by_default(self):
    assert redact_if_disabled("secret text") == "<REDACTED>"

  def test_passes_through_when_enabled(self):
    configure_telemetry(TelemetryConfig(log_user_prompts=True))
    assert redact_if_disabled("secret text") == "secret text"


# ─── Event Logging ────────────────────────────────────────────────────


class TestLogOtelEvent:
  def test_drops_when_not_initialized(self, caplog):
    # Should not raise, just drop silently
    log_otel_event("test_event")

  def test_emits_when_initialized(self, caplog):
    configure_telemetry(TelemetryConfig())
    with patch.dict(os.environ, {}, clear=False):
      # Remove PYTEST_CURRENT_TEST to allow event emission
      env = os.environ.copy()
      env.pop("PYTEST_CURRENT_TEST", None)
      with patch.dict(os.environ, env, clear=True):
        import logging

        with caplog.at_level(logging.INFO):
          log_otel_event("test_event", {"key": "value"})
        assert any("test_event" in r.message for r in caplog.records)

  def test_sequence_increments(self):
    import packages.agnt_services.telemetry_events as mod

    configure_telemetry(TelemetryConfig())
    assert mod._event_sequence == 0
    with patch.dict(os.environ, {}, clear=True):
      log_otel_event("first")
      log_otel_event("second")
    assert mod._event_sequence == 2

  def test_skips_none_metadata_values(self):
    configure_telemetry(TelemetryConfig())
    # Should not raise even with None values
    with patch.dict(os.environ, {}, clear=True):
      log_otel_event("test", {"key": None, "valid": "yes"})


# ─── Convenience Helpers ──────────────────────────────────────────────


class TestConvenienceHelpers:
  def test_log_tool_use(self):
    configure_telemetry(TelemetryConfig())
    with patch.dict(os.environ, {}, clear=True):
      log_tool_use("read_file", 42.5, True)  # Should not raise

  def test_log_tool_use_with_error(self):
    configure_telemetry(TelemetryConfig())
    with patch.dict(os.environ, {}, clear=True):
      log_tool_use("write_file", 100.0, False, error="EPERM")

  def test_log_model_request(self):
    configure_telemetry(TelemetryConfig())
    with patch.dict(os.environ, {}, clear=True):
      log_model_request("gemini-3.1-flash", 1000, 500, 1234.5)

  def test_log_model_request_cache_hit(self):
    configure_telemetry(TelemetryConfig())
    with patch.dict(os.environ, {}, clear=True):
      log_model_request("gemini-3.1-flash", 1000, 500, 50.0, cache_hit=True)

  def test_log_session_event(self):
    configure_telemetry(TelemetryConfig())
    with patch.dict(os.environ, {}, clear=True):
      log_session_event("start", session_id="abc-123")

  def test_log_session_event_with_details(self):
    configure_telemetry(TelemetryConfig())
    with patch.dict(os.environ, {}, clear=True):
      log_session_event("error", details="Connection timeout")


# ─── Bootstrap from Environment ───────────────────────────────────────


class TestBootstrapFromEnv:
  def test_defaults_from_empty_env(self):
    with patch.dict(os.environ, {}, clear=True):
      cfg = bootstrap_telemetry_from_env()
    assert cfg.exporter_protocol == ExporterProtocol.NONE
    assert cfg.service_name == "agnt-services"
    assert is_telemetry_initialized() is True

  def test_reads_grpc_protocol(self):
    with patch.dict(os.environ, {"OTEL_EXPORTER_OTLP_PROTOCOL": "grpc"}, clear=True):
      cfg = bootstrap_telemetry_from_env()
    assert cfg.exporter_protocol == ExporterProtocol.GRPC

  def test_reads_endpoint(self):
    env = {
      "OTEL_EXPORTER_OTLP_PROTOCOL": "http/protobuf",
      "OTEL_EXPORTER_OTLP_ENDPOINT": "http://otel-collector:4318",
    }
    with patch.dict(os.environ, env, clear=True):
      cfg = bootstrap_telemetry_from_env()
    assert cfg.endpoint == "http://otel-collector:4318"

  def test_reads_user_prompt_logging(self):
    with patch.dict(os.environ, {"OTEL_LOG_USER_PROMPTS": "true"}, clear=True):
      cfg = bootstrap_telemetry_from_env()
    assert cfg.log_user_prompts is True

  def test_invalid_protocol_defaults_none(self):
    with patch.dict(os.environ, {"OTEL_EXPORTER_OTLP_PROTOCOL": "invalid"}, clear=True):
      cfg = bootstrap_telemetry_from_env()
    assert cfg.exporter_protocol == ExporterProtocol.NONE


# ─── ExporterProtocol Enum ────────────────────────────────────────────


class TestExporterProtocol:
  def test_all_values(self):
    assert ExporterProtocol.GRPC == "grpc"
    assert ExporterProtocol.HTTP_PROTOBUF == "http/protobuf"
    assert ExporterProtocol.HTTP_JSON == "http/json"
    assert ExporterProtocol.CONSOLE == "console"
    assert ExporterProtocol.NONE == "none"

  def test_is_str_enum(self):
    assert isinstance(ExporterProtocol.GRPC, str)
