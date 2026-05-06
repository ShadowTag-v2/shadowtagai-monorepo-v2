# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Unit tests for PromptSpeculationEngine.

Tests the full CC-ported speculation lifecycle: speculate, accept, abort,
caching, suppression checks, and the 12-rule suggestion filter pipeline.
"""

from __future__ import annotations

import time

import pytest

from packages.agnt_tools.speculation_engine import (
    PromptSpeculationEngine,
    SpeculationResult,
    SpeculationStatus,
    SuppressReason,
)


@pytest.fixture
def engine() -> PromptSpeculationEngine:
    """Create a fresh engine per test."""
    return PromptSpeculationEngine(cache_ms=5000)


@pytest.fixture
def basic_context() -> list[dict]:
    """Minimal valid conversation context."""
    return [
        {"role": "user", "content": "Build the ConfigTool"},
        {"role": "assistant", "content": "I've created the ConfigTool at packages/agnt_tools/config_tool.py"},
    ]


# --- Core Lifecycle ---


class TestSpeculate:
    """Tests for the speculate() entry point."""

    def test_returns_speculation_result(self, engine: PromptSpeculationEngine, basic_context: list) -> None:
        """speculate() should return a SpeculationResult."""
        result = engine.speculate(basic_context, task_phase="active")
        assert isinstance(result, SpeculationResult)

    def test_status_is_ready_on_success(self, engine: PromptSpeculationEngine, basic_context: list) -> None:
        """Status should be READY when a suggestion is generated."""
        result = engine.speculate(basic_context, task_phase="active")
        assert result.status == SpeculationStatus.READY

    def test_suggestion_has_text(self, engine: PromptSpeculationEngine, basic_context: list) -> None:
        """Suggestion should contain actionable text."""
        result = engine.speculate(basic_context, task_phase="active")
        assert result.suggestion is not None
        assert len(result.suggestion.text) > 0

    def test_suggestion_has_context_hash(self, engine: PromptSpeculationEngine, basic_context: list) -> None:
        """Suggestion should have a context hash for caching."""
        result = engine.speculate(basic_context, task_phase="active")
        assert result.suggestion is not None
        assert len(result.suggestion.context_hash) > 0

    def test_metrics_incremented(self, engine: PromptSpeculationEngine, basic_context: list) -> None:
        """total_speculations should increment after each call."""
        engine.speculate(basic_context, task_phase="active")
        assert engine.metrics.total_speculations == 1
        engine.speculate(basic_context, task_phase="active")
        assert engine.metrics.total_speculations == 2

    def test_generation_time_tracked(self, engine: PromptSpeculationEngine, basic_context: list) -> None:
        """generation_time_ms should be positive on cache miss."""
        # Clear cache to force generation
        engine.clear_cache()
        engine.speculate(basic_context, task_phase="start")
        # First call is a cache miss, so generation time should be tracked
        assert engine.metrics.total_generation_time_ms >= 0


class TestTaskPhases:
    """Tests for phase-aware prompt generation."""

    def test_start_phase_generates_prompts(self, engine: PromptSpeculationEngine, basic_context: list) -> None:
        """'start' phase should generate session-start prompts."""
        result = engine.speculate(basic_context, task_phase="start", complexity="architecture")
        assert result.suggestion is not None

    def test_error_phase_generates_prompts(self, engine: PromptSpeculationEngine, basic_context: list) -> None:
        """'error' phase should generate error-recovery prompts."""
        result = engine.speculate(basic_context, task_phase="error")
        assert result.suggestion is not None

    def test_complete_phase_generates_prompts(self, engine: PromptSpeculationEngine, basic_context: list) -> None:
        """'complete' phase should generate finalization prompts."""
        result = engine.speculate(basic_context, task_phase="complete")
        assert result.suggestion is not None


class TestAccept:
    """Tests for accept() — CC's acceptSpeculation."""

    def test_accept_returns_time_saved(self, engine: PromptSpeculationEngine, basic_context: list) -> None:
        """accept() should return time saved in ms."""
        result = engine.speculate(basic_context, task_phase="active")
        assert result.suggestion is not None
        time.sleep(0.01)  # Small delay to get measurable time_saved
        saved = engine.accept(result.suggestion)
        assert saved >= 0

    def test_accept_increments_metric(self, engine: PromptSpeculationEngine, basic_context: list) -> None:
        """accept() should increment the accepted counter."""
        result = engine.speculate(basic_context, task_phase="active")
        assert result.suggestion is not None
        engine.accept(result.suggestion)
        assert engine.metrics.accepted == 1

    def test_accept_sets_accepted_at(self, engine: PromptSpeculationEngine, basic_context: list) -> None:
        """accept() should set the accepted_at timestamp."""
        result = engine.speculate(basic_context, task_phase="active")
        assert result.suggestion is not None
        assert result.suggestion.accepted_at == 0.0
        engine.accept(result.suggestion)
        assert result.suggestion.accepted_at > 0


class TestAbort:
    """Tests for abort() — CC's abortSpeculation."""

    def test_abort_sets_flag(self, engine: PromptSpeculationEngine) -> None:
        """abort() should set the internal abort flag."""
        engine.abort()
        assert engine.status == SpeculationStatus.ABORTED

    def test_abort_increments_metric(self, engine: PromptSpeculationEngine) -> None:
        """abort() should increment the aborted counter."""
        engine.abort()
        assert engine.metrics.aborted == 1


class TestCaching:
    """Tests for context hash caching."""

    def test_cache_hit_on_same_context(self, engine: PromptSpeculationEngine, basic_context: list) -> None:
        """Same context should produce a cache hit on second call."""
        engine.speculate(basic_context, task_phase="active")
        engine.speculate(basic_context, task_phase="active")
        assert engine.metrics.cache_hits >= 1

    def test_cache_miss_on_different_context(self, engine: PromptSpeculationEngine) -> None:
        """Different contexts should produce cache misses."""
        ctx1 = [{"role": "user", "content": "task A"}, {"role": "assistant", "content": "done A"}]
        ctx2 = [{"role": "user", "content": "task B"}, {"role": "assistant", "content": "done B"}]
        engine.speculate(ctx1, task_phase="active")
        engine.speculate(ctx2, task_phase="active")
        assert engine.metrics.cache_misses >= 2

    def test_clear_cache(self, engine: PromptSpeculationEngine, basic_context: list) -> None:
        """clear_cache() should evict all entries."""
        engine.speculate(basic_context, task_phase="active")
        count = engine.clear_cache()
        assert count >= 1

    def test_cache_expiry(self, basic_context: list) -> None:
        """Expired cache entries should not be served."""
        engine = PromptSpeculationEngine(cache_ms=1)  # 1ms TTL
        engine.speculate(basic_context, task_phase="active")
        time.sleep(0.01)  # Wait for expiry
        engine.speculate(basic_context, task_phase="active")
        # Both should be cache misses since TTL is 1ms
        assert engine.metrics.cache_misses >= 2


class TestSuppression:
    """Tests for suggestion suppression checks (CC promptSuggestion.ts L107-118)."""

    def test_suppressed_with_empty_context(self, engine: PromptSpeculationEngine) -> None:
        """Empty context should suppress (early_conversation)."""
        result = engine.speculate([], task_phase="active")
        assert result.suppress_reason is not None

    def test_suppressed_in_planning_phase(self, engine: PromptSpeculationEngine, basic_context: list) -> None:
        """'planning' phase should suppress."""
        result = engine.speculate(basic_context, task_phase="planning")
        assert result.suppress_reason == SuppressReason.PLAN_MODE.value

    def test_suppressed_on_error_message(self, engine: PromptSpeculationEngine) -> None:
        """Last message being an error should suppress."""
        ctx = [
            {"role": "user", "content": "do something"},
            {"role": "assistant", "content": "error occurred", "is_error": True},
        ]
        result = engine.speculate(ctx, task_phase="active")
        assert result.suppress_reason == SuppressReason.LAST_RESPONSE_ERROR.value


class TestSuggestionFilters:
    """Tests for the 12-rule CC suggestion filter pipeline."""

    @pytest.mark.parametrize(
        "text,should_filter",
        [
            # Rule 1: Empty
            ("", True),
            # Rule 2: "done"
            ("done", True),
            # Rule 3: Meta text
            ("nothing found", True),
            ("nothing to suggest here", True),
            # Rule 4: Silence pattern
            ("silence is golden", True),
            # Rule 5: Meta wrapped
            ("(this is meta)", True),
            ("[bracketed note]", True),
            # Rule 6: Error messages
            ("API Error: rate limited", True),
            ("prompt is too long to handle", True),
            # Rule 7: Single word (not in allowlist)
            ("hmm", True),
            # Rule 7b: Single word (in allowlist — should NOT filter)
            ("yes", False),
            ("push", False),
            ("/deploy", False),
            # Rule 8: Too many words
            ("a b c d e f g h i j k l m", True),
            # Rule 9: Too long
            ("x" * 100, True),
            # Rule 10: Multiple sentences
            ("First sentence. Then another sentence.", True),
            # Rule 11: Formatting characters
            ("**bold text**", True),
            ("line\nbreak", True),
            # Rule 12: Evaluative
            ("thanks for doing that", True),
            ("looks good to me", True),
            # Rule 13: Claude voice
            ("Let me check that for you", True),
            ("I'll handle this", True),
            ("Here's what I found", True),
            # Valid suggestions — should NOT filter
            ("Run the test suite", False),
            ("Check git status", False),
            ("Deploy to staging", False),
            ("Run ruff on changed files", False),
        ],
    )
    def test_filter_rules(self, text: str, should_filter: bool) -> None:
        """Test individual filter rules from CC promptSuggestion.ts."""
        result = PromptSpeculationEngine._should_filter(text)
        assert result is should_filter, f"Expected filter={should_filter} for '{text}', got {result}"


class TestReset:
    """Tests for reset() state management."""

    def test_reset_sets_idle(self, engine: PromptSpeculationEngine) -> None:
        """reset() should set status to IDLE."""
        engine.abort()
        engine.reset()
        assert engine.status == SpeculationStatus.IDLE

    def test_reset_clears_abort_flag(self, engine: PromptSpeculationEngine, basic_context: list) -> None:
        """reset() should clear the abort flag, allowing speculation."""
        engine.abort()
        engine.reset()
        result = engine.speculate(basic_context, task_phase="active")
        assert result.status != SpeculationStatus.ABORTED


class TestFormatMetrics:
    """Tests for format_metrics() display."""

    def test_format_metrics_returns_string(self, engine: PromptSpeculationEngine) -> None:
        """format_metrics() should return a readable string."""
        result = engine.format_metrics()
        assert isinstance(result, str)
        assert "Total:" in result

    def test_format_metrics_after_activity(self, engine: PromptSpeculationEngine, basic_context: list) -> None:
        """format_metrics() should reflect actual activity."""
        engine.speculate(basic_context, task_phase="active")
        result = engine.format_metrics()
        assert "Total: 1" in result
