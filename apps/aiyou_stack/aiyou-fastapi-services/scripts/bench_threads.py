#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""CPU-bound threading benchmark for Python 3.14 free-threaded vs GIL builds.

Measures the scaling of multi-threaded CPU work.
Expected behavior:
- GIL build: No speedup with more threads (GIL serializes)
- Free-threaded build: ~Linear speedup up to core count
"""

import sys
import threading
import time

N = 4_000_000  # Iterations per thread


def cpu_work() -> int:
    """Pure-Python CPU-bound work (no I/O, no C extensions)."""
    total = 0
    for i in range(1, N):
        total += i % 97  # Arbitrary computation
    return total


def run_threads(num_threads: int) -> float:
    """Run cpu_work in parallel across num_threads threads.
    Returns wall-clock time in seconds.
    """
    results: list[int] = [0] * num_threads

    def worker(index: int):
        results[index] = cpu_work()

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(num_threads)]

    start = time.time()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    elapsed = time.time() - start

    return elapsed


def main():
    print(f"Python {sys.version}")
    print(f"Threading benchmark (N={N:,} iterations per thread)\n")

    # Check if free-threaded build
    is_free_threaded = not hasattr(sys, "getswitchinterval")
    gil_status = "FREE-THREADED (no GIL)" if is_free_threaded else "GIL build"
    print(f"Build type: {gil_status}\n")

    print("threads | time (s) | speedup vs 1-thread")
    print("--------|----------|--------------------")

    baseline_time = None
    for num_threads in [1, 2, 4, 8]:
        elapsed = run_threads(num_threads)
        if baseline_time is None:
            baseline_time = elapsed
        speedup = baseline_time / elapsed if elapsed > 0 else 0.0
        print(f"   {num_threads:2d}   |  {elapsed:6.2f}  |   {speedup:.2f}x")

    print()
    if is_free_threaded:
        print("✓ Free-threaded build: you should see speedup > 1x with more threads.")
    else:
        print("⚠ GIL build: speedup will be ~1x regardless of thread count.")


if __name__ == "__main__":
    main()
