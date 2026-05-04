#!/usr/bin/env python3
# Copyright 2026 ShadowTag AI. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
"""cProfile hotspot analysis for bridge.handle().

Profiles the bridge dispatch path to identify performance bottlenecks
beyond wall-clock timing. Outputs cumulative and per-call stats.

Usage:
    python packages/firebase_tool_bridge/profile_bridge.py
    python packages/firebase_tool_bridge/profile_bridge.py --calls 500
"""

from __future__ import annotations

import argparse
import cProfile
import pstats
import tempfile
from io import StringIO
from pathlib import Path

from firebase_tool_bridge.bridge import ToolBridge
from firebase_tool_bridge.evidence import EvidenceLogger
from firebase_tool_bridge.registry import FunctionRegistry, RiskTier


class _AutoApprove:
    def request_confirmation(self, *args, **kwargs):
        return True


def build_bridge(tmp_dir: Path) -> ToolBridge:
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
    return ToolBridge(reg, evidence=EvidenceLogger(repo_root=tmp_dir), confirmation=_AutoApprove())


def build_bridge_async(tmp_dir: Path) -> ToolBridge:
    """Build a bridge with async evidence writer for comparison."""
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
    return ToolBridge(
        reg,
        evidence=EvidenceLogger(repo_root=tmp_dir, async_writes=True),
        confirmation=_AutoApprove(),
    )


def _run_calls(bridge: ToolBridge, n_calls: int) -> float:
    """Run n_calls through the bridge and return elapsed seconds."""
    import time

    tiers = [
        ("low_op", {"x": 1}),
        ("med_op", {"x": 2}),
        ("high_op", {"target": "stg"}),
        ("crit_op", {"target": "prod"}),
    ]

    start = time.perf_counter()
    for i in range(n_calls):
        fn_name, args = tiers[i % len(tiers)]
        bridge.handle(fn_name, args)
    return time.perf_counter() - start


def run_profile(n_calls: int = 200) -> None:
    tmp_dir = Path(tempfile.mkdtemp())
    tmp_dir_async = Path(tempfile.mkdtemp())

    bridge_sync = build_bridge(tmp_dir)
    bridge_async = build_bridge_async(tmp_dir_async)

    tiers = [
        ("low_op", {"x": 1}),
        ("med_op", {"x": 2}),
        ("high_op", {"target": "stg"}),
        ("crit_op", {"target": "prod"}),
    ]

    # --- Sync profile ---
    profiler = cProfile.Profile()
    profiler.enable()
    for i in range(n_calls):
        fn_name, args = tiers[i % len(tiers)]
        bridge_sync.handle(fn_name, args)
    profiler.disable()

    stream = StringIO()
    stats = pstats.Stats(profiler, stream=stream)
    stats.sort_stats("cumulative")

    print(f"\n{'=' * 70}")
    print(f"  cProfile: bridge.handle() × {n_calls} calls ({n_calls // 4} per tier)")
    print("  Mode: SYNC evidence writer")
    print(f"{'=' * 70}\n")

    stats.print_stats(30)
    print(stream.getvalue())

    stream2 = StringIO()
    stats2 = pstats.Stats(profiler, stream=stream2)
    stats2.sort_stats("tottime")
    print(f"\n{'=' * 70}")
    print("  Top 10 by total time (self-time hotspots)")
    print(f"{'=' * 70}\n")
    stats2.print_stats(10)
    print(stream2.getvalue())

    # --- Comparison: Sync vs Async ---
    print(f"\n{'=' * 70}")
    print(f"  COMPARISON: Sync vs Async Evidence Writer ({n_calls} calls)")
    print(f"{'=' * 70}\n")

    sync_time = _run_calls(build_bridge(Path(tempfile.mkdtemp())), n_calls)
    async_time = _run_calls(build_bridge_async(Path(tempfile.mkdtemp())), n_calls)

    sync_per_call_us = (sync_time / n_calls) * 1_000_000
    async_per_call_us = (async_time / n_calls) * 1_000_000
    delta_pct = ((sync_time - async_time) / sync_time) * 100 if sync_time > 0 else 0

    print(f"  {'Mode':<20} {'Total (ms)':>12} {'Per-call (µs)':>15} {'Delta':>10}")
    print(f"  {'-' * 60}")
    print(f"  {'Sync':<20} {sync_time * 1000:>12.2f} {sync_per_call_us:>15.1f} {'baseline':>10}")
    print(f"  {'Async':<20} {async_time * 1000:>12.2f} {async_per_call_us:>15.1f} {f'-{delta_pct:.1f}%':>10}")
    print(f"\n  Async is {delta_pct:.1f}% faster ({sync_per_call_us - async_per_call_us:.1f}µs saved per call)\n")

    # Flush async writer
    bridge_async._evidence.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Profile bridge.handle()")
    parser.add_argument("--calls", type=int, default=200, help="Number of calls")
    args = parser.parse_args()
    run_profile(args.calls)
