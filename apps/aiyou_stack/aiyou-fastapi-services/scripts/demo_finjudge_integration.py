import asyncio
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.finjudge.core.pure_judge import JudgeRequest, PureJudgeEngine
from src.ultrathink.finance.leaks import RevenueLeakDetector


async def run_demo():
    print("=== FinJudge Integration Demo ===\n")

    # 1. Initialize Engine
    print("1. Initializing Pure Judge Engine...")
    engine = PureJudgeEngine()
    print(f"   Persona: {engine.judge_persona.name}")
    print(f"   Skill: ChainOfThought trigger='{engine.cot.trigger_phrase}'")

    # 2. Make a Decision
    print("\n2. Evaluating High Risk Request...")
    req_high = JudgeRequest(
        request_id="req_001",
        intent_nl="Approve $1M transfer to offshore account.",
        metrics={"risk_score": 0.9, "burn_rate": 600000},
        context={"user": "trader_joe"},
    )

    ruling_high = await engine.evaluate(req_high)
    print(f"   Ruling ID: {ruling_high.ruling_id}")
    print(f"   Risk Level: {ruling_high.risk_level}")
    print(f"   Memo: {ruling_high.decision_memo}")
    print(f"   Controls: {ruling_high.controls_required}")
    print(f"   Audit: {ruling_high.audit_trail}")

    # 3. Revenue Guard Check (Simulating API Middleware)
    print("\n3. Testing Revenue Guard (Middleware Simulation)...")
    guard = RevenueLeakDetector()

    # Simulate a "Free Tier" request that used 20k tokens (Abuse)
    log_abuse = {"tokens_used": 20000, "revenue_generated": 0.0, "tier": "free"}
    warn = guard.analyze_transaction(log_abuse)

    if warn:
        print(f"   [ALERT] {warn.severity} SEVERITY: {warn.description}")
        print(f"   Recommendation: {warn.recommendation}")
    else:
        print("   No revenue leak detected.")

    print("\n=== Integration Demo Complete ===")


if __name__ == "__main__":
    asyncio.run(run_demo())
