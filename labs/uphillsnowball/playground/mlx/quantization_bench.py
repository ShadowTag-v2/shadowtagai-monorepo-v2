"""Playground: MLX quantization benchmark.

Tests MLX model loading and quantization on Apple Silicon GPU.
Runtime: local Apple Silicon only (M-series).

Per AGENTS.md: labs must not redefine product truth.
"""

from __future__ import annotations

import time


def benchmark_import() -> dict[str, str | float]:
    """Benchmark MLX import time (proxy for GPU readiness)."""
    results: dict[str, str | float] = {}

    start = time.perf_counter()
    try:
        import mlx.core as mx  # noqa: F401

        elapsed = time.perf_counter() - start
        results["mlx_import_ms"] = round(elapsed * 1000, 2)
        results["mlx_available"] = "yes"
        results["default_device"] = str(mx.default_device())
    except ImportError:
        results["mlx_available"] = "no — pip install mlx"
        results["mlx_import_ms"] = -1

    return results


if __name__ == "__main__":
    result = benchmark_import()
    for k, v in result.items():
        print(f"  {k}: {v}")
