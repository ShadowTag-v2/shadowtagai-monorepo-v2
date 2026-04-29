#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""pinkln Infrastructure Analysis Demo

This script demonstrates the infrastructure analysis capabilities for the
PNKLN Core Stack™, including Judge 6 and Gemini Ingestion Layer analysis.

Usage:
    python pnkln_infrastructure_demo.py

Or run specific demos:
    python pnkln_infrastructure_demo.py --demo judge
    python pnkln_infrastructure_demo.py --demo ingestion
    python pnkln_infrastructure_demo.py --demo compare
    python pnkln_infrastructure_demo.py --demo pipeline
    python pnkln_infrastructure_demo.py --demo optimize
    python pnkln_infrastructure_demo.py --demo cost
    python pnkln_infrastructure_demo.py --demo all
"""

import argparse
import asyncio
import sys
from pathlib import Path

# Add pinkln to path
sys.path.insert(0, str(Path(__file__).parent))

from pinkln.agents.infrastructure_agent import InfrastructureAgent
from pinkln.skills.infrastructure_analysis import InfrastructureAnalysisSkill


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def print_subsection(title: str):
    """Print a formatted subsection header."""
    print("\n" + "-" * 70)
    print(f"  {title}")
    print("-" * 70)


async def demo_Claude_Code_6_analysis():
    """Demo 1: Analyze Judge 6 System"""
    print_section("DEMO 1: Judge 6 Analysis")

    agent = InfrastructureAgent()
    result = await agent.analyze_Claude_Code_6()

    print(f"System: {result['system']}")
    print(f"Type: {result['type']}")

    analysis = result["analysis"]["core_analysis"]

    print_subsection("Strengths")
    for i, strength in enumerate(analysis["strengths"], 1):
        print(f"{i}. {strength}")

    print_subsection("Weaknesses")
    for i, weakness in enumerate(analysis["weaknesses"], 1):
        print(f"{i}. {weakness}")

    print_subsection("Recommendations")
    for i, rec in enumerate(analysis["recommendations"][:5], 1):
        print(f"{i}. {rec}")

    print_subsection("pinkln Insights")
    pinkln_insights = result["analysis"]["pinkln_enhancements"]
    print("\nQuestion Everything:")
    for q in pinkln_insights["question_everything"][:2]:
        print(f"  • {q}")

    print("\nSimplify Ruthlessly:")
    for s in pinkln_insights["simplify_ruthlessly"][:2]:
        print(f"  • {s}")

    print_subsection("Next Steps")
    for step in result["next_steps"]:
        print(f"{step['priority']}: {step['action']} ({step['timeline']})")

    print(f"\nConfidence Score: {analysis['confidence']:.2%}")


async def demo_gemini_ingestion_analysis():
    """Demo 2: Analyze Gemini Ingestion Layer"""
    print_section("DEMO 2: Gemini Ingestion Layer Analysis")

    agent = InfrastructureAgent()
    result = await agent.analyze_gemini_ingestion()

    print(f"System: {result['system']}")
    print(f"Type: {result['type']}")

    analysis = result["analysis"]["core_analysis"]

    print_subsection("Strengths")
    for i, strength in enumerate(analysis["strengths"], 1):
        print(f"{i}. {strength}")

    print_subsection("Key Recommendations")
    for i, rec in enumerate(analysis["recommendations"][:5], 1):
        print(f"{i}. {rec}")

    print_subsection("Optimizations")
    for i, opt in enumerate(analysis.get("optimizations", [])[:3], 1):
        print(f"{i}. {opt}")

    print_subsection("pinkln Philosophy Application")
    pinkln_insights = result["analysis"]["pinkln_enhancements"]

    print("\nObsess Over Details - Edge Cases:")
    for edge in pinkln_insights["obsess_over_details"][:3]:
        print(f"  • {edge}")

    print("\nIterate Relentlessly - Improvement Plan:")
    for iteration in pinkln_insights["iterate_relentlessly"][:3]:
        print(f"  • {iteration}")

    print(f"\nConfidence Score: {analysis['confidence']:.2%}")
    print("Note: Pre-production system - lower confidence is expected")


async def demo_comparative_analysis():
    """Demo 3: Comparative Analysis"""
    print_section("DEMO 3: Comparative Analysis - Judge 6 vs Gemini Ingestion")

    agent = InfrastructureAgent()
    result = await agent.comparative_analysis()

    print(f"Comparison Type: {result['comparison_type']}")

    analysis = result["analysis"]

    print_subsection("Role Contrast")
    role_contrast = analysis["role_contrast"]
    print(f"Judge 6: {role_contrast['Judge 6']}")
    print(f"Gemini Ingestion Layer: {role_contrast['Gemini Ingestion Layer']}")
    print(f"\nRelationship: {role_contrast['relationship']}")

    print_subsection("Metric Comparison")
    metric_comp = analysis["metric_comparison"]
    print(f"Focus Shift Insight: {metric_comp['focus_shift']['insight']}")
    print(f"Cost Model Insight: {metric_comp['cost_model']['insight']}")

    print_subsection("Architecture Comparison")
    arch_comp = analysis["architecture_comparison"]
    print("\nInsights:")
    for insight in arch_comp["insights"]:
        print(f"  • {insight}")

    print_subsection("pinkln Insights")
    if "pinkln_insights" in analysis:
        print("\nComplementary Strengths:")
        for strength in analysis["pinkln_insights"]["complementary_strengths"]:
            print(f"  • {strength}")

        print("\nIntegration Optimizations:")
        for opt in analysis["pinkln_insights"]["integration_optimizations"]:
            print(f"  • {opt}")

    print_subsection("Integration Opportunities")
    for opp in result["integration_opportunities"]:
        print(f"\n{opp['opportunity']}:")
        print(f"  Description: {opp['description']}")
        print(f"  Benefit: {opp['benefit']}")


async def demo_full_pipeline_analysis():
    """Demo 4: Full Pipeline Analysis"""
    print_section("DEMO 4: Full Pipeline Analysis")

    agent = InfrastructureAgent()
    result = await agent.analyze_full_pipeline()

    print(f"Pipeline: {result['pipeline']}")

    print_subsection("Components")
    for component_name in result["components"]:
        component = result["components"][component_name]
        analysis = component["analysis"]["core_analysis"]
        print(f"\n{component['system']}:")
        print(f"  Strengths: {len(analysis['strengths'])}")
        print(f"  Recommendations: {len(analysis['recommendations'])}")
        print(f"  Confidence: {analysis['confidence']:.2%}")

    print_subsection("Bottlenecks Identified")
    for i, bottleneck in enumerate(result["bottlenecks"], 1):
        print(f"\n{i}. {bottleneck['location']}")
        print(f"   Issue: {bottleneck['issue']}")
        print(f"   Mitigation: {bottleneck['mitigation']}")

    print_subsection("Optimization Plan")
    opt_plan = result["optimization_plan"]
    print("\nPhase 1 - Quick Wins:")
    for i, action in enumerate(opt_plan["phase_1_quick_wins"], 1):
        print(f"  {i}. {action}")

    print("\nPhase 2 - Improvements:")
    for i, action in enumerate(opt_plan["phase_2_improvements"], 1):
        print(f"  {i}. {action}")

    print_subsection("Cost Breakdown")
    costs = result["cost_breakdown"]
    print(f"Current Monthly: {costs['current_monthly']}")
    print(f"With Optimizations: {costs['with_optimizations']}")
    print(f"Potential Annual Savings: {costs['potential_savings']}")

    print_subsection("Recommended SLAs")
    for sla in result["sla_recommendations"]:
        print(f"\n{sla['metric']}:")
        print(f"  Target: {sla['target']}")
        print(f"  Monitoring: {sla['monitoring']}")


async def demo_optimize_infrastructure():
    """Demo 5: Infrastructure Optimization Recommendations"""
    print_section("DEMO 5: Infrastructure Optimization")

    agent = InfrastructureAgent()
    result = await agent.optimize_infrastructure()

    print_subsection("Quick Wins (< 1 week)")
    for i, qw in enumerate(result["quick_wins"], 1):
        print(f"\n{i}. {qw['action']}")
        print(f"   Impact: {qw['impact']}")
        print(f"   Effort: {qw['effort']}")

    print_subsection("Medium-Term Optimizations (1-4 weeks)")
    for i, mt in enumerate(result["medium_term"], 1):
        print(f"\n{i}. {mt['action']}")
        print(f"   Impact: {mt['impact']}")
        print(f"   Effort: {mt['effort']}")

    print_subsection("Strategic Initiatives (1-3 months)")
    for i, st in enumerate(result["strategic"][:3], 1):
        print(f"\n{i}. {st['action']}")
        print(f"   Impact: {st['impact']}")
        print(f"   Effort: {st['effort']}")

    print_subsection("Estimated Impact")
    impact = result["estimated_impact"]
    print(f"Cost Reduction: {impact['cost_reduction']}")
    print(f"Performance Improvement: {impact['performance_improvement']}")
    print(f"Quality Improvement: {impact['quality_improvement']}")
    print(f"Developer Productivity: {impact['developer_productivity']}")


async def demo_cost_analysis():
    """Demo 6: Cost Analysis"""
    print_section("DEMO 6: Cost Analysis")

    agent = InfrastructureAgent()
    result = await agent.cost_analysis()

    print_subsection("Current Monthly Costs")
    for system, details in result["current_monthly_costs"].items():
        if system == "total_stack":
            continue
        print(f"\n{system.replace('_', ' ').title()}:")
        if "breakdown" in details:
            for component, cost in details["breakdown"].items():
                print(f"  {component}: {cost}")
        if "total" in details:
            print(f"  Total: {details['total']}")
        elif "estimated" in details:
            print(f"  Estimated: {details['estimated']}")

    print(f"\nTotal Stack Cost: {result['current_monthly_costs']['total_stack']}")

    print_subsection("Optimization Opportunities")
    for i, opp in enumerate(result["optimization_opportunities"], 1):
        print(f"\n{i}. {opp['item']}")
        print(f"   Savings: {opp['savings']}")
        print(f"   Percentage: {opp['percentage']}")

    print_subsection("Cost Summary")
    print(f"Potential Monthly Cost: {result['potential_monthly_cost']}")
    print(f"Annual Savings: {result['annual_savings']}")


async def demo_gemini_prompt_generation():
    """Demo 7: Generate Gemini 2.0 Pro Analysis Prompts"""
    print_section("DEMO 7: Gemini 2.0 Pro Prompt Generation")

    skill = InfrastructureAnalysisSkill()

    print("Generating analysis prompts for Gemini 2.0 Pro...\n")

    print_subsection("Judge 6 Analysis Prompt")
    judge_prompt = skill.generate_gemini_prompt(skill.Claude_Code_6_SPEC)
    print(judge_prompt[:500] + "...")
    print(f"\nTotal length: {len(judge_prompt)} characters")

    print_subsection("Gemini Ingestion Layer Analysis Prompt")
    ingestion_prompt = skill.generate_gemini_prompt(
        skill.GEMINI_INGESTION_SPEC,
        include_sections=["architecture", "metrics", "compliance", "optimization"],
    )
    print(ingestion_prompt[:500] + "...")
    print(f"\nTotal length: {len(ingestion_prompt)} characters")

    # Save prompts to files
    output_dir = Path("./analysis_prompts")
    output_dir.mkdir(exist_ok=True)

    with open(output_dir / "Claude_Code_6_analysis.md", "w") as f:
        f.write(judge_prompt)

    with open(output_dir / "gemini_ingestion_analysis.md", "w") as f:
        f.write(ingestion_prompt)

    print(f"\n✓ Prompts saved to {output_dir}/")
    print("  - Claude_Code_6_analysis.md")
    print("  - gemini_ingestion_analysis.md")


async def demo_all():
    """Run all demos"""
    await demo_Claude_Code_6_analysis()
    await demo_gemini_ingestion_analysis()
    await demo_comparative_analysis()
    await demo_full_pipeline_analysis()
    await demo_optimize_infrastructure()
    await demo_cost_analysis()
    await demo_gemini_prompt_generation()


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="pinkln Infrastructure Analysis Demo - PNKLN Core Stack™",
    )
    parser.add_argument(
        "--demo",
        choices=["judge", "ingestion", "compare", "pipeline", "optimize", "cost", "prompt", "all"],
        default="all",
        help="Which demo to run",
    )
    parser.add_argument("--export", action="store_true", help="Export results to JSON file")

    args = parser.parse_args()

    print("\n" + "=" * 70)
    print("  pinkln Agent Architecture System™")
    print("  PNKLN Core Stack™ Infrastructure Analysis")
    print('  "Insanely Great Infrastructure Through Systematic Analysis"')
    print("=" * 70)

    demo_map = {
        "judge": demo_Claude_Code_6_analysis,
        "ingestion": demo_gemini_ingestion_analysis,
        "compare": demo_comparative_analysis,
        "pipeline": demo_full_pipeline_analysis,
        "optimize": demo_optimize_infrastructure,
        "cost": demo_cost_analysis,
        "prompt": demo_gemini_prompt_generation,
        "all": demo_all,
    }

    await demo_map[args.demo]()

    print("\n" + "=" * 70)
    print("  Demo Complete!")
    print("=" * 70)
    print("\n  Next Steps:")
    print("  1. Review the analysis output above")
    print("  2. Check PNKLN_STACK_GUIDE.md for detailed usage")
    print("  3. Implement recommended quick wins")
    print("  4. Set up weekly infrastructure reviews")
    print("  5. Monitor cost and performance improvements")
    print("\n  Integration Options:")
    print("  • Use with Claude Code: See CLAUDE_CODE_GUIDE.md")
    print("  • Use with Vertex AI: See VERTEX_WORKBENCH_GUIDE.md")
    print('\n  Remember: "The people who are crazy enough to think they can')
    print('  change the world are the ones who do." 🚀\n')


if __name__ == "__main__":
    asyncio.run(main())
