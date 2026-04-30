"""PSO Particle: Represents a candidate solution in the search space.

Each particle has:
- Position: Current solution (neural network weights)
- Velocity: Movement direction and speed
- Personal best: Best position found by this particle
- Adam moments (optional): For adaptive momentum (m, v)
"""

from dataclasses import dataclass

import numpy as np


@dataclass
class ParticleState:
    """Immutable state snapshot of a particle."""

    position: np.ndarray
    velocity: np.ndarray
    personal_best: np.ndarray
    personal_best_fitness: float
    fitness: float


@dataclass
class Particle:
    """A single particle in the PSO swarm.

    Represents a candidate neural network weight configuration.
    Uses adaptive momentum (Adam-style) for improved convergence.
    """

    # Core state
    position: np.ndarray
    velocity: np.ndarray
    personal_best: np.ndarray
    personal_best_fitness: float = float("inf")
    fitness: float = float("inf")

    # Adam-style adaptive moments (optional)
    m: np.ndarray | None = None  # First moment (mean)
    v: np.ndarray | None = None  # Second moment (variance)

    # Metadata
    particle_id: int = 0
    age: int = 0  # Number of iterations

    def __post_init__(self):
        """Initialize Adam moments if not provided."""
        if self.m is None:
            self.m = np.zeros_like(self.position)
        if self.v is None:
            self.v = np.zeros_like(self.position)

    @classmethod
    def random(
        cls,
        dimensions: int,
        bounds: tuple[float, float] = (-1.0, 1.0),
        particle_id: int = 0,
    ) -> "Particle":
        """Create a randomly initialized particle."""
        low, high = bounds
        position = np.random.uniform(low, high, dimensions)
        velocity = np.random.uniform(-0.1, 0.1, dimensions)
        return cls(
            position=position,
            velocity=velocity,
            personal_best=position.copy(),
            personal_best_fitness=float("inf"),
            particle_id=particle_id,
        )

    def update_velocity(
        self,
        global_best: np.ndarray,
        w: float = 0.7,  # Inertia weight
        c1: float = 1.5,  # Cognitive coefficient (personal)
        c2: float = 1.5,  # Social coefficient (global)
        beta1: float = 0.9,  # Adam first moment decay
        beta2: float = 0.999,  # Adam second moment decay
    ) -> None:
        """Update velocity using PSO formula with Adam-style momentum.

        v_new = w * v_old + c1 * r1 * (personal_best - position)
                         + c2 * r2 * (global_best - position)

        With Adam: apply momentum smoothing to velocity updates.
        """
        r1 = np.random.random(self.position.shape)
        r2 = np.random.random(self.position.shape)

        # Standard PSO velocity update
        cognitive = c1 * r1 * (self.personal_best - self.position)
        social = c2 * r2 * (global_best - self.position)
        raw_velocity = w * self.velocity + cognitive + social

        # Adam-style adaptive update
        self.m = beta1 * self.m + (1 - beta1) * raw_velocity
        self.v = beta2 * self.v + (1 - beta2) * (raw_velocity**2)

        # Bias correction
        t = self.age + 1
        m_hat = self.m / (1 - beta1**t)
        v_hat = self.v / (1 - beta2**t)

        # Final velocity with adaptive scaling
        eps = 1e-8
        self.velocity = m_hat / (np.sqrt(v_hat) + eps)

    def update_position(
        self,
        bounds: tuple[float, float] | None = None,
        max_velocity: float = 1.0,
    ) -> None:
        """Update position using current velocity.

        Clips position to bounds and velocity to max_velocity.
        """
        # Clip velocity
        self.velocity = np.clip(self.velocity, -max_velocity, max_velocity)

        # Update position
        self.position = self.position + self.velocity

        # Clip to bounds
        if bounds is not None:
            self.position = np.clip(self.position, bounds[0], bounds[1])

        self.age += 1

    def update_personal_best(self, fitness: float) -> bool:
        """Update personal best if current fitness is better.

        Returns True if personal best was updated.
        """
        self.fitness = fitness
        if fitness < self.personal_best_fitness:
            self.personal_best = self.position.copy()
            self.personal_best_fitness = fitness
            return True
        return False

    def get_state(self) -> ParticleState:
        """Get immutable state snapshot."""
        return ParticleState(
            position=self.position.copy(),
            velocity=self.velocity.copy(),
            personal_best=self.personal_best.copy(),
            personal_best_fitness=self.personal_best_fitness,
            fitness=self.fitness,
        )

    def reset_velocity(self, scale: float = 0.1) -> None:
        """Reset velocity to random values (for escaping local minima)."""
        self.velocity = np.random.uniform(-scale, scale, self.position.shape)
        self.m = np.zeros_like(self.position)
        self.v = np.zeros_like(self.position)
