# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Tests for deep_research.telemetry module."""

from __future__ import annotations

import json
from pathlib import Path
from unittest import mock


from deep_research.telemetry import (
  _write_event,
  emit_evaluation_event,
  emit_phase_event,
  emit_research_metric,
  emit_sandbox_event,
)


class FakeTransition:
  """Minimal stand-in for PhaseTransition."""

  def __init__(
    self, from_phase: str, to_phase: str, success: bool = True, error: str | None = None
  ):
    self.from_phase = type("P", (), {"value": from_phase})()
    self.to_phase = type("P", (), {"value": to_phase})()
    self.duration_ms = 42.0
    self.success = success
    self.error = error
    self.metadata = {"session_id": "dr-test123"}


class TestWriteEvent:
  def test_writes_jsonl(self, tmp_path: Path) -> None:
    log_file = tmp_path / "telemetry.jsonl"
    with mock.patch("deep_research.telemetry._TELEMETRY_PATH", log_file):
      _write_event({"type": "test", "value": 1})
    lines = log_file.read_text().strip().split("\n")
    assert len(lines) == 1
    data = json.loads(lines[0])
    assert data["type"] == "test"
    assert data["value"] == 1


class TestEmitPhaseEvent:
  def test_emits_transition(self, tmp_path: Path) -> None:
    log_file = tmp_path / "telemetry.jsonl"
    with mock.patch("deep_research.telemetry._TELEMETRY_PATH", log_file):
      t = FakeTransition("idle", "planning")
      emit_phase_event(t)
    data = json.loads(log_file.read_text().strip())
    assert data["type"] == "deep_research.phase_transition"
    assert data["from_phase"] == "idle"
    assert data["to_phase"] == "planning"
    assert data["success"] is True


class TestEmitResearchMetric:
  def test_emits_metric(self, tmp_path: Path) -> None:
    log_file = tmp_path / "telemetry.jsonl"
    with mock.patch("deep_research.telemetry._TELEMETRY_PATH", log_file):
      emit_research_metric("dr-test", "queries", 42.0, {"source": "gdk"})
    data = json.loads(log_file.read_text().strip())
    assert data["metric"] == "queries"
    assert data["value"] == 42.0


class TestEmitSandboxEvent:
  def test_emits_sandbox(self, tmp_path: Path) -> None:
    log_file = tmp_path / "telemetry.jsonl"
    with mock.patch("deep_research.telemetry._TELEMETRY_PATH", log_file):
      emit_sandbox_event("dr-test", "create", "sb-abc123def456")
    data = json.loads(log_file.read_text().strip())
    assert data["type"] == "deep_research.sandbox"
    assert data["action"] == "create"


class TestEmitEvaluationEvent:
  def test_emits_eval(self, tmp_path: Path) -> None:
    log_file = tmp_path / "telemetry.jsonl"
    with mock.patch("deep_research.telemetry._TELEMETRY_PATH", log_file):
      emit_evaluation_event("dr-test", "build", True, {"exit_code": 0})
    data = json.loads(log_file.read_text().strip())
    assert data["type"] == "deep_research.evaluation"
    assert data["step"] == "build"
    assert data["passed"] is True
