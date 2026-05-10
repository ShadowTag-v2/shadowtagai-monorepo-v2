# labs/uphillsnowball/tests/test_gauntlet.py
"""Tests for the 17-Layer Gauntlet."""

import os
import tempfile
from labs.uphillsnowball.agent.gauntlet import evaluate, GauntletVerdict


class TestGauntletLayers:
  """Test individual gauntlet layers."""

  def test_clean_action_passes(self):
    action = {
      "agent_id": "kosmos-001",
      "role": "director",
      "type": "plan",
      "session_start": __import__("time").time(),
      "actions_this_minute": 5,
      "content": "Standard planning operation.",
      "command": "",
      "target_file": "apps/counselconduit/api/new_file.py",
    }
    result = evaluate(action)
    assert result.passed is True
    assert result.verdict == GauntletVerdict.PASS

  def test_missing_agent_id_blocked(self):
    result = evaluate({"agent_id": ""})
    assert result.passed is False
    assert result.blocked_by == 1

  def test_director_cannot_write_code(self):
    result = evaluate({"agent_id": "test", "role": "director", "type": "code_write"})
    assert result.passed is False
    assert result.blocked_by == 2

  def test_secret_in_content_blocked(self):
    result = evaluate(
      {
        "agent_id": "test",
        "content": 'api_key = "sk-1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMN"',
      }
    )
    assert result.passed is False
    assert result.blocked_by == 5

  def test_forbidden_command_blocked(self):
    result = evaluate({"agent_id": "test", "command": "rm -rf /important/data"})
    assert result.passed is False
    assert result.blocked_by == 6

  def test_immutable_file_blocked(self):
    result = evaluate(
      {
        "agent_id": "test",
        "target_file": "/repo/AGENTS.md",
        "type": "write",
      }
    )
    assert result.passed is False
    assert result.blocked_by == 7

  def test_banned_dependency_blocked(self):
    result = evaluate(
      {
        "agent_id": "test",
        "content": 'const queue = require("bullmq");',
      }
    )
    assert result.passed is False
    assert result.blocked_by == 10

  def test_force_push_blocked(self):
    result = evaluate({"agent_id": "test", "command": "git push --force origin main"})
    assert result.passed is False
    assert result.blocked_by == 15

  def test_telemetry_blocked(self):
    result = evaluate(
      {"agent_id": "test", "content": "SENTRY_DSN=https://sentry.io/key"}
    )
    assert result.passed is False
    assert result.blocked_by == 16

  def test_rkill_blocks_everything(self):
    rkill_path = tempfile.mktemp()
    os.environ["RKILL_FLAG"] = rkill_path
    try:
      with open(rkill_path, "w") as f:
        f.write("EMERGENCY SHUTDOWN")
      result = evaluate({"agent_id": "test"})
      assert result.verdict == GauntletVerdict.RKILL
      assert result.passed is False
    finally:
      os.unlink(rkill_path)
      del os.environ["RKILL_FLAG"]

  def test_rate_limit_warning(self):
    result = evaluate({"agent_id": "test", "actions_this_minute": 61})
    assert result.passed is False

  def test_performance_sub_10ms(self):
    result = evaluate({"agent_id": "test", "content": "normal content"})
    assert result.total_elapsed_ms < 10  # All 17 layers under 10ms
