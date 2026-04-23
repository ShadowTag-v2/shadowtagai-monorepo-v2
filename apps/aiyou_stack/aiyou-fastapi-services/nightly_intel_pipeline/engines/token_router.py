"""Token Router - Long⊗Short Entropy-Based Model Routing
Routes tokens between models based on entropy for compute optimization.

PRISM Integration: Long⊗Short Token Routing
- 80% low-entropy tokens → 7B short-thought model (fast, cheap)
- 20% high-entropy tokens → Full model (deep reasoning)

Based on Ultrathink synthesis for PNKLN inference optimization.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any

import structlog

if TYPE_CHECKING:
    import torch

try:
    import numpy as np

    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

logger = structlog.get_logger(__name__)


class ModelTier(Enum):
    """Model routing tiers based on computational requirements"""

    SHORT = "short"  # 7B model - fast, low compute
    LONG = "long"  # Full model - deep reasoning


@dataclass
class RoutingDecision:
    """Result of token routing decision"""

    tier: ModelTier
    model_id: str
    entropy: float
    threshold: float
    confidence: float
    tokens_routed: int
    reasoning: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "tier": self.tier.value,
            "model_id": self.model_id,
            "entropy": self.entropy,
            "threshold": self.threshold,
            "confidence": self.confidence,
            "tokens_routed": self.tokens_routed,
            "reasoning": self.reasoning,
            "metadata": self.metadata,
        }


@dataclass
class RoutingStats:
    """Statistics for routing decisions"""

    total_tokens: int = 0
    short_tokens: int = 0
    long_tokens: int = 0
    average_entropy: float = 0.0
    compute_savings_pct: float = 0.0
    decisions: list[RoutingDecision] = field(default_factory=list)

    @property
    def short_ratio(self) -> float:
        """Ratio of tokens routed to short model"""
        if self.total_tokens == 0:
            return 0.0
        return self.short_tokens / self.total_tokens

    @property
    def long_ratio(self) -> float:
        """Ratio of tokens routed to long model"""
        if self.total_tokens == 0:
            return 0.0
        return self.long_tokens / self.total_tokens

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "total_tokens": self.total_tokens,
            "short_tokens": self.short_tokens,
            "long_tokens": self.long_tokens,
            "short_ratio": self.short_ratio,
            "long_ratio": self.long_ratio,
            "average_entropy": self.average_entropy,
            "compute_savings_pct": self.compute_savings_pct,
            "decisions_count": len(self.decisions),
        }


# Router Configuration
TOKEN_ROUTER_CONFIG = {
    # Entropy threshold for routing decisions
    # Tokens with entropy below this go to short model
    "entropy_threshold": 0.3,
    # Target routing split (ideal: 80% short, 20% long)
    "target_short_ratio": 0.80,
    "target_long_ratio": 0.20,
    # Model mappings
    "models": {
        "short": {
            "default": "gemini-3.1-flash-lite-preview",
            "alternatives": ["gpt-4o-mini", "claude-3-haiku-20240307"],
            "cost_per_1k_tokens": 0.00015,
            "latency_ms": 50,
        },
        "long": {
            "default": "claude-3-5-sonnet-20241022",
            "alternatives": ["gpt-4o", "gemini-3.1-flash-lite-preview"],
            "cost_per_1k_tokens": 0.003,
            "latency_ms": 500,
        },
    },
    # Adaptive threshold settings
    "adaptive": {
        "enabled": True,
        "min_threshold": 0.1,
        "max_threshold": 0.5,
        "adjustment_rate": 0.01,
        "window_size": 100,  # Number of decisions to average
    },
    # Cost optimization
    "optimization": {
        "compute_savings_target": 0.82,  # 82% GPU savings target
        "latency_target_ms": 100,  # Target latency
        "quality_threshold": 0.95,  # Minimum quality retention
    },
}


class LongShortRouter:
    """Routes tokens between models based on entropy

    PRISM Algorithm:
    - Calculate token-level entropy from logits/probabilities
    - Low entropy (< threshold) → predictable → short model handles
    - High entropy (>= threshold) → uncertain → long model for deep reasoning

    Performance Targets:
    - 80% tokens to short model (7B)
    - 20% tokens to long model (full)
    - 82% GPU compute savings
    - 5.7× latency improvement

    Usage:
        router = LongShortRouter()
        decision = router.route(logits, context="code_review")
        result = await router.execute(decision, prompt)
    """

    def __init__(
        self,
        entropy_threshold: float = 0.3,
        short_model: str | None = None,
        long_model: str | None = None,
        config: dict | None = None,
    ):
        """Initialize Long⊗Short Router

        Args:
            entropy_threshold: Threshold for routing (0-1, normalized)
            short_model: Model ID for short/fast model
            long_model: Model ID for long/deep reasoning model
            config: Optional configuration override

        """
        self.config = config or TOKEN_ROUTER_CONFIG
        self.entropy_threshold = entropy_threshold or self.config["entropy_threshold"]

        # Model assignments
        self.short_model = short_model or self.config["models"]["short"]["default"]
        self.long_model = long_model or self.config["models"]["long"]["default"]

        # Statistics tracking
        self._stats = RoutingStats()
        self._entropy_history: list[float] = []
        self._decision_history: list[RoutingDecision] = []

        # Adaptive threshold
        self._adaptive_threshold = self.entropy_threshold

        logger.info(
            "token_router_initialized",
            entropy_threshold=self.entropy_threshold,
            short_model=self.short_model,
            long_model=self.long_model,
        )

    def calculate_entropy(
        self,
        logits_or_probs: list | np.ndarray | torch.Tensor,
        from_logits: bool = True,
        normalize: bool = True,
    ) -> float:
        """Calculate entropy from logits or probabilities

        Args:
            logits_or_probs: Model output logits or probability distribution
            from_logits: If True, apply softmax to convert logits to probs
            normalize: If True, normalize to [0, 1] range

        Returns:
            Entropy value (normalized if requested)

        """
        # Handle different input types
        if hasattr(logits_or_probs, "numpy"):
            # PyTorch tensor
            values = logits_or_probs.detach().cpu().numpy()
        elif hasattr(logits_or_probs, "__array__") or NUMPY_AVAILABLE:
            values = np.array(logits_or_probs)
        else:
            # Pure Python fallback
            values = list(logits_or_probs)
            return self._calculate_entropy_pure_python(values, from_logits, normalize)

        if not NUMPY_AVAILABLE:
            return self._calculate_entropy_pure_python(list(values), from_logits, normalize)

        # Ensure 1D
        if len(values.shape) > 1:
            values = values.flatten()

        # Convert logits to probabilities if needed
        if from_logits:
            # Softmax
            exp_values = np.exp(values - np.max(values))
            probs = exp_values / np.sum(exp_values)
        else:
            probs = values
            # Ensure valid probability distribution
            probs = probs / np.sum(probs)

        # Calculate entropy: -sum(p * log(p))
        # Avoid log(0) by adding small epsilon
        epsilon = 1e-10
        probs = np.clip(probs, epsilon, 1.0)
        entropy = -np.sum(probs * np.log(probs))

        # Normalize to [0, 1] if requested
        if normalize:
            max_entropy = np.log(len(probs))  # Maximum entropy for uniform distribution
            if max_entropy > 0:
                entropy = entropy / max_entropy

        return float(entropy)

    def _calculate_entropy_pure_python(
        self,
        values: list[float],
        from_logits: bool,
        normalize: bool,
    ) -> float:
        """Pure Python entropy calculation (no numpy)"""
        if from_logits:
            # Softmax
            max_val = max(values)
            exp_values = [math.exp(v - max_val) for v in values]
            sum_exp = sum(exp_values)
            probs = [e / sum_exp for e in exp_values]
        else:
            sum_vals = sum(values)
            probs = [v / sum_vals for v in values]

        # Entropy
        epsilon = 1e-10
        entropy = -sum(p * math.log(max(p, epsilon)) for p in probs)

        if normalize:
            max_entropy = math.log(len(probs))
            if max_entropy > 0:
                entropy = entropy / max_entropy

        return entropy

    def route(
        self,
        entropy: float | None = None,
        logits: list | np.ndarray | None = None,
        probs: list | np.ndarray | None = None,
        context: str | None = None,
        force_tier: ModelTier | None = None,
        num_tokens: int = 1,
    ) -> RoutingDecision:
        """Make routing decision based on entropy

        Args:
            entropy: Pre-calculated entropy value (0-1)
            logits: Model logits (will calculate entropy)
            probs: Probability distribution (will calculate entropy)
            context: Optional context hint for routing
            force_tier: Force specific tier (bypass entropy check)
            num_tokens: Number of tokens in this batch

        Returns:
            RoutingDecision with model assignment

        """
        # Calculate entropy if not provided
        if entropy is None:
            if logits is not None:
                entropy = self.calculate_entropy(logits, from_logits=True)
            elif probs is not None:
                entropy = self.calculate_entropy(probs, from_logits=False)
            else:
                # Default to mid-entropy (will use adaptive threshold)
                entropy = 0.5

        # Use adaptive threshold if enabled
        threshold = self._get_adaptive_threshold()

        # Determine tier
        if force_tier is not None:
            tier = force_tier
            reasoning = f"Forced to {force_tier.value} tier"
        elif entropy < threshold:
            tier = ModelTier.SHORT
            reasoning = f"Low entropy ({entropy:.3f} < {threshold:.3f}) → predictable token"
        else:
            tier = ModelTier.LONG
            reasoning = f"High entropy ({entropy:.3f} >= {threshold:.3f}) → uncertain token"

        # Context-based adjustments
        if context:
            tier, reasoning = self._apply_context_rules(tier, entropy, context, reasoning)

        # Get model for tier
        model_id = self.short_model if tier == ModelTier.SHORT else self.long_model

        # Calculate confidence (how far from threshold)
        distance_from_threshold = abs(entropy - threshold)
        confidence = min(1.0, distance_from_threshold / 0.3 + 0.5)

        # Create decision
        decision = RoutingDecision(
            tier=tier,
            model_id=model_id,
            entropy=entropy,
            threshold=threshold,
            confidence=confidence,
            tokens_routed=num_tokens,
            reasoning=reasoning,
            metadata={"context": context, "adaptive_threshold": self.config["adaptive"]["enabled"]},
        )

        # Update statistics
        self._update_stats(decision)

        logger.debug(
            "routing_decision",
            tier=tier.value,
            entropy=f"{entropy:.3f}",
            threshold=f"{threshold:.3f}",
            model=model_id,
        )

        return decision

    def route_batch(
        self,
        entropies: list[float],
        contexts: list[str] | None = None,
    ) -> list[RoutingDecision]:
        """Route a batch of tokens

        Args:
            entropies: List of entropy values for each token
            contexts: Optional contexts for each token

        Returns:
            List of routing decisions

        """
        decisions = []
        contexts = contexts or [None] * len(entropies)

        for entropy, context in zip(entropies, contexts, strict=False):
            decision = self.route(entropy=entropy, context=context)
            decisions.append(decision)

        return decisions

    def _apply_context_rules(
        self,
        tier: ModelTier,
        entropy: float,
        context: str,
        reasoning: str,
    ) -> tuple[ModelTier, str]:
        """Apply context-specific routing rules"""
        # Critical contexts always use long model
        critical_contexts = [
            "security",
            "legal",
            "financial",
            "safety",
            "atp_risk",
            "executive_review",
        ]

        if any(ctx in context.lower() for ctx in critical_contexts):
            return ModelTier.LONG, f"{reasoning} [OVERRIDE: critical context '{context}']"

        # Simple contexts prefer short model
        simple_contexts = ["summarize", "format", "extract", "classify", "translate"]

        if tier == ModelTier.LONG and any(ctx in context.lower() for ctx in simple_contexts):  # noqa: SIM102
            if entropy < 0.5:  # Only if not very high entropy
                return ModelTier.SHORT, f"{reasoning} [ADJUSTED: simple context '{context}']"

        return tier, reasoning

    def _get_adaptive_threshold(self) -> float:
        """Get adaptive threshold based on recent routing history"""
        if not self.config["adaptive"]["enabled"]:
            return self.entropy_threshold

        if len(self._entropy_history) < 10:
            return self.entropy_threshold

        # Get recent window
        window_size = self.config["adaptive"]["window_size"]
        recent = self._entropy_history[-window_size:]

        # Calculate current short ratio
        current_short_ratio = sum(1 for e in recent if e < self._adaptive_threshold) / len(recent)
        target_short_ratio = self.config["target_short_ratio"]

        # Adjust threshold
        adjustment_rate = self.config["adaptive"]["adjustment_rate"]

        if current_short_ratio < target_short_ratio - 0.05:
            # Too many going to long model, increase threshold
            self._adaptive_threshold = min(
                self.config["adaptive"]["max_threshold"],
                self._adaptive_threshold + adjustment_rate,
            )
        elif current_short_ratio > target_short_ratio + 0.05:
            # Too many going to short model, decrease threshold
            self._adaptive_threshold = max(
                self.config["adaptive"]["min_threshold"],
                self._adaptive_threshold - adjustment_rate,
            )

        return self._adaptive_threshold

    def _update_stats(self, decision: RoutingDecision):
        """Update routing statistics"""
        self._stats.total_tokens += decision.tokens_routed
        self._entropy_history.append(decision.entropy)
        self._decision_history.append(decision)

        if decision.tier == ModelTier.SHORT:
            self._stats.short_tokens += decision.tokens_routed
        else:
            self._stats.long_tokens += decision.tokens_routed

        # Update running average entropy
        if len(self._entropy_history) > 0:
            self._stats.average_entropy = sum(self._entropy_history) / len(self._entropy_history)

        # Calculate compute savings
        # Short model is ~10x cheaper than long model
        short_cost = self._stats.short_tokens * self.config["models"]["short"]["cost_per_1k_tokens"]
        long_cost = self._stats.long_tokens * self.config["models"]["long"]["cost_per_1k_tokens"]
        baseline_cost = (
            self._stats.total_tokens * self.config["models"]["long"]["cost_per_1k_tokens"]
        )

        if baseline_cost > 0:
            actual_cost = short_cost + long_cost
            self._stats.compute_savings_pct = (1 - actual_cost / baseline_cost) * 100

        # Limit history size
        max_history = 10000
        if len(self._entropy_history) > max_history:
            self._entropy_history = self._entropy_history[-max_history:]
            self._decision_history = self._decision_history[-max_history:]

    def get_stats(self) -> RoutingStats:
        """Get current routing statistics"""
        return self._stats

    def get_stats_dict(self) -> dict:
        """Get statistics as dictionary"""
        return self._stats.to_dict()

    def reset_stats(self):
        """Reset statistics"""
        self._stats = RoutingStats()
        self._entropy_history = []
        self._decision_history = []
        self._adaptive_threshold = self.entropy_threshold

    def estimate_cost(self, total_tokens: int) -> dict:
        """Estimate cost with Long⊗Short routing vs baseline

        Args:
            total_tokens: Total tokens to process

        Returns:
            Cost estimation dictionary

        """
        short_ratio = self.config["target_short_ratio"]
        self.config["target_long_ratio"]

        short_tokens = int(total_tokens * short_ratio)
        long_tokens = total_tokens - short_tokens

        short_cost = (short_tokens / 1000) * self.config["models"]["short"]["cost_per_1k_tokens"]
        long_cost = (long_tokens / 1000) * self.config["models"]["long"]["cost_per_1k_tokens"]
        total_cost = short_cost + long_cost

        baseline_cost = (total_tokens / 1000) * self.config["models"]["long"]["cost_per_1k_tokens"]
        savings = baseline_cost - total_cost
        savings_pct = (savings / baseline_cost) * 100 if baseline_cost > 0 else 0

        return {
            "total_tokens": total_tokens,
            "short_tokens": short_tokens,
            "long_tokens": long_tokens,
            "short_cost": short_cost,
            "long_cost": long_cost,
            "total_cost": total_cost,
            "baseline_cost": baseline_cost,
            "savings": savings,
            "savings_pct": savings_pct,
        }


class TokenRouterPipeline:
    """Pipeline wrapper for integrating Token Router with inference

    Provides high-level API for routing-aware inference
    """

    def __init__(
        self,
        router: LongShortRouter | None = None,
        short_client: Any | None = None,
        long_client: Any | None = None,
    ):
        """Initialize router pipeline

        Args:
            router: LongShortRouter instance
            short_client: Client for short model (e.g., Gemini Flash)
            long_client: Client for long model (e.g., Claude Sonnet)

        """
        self.router = router or LongShortRouter()
        self.short_client = short_client
        self.long_client = long_client

        logger.info(
            "token_router_pipeline_initialized",
            short_model=self.router.short_model,
            long_model=self.router.long_model,
        )

    async def infer(
        self,
        prompt: str,
        context: str | None = None,
        estimate_entropy: bool = True,
    ) -> dict:
        """Run inference with automatic routing

        Args:
            prompt: Input prompt
            context: Context hint for routing
            estimate_entropy: Estimate entropy from prompt characteristics

        Returns:
            Inference result with routing metadata

        """
        # Estimate entropy from prompt characteristics
        if estimate_entropy:
            entropy = self._estimate_prompt_entropy(prompt)
        else:
            entropy = 0.5  # Default

        # Get routing decision
        decision = self.router.route(
            entropy=entropy,
            context=context,
            num_tokens=len(prompt.split()),
        )

        # Execute on appropriate model
        if decision.tier == ModelTier.SHORT:
            model = self.router.short_model
        else:
            model = self.router.long_model

        # Return placeholder result (actual inference would use the client)
        return {
            "routing": decision.to_dict(),
            "model": model,
            "prompt_length": len(prompt),
            "estimated_entropy": entropy,
        }

    def _estimate_prompt_entropy(self, prompt: str) -> float:
        """Estimate entropy from prompt characteristics

        Heuristics:
        - Short, structured prompts → low entropy
        - Long, complex prompts → high entropy
        - Questions/ambiguity markers → higher entropy
        """
        # Base entropy from length
        words = len(prompt.split())
        length_entropy = min(1.0, words / 500)  # Longer = higher entropy

        # Question/uncertainty markers
        uncertainty_markers = [
            "?",
            "why",
            "how",
            "what if",
            "could",
            "might",
            "unclear",
            "uncertain",
            "complex",
            "analyze",
        ]
        prompt_lower = prompt.lower()
        uncertainty_count = sum(1 for m in uncertainty_markers if m in prompt_lower)
        uncertainty_entropy = min(1.0, uncertainty_count * 0.1)

        # Structure markers (reduce entropy)
        structure_markers = [
            "list",
            "summarize",
            "extract",
            "format",
            "convert",
            "translate",
            "classify",
        ]
        structure_count = sum(1 for m in structure_markers if m in prompt_lower)
        structure_reduction = min(0.3, structure_count * 0.1)

        # Combine
        estimated_entropy = (length_entropy * 0.4 + uncertainty_entropy * 0.6) - structure_reduction
        return max(0.0, min(1.0, estimated_entropy))

    def generate_report(self) -> str:
        """Generate routing performance report"""
        stats = self.router.get_stats()

        report = f"""
# Token Router Performance Report
Generated: {datetime.now().isoformat()}

## Routing Statistics
- Total Tokens: {stats.total_tokens:,}
- Short Model Tokens: {stats.short_tokens:,} ({stats.short_ratio * 100:.1f}%)
- Long Model Tokens: {stats.long_tokens:,} ({stats.long_ratio * 100:.1f}%)

## Performance
- Average Entropy: {stats.average_entropy:.3f}
- Compute Savings: {stats.compute_savings_pct:.1f}%

## Model Assignment
- Short Model: {self.router.short_model}
- Long Model: {self.router.long_model}
- Entropy Threshold: {self.router.entropy_threshold}
- Adaptive Threshold: {self.router._adaptive_threshold:.3f}

## Cost Estimation (per 1M tokens)
{self._format_cost_estimate(1_000_000)}
"""
        return report.strip()

    def _format_cost_estimate(self, tokens: int) -> str:
        """Format cost estimate as string"""
        estimate = self.router.estimate_cost(tokens)
        return f"""
- Baseline Cost: ${estimate["baseline_cost"]:.2f}
- Optimized Cost: ${estimate["total_cost"]:.2f}
- Savings: ${estimate["savings"]:.2f} ({estimate["savings_pct"]:.1f}%)
""".strip()


# Convenience functions
def route_token(
    entropy: float,
    threshold: float = 0.3,
    context: str | None = None,
) -> RoutingDecision:
    """Quick token routing

    Usage:
        decision = route_token(0.25)  # Low entropy → short model
        decision = route_token(0.75)  # High entropy → long model
    """
    router = LongShortRouter(entropy_threshold=threshold)
    return router.route(entropy=entropy, context=context)


def calculate_token_entropy(logits: list | np.ndarray) -> float:
    """Calculate entropy from logits

    Usage:
        entropy = calculate_token_entropy([1.2, 0.5, -0.3, 0.8])
    """
    router = LongShortRouter()
    return router.calculate_entropy(logits, from_logits=True)


def estimate_routing_cost(total_tokens: int, short_ratio: float = 0.8) -> dict:
    """Estimate routing cost savings

    Usage:
        cost = estimate_routing_cost(1_000_000)
        print(f"Savings: ${cost['savings']:.2f}")
    """
    router = LongShortRouter()
    return router.estimate_cost(total_tokens)
