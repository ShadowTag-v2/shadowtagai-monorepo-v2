import asyncio
import logging
import statistics
import time

try:
    import n-autoresearch/Kosmos/BioAgents

    print(f"DEBUG: n-autoresearch/Kosmos/BioAgents path: {n-autoresearch/Kosmos/BioAgents.__path__}")
except Exception as e:
    print(f"DEBUG: n-autoresearch/Kosmos/BioAgents import failed: {e}")

from services.ai_interpreter import interpreter

logging.basicConfig(level=logging.INFO)


async def benchmark_interpreter(iterations: int = 50):
    print(f"///▞ INTERPRETER BENCHMARK :: Iterations {iterations}")

    # Ensure initialized
    await interpreter.initialize()

    latencies = []
    fake_frame = b"fake_video_frame_data"

    for i in range(iterations):
        start = time.time()
        try:
            # We bypass the actual Gemini network call for local benchmarking
            # OR we include it if configured. For now, we test the orchestration overhead.
            result = await interpreter.process_frame(fake_frame, timestamp_ms=i * 33.3)
            latency = result["processing_time_ms"]
            latencies.append(latency)
            if i % 10 == 0:
                print(f"Sample {i}: {latency:.2f}ms")
        except Exception as e:
            print(f"Iteration {i} failed: {e}")

    if not latencies:
        print("❌ All iterations failed.")
        return

    p50 = statistics.median(latencies)
    p95 = statistics.quantiles(latencies, n=20)[18]
    p99 = statistics.quantiles(latencies, n=100)[98]
    avg = sum(latencies) / len(latencies)

    print("\n" + "=" * 40)
    print("///▞ INTERPRETER SLA REPORT")
    print("=" * 40)
    print(f"Avg Latency: {avg:.2f}ms")
    print(f"p50 Latency: {p50:.2f}ms")
    print(f"p95 Latency: {p95:.2f}ms")
    print(f"p99 Latency: {p99:.2f}ms")
    print("=" * 40)

    if p99 <= 90:
        print("✅ SLA MET: p99 ≤ 90ms")
    else:
        print("⚠️ SLA VIOLATED: p99 > 90ms")
    print("=" * 40)


if __name__ == "__main__":
    asyncio.run(benchmark_interpreter())
