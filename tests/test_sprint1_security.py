# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Sprint 1 Security Tests — B20 Subcommand Cap + P5.4 Context Decay Monitor.

Tests:
    - B20: BashASTAnalyzer integration in BlockAllowRuleEngine
    - B20: Commands ≤50 subcommands pass
    - B20: Commands >50 subcommands trigger BLOCK
    - B20: Warnings and env violations are logged
    - P5.4: File read oversize detection (threshold: 2000 lines)
    - P5.4: Tool result bloat detection (threshold: 50K chars)
    - P5.4: Context window remaining detection (threshold: 20%)
    - P5.4: Legacy API backward compatibility
    - P5.4: Severity escalation (WARNING → CRITICAL)
    - P5.4: Rolling accumulators track session totals
"""

from __future__ import annotations

import pytest

from context_compactor.decay_warning import (
  CONTEXT_REMAINING_PERCENT_THRESHOLD,
  FILE_READ_LINE_THRESHOLD,
  TOOL_RESULT_CHAR_THRESHOLD,
  ContextDecayMonitor,
  DecayCheckResult,
  DecaySeverity,
  DecayWarning,
)
from tool_gateway.block_allow_engine import (
  BlockAllowRuleEngine,
  Verdict,
)


# =========================================================================
# B20: Compound Command Cap (50-Subcommand Limit)
# =========================================================================


class TestB20SubcommandCap:
  """B20 integration: BashASTAnalyzer wired into BlockAllowRuleEngine.evaluate()."""

  @pytest.fixture()
  def engine(self) -> BlockAllowRuleEngine:
    return BlockAllowRuleEngine(
      tenant_id="test-tenant",
      session_boundary={"test-tenant"},
    )

  def test_simple_command_passes(self, engine: BlockAllowRuleEngine) -> None:
    """A simple 'echo hello' should not trigger B20."""
    result = engine.evaluate("bash", {"command": "echo hello"})
    b20 = [r for r in result.matched_rules if r.rule_id == "B20"]
    assert len(b20) == 0

  def test_moderate_pipeline_passes(self, engine: BlockAllowRuleEngine) -> None:
    """A moderate pipeline (5 subcommands) should pass."""
    cmd = "cat file.txt | grep error | sort | uniq -c | head -20"
    result = engine.evaluate("bash", {"command": cmd})
    b20 = [r for r in result.matched_rules if r.rule_id == "B20"]
    assert len(b20) == 0

  def test_50_subcommands_passes(self, engine: BlockAllowRuleEngine) -> None:
    """Exactly 50 subcommands should NOT trigger (boundary: ≤50)."""
    # Build a command with exactly 50 semicolon-separated commands
    cmds = [f"echo {i}" for i in range(50)]
    cmd = " ; ".join(cmds)
    result = engine.evaluate("bash", {"command": cmd})
    b20 = [r for r in result.matched_rules if r.rule_id == "B20"]
    assert len(b20) == 0

  def test_51_subcommands_triggers_block(self, engine: BlockAllowRuleEngine) -> None:
    """51 subcommands should trigger B20 BLOCK."""
    cmds = [f"echo {i}" for i in range(51)]
    cmd = " ; ".join(cmds)
    result = engine.evaluate("bash", {"command": cmd})
    b20 = [r for r in result.matched_rules if r.rule_id == "B20"]
    assert len(b20) == 1
    assert b20[0].verdict == Verdict.BLOCK
    assert b20[0].category == "infra"

  def test_100_subcommands_blocked(self, engine: BlockAllowRuleEngine) -> None:
    """100 subcommands — well over limit — triggers B20."""
    cmds = [f"cmd_{i}" for i in range(100)]
    cmd = " ; ".join(cmds)
    result = engine.evaluate("bash", {"command": cmd})
    assert any(r.rule_id == "B20" for r in result.matched_rules)
    assert result.final_verdict == Verdict.BLOCK

  def test_b20_only_fires_for_shell_tools(self, engine: BlockAllowRuleEngine) -> None:
    """B20 should NOT fire for non-shell tool IDs."""
    result = engine.evaluate("read.document", {"command": "echo hi"})
    b20 = [r for r in result.matched_rules if r.rule_id == "B20"]
    assert len(b20) == 0

  def test_b20_fires_for_run_command(self, engine: BlockAllowRuleEngine) -> None:
    """B20 fires for 'run_command' tool ID."""
    cmds = [f"echo {i}" for i in range(51)]
    cmd = " ; ".join(cmds)
    result = engine.evaluate("run_command", {"command": cmd})
    assert any(r.rule_id == "B20" for r in result.matched_rules)

  def test_b20_fires_for_terminal(self, engine: BlockAllowRuleEngine) -> None:
    """B20 fires for 'terminal' tool ID."""
    cmds = [f"echo {i}" for i in range(51)]
    cmd = " ; ".join(cmds)
    result = engine.evaluate("terminal", {"command": cmd})
    assert any(r.rule_id == "B20" for r in result.matched_rules)

  def test_b20_empty_command_no_crash(self, engine: BlockAllowRuleEngine) -> None:
    """Empty command should not crash B20."""
    result = engine.evaluate("bash", {"command": ""})
    # No B20, no crash
    b20 = [r for r in result.matched_rules if r.rule_id == "B20"]
    assert len(b20) == 0

  def test_b20_no_command_key_no_crash(self, engine: BlockAllowRuleEngine) -> None:
    """Missing 'command' key should not crash B20."""
    result = engine.evaluate("bash", {})
    b20 = [r for r in result.matched_rules if r.rule_id == "B20"]
    assert len(b20) == 0

  def test_b20_description_includes_deny_reason(
    self, engine: BlockAllowRuleEngine
  ) -> None:
    """B20 match description should include the AST deny reason."""
    cmds = [f"echo {i}" for i in range(60)]
    cmd = " ; ".join(cmds)
    result = engine.evaluate("bash", {"command": cmd})
    b20 = [r for r in result.matched_rules if r.rule_id == "B20"]
    assert len(b20) == 1
    assert "Bash AST security" in b20[0].description


# =========================================================================
# P5.4: Context Decay Warning System
# =========================================================================


class TestDecayWarningDataclasses:
  """Test DecayWarning and DecayCheckResult dataclasses."""

  def test_warning_str(self) -> None:
    w = DecayWarning(
      vector="test_vector",
      severity=DecaySeverity.WARNING,
      message="test message",
    )
    assert "[WARNING]" in str(w)
    assert "test_vector" in str(w)

  def test_result_empty(self) -> None:
    r = DecayCheckResult()
    assert not r.has_warnings
    assert r.max_severity == DecaySeverity.INFO
    assert r.format_warnings() == ""

  def test_result_max_severity_critical(self) -> None:
    r = DecayCheckResult(
      warnings=[
        DecayWarning(vector="a", severity=DecaySeverity.INFO, message="x"),
        DecayWarning(vector="b", severity=DecaySeverity.CRITICAL, message="y"),
        DecayWarning(vector="c", severity=DecaySeverity.WARNING, message="z"),
      ]
    )
    assert r.max_severity == DecaySeverity.CRITICAL

  def test_result_format_warnings_xml(self) -> None:
    r = DecayCheckResult(
      warnings=[
        DecayWarning(vector="v1", severity=DecaySeverity.WARNING, message="m1"),
      ]
    )
    formatted = r.format_warnings()
    assert "<CONTEXT_DECAY_WARNING>" in formatted
    assert "</CONTEXT_DECAY_WARNING>" in formatted
    assert "v1" in formatted


class TestFileReadDecay:
  """P5.4 Vector 1: File read oversize detection."""

  def test_under_threshold_no_warning(self) -> None:
    monitor = ContextDecayMonitor()
    result = monitor.check_file_read(500)
    assert not result.has_warnings

  def test_exactly_at_threshold_no_warning(self) -> None:
    monitor = ContextDecayMonitor()
    result = monitor.check_file_read(FILE_READ_LINE_THRESHOLD)
    assert not result.has_warnings

  def test_over_threshold_triggers_warning(self) -> None:
    monitor = ContextDecayMonitor()
    result = monitor.check_file_read(FILE_READ_LINE_THRESHOLD + 1)
    assert result.has_warnings
    w = result.warnings[0]
    assert w.vector == "file_read_oversize"
    assert w.severity == DecaySeverity.WARNING

  def test_3x_threshold_triggers_critical(self) -> None:
    monitor = ContextDecayMonitor()
    result = monitor.check_file_read(FILE_READ_LINE_THRESHOLD * 3 + 1)
    assert result.has_warnings
    w = result.warnings[0]
    assert w.severity == DecaySeverity.CRITICAL

  def test_accumulator_tracks_total(self) -> None:
    monitor = ContextDecayMonitor()
    monitor.check_file_read(100)
    monitor.check_file_read(200)
    monitor.check_file_read(300)
    assert monitor.total_file_lines_read == 600


class TestToolResultDecay:
  """P5.4 Vector 2: Tool result bloat detection."""

  def test_under_threshold_no_warning(self) -> None:
    monitor = ContextDecayMonitor()
    result = monitor.check_tool_result(10_000)
    assert not result.has_warnings

  def test_over_threshold_triggers_warning(self) -> None:
    monitor = ContextDecayMonitor()
    result = monitor.check_tool_result(TOOL_RESULT_CHAR_THRESHOLD + 1)
    assert result.has_warnings
    w = result.warnings[0]
    assert w.vector == "tool_result_bloat"
    assert w.severity == DecaySeverity.WARNING
    assert result.should_truncate_result is True

  def test_3x_threshold_triggers_critical(self) -> None:
    monitor = ContextDecayMonitor()
    result = monitor.check_tool_result(TOOL_RESULT_CHAR_THRESHOLD * 3 + 1)
    w = result.warnings[0]
    assert w.severity == DecaySeverity.CRITICAL

  def test_accumulator_tracks_total(self) -> None:
    monitor = ContextDecayMonitor()
    monitor.check_tool_result(1000)
    monitor.check_tool_result(2000)
    assert monitor.total_tool_result_chars == 3000


class TestContextWindowDecay:
  """P5.4 Vector 3: Context window remaining detection."""

  def test_plenty_remaining_no_warning(self) -> None:
    monitor = ContextDecayMonitor(max_context_tokens=100_000)
    result = monitor.check_decay(current_tokens=50_000)  # 50% remaining
    context_warnings = [
      w for w in result.warnings if w.vector == "context_remaining_low"
    ]
    assert len(context_warnings) == 0

  def test_under_20_percent_triggers_warning(self) -> None:
    monitor = ContextDecayMonitor(max_context_tokens=100_000)
    result = monitor.check_decay(current_tokens=85_000)  # 15% remaining
    context_warnings = [
      w for w in result.warnings if w.vector == "context_remaining_low"
    ]
    assert len(context_warnings) == 1
    assert context_warnings[0].severity == DecaySeverity.WARNING
    assert result.should_compact is True

  def test_under_10_percent_triggers_critical(self) -> None:
    monitor = ContextDecayMonitor(max_context_tokens=100_000)
    result = monitor.check_decay(current_tokens=95_000)  # 5% remaining
    context_warnings = [
      w for w in result.warnings if w.vector == "context_remaining_low"
    ]
    assert len(context_warnings) == 1
    assert context_warnings[0].severity == DecaySeverity.CRITICAL
    assert result.should_compact is True

  def test_zero_tokens_no_warning(self) -> None:
    """Zero current_tokens should not trigger context warning."""
    monitor = ContextDecayMonitor(max_context_tokens=100_000)
    result = monitor.check_decay(current_tokens=0)
    context_warnings = [
      w for w in result.warnings if w.vector == "context_remaining_low"
    ]
    assert len(context_warnings) == 0


class TestLegacyDecayAPI:
  """Backward compatibility with check_context_health()."""

  def test_legacy_returns_none_when_healthy(self) -> None:
    monitor = ContextDecayMonitor(
      token_threshold=100_000,
      turn_threshold=50,
    )
    result = monitor.check_context_health(
      current_tokens=1000,
      current_turns=5,
    )
    assert result is None

  def test_legacy_returns_string_when_unhealthy(self) -> None:
    monitor = ContextDecayMonitor(
      token_threshold=100,
      turn_threshold=5,
    )
    result = monitor.check_context_health(
      current_tokens=200,
      current_turns=10,
    )
    assert result is not None
    assert "<CONTEXT_DECAY_WARNING>" in result

  def test_turn_count_threshold(self) -> None:
    monitor = ContextDecayMonitor(turn_threshold=10)
    result = monitor.check_decay(current_turns=15)
    turn_warnings = [w for w in result.warnings if w.vector == "turn_count_high"]
    assert len(turn_warnings) == 1

  def test_token_count_threshold(self) -> None:
    monitor = ContextDecayMonitor(token_threshold=5000, max_context_tokens=0)
    result = monitor.check_decay(current_tokens=6000)
    token_warnings = [w for w in result.warnings if w.vector == "token_count_high"]
    assert len(token_warnings) == 1


class TestDecayMonitorReset:
  """Accumulator reset behavior."""

  def test_reset_clears_accumulators(self) -> None:
    monitor = ContextDecayMonitor()
    monitor.check_file_read(500)
    monitor.check_tool_result(10_000)
    assert monitor.total_file_lines_read == 500
    assert monitor.total_tool_result_chars == 10_000

    monitor.reset_accumulators()
    assert monitor.total_file_lines_read == 0
    assert monitor.total_tool_result_chars == 0


class TestDecayMultiVector:
  """Multiple decay vectors firing simultaneously."""

  def test_all_three_vectors_fire(self) -> None:
    monitor = ContextDecayMonitor(max_context_tokens=100_000)
    result = monitor.check_decay(
      current_tokens=90_000,  # 10% remaining → CRITICAL
      file_read_lines=5_000,  # Over 2000 → WARNING
      tool_result_chars=200_000,  # Over 50K → CRITICAL
    )
    vectors = {w.vector for w in result.warnings}
    assert "file_read_oversize" in vectors
    assert "tool_result_bloat" in vectors
    assert "context_remaining_low" in vectors
    assert result.should_compact is True
    assert result.should_truncate_result is True
    assert result.max_severity == DecaySeverity.CRITICAL

  def test_constants_match_spec(self) -> None:
    """Verify thresholds match P5.4 specification."""
    assert FILE_READ_LINE_THRESHOLD == 2000
    assert TOOL_RESULT_CHAR_THRESHOLD == 50_000
    assert CONTEXT_REMAINING_PERCENT_THRESHOLD == 20
