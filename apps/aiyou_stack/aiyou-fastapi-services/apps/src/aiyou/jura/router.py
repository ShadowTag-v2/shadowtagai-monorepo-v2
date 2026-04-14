"""JuraRouter: Orchestrates cost-aware request routing.

Combines:
- JuraClassifier for tier assignment
- JuraLimiter for constraint enforcement
- JuraCostTracker for cost accounting
"""

import asyncio
import logging
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

from .classifier import CostTier, JuraClassifier
from .cost_tracker import JuraCostTracker
from .limiter import JuraLimiter

logger = logging.getLogger(__name__)


@dataclass
class RouteResult:
    """Result of routing a request through JURA."""

    request_id: str
    tier: CostTier
    classification_reason: str
    agent_ids: list[str]
    model_used: str
    response: Any
    cost_usd: float
    latency_ms: int
    success: bool
    error: str | None = None


class JuraRouter:
    """Main orchestrator for JURA protocol.

    Usage:
        router = JuraRouter()
        result = await router.route(
            task="Analyze this code",
            context_size=500,
            cost_tier=CostTier.AUTO
        )
    """

    def __init__(
        self,
        classifier: JuraClassifier | None = None,
        limiter: JuraLimiter | None = None,
        cost_tracker: JuraCostTracker | None = None,
    ):
        self.classifier = classifier or JuraClassifier()
        self.limiter = limiter or JuraLimiter()
        self.cost_tracker = cost_tracker or JuraCostTracker()

        # Agent executor (to be wired to n-autoresearch/Kosmos/BioAgents)
        self._executor: Callable[[str, int, str, int], Awaitable[dict[str, Any]]] | None = None

    def set_executor(
        self, executor: Callable[[str, int, str, int], Awaitable[dict[str, Any]]],
    ) -> None:
        """Set the agent executor function.

        Args:
            executor: Async function(task, num_agents, model, timeout_ms) -> response

        """
        self._executor = executor

    async def route(
        self,
        task: str,
        context_size: int = 0,
        task_type: str = "execution",
        cost_tier: CostTier = CostTier.AUTO,
        requested_agents: int = 1,
        metadata: dict[str, Any] | None = None,
    ) -> RouteResult:
        """Route a request through JURA protocol.

        Args:
            task: The task/prompt to execute
            context_size: Number of context tokens
            task_type: "execution" or "governance"
            cost_tier: Requested tier (AUTO for automatic)
            requested_agents: Number of agents requested
            metadata: Additional metadata

        Returns:
            RouteResult with response, cost, and metrics

        """
        start_time = time.time()
        request_id = f"jura_{int(start_time * 1000)}"

        # 1. Classify into tier
        classification = self.classifier.classify(
            task=task,
            context_size=context_size,
            task_type=task_type,
            override=cost_tier if cost_tier != CostTier.AUTO else None,
        )
        tier = classification.tier
        logger.debug(f"Classified to {tier.value}: {classification.reason}")

        # 2. Apply tier limits
        clamped_agents = self.limiter.clamp_agents(tier, requested_agents)
        timeout_ms = self.limiter.get_timeout_ms(tier)
        model = self.limiter.get_primary_model(tier)

        # 3. Check availability
        available, avail_reason = self.limiter.check_availability(tier, clamped_agents)
        if not available:
            return RouteResult(
                request_id=request_id,
                tier=tier,
                classification_reason=classification.reason,
                agent_ids=[],
                model_used=model,
                response=None,
                cost_usd=0.0,
                latency_ms=int((time.time() - start_time) * 1000),
                success=False,
                error=f"Tier unavailable: {avail_reason}",
            )

        # 4. Execute (or mock if no executor)
        agent_ids = []
        response = None
        error = None
        success = True
        input_tokens = context_size + len(task) // 4
        output_tokens = 0

        try:
            if self._executor:
                # Real execution via n-autoresearch/Kosmos/BioAgents
                exec_result = await asyncio.wait_for(
                    self._executor(task, clamped_agents, model, timeout_ms),
                    timeout=timeout_ms / 1000 + 1,  # Add 1s buffer
                )
                response = exec_result.get("response")
                agent_ids = exec_result.get("agent_ids", [])
                output_tokens = exec_result.get("output_tokens", 500)
            else:
                # Mock execution for testing
                await asyncio.sleep(0.01)  # Simulate work
                response = {
                    "message": f"Mock response for {tier.value} tier",
                    "model": model,
                    "agents": clamped_agents,
                }
                agent_ids = [f"mock_agent_{i}" for i in range(clamped_agents)]
                output_tokens = 500

        except TimeoutError:
            success = False
            error = f"Timeout after {timeout_ms}ms"
            logger.warning(f"Request {request_id} timed out")
        except Exception as e:
            success = False
            error = str(e)
            logger.error(f"Request {request_id} failed: {e}")

        # 5. Calculate cost
        latency_ms = int((time.time() - start_time) * 1000)
        cost_usd = self.limiter.estimate_cost(tier, input_tokens, output_tokens)

        # 6. Record cost
        self.cost_tracker.record(
            tier=tier,
            agent_ids=agent_ids,
            model_used=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost_usd,
            latency_ms=latency_ms,
            success=success,
            task_type=task_type,
            metadata=metadata,
        )

        return RouteResult(
            request_id=request_id,
            tier=tier,
            classification_reason=classification.reason,
            agent_ids=agent_ids,
            model_used=model,
            response=response,
            cost_usd=cost_usd,
            latency_ms=latency_ms,
            success=success,
            error=error,
        )

    async def route_governance(
        self,
        task: str,
        context_size: int = 0,
        metadata: dict[str, Any] | None = None,
    ) -> RouteResult:
        """Route a governance request (always uses PRO tier).

        Args:
            task: The governance task
            context_size: Number of context tokens
            metadata: Additional metadata

        Returns:
            RouteResult

        """
        return await self.route(
            task=task,
            context_size=context_size,
            task_type="governance",
            cost_tier=CostTier.PRO,
            requested_agents=5,  # Governance gets more agents
            metadata=metadata,
        )

    def get_stats(self) -> dict[str, Any]:
        """Get current JURA statistics."""
        return {
            "cost_metrics": self.cost_tracker.get_metrics(),
            "pool_stats": self.limiter.get_pool_stats(),
            "tier_configs": {
                tier.value: {
                    "max_agents": limits.max_agents,
                    "timeout_ms": limits.max_response_time_ms,
                    "max_cost": limits.max_cost_usd,
                    "models": limits.models,
                }
                for tier, limits in self.limiter.TIER_LIMITS.items()
            },
        }

    def get_tier_recommendation(self, task: str, context_size: int = 0) -> dict[str, Any]:
        """Get tier recommendation without routing.

        Useful for showing users what tier would be selected.
        """
        classification = self.classifier.classify(
            task=task,
            context_size=context_size,
            task_type="execution",
        )

        limits = self.limiter.get_limits(classification.tier)

        return {
            "recommended_tier": classification.tier.value,
            "reason": classification.reason,
            "complexity_score": classification.complexity_score,
            "context_tokens": classification.context_tokens,
            "tier_limits": {
                "max_agents": limits.max_agents,
                "timeout_ms": limits.max_response_time_ms,
                "max_cost": limits.max_cost_usd,
                "primary_model": limits.models[0] if limits.models else None,
            },
        }
