#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Example usage of UnGPT with AunCRM compliance integration
Demonstrates both single-model and multi-LLM consensus modes
"""

import asyncio
from anthropic import Anthropic
import google.generativeai as genai
from openai import OpenAI

# Import our modules
from config import Config
from aunccrm import Purpose, Reason, Brake, ComplianceContext, RiskLevel, AunCRMValidator
from ungpt.orchestrator import PNKLNAtomicOrchestrator
from ungpt.consensus import ConsensusOrchestrator


class AnthropicOrchestrator(PNKLNAtomicOrchestrator):
    """
    Concrete implementation of atomic orchestrator using Anthropic Claude
    """

    def __init__(self, api_key: str, **kwargs):
        self.anthropic_client = Anthropic(api_key=api_key)
        super().__init__(model_client=self.anthropic_client, model_name=Config.CLAUDE_MODEL, **kwargs)

    async def _call_model(self, prompt: str) -> str:
        """Call Anthropic Claude API"""
        response = await asyncio.to_thread(
            self.anthropic_client.messages.create, model=self.model_name, max_tokens=4000, messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text


async def demo_aunccrm_standalone():
    """
    Demo 1: Standalone AunCRM compliance validation
    """
    print("\n" + "=" * 80)
    print("DEMO 1: AunCRM Compliance Framework")
    print("=" * 80 + "\n")

    # Create a compliance context for a business decision
    purpose = Purpose(
        description="Deploy GPU compute infrastructure at cell tower sites for edge AI",
        business_value="$50M ARR opportunity in edge compute market",
        success_criteria=["Technical feasibility validated", "Partnership agreements with 2+ carriers", "Positive unit economics (LTV:CAC > 4:1)"],
    )

    reasons = [
        Reason(
            justification="5G rollout creates power/cooling infrastructure at cell sites",
            evidence=["Verizon 5G deployment data", "AT&T infrastructure specs"],
            assumptions=["Cell sites have sufficient power capacity", "Zoning permits available"],
            confidence_score=0.85,
        ),
        Reason(
            justification="Edge AI workloads require <10ms latency, incompatible with cloud",
            evidence=["AWS latency benchmarks", "Industry whitepaper on edge computing"],
            assumptions=["Latency requirements remain stable", "Network topology unchanged"],
            confidence_score=0.90,
        ),
    ]

    brakes = [
        Brake(
            constraint="Must achieve $3M ARR before expanding to 2nd region",
            threshold=3_000_000,
            enforcement_method="revenue_tracking",
            roi_threshold=3.0,
            ltv_cac_ratio=4.0,
            time_horizon_months=18,
        ),
        Brake(
            constraint="No capital deployment without signed carrier partnerships",
            enforcement_method="contract_validation",
            violation_action="halt_execution",
        ),
    ]

    context = ComplianceContext(
        context_id="EDGE_GPU_001",
        purpose=purpose,
        reasons=reasons,
        brakes=brakes,
        risk_level=RiskLevel.RA_3,  # Moderate risk - significant capital required
    )

    # Validate
    validator = AunCRMValidator(strict_mode=Config.STRICT_MODE)
    is_valid, violations, recommendations = validator.validate_context(context)

    print(f"Context ID: {context.context_id}")
    print(f"Risk Level: {context.risk_level.value}")
    print(f"\n✓ Validation: {'PASSED' if is_valid else 'FAILED'}")

    if violations:
        print("\n⚠️  Violations:")
        for v in violations:
            print(f"  - {v}")

    if recommendations["recommendations"]:
        print("\n💡 Recommendations:")
        for r in recommendations["recommendations"]:
            print(f"  - {r}")

    print("\n📊 Business Judgment Gates:")
    for key, value in recommendations["business_judgment_gates"].items():
        print(f"  {key}: {value}")


async def demo_atomic_orchestrator():
    """
    Demo 2: Atomic thread orchestration with AunCRM
    """
    print("\n" + "=" * 80)
    print("DEMO 2: UnGPT Atomic Thread Orchestrator")
    print("=" * 80 + "\n")

    if not Config.ANTHROPIC_API_KEY:
        print("⚠️  Skipping - ANTHROPIC_API_KEY not configured")
        return

    orchestrator = AnthropicOrchestrator(
        api_key=Config.ANTHROPIC_API_KEY, max_concurrent_threads=Config.MAX_CONCURRENT_THREADS, enable_compliance=Config.ENABLE_COMPLIANCE
    )

    query = """
    Analyze the business viability of deploying GPU compute infrastructure at cell tower sites.
    Cover: 1) Technical feasibility, 2) Market size, 3) Partnership models, 4) Competitive advantages
    """

    try:
        result = await orchestrator.process_query(query, max_threads=4)

        print("\n" + "=" * 80)
        print("FINAL OUTPUT:")
        print("=" * 80)
        print(result["final_output"])

        print("\n" + "=" * 80)
        print("EXECUTION SUMMARY:")
        print("=" * 80)
        for key, value in result["execution_summary"].items():
            print(f"{key}: {value}")

    except ValueError as e:
        print(f"\n⚠️  Query rejected by cost gate: {e}")


async def demo_consensus_orchestrator():
    """
    Demo 3: Multi-LLM consensus with peer review
    """
    print("\n" + "=" * 80)
    print("DEMO 3: Multi-LLM Consensus System")
    print("=" * 80 + "\n")

    required_keys = ["ANTHROPIC_API_KEY", "GOOGLE_API_KEY", "OPENAI_API_KEY", "XAI_API_KEY"]
    missing = [k for k in required_keys if not getattr(Config, k)]

    if missing:
        print(f"⚠️  Skipping - Missing API keys: {', '.join(missing)}")
        print("   Set these in .env file to enable multi-LLM consensus")
        return

    # Initialize all clients
    anthropic_client = Anthropic(api_key=Config.ANTHROPIC_API_KEY)
    openai_client = OpenAI(api_key=Config.OPENAI_API_KEY)
    genai.configure(api_key=Config.GOOGLE_API_KEY)
    gemini_model = genai.GenerativeModel(Config.GEMINI_MODEL)

    orchestrator = ConsensusOrchestrator(
        anthropic_client=anthropic_client, google_client=gemini_model, openai_client=openai_client, xai_api_key=Config.XAI_API_KEY
    )

    query = """
    What are the key strategic considerations for deploying edge AI compute infrastructure
    at cell tower sites? Provide analysis of technical, financial, and partnership aspects.
    """

    try:
        result = await orchestrator.execute_full_consensus(query)

        print("\n" + "=" * 80)
        print("CONSENSUS SYNTHESIS:")
        print("=" * 80)
        print(result["final_synthesis"])

        print("\n" + "=" * 80)
        print("CONSENSUS META-ANALYSIS:")
        print("=" * 80)
        print("Models consulted: Claude (L1, L3), Grok, Gemini, GPT (L2)")
        print(f"Peer reviews: {sum(len(v) for v in result['peer_reviews'].values())}")
        print(f"Layer 2 responses: {len(result['layer2_responses'])}")

    except Exception as e:
        print(f"\n⚠️  Consensus failed: {e}")


async def main():
    """Run all demos"""

    print("\n" + "=" * 80)
    print("UnGPT + AunCRM Integration Demo")
    print("=" * 80)
    print("\nConfiguration:")
    for key, value in Config.get_summary().items():
        print(f"  {key}: {value}")

    # Run demos
    await demo_aunccrm_standalone()
    await demo_atomic_orchestrator()
    await demo_consensus_orchestrator()

    print("\n" + "=" * 80)
    print("Demos complete!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
