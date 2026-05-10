#!/usr/bin/env python3
"""Adaptive Particle Swarm Optimization with Adam-inspired momentum.
Combines PSO swarm intelligence with adaptive learning rates from Adam optimizer.
Based on patterns from yyz-agentics-june/neuralflow/core/optimizers/optimizers.py
"""

from collections.abc import Callable
from dataclasses import dataclass

import numpy as np


@dataclass
class Particle:
    """A particle in the swarm."""

    id: int
    position: np.ndarray
    velocity: np.ndarray
    best_position: np.ndarray
    best_fitness: float
    m: np.ndarray  # First moment (Adam)
    v: np.ndarray  # Second moment (Adam)


class AdaptivePSO:
    """Adaptive PSO optimizer combining swarm intelligence with Adam momentum.

    Key innovation: Uses Adam's m (velocity) and v (acceleration) terms
    to adaptively adjust PSO inertia and cognitive/social components.

    For 600-agent Flying n-autoresearch/Kosmos/BioAgents swarm task allocation.
    """

    def __init__(
        self,
        num_particles: int = 600,
        dim: int = 100,
        bounds: tuple = (0, 599),
        w: float = 0.7,
        c1: float = 1.5,
        c2: float = 1.5,
        beta1: float = 0.9,
        beta2: float = 0.999,
        epsilon: float = 1e-8,
    ):
        """Initialize Adaptive PSO.

        Args:
            num_particles: Number of particles (agents)
            dim: Dimensionality of search space (tasks)
            bounds: (min, max) bounds for positions
            w: Base inertia weight
            c1: Cognitive parameter (attraction to personal best)
            c2: Social parameter (attraction to global best)
            beta1: Adam first moment decay rate
            beta2: Adam second moment decay rate
            epsilon: Small constant for numerical stability

        """
        self.num_particles = num_particles
        self.dim = dim
        self.lb, self.ub = bounds
        self.w = w
        self.c1 = c1
        self.c2 = c2
        self.beta1 = beta1
        self.beta2 = beta2
        self.epsilon = epsilon

        # Initialize particles
        self.particles = self._init_particles()
        self.global_best_position = None
        self.global_best_fitness = float("inf")
        self.iteration = 0
        self.history = []

    def _init_particles(self) -> list[Particle]:
        """Initialize particle swarm."""
        particles = []
        for i in range(self.num_particles):
            position = np.random.uniform(self.lb, self.ub, self.dim)
            velocity = np.random.uniform(-1, 1, self.dim)
            particles.append(
                Particle(
                    id=i,
                    position=position.copy(),
                    velocity=velocity,
                    best_position=position.copy(),
                    best_fitness=float("inf"),
                    m=np.zeros(self.dim),  # First moment
                    v=np.zeros(self.dim),  # Second moment
                ),
            )
        return particles

    def _compute_adaptive_weights(self, particle: Particle, gradient: np.ndarray) -> tuple:
        """Compute adaptive weights using Adam-like momentum.

        Args:
            particle: The particle to update
            gradient: Gradient of fitness function (attraction direction)

        Returns:
            Tuple of (adaptive_inertia, adaptive_c1, adaptive_c2)

        """
        # Update biased first moment estimate
        particle.m = self.beta1 * particle.m + (1 - self.beta1) * gradient

        # Update biased second moment estimate
        particle.v = self.beta2 * particle.v + (1 - self.beta2) * (gradient**2)

        # Bias correction
        t = self.iteration + 1
        m_hat = particle.m / (1 - self.beta1**t)
        v_hat = particle.v / (1 - self.beta2**t)

        # Adaptive adjustment factor
        adjustment = m_hat / (np.sqrt(v_hat) + self.epsilon)

        # Scale inertia based on adjustment magnitude
        avg_adjustment = np.mean(np.abs(adjustment))
        adaptive_w = self.w * (1 - 0.5 * np.tanh(avg_adjustment))

        # Scale cognitive/social based on convergence
        adaptive_c1 = self.c1 * (1 + 0.3 * np.tanh(-avg_adjustment))
        adaptive_c2 = self.c2 * (1 + 0.3 * np.tanh(avg_adjustment))

        return adaptive_w, adaptive_c1, adaptive_c2

    def optimize(
        self,
        fitness_fn: Callable[[np.ndarray], float],
        max_iter: int = 200,
        early_stop: float = None,
        verbose: bool = False,
    ) -> dict:
        """Run adaptive PSO optimization.

        Args:
            fitness_fn: Function to minimize (takes position array, returns scalar)
            max_iter: Maximum iterations
            early_stop: Stop if fitness below this value
            verbose: Print progress

        Returns:
            Dictionary with optimization results

        """
        # Initial evaluation
        for particle in self.particles:
            fitness = fitness_fn(particle.position)
            particle.best_fitness = fitness
            particle.best_position = particle.position.copy()

            if fitness < self.global_best_fitness:
                self.global_best_fitness = fitness
                self.global_best_position = particle.position.copy()

        self.history.append(self.global_best_fitness)

        # Main optimization loop
        for iteration in range(max_iter):
            self.iteration = iteration

            for particle in self.particles:
                # Compute gradient (direction to best positions)
                cognitive_grad = particle.best_position - particle.position
                social_grad = self.global_best_position - particle.position
                gradient = cognitive_grad + social_grad

                # Get adaptive weights
                adaptive_w, adaptive_c1, adaptive_c2 = self._compute_adaptive_weights(
                    particle,
                    gradient,
                )

                # Random components
                r1 = np.random.random(self.dim)
                r2 = np.random.random(self.dim)

                # Update velocity with adaptive weights
                particle.velocity = (
                    adaptive_w * particle.velocity
                    + adaptive_c1 * r1 * cognitive_grad
                    + adaptive_c2 * r2 * social_grad
                )

                # Update position
                particle.position = particle.position + particle.velocity

                # Enforce bounds
                particle.position = np.clip(particle.position, self.lb, self.ub)

                # Evaluate fitness
                fitness = fitness_fn(particle.position)

                # Update personal best
                if fitness < particle.best_fitness:
                    particle.best_fitness = fitness
                    particle.best_position = particle.position.copy()

                    # Update global best
                    if fitness < self.global_best_fitness:
                        self.global_best_fitness = fitness
                        self.global_best_position = particle.position.copy()

            self.history.append(self.global_best_fitness)

            if verbose and iteration % 10 == 0:
                print(f"///▞ Iteration {iteration}: best fitness = {self.global_best_fitness:.4f}")

            # Early stopping
            if early_stop and self.global_best_fitness < early_stop:
                if verbose:
                    print(f"///▞ Early stop at iteration {iteration}")
                break

        return self._get_results()

    def _get_results(self) -> dict:
        """Get optimization results."""
        allocation = self.global_best_position.astype(int)
        load_distribution = np.bincount(allocation, minlength=600)

        return {
            "allocation": allocation.tolist(),
            "best_fitness": float(self.global_best_fitness),
            "convergence_history": self.history,
            "iterations": self.iteration + 1,
            "metrics": {
                "mean_load": float(np.mean(load_distribution)),
                "max_load": int(np.max(load_distribution)),
                "load_variance": float(np.var(load_distribution)),
                "agents_used": int(np.sum(load_distribution > 0)),
                "utilization": float(np.sum(load_distribution > 0) / 600),
            },
        }

    def get_particle_states(self) -> list[dict]:
        """Get current state of all particles."""
        return [
            {
                "id": p.id,
                "position": p.position.tolist(),
                "velocity": np.linalg.norm(p.velocity),
                "best_fitness": p.best_fitness,
                "m_norm": np.linalg.norm(p.m),
                "v_norm": np.linalg.norm(p.v),
            }
            for p in self.particles
        ]


def main():
    """CLI interface for Adaptive PSO."""
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Adaptive PSO Task Allocation")
    parser.add_argument("--particles", type=int, default=50, help="Number of particles")
    parser.add_argument("--tasks", type=int, default=100, help="Number of tasks")
    parser.add_argument("--iter", type=int, default=150, help="Max iterations")
    parser.add_argument("--output", help="Output JSON file")

    args = parser.parse_args()

    print(f"///▞ Initializing Adaptive PSO: {args.particles} particles, {args.tasks} tasks")

    optimizer = AdaptivePSO(num_particles=args.particles, dim=args.tasks, bounds=(0, 599))

    # Sample fitness function (minimize latency + cost + load variance)
    def fitness_fn(position):
        allocation = position.astype(int)
        load_counts = np.bincount(allocation, minlength=600)

        # Simulate costs
        latency = np.sum(np.random.uniform(10, 100, len(allocation)))
        cost = np.sum(allocation % 3 + 1)  # Tier-based
        variance = np.var(load_counts) * 10
        overload = np.sum(np.maximum(load_counts - 10, 0)) * 100

        return latency + cost + variance + overload

    print(f"///▞ Running Adaptive PSO (max_iter={args.iter})...")
    result = optimizer.optimize(fitness_fn, max_iter=args.iter, verbose=True)

    print("///▞ Optimization complete:")
    print(f"    Best fitness: {result['best_fitness']:.2f}")
    print(f"    Agents used: {result['metrics']['agents_used']}/600")
    print(f"    Utilization: {result['metrics']['utilization']:.1%}")
    print(f"    Max load: {result['metrics']['max_load']}")
    print(f"    Load variance: {result['metrics']['load_variance']:.2f}")

    if args.output:
        with open(args.output, "w") as f:
            json.dump(result, f, indent=2)
        print(f"///▞ Results saved to: {args.output}")


if __name__ == "__main__":
    main()
