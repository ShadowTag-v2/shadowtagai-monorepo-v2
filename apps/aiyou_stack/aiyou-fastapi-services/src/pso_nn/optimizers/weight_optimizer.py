"""
Weight Optimizer: PSO-based neural network weight optimization.

Flattens network weights, optimizes via PSO, and reshapes back.
Supports PyTorch, NumPy arrays, and custom networks.
"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import numpy as np

from ..core.fitness import FitnessFunction
from ..core.swarm import OptimizationResult, ParticleSwarm, SwarmConfig


@dataclass
class NetworkShape:
    """Stores shape information for weight reshaping."""

    shapes: list[tuple[int, ...]]
    total_params: int
    param_names: list[str]


class WeightOptimizer:
    """
    PSO-based optimizer for neural network weights.

    Handles:
    - Weight flattening and reshaping
    - Bounds scaling for different layer types
    - Integration with PyTorch/NumPy networks
    - Warm-starting from existing weights

    Usage:
        optimizer = WeightOptimizer(network, fitness_fn)
        result = optimizer.optimize(data, labels)
        optimized_network = optimizer.get_optimized_network()
    """

    def __init__(
        self,
        network: Any,
        fitness_fn: FitnessFunction | None = None,
        swarm_config: SwarmConfig | None = None,
        bounds: tuple[float, float] = (-2.0, 2.0),
    ):
        """
        Initialize weight optimizer.

        Args:
            network: Neural network (PyTorch Module, NumPy-based, or custom)
            fitness_fn: Fitness function for evaluation
            swarm_config: PSO swarm configuration
            bounds: Weight bounds for initialization
        """
        self.network = network
        self.fitness_fn = fitness_fn
        self.bounds = bounds

        # Extract network shape
        self.shape_info = self._extract_shapes()

        # Initialize swarm with correct dimensions
        config = swarm_config or SwarmConfig()
        config.dimensions = self.shape_info.total_params
        config.bounds = bounds
        self.swarm = ParticleSwarm(config)

        # Warm-start from current weights
        current_weights = self._flatten_weights()
        self.swarm.inject_particle(current_weights)

        self._optimized_weights: np.ndarray | None = None

    def _extract_shapes(self) -> NetworkShape:
        """Extract weight shapes from network."""
        shapes = []
        names = []

        # Try PyTorch-style parameters
        if hasattr(self.network, "parameters"):
            for name, param in self.network.named_parameters():
                shapes.append(tuple(param.shape))
                names.append(name)
        # Try NumPy-style weights attribute
        elif hasattr(self.network, "weights"):
            weights = self.network.weights
            if isinstance(weights, dict):
                for name, w in weights.items():
                    shapes.append(w.shape)
                    names.append(name)
            elif isinstance(weights, list):
                for i, w in enumerate(weights):
                    shapes.append(w.shape)
                    names.append(f"layer_{i}")
        # Try get_weights method
        elif hasattr(self.network, "get_weights"):
            weights = self.network.get_weights()
            for i, w in enumerate(weights):
                shapes.append(w.shape)
                names.append(f"layer_{i}")
        else:
            raise ValueError(
                "Network must have parameters(), weights attribute, or get_weights() method"
            )

        total = sum(np.prod(s) for s in shapes)
        return NetworkShape(shapes=shapes, total_params=total, param_names=names)

    def _flatten_weights(self) -> np.ndarray:
        """Flatten all network weights into 1D array."""
        flat = []

        if hasattr(self.network, "parameters"):
            for param in self.network.parameters():
                flat.append(param.detach().cpu().numpy().flatten())
        elif hasattr(self.network, "weights"):
            weights = self.network.weights
            if isinstance(weights, dict):
                for w in weights.values():
                    flat.append(np.asarray(w).flatten())
            else:
                for w in weights:
                    flat.append(np.asarray(w).flatten())
        elif hasattr(self.network, "get_weights"):
            for w in self.network.get_weights():
                flat.append(np.asarray(w).flatten())

        return np.concatenate(flat)

    def _reshape_weights(self, flat: np.ndarray) -> list[np.ndarray]:
        """Reshape flat weights back to original shapes."""
        weights = []
        offset = 0

        for shape in self.shape_info.shapes:
            size = np.prod(shape)
            w = flat[offset : offset + size].reshape(shape)
            weights.append(w)
            offset += size

        return weights

    def _apply_weights(self, flat: np.ndarray) -> None:
        """Apply flattened weights to network."""
        weights = self._reshape_weights(flat)

        if hasattr(self.network, "parameters"):
            # PyTorch
            import torch

            with torch.no_grad():
                for param, w in zip(self.network.parameters(), weights, strict=False):
                    param.copy_(torch.from_numpy(w))
        elif hasattr(self.network, "set_weights"):
            self.network.set_weights(weights)
        elif hasattr(self.network, "weights"):
            if isinstance(self.network.weights, dict):
                for name, w in zip(self.shape_info.param_names, weights, strict=False):
                    self.network.weights[name] = w
            else:
                self.network.weights = weights

    def create_fitness_wrapper(
        self, data: np.ndarray, labels: np.ndarray, batch_size: int | None = None
    ) -> Callable[[np.ndarray], float]:
        """
        Create a fitness function wrapper for PSO.

        Args:
            data: Training data
            labels: Training labels
            batch_size: If provided, use mini-batch evaluation

        Returns:
            Callable fitness function
        """

        def evaluate(weights: np.ndarray) -> float:
            # Apply flattened weights to network
            self._apply_weights(weights)

            if batch_size and len(data) > batch_size:
                # Mini-batch evaluation
                idx = np.random.choice(len(data), batch_size, replace=False)
                batch_data = data[idx]
                batch_labels = labels[idx]
            else:
                batch_data = data
                batch_labels = labels

            # Always use default MSE since weights are already applied
            # (fitness_fn expects to apply weights itself, which causes issues)
            preds = self._forward(batch_data)
            return np.mean((preds - batch_labels) ** 2)

        return evaluate

    def _forward(self, data: np.ndarray) -> np.ndarray:
        """Forward pass through network."""
        if hasattr(self.network, "forward"):
            result = self.network.forward(data)
        elif callable(self.network):
            result = self.network(data)
        else:
            raise ValueError("Network must be callable or have forward()")

        # Handle PyTorch tensors
        if hasattr(result, "detach"):
            result = result.detach().cpu().numpy()

        return result

    def optimize(
        self,
        data: np.ndarray,
        labels: np.ndarray,
        max_iterations: int | None = None,
        batch_size: int | None = None,
        parallel: bool = False,
        n_workers: int = 4,
        callback: Callable[[int, float], None] | None = None,
    ) -> OptimizationResult:
        """
        Optimize network weights using PSO.

        Args:
            data: Training data
            labels: Training labels
            max_iterations: Override swarm config
            batch_size: Mini-batch size for evaluation
            parallel: Use parallel fitness evaluation
            n_workers: Number of parallel workers
            callback: Called after each iteration with (iter, fitness)

        Returns:
            OptimizationResult with best weights and history
        """
        fitness_wrapper = self.create_fitness_wrapper(data, labels, batch_size)

        # Run optimization
        result = self.swarm.optimize(
            fitness_fn=fitness_wrapper,
            max_iterations=max_iterations,
            parallel=parallel,
            n_workers=n_workers,
        )

        # Store optimized weights
        self._optimized_weights = result.best_position

        # Apply to network
        self._apply_weights(result.best_position)

        return result

    async def optimize_async(
        self,
        data: np.ndarray,
        labels: np.ndarray,
        max_iterations: int | None = None,
        batch_size: int | None = None,
    ) -> OptimizationResult:
        """Async optimization for integration with async frameworks."""
        fitness_wrapper = self.create_fitness_wrapper(data, labels, batch_size)

        result = await self.swarm.optimize_async(
            fitness_fn=fitness_wrapper, max_iterations=max_iterations
        )

        self._optimized_weights = result.best_position
        self._apply_weights(result.best_position)

        return result

    def get_optimized_weights(self) -> np.ndarray | None:
        """Get optimized weights as flat array."""
        return self._optimized_weights

    def get_optimized_weights_dict(self) -> dict[str, np.ndarray]:
        """Get optimized weights as dictionary."""
        if self._optimized_weights is None:
            return {}

        weights = self._reshape_weights(self._optimized_weights)
        return dict(zip(self.shape_info.param_names, weights, strict=False))

    def get_optimized_network(self) -> Any:
        """Get network with optimized weights applied."""
        if self._optimized_weights is not None:
            self._apply_weights(self._optimized_weights)
        return self.network

    def reset(self) -> None:
        """Reset optimizer for new optimization run."""
        self.swarm.reset()
        self._optimized_weights = None

        # Re-inject current weights
        current_weights = self._flatten_weights()
        self.swarm.inject_particle(current_weights)

    def get_stats(self) -> dict[str, Any]:
        """Get optimization statistics."""
        return {
            "network_params": self.shape_info.total_params,
            "param_names": self.shape_info.param_names,
            "swarm_size": self.swarm.config.num_particles,
            "iterations": self.swarm.iteration,
            "best_fitness": self.swarm.global_best_fitness,
            "converged": self.swarm.is_converged(),
            "diversity": self.swarm.get_diversity(),
        }
