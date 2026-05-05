#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Benchmark the Bash Security Classifier pipeline at 10K iterations.

Profiles both PASS and BLOCK paths to verify sub-5ms latency target.
Uses timeit for microsecond precision.

Usage:
    python scripts/benchmark_bash_classifier.py
"""

from __future__ import annotations

import statistics
import sys
import time

sys.path.insert(0, ".")

from packages.agnt_bash_classifier.classifier import BashSecurityClassifier


def benchmark_pipeline(iterations: int = 10_000) -> dict[str, dict[str, float]]:
    """Benchmark PASS and BLOCK paths at the given iteration count.

    Returns:
        Dict with 'pass_path' and 'block_path' keys, each containing
        mean, median, p95, p99, min, max latency in milliseconds.
    """
    classifier = BashSecurityClassifier(telemetry=None)

    # Representative PASS command (benign)
    pass_cmd = "git log --oneline -10"

    # Representative BLOCK command (hits check 5 — backtick substitution)
    block_cmd = "echo `whoami`"

    # Mixed-complexity PASS command (longer, more tokens)
    complex_pass_cmd = "PAGER=cat git diff --stat HEAD~3 HEAD -- packages/agnt_bash_classifier/classifier.py"

    results: dict[str, dict[str, float]] = {}

    for label, cmd in [
        ("pass_path_simple", pass_cmd),
        ("pass_path_complex", complex_pass_cmd),
        ("block_path_early", block_cmd),
    ]:
        timings: list[float] = []
        for _ in range(iterations):
            t0 = time.perf_counter_ns()
            classifier.classify(cmd)
            elapsed_ms = (time.perf_counter_ns() - t0) / 1_000_000
            timings.append(elapsed_ms)

        timings.sort()
        results[label] = {
            "mean_ms": statistics.mean(timings),
            "median_ms": statistics.median(timings),
            "p95_ms": timings[int(len(timings) * 0.95)],
            "p99_ms": timings[int(len(timings) * 0.99)],
            "min_ms": timings[0],
            "max_ms": timings[-1],
            "iterations": iterations,
        }

    return results


def main() -> None:
    """Run the benchmark and print results."""
    print("=" * 70)
    print("  Bash Security Classifier — 10K Iteration Benchmark")
    print("=" * 70)
    print()

    results = benchmark_pipeline(10_000)

    target_ms = 5.0
    all_pass = True

    for label, stats in results.items():
        p99 = stats["p99_ms"]
        status = "✅ PASS" if p99 < target_ms else "❌ FAIL"
        if p99 >= target_ms:
            all_pass = False

        print(f"  [{label}]")
        print(f"    Mean:   {stats['mean_ms']:.3f} ms")
        print(f"    Median: {stats['median_ms']:.3f} ms")
        print(f"    P95:    {stats['p95_ms']:.3f} ms")
        print(f"    P99:    {stats['p99_ms']:.3f} ms  {status} (target <{target_ms}ms)")
        print(f"    Min:    {stats['min_ms']:.3f} ms")
        print(f"    Max:    {stats['max_ms']:.3f} ms")
        print(f"    Iters:  {int(stats['iterations'])}")
        print()

    print("=" * 70)
    if all_pass:
        print("  OVERALL: ✅ ALL PATHS UNDER 5ms P99 TARGET")
    else:
        print("  OVERALL: ❌ LATENCY TARGET EXCEEDED — INVESTIGATE")
    print("=" * 70)


if __name__ == "__main__":
    main()
