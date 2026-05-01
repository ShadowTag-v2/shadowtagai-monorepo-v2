# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Integration tests for Gemini Bridge ↔ Orchestrator wiring.

Tests cover:
  1. Import liveness — all bridge components importable
  2. Orchestrator init — lazy accessors resolve correctly
  3. PipelineMode auto-routing — keyword heuristic classification
  4. Bridge health probe — structured health dict
  5. OTel SpanContext — no-op fallback when opentelemetry absent
  6. Telemetry bridge logging — event emitted to .beads/

Run:
    python -m pytest tests/integration/test_gemini_bridge.py -v
"""

from __future__ import annotations

import json
import os
import sys
import pathlib

import pytest

# Ensure packages are importable from repo root
REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "packages"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))


# ---------------------------------------------------------------------------
# 1. Import liveness
# ---------------------------------------------------------------------------


class TestBridgeImports:
    """Verify all bridge module exports are importable."""

    def test_pipeline_mode_enum(self) -> None:
        from speculation_engine.gemini_bridge import PipelineMode

        assert hasattr(PipelineMode, "PAIR_PROGRAMMING")
        assert hasattr(PipelineMode, "RESEARCH_SWEEP")
        assert hasattr(PipelineMode, "HYBRID")

    def test_pair_programmer_class(self) -> None:
        from speculation_engine.gemini_bridge import GeminiPairProgrammer

        assert callable(GeminiPairProgrammer)

    def test_research_sweep_class(self) -> None:
        from speculation_engine.gemini_bridge import GeminiResearchSweep

        assert callable(GeminiResearchSweep)

    def test_sweep_result_dataclass(self) -> None:
        from speculation_engine.gemini_bridge import SweepResult

        result = SweepResult(query="test", report_text="report")
        assert result.query == "test"
        assert result.report_text == "report"
        assert result.duration_seconds == 0.0

    def test_pair_session_dataclass(self) -> None:
        from speculation_engine.gemini_bridge import PairSession

        session = PairSession(session_id="abc123")
        assert session.session_id == "abc123"
        assert session.turn_count == 0
        assert session.duration_seconds >= 0


# ---------------------------------------------------------------------------
# 2. Orchestrator init
# ---------------------------------------------------------------------------


class TestOrchestratorInit:
    """Verify orchestrator initializes and wires bridge accessors."""

    def test_init_default_config(self) -> None:
        from speculation_engine.orchestrator import (
            SpeculativeResearchOrchestrator,
        )

        orch = SpeculativeResearchOrchestrator(workspace=str(REPO_ROOT))
        assert orch._config is not None

    def test_init_disabled_speculation(self) -> None:
        from speculation_engine.orchestrator import (
            SpeculativeResearchOrchestrator,
            SpeculativeResearchConfig,
        )

        config = SpeculativeResearchConfig(
            speculate_during_research=False,
            speculate_during_synthesis=False,
            use_cow_overlay=False,
        )
        orch = SpeculativeResearchOrchestrator(workspace=str(REPO_ROOT), config=config)
        assert orch._config.speculate_during_research is False

    def test_lazy_pair_programmer(self) -> None:
        from speculation_engine.orchestrator import SpeculativeResearchOrchestrator

        orch = SpeculativeResearchOrchestrator(workspace=str(REPO_ROOT))
        pp = orch.pair_programmer
        assert pp is not None

    def test_lazy_research_sweep(self) -> None:
        from speculation_engine.orchestrator import SpeculativeResearchOrchestrator

        orch = SpeculativeResearchOrchestrator(workspace=str(REPO_ROOT))
        sweep = orch.research_sweep
        assert sweep is not None


# ---------------------------------------------------------------------------
# 3. PipelineMode auto-routing
# ---------------------------------------------------------------------------


class TestAutoRoute:
    """Verify pipeline mode auto-routing heuristics."""

    def _make_orchestrator(self):
        from speculation_engine.orchestrator import (
            SpeculativeResearchOrchestrator,
            SpeculativeResearchConfig,
        )

        return SpeculativeResearchOrchestrator(
            workspace=str(REPO_ROOT),
            config=SpeculativeResearchConfig(
                speculate_during_research=False,
                speculate_during_synthesis=False,
            ),
        )

    def test_short_query_routes_pair(self) -> None:
        from speculation_engine.gemini_bridge import PipelineMode

        orch = self._make_orchestrator()
        mode = orch.auto_route("Fix the typo in main.py")
        assert mode == PipelineMode.PAIR_PROGRAMMING

    def test_research_keyword_routes_sweep(self) -> None:
        from speculation_engine.gemini_bridge import PipelineMode

        orch = self._make_orchestrator()
        mode = orch.auto_route("Research the competitive landscape for legal AI startups")
        assert mode == PipelineMode.RESEARCH_SWEEP

    def test_analyze_keyword(self) -> None:
        from speculation_engine.gemini_bridge import PipelineMode

        orch = self._make_orchestrator()
        mode = orch.auto_route("Analyze the performance of Cloud Run cold starts")
        assert mode == PipelineMode.RESEARCH_SWEEP

    def test_long_query_routes_sweep(self) -> None:
        from speculation_engine.gemini_bridge import PipelineMode

        orch = self._make_orchestrator()
        long_query = "Please help me understand " + "x" * 200
        mode = orch.auto_route(long_query)
        assert mode == PipelineMode.RESEARCH_SWEEP

    def test_benchmark_keyword(self) -> None:
        from speculation_engine.gemini_bridge import PipelineMode

        orch = self._make_orchestrator()
        mode = orch.auto_route("Benchmark Python 3.14 vs 3.13 async performance")
        assert mode == PipelineMode.RESEARCH_SWEEP


# ---------------------------------------------------------------------------
# 4. Bridge health probe
# ---------------------------------------------------------------------------


class TestBridgeHealthProbe:
    """Verify _probe_bridge_health returns correct structure."""

    def test_probe_returns_dict(self) -> None:
        from kairos_daemon import _probe_bridge_health

        result = _probe_bridge_health()
        assert isinstance(result, dict)
        assert "healthy" in result
        assert "importable" in result
        assert "orchestrator_init" in result
        assert "sweep_ready" in result

    def test_probe_import_check(self) -> None:
        from kairos_daemon import _probe_bridge_health

        result = _probe_bridge_health()
        # All bridge components are importable in this repo
        assert result["importable"] is True

    def test_probe_orchestrator_check(self) -> None:
        from kairos_daemon import _probe_bridge_health

        result = _probe_bridge_health()
        assert result["orchestrator_init"] is True

    def test_probe_sweep_check(self) -> None:
        from kairos_daemon import _probe_bridge_health

        result = _probe_bridge_health()
        assert result["sweep_ready"] is True

    def test_probe_overall_health(self) -> None:
        from kairos_daemon import _probe_bridge_health

        result = _probe_bridge_health()
        assert result["healthy"] is True
        assert result["error"] is None


# ---------------------------------------------------------------------------
# 5. OTel SpanContext fallback
# ---------------------------------------------------------------------------


class TestSpanContext:
    """Verify SpanContext works as no-op when OTel is not installed."""

    def test_span_context_noop(self) -> None:
        from speculation_engine.telemetry import SpanContext

        # Should not raise even without opentelemetry installed
        with SpanContext("test.operation", key="value") as span:
            span.set_attribute("result", "ok")

    def test_span_context_with_exception(self) -> None:
        from speculation_engine.telemetry import SpanContext

        with pytest.raises(ValueError, match="test error"), SpanContext("test.failing_op"):
            raise ValueError("test error")


# ---------------------------------------------------------------------------
# 6. Telemetry bridge logging
# ---------------------------------------------------------------------------


class TestBridgeTelemetry:
    """Verify bridge call logging writes to .beads/ evidence trail."""

    def test_log_bridge_call(self, tmp_path: pathlib.Path) -> None:
        # Set BEADS_DIR to temp path
        os.environ["BEADS_DIR"] = str(tmp_path)
        try:
            from speculation_engine.telemetry import log_bridge_call

            log_bridge_call(
                operation="research_sweep",
                duration_ms=1234.5,
                success=True,
                query="test topic",
            )

            log_file = tmp_path / "speculation_telemetry.jsonl"
            assert log_file.exists()

            entries = [json.loads(line) for line in log_file.read_text().strip().split("\n")]
            assert len(entries) == 1
            assert entries[0]["event_type"] == "bridge_research_sweep"
            assert entries[0]["duration_ms"] == 1234.5
            assert entries[0]["success"] is True
        finally:
            del os.environ["BEADS_DIR"]

    def test_log_bridge_call_failure(self, tmp_path: pathlib.Path) -> None:
        os.environ["BEADS_DIR"] = str(tmp_path)
        try:
            from speculation_engine.telemetry import log_bridge_call

            log_bridge_call(
                operation="pair_programming",
                duration_ms=567.8,
                success=False,
                error="connection timeout",
            )

            log_file = tmp_path / "speculation_telemetry.jsonl"
            entries = [json.loads(line) for line in log_file.read_text().strip().split("\n")]
            assert entries[0]["success"] is False
            assert entries[0]["error"] == "connection timeout"
        finally:
            del os.environ["BEADS_DIR"]
