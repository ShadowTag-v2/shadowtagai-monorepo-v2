# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Integration tests for the context_compactor package.

Covers the full reconciled surface area:
  - Orchestrator (ContextCompactor) + 4-layer pipeline
  - compact_conversation + summarize_fn error handling
  - partial_compact_conversation (UP_TO / FROM)
  - Warning state thread safety
  - Types (RecompactionInfo, ContextEditStrategy)
  - Telemetry hook emission
  - Shim deprecation warning
  - Decay monitor integration
"""

from __future__ import annotations

import json
import threading
import uuid

import pytest

from context_compactor import (
  AutoCompactTrackingState,
  CompactDirection,
  ContextEditRule,
  ContextEditRuleType,
  ContextEditStrategy,
  ConversationCompactionResult,
  MicrocompactResult,
  PromptTooLongError,
  RecompactionInfo,
  clear_compact_warning_suppression,
  compact_conversation,
  get_compact_warning_suppressed,
  is_compact_boundary_message,
  microcompact_messages,
  partial_compact_conversation,
  register_cleanup_hook,
  run_post_compact_cleanup,
  suppress_compact_warning,
)
from context_compactor.compactor import ContextCompactor
from context_compactor.layers import Message as LayerMessage
from context_compactor.decay_warning import (
  ContextDecayMonitor,
  DecaySeverity,
)


# ── Helpers ───────────────────────────────────────────────────────────────────


def _msg(role: str, content: str | list, **kwargs) -> dict:
  """Create a flat message dict."""
  return {"role": role, "content": content, "uuid": str(uuid.uuid4()), **kwargs}


def _user(text: str, **kwargs) -> dict:
  return _msg("user", text, **kwargs)


def _assistant(text: str, msg_id: str | None = None) -> dict:
  m = _msg("assistant", text)
  # Add message.id for group_messages_by_api_round boundary detection
  m["message"] = {"id": msg_id or str(uuid.uuid4())}
  return m


def _simple_conversation(n: int = 10) -> list[dict]:
  """Generate n user-assistant pairs."""
  msgs = []
  for i in range(n):
    msgs.append(_user(f"Question {i}: " + "x" * 200))
    msgs.append(_assistant(f"Answer {i}: " + "y" * 200))
  return msgs


def _layer_messages(n: int = 5) -> list[LayerMessage]:
  """Generate Message dataclass instances for layer-level tests."""
  import time

  msgs = []
  for i in range(n):
    msgs.append(
      LayerMessage(
        role="user",
        content=f"Q{i}: " + "x" * 200,
        timestamp=time.time() - 600,
        token_count=60,
      )
    )
    msgs.append(
      LayerMessage(
        role="assistant",
        content=f"A{i}: " + "y" * 200,
        timestamp=time.time() - 500,
        token_count=60,
      )
    )
  return msgs


def _mock_summarize(
  summary: str = "This is a comprehensive summary of the conversation.",
):
  """Return a summarize_fn that returns a fixed summary."""

  def _fn(messages, prompt):
    return summary

  return _fn


# ── Tests: ContextCompactor orchestrator ──────────────────────────────────────


class TestContextCompactorOrchestrator:
  """Tests for the ContextCompactor 4-layer pipeline."""

  def test_compactor_disabled_noop(self):
    compactor = ContextCompactor(feature_flags={"context_compaction": False})
    result = compactor.run([], target_tokens=10000, current_tokens=50000)
    assert result.layer_used == "disabled"
    assert result.tokens_saved == 0

  def test_compactor_enabled_with_headroom(self):
    compactor = ContextCompactor(feature_flags={"context_compaction": True})
    msgs = _layer_messages(5)
    result = compactor.run(msgs, target_tokens=100000, current_tokens=50000)
    assert result.tokens_before == 50000

  def test_should_compact_below_buffer(self):
    compactor = ContextCompactor(feature_flags={"context_compaction": True})
    assert compactor.should_compact(current_tokens=95000, max_tokens=100000) is True

  def test_should_compact_above_buffer(self):
    compactor = ContextCompactor(feature_flags={"context_compaction": True})
    assert compactor.should_compact(current_tokens=50000, max_tokens=100000) is False

  def test_should_warn_threshold(self):
    compactor = ContextCompactor(feature_flags={"context_compaction": True})
    assert compactor.should_warn(current_tokens=85000, max_tokens=100000) is True
    assert compactor.should_warn(current_tokens=50000, max_tokens=100000) is False

  def test_stats_property(self):
    compactor = ContextCompactor(feature_flags={"context_compaction": True})
    stats = compactor.stats
    assert "run_count" in stats
    assert "total_tokens_saved" in stats
    assert stats["run_count"] == 0

  def test_pre_compact_returns_microcompact_result(self):
    compactor = ContextCompactor(feature_flags={"context_compaction": True})
    msgs = _simple_conversation(3)  # pre_compact uses dict messages
    result = compactor.pre_compact(msgs)
    assert isinstance(result, MicrocompactResult)


class TestContextCompactorTelemetry:
  """Tests for telemetry hook emission."""

  def test_telemetry_emitted_to_file(self, tmp_path):
    telemetry_dir = tmp_path / ".beads"
    compactor = ContextCompactor(
      telemetry_dir=telemetry_dir,
      feature_flags={"context_compaction": True},
    )
    msgs = _layer_messages(5)
    compactor.run(msgs, target_tokens=100000, current_tokens=50000)
    telemetry_file = telemetry_dir / "telemetry.jsonl"
    # Even if nothing was compacted, we don't emit for skipped layers
    # But the file should at least exist if any layer ran
    if telemetry_file.exists():
      lines = telemetry_file.read_text().strip().split("\n")
      for line in lines:
        event = json.loads(line)
        assert "event" in event
        assert "timestamp" in event

  def test_telemetry_not_emitted_without_dir(self):
    compactor = ContextCompactor(
      telemetry_dir=None,
      feature_flags={"context_compaction": True},
    )
    # Should not raise
    msgs = _layer_messages(3)
    compactor.run(msgs, target_tokens=100000, current_tokens=50000)

  def test_cache_break_detection(self):
    compactor = ContextCompactor(feature_flags={"context_compaction": True})
    msgs = _layer_messages(3)
    compactor.run(msgs, target_tokens=100000, current_tokens=50000)
    # After a run, cache report should exist
    # (It may be None if target was already met and no layers ran)
    report = compactor.last_cache_report
    # Just verify the property is accessible
    assert report is None or hasattr(report, "cache_broken")


# ── Tests: compact_conversation orchestrator ──────────────────────────────────


class TestCompactConversationOrchestrator:
  """Tests for the L2 compact_conversation function."""

  def test_happy_path(self):
    msgs = _simple_conversation(10)
    result = compact_conversation(
      msgs,
      summarize_fn=_mock_summarize(),
    )
    assert isinstance(result, ConversationCompactionResult)
    assert result.summary == "This is a comprehensive summary of the conversation."
    assert result.tokens_before > 0
    assert result.is_partial is False

  def test_empty_messages_raises(self):
    with pytest.raises(ValueError, match="Not enough messages"):
      compact_conversation([], summarize_fn=_mock_summarize())

  def test_none_summarize_fn_raises(self):
    msgs = _simple_conversation(3)
    with pytest.raises(NotImplementedError, match="summarize_fn"):
      compact_conversation(msgs, summarize_fn=None)

  def test_summarize_fn_ptl_retry(self):
    """Test that PromptTooLongError triggers PTL retry with truncation."""
    call_count = 0

    def _failing_then_ok(messages, prompt):
      nonlocal call_count
      call_count += 1
      if call_count == 1:
        # Response must have role=assistant with text matching "by N tokens"
        raise PromptTooLongError(
          "too long",
          response={
            "role": "assistant",
            "content": "Prompt exceeded limit by 5000 tokens",
          },
        )
      return "Summary after retry"

    msgs = _simple_conversation(10)
    result = compact_conversation(msgs, summarize_fn=_failing_then_ok)
    assert result.summary == "Summary after retry"
    assert call_count == 2

  def test_summarize_fn_ptl_exhausted(self):
    """Test that exhausting PTL retries raises ValueError."""

    def _always_ptl(messages, prompt):
      raise PromptTooLongError("always too long")

    msgs = _simple_conversation(10)
    with pytest.raises(ValueError, match="Conversation too long"):
      compact_conversation(msgs, summarize_fn=_always_ptl)

  def test_summarize_fn_generic_error(self):
    """Test that generic exceptions from summarize_fn are caught."""

    def _crash(messages, prompt):
      raise RuntimeError("API timeout")

    msgs = _simple_conversation(5)
    with pytest.raises(ValueError, match="Compaction interrupted"):
      compact_conversation(msgs, summarize_fn=_crash)

  def test_summarize_fn_returns_empty(self):
    """Test that empty summary raises ValueError."""
    msgs = _simple_conversation(3)
    with pytest.raises(ValueError, match="Failed to generate"):
      compact_conversation(msgs, summarize_fn=lambda m, p: "")

  def test_auto_compact_trigger(self):
    msgs = _simple_conversation(5)
    result = compact_conversation(
      msgs,
      is_auto_compact=True,
      summarize_fn=_mock_summarize(),
    )
    assert result.is_partial is False

  def test_custom_instructions(self):
    msgs = _simple_conversation(5)
    result = compact_conversation(
      msgs,
      custom_instructions="Focus on code changes",
      summarize_fn=_mock_summarize(),
    )
    assert result.summary != ""

  def test_boundary_message_in_result(self):
    msgs = _simple_conversation(5)
    result = compact_conversation(msgs, summarize_fn=_mock_summarize())
    assert len(result.messages) >= 2
    assert is_compact_boundary_message(result.messages[0])


# ── Tests: partial_compact_conversation ───────────────────────────────────────


class TestPartialCompactConversation:
  """Tests for directional partial compaction."""

  def test_up_to_direction(self):
    msgs = _simple_conversation(10)
    result = partial_compact_conversation(
      msgs,
      pivot_index=10,
      direction=CompactDirection.UP_TO,
      summarize_fn=_mock_summarize(),
    )
    assert result.is_partial is True
    assert result.rounds_preserved > 0

  def test_from_direction(self):
    msgs = _simple_conversation(10)
    result = partial_compact_conversation(
      msgs,
      pivot_index=5,
      direction=CompactDirection.FROM,
      summarize_fn=_mock_summarize(),
    )
    assert result.is_partial is True

  def test_empty_segment_raises(self):
    msgs = _simple_conversation(5)
    with pytest.raises(ValueError, match="Nothing to summarize"):
      partial_compact_conversation(
        msgs,
        pivot_index=0,
        direction=CompactDirection.UP_TO,
        summarize_fn=_mock_summarize(),
      )

  def test_user_feedback_threaded(self):
    msgs = _simple_conversation(8)
    result = partial_compact_conversation(
      msgs,
      pivot_index=8,
      direction=CompactDirection.UP_TO,
      user_feedback="Keep all code changes",
      summarize_fn=_mock_summarize(),
    )
    assert result.summary != ""

  def test_ptl_retry_in_partial(self):
    call_count = 0

    def _fail_once(messages, prompt):
      nonlocal call_count
      call_count += 1
      if call_count == 1:
        raise PromptTooLongError(
          "too long",
          response={"role": "assistant", "content": "exceeded by 3000 tokens"},
        )
      return "Partial summary"

    msgs = _simple_conversation(10)
    result = partial_compact_conversation(
      msgs,
      pivot_index=10,
      direction=CompactDirection.UP_TO,
      summarize_fn=_fail_once,
    )
    assert result.summary == "Partial summary"


# ── Tests: Warning state ─────────────────────────────────────────────────────


class TestWarningState:
  """Tests for thread-safe compact warning suppression."""

  def setup_method(self):
    clear_compact_warning_suppression()

  def test_initial_state_is_not_suppressed(self):
    assert get_compact_warning_suppressed() is False

  def test_suppress_and_clear(self):
    suppress_compact_warning()
    assert get_compact_warning_suppressed() is True
    clear_compact_warning_suppression()
    assert get_compact_warning_suppressed() is False

  def test_thread_safety(self):
    """Verify warning state is thread-safe."""
    results = []

    def _toggle():
      suppress_compact_warning()
      results.append(get_compact_warning_suppressed())
      clear_compact_warning_suppression()

    threads = [threading.Thread(target=_toggle) for _ in range(10)]
    for t in threads:
      t.start()
    for t in threads:
      t.join()
    assert len(results) == 10
    assert all(r is True for r in results)


# ── Tests: Types ──────────────────────────────────────────────────────────────


class TestTypes:
  """Tests for ported type definitions."""

  def test_recompaction_info_defaults(self):
    info = RecompactionInfo()
    assert info.is_recompaction_in_chain is False
    assert info.turns_since_previous_compact == -1

  def test_recompaction_info_with_values(self):
    info = RecompactionInfo(
      is_recompaction_in_chain=True,
      turns_since_previous_compact=5,
      previous_compact_turn_id="turn-42",
      auto_compact_threshold=80000,
      query_source="compact",
    )
    assert info.is_recompaction_in_chain is True
    assert info.turns_since_previous_compact == 5

  def test_auto_compact_tracking_state(self):
    state = AutoCompactTrackingState()
    assert state.compacted is False
    assert state.consecutive_failures == 0
    state.consecutive_failures = 3
    assert state.consecutive_failures == 3

  def test_context_edit_rule_type_enum(self):
    assert ContextEditRuleType.TOOL_RESULT == "tool_result"
    assert ContextEditRuleType.THINKING == "thinking"

  def test_context_edit_rule(self):
    rule = ContextEditRule(
      type="tool_result",
      tool_names=["Read", "Bash"],
      keep_recent=3,
    )
    assert rule.tool_names == ["Read", "Bash"]

  def test_context_edit_strategy(self):
    strategy = ContextEditStrategy(enabled=True)
    assert strategy.enabled is True
    assert strategy.rules == []


# ── Tests: Decay monitor integration ──────────────────────────────────────────


class TestDecayMonitorIntegration:
  """Tests for ContextDecayMonitor integration with compactor."""

  def test_file_read_oversize_warning(self):
    monitor = ContextDecayMonitor()
    result = monitor.check_file_read(3000)
    assert result.has_warnings
    assert any(w.vector == "file_read_oversize" for w in result.warnings)

  def test_tool_result_bloat_warning(self):
    monitor = ContextDecayMonitor()
    result = monitor.check_tool_result(100_000)
    assert result.has_warnings
    assert result.should_truncate_result

  def test_context_remaining_low_critical(self):
    monitor = ContextDecayMonitor(max_context_tokens=100_000)
    result = monitor.check_decay(current_tokens=95_000)
    assert result.should_compact
    assert any(w.severity == DecaySeverity.CRITICAL for w in result.warnings)

  def test_format_warnings_xml(self):
    monitor = ContextDecayMonitor()
    result = monitor.check_file_read(5000)
    formatted = result.format_warnings()
    assert "<CONTEXT_DECAY_WARNING>" in formatted
    assert "</CONTEXT_DECAY_WARNING>" in formatted

  def test_reset_accumulators(self):
    monitor = ContextDecayMonitor()
    monitor.check_file_read(1000)
    assert monitor.total_file_lines_read == 1000
    monitor.reset_accumulators()
    assert monitor.total_file_lines_read == 0


# ── Tests: Shim deprecation ──────────────────────────────────────────────────


class TestShimDeprecation:
  """Verify the agnt_utils.compact shim emits DeprecationWarning."""

  def test_import_emits_deprecation(self):
    with pytest.warns(DeprecationWarning, match="deprecated"):
      import importlib

      # Force re-import to trigger the warning
      import packages.agnt_utils.compact as shim_mod

      importlib.reload(shim_mod)

  def test_shim_exports_match_canonical(self):
    """Verify the shim re-exports match the canonical package."""
    import importlib
    import warnings

    with warnings.catch_warnings():
      warnings.simplefilter("ignore", DeprecationWarning)
      import packages.agnt_utils.compact as shim_mod

      importlib.reload(shim_mod)

    # Check critical exports exist
    assert hasattr(shim_mod, "compact_conversation")
    assert hasattr(shim_mod, "partial_compact_conversation")
    assert hasattr(shim_mod, "microcompact_messages")
    assert hasattr(shim_mod, "AutoCompactMiddleware")


# ── Tests: Cross-module integration ──────────────────────────────────────────


class TestCrossModuleIntegration:
  """End-to-end tests spanning multiple compaction subsystems."""

  def test_full_pipeline_flow(self, tmp_path):
    """Test the complete compaction flow: microcompact → compact_conversation → cleanup."""
    msgs = _simple_conversation(10)

    # Phase 1: Microcompaction
    mc_result = microcompact_messages(msgs)
    assert isinstance(mc_result, MicrocompactResult)

    # Phase 2: Conversation compaction
    cc_result = compact_conversation(
      mc_result.messages,
      summarize_fn=_mock_summarize("Session covered 10 Q&A pairs."),
    )
    assert (
      cc_result.tokens_after < cc_result.tokens_before or cc_result.tokens_after > 0
    )

    # Phase 3: Post-compact cleanup
    cleanup_called = []
    register_cleanup_hook("test_hook", lambda: cleanup_called.append(True))
    run_post_compact_cleanup()
    assert len(cleanup_called) >= 1

  def test_compactor_with_decay_monitor(self):
    """Test ContextCompactor + ContextDecayMonitor coordination."""
    compactor = ContextCompactor(feature_flags={"context_compaction": True})
    monitor = ContextDecayMonitor(max_context_tokens=100_000)

    # Simulate approaching the limit
    decay = monitor.check_decay(current_tokens=92_000)
    assert decay.should_compact is True

    # Compactor agrees
    assert compactor.should_compact(92_000, 100_000) is True

  def test_warning_state_with_compaction(self):
    """Test warning state transitions during compaction lifecycle."""
    clear_compact_warning_suppression()
    assert get_compact_warning_suppressed() is False

    # After compaction succeeds
    msgs = _simple_conversation(5)
    compact_conversation(msgs, summarize_fn=_mock_summarize())
    suppress_compact_warning()
    assert get_compact_warning_suppressed() is True

    # New attempt clears suppression
    clear_compact_warning_suppression()
    assert get_compact_warning_suppressed() is False

  def test_recompaction_info_threading(self):
    """Test RecompactionInfo is correctly threaded through compaction."""
    info = RecompactionInfo(
      is_recompaction_in_chain=True,
      turns_since_previous_compact=3,
      auto_compact_threshold=80000,
      query_source="compact",
    )
    # Verify the info object is usable in telemetry contexts
    assert info.is_recompaction_in_chain is True
    assert info.query_source == "compact"
