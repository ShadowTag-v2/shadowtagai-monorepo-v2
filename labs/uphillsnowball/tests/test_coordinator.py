"""Tests for SynthesisCoordinator — 8-Agent capability routing."""

from __future__ import annotations

import pytest

from src.agents.coordinator import (
  AgentCapability,
  AgentRole,
  SynthesisCoordinator,
  SYNTHESIS_MAP,
)


@pytest.fixture
def coordinator():
  """Create a fresh SynthesisCoordinator."""
  return SynthesisCoordinator()


class TestSynthesisMap:
  """Test the 8-agent synthesis map structure."""

  def test_all_8_agents_present(self):
    """All 8 roles must be in the map."""
    assert len(SYNTHESIS_MAP) == 8
    for role in AgentRole:
      assert role in SYNTHESIS_MAP

  def test_builder_cannot_review(self):
    """Builder is forbidden from reviewing code."""
    spec = SYNTHESIS_MAP[AgentRole.BUILDER]
    assert AgentCapability.REVIEW_CODE in spec.forbidden
    assert AgentCapability.WRITE_TESTS in spec.forbidden
    assert AgentCapability.WRITE_CODE in spec.capabilities

  def test_reviewer_cannot_write_code(self):
    """Reviewer is forbidden from writing production code."""
    spec = SYNTHESIS_MAP[AgentRole.REVIEWER]
    assert AgentCapability.WRITE_CODE in spec.forbidden
    assert AgentCapability.REVIEW_CODE in spec.capabilities

  def test_tester_cannot_decide_architecture(self):
    """Tester is forbidden from writing production code or reviews."""
    spec = SYNTHESIS_MAP[AgentRole.TESTER]
    assert AgentCapability.WRITE_CODE in spec.forbidden
    assert AgentCapability.REVIEW_CODE in spec.forbidden
    assert AgentCapability.WRITE_TESTS in spec.capabilities

  def test_each_agent_has_temporal_activity(self):
    """Every agent must map to a Temporal activity."""
    for role, spec in SYNTHESIS_MAP.items():
      assert spec.temporal_activity, f"{role} missing temporal_activity"


class TestCoordinatorDispatch:
  """Test capability validation and dispatch."""

  def test_builder_dispatch_write_code(self, coordinator):
    """Builder should dispatch to j3_decisive_ops_strike for code writing."""
    activity = coordinator.dispatch(AgentRole.BUILDER, AgentCapability.WRITE_CODE)
    assert activity == "j3_decisive_ops_strike"

  def test_builder_dispatch_review_raises(self, coordinator):
    """Builder attempting review should raise PermissionError."""
    with pytest.raises(PermissionError, match="forbidden"):
      coordinator.dispatch(AgentRole.BUILDER, AgentCapability.REVIEW_CODE)

  def test_reviewer_dispatch_review(self, coordinator):
    """Reviewer should dispatch to j6_sustaining_ops_audit."""
    activity = coordinator.dispatch(AgentRole.REVIEWER, AgentCapability.REVIEW_CODE)
    assert activity == "j6_sustaining_ops_audit"

  def test_tester_dispatch_tests(self, coordinator):
    """Tester should dispatch to j3_roc_drill_sandbox."""
    activity = coordinator.dispatch(AgentRole.TESTER, AgentCapability.WRITE_TESTS)
    assert activity == "j3_roc_drill_sandbox"

  def test_judge6_dispatch_risk(self, coordinator):
    """Judge 6 should dispatch to deploy gate."""
    activity = coordinator.dispatch(AgentRole.JUDGE_6, AgentCapability.ENFORCE_RISK)
    assert activity == "j6_judge_deploy_gate"

  def test_unauthorized_capability_raises(self, coordinator):
    """Agent with forbidden capability should raise PermissionError."""
    with pytest.raises(PermissionError, match="forbidden"):
      coordinator.dispatch(AgentRole.KAIROS, AgentCapability.WRITE_CODE)


class TestTriadAndDaemons:
  """Test triad and daemon activity lists."""

  def test_triad_has_3_activities(self, coordinator):
    """Triad should return exactly 3 activities in order."""
    triad = coordinator.get_triad_activities()
    assert len(triad) == 3
    assert triad[0] == "j3_decisive_ops_strike"
    assert triad[1] == "j6_sustaining_ops_audit"
    assert triad[2] == "j3_roc_drill_sandbox"

  def test_daemons_has_4_activities(self, coordinator):
    """Daemons should return exactly 4 support activities."""
    daemons = coordinator.get_daemon_activities()
    assert len(daemons) == 4
