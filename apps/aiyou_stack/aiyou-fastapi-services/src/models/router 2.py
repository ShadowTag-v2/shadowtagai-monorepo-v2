"""Token-level request routing inspired by Aegaeon."""

import logging
from dataclasses import dataclass
from datetime import datetime

from .registry import ModelRegistry

logger = logging.getLogger(__name__)


@dataclass
class RoutingDecision:
    """Result of routing decision."""

    model_name: str
    estimated_tokens: int
    gpu_id: int | None
    reason: str
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class TokenLevelRouter:
    """
    Token-level router for multi-model serving.

    Implements Aegaeon-style token-granular scheduling:
    1. Estimates token budget for incoming requests
    2. Routes to models with available token capacity
    3. Enables token-level preemption for bursty workloads
    """

    def __init__(
        self,
        registry: ModelRegistry,
        token_budget_per_gpu: int = 32768,
        enable_preemption: bool = True,
    ):
        self.registry = registry
        self.token_budget_per_gpu = token_budget_per_gpu
        self.enable_preemption = enable_preemption

        # Track token allocations per GPU
        self.gpu_token_usage: dict[int, int] = {}

    def estimate_tokens(self, prompt: str, max_tokens: int = None) -> int:
        """
        Estimate token count for a request.

        Simple estimation: ~4 chars per token (GPT-style).
        For production, use tiktoken or model-specific tokenizer.
        """
        estimated_prompt_tokens = len(prompt) // 4
        estimated_completion_tokens = max_tokens or 512
        return estimated_prompt_tokens + estimated_completion_tokens

    async def route_request(
        self,
        prompt: str,
        model_name: str | None = None,
        max_tokens: int = 512,
        strategy: str = "least_loaded",
    ) -> RoutingDecision:
        """
        Route a request to the best available model.

        Args:
            prompt: Input prompt
            model_name: Specific model to use (optional)
            max_tokens: Maximum tokens to generate
            strategy: Routing strategy (least_loaded, round_robin, token_aware)

        Returns:
            RoutingDecision with selected model
        """
        estimated_tokens = self.estimate_tokens(prompt, max_tokens)

        # If specific model requested, route to it
        if model_name:
            model = self.registry.get_model(model_name)
            if model and model.backend:
                return RoutingDecision(
                    model_name=model_name,
                    estimated_tokens=estimated_tokens,
                    gpu_id=model.gpu_id,
                    reason=f"User-specified model: {model_name}",
                )
            else:
                raise ValueError(f"Model {model_name} not available")

        # Auto-routing based on strategy
        if strategy == "token_aware":
            return await self._route_token_aware(estimated_tokens)
        elif strategy == "round_robin":
            return self._route_round_robin(estimated_tokens)
        else:  # least_loaded (default)
            return self._route_least_loaded(estimated_tokens)

    def _route_least_loaded(self, estimated_tokens: int) -> RoutingDecision:
        """Route to model with least active requests."""
        model = self.registry.get_least_loaded_model()

        if not model:
            raise RuntimeError("No ready models available")

        return RoutingDecision(
            model_name=model.name,
            estimated_tokens=estimated_tokens,
            gpu_id=model.gpu_id,
            reason=f"Least loaded ({model.metrics.active_requests} active requests)",
        )

    def _route_round_robin(self, estimated_tokens: int) -> RoutingDecision:
        """Simple round-robin routing."""
        ready_models = self.registry.get_ready_models()

        if not ready_models:
            raise RuntimeError("No ready models available")

        # Simple round-robin: pick by timestamp
        model = min(ready_models, key=lambda m: m.metrics.last_request_time or datetime.min)

        return RoutingDecision(
            model_name=model.name,
            estimated_tokens=estimated_tokens,
            gpu_id=model.gpu_id,
            reason="Round-robin rotation",
        )

    async def _route_token_aware(self, estimated_tokens: int) -> RoutingDecision:
        """
        Advanced token-aware routing (Aegaeon-style).

        Routes based on available token budget per GPU.
        """
        ready_models = self.registry.get_ready_models()

        if not ready_models:
            raise RuntimeError("No ready models available")

        # Find model on GPU with most available token budget
        best_model = None
        best_available = 0

        for model in ready_models:
            if model.gpu_id is None:
                continue

            used_tokens = self.gpu_token_usage.get(model.gpu_id, 0)
            available = self.token_budget_per_gpu - used_tokens

            # Check if this GPU has enough budget
            if available >= estimated_tokens and available > best_available:
                best_model = model
                best_available = available

        # If no GPU has enough budget, fall back to least loaded
        if not best_model:
            logger.warning(
                f"No GPU with {estimated_tokens} token budget available, "
                "falling back to least loaded"
            )
            return self._route_least_loaded(estimated_tokens)

        return RoutingDecision(
            model_name=best_model.name,
            estimated_tokens=estimated_tokens,
            gpu_id=best_model.gpu_id,
            reason=f"Token-aware ({best_available} tokens available on GPU {best_model.gpu_id})",
        )

    async def allocate_tokens(self, decision: RoutingDecision):
        """Allocate tokens for a request."""
        if decision.gpu_id is not None:
            current = self.gpu_token_usage.get(decision.gpu_id, 0)
            self.gpu_token_usage[decision.gpu_id] = current + decision.estimated_tokens

    async def release_tokens(self, decision: RoutingDecision):
        """Release tokens after request completion."""
        if decision.gpu_id is not None:
            current = self.gpu_token_usage.get(decision.gpu_id, 0)
            self.gpu_token_usage[decision.gpu_id] = max(0, current - decision.estimated_tokens)

    def get_routing_stats(self) -> dict:
        """Get routing statistics."""
        return {
            "token_budget_per_gpu": self.token_budget_per_gpu,
            "gpu_token_usage": dict(self.gpu_token_usage),
            "gpu_utilization": {
                gpu_id: (used / self.token_budget_per_gpu)
                for gpu_id, used in self.gpu_token_usage.items()
            },
        }
