"""PSO Swarm: Manages a population of particles for optimization.

Implements standard PSO with:
- Global best tracking
- Adaptive parameter control
- Early stopping on convergence
- Parallel fitness evaluation support
"""

import asyncio
from collections.abc import Callable
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from dataclasses import dataclass

import numpy as np

from .particle import Particle, ParticleState


@dataclass
class SwarmConfig:
    """Configuration for PSO swarm."""

    num_particles: int = 50
    dimensions: int = 100
    bounds: tuple[float, float] = (-1.0, 1.0)
    max_velocity: float = 1.0

    # PSO coefficients
    w_start: float = 0.9  # Initial inertia
    w_end: float = 0.4  # Final inertia
    c1: float = 1.5  # Cognitive coefficient
    c2: float = 1.5  # Social coefficient

    # Adam parameters
    beta1: float = 0.9
    beta2: float = 0.999

    # Convergence
    max_iterations: int = 100
    convergence_threshold: float = 1e-6
    stagnation_limit: int = 10  # Iterations without improvement


@dataclass
class OptimizationResult:
    """Result of PSO optimization."""

    best_position: np.ndarray
    best_fitness: float
    iterations: int
    converged: bool
    fitness_history: list[float]
    final_swarm_state: list[ParticleState]


class ParticleSwarm:
    """Particle Swarm Optimizer for neural network weights.

    Manages a population of particles exploring the weight space.
    Supports parallel fitness evaluation for large swarms.
    """

    def __init__(self, config: SwarmConfig | None = None, **kwargs):
        """Initialize swarm.

        Args:
            config: SwarmConfig instance, or pass individual params as kwargs

        """
        if config is None:
            config = SwarmConfig(**kwargs)
        self.config = config

        # Initialize particles
        self.particles: list[Particle] = []
        self._initialize_swarm()

        # Global best
        self.global_best: np.ndarray = None
        self.global_best_fitness: float = float("inf")

        # History
        self.fitness_history: list[float] = []
        self.iteration: int = 0
        self.stagnation_count: int = 0

    def _initialize_swarm(self) -> None:
        """Create initial particle population."""
        self.particles = [
            Particle.random(
                dimensions=self.config.dimensions,
                bounds=self.config.bounds,
                particle_id=i,
            )
            for i in range(self.config.num_particles)
        ]

    def _get_inertia(self) -> float:
        """Get current inertia weight (linear decay)."""
        progress = self.iteration / self.config.max_iterations
        return self.config.w_start - progress * (self.config.w_start - self.config.w_end)

    def step(self, fitness_fn: Callable[[np.ndarray], float]) -> float:
        """Execute one iteration of PSO.

        Args:
            fitness_fn: Function that takes position and returns fitness score
                       (lower is better)

        Returns:
            Current global best fitness

        """
        w = self._get_inertia()
        improved = False

        # Evaluate all particles
        for particle in self.particles:
            # Calculate fitness
            fitness = fitness_fn(particle.position)

            # Update personal best
            if particle.update_personal_best(fitness):
                # Check if this is new global best
                if fitness < self.global_best_fitness:
                    self.global_best = particle.position.copy()
                    self.global_best_fitness = fitness
                    improved = True

        # Update velocities and positions
        for particle in self.particles:
            particle.update_velocity(
                global_best=self.global_best,
                w=w,
                c1=self.config.c1,
                c2=self.config.c2,
                beta1=self.config.beta1,
                beta2=self.config.beta2,
            )
            particle.update_position(
                bounds=self.config.bounds,
                max_velocity=self.config.max_velocity,
            )

        # Track history and stagnation
        self.fitness_history.append(self.global_best_fitness)
        self.iteration += 1

        if improved:
            self.stagnation_count = 0
        else:
            self.stagnation_count += 1

        return self.global_best_fitness

    def step_parallel(
        self,
        fitness_fn: Callable[[np.ndarray], float],
        executor: ProcessPoolExecutor | None = None,
    ) -> float:
        """Execute one iteration with parallel fitness evaluation.

        Args:
            fitness_fn: Fitness function (must be picklable for ProcessPool)
            executor: Optional executor for parallel evaluation

        """
        w = self._get_inertia()

        # Parallel fitness evaluation
        positions = [p.position for p in self.particles]

        if executor is not None:
            fitnesses = list(executor.map(fitness_fn, positions))
        else:
            # Fallback to sequential
            fitnesses = [fitness_fn(pos) for pos in positions]

        # Update particles with evaluated fitness
        improved = False
        for particle, fitness in zip(self.particles, fitnesses, strict=False):
            if particle.update_personal_best(fitness):
                if fitness < self.global_best_fitness:
                    self.global_best = particle.position.copy()
                    self.global_best_fitness = fitness
                    improved = True

        # Update velocities and positions
        for particle in self.particles:
            particle.update_velocity(
                global_best=self.global_best,
                w=w,
                c1=self.config.c1,
                c2=self.config.c2,
            )
            particle.update_position(
                bounds=self.config.bounds,
                max_velocity=self.config.max_velocity,
            )

        self.fitness_history.append(self.global_best_fitness)
        self.iteration += 1
        self.stagnation_count = 0 if improved else self.stagnation_count + 1

        return self.global_best_fitness

    def is_converged(self) -> bool:
        """Check if swarm has converged."""
        if self.iteration < 2:
            return False

        # Check fitness improvement
        if len(self.fitness_history) >= 2:
            improvement = abs(self.fitness_history[-1] - self.fitness_history[-2])
            if improvement < self.config.convergence_threshold:
                return True

        # Check stagnation
        return self.stagnation_count >= self.config.stagnation_limit

    def optimize(
        self,
        fitness_fn: Callable[[np.ndarray], float],
        max_iterations: int | None = None,
        parallel: bool = False,
        n_workers: int = 4,
    ) -> OptimizationResult:
        """Run full optimization loop.

        Args:
            fitness_fn: Function to minimize
            max_iterations: Override config max_iterations
            parallel: Use parallel fitness evaluation
            n_workers: Number of parallel workers

        Returns:
            OptimizationResult with best solution and history

        """
        max_iter = max_iterations or self.config.max_iterations

        executor = None
        if parallel:
            executor = ProcessPoolExecutor(max_workers=n_workers)

        try:
            for _ in range(max_iter):
                if parallel and executor:
                    self.step_parallel(fitness_fn, executor)
                else:
                    self.step(fitness_fn)

                if self.is_converged():
                    break
        finally:
            if executor:
                executor.shutdown(wait=False)

        return OptimizationResult(
            best_position=self.global_best.copy(),
            best_fitness=self.global_best_fitness,
            iterations=self.iteration,
            converged=self.is_converged(),
            fitness_history=self.fitness_history.copy(),
            final_swarm_state=[p.get_state() for p in self.particles],
        )

    async def optimize_async(
        self,
        fitness_fn: Callable[[np.ndarray], float],
        max_iterations: int | None = None,
    ) -> OptimizationResult:
        """Async optimization for integration with async frameworks.

        Uses ThreadPoolExecutor for parallel evaluation without blocking.
        """
        max_iter = max_iterations or self.config.max_iterations
        loop = asyncio.get_event_loop()

        with ThreadPoolExecutor() as executor:
            for _ in range(max_iter):
                # Run step in thread pool
                await loop.run_in_executor(executor, lambda: self.step(fitness_fn))

                if self.is_converged():
                    break

        return OptimizationResult(
            best_position=self.global_best.copy(),
            best_fitness=self.global_best_fitness,
            iterations=self.iteration,
            converged=self.is_converged(),
            fitness_history=self.fitness_history.copy(),
            final_swarm_state=[p.get_state() for p in self.particles],
        )

    def reset(self) -> None:
        """Reset swarm for new optimization run."""
        self._initialize_swarm()
        self.global_best = None
        self.global_best_fitness = float("inf")
        self.fitness_history = []
        self.iteration = 0
        self.stagnation_count = 0

    def get_diversity(self) -> float:
        """Calculate swarm diversity (average distance from centroid).

        Higher diversity = more exploration, lower = more exploitation.
        """
        positions = np.array([p.position for p in self.particles])
        centroid = np.mean(positions, axis=0)
        distances = np.linalg.norm(positions - centroid, axis=1)
        return np.mean(distances)

    def inject_particle(self, position: np.ndarray) -> None:
        """Inject a new particle at specified position (e.g., from prior)."""
        if len(self.particles) > 0:
            # Replace worst particle
            worst_idx = np.argmax([p.fitness for p in self.particles])
            self.particles[worst_idx] = Particle(
                position=position.copy(),
                velocity=np.random.uniform(-0.1, 0.1, position.shape),
                personal_best=position.copy(),
                particle_id=worst_idx,
            )
