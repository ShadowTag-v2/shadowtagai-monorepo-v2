# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
ULTRATHINK Framework - Basic Python Usage Examples

Examples demonstrating core functionality of the ULTRATHINK framework.
"""

import asyncio
from ultrathink import UltrathinkOrchestrator, TaskType, AgentContext, AgentRole, SkillType, ChiefDesignOfficer, UltrathinkConfig


async def example_1_orchestrator_basic():
    """Example 1: Basic orchestrator usage with automatic routing."""
    print("=" * 60)
    print("Example 1: Basic Orchestrator Usage")
    print("=" * 60)

    orchestrator = UltrathinkOrchestrator()

    result = await orchestrator.execute(task="Review this API design for elegance and simplicity", task_type=TaskType.DESIGN_REVIEW)

    print(f"\nTask: {result['task']}")
    print(f"Type: {result['task_type']}")
    print(f"\nResult:\n{result['result'].content}")
    print(f"\nConfidence: {result['result'].confidence:.0%}")


async def example_2_specific_agent():
    """Example 2: Using a specific agent directly."""
    print("\n" + "=" * 60)
    print("Example 2: Direct Agent Usage (CDO)")
    print("=" * 60)

    cdo = ChiefDesignOfficer()

    context = AgentContext(
        task="Audit this dashboard UI with 50 widgets for simplification opportunities",
        role=AgentRole.CDO,
        metadata={"current_widgets": 50, "user_complaints": ["too complex", "overwhelming", "can't find features"]},
    )

    response = await cdo.execute(context)

    print(f"\nCDO Analysis:\n{response.content}")
    print("\nRecommendations:")
    for i, rec in enumerate(response.recommendations, 1):
        print(f"{i}. {rec}")


async def example_3_skill_execution():
    """Example 3: Direct skill execution."""
    print("\n" + "=" * 60)
    print("Example 3: Direct Skill Execution")
    print("=" * 60)

    orchestrator = UltrathinkOrchestrator()

    result = await orchestrator.execute_skill(
        skill_type=SkillType.WEALTH,
        content="""
        Current Business State:
        - 50,000 email subscribers
        - $50,000/year revenue
        - Single product priced at $97
        - No upsell or cross-sell mechanism
        - 2% conversion rate from email to purchase
        """,
        parameters={"revenue_goal": 1000000, "audience_size": 50000, "engagement_rate": 0.15, "current_offers": ["Email course at $97"]},
    )

    print(f"\nMonetization Strategy:\n{result.result}")
    print("\nKey Improvements:")
    for imp in result.improvements:
        print(f"- {imp}")


async def example_4_strategic_decision():
    """Example 4: Strategic decision using PanelGPT."""
    print("\n" + "=" * 60)
    print("Example 4: Strategic Decision (PanelGPT)")
    print("=" * 60)

    orchestrator = UltrathinkOrchestrator()

    result = await orchestrator.execute(task="Should we pivot from B2C to B2B, or expand our B2C offering?", task_type=TaskType.STRATEGIC_DECISION)

    debate_result = result["result"]

    print(f"\nConsensus: {debate_result.consensus}")
    print(f"Confidence: {debate_result.confidence:.0%}")
    print(f"\nDebate Rounds: {len(debate_result.transcript)}")


async def example_5_holistic_initiative():
    """Example 5: Holistic initiative with all agents."""
    print("\n" + "=" * 60)
    print("Example 5: Holistic Initiative (All Agents)")
    print("=" * 60)

    orchestrator = UltrathinkOrchestrator()

    result = await orchestrator.execute(task="Launch a new SaaS product for project management", task_type=TaskType.HOLISTIC_INITIATIVE)

    responses = result["result"]

    print(f"\nAgents Consulted: {len(responses)}")
    for role, response in responses.items():
        print(f"\n--- {role.value.upper()} ---")
        print(response.content[:300] + "...")


async def example_6_custom_config():
    """Example 6: Custom configuration."""
    print("\n" + "=" * 60)
    print("Example 6: Custom Configuration")
    print("=" * 60)

    config = UltrathinkConfig(
        model="claude-sonnet-4-5-20250929",
        temperature=0.8,
        max_tokens=8192,
        enable_extended_thinking=True,
        security_mode=True,
        iteration_limit=10,
        confidence_threshold=0.9,
    )

    orchestrator = UltrathinkOrchestrator(config)

    # Get status
    agent_status = orchestrator.get_agent_status()
    skill_status = orchestrator.get_skill_status()

    print("\nAgent Status:")
    for agent_role, status in agent_status.items():
        print(f"- {agent_role}: {status['execution_count']} executions")

    print("\nSkill Status:")
    for skill_name, status in skill_status.items():
        print(f"- {skill_name}: {status['success_rate']:.0%} success rate")


async def example_7_foundation_prompts():
    """Example 7: Using foundation prompts."""
    print("\n" + "=" * 60)
    print("Example 7: Foundation Prompts")
    print("=" * 60)

    orchestrator = UltrathinkOrchestrator()
    prompts = orchestrator.get_foundation_prompts()

    print("\nAvailable Foundation Prompts:")
    for name in prompts.keys():
        print(f"- {name}")

    print("\nEntry Protocol Preview:")
    print(prompts["ultrathink_entry_protocol"][:300] + "...")


async def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("ULTRATHINK FRAMEWORK - Python Examples")
    print("=" * 60)

    await example_1_orchestrator_basic()
    await example_2_specific_agent()
    await example_3_skill_execution()
    await example_4_strategic_decision()
    await example_5_holistic_initiative()
    await example_6_custom_config()
    await example_7_foundation_prompts()

    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
