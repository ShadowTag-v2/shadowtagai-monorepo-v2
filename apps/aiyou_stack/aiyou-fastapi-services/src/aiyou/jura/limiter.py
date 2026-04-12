"""
JuraLimiter: Enforces tier-based constraints on agent assignments.

Each tier has limits on:
- Maximum agents
- Response time
- Cost per request
- Allowed LLM models
- Agent pool
"""

from dataclasses import dataclass
from typing import Any

from .classifier import CostTier


@dataclass
class TierLimits:
    """Constraints for a cost tier."""

    max_agents: int
    max_response_time_ms: int
    max_cost_usd: float
    models: list[str]
    agent_pool: str  # "worker", "execution", "strategy"


class JuraLimiter:
    """
    Enforces tier-based constraints on request routing.

    Tier allocation:
    - FREE: 180 worker agents (30% of 600)
    - FLASH: 360 execution agents (60% of 600)
    - PRO: 60 strategy agents (10% of 600)
    """

    TIER_LIMITS: dict[CostTier, TierLimits] = {
        CostTier.FREE: TierLimits(
            max_agents=1,
            max_response_time_ms=5000,
            max_cost_usd=0.001,
            models=["grok-2"],
            agent_pool="worker",
        ),
        CostTier.FLASH: TierLimits(
            max_agents=3,
            max_response_time_ms=2000,
            max_cost_usd=0.01,
            models=[
                "gemini-2.5-flash-preview-05-20",  # Primary: Gemini 2.5 Flash Preview
                "gemini-2.0-flash",  # Fallback 1
                "gemini-2.0-flash-lite",  # Fallback 2 (rate limit)
            ],
            agent_pool="execution",
        ),
        CostTier.PRO: TierLimits(
            max_agents=8,
            max_response_time_ms=10000,
            max_cost_usd=1.0,
            models=[
                "gemini-2.5-pro-preview-06-05",  # Primary: Gemini 2.5 Pro Preview
                "claude-sonnet-4-20250514",  # Fallback 1: Claude Sonnet 4
                "gemini-2.0-flash",  # Fallback 2 (rate limit)
            ],
            agent_pool="strategy",
        ),
    }

    # Agent pool sizes (out of 600 total)
    POOL_SIZES = {
        "worker": 180,  # FREE tier
        "execution": 360,  # FLASH tier
        "strategy": 60,  # PRO tier
    }

    def __init__(self):
        # Track current usage per tier
        self._active_requests: dict[CostTier, int] = {
            CostTier.FREE: 0,
            CostTier.FLASH: 0,
            CostTier.PRO: 0,
        }

    def get_limits(self, tier: CostTier) -> TierLimits:
        """Get limits for a tier."""
        if tier == CostTier.AUTO:
            raise ValueError("Cannot get limits for AUTO tier")
        return self.TIER_LIMITS[tier]

    def check_availability(self, tier: CostTier, requested_agents: int = 1) -> tuple[bool, str]:
        """
        Check if a tier has capacity for a request.

        Args:
            tier: The cost tier
            requested_agents: Number of agents requested

        Returns:
            (available, reason) tuple
        """
        if tier == CostTier.AUTO:
            return False, "AUTO tier must be resolved first"

        limits = self.TIER_LIMITS[tier]

        # Check agent count
        if requested_agents > limits.max_agents:
            return False, f"Requested {requested_agents} agents, tier limit is {limits.max_agents}"

        # Check pool capacity (simplified - actual would check real agent availability)
        pool_size = self.POOL_SIZES[limits.agent_pool]
        if requested_agents > pool_size:
            return (
                False,
                f"Pool {limits.agent_pool} has {pool_size} agents, requested {requested_agents}",
            )

        return True, "Available"

    def clamp_agents(self, tier: CostTier, requested: int) -> int:
        """
        Clamp requested agent count to tier limits.

        Args:
            tier: The cost tier
            requested: Number of agents requested

        Returns:
            Clamped agent count
        """
        if tier == CostTier.AUTO:
            return requested
        limits = self.TIER_LIMITS[tier]
        return min(max(1, requested), limits.max_agents)

    def get_timeout_ms(self, tier: CostTier) -> int:
        """Get timeout for a tier in milliseconds."""
        if tier == CostTier.AUTO:
            return 5000  # Default
        return self.TIER_LIMITS[tier].max_response_time_ms

    def get_allowed_models(self, tier: CostTier) -> list[str]:
        """Get allowed LLM models for a tier."""
        if tier == CostTier.AUTO:
            return []
        return self.TIER_LIMITS[tier].models

    def get_primary_model(self, tier: CostTier) -> str:
        """Get the primary (first) model for a tier."""
        models = self.get_allowed_models(tier)
        return models[0] if models else "gemini-2.0-flash"

    def get_fallback_model(self, tier: CostTier, failed_model: str) -> str | None:
        """
        Get next fallback model when primary is rate limited.

        Args:
            tier: The cost tier
            failed_model: The model that was rate limited

        Returns:
            Next model in fallback chain, or None if exhausted
        """
        models = self.get_allowed_models(tier)
        if not models:
            return None

        try:
            idx = models.index(failed_model)
            if idx + 1 < len(models):
                return models[idx + 1]
        except ValueError:
            # Model not found, return first available
            return models[0]

        return None

    def get_model_with_fallback(self, tier: CostTier, rate_limited: list[str] = None) -> str:
        """
        Get best available model, skipping rate-limited ones.

        Args:
            tier: The cost tier
            rate_limited: List of rate-limited model names

        Returns:
            Best available model
        """
        rate_limited = rate_limited or []
        models = self.get_allowed_models(tier)

        for model in models:
            if model not in rate_limited:
                return model

        # All rate limited - return last fallback anyway
        return models[-1] if models else "gemini-2.0-flash"

    def estimate_cost(self, tier: CostTier, input_tokens: int, output_tokens: int) -> float:
        """
        Estimate cost for a request based on tier.

        Pricing (per 1M tokens):
        - Grok-2: $2.00 input, $10.00 output
        - Gemini Flash: $0.075 input, $0.30 output
        - Gemini Pro: $1.25 input, $10.00 output
        - Claude Sonnet: $3.00 input, $15.00 output
        """
        pricing = {
            CostTier.FREE: {"input": 2.00, "output": 10.00},  # Grok
            CostTier.FLASH: {"input": 0.075, "output": 0.30},  # Gemini Flash
            CostTier.PRO: {"input": 1.25, "output": 10.00},  # Gemini Pro (avg)
        }

        if tier == CostTier.AUTO:
            tier = CostTier.FLASH  # Default estimate

        rates = pricing[tier]
        cost = (input_tokens * rates["input"] + output_tokens * rates["output"]) / 1_000_000
        return cost

    def check_cost_limit(self, tier: CostTier, estimated_cost: float) -> tuple[bool, str]:
        """
        Check if estimated cost is within tier limits.

        Args:
            tier: The cost tier
            estimated_cost: Estimated cost in USD

        Returns:
            (within_limit, reason) tuple
        """
        if tier == CostTier.AUTO:
            return True, "AUTO tier - no cost limit"

        limits = self.TIER_LIMITS[tier]
        if estimated_cost > limits.max_cost_usd:
            return (
                False,
                f"Estimated ${estimated_cost:.4f} exceeds tier limit ${limits.max_cost_usd}",
            )
        return True, f"Within limit (${estimated_cost:.4f} <= ${limits.max_cost_usd})"

    def get_pool_stats(self) -> dict[str, Any]:
        """Get current pool statistics."""
        return {
            "pools": self.POOL_SIZES,
            "active_requests": dict(self._active_requests),
            "tier_limits": {
                tier.value: {
                    "max_agents": limits.max_agents,
                    "timeout_ms": limits.max_response_time_ms,
                    "max_cost": limits.max_cost_usd,
                    "primary_model": limits.models[0] if limits.models else None,
                }
                for tier, limits in self.TIER_LIMITS.items()
            },
        }
