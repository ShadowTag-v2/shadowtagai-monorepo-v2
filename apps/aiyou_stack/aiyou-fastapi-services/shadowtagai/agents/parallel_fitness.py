#!/usr/bin/env python3
"""Parallel Fitness Evaluator for 600-agent Flying n-autoresearch/Kosmos/BioAgents swarm.
Uses multiprocessing with shared memory for 4-10x speedup.
Based on patterns from yyz-agentics-june/performance_optimization/src/parallel_optimized.py
"""

import time
from collections.abc import Callable
from dataclasses import dataclass
from multiprocessing import Pool, cpu_count, shared_memory

import numpy as np


@dataclass
class BatchResult:
    """Result from a batch fitness evaluation."""

    batch_id: int
    fitness_values: list[float]
    latencies_ms: list[float]


class ParallelFitnessEvaluator:
    """Parallel fitness evaluation for swarm optimization.

    Uses multiprocessing pools with shared memory to evaluate
    fitness of 600 agents in parallel batches.

    Target: 4-10x speedup over sequential evaluation.
    """

    def __init__(
        self, num_workers: int = None, batch_size: int = 25, use_shared_memory: bool = True,
    ):
        """Initialize parallel evaluator.

        Args:
            num_workers: Number of worker processes (default: CPU count)
            batch_size: Agents per batch (default: 25 = one squad)
            use_shared_memory: Use shared memory for large arrays

        """
        self.num_workers = num_workers or cpu_count()
        self.batch_size = batch_size
        self.use_shared_memory = use_shared_memory
        self._shared_mem = None

    def evaluate_batch(
        self, positions: np.ndarray, fitness_fn: Callable[[np.ndarray], float],
    ) -> list[float]:
        """Evaluate fitness for a batch of positions in parallel.

        Args:
            positions: Array of shape (num_particles, dim)
            fitness_fn: Fitness function taking position array

        Returns:
            List of fitness values

        """
        num_particles = len(positions)

        if num_particles <= self.batch_size:
            # Sequential for small batches
            return [fitness_fn(pos) for pos in positions]

        # Split into batches
        num_batches = (num_particles + self.batch_size - 1) // self.batch_size
        batches = np.array_split(positions, num_batches)

        # Parallel evaluation
        with Pool(processes=self.num_workers) as pool:
            results = pool.starmap(
                _evaluate_batch_worker, [(batch, fitness_fn) for batch in batches],
            )

        # Flatten results
        return [val for batch_result in results for val in batch_result]

    def evaluate_swarm(
        self,
        swarm_positions: np.ndarray,
        fitness_fn: Callable[[np.ndarray], float],
        num_agents: int = 600,
    ) -> dict:
        """Evaluate entire 600-agent swarm in parallel.

        Args:
            swarm_positions: Array of shape (num_agents, dim)
            fitness_fn: Fitness function
            num_agents: Expected number of agents

        Returns:
            Dictionary with fitness values and timing metrics

        """
        start_time = time.time()

        # Create batches of 25 (one squad each)
        num_batches = (num_agents + self.batch_size - 1) // self.batch_size
        batches = np.array_split(swarm_positions, num_batches)

        # Prepare worker arguments
        args = [(i, batch, num_agents) for i, batch in enumerate(batches)]

        # Parallel evaluation
        with Pool(processes=self.num_workers) as pool:
            batch_results = pool.map(_swarm_worker, args)

        # Aggregate results
        fitness_values = []
        batch_latencies = []

        for result in batch_results:
            fitness_values.extend(result["fitness"])
            batch_latencies.append(result["latency_ms"])

        total_time = (time.time() - start_time) * 1000

        return {
            "fitness_values": fitness_values,
            "total_time_ms": total_time,
            "batch_latencies_ms": batch_latencies,
            "metrics": {
                "num_agents": num_agents,
                "num_batches": num_batches,
                "num_workers": self.num_workers,
                "avg_batch_latency_ms": np.mean(batch_latencies),
                "speedup_estimate": num_agents / (total_time / 1000) if total_time > 0 else 0,
            },
        }

    def evaluate_with_shared_memory(
        self, positions: np.ndarray, agent_states: np.ndarray, fitness_fn_name: str,
    ) -> list[float]:
        """Evaluate using shared memory for large state arrays.

        Avoids copying large arrays to each worker process.

        Args:
            positions: Particle positions
            agent_states: Large array of agent states (shared)
            fitness_fn_name: Name of fitness function to use

        Returns:
            List of fitness values

        """
        # Create shared memory
        shm = shared_memory.SharedMemory(create=True, size=agent_states.nbytes)
        shared_array = np.ndarray(agent_states.shape, dtype=agent_states.dtype, buffer=shm.buf)
        shared_array[:] = agent_states[:]

        try:
            # Split positions into batches
            num_batches = (len(positions) + self.batch_size - 1) // self.batch_size
            batches = np.array_split(positions, num_batches)

            # Worker arguments with shared memory name
            args = [
                (batch, shm.name, agent_states.shape, agent_states.dtype, fitness_fn_name)
                for batch in batches
            ]

            # Parallel evaluation
            with Pool(processes=self.num_workers) as pool:
                results = pool.map(_shared_memory_worker, args)

            return [val for batch_result in results for val in batch_result]

        finally:
            shm.close()
            shm.unlink()

    def benchmark(self, num_agents: int = 600, dim: int = 100, iterations: int = 10) -> dict:
        """Benchmark parallel vs sequential evaluation.

        Returns:
            Dictionary with timing comparison

        """
        # Generate test data
        positions = np.random.uniform(0, 599, (num_agents, dim))

        def test_fitness(pos):
            # Simulate computation
            return np.sum(pos**2) + np.random.random() * 10

        # Sequential benchmark
        seq_start = time.time()
        for _ in range(iterations):
            _ = [test_fitness(pos) for pos in positions]
        seq_time = (time.time() - seq_start) * 1000

        # Parallel benchmark
        par_start = time.time()
        for _ in range(iterations):
            _ = self.evaluate_batch(positions, test_fitness)
        par_time = (time.time() - par_start) * 1000

        speedup = seq_time / par_time if par_time > 0 else 0

        return {
            "sequential_ms": seq_time,
            "parallel_ms": par_time,
            "speedup": speedup,
            "num_workers": self.num_workers,
            "batch_size": self.batch_size,
            "iterations": iterations,
        }


def _evaluate_batch_worker(batch: np.ndarray, fitness_fn: Callable) -> list[float]:
    """Worker function for batch evaluation."""
    return [fitness_fn(pos) for pos in batch]


def _swarm_worker(args: tuple[int, np.ndarray, int]) -> dict:
    """Worker function for swarm evaluation."""
    batch_id, batch, num_agents = args
    start = time.time()

    # Simulate fitness evaluation with agent properties
    fitness_values = []
    for pos in batch:
        allocation = pos.astype(int)
        load_counts = np.bincount(allocation, minlength=num_agents)

        # Fitness components
        latency = np.sum(np.random.uniform(10, 100, len(allocation)))
        cost = np.sum(allocation % 3 + 1)
        variance = np.var(load_counts) * 10
        overload = np.sum(np.maximum(load_counts - 10, 0)) * 100

        fitness_values.append(latency + cost + variance + overload)

    latency_ms = (time.time() - start) * 1000

    return {"batch_id": batch_id, "fitness": fitness_values, "latency_ms": latency_ms}


def _shared_memory_worker(args: tuple) -> list[float]:
    """Worker function using shared memory."""
    batch, shm_name, shape, dtype, fitness_fn_name = args

    # Attach to shared memory
    existing_shm = shared_memory.SharedMemory(name=shm_name)
    agent_states = np.ndarray(shape, dtype=dtype, buffer=existing_shm.buf)

    try:
        fitness_values = []
        for pos in batch:
            allocation = pos.astype(int)

            # Use shared agent states for evaluation
            selected_states = agent_states[allocation % len(agent_states)]
            fitness = np.sum(selected_states) + np.var(allocation)

            fitness_values.append(fitness)

        return fitness_values

    finally:
        existing_shm.close()


def main():
    """CLI interface for parallel fitness evaluator."""
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Parallel Fitness Evaluator")
    parser.add_argument("--agents", type=int, default=600, help="Number of agents")
    parser.add_argument("--tasks", type=int, default=100, help="Number of tasks")
    parser.add_argument("--workers", type=int, help="Number of workers")
    parser.add_argument("--batch", type=int, default=25, help="Batch size")
    parser.add_argument("--benchmark", action="store_true", help="Run benchmark")
    parser.add_argument("--output", help="Output JSON file")

    args = parser.parse_args()

    evaluator = ParallelFitnessEvaluator(num_workers=args.workers, batch_size=args.batch)

    if args.benchmark:
        print("///▞ Running parallel vs sequential benchmark...")
        result = evaluator.benchmark(num_agents=args.agents, dim=args.tasks, iterations=10)
        print("///▞ Benchmark results:")
        print(f"    Sequential: {result['sequential_ms']:.2f}ms")
        print(f"    Parallel: {result['parallel_ms']:.2f}ms")
        print(f"    Speedup: {result['speedup']:.2f}x")
        print(f"    Workers: {result['num_workers']}")

    else:
        print(f"///▞ Evaluating {args.agents} agents with {args.workers or cpu_count()} workers")
        positions = np.random.uniform(0, 599, (args.agents, args.tasks))
        result = evaluator.evaluate_swarm(positions, None, args.agents)

        print("///▞ Evaluation complete:")
        print(f"    Total time: {result['total_time_ms']:.2f}ms")
        print(f"    Batches: {result['metrics']['num_batches']}")
        print(f"    Avg batch latency: {result['metrics']['avg_batch_latency_ms']:.2f}ms")

    if args.output:
        with open(args.output, "w") as f:
            # Convert numpy arrays to lists for JSON
            if isinstance(result.get("fitness_values"), np.ndarray):
                result["fitness_values"] = result["fitness_values"].tolist()
            json.dump(result, f, indent=2)
        print(f"///▞ Results saved to: {args.output}")


if __name__ == "__main__":
    main()
