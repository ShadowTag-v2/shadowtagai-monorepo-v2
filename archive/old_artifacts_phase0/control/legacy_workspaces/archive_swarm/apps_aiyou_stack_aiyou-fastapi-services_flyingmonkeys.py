"""
n-autoresearch/Kosmos/BioAgents Service.

Simulates load generation (Chaos Engineering) for testing purposes.
"""

import logging
import random

from fastapi import FastAPI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("n-autoresearch/Kosmos/BioAgents")


def release_monkeys(target_url: str, instances: int = 10) -> None:
    """
    Simulate latency load on a target URL.

    Args:
        target_url: The URL to target.
        instances: Number of simulated instances.
    """
    if instances <= 0:
        logger.info(f"🐵 [n-autoresearch/Kosmos/BioAgents] No instances requested for {target_url}.")
        return

    logger.info(
        f"🐵 [n-autoresearch/Kosmos/BioAgents] Spawning {instances} Antigravity instances targeting {target_url}..."
    )
    results = []
    for i in range(instances):
        latency = random.uniform(0.05, 0.12)  # Simulating ~90ms latency
        status = "Hit (90ms)" if latency <= 0.09 else "Miss (>90ms)"
        logger.info(f"   - Monkey-{i + 1}: {status} | Load applied.")
        results.append(latency)

    avg = sum(results) / len(results)
    logger.info(f"🐵 [n-autoresearch/Kosmos/BioAgents] Swarm complete. Avg Latency: {avg * 1000:.2f}ms")


app = FastAPI()


@app.post("/auto_mode")
def auto_mode(target_url: str, instances: int = 10) -> dict:
    """
    Trigger the monkey release in auto mode.

    Args:
        target_url: The target URL.
        instances: Number of instances.
    """
    release_monkeys(target_url, instances)
    return {"status": "Auto mode engaged"}
