#!/usr/bin/env python3
"""
pinkln Agent Architecture System - Claude Code Demo

This script demonstrates the full capabilities of the pinkln Agent Architecture
System running in Claude Code environment.

Usage:
    python claude_code_demo.py

Or run specific demos:
    python claude_code_demo.py --demo complexity
    python claude_code_demo.py --demo revenue
    python claude_code_demo.py --demo debate
    python claude_code_demo.py --demo all
"""

import argparse
import asyncio
import sys
from pathlib import Path

# Add pinkln to path
sys.path.insert(0, str(Path(__file__).parent))

from pinkln.core.master_system import PnklnOS
from pinkln_claude_integration import ClaudePnklnAgent


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


async def demo_complexity_assessment():
    """Demo 1: Complexity Assessment and Strategy Selection"""
    print_section("DEMO 1: Complexity Assessment & Strategy Selection")

    pinkln_os = PnklnOS()

    test_cases = [
        {
            "name": "Simple Task",
            "challenge": "Calculate the compound interest on $10,000 at 5% for 3 years.",
            "expected": "chain_of_thought",
        },
        {
            "name": "Medium Complexity",
            "challenge": """Analyze whether we should build our own authentication system or use Auth0.
            We have 3 backend developers and need to support 10,000 users.""",
            "expected": "tree_of_thoughts",
        },
        {
            "name": "High Complexity",
            "challenge": """Design a comprehensive go-to-market strategy for a new AI-powered
            project management tool. Consider: pricing, positioning, channels, competitor analysis,
            feature prioritization, and 12-month revenue targets. We have $100K marketing budget.""",
            "expected": "multi_agent_debate",
        },
    ]

    for case in test_cases:
        complexity = pinkln_os.assess_complexity(case["challenge"])
        strategy = pinkln_os.select_reasoning_strategy(complexity)

        print(f"Test: {case['name']}")
        print(f"  Complexity Score: {complexity:.2f}")
        print(f"  Selected Strategy: {strategy}")
        print(f"  Expected Strategy: {case['expected']}")
        print(f"  Match: {'✓' if strategy == case['expected'] else '✗'}")
        print()


async def demo_revenue_optimization():
    """Demo 2: Real-World Revenue Optimization"""
    print_section("DEMO 2: Revenue Optimization Analysis")

    agent = ClaudePnklnAgent()

    revenue_challenge = """
I run a B2B SaaS analytics platform with these metrics:
- 850 active companies
- $149/month average subscription
- 88% monthly retention
- $800 customer acquisition cost
- 4.5% free trial to paid conversion
- Average customer uses 60% of features

Main features: Custom dashboards, API access, team collaboration, data exports.
Competitors charge $99-$299/month.

What are my top 3 revenue optimization opportunities and what should I do this week?
"""

    print("Executing revenue optimization analysis...\n")
    result = await agent.execute(revenue_challenge, role="Monetization Architect")

    print(f"Complexity: {result['complexity']:.2f}")
    print(f"Strategy: {result['strategy']}")
    print(f"Role: {result['role']}\n")
    print(result["solution"]["content"])

    if "boy_scout_metadata" in result:
        print("\n--- Boy Scout Actions ---")
        for action in result.get("boy_scout_metadata", {}).get("cleanup_actions", []):
            print(f"  - {action}")


async def demo_design_critique():
    """Demo 3: Design Critique Workflow"""
    print_section("DEMO 3: Design Critique")

    agent = ClaudePnklnAgent()

    design_challenge = """
Review our onboarding flow for a developer tool:

1. User signs up with email/password (10 fields including company size, role, tech stack)
2. Email verification required
3. Redirect to empty dashboard with "Get Started" guide
4. Guide has 8 steps to complete before using the product
5. Average time to first value: 45 minutes
6. Only 23% of users complete onboarding

What's wrong and how do we fix it? Apply the pinkln principles ruthlessly.
"""

    result = await agent.execute(design_challenge, role="Design Critic")

    print(f"Complexity: {result['complexity']:.2f}")
    print(f"Strategy: {result['strategy']}\n")
    print(result["solution"]["content"])


async def demo_multi_agent_debate():
    """Demo 4: Multi-Agent Debate Pattern"""
    print_section("DEMO 4: Multi-Agent Debate & Synthesis")

    agent = ClaudePnklnAgent()

    complex_decision = """
Should our startup pivot from a B2C mobile app to a B2B API platform?

Context:
- Current: 120K free users, 1,200 paid subscribers at $4.99/month
- Burn rate: $45K/month
- Runway: 11 months
- Team: 2 mobile engineers, 1 backend engineer, 1 designer
- 5 enterprise companies have expressed interest at $500-$1,000/month
- Pivot would require 3-4 months of development
- Current paying users might churn
"""

    perspectives = [
        {
            "role": "Growth-Focused CEO",
            "focus": "long-term revenue potential and market opportunity",
        },
        {"role": "Cautious CFO", "focus": "financial runway, burn rate, and downside risks"},
        {
            "role": "Pragmatic CTO",
            "focus": "technical feasibility, team capacity, and execution timeline",
        },
    ]

    print("Running multi-agent debate with 3 perspectives...\n")
    result = await agent.multi_agent_debate(complex_decision, perspectives)

    for i, perspective in enumerate(result["perspectives"], 1):
        print(f"\n--- Perspective {i}: {perspective['role']} ---")
        print(f"Focus: {perspective['focus']}")
        print(f"\n{perspective['response']['solution']['content'][:500]}...\n")

    if "synthesis" in result:
        print("\n--- FINAL SYNTHESIS ---")
        print(result["synthesis"]["solution"]["content"])


async def demo_iterative_refinement():
    """Demo 5: Iterative Refinement to Excellence"""
    print_section("DEMO 5: Iterate to Excellence")

    agent = ClaudePnklnAgent()

    challenge = """
Create a cold email template for selling a new AI code review tool to engineering
managers at Series A-C startups. The tool finds bugs, suggests improvements, and
learns from team patterns.
"""

    print("Iteration 1: Initial Draft")
    print("-" * 70)
    result1 = await agent.execute(challenge, role="Copy Converter")
    print(result1["solution"]["content"][:400] + "...\n")

    print("\nIteration 2: Critique and Refine")
    print("-" * 70)
    critique_challenge = f"""
Here's an email template:
{result1["solution"]["content"]}

Apply pinkln principles to critique and improve:
1. What's missing or unclear?
2. How can we simplify ruthlessly?
3. Where do we need more obsession over details?
4. Provide an improved version.
"""
    result2 = await agent.execute(critique_challenge, role="Copy Converter (Refinement)")
    print(result2["solution"]["content"][:400] + "...\n")

    print("\nIteration 3: Final Excellence Pass")
    print("-" * 70)
    final_challenge = f"""
Previous version:
{result2["solution"]["content"]}

Final excellence pass - make this insanely great:
- Every word must earn its place
- The subject line must make them want to read
- The value prop must be immediately clear
- The CTA must be irresistible
"""
    result3 = await agent.execute(final_challenge, role="Copy Converter (Excellence)")
    print(result3["solution"]["content"])


async def demo_skills_showcase():
    """Demo 6: Individual Skills Showcase"""
    print_section("DEMO 6: Skills Showcase")

    agent = ClaudePnklnAgent()

    skills_demos = [
        {
            "skill": "research",
            "task": {"topic": "AI monetization strategies for developer tools in 2024"},
        },
        {
            "skill": "prompt",
            "task": {"goal": "create a prompt for generating product requirement documents"},
        },
        {
            "skill": "workflow",
            "task": {"process": "current CI/CD pipeline with 15-step manual deployment"},
        },
    ]

    for demo in skills_demos:
        print(f"\n--- {demo['skill'].upper()} SKILL ---")
        result = await agent.skill_execution(demo["skill"], demo["task"])
        print(f"Complexity: {result['complexity']:.2f}")
        print(f"Strategy: {result['strategy']}")
        print(f"\n{result['solution']['content'][:300]}...\n")


async def demo_session_tracking():
    """Demo 7: Session Tracking and Analytics"""
    print_section("DEMO 7: Session Tracking & Analytics")

    agent = ClaudePnklnAgent(session_id="demo-session-001")

    # Run a few challenges
    challenges = [
        "Optimize our pricing page conversion rate",
        "Design a referral program for B2B SaaS",
        "Create a growth experiment framework",
    ]

    print("Running 3 challenges to build session data...\n")
    for i, challenge in enumerate(challenges, 1):
        print(f"{i}. {challenge}")
        await agent.execute(challenge, role="Growth Strategist")

    # Get session summary
    summary = agent.get_session_summary()

    print("\n--- SESSION SUMMARY ---")
    print(f"Session ID: {summary['session_id']}")
    print(f"Duration: {summary['duration_minutes']:.2f} minutes")
    print(f"Total Calls: {summary['total_calls']}")
    print(f"Challenges Completed: {summary['challenges_completed']}")
    print("\nRecent Challenges:")
    for challenge in summary["recent_challenges"]:
        print(f"  - {challenge}...")
    print(f"\npinkln Philosophy: {summary['pinkln_philosophy']}")


async def demo_all():
    """Run all demos"""
    await demo_complexity_assessment()
    await demo_revenue_optimization()
    await demo_design_critique()
    await demo_multi_agent_debate()
    await demo_iterative_refinement()
    await demo_skills_showcase()
    await demo_session_tracking()


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="pinkln Agent Architecture System - Claude Code Demo"
    )
    parser.add_argument(
        "--demo",
        choices=["complexity", "revenue", "design", "debate", "refine", "skills", "session", "all"],
        default="all",
        help="Which demo to run",
    )

    args = parser.parse_args()

    print("\n" + "=" * 70)
    print("  pinkln Agent Architecture System™")
    print("  Claude Code Edition")
    print('  "Insanely Great AI Systems Through Elegant Orchestration"')
    print("=" * 70)

    demo_map = {
        "complexity": demo_complexity_assessment,
        "revenue": demo_revenue_optimization,
        "design": demo_design_critique,
        "debate": demo_multi_agent_debate,
        "refine": demo_iterative_refinement,
        "skills": demo_skills_showcase,
        "session": demo_session_tracking,
        "all": demo_all,
    }

    await demo_map[args.demo]()

    print("\n" + "=" * 70)
    print("  Demo Complete!")
    print("=" * 70)
    print("\n  Next Steps:")
    print("  1. Try the integration: from pinkln_claude_integration import ClaudePnklnAgent")
    print("  2. Build custom skills in pinkln/skills/")
    print("  3. Create custom agents in pinkln/agents/")
    print("  4. Explore the marketplace for more components")
    print('\n  Remember: "The people who are crazy enough to think they can')
    print('  change the world are the ones who do." 🚀\n')


if __name__ == "__main__":
    asyncio.run(main())
