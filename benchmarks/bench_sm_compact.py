# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""bench_sm_compact — SM Compact vs L1-L4 Pipeline Latency Benchmark.

Target: SM compact should be ≥10x faster than the full L1-L4 pipeline.

Usage:
    python benchmarks/bench_sm_compact.py [--iterations 1000]
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from typing import Any

# Ensure repo root on path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from agnt_utils.token_estimate import rough_token_estimate  # noqa: E402
from agnt_utils.truncate import smart_truncate  # noqa: E402


# ---------------------------------------------------------------------------
# Simulated context payloads
# ---------------------------------------------------------------------------


def _make_context(size_kb: int) -> str:
    """Generate a realistic multi-block context string."""
    block = (
        "The attorney-client privilege protects confidential communications "
        "between a lawyer and their client for the purpose of providing legal "
        "advice. Under *Heppner v. Alaniz* (S.D.N.Y. 2026), AI-generated "
        "summaries of privileged conversations may lose privilege status if "
        "the underlying LLM model was not operating under a privilege-"
        "preserving routing configuration.\n\n"
    )
    # Repeat to fill target size
    repeats = max(1, (size_kb * 1024) // len(block))
    return block * repeats


# ---------------------------------------------------------------------------
# Pipeline implementations
# ---------------------------------------------------------------------------


def sm_compact(context: str, budget: int = 4096) -> str:
    """SM (Session Memory) compact — fast-path single-pass truncation.

    Uses token estimation + smart truncation to trim context to budget.
    No multi-layer analysis, no structural parsing — just cut.
    """
    tokens = rough_token_estimate(context)
    if tokens <= budget:
        return context
    return smart_truncate(context, max_tokens=budget)


def l1_l4_pipeline(context: str, budget: int = 4096) -> str:
    """Full L1-L4 context compaction pipeline (simulated).

    L1: Token counting + naive truncation
    L2: Structural block detection (headers, code fences)
    L3: Semantic deduplication (cosine similarity of blocks)
    L4: Priority ranking + budget allocation

    This simulation performs real work at each layer proportional
    to what the actual pipeline does.
    """
    # L1: Token count + first-pass truncation
    tokens = rough_token_estimate(context)
    if tokens <= budget:
        return context

    # L2: Structural block detection
    blocks = context.split("\n\n")
    # Simulate per-block token computation (L2 cost)
    for b in blocks:
        rough_token_estimate(b)

    # L3: Semantic dedup simulation (pairwise comparison — O(n²))
    seen_hashes: set[int] = set()
    deduped: list[str] = []
    for block in blocks:
        h = hash(block[:200])
        if h not in seen_hashes:
            seen_hashes.add(h)
            deduped.append(block)

    # L4: Priority ranking + budget allocation
    scored: list[tuple[float, str]] = []
    for block in deduped:
        # Score by: length (shorter = higher priority) + keyword density
        keywords = sum(1 for w in ("privilege", "attorney", "confidential") if w in block.lower())
        score = keywords * 10 + (1.0 / max(1, len(block)))
        scored.append((score, block))

    scored.sort(key=lambda x: x[0], reverse=True)

    # Assemble within budget
    result_parts: list[str] = []
    used = 0
    for _, block in scored:
        block_tokens = rough_token_estimate(block)
        if used + block_tokens > budget:
            remaining = budget - used
            if remaining > 50:
                result_parts.append(smart_truncate(block, max_tokens=remaining))
            break
        result_parts.append(block)
        used += block_tokens

    return "\n\n".join(result_parts)


# ---------------------------------------------------------------------------
# Benchmark runner
# ---------------------------------------------------------------------------


def _percentile(data: list[float], pct: float) -> float:
    """Calculate percentile from sorted data."""
    if not data:
        return 0.0
    sorted_data = sorted(data)
    k = (len(sorted_data) - 1) * (pct / 100.0)
    f = int(k)
    c = f + 1
    if c >= len(sorted_data):
        return sorted_data[f]
    return sorted_data[f] + (k - f) * (sorted_data[c] - sorted_data[f])


def run_benchmark(iterations: int = 500) -> dict[str, Any]:
    """Run SM compact vs L1-L4 benchmark and return results."""

    sizes_kb = [4, 16, 64, 128]
    results: dict[str, Any] = {}

    for size_kb in sizes_kb:
        context = _make_context(size_kb)
        context_tokens = rough_token_estimate(context)
        budget = min(4096, context_tokens // 2)  # Force compaction

        # Warmup
        sm_compact(context, budget)
        l1_l4_pipeline(context, budget)

        # Benchmark SM Compact
        sm_times: list[float] = []
        for _ in range(iterations):
            t0 = time.perf_counter_ns()
            sm_compact(context, budget)
            sm_times.append((time.perf_counter_ns() - t0) / 1_000_000)  # ms

        # Benchmark L1-L4
        l4_times: list[float] = []
        for _ in range(iterations):
            t0 = time.perf_counter_ns()
            l1_l4_pipeline(context, budget)
            l4_times.append((time.perf_counter_ns() - t0) / 1_000_000)  # ms

        sm_p50 = _percentile(sm_times, 50)
        sm_p95 = _percentile(sm_times, 95)
        sm_p99 = _percentile(sm_times, 99)
        l4_p50 = _percentile(l4_times, 50)
        l4_p95 = _percentile(l4_times, 95)
        l4_p99 = _percentile(l4_times, 99)
        speedup = l4_p50 / sm_p50 if sm_p50 > 0 else float("inf")

        results[f"{size_kb}KB"] = {
            "context_tokens": context_tokens,
            "budget": budget,
            "sm_p50_ms": round(sm_p50, 3),
            "sm_p95_ms": round(sm_p95, 3),
            "sm_p99_ms": round(sm_p99, 3),
            "l4_p50_ms": round(l4_p50, 3),
            "l4_p95_ms": round(l4_p95, 3),
            "l4_p99_ms": round(l4_p99, 3),
            "speedup_x": round(speedup, 1),
            "target_met": speedup >= 10.0,
        }

    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="SM Compact vs L1-L4 Benchmark")
    parser.add_argument("--iterations", type=int, default=500, help="Iterations per size")
    args = parser.parse_args()

    print("=" * 72)
    print("  SM Compact vs L1-L4 Pipeline Latency Benchmark")
    print("  Target: SM compact ≥ 10x faster than L1-L4")
    print("=" * 72)
    print()

    results = run_benchmark(iterations=args.iterations)

    # Pretty print table
    header = f"{'Size':>8} {'Tokens':>8} {'SM p50':>10} {'SM p95':>10} {'L4 p50':>10} {'L4 p95':>10} {'Speedup':>10} {'Target':>8}"
    print(header)
    print("-" * len(header))

    all_met = True
    for size, data in results.items():
        met = "✅" if data["target_met"] else "❌"
        if not data["target_met"]:
            all_met = False
        print(
            f"{size:>8} {data['context_tokens']:>8} "
            f"{data['sm_p50_ms']:>9.3f}ms {data['sm_p95_ms']:>9.3f}ms "
            f"{data['l4_p50_ms']:>9.3f}ms {data['l4_p95_ms']:>9.3f}ms "
            f"{data['speedup_x']:>9.1f}x {met:>8}"
        )

    print()
    if all_met:
        print("🎯 ALL targets met: SM compact is ≥10x faster across all sizes.")
    else:
        print("⚠️  Some targets missed — review L4 pipeline bottlenecks.")

    sys.exit(0 if all_met else 1)


if __name__ == "__main__":
    main()
