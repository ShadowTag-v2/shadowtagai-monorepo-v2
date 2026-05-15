"""PsoModel: High-level adapter for n-autoresearch/Kosmos/BioAgents integration.

Provides a simple interface for PSO-based neural network optimization
that integrates with the n-autoresearch/Kosmos/BioAgents swarm and existing optimizers.

Usage:
    model = PsoModel(target_network=my_nn)
    result = await model.optimize(training_data, labels)
    optimized_nn = model.get_optimized_network()
"""

import asyncio
import logging
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import numpy as np

from ..core.fitness import CrossEntropyFitness, FitnessFunction, MSEFitness
from ..core.swarm import OptimizationResult, SwarmConfig
from ..optimizers.weight_optimizer import WeightOptimizer

logger = logging.getLogger(__name__)


@dataclass
class PsoModelConfig:
    """Configuration for PsoModel."""

    # Swarm settings
    num_particles: int = 50
    max_iterations: int = 100
    bounds: tuple[float, float] = (-2.0, 2.0)

    # PSO coefficients
    w_start: float = 0.9
    w_end: float = 0.4
    c1: float = 1.5
    c2: float = 1.5

    # Optimization settings
    batch_size: int | None = 32
    parallel: bool = False
    n_workers: int = 4

    # Convergence
    convergence_threshold: float = 1e-6
    stagnation_limit: int = 10

    # Task type
    task_type: str = "regression"  # "regression" or "classification"


class PsoModel:
    """High-level PSO model adapter for n-autoresearch/Kosmos/BioAgents integration.

    This class wraps the low-level PSO optimizer to provide a simple
    interface for neural network optimization that integrates with
    the n-autoresearch/Kosmos/BioAgents swarm orchestrator.

    Features:
    - Automatic fitness function selection based on task type
    - Async optimization for non-blocking swarm operations
    - Integration with AdaptivePSO and ParallelFitnessEvaluator
    - Progress callbacks for monitoring
    - Early stopping on convergence

    Usage:
        # Basic usage
        model = PsoModel(target_network=my_neural_net)
        result = await model.optimize(train_data, train_labels)

        # With n-autoresearch/Kosmos/BioAgents integration
        from shadowtagai.agents.adaptive_pso import AdaptivePSO
        from shadowtagai.agents.parallel_fitness import ParallelFitnessEvaluator

        model = PsoModel(
            target_network=my_nn,
            adaptive_pso=AdaptivePSO(num_particles=600),
            parallel_evaluator=ParallelFitnessEvaluator()
        )
    """

    def __init__(
        self,
        target_network: Any,
        config: PsoModelConfig | None = None,
        adaptive_pso: Any | None = None,
        parallel_evaluator: Any | None = None,
        fitness_fn: FitnessFunction | None = None,
    ):
        """Initialize PsoModel.

        Args:
            target_network: Neural network to optimize
            config: PsoModelConfig or use defaults
            adaptive_pso: Optional AdaptivePSO instance for enhanced optimization
            parallel_evaluator: Optional ParallelFitnessEvaluator for fast evaluation
            fitness_fn: Custom fitness function (auto-selected if not provided)

        """
        self.network = target_network
        self.config = config or PsoModelConfig()
        self.adaptive_pso = adaptive_pso
        self.parallel_evaluator = parallel_evaluator

        # Select fitness function
        if fitness_fn:
            self.fitness_fn = fitness_fn
        elif self.config.task_type == "classification":
            self.fitness_fn = CrossEntropyFitness()
        else:
            self.fitness_fn = MSEFitness()

        self.fitness_fn.set_network(target_network)

        # Create weight optimizer
        swarm_config = SwarmConfig(
            num_particles=self.config.num_particles,
            max_iterations=self.config.max_iterations,
            bounds=self.config.bounds,
            w_start=self.config.w_start,
            w_end=self.config.w_end,
            c1=self.config.c1,
            c2=self.config.c2,
            convergence_threshold=self.config.convergence_threshold,
            stagnation_limit=self.config.stagnation_limit,
        )

        self._optimizer = WeightOptimizer(
            network=target_network,
            fitness_fn=self.fitness_fn,
            swarm_config=swarm_config,
            bounds=self.config.bounds,
        )

        # Track optimization state
        self._result: OptimizationResult | None = None
        self._callbacks: list[Callable] = []

    def add_callback(self, callback: Callable[[int, float, dict], None]) -> "PsoModel":
        """Add progress callback.

        Callback receives: (iteration, fitness, stats_dict)
        """
        self._callbacks.append(callback)
        return self

    async def optimize(
        self,
        data: np.ndarray,
        labels: np.ndarray,
        max_iterations: int | None = None,
        batch_size: int | None = None,
    ) -> OptimizationResult:
        """Optimize neural network weights using PSO.

        Args:
            data: Training data
            labels: Training labels
            max_iterations: Override config max_iterations
            batch_size: Override config batch_size

        Returns:
            OptimizationResult with best weights and history

        """
        max_iter = max_iterations or self.config.max_iterations
        batch = batch_size or self.config.batch_size

        logger.info(
            f"Starting PSO optimization: {self._optimizer.shape_info.total_params} params, "
            f"{self.config.num_particles} particles, max {max_iter} iterations",
        )

        # Use adaptive PSO if available
        if self.adaptive_pso is not None:
            self._result = await self._optimize_with_adaptive(data, labels, max_iter, batch)
        else:
            self._result = await self._optimizer.optimize_async(
                data=data,
                labels=labels,
                max_iterations=max_iter,
                batch_size=batch,
            )

        logger.info(
            f"PSO optimization complete: fitness={self._result.best_fitness:.6f}, "
            f"iterations={self._result.iterations}, converged={self._result.converged}",
        )

        return self._result

    async def _optimize_with_adaptive(
        self,
        data: np.ndarray,
        labels: np.ndarray,
        max_iterations: int,
        batch_size: int | None,
    ) -> OptimizationResult:
        """Optimization using AdaptivePSO from shadowtagai.

        Integrates with existing swarm infrastructure.
        """
        # Create fitness wrapper
        fitness_wrapper = self._optimizer.create_fitness_wrapper(data, labels, batch_size)

        # Use parallel evaluator if available
        if self.parallel_evaluator is not None:
            # Wrap for parallel evaluation
            async def parallel_fitness(positions: list[np.ndarray]) -> list[float]:
                return await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.parallel_evaluator.evaluate_batch(fitness_wrapper, positions),
                )

            # Run adaptive PSO with parallel evaluation
            best_pos, best_fit, history = await self.adaptive_pso.optimize_async(
                fitness_fn=fitness_wrapper,
                parallel_fn=parallel_fitness,
                max_iterations=max_iterations,
            )
        else:
            # Standard adaptive PSO
            best_pos, best_fit, history = await self.adaptive_pso.optimize_async(
                fitness_fn=fitness_wrapper,
                max_iterations=max_iterations,
            )

        # Apply best weights
        self._optimizer._apply_weights(best_pos)

        return OptimizationResult(
            best_position=best_pos,
            best_fitness=best_fit,
            iterations=len(history),
            converged=True,
            fitness_history=history,
            final_swarm_state=[],
        )

    def optimize_sync(
        self,
        data: np.ndarray,
        labels: np.ndarray,
        max_iterations: int | None = None,
        batch_size: int | None = None,
    ) -> OptimizationResult:
        """Synchronous optimization (non-async version)."""
        max_iter = max_iterations or self.config.max_iterations
        batch = batch_size or self.config.batch_size

        self._result = self._optimizer.optimize(
            data=data,
            labels=labels,
            max_iterations=max_iter,
            batch_size=batch,
            parallel=self.config.parallel,
            n_workers=self.config.n_workers,
        )

        return self._result

    def get_optimized_network(self) -> Any:
        """Get neural network with optimized weights applied."""
        return self._optimizer.get_optimized_network()

    def get_optimized_weights(self) -> np.ndarray | None:
        """Get optimized weights as flat array."""
        return self._optimizer.get_optimized_weights()

    def get_optimized_weights_dict(self) -> dict[str, np.ndarray]:
        """Get optimized weights as dictionary by layer name."""
        return self._optimizer.get_optimized_weights_dict()

    def get_result(self) -> OptimizationResult | None:
        """Get last optimization result."""
        return self._result

    def get_stats(self) -> dict[str, Any]:
        """Get optimization statistics."""
        stats = self._optimizer.get_stats()
        stats.update(
            {
                "task_type": self.config.task_type,
                "has_adaptive_pso": self.adaptive_pso is not None,
                "has_parallel_evaluator": self.parallel_evaluator is not None,
            },
        )
        return stats

    def reset(self) -> None:
        """Reset optimizer for new optimization run."""
        self._optimizer.reset()
        self._result = None

    def save_weights(self, path: str) -> None:
        """Save optimized weights to file."""
        weights = self.get_optimized_weights()
        if weights is not None:
            np.save(path, weights)
            logger.info(f"Saved weights to {path}")

    def load_weights(self, path: str) -> None:
        """Load weights from file and apply to network."""
        weights = np.load(path)
        self._optimizer._apply_weights(weights)
        self._optimizer._optimized_weights = weights
        logger.info(f"Loaded weights from {path}")


# Factory function for common configurations
def create_pso_model(
    network: Any,
    task: str = "regression",
    num_particles: int = 50,
    max_iterations: int = 100,
    use_parallel: bool = False,
) -> PsoModel:
    """Create PsoModel with common configuration.

    Args:
        network: Neural network to optimize
        task: "regression" or "classification"
        num_particles: Swarm size
        max_iterations: Maximum optimization iterations
        use_parallel: Enable parallel fitness evaluation

    Returns:
        Configured PsoModel instance

    """
    config = PsoModelConfig(
        num_particles=num_particles,
        max_iterations=max_iterations,
        task_type=task,
        parallel=use_parallel,
    )
    return PsoModel(target_network=network, config=config)
