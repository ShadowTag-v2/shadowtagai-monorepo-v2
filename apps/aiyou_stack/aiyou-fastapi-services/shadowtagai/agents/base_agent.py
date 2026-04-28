#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Abstract Base Agent for Flying n-autoresearch/Kosmos/BioAgents swarm.
Defines composable agent interface with forward/backward pattern.
Based on patterns from yyz-agentics-june/neural_network/core/base.py
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

import numpy as np


class AgentTier(Enum):
    """Agent service tiers."""

    FREE = "FREE"
    FLASH = "FLASH"
    PRO = "PRO"


class AgentStatus(Enum):
    """Agent operational status."""

    IDLE = "IDLE"
    ACTIVE = "ACTIVE"
    BUSY = "BUSY"
    RELIEVED = "RELIEVED"
    ERROR = "ERROR"


@dataclass
class AgentContext:
    """Execution context passed through agent pipeline."""

    task_id: str
    tier: AgentTier
    input_data: Any
    metadata: dict = field(default_factory=dict)
    cache: dict = field(default_factory=dict)
    gradients: dict = field(default_factory=dict)


@dataclass
class AgentResult:
    """Result from agent forward pass."""

    output: Any
    latency_ms: float
    success: bool
    error: str | None = None
    metrics: dict = field(default_factory=dict)


class BaseAgent(ABC):
    """Abstract base class for Flying Monkey agents.

    Implements composable forward/backward pattern from neural networks.
    Agents can be chained in sequences for complex task pipelines.

    FM 5-0 TLP 8-step mapping:
    - forward(): Steps 1-7 (receive → execute)
    - backward(): Step 8 (supervise/refine)
    """

    def __init__(self, agent_id: int, tier: AgentTier = AgentTier.FREE, squad_id: int = None):
        """Initialize base agent.

        Args:
            agent_id: Unique agent identifier (0-599)
            tier: Service tier (FREE, FLASH, PRO)
            squad_id: Squad assignment (0-23)

        """
        self.agent_id = agent_id
        self.tier = tier
        self.squad_id = squad_id or agent_id // 25

        # State
        self.status = AgentStatus.IDLE
        self.params: dict[str, np.ndarray] = {}
        self.grads: dict[str, np.ndarray] = {}
        self.cache: dict[str, Any] = {}

        # Metrics
        self.tasks_completed = 0
        self.errors = 0
        self.total_latency_ms = 0.0
        self.shift_start = datetime.utcnow()
        self.shift_end = None

        # Initialize agent-specific parameters
        self._init_params()

    @abstractmethod
    def _init_params(self):
        """Initialize agent-specific parameters."""

    @abstractmethod
    def forward(self, context: AgentContext, training: bool = True) -> AgentResult:
        """Execute forward pass (task processing).

        Args:
            context: Execution context with task data
            training: Whether to cache values for backward pass

        Returns:
            AgentResult with output and metrics

        """

    @abstractmethod
    def backward(self, grad_output: np.ndarray) -> np.ndarray:
        """Execute backward pass (refinement/feedback).

        Args:
            grad_output: Gradient from downstream agent

        Returns:
            Gradient to upstream agent

        """

    def __call__(self, context: AgentContext, training: bool = True) -> AgentResult:
        """Allow agent to be called as function."""
        return self.forward(context, training)

    def update_params(self, learning_rate: float = 0.01):
        """Update parameters using accumulated gradients."""
        for name, param in self.params.items():
            if name in self.grads:
                self.params[name] = param - learning_rate * self.grads[name]

    def reset_gradients(self):
        """Reset accumulated gradients."""
        self.grads = {name: np.zeros_like(param) for name, param in self.params.items()}

    def get_state(self) -> dict:
        """Get current agent state."""
        return {
            "agent_id": self.agent_id,
            "tier": self.tier.value,
            "squad_id": self.squad_id,
            "status": self.status.value,
            "tasks_completed": self.tasks_completed,
            "errors": self.errors,
            "avg_latency_ms": self.total_latency_ms / max(self.tasks_completed, 1),
            "shift_start": self.shift_start.isoformat(),
            "shift_end": self.shift_end.isoformat() if self.shift_end else None,
        }

    def relieve(self):
        """End agent's shift."""
        self.status = AgentStatus.RELIEVED
        self.shift_end = datetime.utcnow()


class CompositeAgent(BaseAgent):
    """Agent composed of multiple sub-agents in sequence.

    Enables complex task pipelines by chaining agents.
    """

    def __init__(
        self,
        agent_id: int,
        components: list[BaseAgent],
        tier: AgentTier = AgentTier.FREE,
    ):
        """Initialize composite agent.

        Args:
            agent_id: Unique identifier
            components: List of sub-agents to chain
            tier: Service tier

        """
        super().__init__(agent_id, tier)
        self.components = components

    def _init_params(self):
        """Composite agents have no direct params."""

    def forward(self, context: AgentContext, training: bool = True) -> AgentResult:
        """Execute all components in sequence."""
        import time

        start = time.time()

        current_context = context
        results = []

        for component in self.components:
            result = component.forward(current_context, training)
            results.append(result)

            if not result.success:
                return AgentResult(
                    output=None,
                    latency_ms=(time.time() - start) * 1000,
                    success=False,
                    error=f"Component {component.agent_id} failed: {result.error}",
                )

            # Pass output to next component
            current_context = AgentContext(
                task_id=context.task_id,
                tier=context.tier,
                input_data=result.output,
                metadata=context.metadata,
                cache=context.cache,
            )

        total_latency = (time.time() - start) * 1000
        self.total_latency_ms += total_latency
        self.tasks_completed += 1

        return AgentResult(
            output=results[-1].output if results else None,
            latency_ms=total_latency,
            success=True,
            metrics={
                "num_components": len(self.components),
                "component_latencies": [r.latency_ms for r in results],
            },
        )

    def backward(self, grad_output: np.ndarray) -> np.ndarray:
        """Propagate gradient through all components in reverse."""
        grad = grad_output
        for component in reversed(self.components):
            grad = component.backward(grad)
        return grad


class TaskProcessorAgent(BaseAgent):
    """Concrete agent for task processing.

    Implements basic task allocation and execution.
    """

    def _init_params(self):
        """Initialize processing parameters."""
        self.params = {"weights": np.random.randn(64, 64) * 0.01, "bias": np.zeros(64)}

    def forward(self, context: AgentContext, training: bool = True) -> AgentResult:
        """Process task."""
        import time

        start = time.time()

        try:
            self.status = AgentStatus.ACTIVE

            # Get input
            x = context.input_data
            if isinstance(x, (list, tuple)):
                x = np.array(x)

            # Ensure correct shape
            if x.ndim == 1:
                x = x.reshape(1, -1)

            # Pad or truncate to 64 dimensions
            if x.shape[1] < 64:
                x = np.pad(x, ((0, 0), (0, 64 - x.shape[1])))
            elif x.shape[1] > 64:
                x = x[:, :64]

            # Forward computation
            z = np.dot(x, self.params["weights"]) + self.params["bias"]
            output = np.maximum(z, 0)  # ReLU activation

            # Cache for backward
            if training:
                self.cache["input"] = x
                self.cache["z"] = z

            latency = (time.time() - start) * 1000
            self.total_latency_ms += latency
            self.tasks_completed += 1
            self.status = AgentStatus.IDLE

            return AgentResult(
                output=output,
                latency_ms=latency,
                success=True,
                metrics={"output_shape": output.shape},
            )

        except Exception as e:
            self.errors += 1
            self.status = AgentStatus.ERROR
            return AgentResult(
                output=None,
                latency_ms=(time.time() - start) * 1000,
                success=False,
                error=str(e),
            )

    def backward(self, grad_output: np.ndarray) -> np.ndarray:
        """Compute gradients."""
        # ReLU backward
        z = self.cache.get("z")
        if z is not None:
            grad_output = grad_output * (z > 0)

        # Weights gradient
        x = self.cache.get("input")
        if x is not None:
            self.grads["weights"] = np.dot(x.T, grad_output)
            self.grads["bias"] = np.sum(grad_output, axis=0)

        # Input gradient
        return np.dot(grad_output, self.params["weights"].T)


class PheromoneAgent(BaseAgent):
    """Agent for ACO pheromone field updates.

    Maintains and updates pheromone trails for squad routing.
    """

    def __init__(self, agent_id: int, num_squads: int = 24, **kwargs):
        self.num_squads = num_squads
        super().__init__(agent_id, **kwargs)

    def _init_params(self):
        """Initialize pheromone matrix."""
        self.params = {
            "pheromones": np.ones((self.num_squads, self.num_squads)),
            "evaporation_rate": np.array([0.1]),
        }

    def forward(self, context: AgentContext, training: bool = True) -> AgentResult:
        """Update pheromone field based on task result."""
        import time

        start = time.time()

        try:
            self.status = AgentStatus.ACTIVE

            # Get route from input
            route = context.input_data
            quality = context.metadata.get("quality", 1.0)

            # Evaporate existing pheromones
            rho = self.params["evaporation_rate"][0]
            self.params["pheromones"] *= 1 - rho

            # Deposit new pheromones along route
            if isinstance(route, (list, tuple)) and len(route) > 1:
                for i in range(len(route) - 1):
                    src, dst = route[i], route[i + 1]
                    if 0 <= src < self.num_squads and 0 <= dst < self.num_squads:
                        self.params["pheromones"][src, dst] += quality

            latency = (time.time() - start) * 1000
            self.total_latency_ms += latency
            self.tasks_completed += 1
            self.status = AgentStatus.IDLE

            return AgentResult(
                output=self.params["pheromones"].copy(),
                latency_ms=latency,
                success=True,
                metrics={
                    "total_pheromone": float(np.sum(self.params["pheromones"])),
                    "max_pheromone": float(np.max(self.params["pheromones"])),
                },
            )

        except Exception as e:
            self.errors += 1
            self.status = AgentStatus.ERROR
            return AgentResult(
                output=None,
                latency_ms=(time.time() - start) * 1000,
                success=False,
                error=str(e),
            )

    def backward(self, grad_output: np.ndarray) -> np.ndarray:
        """Pheromone gradients for reinforcement."""
        self.grads["pheromones"] = grad_output
        return grad_output


def main():
    """Demo of base agent usage."""
    import json

    print("///▞ Creating TaskProcessor agent...")
    agent = TaskProcessorAgent(agent_id=42, tier=AgentTier.FLASH)

    # Create context
    context = AgentContext(
        task_id="TASK-001",
        tier=AgentTier.FLASH,
        input_data=np.random.randn(1, 32),
        metadata={"priority": "high"},
    )

    # Forward pass
    result = agent.forward(context)
    print(f"///▞ Forward pass: success={result.success}, latency={result.latency_ms:.2f}ms")

    # Backward pass
    grad = np.random.randn(1, 64)
    input_grad = agent.backward(grad)
    print(f"///▞ Backward pass: grad shape={input_grad.shape}")

    # Get state
    state = agent.get_state()
    print("///▞ Agent state:")
    print(json.dumps(state, indent=2))

    # Demo composite agent
    print("\n///▞ Creating composite agent...")
    composite = CompositeAgent(
        agent_id=100,
        components=[
            TaskProcessorAgent(agent_id=101),
            TaskProcessorAgent(agent_id=102),
            TaskProcessorAgent(agent_id=103),
        ],
        tier=AgentTier.PRO,
    )

    result = composite.forward(context)
    print(f"///▞ Composite forward: success={result.success}, latency={result.latency_ms:.2f}ms")
    print(f"    Component latencies: {result.metrics.get('component_latencies', [])}")


if __name__ == "__main__":
    main()
