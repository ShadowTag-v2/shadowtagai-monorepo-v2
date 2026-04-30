"""Simple Agent Example - pinkln Agent Architecture System

This example demonstrates basic usage of the pinkln agent system.
"""

import asyncio
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.master_system import PnklnOS
from skills.design_critic import DesignCriticSkill
from skills.monetization_architect import MonetizationArchitectSkill
from skills.research_explorer import ResearchExplorerSkill


async def example_1_simple_skill():
    """Example 1: Using a single skill directly."""
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Simple Skill Usage")
    print("=" * 70)

    # Create a research skill
    research_skill = ResearchExplorerSkill()

    # Execute the skill
    result = await research_skill.execute({"topic": "AI-powered SaaS monetization strategies"})

    print("\n📊 Research Results:")
    print(f"Topic: {result['output']['topic']}")
    print("\n💡 Assumptions Identified:")
    for assumption in result["output"]["assumptions"]:
        print(f"  - {assumption}")

    print("\n🚀 Quick Wins:")
    for win in result["output"]["quick_wins"]:
        print(f"  - {win}")

    print("\n💰 Revenue Insights:")
    insights = result["output"]["revenue_insights"]
    print(f"  Potential Monthly Increase: {insights['potential_monthly_increase']}")
    print(f"  Timeline: {insights['implementation_timeline']}")
    print(f"  Risk Level: {insights['risk_level']}")


async def example_2_design_review():
    """Example 2: Using DesignCriticSkill."""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Design Review")
    print("=" * 70)

    design_skill = DesignCriticSkill()

    result = await design_skill.execute(
        {"artifact": "User onboarding flow with 7 steps and 3 forms"},
    )

    print("\n🎨 Design Critique:")
    print(f"Stated Problem: {result['output']['stated_problem']}")
    print(f"Real Problem: {result['output']['real_problem']}")

    print("\n⚠️ Major Issues:")
    for issue in result["output"]["major_issues"]:
        print(f"  - {issue}")

    print("\n✨ Improvements (by priority):")
    for improvement in result["output"]["improvements"]:
        quick_win = "⚡" if improvement["quick_win"] else "📅"
        print(f"  {quick_win} P{improvement['priority']}: {improvement['description']}")

    print("\n🧹 Boy Scout Actions:")
    for action in result["output"]["boy_scout_actions"]:
        print(f"  - {action}")


async def example_3_monetization_design():
    """Example 3: Designing a monetization system."""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Monetization Architecture")
    print("=" * 70)

    monetization_skill = MonetizationArchitectSkill()

    result = await monetization_skill.execute(
        {
            "catalog": "Online course library with 50+ hours of content",
            "audience": "5,000 email subscribers",
            "offers": ["$97 course"],
        },
    )

    print("\n💵 Monetization Architecture:")

    offers = result["output"]

    print("\n1️⃣ Core Offer (Entry):")
    print(f"   {offers['core_offer']['name']} - ${offers['core_offer']['price']}")
    print(f"   {offers['core_offer']['value_prop']}")
    print(f"   Expected Conversion: {offers['core_offer']['expected_conversion']}")

    print("\n2️⃣ Upsell:")
    print(f"   {offers['upsell']['name']} - ${offers['upsell']['price']}")
    print(f"   {offers['upsell']['value_prop']}")
    print(f"   Expected Conversion: {offers['upsell']['expected_conversion']}")

    print("\n3️⃣ Continuity:")
    print(
        f"   {offers['continuity']['name']} - ${offers['continuity']['price']}/{offers['continuity']['frequency']}",
    )
    print(f"   Expected LTV: ${offers['continuity']['expected_ltv']}")

    print("\n4️⃣ Premium:")
    print(f"   {offers['premium']['name']} - ${offers['premium']['price']}")
    print(f"   {offers['premium']['value_prop']}")
    print(f"   Expected Conversion: {offers['premium']['expected_conversion']}")

    print("\n💸 Money Left on Table:")
    for leak in offers["money_on_table"]:
        print(f"  - {leak}")


async def example_4_ultrathink_os():
    """Example 4: Using the pnkln OS master system."""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: pnkln OS Integration")
    print("=" * 70)

    # Initialize the pnkln OS
    os_instance = PnklnOS()

    # Get the master system prompt
    system_prompt = os_instance.get_system_prompt()

    print("\n🧠 Master System Prompt:")
    print(system_prompt[:500] + "...\n")

    # Assess complexity of a problem
    problem = "Design a scalable monetization system with multiple revenue streams"
    complexity = os_instance.assess_complexity(problem)
    strategy = os_instance.select_reasoning_strategy(complexity)

    print(f"📊 Problem: {problem}")
    print(f"Complexity Score: {complexity:.2f}")
    print(f"Selected Strategy: {strategy}")

    # Create an agent prompt
    agent_prompt = os_instance.create_agent_prompt(
        agent_role="Revenue Architect",
        task="Design a $1M/year revenue system",
        constraints="Must be implementable in 90 days",
        target_audience="Online course creators",
    )

    print("\n🤖 Generated Agent Prompt:")
    print(agent_prompt[:400] + "...\n")


async def main():
    """Run all examples."""
    print("\n" + "🎨" * 35)
    print("pinkln Agent Architecture System - Examples")
    print("🎨" * 35)

    await example_1_simple_skill()
    await example_2_design_review()
    await example_3_monetization_design()
    await example_4_ultrathink_os()

    print("\n" + "=" * 70)
    print("✅ All examples completed!")
    print("=" * 70)
    print("\nNext steps:")
    print("1. Explore /pinkln/docs for comprehensive documentation")
    print("2. Check /pinkln/registry/skills.yaml for all available skills")
    print("3. See /pinkln/registry/agents.yaml for agent configurations")
    print("4. Try combining multiple skills in custom agents")
    print("\n💡 Remember: Question everything. Simplify ruthlessly. Ship elegantly.\n")


if __name__ == "__main__":
    asyncio.run(main())
