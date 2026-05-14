# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
MAD-Enhanced Decision Engine

Integrates Multi-Agent Debates (MAD) for critical production decisions.

When decisions are high-risk (production deployments, security approvals,
financial transactions), use MAD consensus instead of single-provider risk:

1. Query all providers in parallel (Gemini, Claude, GPT-5)
2. Check for unanimous consensus (fast path)
3. If split, run debate round
4. Weight votes by Glicko-2 ratings
5. Return majority decision with transparent reasoning

This provides:
- Reduced single-provider bias
- Higher confidence through multi-expert consensus
- Transparent decision-making (all reasoning visible)
- Glicko-weighted expertise (best providers matter more)
"""

import time
import logging
from typing import Any

from .failover_engine import JudgeDecision, ProviderType
from .glicko_failover import GlickoEnhancedFailover
from .mad_consensus import MADEngine, MADConsensus, DecisionType
from .glicko2 import Glicko2Player

logger = logging.getLogger(__name__)


class MADDecisionEngine(GlickoEnhancedFailover):
    """
    Decision engine that uses MAD consensus for critical decisions.

    Extends GlickoEnhancedFailover to add MAD consensus capability:
    - Routine decisions: Use Glicko-enhanced failover (fast, single provider)
    - Critical decisions: Use MAD consensus (slower, multi-provider)

    Decision is "critical" if:
    1. Risk level is "high" or "critical" (user-specified)
    2. User explicitly requests multi-agent review
    3. Decision type matches critical patterns (production deploy, security, financial)

    Example:
        engine = MADDecisionEngine()

        # Routine decision (Glicko failover)
        decision = engine.execute_decision({
            "user_request": "Update user profile",
            "risk_level": "low"
        })
        # Uses best-rated provider, fast response

        # Critical decision (MAD consensus)
        decision = engine.execute_decision({
            "user_request": "Deploy to production",
            "risk_level": "high"
        })
        # Queries all 3 providers, runs debate, weighted voting
    """

    def __init__(
        self,
        gemini_timeout_ms: int = 70,
        claude_timeout_ms: int = 75,
        gpt5_timeout_ms: int = 85,
        coordination_buffer_ms: int = 5,
        enable_metrics: bool = True,
        rebalance_threshold: float = 50.0,
        mad_max_debate_rounds: int = 2,
        mad_require_unanimity: bool = False,
    ):
        """
        Initialize MAD decision engine.

        Args:
            gemini_timeout_ms: Timeout for Gemini (default: 70ms)
            claude_timeout_ms: Timeout for Claude (default: 75ms)
            gpt5_timeout_ms: Timeout for GPT-5 (default: 85ms)
            coordination_buffer_ms: Overhead for failover (default: 5ms)
            enable_metrics: Whether to emit metrics (default: True)
            rebalance_threshold: Glicko rebalancing threshold (default: 50)
            mad_max_debate_rounds: Max MAD debate rounds (default: 2)
            mad_require_unanimity: Require unanimous MAD consensus (default: False)
        """
        super().__init__(
            gemini_timeout_ms=gemini_timeout_ms,
            claude_timeout_ms=claude_timeout_ms,
            gpt5_timeout_ms=gpt5_timeout_ms,
            coordination_buffer_ms=coordination_buffer_ms,
            enable_metrics=enable_metrics,
            rebalance_threshold=rebalance_threshold,
        )

        # Initialize MAD engine
        # Create mock agents dict (in production, these would be real LLM clients)
        self.mad_agents = {
            "gemini": self,  # Use self for agent calls
            "claude": self,
            "gpt5": self,
        }

        # Map Glicko ratings to agent IDs
        self.mad_glicko_ratings = {
            "gemini": self.glicko_ratings[ProviderType.GEMINI].get_rating(),
            "claude": self.glicko_ratings[ProviderType.CLAUDE].get_rating(),
            "gpt5": self.glicko_ratings[ProviderType.GPT5].get_rating(),
        }

        self.mad_engine = MADEngine(
            agents=self.mad_agents,
            glicko_ratings=self.mad_glicko_ratings,
            max_debate_rounds=mad_max_debate_rounds,
            require_unanimity=mad_require_unanimity,
        )

        # Critical decision patterns
        self.critical_patterns = ["production", "deploy", "security", "financial", "payment", "transaction", "delete", "terminate"]

        logger.info("MADDecisionEngine initialized with MAD consensus capability")

    def execute_decision(self, context: dict[str, Any]) -> JudgeDecision:
        """
        Execute decision with MAD consensus if critical, else Glicko failover.

        Args:
            context: Decision context

        Returns:
            JudgeDecision from MAD consensus or Glicko failover
        """
        # Check if this is a critical decision
        if self._is_critical_decision(context):
            logger.info("Critical decision detected - using MAD consensus")
            return self._execute_mad_decision(context)
        else:
            logger.debug("Routine decision - using Glicko failover")
            return super().execute_decision(context)

    def _is_critical_decision(self, context: dict[str, Any]) -> bool:
        """
        Determine if decision warrants MAD consensus.

        Criteria:
        1. Risk level is "high" or "critical"
        2. User explicitly requests multi-agent review
        3. Decision type matches critical patterns
        """
        # Explicit risk level
        risk_level = context.get("risk_level", "low").lower()
        if risk_level in ["high", "critical"]:
            return True

        # Explicit MAD request
        if context.get("multi_agent_review", False):
            return True

        # Pattern matching on user request
        user_request = context.get("user_request", "").lower()
        if any(pattern in user_request for pattern in self.critical_patterns):
            return True

        return False

    def _execute_mad_decision(self, context: dict[str, Any]) -> JudgeDecision:
        """
        Execute decision using MAD consensus.

        This runs multi-agent debate with Glicko-weighted voting.

        Args:
            context: Decision context

        Returns:
            JudgeDecision from MAD consensus
        """
        start_time = time.time()

        # Update MAD Glicko ratings (they may have changed)
        self.mad_glicko_ratings = {
            "gemini": self.glicko_ratings[ProviderType.GEMINI].get_rating(),
            "claude": self.glicko_ratings[ProviderType.CLAUDE].get_rating(),
            "gpt5": self.glicko_ratings[ProviderType.GPT5].get_rating(),
        }
        self.mad_engine.glicko_ratings = self.mad_glicko_ratings

        # Reach MAD consensus
        consensus = self.mad_engine.reach_consensus(
            context=context,
            timeout_per_agent=2.0,  # 2s per agent (generous for critical decisions)
        )

        # Convert MADConsensus to JudgeDecision format
        decision = self._convert_mad_to_judge_decision(consensus, start_time)

        # Update Glicko ratings based on MAD participation
        self._update_mad_glicko_ratings(consensus)

        return decision

    def _convert_mad_to_judge_decision(self, consensus: MADConsensus, start_time: float) -> JudgeDecision:
        """
        Convert MADConsensus to JudgeDecision format.

        Args:
            consensus: MAD consensus result
            start_time: Decision start time

        Returns:
            JudgeDecision
        """
        # Map DecisionType to decision string
        decision_map = {
            DecisionType.APPROVE: "approve",
            DecisionType.REJECT: "reject",
            DecisionType.ESCALATE: "escalate",
            DecisionType.DEFER: "defer",
        }

        return JudgeDecision(
            decision=decision_map.get(consensus.decision, "defer"),
            confidence=consensus.confidence,
            reasoning=consensus.reasoning,
            provider_used=ProviderType.GEMINI,  # Placeholder (actually MAD)
            latency_ms=consensus.total_latency_ms,
            fallback_chain=[],  # MAD doesn't use fallback
            is_degraded_mode=False,
        )

    def _update_mad_glicko_ratings(self, consensus: MADConsensus):
        """
        Update Glicko ratings based on MAD participation.

        Providers that voted with the majority get small rating boost.
        Providers in minority get small rating penalty.
        """
        winning_decision = consensus.decision

        for vote in consensus.individual_votes:
            # Map agent_id to ProviderType
            provider_map = {"gemini": ProviderType.GEMINI, "claude": ProviderType.CLAUDE, "gpt5": ProviderType.GPT5}

            provider_type = provider_map.get(vote.agent_id)
            if not provider_type:
                continue

            # Determine outcome (1.0 if voted with majority, 0.0 if minority)
            outcome = 1.0 if vote.decision == winning_decision else 0.0

            # Small update (MAD consensus doesn't strongly indicate individual skill)
            # Use opponent rating = system average
            avg_rating = sum(player.get_rating() for player in self.glicko_ratings.values()) / len(self.glicko_ratings)

            system_average = Glicko2Player(mu=avg_rating, phi=200, sigma=0.06)

            # Update with reduced weight (0.5 multiplier)
            self.glicko_ratings[provider_type].update(
                [
                    (outcome * 0.5 + 0.25, system_average)  # 0.25-0.75 range
                ]
            )

            logger.debug(
                f"Updated {provider_type.value} rating from MAD: "
                f"{self.glicko_ratings[provider_type].get_rating():.0f} "
                f"(voted {vote.decision.value}, majority {winning_decision.value})"
            )

    def get_mad_stats(self) -> dict[str, Any]:
        """Get statistics about MAD consensus usage."""
        # TODO: Track MAD usage stats
        return {
            "total_mad_decisions": 0,  # Placeholder
            "unanimous_rate": 0.0,
            "avg_debate_rounds": 0.0,
            "avg_mad_latency_ms": 0.0,
        }


# Example usage
if __name__ == "__main__":
    print("=== MAD Decision Engine Demo ===\n")

    # Initialize engine
    engine = MADDecisionEngine()

    print("Testing routine vs critical decision routing...\n")

    # Test 1: Routine decision (Glicko failover)
    print("Test 1: Routine decision (low risk)")
    print("-" * 70)

    routine_context = {"user_request": "Update user email address", "risk_level": "low", "user_id": "user_123"}

    start = time.time()
    decision = engine.execute_decision(routine_context)
    elapsed = time.time() - start

    print(f"Decision: {decision.decision}")
    print(f"Provider: {decision.provider_used.value}")
    print(f"Confidence: {decision.confidence:.2%}")
    print(f"Latency: {decision.latency_ms:.1f}ms (actual: {elapsed * 1000:.1f}ms)")
    print(f"Reasoning: {decision.reasoning[:100]}...")

    print("\n" + "=" * 70 + "\n")

    # Test 2: Critical decision (MAD consensus)
    print("Test 2: Critical decision (high risk - production deployment)")
    print("-" * 70)

    critical_context = {
        "user_request": "Deploy payment gateway to production",
        "risk_level": "high",
        "user_id": "user_123",
        "tests_passed": True,
        "security_scan": False,  # Missing security scan
    }

    start = time.time()
    decision = engine.execute_decision(critical_context)
    elapsed = time.time() - start

    print(f"Decision: {decision.decision}")
    print(f"Provider: {decision.provider_used.value} (actually MAD consensus)")
    print(f"Confidence: {decision.confidence:.2%}")
    print(f"Latency: {decision.latency_ms:.1f}ms (actual: {elapsed * 1000:.1f}ms)")
    print("\nFull reasoning:")
    print(decision.reasoning)

    print("\n" + "=" * 70 + "\n")

    # Test 3: Explicit MAD request
    print("Test 3: Explicit multi-agent review request")
    print("-" * 70)

    explicit_mad_context = {
        "user_request": "Approve new API integration",
        "risk_level": "medium",
        "multi_agent_review": True,  # Explicit request
        "user_id": "user_456",
    }

    start = time.time()
    decision = engine.execute_decision(explicit_mad_context)
    elapsed = time.time() - start

    print(f"Decision: {decision.decision}")
    print(f"Confidence: {decision.confidence:.2%}")
    print(f"Latency: {decision.latency_ms:.1f}ms")
    print("\nMAD consensus reasoning (first 300 chars):")
    print(decision.reasoning[:300] + "...")

    print("\n" + "=" * 70 + "\n")

    # Show provider rankings
    print("Current provider rankings:")
    stats = engine.get_provider_stats()
    for rank in stats["rankings"]:
        print(f"  {rank['provider']}: {rank['rating']:.0f} rating ({rank['allocation_pct']:.1f}% allocation)")
