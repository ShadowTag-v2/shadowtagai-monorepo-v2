"""
test_sovereign_orchestrator.py — Tests for the Autonomous Pipeline Orchestrator

Covers:
  - Pipeline phases (triage, diagnose, budget check, heal, document)
  - Rate limiting for healing actions
  - Budget-gated execution
  - HTTP handler
"""

from __future__ import annotations

import base64
import json
import time
from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest

import sovereign_orchestrator as orch


# ─── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture(autouse=True)
def _reset_heal_timestamps():
  """Clear heal timestamps between tests."""
  orch._heal_timestamps.clear()
  yield
  orch._heal_timestamps.clear()


def _make_healing_request(
  table: str = "users", change_type: str = "INSERT"
) -> orch.HealingRequest:
  return orch.HealingRequest(
    source="test",
    table=table,
    change_type=change_type,
    timestamp=datetime.now(tz=UTC).isoformat(),
  )


# ─── Triage ────────────────────────────────────────────────────────────────────


class TestTriage:
  """Tests for the triage phase."""

  def test_critical_tables_high_urgency(self):
    req = _make_healing_request(table="transactions")
    result = orch._phase_triage(req)
    assert result["is_critical"] is True
    assert result["urgency"] == "HIGH"

  def test_non_critical_tables_low_urgency(self):
    req = _make_healing_request(table="audit_logs")
    result = orch._phase_triage(req)
    assert result["is_critical"] is False
    assert result["urgency"] == "LOW"

  def test_all_critical_tables_recognized(self):
    for table in ["users", "transactions", "sessions", "cases"]:
      req = _make_healing_request(table=table)
      result = orch._phase_triage(req)
      assert result["is_critical"] is True, f"{table} should be critical"


# ─── Budget Check ──────────────────────────────────────────────────────────────


class TestBudgetCheck:
  """Tests for the budget check phase."""

  def test_returns_status_from_finops(self):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "GREEN"}

    with patch("httpx.get", return_value=mock_response):
      status = orch._phase_budget_check()
    assert status == "GREEN"

  def test_defaults_to_yellow_on_error(self):
    with patch("httpx.get", side_effect=ConnectionError("timeout")):
      status = orch._phase_budget_check()
    assert status == "YELLOW"


# ─── Heal Phase ────────────────────────────────────────────────────────────────


class TestHealPhase:
  """Tests for the healing phase."""

  def test_noop_with_no_recommendations(self):
    diagnosis = {"table": "users", "recommendations": []}
    action, actions = orch._phase_heal(diagnosis)
    assert action == orch.HealingAction.NOOP
    assert actions == []

  def test_index_recommendation_detected(self):
    diagnosis = {
      "table": "users",
      "recommendations": [
        {"type": "INDEX_RECOMMENDATION", "reason": "slow query", "table": "users"}
      ],
    }
    action, actions = orch._phase_heal(diagnosis)
    assert action == orch.HealingAction.INDEX_RECOMMENDATION
    assert len(actions) == 1
    assert "INDEX_REC" in actions[0]

  def test_query_rewrite_detected(self):
    diagnosis = {
      "table": "sessions",
      "recommendations": [{"type": "QUERY_REWRITE", "table": "sessions"}],
    }
    action, actions = orch._phase_heal(diagnosis)
    assert action == orch.HealingAction.QUERY_REWRITE


# ─── Rate Limiter ──────────────────────────────────────────────────────────────


class TestHealRateLimiter:
  """Tests for the healing rate limiter."""

  def test_allows_under_limit(self):
    assert orch._check_heal_rate() is True

  def test_blocks_over_limit(self):
    for _ in range(orch.MAX_HEALS_PER_HOUR):
      orch._record_heal()
    assert orch._check_heal_rate() is False

  def test_window_expiry(self):
    orch._heal_timestamps.append(time.time() - 7200)  # 2 hours ago
    assert orch._check_heal_rate() is True


# ─── Full Pipeline ─────────────────────────────────────────────────────────────


class TestFullPipeline:
  """Tests for the run_pipeline function."""

  def test_low_urgency_skips_to_complete(self):
    req = _make_healing_request(table="audit_logs")
    with patch.object(orch, "_phase_document"):
      result = orch.run_pipeline(req)
    assert result.phase == orch.OrchestratorPhase.COMPLETE
    assert result.healing_action == orch.HealingAction.NOOP

  def test_red_budget_aborts_pipeline(self):
    req = _make_healing_request(table="users")
    with (
      patch.object(
        orch,
        "_phase_diagnose",
        return_value={"table": "users", "health": "DEGRADED", "recommendations": []},
      ),
      patch.object(orch, "_phase_budget_check", return_value="RED"),
      patch.object(orch, "_phase_document"),
    ):
      result = orch.run_pipeline(req)
    assert result.phase == orch.OrchestratorPhase.ABORTED
    assert "Budget RED" in result.error

  def test_heal_rate_limit_aborts(self):
    for _ in range(orch.MAX_HEALS_PER_HOUR):
      orch._record_heal()

    req = _make_healing_request(table="transactions")
    with (
      patch.object(
        orch,
        "_phase_diagnose",
        return_value={
          "table": "transactions",
          "health": "DEGRADED",
          "recommendations": [{"type": "INDEX_RECOMMENDATION"}],
        },
      ),
      patch.object(orch, "_phase_budget_check", return_value="GREEN"),
      patch.object(orch, "_phase_document"),
    ):
      result = orch.run_pipeline(req)
    assert result.phase == orch.OrchestratorPhase.ABORTED
    assert "rate limit" in result.error.lower()

  def test_successful_healing_pipeline(self):
    req = _make_healing_request(table="users")
    diagnosis = {
      "table": "users",
      "health": "DEGRADED",
      "recommendations": [
        {"type": "INDEX_RECOMMENDATION", "reason": "slow query", "table": "users"}
      ],
    }
    with (
      patch.object(orch, "_phase_diagnose", return_value=diagnosis),
      patch.object(orch, "_phase_budget_check", return_value="GREEN"),
      patch.object(orch, "_phase_document"),
    ):
      result = orch.run_pipeline(req)
    assert result.phase == orch.OrchestratorPhase.COMPLETE
    assert result.healing_action == orch.HealingAction.INDEX_RECOMMENDATION
    assert len(result.actions_taken) >= 1


# ─── HTTP Handler ──────────────────────────────────────────────────────────────


class TestHTTPHandler:
  """Tests for the handle_healing_request HTTP function."""

  def test_returns_200_on_success(self):
    request = MagicMock()
    data = {"table": "users", "change_type": "INSERT", "source": "test"}
    request.get_json.return_value = data

    with (
      patch.object(
        orch,
        "_phase_diagnose",
        return_value={"table": "users", "health": "HEALTHY", "recommendations": []},
      ),
      patch.object(orch, "_phase_budget_check", return_value="GREEN"),
      patch.object(orch, "_phase_document"),
    ):
      response, status = orch.handle_healing_request(request)
    assert status == 200

  def test_returns_400_on_empty(self):
    request = MagicMock()
    request.get_json.return_value = None
    response, status = orch.handle_healing_request(request)
    assert status == 400

  def test_handles_pubsub_envelope(self):
    data = {"table": "transactions", "change_type": "UPDATE", "source": "cdc"}
    encoded = base64.b64encode(json.dumps(data).encode()).decode()
    envelope = {"message": {"data": encoded}}

    request = MagicMock()
    request.get_json.return_value = envelope

    with (
      patch.object(
        orch,
        "_phase_diagnose",
        return_value={
          "table": "transactions",
          "health": "HEALTHY",
          "recommendations": [],
        },
      ),
      patch.object(orch, "_phase_budget_check", return_value="GREEN"),
      patch.object(orch, "_phase_document"),
    ):
      response, status = orch.handle_healing_request(request)
    assert status == 200
    body = json.loads(response)
    assert body["phase"] == "COMPLETE"


# ─── Data Models ───────────────────────────────────────────────────────────────


class TestDataModels:
  """Tests for enum and dataclass correctness."""

  def test_healing_action_values(self):
    assert orch.HealingAction.NOOP == "NOOP"
    assert orch.HealingAction.INDEX_RECOMMENDATION == "INDEX_RECOMMENDATION"

  def test_orchestrator_phase_values(self):
    assert orch.OrchestratorPhase.TRIAGE == "TRIAGE"
    assert orch.OrchestratorPhase.COMPLETE == "COMPLETE"

  def test_pipeline_result_serialization(self):
    from dataclasses import asdict

    result = orch.PipelineResult(
      request_id="test_001",
      started_at="2026-05-08T00:00:00Z",
    )
    data = asdict(result)
    serialized = json.dumps(data, default=str)
    assert "request_id" in serialized
