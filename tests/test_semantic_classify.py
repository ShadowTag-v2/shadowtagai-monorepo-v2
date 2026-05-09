# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Hypothesis property-based tests for _semantic_classify() edge cases.

Tests the structured semantic intent classifier in the orchestrator
using property-based fuzzing to find edge cases in scoring logic.
"""

from __future__ import annotations

import sys
import time

import pytest
from hypothesis import given, settings, assume
from hypothesis import strategies as st

sys.path.insert(0, "packages")

from speculation_engine.feature_flags import FeatureFlagStore, SpecFlags
from speculation_engine.orchestrator import SpeculativeResearchOrchestrator


@pytest.fixture
def orchestrator() -> SpeculativeResearchOrchestrator:
    """Create an orchestrator with semantic routing enabled."""
    flags = FeatureFlagStore.create()
    flags.set_flag(SpecFlags.SEMANTIC_ROUTING, True)
    orch = SpeculativeResearchOrchestrator(workspace="/tmp/test", flags=flags)
    orch._session_id = "test-semantic"
    return orch


@pytest.fixture
def keyword_orchestrator() -> SpeculativeResearchOrchestrator:
    """Create an orchestrator with keyword routing."""
    flags = FeatureFlagStore.create()
    flags.set_flag(SpecFlags.SEMANTIC_ROUTING, False)
    orch = SpeculativeResearchOrchestrator(workspace="/tmp/test", flags=flags)
    orch._session_id = "test-keyword"
    return orch


class TestSemanticClassifyProperties:
    """Property-based tests for _semantic_classify()."""

    @given(query=st.text(min_size=1, max_size=500))
    @settings(max_examples=200, deadline=1000)
    def test_always_returns_valid_pipeline_mode(self, query: str) -> None:
        """_semantic_classify always returns a valid PipelineMode."""
        assume(query.strip())  # Skip empty-ish strings
        flags = FeatureFlagStore.create()
        orch = SpeculativeResearchOrchestrator(workspace="/tmp/test", flags=flags)

        from speculation_engine.gemini_bridge import PipelineMode

        result = orch._semantic_classify(query)
        assert result in (PipelineMode.PAIR_PROGRAMMING, PipelineMode.RESEARCH_SWEEP)

    @given(query=st.text(min_size=1, max_size=500))
    @settings(max_examples=200, deadline=1000)
    def test_never_raises(self, query: str) -> None:
        """_semantic_classify never raises an exception on any input."""
        assume(query.strip())
        flags = FeatureFlagStore.create()
        orch = SpeculativeResearchOrchestrator(workspace="/tmp/test", flags=flags)

        # This must not raise
        orch._semantic_classify(query)

    @given(query=st.text(min_size=1, max_size=500))
    @settings(max_examples=200, deadline=1000)
    def test_deterministic(self, query: str) -> None:
        """Same query always produces the same result."""
        assume(query.strip())
        flags = FeatureFlagStore.create()
        orch = SpeculativeResearchOrchestrator(workspace="/tmp/test", flags=flags)

        result1 = orch._semantic_classify(query)
        result2 = orch._semantic_classify(query)
        assert result1 == result2

    @given(query=st.text(min_size=1, max_size=500))
    @settings(max_examples=100, deadline=2000)
    def test_latency_under_20ms_cold(self, query: str) -> None:
        """Every classification completes in under 20ms (cold start budget).

        Cold start includes FeatureFlagStore.create() disk I/O for
        .beads/feature_flags.json. The warmed 5ms target is validated
        separately in test_latency_under_5ms_warmed.
        """
        assume(query.strip())
        flags = FeatureFlagStore.create()
        orch = SpeculativeResearchOrchestrator(workspace="/tmp/test", flags=flags)

        start = time.perf_counter()
        orch._semantic_classify(query)
        elapsed_ms = (time.perf_counter() - start) * 1000

        assert elapsed_ms < 20.0, f"Classification took {elapsed_ms:.2f}ms (limit: 20ms cold)"

    def test_latency_under_5ms_warmed(self) -> None:
        """After warmup, classification completes in under 5ms."""
        flags = FeatureFlagStore.create()
        orch = SpeculativeResearchOrchestrator(workspace="/tmp/test", flags=flags)

        # Warmup — absorb JIT + disk cache penalty
        orch._semantic_classify("warmup query")

        queries = [
            "fix the bug",
            "research the competitive landscape of vector databases and analyze trade-offs",
            "compare React vs Vue for our architecture. Evaluate pros and cons.",
            "!@#$%^&*()",
            "a" * 300,
        ]
        for query in queries:
            start = time.perf_counter()
            orch._semantic_classify(query)
            elapsed_ms = (time.perf_counter() - start) * 1000
            assert elapsed_ms < 5.0, f"Warmed classification took {elapsed_ms:.2f}ms (limit: 5ms)"


class TestSemanticClassifyEdgeCases:
    """Targeted edge cases for _semantic_classify()."""

    def test_empty_string(self, orchestrator: SpeculativeResearchOrchestrator) -> None:
        """Empty string should route to pair programming (low complexity)."""
        from speculation_engine.gemini_bridge import PipelineMode

        result = orchestrator._semantic_classify("")
        assert result == PipelineMode.PAIR_PROGRAMMING

    def test_single_word(self, orchestrator: SpeculativeResearchOrchestrator) -> None:
        """Single word → pair programming."""
        from speculation_engine.gemini_bridge import PipelineMode

        result = orchestrator._semantic_classify("help")
        assert result == PipelineMode.PAIR_PROGRAMMING

    def test_research_keyword_triggers_research(self, orchestrator: SpeculativeResearchOrchestrator) -> None:
        """Strong research signal → research sweep."""
        from speculation_engine.gemini_bridge import PipelineMode

        result = orchestrator._semantic_classify("research the competitive landscape of vector databases and analyze trade-offs")
        assert result == PipelineMode.RESEARCH_SWEEP

    def test_pure_action_stays_pair_programming(self, orchestrator: SpeculativeResearchOrchestrator) -> None:
        """Pure action command → pair programming."""
        from speculation_engine.gemini_bridge import PipelineMode

        result = orchestrator._semantic_classify("fix the bug")
        assert result == PipelineMode.PAIR_PROGRAMMING

    def test_long_simple_query(self, orchestrator: SpeculativeResearchOrchestrator) -> None:
        """Long query with no research markers still respects length factor."""
        from speculation_engine.gemini_bridge import PipelineMode

        # Very long but no research keywords — length alone gives max 0.3,
        # which is below the 0.4 threshold
        query = "please " * 50
        result = orchestrator._semantic_classify(query)
        assert result == PipelineMode.PAIR_PROGRAMMING

    def test_comparison_query_routes_to_research(self, orchestrator: SpeculativeResearchOrchestrator) -> None:
        """Comparison query with enough signals → research sweep."""
        from speculation_engine.gemini_bridge import PipelineMode

        result = orchestrator._semantic_classify("compare React vs Vue for our architecture. Evaluate pros and cons.")
        assert result == PipelineMode.RESEARCH_SWEEP

    def test_multi_hop_reasoning_query(self, orchestrator: SpeculativeResearchOrchestrator) -> None:
        """Multi-hop reasoning indicators increase complexity score."""
        from speculation_engine.gemini_bridge import PipelineMode

        result = orchestrator._semantic_classify(
            "First investigate the cache layer, and then analyze why latency spikes happen. After that, benchmark the alternatives."
        )
        assert result == PipelineMode.RESEARCH_SWEEP

    def test_unicode_input(self, orchestrator: SpeculativeResearchOrchestrator) -> None:
        """Unicode input doesn't crash the classifier."""
        from speculation_engine.gemini_bridge import PipelineMode

        result = orchestrator._semantic_classify("研究してください 🚀 analyze the 性能")
        assert result in (PipelineMode.PAIR_PROGRAMMING, PipelineMode.RESEARCH_SWEEP)

    def test_special_chars_only(self, orchestrator: SpeculativeResearchOrchestrator) -> None:
        """Special characters don't crash."""
        from speculation_engine.gemini_bridge import PipelineMode

        result = orchestrator._semantic_classify("!@#$%^&*()")
        assert result == PipelineMode.PAIR_PROGRAMMING

    def test_newlines_and_whitespace(self, orchestrator: SpeculativeResearchOrchestrator) -> None:
        """Whitespace-heavy queries work correctly."""
        from speculation_engine.gemini_bridge import PipelineMode

        result = orchestrator._semantic_classify("  \n\t  fix the button  \n  ")
        assert result == PipelineMode.PAIR_PROGRAMMING


class TestAutoRouteIntegration:
    """Integration tests for auto_route() with flag-gated classifiers."""

    def test_keyword_route_short_query(self, keyword_orchestrator: SpeculativeResearchOrchestrator) -> None:
        """Short query with keyword classifier → pair programming."""
        from speculation_engine.gemini_bridge import PipelineMode

        result = keyword_orchestrator.auto_route("fix the button")
        assert result == PipelineMode.PAIR_PROGRAMMING

    def test_keyword_route_research_query(self, keyword_orchestrator: SpeculativeResearchOrchestrator) -> None:
        """Research keyword with keyword classifier → research sweep."""
        from speculation_engine.gemini_bridge import PipelineMode

        result = keyword_orchestrator.auto_route("research the caching landscape")
        assert result == PipelineMode.RESEARCH_SWEEP

    def test_semantic_route_matches_keyword_on_clear_signals(
        self,
        orchestrator: SpeculativeResearchOrchestrator,
        keyword_orchestrator: SpeculativeResearchOrchestrator,
    ) -> None:
        """Both classifiers agree on clearly short queries."""
        from speculation_engine.gemini_bridge import PipelineMode

        short_query = "fix bug"
        result_sem = orchestrator.auto_route(short_query)
        result_kw = keyword_orchestrator.auto_route(short_query)
        assert result_sem == result_kw == PipelineMode.PAIR_PROGRAMMING

    def test_flag_toggle_switches_classifier(self) -> None:
        """Toggling SEMANTIC_ROUTING flag at runtime switches classifier."""
        from speculation_engine.gemini_bridge import PipelineMode

        flags = FeatureFlagStore.create()
        orch = SpeculativeResearchOrchestrator(workspace="/tmp/test", flags=flags)
        orch._session_id = "toggle-test"

        # Default: keyword
        flags.set_flag(SpecFlags.SEMANTIC_ROUTING, False)
        result1 = orch.auto_route("fix the button")

        # Enable semantic
        flags.set_flag(SpecFlags.SEMANTIC_ROUTING, True)
        result2 = orch.auto_route("fix the button")

        # Both should return pair programming for a short query
        assert result1 == result2 == PipelineMode.PAIR_PROGRAMMING
