#!/usr/bin/env python3
"""Task Allocation Optimizer using Particle Swarm Optimization.
Allocates N tasks to 600 Flying n-autoresearch/Kosmos/BioAgents agents minimizing latency + cost + load variance.
Based on FM 5-0 MDMP Step 3: COA Development.
"""

from dataclasses import dataclass
from datetime import datetime

import numpy as np

try:
    from sko.PSO import PSO
except ImportError:
    PSO = None


@dataclass
class AgentState:
    """Current state of a Flying Monkey agent."""

    agent_id: int
    tier: str  # FREE, FLASH, PRO
    current_load: int
    latency_ms: float
    shift_end: datetime
    available: bool


@dataclass
class Task:
    """Task to be allocated."""

    task_id: int
    complexity: float  # 0.0 to 1.0
    required_tier: str  # Minimum tier required
    deadline_ms: float


class TaskAllocationOptimizer:
    """PSO-based task allocation for 600-agent Flying n-autoresearch/Kosmos/BioAgents swarm.

    Objective function minimizes:
    - Total latency across all tasks
    - Cost (tier-weighted)
    - Load variance across agents

    Constraints:
    - Agent must meet task's required tier
    - Agent must be available (shift not ended)
    - Agent load must not exceed capacity
    """

    # Tier costs (relative)
    TIER_COSTS = {"FREE": 1.0, "FLASH": 5.0, "PRO": 25.0}

    # Tier capabilities (higher can do lower)
    TIER_LEVELS = {"FREE": 0, "FLASH": 1, "PRO": 2}

    def __init__(self, num_agents: int = 600, num_tasks: int = 100, max_load_per_agent: int = 10):
        self.num_agents = num_agents
        self.num_tasks = num_tasks
        self.max_load = max_load_per_agent

        # Initialize agent states (will be loaded from Redis in production)
        self.agents = self._init_agents()
        self.tasks: list[Task] = []

    def _init_agents(self) -> list[AgentState]:
        """Initialize 600 agents with default states."""
        agents = []
        for i in range(self.num_agents):
            # Distribute tiers: 70% FREE, 20% FLASH, 10% PRO
            if i < 420:
                tier = "FREE"
            elif i < 540:
                tier = "FLASH"
            else:
                tier = "PRO"

            agents.append(
                AgentState(
                    agent_id=i,
                    tier=tier,
                    current_load=0,
                    latency_ms=np.random.uniform(10, 100),  # Simulated
                    shift_end=datetime.now(),  # Will be set properly
                    available=True,
                ),
            )
        return agents

    def set_tasks(self, tasks: list[Task]):
        """Set tasks to be allocated."""
        self.tasks = tasks
        self.num_tasks = len(tasks)

    def _objective_function(self, x: np.ndarray) -> float:
        """PSO objective function to minimize.

        Args:
            x: Array of shape (num_tasks,) with values in [0, num_agents)
               Each value is the agent ID assigned to that task.

        Returns:
            Total cost = latency + tier_cost + load_variance + penalties

        """
        # Convert continuous values to agent indices
        allocation = np.clip(x.astype(int), 0, self.num_agents - 1)

        total_latency = 0.0
        total_cost = 0.0
        load_counts = np.zeros(self.num_agents)
        penalties = 0.0

        for task_idx, agent_idx in enumerate(allocation):
            agent = self.agents[agent_idx]
            task = self.tasks[task_idx] if task_idx < len(self.tasks) else None

            # Latency component
            total_latency += agent.latency_ms

            # Cost component (tier-weighted)
            total_cost += self.TIER_COSTS[agent.tier]

            # Load tracking
            load_counts[agent_idx] += 1

            # Penalty: Agent can't handle task's required tier
            if task:
                agent_level = self.TIER_LEVELS[agent.tier]
                required_level = self.TIER_LEVELS.get(task.required_tier, 0)
                if agent_level < required_level:
                    penalties += 1000  # Heavy penalty

            # Penalty: Agent unavailable
            if not agent.available:
                penalties += 500

        # Load variance penalty (encourage even distribution)
        load_variance = np.var(load_counts) * 10

        # Overload penalty
        overload_penalty = np.sum(np.maximum(load_counts - self.max_load, 0)) * 100

        return total_latency + total_cost + load_variance + overload_penalty + penalties

    def optimize(
        self,
        max_iter: int = 150,
        pop_size: int = 50,
        w: float = 0.8,
        c1: float = 0.5,
        c2: float = 0.5,
    ) -> dict:
        """Run PSO optimization for task allocation.

        Args:
            max_iter: Maximum iterations
            pop_size: Population size (particles)
            w: Inertia weight
            c1: Cognitive parameter
            c2: Social parameter

        Returns:
            Dictionary with allocation results

        """
        if PSO is None:
            raise ImportError("scikit-opt not installed: pip install scikit-opt")

        if not self.tasks:
            # Generate dummy tasks for testing
            self.tasks = [
                Task(
                    task_id=i,
                    complexity=np.random.random(),
                    required_tier=np.random.choice(["FREE", "FLASH", "PRO"], p=[0.7, 0.2, 0.1]),
                    deadline_ms=np.random.uniform(100, 5000),
                )
                for i in range(self.num_tasks)
            ]

        # PSO setup
        pso = PSO(
            func=self._objective_function,
            n_dim=self.num_tasks,
            pop=pop_size,
            max_iter=max_iter,
            lb=[0] * self.num_tasks,
            ub=[self.num_agents - 1] * self.num_tasks,
            w=w,
            c1=c1,
            c2=c2,
        )

        # Run optimization
        pso.run()

        # Extract results
        best_allocation = pso.gbest_x.astype(int)
        best_cost = pso.gbest_y

        # Compute metrics
        load_distribution = np.bincount(best_allocation, minlength=self.num_agents)

        # Handle NumPy 2.x scalar conversion
        cost_val = best_cost[0] if hasattr(best_cost, "__len__") else best_cost

        # Handle convergence history
        hist = pso.gbest_y_hist if hasattr(pso, "gbest_y_hist") else []
        if hasattr(hist, "tolist"):
            hist = hist.tolist()

        return {
            "allocation": best_allocation.tolist(),
            "total_cost": float(cost_val),
            "convergence_history": hist,
            "metrics": {
                "mean_load": float(np.mean(load_distribution)),
                "max_load": int(np.max(load_distribution)),
                "load_variance": float(np.var(load_distribution)),
                "agents_used": int(np.sum(load_distribution > 0)),
                "utilization": float(np.sum(load_distribution > 0) / self.num_agents),
            },
        }

    def get_agent_assignments(self, allocation: list[int]) -> dict[int, list[int]]:
        """Convert allocation to agent-centric view.

        Args:
            allocation: List where allocation[task_id] = agent_id

        Returns:
            Dictionary mapping agent_id to list of task_ids

        """
        assignments = {}
        for task_id, agent_id in enumerate(allocation):
            if agent_id not in assignments:
                assignments[agent_id] = []
            assignments[agent_id].append(task_id)
        return assignments


def main():
    """CLI interface for task allocation optimizer."""
    import argparse
    import json

    parser = argparse.ArgumentParser(description="PSO Task Allocation Optimizer")
    parser.add_argument("--agents", type=int, default=600, help="Number of agents")
    parser.add_argument("--tasks", type=int, default=100, help="Number of tasks")
    parser.add_argument("--iter", type=int, default=150, help="Max iterations")
    parser.add_argument("--output", help="Output JSON file")

    args = parser.parse_args()

    print(f"///▞ Initializing PSO optimizer: {args.agents} agents, {args.tasks} tasks")

    optimizer = TaskAllocationOptimizer(num_agents=args.agents, num_tasks=args.tasks)

    print(f"///▞ Running PSO optimization (max_iter={args.iter})...")
    result = optimizer.optimize(max_iter=args.iter)

    print("///▞ Optimization complete:")
    print(f"    Total cost: {result['total_cost']:.2f}")
    print(f"    Agents used: {result['metrics']['agents_used']}/{args.agents}")
    print(f"    Utilization: {result['metrics']['utilization']:.1%}")
    print(f"    Max load: {result['metrics']['max_load']}")
    print(f"    Load variance: {result['metrics']['load_variance']:.2f}")

    if args.output:
        with open(args.output, "w") as f:
            json.dump(result, f, indent=2)
        print(f"///▞ Results saved to: {args.output}")
    else:
        print("\n///▞ Sample allocation (first 10 tasks):")
        for i in range(min(10, len(result["allocation"]))):
            print(f"    Task {i} → Agent {result['allocation'][i]}")


if __name__ == "__main__":
    main()
