# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Tests for packages/speculation_engine — the CC v2.1.91 3-stage pipeline port.

Coverage:
  - OverlayFS: CoW write/read/merge/cleanup
  - SpeculationEngine: start/complete/abort/accept lifecycle
  - Tool permissions: 4-tier (read/write/bash/denied) boundary classification
  - Suggestion: enablement gates, suppression, 12-rule filter
  - Telemetry: event logging to .beads/
  - Message preparation: thinking block removal, INTERRUPT filtering
"""

from __future__ import annotations

from pathlib import Path

import pytest

from speculation_engine import (
  SAFE_READ_TOOLS,
  WRITE_TOOLS,
  BoundaryType,
  CompletionBoundary,
  FilterReason,
  OverlayFS,
  SessionState,
  SpeculationEngine,
  SpeculationState,
  SuggestionConfig,
  SuppressReason,
  check_enablement_gates,
  get_suggestion_suppress_reason,
  log_speculation_event,
  log_suggestion_event,
  prepare_messages_for_injection,
  should_filter_suggestion,
  try_generate_suggestion,
)


# ── OverlayFS CoW Tests ──────────────────────────────────────────


class TestOverlayFS:
  def test_create_overlay(self, tmp_path: Path) -> None:
    overlay = OverlayFS.create(tmp_path)
    assert overlay.base_dir == tmp_path
    assert overlay.overlay_dir.exists()
    overlay.cleanup()

  def test_write_and_read(self, tmp_path: Path) -> None:
    overlay = OverlayFS.create(tmp_path)
    overlay.write_file("test.txt", "hello world")
    assert overlay.read_file("test.txt") == "hello world"
    overlay.cleanup()

  def test_read_falls_through_to_base(self, tmp_path: Path) -> None:
    (tmp_path / "base.txt").write_text("base content")
    overlay = OverlayFS.create(tmp_path)
    assert overlay.read_file("base.txt") == "base content"
    overlay.cleanup()

  def test_write_shadows_base(self, tmp_path: Path) -> None:
    (tmp_path / "file.txt").write_text("original")
    overlay = OverlayFS.create(tmp_path)
    overlay.write_file("file.txt", "modified")
    assert overlay.read_file("file.txt") == "modified"
    # Base should be unchanged
    assert (tmp_path / "file.txt").read_text() == "original"
    overlay.cleanup()

  def test_copy_to_main_merges(self, tmp_path: Path) -> None:
    overlay = OverlayFS.create(tmp_path)
    overlay.write_file("new.txt", "merged content")
    merged = overlay.copy_to_main()
    assert "new.txt" in merged
    assert (tmp_path / "new.txt").read_text() == "merged content"
    overlay.cleanup()

  def test_written_files_tracking(self, tmp_path: Path) -> None:
    overlay = OverlayFS.create(tmp_path)
    overlay.write_file("a.txt", "a")
    overlay.write_file("b.txt", "b")
    assert overlay.written_files == frozenset({"a.txt", "b.txt"})
    overlay.cleanup()

  def test_read_nonexistent_returns_none(self, tmp_path: Path) -> None:
    overlay = OverlayFS.create(tmp_path)
    assert overlay.read_file("nonexistent.txt") is None
    overlay.cleanup()

  def test_cleanup_removes_overlay_dir(self, tmp_path: Path) -> None:
    overlay = OverlayFS.create(tmp_path)
    overlay_path = overlay.overlay_dir
    overlay.cleanup()
    assert not overlay_path.exists()

  def test_nested_paths(self, tmp_path: Path) -> None:
    overlay = OverlayFS.create(tmp_path)
    overlay.write_file("deep/nested/file.txt", "deep")
    assert overlay.read_file("deep/nested/file.txt") == "deep"
    overlay.cleanup()


# ── SpeculationEngine Lifecycle Tests ─────────────────────────────


class TestSpeculationEngineLifecycle:
  def test_initial_state_idle(self) -> None:
    engine = SpeculationEngine(cwd="/tmp")
    assert engine.state == SpeculationState.IDLE

  def test_start_transitions_to_active(self, tmp_path: Path) -> None:
    engine = SpeculationEngine(cwd=str(tmp_path))
    engine.start()
    assert engine.state == SpeculationState.ACTIVE
    assert engine.overlay is not None
    engine.abort()

  def test_complete_transitions_to_complete(self, tmp_path: Path) -> None:
    engine = SpeculationEngine(cwd=str(tmp_path))
    engine.start()
    engine.complete(output_tokens=42)
    assert engine.state == SpeculationState.COMPLETE
    assert engine.boundary is not None
    assert engine.boundary.type == BoundaryType.COMPLETE
    assert engine.boundary.output_tokens == 42
    engine.abort()

  def test_abort_transitions_to_idle(self, tmp_path: Path) -> None:
    engine = SpeculationEngine(cwd=str(tmp_path))
    engine.start()
    engine.abort("user_typed")
    assert engine.state == SpeculationState.IDLE
    assert engine.overlay is None

  def test_accept_returns_result_dict(self, tmp_path: Path) -> None:
    engine = SpeculationEngine(cwd=str(tmp_path))
    engine.start()
    engine.on_message({"role": "assistant", "content": "test"})
    engine.complete()
    result = engine.accept()
    assert isinstance(result, dict)
    assert "messages" in result
    assert "boundary" in result
    assert "time_saved_ms" in result
    assert "merged_files" in result

  def test_accept_merges_overlay(self, tmp_path: Path) -> None:
    engine = SpeculationEngine(cwd=str(tmp_path))
    engine.start()
    assert engine.overlay is not None
    engine.overlay.write_file("spec.txt", "speculative content")
    engine.complete()
    result = engine.accept()
    assert "spec.txt" in result["merged_files"]
    assert (tmp_path / "spec.txt").read_text() == "speculative content"

  def test_accept_resets_state(self, tmp_path: Path) -> None:
    engine = SpeculationEngine(cwd=str(tmp_path))
    engine.start()
    engine.complete()
    engine.accept()
    assert engine.state == SpeculationState.IDLE

  def test_pipelined_suggestion_flow(self, tmp_path: Path) -> None:
    engine = SpeculationEngine(cwd=str(tmp_path))
    engine.start()
    engine.set_pipelined_suggestion("Run tests next")
    assert engine.state == SpeculationState.WAITING_ACCEPT
    assert engine.pipelined_suggestion == "Run tests next"
    engine.abort()


# ── Tool Permission Tests ─────────────────────────────────────────


class TestToolPermissions:
  @pytest.fixture
  def engine(self, tmp_path: Path) -> SpeculationEngine:
    eng = SpeculationEngine(cwd=str(tmp_path))
    eng.start()
    return eng

  @pytest.mark.parametrize("tool_name", list(SAFE_READ_TOOLS)[:5])
  def test_read_tools_allowed(self, engine: SpeculationEngine, tool_name: str) -> None:
    allowed, boundary = engine.can_use_tool(tool_name)
    assert allowed is True
    assert boundary is None
    engine.abort()

  @pytest.mark.parametrize("tool_name", list(WRITE_TOOLS)[:3])
  def test_write_tools_blocked_without_bypass(
    self, engine: SpeculationEngine, tool_name: str
  ) -> None:
    allowed, boundary = engine.can_use_tool(tool_name, file_path="/tmp/test.py")
    assert allowed is False
    assert boundary is not None
    assert boundary.type == BoundaryType.EDIT
    engine.abort()

  def test_write_tools_allowed_with_bypass(self, tmp_path: Path) -> None:
    # Security model: bypass_permissions alone is not enough.
    # trust_level >= 2 (Always Allow) is required for write operations.
    # Use the .create() factory which maps trust_level → bypass_permissions.
    engine = SpeculationEngine.create(cwd=str(tmp_path), trust_level=2)
    engine.start()
    allowed, boundary = engine.can_use_tool("Edit", file_path=str(tmp_path / "f.py"))
    assert allowed is True
    assert boundary is None
    engine.abort()

  def test_bash_read_only_allowed(self, engine: SpeculationEngine) -> None:
    allowed, boundary = engine.can_use_tool("Bash", command="git status")
    assert allowed is True
    assert boundary is None
    engine.abort()

  def test_bash_write_blocked(self, engine: SpeculationEngine) -> None:
    allowed, boundary = engine.can_use_tool("Bash", command="rm -rf /")
    assert allowed is False
    assert boundary is not None
    assert boundary.type == BoundaryType.BASH
    engine.abort()

  def test_unknown_tool_denied(self, engine: SpeculationEngine) -> None:
    allowed, boundary = engine.can_use_tool("SomeUnknownTool")
    assert allowed is False
    assert boundary is not None
    assert boundary.type == BoundaryType.DENIED_TOOL
    engine.abort()

  def test_write_outside_cwd_blocked(self, engine: SpeculationEngine) -> None:
    allowed, boundary = engine.can_use_tool("Edit", file_path="/etc/passwd")
    assert allowed is False
    assert boundary is not None
    assert boundary.detail == "outside_cwd"
    engine.abort()

  def test_tools_executed_counter(self, engine: SpeculationEngine) -> None:
    engine.can_use_tool("Read")
    engine.can_use_tool("Glob")
    assert engine.tools_executed == 2
    engine.abort()


# ── Message Limits Tests ──────────────────────────────────────────


class TestMessageLimits:
  def test_turn_limit_triggers_abort(self, tmp_path: Path) -> None:
    engine = SpeculationEngine(cwd=str(tmp_path))
    engine.start()
    for i in range(21):
      engine.on_message({"role": "assistant", "content": f"turn {i}"})
    assert engine.state == SpeculationState.IDLE


# ── Suggestion Enablement Gates Tests ─────────────────────────────


class TestEnablementGates:
  def test_all_gates_pass(self) -> None:
    config = SuggestionConfig()
    assert check_enablement_gates(config) is None

  def test_env_override_false(self) -> None:
    config = SuggestionConfig(env_override=False)
    assert check_enablement_gates(config) == SuppressReason.ENV_OVERRIDE

  def test_feature_flag_off(self) -> None:
    config = SuggestionConfig(feature_flag_enabled=False)
    assert check_enablement_gates(config) == SuppressReason.FEATURE_FLAG_OFF

  def test_non_interactive(self) -> None:
    config = SuggestionConfig(is_interactive=False)
    assert check_enablement_gates(config) == SuppressReason.NON_INTERACTIVE

  def test_swarm_teammate(self) -> None:
    config = SuggestionConfig(is_swarm_leader=False)
    assert check_enablement_gates(config) == SuppressReason.SWARM_TEAMMATE

  def test_disabled(self) -> None:
    config = SuggestionConfig(enabled=False)
    assert check_enablement_gates(config) == SuppressReason.DISABLED


# ── Session Suppression Tests ─────────────────────────────────────


class TestSessionSuppression:
  def test_no_suppression_default(self) -> None:
    state = SessionState(assistant_turn_count=3)
    config = SuggestionConfig()
    assert get_suggestion_suppress_reason(state, config) is None

  def test_pending_permission(self) -> None:
    state = SessionState(pending_permission=True, assistant_turn_count=3)
    config = SuggestionConfig()
    assert (
      get_suggestion_suppress_reason(state, config) == SuppressReason.PENDING_PERMISSION
    )

  def test_elicitation_active(self) -> None:
    state = SessionState(elicitation_active=True, assistant_turn_count=3)
    config = SuggestionConfig()
    assert (
      get_suggestion_suppress_reason(state, config) == SuppressReason.ELICITATION_ACTIVE
    )

  def test_plan_mode(self) -> None:
    state = SessionState(plan_mode=True, assistant_turn_count=3)
    config = SuggestionConfig()
    assert get_suggestion_suppress_reason(state, config) == SuppressReason.PLAN_MODE

  def test_too_few_turns(self) -> None:
    state = SessionState(assistant_turn_count=0)
    config = SuggestionConfig()
    assert get_suggestion_suppress_reason(state, config) == SuppressReason.TOO_FEW_TURNS

  def test_cache_cold(self) -> None:
    state = SessionState(assistant_turn_count=3, last_request_tokens=20_000)
    config = SuggestionConfig(cache_cold_threshold=10_000)
    assert get_suggestion_suppress_reason(state, config) == SuppressReason.CACHE_COLD


# ── 12-Rule Suggestion Filter Tests ──────────────────────────────


class TestSuggestionFilter:
  @pytest.mark.parametrize(
    "text,expected",
    [
      ("", FilterReason.META_TEXT),
      ("done", FilterReason.DONE),
      ("nothing found", FilterReason.META_TEXT),
      ("no suggestion needed", FilterReason.META_TEXT),
      ("(this is meta)", FilterReason.META_WRAPPED),
      ("[bracketed note]", FilterReason.META_WRAPPED),
      ("API Error: 500", FilterReason.ERROR_MESSAGE),
      ("rate limit exceeded", FilterReason.ERROR_MESSAGE),
      ("Result: found it", FilterReason.PREFIXED_LABEL),
      ("hmm", FilterReason.TOO_FEW_WORDS),
      ("a b c d e f g h i j k l m", FilterReason.TOO_MANY_WORDS),
      ("abcdefghij " * 10 + "end", FilterReason.TOO_LONG),
      ("First sentence. Then another.", FilterReason.MULTIPLE_SENTENCES),
      ("**bold text**", FilterReason.HAS_FORMATTING),
      ("line\nbreak", FilterReason.HAS_FORMATTING),
      ("thanks for that", FilterReason.EVALUATIVE),
      ("looks good to me", FilterReason.EVALUATIVE),
      ("Let me check that", FilterReason.CLAUDE_VOICE),
      ("I'll handle this", FilterReason.CLAUDE_VOICE),
    ],
  )
  def test_filter_catches(self, text: str, expected: FilterReason) -> None:
    assert should_filter_suggestion(text) == expected

  @pytest.mark.parametrize(
    "text",
    [
      "Run the test suite",
      "Check git status",
      "Deploy to staging",
      "yes",
      "push",
      "/deploy",
      "Run ruff on files",
    ],
  )
  def test_filter_passes_valid(self, text: str) -> None:
    assert should_filter_suggestion(text) is None


# ── try_generate_suggestion Tests ─────────────────────────────────


class TestTryGenerateSuggestion:
  def test_suppressed_when_no_generate_fn(self) -> None:
    state = SessionState(assistant_turn_count=3)
    config = SuggestionConfig()
    result = try_generate_suggestion([], state, config)
    assert result.suppressed is True

  def test_suppressed_on_abort_signal(self) -> None:
    state = SessionState(assistant_turn_count=3)
    config = SuggestionConfig()
    result = try_generate_suggestion([], state, config, abort_signal=True)
    assert result.suppressed is True

  def test_generates_with_fn(self) -> None:
    def gen_fn(msgs, prompt):
      return "Run the tests", "gen-123"

    state = SessionState(assistant_turn_count=3)
    config = SuggestionConfig()
    result = try_generate_suggestion([], state, config, generate_fn=gen_fn)
    assert result.suggestion == "Run the tests"
    assert result.generation_request_id == "gen-123"

  def test_filters_bad_suggestion(self) -> None:
    def gen_fn(msgs, prompt):
      return "done", "gen-456"

    state = SessionState(assistant_turn_count=3)
    config = SuggestionConfig()
    result = try_generate_suggestion([], state, config, generate_fn=gen_fn)
    assert result.filtered is True
    assert result.filter_reason == FilterReason.DONE


# ── Message Preparation Tests ─────────────────────────────────────


class TestPrepareMessages:
  def test_removes_thinking_blocks(self) -> None:
    msgs = [
      {
        "role": "assistant",
        "content": [
          {"type": "thinking", "text": "..."},
          {"type": "text", "text": "actual response"},
        ],
      },
    ]
    cleaned = prepare_messages_for_injection(msgs, None)
    assert len(cleaned) == 1
    assert len(cleaned[0]["content"]) == 1
    assert cleaned[0]["content"][0]["type"] == "text"

  def test_removes_interrupt_messages(self) -> None:
    msgs = [
      {
        "role": "user",
        "content": [
          {"type": "text", "text": "INTERRUPT_MESSAGE_FOR_TOOL_USE stop"},
        ],
      },
    ]
    cleaned = prepare_messages_for_injection(msgs, None)
    assert len(cleaned) == 0

  def test_strips_trailing_assistant_on_boundary(self) -> None:
    msgs = [
      {"role": "user", "content": "hello"},
      {"role": "assistant", "content": "partial"},
    ]
    boundary = CompletionBoundary(type=BoundaryType.BASH)
    cleaned = prepare_messages_for_injection(msgs, boundary)
    assert len(cleaned) == 1
    assert cleaned[0]["role"] == "user"

  def test_keeps_all_on_complete(self) -> None:
    msgs = [
      {"role": "user", "content": "hello"},
      {"role": "assistant", "content": "done"},
    ]
    boundary = CompletionBoundary(type=BoundaryType.COMPLETE)
    cleaned = prepare_messages_for_injection(msgs, boundary)
    assert len(cleaned) == 2


# ── Telemetry Tests ───────────────────────────────────────────────


class TestTelemetry:
  def test_log_suggestion_event_no_crash(
    self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
  ) -> None:
    monkeypatch.setenv("BEADS_DIR", str(tmp_path / ".beads"))
    log_suggestion_event(event="test", reason="unit_test")
    log_file = tmp_path / ".beads" / "speculation_telemetry.jsonl"
    assert log_file.exists()

  def test_log_speculation_event_no_crash(
    self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
  ) -> None:
    monkeypatch.setenv("BEADS_DIR", str(tmp_path / ".beads"))
    log_speculation_event(event="test", duration_ms=100.0)
    log_file = tmp_path / ".beads" / "speculation_telemetry.jsonl"
    assert log_file.exists()


# ── CompletionBoundary Tests ──────────────────────────────────────


class TestCompletionBoundary:
  def test_bash_boundary(self) -> None:
    b = CompletionBoundary(type=BoundaryType.BASH, command="npm install")
    assert b.type == BoundaryType.BASH
    assert b.command == "npm install"

  def test_edit_boundary(self) -> None:
    b = CompletionBoundary(type=BoundaryType.EDIT, file_path="main.py")
    assert b.file_path == "main.py"

  def test_complete_boundary_tokens(self) -> None:
    b = CompletionBoundary(type=BoundaryType.COMPLETE, output_tokens=500)
    assert b.output_tokens == 500
