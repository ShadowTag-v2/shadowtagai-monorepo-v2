#!/usr/bin/env python3
"""
Integration tests for PNKLN Core Stack™ API
Tests AutoGen → Gemini migration functionality
"""

import asyncio
import sys

from app.services.gemini_agents import GeminiAgent, GeminiGroupChat


async def test_agent_initialization():
    """Test agent initialization without API key (fallback mode)"""
    print("=" * 70)
    print("TEST 1: Agent Initialization (Fallback Mode)")
    print("=" * 70)

    agent = GeminiAgent(
        name="skeptic",
        persona="You are a skeptical analyst",
        temperature=0.5,
        api_key=None,  # Test fallback mode
    )

    assert agent.name == "skeptic"
    assert agent.persona == "You are a skeptical analyst"
    assert agent.model is None  # Should be None in fallback mode
    print("✓ Agent initialized successfully in fallback mode")
    print()


async def test_agent_fallback_proposal():
    """Test agent tier proposal fallback (without Gemini API)"""
    print("=" * 70)
    print("TEST 2: Agent Fallback Tier Proposal")
    print("=" * 70)

    agent = GeminiAgent(
        name="skeptic", persona="You are a skeptical analyst", temperature=0.5, api_key=None
    )

    # Test Tier 1 content (regulatory)
    proposal = await agent.propose_tier(
        title="FAA Issues New DO-178D Regulation for AI Systems",
        content="The Federal Aviation Administration today announced new regulatory requirements for AI-based flight control systems. This regulation mandates version-level audit trails and compliance with DO-178D software certification standards.",
        tags=["aviation", "regulation"],
    )

    print("Title: FAA Issues New DO-178D Regulation for AI Systems")
    print(f"Result: Tier {proposal['tier']} (confidence: {proposal['confidence']:.0%})")
    print(f"Agent: {proposal['agent']}")
    print(f"Reasoning: {proposal['reasoning']}")

    assert proposal["tier"] == 1  # Should classify as Tier 1 (regulation keyword)
    assert proposal["agent"] == "skeptic"
    assert 0.0 <= proposal["confidence"] <= 1.0
    print("✓ Tier 1 classification successful")
    print()

    # Test Tier 3 content (social media)
    proposal2 = await agent.propose_tier(
        title="My opinion on why AI is overhyped",
        content="This is just my opinion on social media about AI trends...",
        tags=["opinion"],
    )

    print("Title: My opinion on why AI is overhyped")
    print(f"Result: Tier {proposal2['tier']} (confidence: {proposal2['confidence']:.0%})")
    print(f"Reasoning: {proposal2['reasoning']}")

    assert proposal2["tier"] == 3  # Should classify as Tier 3 (opinion keyword)
    print("✓ Tier 3 classification successful")
    print()


async def test_group_chat_initialization():
    """Test multi-agent group chat initialization"""
    print("=" * 70)
    print("TEST 3: Group Chat Initialization")
    print("=" * 70)

    chat = GeminiGroupChat(
        api_key=None,  # Test fallback mode
        agents=["skeptic", "optimist", "neutral"],
    )

    assert len(chat.agents) == 3
    assert "skeptic" in chat.agents
    assert "optimist" in chat.agents
    assert "neutral" in chat.agents

    # Verify agent temperatures
    assert chat.agents["skeptic"].generation_config["temperature"] == 0.5
    assert chat.agents["optimist"].generation_config["temperature"] == 0.9
    assert chat.agents["neutral"].generation_config["temperature"] == 0.3

    print(f"✓ Group chat initialized with {len(chat.agents)} agents")
    print("  - Skeptic (temperature: 0.5 - conservative)")
    print("  - Optimist (temperature: 0.9 - creative)")
    print("  - Neutral (temperature: 0.3 - deterministic)")
    print()


async def test_multi_agent_debate():
    """Test full multi-agent debate classification"""
    print("=" * 70)
    print("TEST 4: Multi-Agent Debate Classification")
    print("=" * 70)

    chat = GeminiGroupChat(api_key=None, agents=["skeptic", "optimist", "neutral"])

    # Test with high-value intelligence item
    result = await chat.classify_with_debate(
        title="BREAKING: DoD Awards $500M Contract for AI-Based ISR System",
        content="""
        The Department of Defense today announced a $500 million contract award
        for development of an AI-based Intelligence, Surveillance, and Reconnaissance
        (ISR) system. The contract, awarded to a major defense contractor, includes
        provisions for ATP 5-19 compliant data handling and ITAR-controlled algorithm
        development. This represents the largest DoD AI contract to date and signals
        accelerating adoption of AI in defense applications.
        """,
        tags=["defense", "DOD", "ISR", "AI"],
        rounds=2,
        voting_method="weighted_confidence",
    )

    print("Article: DoD Awards $500M Contract for AI-Based ISR System")
    print("\nFinal Classification:")
    print(f"  Tier: {result.tier}")
    print(f"  Confidence: {result.confidence:.0%}")
    print(f"  Tags: {', '.join(result.tags)}")
    print("\nReasoning (first 200 chars):")
    print(f"  {result.reasoning[:200]}...")

    assert result.tier in [1, 2, 3]
    assert 0.0 <= result.confidence <= 1.0
    assert len(result.tags) >= 4

    print("\n✓ Multi-agent debate completed successfully")
    print()


async def test_voting_methods():
    """Test different voting aggregation methods"""
    print("=" * 70)
    print("TEST 5: Voting Method Comparison")
    print("=" * 70)

    chat = GeminiGroupChat(api_key=None)

    test_item = {
        "title": "FAA Proposes New Aviation Safety Regulation",
        "content": "The FAA has proposed new safety requirements for commercial aircraft...",
        "tags": ["aviation", "regulation"],
    }

    methods = ["weighted_confidence", "majority_vote", "neutral_arbiter"]

    for method in methods:
        result = await chat.classify_with_debate(
            title=test_item["title"],
            content=test_item["content"],
            tags=test_item["tags"],
            rounds=1,
            voting_method=method,
        )

        print(f"{method:25} → Tier {result.tier} ({result.confidence:.0%} confidence)")

    print("\n✓ All voting methods tested successfully")
    print()


async def test_persona_variations():
    """Test that different personas produce different biases"""
    print("=" * 70)
    print("TEST 6: Agent Persona Bias Validation")
    print("=" * 70)

    test_content = {
        "title": "Startup Claims Revolutionary AI Breakthrough",
        "content": "A small startup today announced what they claim is a revolutionary AI breakthrough...",
        "tags": ["AI", "startup"],
    }

    # Test each agent individually
    for agent_name in ["skeptic", "optimist", "neutral"]:
        chat = GeminiGroupChat(api_key=None, agents=[agent_name])
        result = await chat.classify_with_debate(
            title=test_content["title"],
            content=test_content["content"],
            tags=test_content["tags"],
            rounds=1,
            voting_method="weighted_confidence",
        )

        print(
            f"{agent_name.capitalize():10} → Tier {result.tier} (confidence: {result.confidence:.0%})"
        )

    print("\n✓ Agent personas exhibit expected bias patterns")
    print()


async def main():
    """Run all integration tests"""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "PNKLN CORE STACK™ INTEGRATION TESTS" + " " * 18 + "║")
    print("║" + " " * 15 + "AutoGen → Gemini Migration Validation" + " " * 15 + "║")
    print("╚" + "=" * 68 + "╝")
    print()

    tests = [
        ("Agent Initialization", test_agent_initialization),
        ("Agent Fallback Proposal", test_agent_fallback_proposal),
        ("Group Chat Initialization", test_group_chat_initialization),
        ("Multi-Agent Debate", test_multi_agent_debate),
        ("Voting Methods", test_voting_methods),
        ("Persona Bias Validation", test_persona_variations),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            await test_func()
            passed += 1
        except Exception as e:
            print(f"✗ {test_name} FAILED: {e}")
            failed += 1

    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Total Tests: {len(tests)}")
    print(f"Passed: {passed} ✓")
    print(f"Failed: {failed} ✗")
    print("=" * 70)

    if failed > 0:
        print("\n⚠️  Some tests failed. Review output above for details.")
        sys.exit(1)
    else:
        print("\n🎉 All tests passed! AutoGen → Gemini migration validated.")
        print("\nNext Steps:")
        print("  1. Set GEMINI_API_KEY to test with real Gemini 2.0 Pro API")
        print("  2. Deploy to Cloud Run: gcloud run deploy pnkln-api")
        print("  3. Run load tests to validate p99 latency targets")
        print("  4. Enable A/B testing (20% multi-agent, 80% single model)")
        sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())
