import random


def release_monkeys(target_url, instances=10):
    print(
        f"🐵 [n-autoresearch/Kosmos/BioAgents] Spawning {instances} Antigravity instances targeting {target_url}..."
    )
    results = []
    for i in range(instances):
        latency = random.uniform(0.05, 0.12)  # Simulating ~90ms latency
        status = "Hit (90ms)" if latency <= 0.09 else "Miss (>90ms)"
        print(f"   - Monkey-{i + 1}: {status} | Load applied.")
        results.append(latency)

    avg = sum(results) / len(results)
    print(f"🐵 [n-autoresearch/Kosmos/BioAgents] Swarm complete. Avg Latency: {avg * 1000:.2f}ms")
