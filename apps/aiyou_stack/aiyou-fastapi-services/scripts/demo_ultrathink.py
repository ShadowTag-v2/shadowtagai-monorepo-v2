# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.ultrathink.agents.roster import StandardRoster
from src.ultrathink.core.memory import SecureMemoryWrapper, ShortTermMemory
from src.ultrathink.finance.leaks import RevenueLeakDetector
from src.ultrathink.frameworks.glicko import Glicko2Engine
from src.ultrathink.frameworks.mad import MultiAgentDebate
from src.ultrathink.skills.patterns import ChainOfThought


def run_demo():
    print("=== Ultrathink Core Framework Demo ===\n")

    # 1. Roster & Agents
    print("1. Loading Roster...")
    roster = StandardRoster.list_all()
    designer = roster["DESIGNER"]
    critic = roster["CRITIC"]
    print(f"   Loaded: {designer.name} ({designer.role})")
    print(f"   Loaded: {critic.name} ({critic.role})")

    # 2. Skills
    print("\n2. Applying Skills...")
    cot = ChainOfThought()
    prompt = "Design a login screen for a fintech app."
    expanded_prompt = cot.apply(prompt)
    print(f"   Original: {prompt}")
    print(f"   CoT: {expanded_prompt.splitlines()[-1]}")

    # 3. Multi-Agent Debate
    print("\n3. Running Multi-Agent Debate (Mock)...")
    debate = MultiAgentDebate(agents=[designer, critic])
    result = debate.run_debate(topic="Should we use biometric auth by default?", rounds=2)
    for turn in result.transcript:
        print(f"   [Round {turn.round}] {turn.agent_name}: {turn.content[:40]}...")

    # 4. Glicko Rating Update
    print("\n4. Updating Ratings (Glicko-2)...")
    engine = Glicko2Engine()
    # Simulating Designer 'winning' the debate (better argument) against Critic
    # Current ratings (standard start)
    r1, rd1, v1 = 1500, 350, 0.06
    r2, rd2, v2 = 1500, 350, 0.06

    print(f"   Start Ratings: Designer={r1:.0f}, Critic={r2:.0f}")

    # Designer vs Critic (Win)
    new_r1, new_rd1, new_v1 = engine.update_rating(r1, rd1, v1, [(r2, rd2, 1.0)])
    # Critic vs Designer (Loss)
    new_r2, new_rd2, new_v2 = engine.update_rating(r2, rd2, v2, [(r1, rd1, 0.0)])

    print(f"   End Ratings:   Designer={new_r1:.0f}, Critic={new_r2:.0f}")

    # 5. Finance / Leak Detection
    print("\n5. Checking for Revenue Leaks...")
    detector = RevenueLeakDetector()

    # Case A: Good Transaction
    log_a = {"tokens_used": 500, "revenue_generated": 0.10, "tier": "pro"}
    warn_a = detector.analyze_transaction(log_a)
    print(f"   Case A (Pro, low usage): {'No Leak' if not warn_a else warn_a.description}")

    # Case B: Bad Transaction (Free tier abuse)
    log_b = {"tokens_used": 15000, "revenue_generated": 0.0, "tier": "free"}
    warn_b = detector.analyze_transaction(log_b)
    print(f"   Case B (Free, abuse):    {warn_b.description if warn_b else 'No Leak'}")

    print(f"   Case B (Free, abuse):    {warn_b.description if warn_b else 'No Leak'}")

    # 6. Memory & Security
    print("\n6. Testing Secure Memory...")
    raw_memory = ShortTermMemory()
    secure_memory = SecureMemoryWrapper(raw_memory)

    sensitive_input = (
        "User API Key is [VAPORIZED_OPENAI_TOKEN] and email is redacted@shadowtag-v4.local"
    )
    print(f"   Input: {sensitive_input}")

    secure_memory.add("user", sensitive_input)
    stored_context = secure_memory.get_context()
    print(f"   Stored: {stored_context}")

    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    run_demo()
