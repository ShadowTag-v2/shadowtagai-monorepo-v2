# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Tests for OTel histogram events and MCP Interactions wrapper."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest


class TestOTelHistogramEvents:
  """Verify the 3 new OTel histogram telemetry events."""

  def test_throttle_invocation_event(self):
    from telemetry.catalog import EventCatalog, EventCategory

    event = EventCatalog.throttle_invocation(
      function_name="refresh_cache",
      interval_ms=5000,
      was_suppressed=True,
      elapsed_since_last_ms=1200.5,
    )
    assert event.event == "agnt_throttle_invocation"
    assert event.category == EventCategory.TOOL
    assert event.duration_ms == 1200.5
    assert event.properties["function_name"] == "refresh_cache"
    assert event.properties["interval_ms"] == 5000
    assert event.properties["was_suppressed"] is True

  def test_throttle_invocation_defaults(self):
    from telemetry.catalog import EventCatalog

    event = EventCatalog.throttle_invocation()
    assert event.event == "agnt_throttle_invocation"
    assert event.properties["function_name"] == ""
    assert event.properties["was_suppressed"] is False

  def test_debounce_invocation_event(self):
    from telemetry.catalog import EventCatalog, EventCategory

    event = EventCatalog.debounce_invocation(
      function_name="auto_save",
      wait_ms=300,
      was_coalesced=True,
      max_wait_triggered=True,
      pending_duration_ms=950.0,
    )
    assert event.event == "agnt_debounce_invocation"
    assert event.category == EventCategory.TOOL
    assert event.duration_ms == 950.0
    assert event.properties["was_coalesced"] is True
    assert event.properties["max_wait_triggered"] is True

  def test_debounce_invocation_defaults(self):
    from telemetry.catalog import EventCatalog

    event = EventCatalog.debounce_invocation()
    assert event.event == "agnt_debounce_invocation"
    assert event.properties["was_coalesced"] is False
    assert event.properties["max_wait_triggered"] is False

  def test_cooldown_check_event(self):
    from telemetry.catalog import EventCatalog, EventCategory

    event = EventCatalog.cooldown_check(
      throttle_name="autoDream",
      cooldown_ms=86400000,
      was_allowed=False,
      time_until_next_ms=43200000,
    )
    assert event.event == "agnt_cooldown_check"
    assert event.category == EventCategory.TOOL
    assert event.properties["throttle_name"] == "autoDream"
    assert event.properties["was_allowed"] is False
    assert event.properties["time_until_next_ms"] == 43200000

  def test_cooldown_check_serialization(self):
    from telemetry.catalog import EventCatalog

    event = EventCatalog.cooldown_check(
      throttle_name="test", cooldown_ms=1000, was_allowed=True
    )
    d = event.to_dict()
    assert d["event"] == "agnt_cooldown_check"
    assert "properties" in d
    # Must be JSON-serializable
    json_str = json.dumps(d)
    assert "agnt_cooldown_check" in json_str


class TestInteractionsWrapper:
  """Test the MCP Interactions API tool wrapper."""

  def test_create_session(self):
    from mcp_tools.interactions_wrapper import (
      InteractionsModel,
      InteractionsTool,
      SessionState,
    )

    tool = InteractionsTool(api_key="test-key", session_dir=Path("/tmp/test_sessions"))
    session = tool.create_session(model=InteractionsModel.FLASH)

    assert session.session_id.startswith("interactions-")
    assert session.state == SessionState.ACTIVE
    assert session.model == InteractionsModel.FLASH
    assert session.turn_count == 0

  def test_send_turn(self):
    from mcp_tools.interactions_wrapper import InteractionsTool

    tool = InteractionsTool(api_key="test-key", session_dir=Path("/tmp/test_sessions"))
    session = tool.create_session()
    result = tool.send_turn(session.session_id, "What is 2+2?")

    assert result.text  # Stub response should be non-empty
    assert result.latency_ms >= 0
    assert result.finish_reason == "STOP"
    assert session.turn_count == 1

  def test_send_turn_increments(self):
    from mcp_tools.interactions_wrapper import InteractionsTool

    tool = InteractionsTool(api_key="test-key", session_dir=Path("/tmp/test_sessions"))
    session = tool.create_session()

    tool.send_turn(session.session_id, "Turn 1")
    tool.send_turn(session.session_id, "Turn 2")
    tool.send_turn(session.session_id, "Turn 3")

    assert session.turn_count == 3

  def test_close_session(self):
    from mcp_tools.interactions_wrapper import InteractionsTool

    tool = InteractionsTool(api_key="test-key", session_dir=Path("/tmp/test_sessions"))
    session = tool.create_session()
    sid = session.session_id

    assert tool.close_session(sid) is True
    assert tool.close_session(sid) is False  # Already closed
    assert len(tool.list_sessions()) == 0

  def test_max_turns_enforcement(self):
    from mcp_tools.interactions_wrapper import InteractionsTool

    tool = InteractionsTool(
      api_key="test-key",
      session_dir=Path("/tmp/test_sessions"),
      max_turns=3,
    )
    session = tool.create_session()

    tool.send_turn(session.session_id, "1")
    tool.send_turn(session.session_id, "2")
    tool.send_turn(session.session_id, "3")

    with pytest.raises(ValueError, match="exceeded max turns"):
      tool.send_turn(session.session_id, "4")

  def test_session_not_found(self):
    from mcp_tools.interactions_wrapper import InteractionsTool

    tool = InteractionsTool(api_key="test-key", session_dir=Path("/tmp/test_sessions"))

    with pytest.raises(ValueError, match="not found"):
      tool.send_turn("nonexistent", "hello")

  def test_resume_session(self, tmp_path):
    from mcp_tools.interactions_wrapper import (
      InteractionsTool,
      SessionState,
    )

    tool1 = InteractionsTool(api_key="test-key", session_dir=tmp_path)
    session = tool1.create_session()
    tool1.send_turn(session.session_id, "Turn 1")
    sid = session.session_id

    # New tool instance, same session dir
    tool2 = InteractionsTool(api_key="test-key", session_dir=tmp_path)
    resumed = tool2.resume_session(sid)

    assert resumed is not None
    assert resumed.session_id == sid
    assert resumed.turn_count == 1
    assert resumed.state == SessionState.ACTIVE

  def test_no_api_key_warning(self, caplog):
    import logging
    from unittest.mock import patch as mock_patch

    from mcp_tools.interactions_wrapper import InteractionsTool

    # Must remove GEMINI_API_KEY from env so the `or` fallback also yields ""
    with mock_patch.dict(os.environ, {}, clear=True), caplog.at_level(logging.WARNING):
      _tool = InteractionsTool(api_key="", session_dir=Path("/tmp/test_sessions"))  # noqa: F841
    assert "GEMINI_API_KEY" in caplog.text

  def test_list_sessions(self, tmp_path):
    from mcp_tools.interactions_wrapper import InteractionsTool

    tool = InteractionsTool(api_key="test-key", session_dir=tmp_path)
    tool.create_session()
    tool.create_session()

    assert len(tool.list_sessions()) == 2

  def test_model_enum(self):
    from mcp_tools.interactions_wrapper import InteractionsModel

    assert InteractionsModel.FLASH == "gemini-3.1-flash-lite-preview-thinking"
    assert InteractionsModel.PRO == "gemini-3.1-pro"


class TestSMCompactBenchmark:
  """Smoke-test the benchmark script imports and core logic."""

  def test_sm_compact_within_budget(self):
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from benchmarks.bench_sm_compact import sm_compact

    short_text = "Hello world. " * 10
    result = sm_compact(short_text, budget=4096)
    assert result == short_text  # No truncation needed

  def test_sm_compact_truncates(self):
    from benchmarks.bench_sm_compact import sm_compact

    long_text = "The quick brown fox jumps over the lazy dog. " * 2000
    result = sm_compact(long_text, budget=100)
    assert len(result) < len(long_text)

  def test_l1_l4_pipeline_truncates(self):
    from benchmarks.bench_sm_compact import l1_l4_pipeline

    long_text = "Attorney privilege analysis.\n\n" * 500
    result = l1_l4_pipeline(long_text, budget=200)
    assert len(result) < len(long_text)

  def test_benchmark_runner_returns_results(self):
    from benchmarks.bench_sm_compact import run_benchmark

    results = run_benchmark(iterations=5)
    assert "4KB" in results
    assert "16KB" in results
    for data in results.values():
      assert "speedup_x" in data
      assert data["sm_p50_ms"] >= 0
