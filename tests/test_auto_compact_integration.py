# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Integration tests — multi-turn conversation simulations.

Tests the full auto-compact middleware flow including:
  - Session loop integration (should_compact → compact_if_needed)
  - Circuit breaker tripping after N failures
  - Token warning state machine transitions
  - Post-compact cleanup hook invocation
  - Two-phase (proactive + reactive) orchestration
  - API context management config building
  - Compaction prompt formatting
"""

from __future__ import annotations


import pytest

from context_compactor.api_context_management import (
    TOOLS_CLEARABLE_RESULTS,
    TOOLS_CLEARABLE_USES,
    StrategyType,
    build_api_context_management,
)
from context_compactor.auto_compact import (
    AutoCompactMiddleware,
    AutoCompactTracker,
    calculate_token_warning_state,
    get_auto_compact_threshold,
    get_effective_context_window,
)
from context_compactor.compact_prompts import (
    format_compact_summary,
    get_compact_prompt,
    get_compact_user_summary_message,
    get_partial_compact_prompt,
)
from context_compactor.post_compact_cleanup import (
    PostCompactCleanupState,
    is_main_thread_compact,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_messages(count: int, tokens_per_msg: int = 500) -> list[dict]:
    """Create dummy messages with ~tokens_per_msg tokens each."""
    content = "x " * (tokens_per_msg * 4)  # ~4 bytes per token
    return [{"role": "assistant" if i % 2 else "user", "content": content} for i in range(count)]


class MockCompactor:
    """Minimal mock of ContextCompactor for middleware testing."""

    def __init__(self, *, should_fail: bool = False) -> None:
        self._should_fail = should_fail
        self.run_count = 0

    @property
    def is_enabled(self) -> bool:
        return True

    def run(self, messages, target_tokens, current_tokens, max_layer=4):
        self.run_count += 1
        if self._should_fail:
            raise RuntimeError("Compaction failed")
        from context_compactor.layers import CompactionResult

        return CompactionResult(
            tokens_before=current_tokens,
            tokens_after=target_tokens,
            layer_used="L1",
        )


# ===========================================================================
# Test: Effective Context Window
# ===========================================================================


class TestEffectiveContextWindow:
    def test_basic_calculation(self) -> None:
        result = get_effective_context_window(200_000)
        assert result < 200_000
        assert result > 150_000

    def test_with_override(self) -> None:
        result = get_effective_context_window(200_000, auto_compact_window_override=100_000)
        assert result < 100_000

    def test_override_larger_than_context(self) -> None:
        result = get_effective_context_window(200_000, auto_compact_window_override=300_000)
        # Should use the smaller of the two
        assert result < 200_000


class TestAutoCompactThreshold:
    def test_basic_threshold(self) -> None:
        threshold = get_auto_compact_threshold(200_000)
        assert threshold > 0
        assert threshold < 200_000

    def test_with_percent_override(self) -> None:
        threshold_normal = get_auto_compact_threshold(200_000)
        threshold_50pct = get_auto_compact_threshold(200_000, percent_override=50)
        assert threshold_50pct < threshold_normal

    def test_invalid_percent_ignored(self) -> None:
        threshold = get_auto_compact_threshold(200_000, percent_override=-10)
        threshold_normal = get_auto_compact_threshold(200_000)
        assert threshold == threshold_normal


# ===========================================================================
# Test: Token Warning State Machine
# ===========================================================================


class TestTokenWarningState:
    def test_healthy_state(self) -> None:
        state = calculate_token_warning_state(10_000, 200_000)
        assert state.percent_left > 50
        assert not state.is_above_warning_threshold
        assert not state.is_above_error_threshold
        assert not state.is_above_auto_compact_threshold

    def test_warning_state(self) -> None:
        threshold = get_auto_compact_threshold(200_000)
        state = calculate_token_warning_state(threshold - 5000, 200_000)
        assert state.is_above_warning_threshold

    def test_auto_compact_state(self) -> None:
        threshold = get_auto_compact_threshold(200_000)
        state = calculate_token_warning_state(threshold + 1000, 200_000)
        assert state.is_above_auto_compact_threshold

    def test_disabled_auto_compact(self) -> None:
        threshold = get_auto_compact_threshold(200_000)
        state = calculate_token_warning_state(
            threshold + 1000,
            200_000,
            auto_compact_enabled=False,
        )
        assert not state.is_above_auto_compact_threshold


# ===========================================================================
# Test: Auto-Compact Tracker
# ===========================================================================


class TestAutoCompactTracker:
    def test_initial_state(self) -> None:
        tracker = AutoCompactTracker()
        assert tracker.consecutive_failures == 0
        assert not tracker.compacted

    def test_success_resets(self) -> None:
        tracker = AutoCompactTracker(consecutive_failures=2, compacted=False)
        tracker.reset_on_success()
        assert tracker.consecutive_failures == 0
        assert tracker.compacted

    def test_failure_increments(self) -> None:
        tracker = AutoCompactTracker()
        tracker.record_failure()
        assert tracker.consecutive_failures == 1
        tracker.record_failure()
        assert tracker.consecutive_failures == 2
        tracker.record_failure()
        assert tracker.consecutive_failures == 3  # Circuit breaker tripped


# ===========================================================================
# Test: Auto-Compact Middleware
# ===========================================================================


class TestAutoCompactMiddleware:
    def test_no_compact_below_threshold(self) -> None:
        compactor = MockCompactor()
        tracker = AutoCompactTracker()
        middleware = AutoCompactMiddleware(compactor, tracker)

        messages = _make_messages(5, tokens_per_msg=100)
        result = middleware.compact_if_needed(
            messages,
            max_context_tokens=200_000,
            query_source="repl_main_thread",
        )
        assert not result.was_compacted
        assert compactor.run_count == 0

    def test_compact_above_threshold(self) -> None:
        compactor = MockCompactor()
        tracker = AutoCompactTracker()
        middleware = AutoCompactMiddleware(compactor, tracker)

        messages = _make_messages(200, tokens_per_msg=1000)
        result = middleware.compact_if_needed(
            messages,
            max_context_tokens=200_000,
            query_source="repl_main_thread",
        )
        assert result.was_compacted
        assert compactor.run_count == 1

    def test_recursion_guard(self) -> None:
        compactor = MockCompactor()
        tracker = AutoCompactTracker()
        middleware = AutoCompactMiddleware(compactor, tracker)

        messages = _make_messages(200, tokens_per_msg=1000)
        result = middleware.compact_if_needed(
            messages,
            max_context_tokens=200_000,
            query_source="compact",
        )
        assert not result.was_compacted

    def test_circuit_breaker(self) -> None:
        compactor = MockCompactor(should_fail=True)
        tracker = AutoCompactTracker()
        middleware = AutoCompactMiddleware(compactor, tracker)

        messages = _make_messages(200, tokens_per_msg=1000)

        # First 3 failures
        for i in range(3):
            result = middleware.compact_if_needed(
                messages,
                max_context_tokens=200_000,
            )
            assert not result.was_compacted

        # 4th attempt should be skipped by circuit breaker
        result = middleware.compact_if_needed(
            messages,
            max_context_tokens=200_000,
        )
        assert not result.was_compacted
        assert compactor.run_count == 3  # Not 4

    def test_disabled_middleware(self) -> None:
        compactor = MockCompactor()
        tracker = AutoCompactTracker()
        middleware = AutoCompactMiddleware(
            compactor,
            tracker,
            auto_compact_enabled=False,
        )

        messages = _make_messages(200, tokens_per_msg=1000)
        result = middleware.compact_if_needed(
            messages,
            max_context_tokens=200_000,
        )
        assert not result.was_compacted


# ===========================================================================
# Test: Post-Compact Cleanup
# ===========================================================================


class TestPostCompactCleanup:
    def test_main_thread_detection(self) -> None:
        assert is_main_thread_compact(None)
        assert is_main_thread_compact("repl_main_thread")
        assert is_main_thread_compact("main")
        assert is_main_thread_compact("sdk")
        assert not is_main_thread_compact("agent:subagent_1")
        assert not is_main_thread_compact("compact")

    def test_cleanup_hooks_fire(self) -> None:
        state = PostCompactCleanupState()
        called = []
        state.register_hook("test_hook", lambda: called.append("fired"))
        state.run()
        assert called == ["fired"]

    def test_main_thread_only_hooks(self) -> None:
        state = PostCompactCleanupState()
        called = []
        state.register_hook(
            "main_only",
            lambda: called.append("main"),
            main_thread_only=True,
        )

        # Subagent should NOT fire main-thread hooks
        state.run("agent:sub")
        assert called == []

        # Main thread should fire
        state.run("repl_main_thread")
        assert called == ["main"]

    def test_hook_failure_is_caught(self) -> None:
        state = PostCompactCleanupState()
        state.register_hook("bad_hook", lambda: 1 / 0)
        state.register_hook("good_hook", lambda: None)
        results = state.run()
        assert results["bad_hook"] is False
        assert results["good_hook"] is True


# ===========================================================================
# Test: API Context Management
# ===========================================================================


class TestAPIContextManagement:
    def test_empty_config(self) -> None:
        config = build_api_context_management(
            enable_tool_result_clearing=False,
        )
        assert config is None

    def test_thinking_only(self) -> None:
        config = build_api_context_management(
            has_thinking=True,
            enable_tool_result_clearing=False,
        )
        assert config is not None
        assert len(config.edits) == 1
        assert config.edits[0].strategy_type == StrategyType.CLEAR_THINKING

    def test_clear_all_thinking(self) -> None:
        config = build_api_context_management(
            has_thinking=True,
            clear_all_thinking=True,
            enable_tool_result_clearing=False,
        )
        assert config is not None
        assert config.edits[0].keep == {"thinking_turns": 1}

    def test_tool_result_clearing(self) -> None:
        config = build_api_context_management(
            enable_tool_result_clearing=True,
        )
        assert config is not None
        found_tool_strategy = False
        for edit in config.edits:
            if hasattr(edit, "clear_tool_inputs"):
                found_tool_strategy = True
        assert found_tool_strategy

    def test_both_strategies(self) -> None:
        config = build_api_context_management(
            has_thinking=True,
            enable_tool_result_clearing=True,
            enable_tool_use_clearing=True,
        )
        assert config is not None
        assert len(config.edits) == 3  # thinking + results + uses

    def test_clearable_tools_are_frozensets(self) -> None:
        assert isinstance(TOOLS_CLEARABLE_RESULTS, frozenset)
        assert isinstance(TOOLS_CLEARABLE_USES, frozenset)
        assert "Bash" in TOOLS_CLEARABLE_RESULTS
        assert "Edit" in TOOLS_CLEARABLE_USES

    def test_serialization(self) -> None:
        config = build_api_context_management(
            has_thinking=True,
            enable_tool_result_clearing=True,
        )
        assert config is not None
        api_dict = config.to_api_dict()
        assert api_dict is not None
        assert "edits" in api_dict
        assert len(api_dict["edits"]) == 2


# ===========================================================================
# Test: Compaction Prompts
# ===========================================================================


class TestCompactPrompts:
    def test_base_prompt_structure(self) -> None:
        prompt = get_compact_prompt()
        assert "CRITICAL: Respond with TEXT ONLY" in prompt
        assert "Primary Request and Intent" in prompt
        assert "REMINDER: Do NOT call any tools" in prompt

    def test_custom_instructions(self) -> None:
        prompt = get_compact_prompt("Focus on Python code changes")
        assert "Focus on Python code changes" in prompt

    def test_partial_prompt(self) -> None:
        prompt = get_partial_compact_prompt()
        assert "RECENT portion" in prompt

    def test_format_summary_strips_analysis(self) -> None:
        raw = "<analysis>thinking here</analysis>\n<summary>the result</summary>"
        result = format_compact_summary(raw)
        assert "thinking here" not in result
        assert "the result" in result
        assert "Summary:" in result

    def test_format_summary_no_tags(self) -> None:
        raw = "plain text summary"
        result = format_compact_summary(raw)
        assert result == "plain text summary"

    def test_user_summary_message(self) -> None:
        msg = get_compact_user_summary_message("test summary")
        assert "continued from a previous conversation" in msg
        assert "test summary" in msg

    def test_user_summary_with_transcript(self) -> None:
        msg = get_compact_user_summary_message(
            "test",
            transcript_path="/tmp/transcript.md",
        )
        assert "/tmp/transcript.md" in msg

    def test_user_summary_suppress_followup(self) -> None:
        msg = get_compact_user_summary_message("test", suppress_follow_up=True)
        assert "Resume directly" in msg

    def test_user_summary_recent_preserved(self) -> None:
        msg = get_compact_user_summary_message("test", recent_preserved=True)
        assert "preserved verbatim" in msg


# ===========================================================================
# Test: Multi-Turn Conversation Integration
# ===========================================================================


class TestMultiTurnIntegration:
    """Simulate realistic multi-turn conversation compaction scenarios."""

    def test_progressive_context_growth(self) -> None:
        """Simulate a conversation growing past the threshold.

        Uses a 50K context window so threshold is reachable with
        realistic message sizes within 50 turns.
        """
        compactor = MockCompactor()
        tracker = AutoCompactTracker()
        middleware = AutoCompactMiddleware(compactor, tracker)

        messages: list[dict] = []

        # Grow the conversation gradually — 50K window is ~37K threshold
        for turn in range(50):
            messages.append({"role": "user", "content": f"User message {turn} " * 200})
            messages.append({"role": "assistant", "content": f"Response {turn} " * 400})

            result = middleware.compact_if_needed(
                messages,
                max_context_tokens=50_000,
            )

            if result.was_compacted:
                # Reset — in real life the compactor would rewrite messages
                messages = messages[-10:]
                break
        else:
            pytest.fail("Expected compaction to trigger before 50 turns")

    def test_recovery_after_circuit_breaker(self) -> None:
        """Verify that resetting the tracker allows compaction to resume."""
        tracker = AutoCompactTracker(consecutive_failures=3)
        compactor = MockCompactor()
        middleware = AutoCompactMiddleware(compactor, tracker)

        messages = _make_messages(200, tokens_per_msg=1000)

        # Should be blocked by circuit breaker
        result = middleware.compact_if_needed(messages, max_context_tokens=200_000)
        assert not result.was_compacted

        # Reset and try again
        tracker.reset_on_success()
        result = middleware.compact_if_needed(messages, max_context_tokens=200_000)
        assert result.was_compacted

    def test_two_phase_flow(self) -> None:
        """Simulate the proactive + reactive two-phase compaction."""
        from context_compactor.compactor import ContextCompactor
        from context_compactor.micro_compact import MicrocompactResult

        # Phase 1: Proactive microcompaction
        compactor = ContextCompactor(
            feature_flags={"context_compaction": True},
        )
        messages = [
            {"role": "user", "content": "hello"},
            {"role": "assistant", "content": "hi there"},
        ]
        pre_result = compactor.pre_compact(messages)
        assert isinstance(pre_result, MicrocompactResult)

        # Phase 2: Reactive pipeline (if needed)
        # This would fire if tokens exceed threshold
        # In this test, tokens are low so it should be a no-op
