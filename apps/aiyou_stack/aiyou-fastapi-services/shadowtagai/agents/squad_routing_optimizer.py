#!/usr/bin/env python3
"""Squad Routing Optimizer using Ant Colony Optimization.
Routes tasks through 24 squads (groups of 25 agents) to minimize handoff latency.
Based on FM 5-0 MDMP Step 4: COA Analysis (Wargaming).
"""

from dataclasses import dataclass

import numpy as np

# Patch numpy for scikit-opt compatibility with NumPy 2.x
if not hasattr(np, "int"):
    int = int
if not hasattr(np, "float"):
    float = float

try:
    from sko.ACA import ACA_TSP
except ImportError:
    ACA_TSP = None


@dataclass
class Squad:
    """A squad of 25 Flying n-autoresearch/Kosmos/BioAgents agents."""

    squad_id: int
    name: str
    specialty: str
    agents: list[int]  # Agent IDs in this squad
    avg_latency_ms: float
    current_load: int
    max_capacity: int


class SquadRoutingOptimizer:
    """ACO-based squad routing for Flying n-autoresearch/Kosmos/BioAgents swarm.

    Uses Ant Colony Optimization to find optimal routing through
    multiple squads for complex multi-stage tasks.

    Pheromone trails represent successful handoff history.
    """

    # Default squad configuration (24 squads × 25 agents = 600)
    SQUAD_SPECIALTIES = [
        "SECURITY",
        "BACKEND",
        "FRONTEND",
        "DEVOPS",
        "DATABASE",
        "ML_OPS",
        "TESTING",
        "DOCS",
        "ANALYTICS",
        "INFRA",
        "API",
        "AUTH",
        "CACHE",
        "QUEUE",
        "STORAGE",
        "MONITOR",
        "ALERT",
        "DEPLOY",
        "ROLLBACK",
        "SCALE",
        "MIGRATE",
        "BACKUP",
        "AUDIT",
        "COMPLIANCE",
    ]

    def __init__(self, num_squads: int = 24):
        self.num_squads = num_squads
        self.squads = self._init_squads()
        self.distance_matrix = self._compute_latency_matrix()

    def _init_squads(self) -> list[Squad]:
        """Initialize 24 squads with default configurations."""
        squads = []
        for i in range(self.num_squads):
            specialty = (
                self.SQUAD_SPECIALTIES[i] if i < len(self.SQUAD_SPECIALTIES) else f"SQUAD_{i}"
            )
            squads.append(
                Squad(
                    squad_id=i,
                    name=f"Squad-{i:02d}",
                    specialty=specialty,
                    agents=list(range(i * 25, (i + 1) * 25)),
                    avg_latency_ms=np.random.uniform(50, 200),
                    current_load=np.random.randint(0, 20),
                    max_capacity=25,
                ),
            )
        return squads

    def _compute_latency_matrix(self) -> np.ndarray:
        """Compute handoff latency matrix between squads.

        Latency depends on:
        - Physical network distance (simulated)
        - Current load of target squad
        - Specialty compatibility
        """
        matrix = np.zeros((self.num_squads, self.num_squads))

        for i in range(self.num_squads):
            for j in range(self.num_squads):
                if i == j:
                    matrix[i][j] = 0
                else:
                    # Base latency
                    base = np.random.uniform(0.1, 0.5)

                    # Load factor (higher load = higher latency)
                    load_factor = 1 + (self.squads[j].current_load / self.squads[j].max_capacity)

                    # Specialty compatibility (related squads have lower latency)
                    specialty_factor = 1.0
                    related_pairs = [
                        ("SECURITY", "AUTH"),
                        ("BACKEND", "API"),
                        ("DATABASE", "CACHE"),
                        ("DEVOPS", "DEPLOY"),
                        ("TESTING", "COMPLIANCE"),
                        ("ML_OPS", "ANALYTICS"),
                    ]
                    src_spec = self.squads[i].specialty
                    dst_spec = self.squads[j].specialty
                    for a, b in related_pairs:
                        if (src_spec == a and dst_spec == b) or (src_spec == b and dst_spec == a):
                            specialty_factor = 0.7  # 30% latency reduction
                            break

                    matrix[i][j] = base * load_factor * specialty_factor

        return matrix

    def optimize(
        self,
        required_squads: list[int] = None,
        max_iter: int = 200,
        num_ants: int = 30,
        alpha: float = 1.0,
        beta: float = 2.0,
        rho: float = 0.1,
    ) -> dict:
        """Run ACO optimization for squad routing.

        Args:
            required_squads: List of squad IDs that must be visited (in any order)
            max_iter: Maximum iterations
            num_ants: Number of ants
            alpha: Pheromone importance
            beta: Heuristic importance
            rho: Pheromone evaporation rate

        Returns:
            Dictionary with routing results

        """
        if ACA_TSP is None:
            raise ImportError("scikit-opt not installed: pip install scikit-opt")

        # Default: route through 5 random squads
        if required_squads is None:
            required_squads = np.random.choice(
                self.num_squads, size=min(5, self.num_squads), replace=False,
            ).tolist()

        num_points = len(required_squads)

        if num_points < 2:
            return {
                "route": required_squads,
                "total_latency": 0,
                "convergence_history": [],
                "squad_names": [self.squads[i].specialty for i in required_squads],
            }

        # Build sub-matrix for required squads only
        sub_matrix = np.zeros((num_points, num_points))
        for i in range(num_points):
            for j in range(num_points):
                sub_matrix[i][j] = self.distance_matrix[required_squads[i]][required_squads[j]]

        # ACO setup
        def distance_func(path):
            """Calculate total distance of a path."""
            total = 0
            for i in range(len(path) - 1):
                total += sub_matrix[int(path[i])][int(path[i + 1])]
            return total

        aca = ACA_TSP(
            func=distance_func,
            n_dim=num_points,
            size_pop=num_ants,
            max_iter=max_iter,
            distance_matrix=sub_matrix,
            alpha=alpha,
            beta=beta,
            rho=rho,
        )

        # Run optimization
        best_path, best_distance = aca.run()

        # Map back to original squad IDs
        route = [required_squads[int(i)] for i in best_path]

        return {
            "route": route,
            "total_latency": float(best_distance),
            "convergence_history": (
                aca.y_best_history.tolist()
                if hasattr(aca.y_best_history, "tolist")
                else list(aca.y_best_history)
            )
            if hasattr(aca, "y_best_history")
            else [],
            "squad_names": [self.squads[i].specialty for i in route],
            "metrics": {
                "num_squads": num_points,
                "avg_latency_per_hop": float(best_distance / max(num_points - 1, 1)),
                "total_hops": num_points - 1,
            },
        }

    def get_squad_by_specialty(self, specialty: str) -> int | None:
        """Get squad ID by specialty name."""
        for squad in self.squads:
            if squad.specialty == specialty:
                return squad.squad_id
        return None

    def plan_route(self, specialties: list[str], **kwargs) -> dict:
        """Plan route by specialty names instead of IDs.

        Args:
            specialties: List of specialty names (e.g., ["SECURITY", "BACKEND", "DEPLOY"])
            **kwargs: Additional arguments for optimize()

        Returns:
            Routing results

        """
        squad_ids = []
        for spec in specialties:
            sid = self.get_squad_by_specialty(spec)
            if sid is not None:
                squad_ids.append(sid)
            else:
                raise ValueError(f"Unknown specialty: {spec}")

        return self.optimize(required_squads=squad_ids, **kwargs)


def main():
    """CLI interface for squad routing optimizer."""
    import argparse
    import json

    parser = argparse.ArgumentParser(description="ACO Squad Routing Optimizer")
    parser.add_argument("--squads", type=int, default=24, help="Number of squads")
    parser.add_argument("--route", nargs="+", help="Required squad specialties")
    parser.add_argument("--iter", type=int, default=200, help="Max iterations")
    parser.add_argument("--output", help="Output JSON file")

    args = parser.parse_args()

    print(f"///▞ Initializing ACO optimizer: {args.squads} squads")

    optimizer = SquadRoutingOptimizer(num_squads=args.squads)

    if args.route:
        print(f"///▞ Planning route through: {' → '.join(args.route)}")
        result = optimizer.plan_route(args.route, max_iter=args.iter)
    else:
        # Default: random 5 squads
        print(f"///▞ Running ACO optimization (max_iter={args.iter})...")
        result = optimizer.optimize(max_iter=args.iter)

    print("///▞ Optimization complete:")
    print(f"    Route: {' → '.join(result['squad_names'])}")
    print(f"    Total latency: {result['total_latency']:.3f}")
    print(f"    Avg latency/hop: {result['metrics']['avg_latency_per_hop']:.3f}")

    if args.output:
        with open(args.output, "w") as f:
            json.dump(result, f, indent=2)
        print(f"///▞ Results saved to: {args.output}")


if __name__ == "__main__":
    main()
