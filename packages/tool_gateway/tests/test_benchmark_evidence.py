# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Benchmark tests for AsyncEvidenceLogger throughput.

Quantifies the I/O gain of async vs sync evidence logging paths.
Uses pytest-benchmark for statistically rigorous measurements.

Metrics:
  - log_execution latency (async path with aiofiles)
  - log_execution latency (sync fallback path)
  - Throughput: operations/second for burst logging
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from unittest.mock import MagicMock


from tool_gateway.async_evidence import AsyncEvidenceLogger


def _make_logger(tmp_path: Path) -> AsyncEvidenceLogger:
    """Create an AsyncEvidenceLogger writing to a temp directory."""
    beads_dir = tmp_path / ".beads"
    beads_dir.mkdir()
    return AsyncEvidenceLogger(beads_dir)


def _make_decision() -> MagicMock:
    """Create a mock Decision object for benchmarking."""
    decision = MagicMock()
    decision.allowed = True
    decision.reason = "benchmark_test"
    decision.contract_id = "bench-001"
    decision.reuse_hints = []
    decision.preconditions_met = True
    return decision


# ─── Benchmark: log_execution async path ────────────────────────────
class TestAsyncEvidenceBenchmark:
    """Benchmark suite for AsyncEvidenceLogger operations."""

    def test_log_execution_latency(self, benchmark, tmp_path):
        """Measure single log_execution call latency."""
        logger = _make_logger(tmp_path)

        def run():
            asyncio.run(
                logger.log_execution("bench-tool", success=True, detail="benchmark run")
            )

        benchmark(run)

        # Verify file was actually written
        issues_file = tmp_path / ".beads" / "issues.jsonl"
        assert issues_file.exists()
        lines = issues_file.read_text().strip().split("\n")
        assert len(lines) > 0

    def test_log_check_latency(self, benchmark, tmp_path):
        """Measure single log_check call latency."""
        logger = _make_logger(tmp_path)
        decision = _make_decision()
        context = {"tool": "benchmark", "action": "test", "uid": "b001"}

        def run():
            asyncio.run(
                logger.log_check("bench-tool", context, decision)
            )

        benchmark(run)

    def test_burst_throughput(self, benchmark, tmp_path):
        """Measure throughput of 100 sequential log writes."""
        logger = _make_logger(tmp_path)

        async def burst_100():
            for i in range(100):
                await logger.log_execution(
                    f"tool-{i}", success=True, detail=f"burst entry {i}"
                )

        def run():
            asyncio.run(burst_100())

        benchmark(run)

        # Verify all 100 entries written per iteration
        issues_file = tmp_path / ".beads" / "issues.jsonl"
        lines = issues_file.read_text().strip().split("\n")
        # At least 100 lines from the last benchmark iteration
        assert len(lines) >= 100

    def test_sync_fallback_latency(self, benchmark, tmp_path, monkeypatch):
        """Measure latency when aiofiles is NOT available (sync fallback)."""
        import tool_gateway.async_evidence as mod

        monkeypatch.setattr(mod, "_HAS_AIOFILES", False)
        logger = _make_logger(tmp_path)

        def run():
            asyncio.run(
                logger.log_execution("sync-bench", success=True, detail="sync path")
            )

        benchmark(run)
