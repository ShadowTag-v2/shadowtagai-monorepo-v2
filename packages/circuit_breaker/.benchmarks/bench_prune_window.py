#!/usr/bin/env python3
"""Benchmark: _prune_window under concurrent multi-threaded load.

Profiles the sliding window pruning path with ThreadPoolExecutor to
measure lock contention, pruning throughput, and deque integrity under
concurrent reads/writes from multiple threads.

Usage:
    python -m packages.circuit_breaker..benchmarks.bench_prune_window
    # or
    python packages/circuit_breaker/.benchmarks/bench_prune_window.py
"""

from __future__ import annotations

import statistics
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

# Ensure package importable — packages/ dir must be on path
# so that `circuit_breaker` resolves as a top-level package
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from circuit_breaker.breaker import CircuitBreaker, FailureMode


def _make_breaker(
    window_s: float = 5.0,
    threshold: int = 100,
) -> CircuitBreaker:
    """Create a sliding-window breaker for benchmarking."""
    return CircuitBreaker(
        service_name="bench_prune",
        failure_threshold=threshold,
        reset_timeout_s=60.0,
        failure_mode=FailureMode.SLIDING_WINDOW,
        window_s=window_s,
    )


def bench_concurrent_record_failure(
    n_threads: int = 8,
    ops_per_thread: int = 5_000,
    window_s: float = 5.0,
) -> dict:
    """Hammer record_failure from N threads and measure throughput + contention.

    Each thread calls record_failure() which internally acquires the lock,
    appends to the deque, and calls _prune_window().
    """
    breaker = _make_breaker(window_s=window_s, threshold=ops_per_thread * n_threads + 1)
    total_ops = n_threads * ops_per_thread
    thread_times: list[float] = []

    def _worker() -> float:
        t0 = time.perf_counter()
        for _ in range(ops_per_thread):
            breaker.record_failure()
        return time.perf_counter() - t0

    wall_start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=n_threads) as pool:
        futures = [pool.submit(_worker) for _ in range(n_threads)]
        for f in as_completed(futures):
            thread_times.append(f.result())
    wall_elapsed = time.perf_counter() - wall_start

    return {
        "test": "concurrent_record_failure",
        "threads": n_threads,
        "ops_per_thread": ops_per_thread,
        "total_ops": total_ops,
        "wall_time_s": round(wall_elapsed, 4),
        "throughput_ops_s": round(total_ops / wall_elapsed),
        "mean_thread_time_s": round(statistics.mean(thread_times), 4),
        "max_thread_time_s": round(max(thread_times), 4),
        "deque_len": len(breaker._events),
    }


def bench_concurrent_mixed_read_write(
    n_writers: int = 4,
    n_readers: int = 4,
    ops_per_thread: int = 5_000,
    window_s: float = 2.0,
) -> dict:
    """Mixed workload: writers call record_failure, readers call window_failures.

    This exercises the contention path where _prune_window is called by both
    record_failure (write path) and window_failures property (read path).
    """
    breaker = _make_breaker(window_s=window_s, threshold=999_999)
    writer_times: list[float] = []
    reader_times: list[float] = []

    def _writer() -> float:
        t0 = time.perf_counter()
        for i in range(ops_per_thread):
            if i % 3 == 0:
                breaker.record_success()
            else:
                breaker.record_failure()
        return time.perf_counter() - t0

    def _reader() -> float:
        t0 = time.perf_counter()
        for _ in range(ops_per_thread):
            _ = breaker.window_failures
        return time.perf_counter() - t0

    wall_start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=n_writers + n_readers) as pool:
        w_futures = [pool.submit(_writer) for _ in range(n_writers)]
        r_futures = [pool.submit(_reader) for _ in range(n_readers)]
        for f in as_completed(w_futures):
            writer_times.append(f.result())
        for f in as_completed(r_futures):
            reader_times.append(f.result())
    wall_elapsed = time.perf_counter() - wall_start

    total_ops = (n_writers + n_readers) * ops_per_thread
    return {
        "test": "concurrent_mixed_read_write",
        "writers": n_writers,
        "readers": n_readers,
        "ops_per_thread": ops_per_thread,
        "total_ops": total_ops,
        "wall_time_s": round(wall_elapsed, 4),
        "throughput_ops_s": round(total_ops / wall_elapsed),
        "mean_writer_time_s": round(statistics.mean(writer_times), 4),
        "mean_reader_time_s": round(statistics.mean(reader_times), 4),
        "deque_len": len(breaker._events),
    }


def bench_prune_under_expiry_pressure(
    n_threads: int = 8,
    ops_per_thread: int = 2_000,
    window_s: float = 0.001,  # 1ms window — forces aggressive pruning
) -> dict:
    """Extreme pruning: 1ms window forces every call to prune nearly all events.

    This is the worst-case scenario for _prune_window — the deque fills,
    then every subsequent call must popleft through stale events.
    """
    breaker = _make_breaker(window_s=window_s, threshold=999_999)
    thread_times: list[float] = []
    total_ops = n_threads * ops_per_thread

    def _worker() -> float:
        t0 = time.perf_counter()
        for _ in range(ops_per_thread):
            breaker.record_failure()
            # Small yield to let events age past the 1ms window
        return time.perf_counter() - t0

    wall_start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=n_threads) as pool:
        futures = [pool.submit(_worker) for _ in range(n_threads)]
        for f in as_completed(futures):
            thread_times.append(f.result())
    wall_elapsed = time.perf_counter() - wall_start

    return {
        "test": "prune_under_expiry_pressure",
        "threads": n_threads,
        "ops_per_thread": ops_per_thread,
        "total_ops": total_ops,
        "wall_time_s": round(wall_elapsed, 4),
        "throughput_ops_s": round(total_ops / wall_elapsed),
        "window_s": window_s,
        "deque_len_final": len(breaker._events),
        "max_thread_time_s": round(max(thread_times), 4),
    }


def bench_allow_request_contention(
    n_threads: int = 8,
    ops_per_thread: int = 10_000,
) -> dict:
    """Pure allow_request() hot path contention — no state mutation.

    Measures the overhead of lock acquisition + _maybe_transition_to_half_open
    on the CLOSED fast path, which is the most frequent production call.
    """
    breaker = _make_breaker()
    total_ops = n_threads * ops_per_thread
    thread_times: list[float] = []

    def _worker() -> float:
        t0 = time.perf_counter()
        for _ in range(ops_per_thread):
            breaker.allow_request()
        return time.perf_counter() - t0

    wall_start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=n_threads) as pool:
        futures = [pool.submit(_worker) for _ in range(n_threads)]
        for f in as_completed(futures):
            thread_times.append(f.result())
    wall_elapsed = time.perf_counter() - wall_start

    return {
        "test": "allow_request_contention",
        "threads": n_threads,
        "ops_per_thread": ops_per_thread,
        "total_ops": total_ops,
        "wall_time_s": round(wall_elapsed, 4),
        "throughput_ops_s": round(total_ops / wall_elapsed),
        "mean_thread_time_s": round(statistics.mean(thread_times), 4),
    }


def main() -> None:
    """Run all benchmarks and print results."""
    print("=" * 72)
    print("Circuit Breaker _prune_window — Concurrent ThreadPoolExecutor Profiler")
    print("=" * 72)

    benchmarks = [
        bench_concurrent_record_failure,
        bench_concurrent_mixed_read_write,
        bench_prune_under_expiry_pressure,
        bench_allow_request_contention,
    ]

    for bench_fn in benchmarks:
        print(f"\n{'─' * 60}")
        result = bench_fn()
        print(f"  {result['test']}")
        print(f"{'─' * 60}")
        for k, v in result.items():
            if k == "test":
                continue
            label = k.replace("_", " ").title()
            print(f"  {label:30s} : {v}")

    print(f"\n{'=' * 72}")
    print("All benchmarks complete.")
    print("=" * 72)


if __name__ == "__main__":
    main()
