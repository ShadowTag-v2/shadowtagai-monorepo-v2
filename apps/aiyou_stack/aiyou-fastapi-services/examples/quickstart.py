"""Ultrathink Quickstart Examples

Run these to see all framework capabilities in action.
"""

import asyncio

from ultrathink import BAB, CARE, RTF, CoT, ToT
from ultrathink.core.agents import MultiAgentDebate, PanelGPT
from ultrathink.monetization import RevenueTracker


def example_1_simple_prompting():
    """Example 1: Basic prompting techniques."""
    print("=" * 60)
    print("Example 1: Simple Prompting (RTF)")
    print("=" * 60)

    # RTF: Role-Task-Format
    rtf = RTF(
        role="expert financial analyst",
        task="analyze SaaS metrics",
        format="JSON with key insights",
        tone="professional",
    )

    prompt = rtf.format("MRR: $10k, Churn: 5%, CAC: $500, LTV: $2000")
    print(f"\nGenerated prompt:\n{prompt}\n")


def example_2_transformation_planning():
    """Example 2: Before-After-Bridge for planning."""
    print("=" * 60)
    print("Example 2: Transformation Planning (BAB)")
    print("=" * 60)

    bab = BAB(
        before="Manual CSV uploads taking 4 hours daily",
        after="Automated pipeline processing millions of records in minutes",
        bridge="Build ETL pipeline with Airflow + BigQuery",
        timeline="6 weeks",
    )

    prompt = bab.format("Current tech stack: Python, PostgreSQL, FastAPI")
    print(f"\nGenerated prompt:\n{prompt}\n")


def example_3_context_rich():
    """Example 3: CARE for context-rich tasks."""
    print("=" * 60)
    print("Example 3: Context-Rich Prompting (CARE)")
    print("=" * 60)

    care = CARE(
        context="Launching B2B SaaS for DevOps teams. Target: 20-200 person engineering orgs.",
        action="Create pricing strategy with 3 tiers",
        result="Pricing table with features, $/month, target personas",
        example={
            "tier": "Enterprise",
            "price": "$999/mo",
            "features": ["SSO", "99.9% SLA", "dedicated support"],
            "target": "200+ eng teams",
        },
    )

    prompt = care.format("Product: Kubernetes cost optimization platform")
    print(f"\nGenerated prompt:\n{prompt}\n")


def example_4_chain_of_thought():
    """Example 4: Chain-of-Thought reasoning."""
    print("=" * 60)
    print("Example 4: Chain-of-Thought Reasoning")
    print("=" * 60)

    cot = CoT(steps=5, verify=True, style="detailed")

    problem = "If CAC is $500, LTV is $2000, but churn increased from 3% to 8%, what's the new payback period?"

    result = cot.reason(problem)
    print(f"\nReasoning strategy: {result.metadata['technique']}")
    print(f"Steps configured: {result.metadata['num_steps']}")
    print(f"Verification: {result.metadata['verified']}")
    print(f"Confidence: {result.confidence:.0%}\n")
    print(f"Final answer: {result.final_answer}")
    print(
        "\n(Note: This is a placeholder - in production, would show actual step-by-step reasoning)\n",
    )


def example_5_tree_of_thoughts():
    """Example 5: Tree-of-Thoughts for exploration."""
    print("=" * 60)
    print("Example 5: Tree-of-Thoughts Exploration")
    print("=" * 60)

    tot = ToT(branches=3, max_depth=5, search="bfs")

    problem = "Design a go-to-market strategy for a new AI coding assistant"

    result = tot.reason(problem)
    print(f"\nSearch strategy: {result.metadata['search_strategy']}")
    print(f"Branches per node: {result.metadata['branches']}")
    print(f"Max depth: {result.metadata['max_depth']}")
    print(f"Branches explored: {result.explored_branches}")
    print("\n(Note: Would show tree visualization in production)\n")


def example_6_multi_agent_debate():
    """Example 6: Multi-Agent Debate."""
    print("=" * 60)
    print("Example 6: Multi-Agent Debate (MAD)")
    print("=" * 60)

    mad = MultiAgentDebate(agents=3, rounds=5, strategy="RCR")

    problem = "Should we build our own LLM infrastructure or use managed APIs?"

    result = mad.solve(problem)
    print(f"\nDebate participants: {result.metadata['num_agents']} agents")
    print(f"Strategy: {result.metadata['strategy']}")
    print(f"Rounds completed: {result.total_rounds}")
    print(f"\nConsensus: {result.consensus}")
    print("\n(Note: In production, would show full debate transcript)\n")


async def example_7_revenue_tracking():
    """Example 7: Revenue opportunity tracking."""
    print("=" * 60)
    print("Example 7: Revenue Opportunity Tracking")
    print("=" * 60)

    tracker = RevenueTracker()

    # Simulate conversation
    messages = [
        {"role": "user", "content": "I need to process millions of records daily"},
        {
            "role": "assistant",
            "content": "Currently doing this manually, takes my team 6 hours",
        },
        {"role": "user", "content": "Yes, and we have 5 people doing this"},
    ]

    opportunities = tracker.analyze_conversation(messages)

    print(f"\nDetected {len(opportunities)} revenue opportunities:\n")
    for opp in opportunities:
        print(f"- {opp.type.value}: ${opp.value_usd:.2f}")
        print(f"  Confidence: {opp.confidence:.0%}")
        print(f"  Action: {opp.action}")
        print(f"  Priority: {opp.priority}/10\n")

    # Simulate usage tracking
    tracker.log_request(endpoint="/analyze", reasoning="MAD", latency=1200, tokens=5000)
    tracker.log_request(endpoint="/reason", reasoning="ToT", latency=800, tokens=3000)

    roi = tracker.calculate_roi()
    print("ROI Analysis:")
    print(f"- Total opportunity value: ${roi['total_opportunity_value_usd']:,.2f}")
    print(f"- Compute cost: ${roi['compute_cost_usd']:.2f}")
    print(f"- ROI ratio: {roi['roi_ratio']:.1f}x\n")


def example_8_panel_discussion():
    """Example 8: Expert Panel (PanelGPT)."""
    print("=" * 60)
    print("Example 8: Expert Panel Discussion (PanelGPT)")
    print("=" * 60)

    from ultrathink.core.agents.panel_gpt import PanelMember

    panel = PanelGPT(
        members=[
            PanelMember(
                name="Dr. Sarah Chen",
                expertise="ML infrastructure & scaling",
                perspective="Cost-efficiency and performance",
            ),
            PanelMember(
                name="Marcus Thompson",
                expertise="Product strategy & GTM",
                perspective="User value and monetization",
            ),
            PanelMember(
                name="Aisha Patel",
                expertise="Engineering leadership",
                perspective="Team productivity and velocity",
            ),
        ],
        rounds=3,
    )

    result = panel.discuss("Should we migrate from monolith to microservices?")

    print(f"\nPanel members: {len(panel.members)}")
    for member in panel.members:
        print(f"- {member.name}: {member.expertise}")

    print(f"\nDiscussion rounds: {result.metadata['rounds']}")
    print(f"Final synthesis: {result.synthesis}")
    print("\n(Note: In production, would show full panel transcript)\n")


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print(" " * 15 + "ULTRATHINK QUICKSTART")
    print("=" * 60 + "\n")

    # Prompting techniques
    example_1_simple_prompting()
    example_2_transformation_planning()
    example_3_context_rich()

    # Reasoning engines
    example_4_chain_of_thought()
    example_5_tree_of_thoughts()

    # Multi-agent systems
    example_6_multi_agent_debate()
    example_8_panel_discussion()

    # Revenue tracking (async)
    asyncio.run(example_7_revenue_tracking())

    print("=" * 60)
    print(" " * 10 + "✨ All examples completed! ✨")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Run: uvicorn main:app --reload")
    print("2. Visit: http://localhost:8000/docs")
    print("3. Try the API endpoints")
    print("4. Check /analytics/revenue for insights\n")


if __name__ == "__main__":
    main()
