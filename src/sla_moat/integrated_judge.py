# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Integrated Judge #6 Engine - Complete Pinkln + SLA Moat System

This is the production-ready integration of all components:

LAYER 2 (Pinkln Intelligence):
├─ Glicko-2: Dynamic provider ranking
├─ DTE: Self-evolution (+3.7%/iteration)
├─ MAD: Multi-agent consensus for critical decisions
└─ Cheat Sheet Fusion: Provider-optimized prompts

LAYER 1 (SLA Moat Resilience):
├─ 4-layer failover (Gemini→Claude→GPT-5→Local)
├─ p99≤90ms SLA guarantee
└─ Force majeure contracts + E&O insurance

This is the "Insanely Great" product that combines infrastructure resilience
with self-evolving intelligence. The system gets better with every decision
(Boy Scout Rule) while maintaining contractual SLA guarantees.

Example:
    # Initialize complete system
    judge = IntegratedJudge()

    # Routine decision (Glicko failover + Cheat Sheet)
    decision = judge.decide({
        "user_request": "Update user profile",
        "risk_level": "low"
    })
    # Fast, single provider, optimized prompt

    # Critical decision (MAD consensus + Cheat Sheet)
    decision = judge.decide({
        "user_request": "Deploy to production",
        "risk_level": "high"
    })
    # Multi-agent debate, Glicko-weighted voting, transparent reasoning

    # After 1000 decisions:
    # - Provider rankings optimized (best-rated first)
    # - Local model improved via DTE (+3.7% accuracy)
    # - Prompts evolved for each provider
    # - System compounds intelligence (Boy Scout Rule)
"""

import logging
from typing import Any
from dataclasses import dataclass

from .failover_engine import JudgeDecision, ProviderType
from .mad_decision_engine import MADDecisionEngine
from .cheat_sheet_fusion import CheatSheetFusion, CheatSheetLibrary, ProviderType as CheatProviderType
from .dte_local_trainer import DTELocalModelTrainer

logger = logging.getLogger(__name__)


@dataclass
class IntegratedDecisionMetrics:
    """Comprehensive metrics for integrated decision."""

    decision: JudgeDecision
    cheat_sheet_used: str  # Which cheat sheet profile used
    mad_consensus_used: bool  # Whether MAD was invoked
    glicko_ranking_used: bool  # Whether Glicko dynamic ranking used
    provider_allocation_pct: float  # Current allocation % of provider used
    system_age_decisions: int  # Total decisions made (system maturity)


class IntegratedJudge:
    """
    Complete Judge #6 engine with all Pinkln + SLA Moat components integrated.

    This is the production-ready system that combines:
    - Glicko-2 dynamic provider ranking
    - DTE self-evolution for local model
    - MAD multi-agent consensus for critical decisions
    - Cheat Sheet Fusion for provider-optimized prompts
    - 4-layer failover with p99≤90ms SLA guarantee

    The system continuously improves itself (Boy Scout Rule):
    - Provider rankings adjust based on performance
    - Local model evolves via DTE (+3.7% per iteration)
    - Prompts optimize for each provider's strengths
    - Decision quality compounds over time
    """

    def __init__(
        self,
        enable_glicko: bool = True,
        enable_mad: bool = True,
        enable_cheat_sheet: bool = True,
        enable_dte: bool = False,  # DTE runs offline, not in request path
        model_path: str = "models/judge6_local.pt",
    ):
        """
        Initialize integrated judge.

        Args:
            enable_glicko: Use Glicko-2 dynamic provider ranking (default: True)
            enable_mad: Use MAD consensus for critical decisions (default: True)
            enable_cheat_sheet: Use provider-optimized prompts (default: True)
            enable_dte: Enable DTE evolution (default: False - runs offline)
            model_path: Path to local PyTorch model
        """
        self.enable_glicko = enable_glicko
        self.enable_mad = enable_mad
        self.enable_cheat_sheet = enable_cheat_sheet
        self.enable_dte = enable_dte

        # Initialize core decision engine
        if enable_mad and enable_glicko:
            # MAD + Glicko (full integration)
            self.engine = MADDecisionEngine()
            logger.info("Initialized with MAD + Glicko-2")
        elif enable_glicko:
            # Glicko only (dynamic ranking, no MAD)
            from .glicko_failover import GlickoEnhancedFailover

            self.engine = GlickoEnhancedFailover()
            logger.info("Initialized with Glicko-2 only")
        else:
            # Base failover (static ranking)
            from .failover_engine import JREngineWithFailover

            self.engine = JREngineWithFailover()
            logger.info("Initialized with base failover (no Glicko)")

        # Initialize Cheat Sheet Fusion
        if enable_cheat_sheet:
            self.cheat_sheet_library = CheatSheetLibrary()
            self.cheat_sheet_fusion = CheatSheetFusion(self.cheat_sheet_library)
            logger.info("Cheat Sheet Fusion enabled")
        else:
            self.cheat_sheet_fusion = None

        # Initialize DTE trainer (offline use only)
        if enable_dte:
            self.dte_trainer = DTELocalModelTrainer(model_path=model_path, target_accuracy=0.80, target_commercial_agreement=0.80)
            logger.info("DTE evolution enabled (offline mode)")
        else:
            self.dte_trainer = None

        # Track system maturity
        self.total_decisions = 0

        logger.info(f"IntegratedJudge initialized: Glicko={enable_glicko}, MAD={enable_mad}, CheatSheet={enable_cheat_sheet}, DTE={enable_dte}")

    def decide(self, context: dict[str, Any]) -> IntegratedDecisionMetrics:
        """
        Make a decision with full Pinkln + SLA Moat integration.

        This is the main entry point for production use.

        Args:
            context: Decision context with user request, risk level, etc.

        Returns:
            IntegratedDecisionMetrics with decision + system metadata
        """
        self.total_decisions += 1

        # Apply Cheat Sheet Fusion if enabled
        if self.cheat_sheet_fusion and "user_request" in context:
            # Determine which provider will be used (peek at rankings)
            if hasattr(self.engine, "glicko_ratings"):
                from .glicko2 import get_ranked_providers

                ranked = get_ranked_providers(self.engine.glicko_ratings)
                likely_provider = ranked[0][0]  # Best-rated provider
            else:
                likely_provider = ProviderType.GEMINI  # Default

            # Map ProviderType to CheatProviderType
            cheat_provider = self._map_provider_type(likely_provider)

            # Apply cheat sheet fusion to user request
            original_request = context["user_request"]
            optimized_prompt = self.cheat_sheet_fusion.apply(base_prompt=original_request, provider=cheat_provider)

            # Update context with optimized prompt
            context["_original_request"] = original_request
            context["_optimized_prompt"] = optimized_prompt
            context["user_request"] = optimized_prompt

            cheat_sheet_used = cheat_provider.value
        else:
            cheat_sheet_used = "none"

        # Execute decision (Glicko failover or MAD consensus)
        decision = self.engine.execute_decision(context)

        # Determine if MAD was used
        mad_used = self.enable_mad and self._was_mad_used(context)

        # Get provider allocation
        if hasattr(self.engine, "glicko_ratings"):
            from .glicko2 import get_allocation_percentages

            allocations = get_allocation_percentages(self.engine.glicko_ratings)
            provider_allocation = allocations.get(decision.provider_used, 0.0)
        else:
            provider_allocation = 0.0  # Unknown for base failover

        # Build comprehensive metrics
        metrics = IntegratedDecisionMetrics(
            decision=decision,
            cheat_sheet_used=cheat_sheet_used,
            mad_consensus_used=mad_used,
            glicko_ranking_used=self.enable_glicko,
            provider_allocation_pct=provider_allocation * 100,
            system_age_decisions=self.total_decisions,
        )

        return metrics

    def _map_provider_type(self, provider: ProviderType) -> CheatProviderType:
        """Map ProviderType to CheatProviderType."""
        mapping = {
            ProviderType.GEMINI: CheatProviderType.GEMINI,
            ProviderType.CLAUDE: CheatProviderType.CLAUDE,
            ProviderType.GPT5: CheatProviderType.GPT5,
            ProviderType.LOCAL: CheatProviderType.LOCAL,
        }
        return mapping.get(provider, CheatProviderType.GEMINI)

    def _was_mad_used(self, context: dict[str, Any]) -> bool:
        """Check if MAD consensus was used for this decision."""
        if not self.enable_mad:
            return False

        # Check critical decision criteria (same as MADDecisionEngine)
        risk_level = context.get("risk_level", "low").lower()
        if risk_level in ["high", "critical"]:
            return True

        if context.get("multi_agent_review", False):
            return True

        user_request = context.get("user_request", "").lower()
        critical_patterns = ["production", "deploy", "security", "financial", "payment", "transaction", "delete", "terminate"]
        if any(pattern in user_request for pattern in critical_patterns):
            return True

        return False

    def evolve_local_model(self, max_iterations: int = 10, save_checkpoints: bool = True) -> dict[str, Any]:
        """
        Run DTE evolution on local model (offline operation).

        This should be run periodically (e.g., weekly) to improve local fallback.

        Args:
            max_iterations: Number of DTE iterations
            save_checkpoints: Save model checkpoints

        Returns:
            Training summary with improvements
        """
        if not self.dte_trainer:
            raise RuntimeError("DTE not enabled. Initialize with enable_dte=True")

        logger.info(f"Starting DTE evolution: max_iterations={max_iterations}")

        # Run evolution
        self.dte_trainer.evolve_continuously(max_iterations=max_iterations, save_checkpoints=save_checkpoints)

        # Get training summary
        summary = self.dte_trainer.get_training_summary()

        logger.info(f"DTE evolution complete: accuracy improved {summary['initial_accuracy']:.2%} → {summary['final_accuracy']:.2%}")

        return summary

    def get_system_status(self) -> dict[str, Any]:
        """
        Get comprehensive system status and health metrics.

        Returns:
            Dict with all system statistics and health indicators
        """
        status = {
            "system_age_decisions": self.total_decisions,
            "components_enabled": {
                "glicko_2": self.enable_glicko,
                "mad_consensus": self.enable_mad,
                "cheat_sheet_fusion": self.enable_cheat_sheet,
                "dte_evolution": self.enable_dte,
            },
        }

        # Add Glicko stats if enabled
        if hasattr(self.engine, "get_provider_stats"):
            status["provider_stats"] = self.engine.get_provider_stats()

        # Add MAD stats if enabled
        if hasattr(self.engine, "get_mad_stats"):
            status["mad_stats"] = self.engine.get_mad_stats()

        # Add DTE stats if enabled
        if self.dte_trainer:
            status["dte_stats"] = self.dte_trainer.get_training_summary()

        return status


# Example usage
if __name__ == "__main__":
    print("=== Integrated Judge #6 Engine Demo ===\n")
    print("Complete Pinkln + SLA Moat Integration\n")
    print("=" * 70 + "\n")

    # Initialize complete system
    judge = IntegratedJudge(
        enable_glicko=True,
        enable_mad=True,
        enable_cheat_sheet=True,
        enable_dte=False,  # DTE runs offline
    )

    print("System initialized with:")
    print("  ✓ Glicko-2 dynamic provider ranking")
    print("  ✓ MAD multi-agent consensus")
    print("  ✓ Cheat Sheet Fusion (provider-optimized prompts)")
    print("  ✓ 4-layer failover (Gemini→Claude→GPT-5→Local)")
    print()

    # Test 1: Routine decision
    print("=" * 70)
    print("TEST 1: Routine Decision (Low Risk)")
    print("=" * 70 + "\n")

    metrics = judge.decide({"user_request": "Update user email to new_email@example.com", "risk_level": "low", "user_id": "user_123"})

    print(f"Decision: {metrics.decision.decision}")
    print(f"Provider: {metrics.decision.provider_used.value}")
    print(f"Confidence: {metrics.decision.confidence:.2%}")
    print(f"Latency: {metrics.decision.latency_ms:.1f}ms")
    print(f"Cheat Sheet: {metrics.cheat_sheet_used}")
    print(f"MAD Used: {metrics.mad_consensus_used}")
    print(f"Glicko Ranking: {metrics.glicko_ranking_used}")
    print(f"Provider Allocation: {metrics.provider_allocation_pct:.1f}%")
    print(f"System Age: {metrics.system_age_decisions} decisions")

    print("\n" + "=" * 70)
    print("TEST 2: Critical Decision (High Risk - Production Deploy)")
    print("=" * 70 + "\n")

    metrics = judge.decide(
        {
            "user_request": "Deploy payment gateway integration to production",
            "risk_level": "high",
            "user_id": "admin_456",
            "tests_passed": True,
            "security_scan": False,  # Missing security scan
        }
    )

    print(f"Decision: {metrics.decision.decision}")
    print(f"Provider: {metrics.decision.provider_used.value} (MAD consensus)")
    print(f"Confidence: {metrics.decision.confidence:.2%}")
    print(f"Latency: {metrics.decision.latency_ms:.1f}ms")
    print(f"Cheat Sheet: {metrics.cheat_sheet_used}")
    print(f"MAD Used: {metrics.mad_consensus_used}")
    print(f"System Age: {metrics.system_age_decisions} decisions")
    print("\nReasoning (first 200 chars):")
    print(metrics.decision.reasoning[:200] + "...")

    print("\n" + "=" * 70)
    print("TEST 3: Multiple Decisions (System Learning)")
    print("=" * 70 + "\n")

    print("Making 10 decisions to show system learning...\n")

    for i in range(1, 11):
        context = {"user_request": f"Process transaction {i}", "risk_level": "medium", "amount": i * 100}

        metrics = judge.decide(context)
        print(f"  Decision {i}: {metrics.decision.decision} by {metrics.decision.provider_used.value} ({metrics.decision.latency_ms:.0f}ms)")

    print("\n" + "=" * 70)
    print("SYSTEM STATUS")
    print("=" * 70 + "\n")

    status = judge.get_system_status()

    print(f"Total decisions: {status['system_age_decisions']}")
    print("\nComponents enabled:")
    for component, enabled in status["components_enabled"].items():
        print(f"  {component}: {'✓' if enabled else '✗'}")

    if "provider_stats" in status:
        print("\nProvider rankings:")
        for rank in status["provider_stats"]["rankings"]:
            print(f"  {rank['provider']}: {rank['rating']:.0f} rating ({rank['allocation_pct']:.1f}% allocation)")

    print("\n" + "=" * 70)
    print("\n✨ Integrated Judge #6 ready for production! ✨")
    print("\nKey features:")
    print("  • Self-optimizing (Glicko-2 rankings adjust automatically)")
    print("  • Self-evolving (DTE improves local model +3.7%/iteration)")
    print("  • Self-validating (MAD consensus for critical decisions)")
    print("  • Provider-optimized prompts (Cheat Sheet Fusion)")
    print("  • p99≤90ms SLA guarantee (4-layer failover)")
    print("\nThe system gets better with every decision. 🚀")
