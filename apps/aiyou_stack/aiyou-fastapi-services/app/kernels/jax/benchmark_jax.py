# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import time

from Claude_Code_6_jax import Claude_Code_6_enforce, init_mock_data


def benchmark(batch_size=1024, seq_len=256, iters=1000):
    print(f"Benchmarking JAX Judge 6 (Batch: {batch_size}, Seq: {seq_len})")

    # Initialize data
    input_ids, policy_matrix = init_mock_data(batch_size, seq_len)

    # Warmup (compilation)
    print("Compiling...")
    _ = Claude_Code_6_enforce(input_ids, policy_matrix).block_until_ready()

    # Measure
    print(f"Running {iters} iterations...")
    start = time.perf_counter()
    for _ in range(iters):
        _ = Claude_Code_6_enforce(input_ids, policy_matrix).block_until_ready()
    end = time.perf_counter()

    elapsed = end - start
    latency_ms = (elapsed / iters) * 1000
    throughput = (batch_size * iters) / elapsed

    print(f"Mean Latency: {latency_ms:.3f} ms")
    print(f"Throughput: {throughput:.0f} seq/sec")

    if latency_ms <= 12.0:
        print("✅ PASS: Latency <= 12ms")
    else:
        print("❌ FAIL: Latency > 12ms")


if __name__ == "__main__":
    benchmark()
