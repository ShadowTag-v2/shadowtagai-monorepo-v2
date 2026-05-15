# Copyright 2026 ShadowTagAI. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
"""Formalized pytest-benchmark tests for bridge.handle() latency.

Migrates the ad-hoc timing from integration_demo_test.py to proper
pytest-benchmark markers for reproducible statistical analysis.

Usage:
    pytest packages/firebase_tool_bridge/benchmark_test.py --benchmark-only -v
    pytest packages/firebase_tool_bridge/benchmark_test.py --benchmark-json=.benchmarks/output.json
"""

from __future__ import annotations

import pytest

from firebase_tool_bridge.bridge import CallStatus, ToolBridge
from firebase_tool_bridge.evidence import EvidenceLogger
from firebase_tool_bridge.registry import FunctionRegistry, RiskTier


class _AutoApprove:
  """Confirmation provider that always approves — for benchmarking only."""

  def request_confirmation(self, *args, **kwargs) -> bool:
    return True


@pytest.fixture
def bench_registry() -> FunctionRegistry:
  """Registry with one function per risk tier."""
  reg = FunctionRegistry()
  reg.register("low_op", lambda **kw: {"echo": kw}, RiskTier.LOW)
  reg.register("med_op", lambda **kw: {"echo": kw}, RiskTier.MEDIUM)
  reg.register(
    "high_op",
    lambda **kw: {"echo": kw},
    RiskTier.HIGH,
    action_tags=frozenset({"deploy"}),
  )
  reg.register(
    "crit_op",
    lambda **kw: {"echo": kw},
    RiskTier.CRITICAL,
    action_tags=frozenset({"data_delete"}),
  )
  return reg


@pytest.fixture
def bench_bridge(bench_registry, tmp_path) -> ToolBridge:
  """ToolBridge wired for benchmarking with tmp evidence."""
  return ToolBridge(
    bench_registry,
    evidence=EvidenceLogger(repo_root=tmp_path),
    confirmation=_AutoApprove(),
  )


# ─── Individual Tier Benchmarks ──────────────────────────────────────────────


class TestBridgeBenchmarks:
  """pytest-benchmark formalized latency measurements.

  Each test uses the `benchmark` fixture from pytest-benchmark.
  Run with `--benchmark-disable` to skip in CI, or `--benchmark-only`
  to run benchmarks exclusively.
  """

  @pytest.mark.benchmark(group="bridge-handle", min_rounds=50, warmup=True)
  def test_bench_low_risk(self, benchmark, bench_bridge):
    """Benchmark LOW risk dispatch — no confirmation gate."""
    result = benchmark(bench_bridge.handle, "low_op", {"x": 1})
    assert result.status == CallStatus.SUCCESS

  @pytest.mark.benchmark(group="bridge-handle", min_rounds=50, warmup=True)
  def test_bench_medium_risk(self, benchmark, bench_bridge):
    """Benchmark MEDIUM risk dispatch — no confirmation gate."""
    result = benchmark(bench_bridge.handle, "med_op", {"x": 1})
    assert result.status == CallStatus.SUCCESS

  @pytest.mark.benchmark(group="bridge-handle", min_rounds=50, warmup=True)
  def test_bench_high_risk(self, benchmark, bench_bridge):
    """Benchmark HIGH risk dispatch — passes through confirmation gate."""
    result = benchmark(bench_bridge.handle, "high_op", {"target": "staging"})
    assert result.status == CallStatus.SUCCESS

  @pytest.mark.benchmark(group="bridge-handle", min_rounds=50, warmup=True)
  def test_bench_critical_risk(self, benchmark, bench_bridge):
    """Benchmark CRITICAL risk dispatch — passes through confirmation gate."""
    result = benchmark(bench_bridge.handle, "crit_op", {"target": "production"})
    assert result.status == CallStatus.SUCCESS

  @pytest.mark.benchmark(group="bridge-handle", min_rounds=50, warmup=True)
  def test_bench_unregistered_rejection(self, benchmark, bench_bridge):
    """Benchmark rejection of unregistered function calls."""
    result = benchmark(bench_bridge.handle, "nonexistent_fn", {"x": 1})
    assert result.status == CallStatus.REJECTED_UNREGISTERED

  @pytest.mark.benchmark(group="bridge-batch", min_rounds=20, warmup=True)
  def test_bench_batch_4_calls(self, benchmark, bench_bridge):
    """Benchmark batch dispatch of 4 calls (one per tier)."""
    calls = [
      ("low_op", {"x": 1}),
      ("med_op", {"x": 2}),
      ("high_op", {"target": "staging"}),
      ("crit_op", {"target": "prod"}),
    ]
    results = benchmark(bench_bridge.handle_batch, calls)
    assert len(results) == 4
    assert all(r.status == CallStatus.SUCCESS for r in results)
