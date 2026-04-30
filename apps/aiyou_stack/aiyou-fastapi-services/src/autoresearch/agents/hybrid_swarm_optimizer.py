import numpy as np

# Patch for scikit-opt compatibility with newer NumPy
if not hasattr(np, "int"):
    int = int

from typing import Any

from sko.ACA import ACA_TSP
from sko.PSO import PSO


class HybridSwarmOptimizer:
    """Hybrid Swarm Optimizer: PSO + ACO Cascade.

    Phase 1: PSO (Particle Swarm Optimization)
    - Allocates tasks to agents to minimize load variance and cost.

    Phase 2: ACO (Ant Colony Optimization)
    - Optimizes the routing/handoff sequence between the allocated squads.

    Target: 15-25% latency drop on multi-hop workflows.
    """

    def __init__(self, num_agents: int, num_tasks: int, num_squads: int):
        self.num_agents = num_agents
        self.num_tasks = num_tasks
        self.num_squads = num_squads

        # Mock Data for Simulation
        self.agent_latency = np.random.uniform(1.0, 5.0, num_agents)
        self.agent_cost = np.random.uniform(0.0001, 0.001, num_agents)
        self.handoff_latency = np.random.uniform(0.1, 2.0, (num_squads, num_squads))
        np.fill_diagonal(self.handoff_latency, 0)

    # --- Phase 1: PSO Task Allocation ---
    def _pso_objective(self, allocation: np.ndarray) -> float:
        allocation = allocation.astype(int)
        total_latency = sum(self.agent_latency[allocation[i]] for i in range(self.num_tasks))
        total_cost = sum(self.agent_cost[allocation[i]] for i in range(self.num_tasks))
        agent_load = np.bincount(allocation, minlength=self.num_agents)
        load_variance = np.var(agent_load)
        return total_latency + 100 * total_cost + 0.1 * load_variance

    def run_pso_allocation(self, max_iter: int = 50) -> dict[str, Any]:
        pso = PSO(
            func=self._pso_objective,
            n_dim=self.num_tasks,
            pop=40,
            max_iter=max_iter,
            lb=[0] * self.num_tasks,
            ub=[self.num_agents - 1] * self.num_tasks,
            w=0.8,
            c1=0.5,
            c2=0.5,
        )
        pso.run()
        return {"allocation": pso.gbest_x.astype(int), "cost": pso.gbest_y}

    # --- Phase 2: ACO Routing Optimization ---
    def _aco_distance_callback(self, route: np.ndarray, required_squads: list[int]) -> float:
        total = 0
        # Map route indices back to actual squad IDs
        actual_route = [required_squads[i] for i in route]
        for i in range(len(actual_route) - 1):
            total += self.handoff_latency[actual_route[i], actual_route[i + 1]]
        return total

    def run_aco_routing(self, required_squads: list[int], max_iter: int = 50) -> dict[str, Any]:
        n = len(required_squads)
        if n < 2:
            return {"route": required_squads, "latency": 0.0}

        # Build sub-matrix for ACO
        distance_matrix = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                distance_matrix[i, j] = self.handoff_latency[required_squads[i], required_squads[j]]

        def aco_func(route):
            # ACO passes a permutation of 0..n-1
            total = 0
            for i in range(len(route) - 1):
                total += distance_matrix[route[i], route[i + 1]]
            return total

        aca = ACA_TSP(
            func=aco_func,
            n_dim=n,
            size_pop=20,
            max_iter=max_iter,
            distance_matrix=distance_matrix,
        )
        best_route_indices, best_latency = aca.run()

        # Map back to squad IDs
        best_route = [required_squads[i] for i in best_route_indices]
        return {"route": best_route, "latency": best_latency}

    # --- Main Optimization Pipeline ---
    def optimize_mission(self) -> dict[str, Any]:
        print("///▞ HYBRID SWARM :: Initiating Optimization Cascade...")

        # Phase 1: PSO
        print("Phase 1: PSO Task Allocation...")
        pso_result = self.run_pso_allocation()
        allocation = pso_result["allocation"]

        # Derive required squads from allocation (Mock mapping: Agent ID % Num Squads)
        required_squads = list(set([agent_id % self.num_squads for agent_id in allocation]))
        print(f"Phase 1 Complete. Identified {len(required_squads)} active squads.")

        # Phase 2: ACO
        print("Phase 2: ACO Routing Optimization...")
        aco_result = self.run_aco_routing(required_squads)

        return {
            "task_allocation": allocation.tolist(),
            "optimal_route": aco_result["route"],
            "estimated_cost": pso_result["cost"],
            "handoff_latency": aco_result["latency"],
        }


if __name__ == "__main__":
    # Test Run
    optimizer = HybridSwarmOptimizer(num_agents=600, num_tasks=100, num_squads=24)
    result = optimizer.optimize_mission()
    print("\n///▞ OPTIMIZATION COMPLETE")
    print(f"Optimal Route: {result['optimal_route']}")
    print(f"Est. Latency: {result['handoff_latency']:.4f}s")
