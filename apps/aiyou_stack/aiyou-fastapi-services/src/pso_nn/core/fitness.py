"""Fitness Functions: Loss-based fitness for neural network optimization.

Converts neural network losses to PSO fitness values.
Supports MSE, cross-entropy, and custom composed fitness functions.
"""

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import numpy as np


class FitnessFunction(ABC):
    """Abstract base class for fitness functions."""

    @abstractmethod
    def __call__(self, weights: np.ndarray, data: Any, labels: Any) -> float:
        """Calculate fitness (lower is better).

        Args:
            weights: Flattened neural network weights
            data: Input data for evaluation
            labels: Target labels

        Returns:
            Fitness score (lower = better)

        """

    @abstractmethod
    def set_network(self, network: Any) -> None:
        """Set the neural network to evaluate."""


@dataclass
class MSEFitness(FitnessFunction):
    """Mean Squared Error fitness for regression tasks.

    Fitness = MSE(predictions, targets)
    """

    network: Any = None
    weight_decay: float = 0.0  # L2 regularization

    def set_network(self, network: Any) -> None:
        self.network = network

    def __call__(self, weights: np.ndarray, data: np.ndarray, labels: np.ndarray) -> float:
        """Calculate MSE fitness."""
        if self.network is None:
            raise ValueError("Network not set. Call set_network() first.")

        # Apply weights to network
        self._apply_weights(weights)

        # Forward pass
        predictions = self._forward(data)

        # MSE loss
        mse = np.mean((predictions - labels) ** 2)

        # L2 regularization
        l2_penalty = self.weight_decay * np.sum(weights**2)

        return mse + l2_penalty

    def _apply_weights(self, weights: np.ndarray) -> None:
        """Apply flattened weights to network."""
        # This is a placeholder - actual implementation depends on
        # network framework (PyTorch, NumPy, etc.)
        if hasattr(self.network, "set_weights"):
            self.network.set_weights(weights)

    def _forward(self, data: np.ndarray) -> np.ndarray:
        """Forward pass through network."""
        if hasattr(self.network, "forward"):
            return self.network.forward(data)
        if callable(self.network):
            return self.network(data)
        raise ValueError("Network must have forward() method or be callable")


@dataclass
class CrossEntropyFitness(FitnessFunction):
    """Cross-entropy fitness for classification tasks.

    Fitness = -sum(labels * log(predictions + eps))
    """

    network: Any = None
    weight_decay: float = 0.0
    eps: float = 1e-8  # Numerical stability

    def set_network(self, network: Any) -> None:
        self.network = network

    def __call__(self, weights: np.ndarray, data: np.ndarray, labels: np.ndarray) -> float:
        """Calculate cross-entropy fitness."""
        if self.network is None:
            raise ValueError("Network not set. Call set_network() first.")

        # Apply weights to network
        self._apply_weights(weights)

        # Forward pass with softmax
        logits = self._forward(data)
        predictions = self._softmax(logits)

        # Cross-entropy loss
        ce_loss = -np.mean(np.sum(labels * np.log(predictions + self.eps), axis=-1))

        # L2 regularization
        l2_penalty = self.weight_decay * np.sum(weights**2)

        return ce_loss + l2_penalty

    def _apply_weights(self, weights: np.ndarray) -> None:
        if hasattr(self.network, "set_weights"):
            self.network.set_weights(weights)

    def _forward(self, data: np.ndarray) -> np.ndarray:
        if hasattr(self.network, "forward"):
            return self.network.forward(data)
        if callable(self.network):
            return self.network(data)
        raise ValueError("Network must have forward() method or be callable")

    @staticmethod
    def _softmax(x: np.ndarray) -> np.ndarray:
        """Numerically stable softmax."""
        e_x = np.exp(x - np.max(x, axis=-1, keepdims=True))
        return e_x / np.sum(e_x, axis=-1, keepdims=True)


@dataclass
class ComposedFitness(FitnessFunction):
    """Composed fitness from multiple objectives.

    Combines multiple fitness functions with weights.
    """

    components: list[tuple[FitnessFunction, float]] = None  # (fitness, weight)
    network: Any = None

    def __post_init__(self):
        if self.components is None:
            self.components = []

    def add_component(self, fitness_fn: FitnessFunction, weight: float = 1.0) -> "ComposedFitness":
        """Add a fitness component."""
        self.components.append((fitness_fn, weight))
        return self

    def set_network(self, network: Any) -> None:
        self.network = network
        for fitness_fn, _ in self.components:
            fitness_fn.set_network(network)

    def __call__(self, weights: np.ndarray, data: np.ndarray, labels: np.ndarray) -> float:
        """Calculate weighted sum of component fitnesses."""
        total = 0.0
        for fitness_fn, w in self.components:
            total += w * fitness_fn(weights, data, labels)
        return total


class SimpleFitness:
    """Simple fitness wrapper for custom functions.

    Usage:
        fitness = SimpleFitness(lambda w: my_loss(w, data, labels))
    """

    def __init__(self, fn: Callable[[np.ndarray], float]):
        self.fn = fn

    def __call__(self, weights: np.ndarray) -> float:
        return self.fn(weights)


def create_batch_fitness(
    fitness_fn: FitnessFunction, data: np.ndarray, labels: np.ndarray, batch_size: int = 32,
) -> Callable[[np.ndarray], float]:
    """Create a fitness function that evaluates on random mini-batches.

    Useful for large datasets where full evaluation is expensive.
    """
    n_samples = len(data)

    def batch_fitness(weights: np.ndarray) -> float:
        # Random batch
        idx = np.random.choice(n_samples, batch_size, replace=False)
        batch_data = data[idx]
        batch_labels = labels[idx]
        return fitness_fn(weights, batch_data, batch_labels)

    return batch_fitness


def create_noisy_fitness(
    fitness_fn: Callable[[np.ndarray], float], noise_scale: float = 0.01,
) -> Callable[[np.ndarray], float]:
    """Add noise to fitness evaluation for exploration.

    Helps escape local minima by making the fitness landscape less smooth.
    """

    def noisy_fitness(weights: np.ndarray) -> float:
        base_fitness = fitness_fn(weights)
        noise = np.random.normal(0, noise_scale * abs(base_fitness))
        return base_fitness + noise

    return noisy_fitness
