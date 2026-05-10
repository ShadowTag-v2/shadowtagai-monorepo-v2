# Copyright 2026 ShadowTagAI. All rights reserved.
"""Integration tests for HumanGateStep → OnExternalEvent("UserApproved") flow.

Tests the full lifecycle:
1. Register a pending gate (simulating SK Process reaching HumanGateStep)
2. Query gate status (pending)
3. Submit approval decision via API
4. Verify gate resolved + correct event fired
5. Verify idempotency (double-approve returns 409)
"""

from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from apps.counselconduit.api.human_gate import (
  _pending_gates,
  register_pending_gate,
  router,
)


@pytest.fixture()
def client():
  """Create a test client with the human gate router mounted."""
  app = FastAPI()
  app.include_router(router)
  return TestClient(app)


@pytest.fixture(autouse=True)
def _clear_gates():
  """Clear the in-memory gate registry before each test."""
  _pending_gates.clear()
  yield
  _pending_gates.clear()


# ============================================================================
# Gate Registration Tests
# ============================================================================


class TestGateRegistration:
  """Tests for the gate registration lifecycle."""

  def test_register_pending_gate(self):
    """A gate can be registered as pending."""
    register_pending_gate("proc-001", {"step": "HumanGateStep"})
    assert "proc-001" in _pending_gates
    assert _pending_gates["proc-001"]["status"] == "pending"

  def test_register_with_metadata(self):
    """Metadata is preserved in registration."""
    register_pending_gate("proc-002", {"risk_score": 0.85, "step": "HumanGateStep"})
    gate = _pending_gates["proc-002"]
    assert gate["metadata"]["risk_score"] == 0.85


# ============================================================================
# Gate Query Tests
# ============================================================================


class TestGateQuery:
  """Tests for querying gate status."""

  def test_get_pending_gate(self, client):
    """Pending gate returns status=pending."""
    register_pending_gate("proc-003")
    resp = client.get(
      "/api/v1/process/gate/proc-003",
      headers={"X-Firm-Id": "firm-test"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "pending"
    assert data["process_id"] == "proc-003"

  def test_get_nonexistent_gate(self, client):
    """Querying a nonexistent gate returns 404."""
    resp = client.get(
      "/api/v1/process/gate/proc-999",
      headers={"X-Firm-Id": "firm-test"},
    )
    assert resp.status_code == 404

  def test_get_gate_requires_firm_id(self, client):
    """Missing X-Firm-Id returns 401."""
    register_pending_gate("proc-004")
    resp = client.get("/api/v1/process/gate/proc-004")
    assert resp.status_code == 401

  def test_list_pending_gates(self, client):
    """List endpoint returns all pending gates."""
    register_pending_gate("proc-005")
    register_pending_gate("proc-006")
    resp = client.get(
      "/api/v1/process/gates/pending",
      headers={"X-Firm-Id": "firm-test"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["pending_count"] == 2


# ============================================================================
# Gate Decision Tests (OnExternalEvent Flow)
# ============================================================================


class TestGateDecision:
  """Tests for the approve/reject decision flow (OnExternalEvent)."""

  def test_approve_fires_user_approved_event(self, client):
    """Approving a gate fires OnExternalEvent('UserApproved')."""
    register_pending_gate("proc-010")
    resp = client.post(
      "/api/v1/process/gate/decide",
      json={"process_id": "proc-010", "decision": "approve"},
      headers={"X-Firm-Id": "firm-test", "X-User-Id": "reviewer-001"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["event_fired"] == "UserApproved"
    assert data["decision"] == "approve"
    assert data["reviewer"] == "reviewer-001"

  def test_reject_fires_user_rejected_event(self, client):
    """Rejecting a gate fires OnExternalEvent('UserRejected')."""
    register_pending_gate("proc-011")
    resp = client.post(
      "/api/v1/process/gate/decide",
      json={"process_id": "proc-011", "decision": "reject"},
      headers={"X-Firm-Id": "firm-test", "X-User-Id": "reviewer-002"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["event_fired"] == "UserRejected"

  def test_approve_resolves_gate_status(self, client):
    """After approval, gate status changes from 'pending' to 'approve'."""
    register_pending_gate("proc-012")
    client.post(
      "/api/v1/process/gate/decide",
      json={"process_id": "proc-012", "decision": "approve"},
      headers={"X-Firm-Id": "firm-test", "X-User-Id": "reviewer-001"},
    )
    assert _pending_gates["proc-012"]["status"] == "approve"

  def test_double_approve_returns_409(self, client):
    """Idempotency: approving an already-resolved gate returns 409 Conflict."""
    register_pending_gate("proc-013")
    # First approval
    resp1 = client.post(
      "/api/v1/process/gate/decide",
      json={"process_id": "proc-013", "decision": "approve"},
      headers={"X-Firm-Id": "firm-test", "X-User-Id": "reviewer-001"},
    )
    assert resp1.status_code == 200
    # Second approval (should conflict)
    resp2 = client.post(
      "/api/v1/process/gate/decide",
      json={"process_id": "proc-013", "decision": "approve"},
      headers={"X-Firm-Id": "firm-test", "X-User-Id": "reviewer-001"},
    )
    assert resp2.status_code == 409

  def test_decide_nonexistent_gate_returns_404(self, client):
    """Deciding on a nonexistent gate returns 404."""
    resp = client.post(
      "/api/v1/process/gate/decide",
      json={"process_id": "proc-999", "decision": "approve"},
      headers={"X-Firm-Id": "firm-test", "X-User-Id": "reviewer-001"},
    )
    assert resp.status_code == 404

  def test_decide_requires_auth_headers(self, client):
    """Missing auth headers returns 401."""
    register_pending_gate("proc-014")
    resp = client.post(
      "/api/v1/process/gate/decide",
      json={"process_id": "proc-014", "decision": "approve"},
    )
    assert resp.status_code == 401

  def test_invalid_decision_value(self, client):
    """Invalid decision value (not approve/reject) returns 422."""
    register_pending_gate("proc-015")
    resp = client.post(
      "/api/v1/process/gate/decide",
      json={"process_id": "proc-015", "decision": "maybe"},
      headers={"X-Firm-Id": "firm-test", "X-User-Id": "reviewer-001"},
    )
    assert resp.status_code == 422

  def test_approve_with_reviewer_notes(self, client):
    """Approval with reviewer notes is accepted."""
    register_pending_gate("proc-016")
    resp = client.post(
      "/api/v1/process/gate/decide",
      json={
        "process_id": "proc-016",
        "decision": "approve",
        "reviewer_notes": "Risk score acceptable. Approved per firm policy.",
      },
      headers={"X-Firm-Id": "firm-test", "X-User-Id": "reviewer-001"},
    )
    assert resp.status_code == 200
