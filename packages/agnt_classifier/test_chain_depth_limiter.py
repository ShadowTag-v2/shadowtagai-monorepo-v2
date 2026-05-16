# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Tests for Judge 6 — Chain Depth Limiter.

Validates:
  - Progressive escalation at C1–C5 thresholds
  - Encoding evasion detection (base64, hex, octal)
  - Chain reset behavior
  - Effective depth calculation with encoding bonus
  - Summary/diagnostic output
"""

from __future__ import annotations

import base64


from agnt_classifier.chain_depth_limiter import (
  ChainDepthLimiter,
  EscalationLevel,
  THRESHOLD_C1_WARN,
  THRESHOLD_C2_ESCALATE,
  THRESHOLD_C3_HUMAN,
  THRESHOLD_C4_BLOCK,
  THRESHOLD_C5_KILL,
)


# ── Threshold Tests ───────────────────────────────────────────────────────


class TestThresholdEscalation:
  """Verify progressive escalation at each C-level."""

  def test_normal_below_c1(self):
    limiter = ChainDepthLimiter()
    for _ in range(THRESHOLD_C1_WARN - 1):
      state = limiter.check("echo hello")
    assert state.escalation_level == EscalationLevel.NORMAL

  def test_c1_warning_at_threshold(self):
    limiter = ChainDepthLimiter()
    for _ in range(THRESHOLD_C1_WARN):
      state = limiter.check("ls -la")
    assert state.escalation_level == EscalationLevel.WARN

  def test_c2_escalate_at_threshold(self):
    limiter = ChainDepthLimiter()
    for _ in range(THRESHOLD_C2_ESCALATE):
      state = limiter.check("git status")
    assert state.escalation_level == EscalationLevel.ESCALATE

  def test_c3_human_required(self):
    limiter = ChainDepthLimiter()
    for _ in range(THRESHOLD_C3_HUMAN):
      state = limiter.check("cat file.txt")
    assert state.escalation_level == EscalationLevel.HUMAN_REQUIRED

  def test_c4_blocked(self):
    limiter = ChainDepthLimiter()
    for _ in range(THRESHOLD_C4_BLOCK):
      state = limiter.check("pwd")
    assert state.escalation_level == EscalationLevel.BLOCKED

  def test_c5_killed(self):
    limiter = ChainDepthLimiter()
    for _ in range(THRESHOLD_C5_KILL):
      state = limiter.check("whoami")
    assert state.escalation_level == EscalationLevel.KILLED


# ── Encoding Detection Tests ──────────────────────────────────────────────


class TestEncodingDetection:
  """Verify detection of encoding-based evasion patterns."""

  def test_base64_decode_detection(self):
    limiter = ChainDepthLimiter()
    state = limiter.check("echo dGVzdA== | base64 --decode")
    assert state.encoding_detections == 1

  def test_hex_escape_detection(self):
    limiter = ChainDepthLimiter()
    state = limiter.check(r"echo -e '\x72\x6d\x20\x2d\x72\x66'")
    assert state.encoding_detections == 1

  def test_octal_escape_detection(self):
    limiter = ChainDepthLimiter()
    state = limiter.check(r"printf '\162\155\040\055\162\146'")
    assert state.encoding_detections >= 1

  def test_python_inline_decode(self):
    limiter = ChainDepthLimiter()
    state = limiter.check(
      "python3 -c 'import base64; print(base64.b64decode(\"dGVzdA==\"))'"
    )
    assert state.encoding_detections == 1

  def test_long_base64_string_detection(self):
    limiter = ChainDepthLimiter()
    # Create a valid base64-encoded ASCII string (> 40 chars, > 10 bytes decoded)
    payload = base64.b64encode(b"This is a test command to delete everything").decode()
    state = limiter.check(f"echo {payload}")
    assert state.encoding_detections == 1

  def test_encoding_bonus_escalates_faster(self):
    """Each encoding detection adds +5 to effective depth."""
    limiter = ChainDepthLimiter()
    # 2 encoding detections = +10 effective depth
    limiter.check("echo dGVzdA== | base64 --decode")
    state = limiter.check(
      "python3 -c 'import base64; print(base64.b64decode(\"test\"))'"
    )
    # Depth = 2, encoding bonus = 2 * 5 = 10, effective = 12
    assert state.escalation_level == EscalationLevel.ESCALATE

  def test_safe_command_no_encoding(self):
    limiter = ChainDepthLimiter()
    state = limiter.check("echo hello world")
    assert state.encoding_detections == 0


# ── Reset Tests ───────────────────────────────────────────────────────────


class TestReset:
  """Verify chain reset behavior."""

  def test_reset_clears_depth(self):
    limiter = ChainDepthLimiter()
    for _ in range(8):
      limiter.check("echo test")
    assert limiter.state.depth == 8
    limiter.reset()
    assert limiter.state.depth == 0
    assert limiter.state.escalation_level == EscalationLevel.NORMAL

  def test_reset_clears_encoding_detections(self):
    limiter = ChainDepthLimiter()
    limiter.check("echo dGVzdA== | base64 --decode")
    assert limiter.state.encoding_detections == 1
    limiter.reset()
    assert limiter.state.encoding_detections == 0

  def test_reset_preserves_session_id(self):
    limiter = ChainDepthLimiter(session_id="test-session-123")
    limiter.check("echo test")
    limiter.reset()
    assert limiter.state.session_id == "test-session-123"


# ── Summary Tests ─────────────────────────────────────────────────────────


class TestSummary:
  """Verify diagnostic summary output."""

  def test_summary_contains_required_fields(self):
    limiter = ChainDepthLimiter(session_id="diag-test")
    limiter.check("ls")
    summary = limiter.summary()
    assert summary["session_id"] == "diag-test"
    assert summary["depth"] == 1
    assert summary["encoding_detections"] == 0
    assert summary["escalation_level"] == "NORMAL"
    assert "commands_per_minute" in summary
    assert "command_count" in summary

  def test_summary_tracks_command_count(self):
    limiter = ChainDepthLimiter()
    for i in range(5):
      limiter.check(f"echo {i}")
    summary = limiter.summary()
    assert summary["command_count"] == 5
    assert summary["depth"] == 5


# ── Custom Threshold Tests ────────────────────────────────────────────────


class TestCustomThresholds:
  """Verify custom threshold configuration."""

  def test_low_thresholds_for_testing(self):
    limiter = ChainDepthLimiter(
      warn_threshold=2,
      escalate_threshold=3,
      human_threshold=5,
      block_threshold=7,
      kill_threshold=10,
    )
    limiter.check("echo 1")
    assert limiter.state.escalation_level == EscalationLevel.NORMAL

    limiter.check("echo 2")
    assert limiter.state.escalation_level == EscalationLevel.WARN

    limiter.check("echo 3")
    assert limiter.state.escalation_level == EscalationLevel.ESCALATE

  def test_command_truncation(self):
    """Commands stored in state are truncated to 200 chars."""
    limiter = ChainDepthLimiter()
    long_cmd = "a" * 500
    limiter.check(long_cmd)
    assert len(limiter.state.commands[0]) == 200
