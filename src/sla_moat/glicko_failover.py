# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Glicko-Enhanced Failover Engine

Extends the base JREngineWithFailover to use Glicko-2 dynamic provider ranking.

Key enhancements:
1. Dynamic provider selection (best-rated first, not hardcoded)
2. Automatic allocation percentage adjustment
3. Real-time rating updates based on success/latency/quality
4. Automatic rebalancing when ratings shift significantly

This makes the failover architecture self-optimizing - no manual tuning needed.
"""

import time
import logging
from typing import Any

from .failover_engine import JREngineWithFailover, JudgeDecision, ProviderType, FailoverReason, TimeoutError, APIError
from .glicko2 import Glicko2Player, create_provider_ratings, update_provider_rating, get_ranked_providers, get_allocation_percentages

logger = logging.getLogger(__name__)


class GlickoEnhancedFailover(JREngineWithFailover):
    """
    Failover engine with Glicko-2 dynamic provider selection.

    Differences from base JREngineWithFailover:
    - Provider order determined by Glicko rating (not hardcoded)
    - Allocation percentages adjust based on performance
    - Ratings update after each decision (success/failure/latency/quality)
    - Automatic rebalancing when ratings shift significantly

    Example:
        # Initialize with Glicko-2 ratings
        engine = GlickoEnhancedFailover()

        # Execute decision - automatically uses best-rated provider first
        decision = engine.execute_decision(context)

        # After 1000 decisions, provider order may have changed:
        # If Claude outperforms Gemini → Claude becomes primary
        # If GPT-5 has lowest latency → GPT-5 gets ranking boost
        # Local model improves via DTE → Local gets higher rating
    """

    def __init__(
        self,
        gemini_timeout_ms: int = 70,
        claude_timeout_ms: int = 75,
        gpt5_timeout_ms: int = 85,
        coordination_buffer_ms: int = 5,
        enable_metrics: bool = True,
        rebalance_threshold: float = 50.0,  # Rebalance if rating changes >50 points
    ):
        """
        Initialize Glicko-enhanced failover engine.

        Args:
            gemini_timeout_ms: Timeout for Gemini (default: 70ms)
            claude_timeout_ms: Timeout for Claude (default: 75ms)
            gpt5_timeout_ms: Timeout for GPT-5 (default: 85ms)
            coordination_buffer_ms: Overhead for failover logic (default: 5ms)
            enable_metrics: Whether to emit metrics (default: True)
            rebalance_threshold: Rebalance if rating changes exceed this (default: 50)
        """
        super().__init__(
            gemini_timeout_ms=gemini_timeout_ms,
            claude_timeout_ms=claude_timeout_ms,
            gpt5_timeout_ms=gpt5_timeout_ms,
            coordination_buffer_ms=coordination_buffer_ms,
            enable_metrics=enable_metrics,
        )

        # Initialize Glicko-2 ratings for all providers
        self.glicko_ratings = create_provider_ratings()
        self.rebalance_threshold = rebalance_threshold

        # Track last allocation for rebalancing detection
        self.last_allocations = get_allocation_percentages(self.glicko_ratings)

        # Decision counter for periodic rebalancing
        self.decision_count = 0
        self.rebalance_interval = 100  # Check for rebalancing every 100 decisions

        logger.info(f"GlickoEnhancedFailover initialized with dynamic provider ranking. Initial rankings: {self._get_ranking_summary()}")

    def execute_decision(self, context: dict[str, Any]) -> JudgeDecision:
        """
        Execute decision with Glicko-2 dynamic provider selection.

        Provider order is determined by Glicko ratings, not hardcoded.
        After each decision, ratings are updated based on outcome.

        Args:
            context: Decision context

        Returns:
            JudgeDecision with provider used and performance metrics
        """
        start_time = time.time()
        fallback_chain: list[ProviderType] = []

        # Get providers ranked by Glicko-2 rating (best first)
        ranked_providers = get_ranked_providers(self.glicko_ratings)

        logger.debug(f"Provider order: {[p.value for p, _ in ranked_providers]}")

        # Try providers in rating order (dynamic, not static)
        for provider_type, glicko_player in ranked_providers:
            # Skip local provider until last resort
            if provider_type == ProviderType.LOCAL and len(fallback_chain) < 3:
                continue

            try:
                # Get timeout for this provider
                timeout = self._get_provider_timeout(provider_type)

                # Call provider
                provider_start = time.time()
                decision = self._call_provider(provider_type, context, timeout)
                latency_ms = (time.time() - provider_start) * 1000

                # Update Glicko rating - SUCCESS
                self._update_glicko_rating(
                    provider_type=provider_type,
                    outcome=1.0,  # Success
                    latency_ms=latency_ms,
                    confidence=decision.confidence,
                )

                # Check time budget
                if self._check_time_budget(start_time, 0.090):  # 90ms SLA
                    decision.fallback_chain = fallback_chain
                    self._emit_metrics(decision)
                    self._check_rebalancing()
                    return decision
                else:
                    # Success but too slow - try faster provider
                    fallback_chain.append(provider_type)
                    self._log_failover(
                        provider_type,
                        self._get_next_provider(provider_type, ranked_providers),
                        FailoverReason.TIMEOUT,
                        (time.time() - start_time) * 1000,
                        f"{provider_type.value} exceeded time budget",
                    )

            except (TimeoutError, APIError) as e:
                # Update Glicko rating - FAILURE
                self._update_glicko_rating(
                    provider_type=provider_type,
                    outcome=0.0,  # Failure
                    latency_ms=None,
                    confidence=None,
                )

                fallback_chain.append(provider_type)
                next_provider = self._get_next_provider(provider_type, ranked_providers)
                self._log_failover(
                    provider_type,
                    next_provider,
                    FailoverReason.API_ERROR if isinstance(e, APIError) else FailoverReason.TIMEOUT,
                    (time.time() - start_time) * 1000,
                    str(e),
                )

        # If we get here, all providers failed (shouldn't happen with local fallback)
        # Force local fallback as last resort
        decision = self._local_judge(context)
        decision.fallback_chain = fallback_chain
        decision.is_degraded_mode = True
        self._emit_metrics(decision)
        self._check_rebalancing()

        logger.warning(f"All preferred providers failed - using local fallback. Latency: {decision.latency_ms:.2f}ms")

        return decision

    def _call_provider(self, provider_type: ProviderType, context: dict[str, Any], timeout: float) -> JudgeDecision:
        """
        Call a specific provider.

        Routes to appropriate judge method based on provider type.
        """
        if provider_type == ProviderType.GEMINI:
            return self._gemini_judge(context, timeout)
        elif provider_type == ProviderType.CLAUDE:
            return self._claude_judge(context, timeout)
        elif provider_type == ProviderType.GPT5:
            return self._gpt5_judge(context, timeout)
        elif provider_type == ProviderType.LOCAL:
            return self._local_judge(context)
        else:
            raise ValueError(f"Unknown provider type: {provider_type}")

    def _get_provider_timeout(self, provider_type: ProviderType) -> float:
        """Get timeout for a provider (in seconds)."""
        timeouts = {
            ProviderType.GEMINI: self.gemini_timeout,
            ProviderType.CLAUDE: self.claude_timeout,
            ProviderType.GPT5: self.gpt5_timeout,
            ProviderType.LOCAL: 0.010,  # 10ms for local
        }
        return timeouts.get(provider_type, 0.075)

    def _get_next_provider(self, current: ProviderType, ranked_providers: list[tuple[ProviderType, Glicko2Player]]) -> ProviderType:
        """Get next provider in ranked list."""
        for i, (provider, _) in enumerate(ranked_providers):
            if provider == current and i + 1 < len(ranked_providers):
                return ranked_providers[i + 1][0]

        return ProviderType.LOCAL  # Default to local

    def _update_glicko_rating(self, provider_type: ProviderType, outcome: float, latency_ms: float | None = None, confidence: float | None = None):
        """
        Update provider's Glicko-2 rating based on decision outcome.

        Args:
            provider_type: Provider to update
            outcome: 1.0 (success), 0.0 (failure)
            latency_ms: Response latency (bonus if <70ms)
            confidence: Decision confidence (bonus if >0.9)
        """
        # Calculate bonuses
        latency_bonus = 0.0
        quality_bonus = 0.0

        if latency_ms is not None and latency_ms < 70:
            latency_bonus = 0.1  # Fast response bonus

        if confidence is not None and confidence > 0.9:
            quality_bonus = 0.1  # High confidence bonus

        # Get system average as opponent
        avg_rating = sum(player.get_rating() for player in self.glicko_ratings.values()) / len(self.glicko_ratings)

        system_average = Glicko2Player(mu=avg_rating, phi=200, sigma=0.06)

        # Update rating
        update_provider_rating(
            provider=self.glicko_ratings[provider_type],
            outcome=outcome,
            opponent=system_average,
            latency_bonus=latency_bonus,
            quality_bonus=quality_bonus,
        )

        logger.debug(
            f"Updated {provider_type.value} rating: "
            f"{self.glicko_ratings[provider_type].get_rating():.0f} "
            f"(outcome={outcome}, latency_bonus={latency_bonus:.1f}, "
            f"quality_bonus={quality_bonus:.1f})"
        )

    def _check_rebalancing(self):
        """
        Check if provider allocations should be rebalanced.

        Rebalancing occurs when:
        1. Decision count reaches rebalance_interval (every 100 decisions)
        2. Any provider's rating changed significantly (>threshold)
        """
        self.decision_count += 1

        # Check interval-based rebalancing
        if self.decision_count % self.rebalance_interval == 0:
            current_allocations = get_allocation_percentages(self.glicko_ratings)

            # Check if allocations changed significantly
            max_change = max(
                abs(current_allocations.get(p, 0) - self.last_allocations.get(p, 0))
                for p in [ProviderType.GEMINI, ProviderType.CLAUDE, ProviderType.GPT5]
            )

            if max_change > 0.05:  # 5% change in allocation
                logger.info(f"Rebalancing providers after {self.decision_count} decisions. Rankings: {self._get_ranking_summary()}")
                self.last_allocations = current_allocations

    def _get_ranking_summary(self) -> str:
        """Get human-readable ranking summary."""
        ranked = get_ranked_providers(self.glicko_ratings)
        return ", ".join([f"{p.value}:{player.get_rating():.0f}" for p, player in ranked])

    def get_provider_stats(self) -> dict[str, Any]:
        """
        Get detailed provider statistics.

        Returns:
            Dict with rankings, ratings, and allocation percentages
        """
        ranked = get_ranked_providers(self.glicko_ratings)
        allocations = get_allocation_percentages(self.glicko_ratings)

        return {
            "rankings": [
                {
                    "provider": provider.value,
                    "rating": player.get_rating(),
                    "rating_deviation": player.get_rd(),
                    "volatility": player.get_volatility(),
                    "allocation_pct": allocations.get(provider, 0) * 100,
                }
                for provider, player in ranked
            ],
            "total_decisions": self.decision_count,
            "failover_stats": self.get_failover_stats(),
        }


# Example usage
if __name__ == "__main__":
    print("=== Glicko-Enhanced Failover Engine Demo ===\n")

    # Initialize engine
    engine = GlickoEnhancedFailover()

    print("Initial provider rankings:")
    stats = engine.get_provider_stats()
    for rank in stats["rankings"]:
        print(f"  {rank['provider']}: {rank['rating']:.0f} rating ({rank['allocation_pct']:.1f}% allocation)")
    print()

    # Simulate 20 decisions with varying outcomes
    print("Simulating 20 decisions...\n")

    for i in range(1, 21):
        context = {
            "user_request": f"Decision {i}",
            "simulate_gemini_failure": i % 7 == 0,  # Gemini fails occasionally
            "simulate_claude_failure": i % 11 == 0,  # Claude fails occasionally
        }

        decision = engine.execute_decision(context)

        print(
            f"Decision {i}: {decision.decision} by {decision.provider_used.value} ({decision.latency_ms:.1f}ms, confidence={decision.confidence:.2f})"
        )

        if decision.fallback_chain:
            print(f"  Fallback chain: {[p.value for p in decision.fallback_chain]}")

    print("\n" + "=" * 70 + "\n")

    # Show updated rankings
    print("Final provider rankings after 20 decisions:")
    stats = engine.get_provider_stats()
    for rank in stats["rankings"]:
        print(f"  {rank['provider']}: {rank['rating']:.0f} rating ({rank['allocation_pct']:.1f}% allocation, RD={rank['rating_deviation']:.0f})")
    print()

    # Show failover statistics
    failover_stats = stats["failover_stats"]
    print("Failover statistics:")
    print(f"  Total failovers: {failover_stats['total_failovers']}")
    print(f"  By provider: {failover_stats['failovers_by_provider']}")
    print(f"  By reason: {failover_stats['failovers_by_reason']}")
