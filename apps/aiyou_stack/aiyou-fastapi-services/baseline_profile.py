#!/usr/bin/env python3
"""Baseline profiling script for Judge#6 (pre‑Triton) workload.

Purpose
-------
* Load the existing Judge#6 runtime (`erik-hancock-llm-memory/judge6/runtime/base.py`).
* Execute a representative batch of inference calls.
* Measure end‑to‑end latency (including model forward pass, token handling, and any post‑processing).
* Output mean, median, p90 and p99 latency statistics.

Usage
-----
```bash
python baseline_profile.py [--batch-size N] [--seq-len L] [--iterations I]
```
* `--batch-size` – number of parallel requests (default: 256)
* `--seq-len`   – token sequence length per request (default: 256)
* `--iterations` – how many times to repeat the batch (default: 30)

The script works on CPU or GPU. If a CUDA device is available it will
synchronize before each timing measurement to ensure accurate results.
"""

import argparse
import json
import os
import sys
import time
from statistics import mean, median

import torch

# Add project root to sys.path so we can import the runtime module
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)

# Import the Judge#6 runtime (adjust import if the module path changes)
import importlib.util  # noqa: E402

# Dynamically load JudgeSixRuntime from the file path (handles hyphenated directory name)
runtime_path = os.path.join(PROJECT_ROOT, "erik-hancock-llm-memory", "judge6", "runtime", "base.py")
spec = importlib.util.spec_from_file_location("base", runtime_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
JudgeSixRuntime = getattr(module, "JudgeSixRuntime", None)
if JudgeSixRuntime is None:
    sys.stderr.write("[ERROR] JudgeSixRuntime class not found in base.py\n")
    raise SystemExit(1)


def run_batch(runtime, batch_size, seq_len):
    """Execute a single batch of dummy inputs and return elapsed time (seconds)."""
    # Create dummy input data – the actual runtime expects a dict with a token list
    dummy_input = {"tokens": [0] * seq_len}
    inputs = [dummy_input for _ in range(batch_size)]

    # Warm‑up (GPU kernels need a first run to compile)
    _ = runtime.process_batch(inputs)

    if torch.cuda.is_available():
        torch.cuda.synchronize()
    start = time.perf_counter()
    _ = runtime.process_batch(inputs)
    if torch.cuda.is_available():
        torch.cuda.synchronize()
    end = time.perf_counter()
    return end - start


def main():
    parser = argparse.ArgumentParser(description="Baseline profiling for Judge#6")
    parser.add_argument("--batch-size", type=int, default=256)
    parser.add_argument("--seq-len", type=int, default=256)
    parser.add_argument("--iterations", type=int, default=30)
    args = parser.parse_args()

    runtime = JudgeSixRuntime()
    latencies = []
    for i in range(args.iterations):
        elapsed = run_batch(runtime, args.batch_size, args.seq_len)
        latencies.append(elapsed)
        print(f"Iteration {i + 1}/{args.iterations}: {elapsed * 1000:.2f} ms")

    # Statistics (ms)
    lat_ms = [l * 1000 for l in latencies]  # noqa: E741
    print("\n=== Summary ===")
    print(f"Mean   : {mean(lat_ms):.2f} ms")
    print(f"Median : {median(lat_ms):.2f} ms")
    print(f"p90    : {sorted(lat_ms)[int(0.9 * len(lat_ms))]:.2f} ms")
    print(f"p99    : {sorted(lat_ms)[int(0.99 * len(lat_ms)) - 1]:.2f} ms")

    # Save raw results for later analysis
    out_path = os.path.join(PROJECT_ROOT, "benchmark_results", "baseline_profile.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump({"latencies_ms": lat_ms}, f, indent=2)
    print(f"Saved raw results to {out_path}")


if __name__ == "__main__":
    main()
