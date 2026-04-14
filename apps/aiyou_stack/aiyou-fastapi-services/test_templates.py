#!/usr/bin/env python3
"""Quick test script to validate template functionality
"""

from src.models.optimization import AreaType, DoingLessBetterResults, LifeArea, OptimizationStrategy
from src.models.problem_solving import DimensionType, IsIsNotDiagram, IsIsNotDimension
from src.models.prompt_templates import (
    BABTemplate,
    CARETemplate,
    RISETemplate,
    RTFTemplate,
    TAGTemplate,
)
from src.services.template_renderer import TemplateRenderer


def test_prompt_templates():
    """Test all prompt engineering templates"""
    print("=" * 80)
    print("TESTING PROMPT ENGINEERING TEMPLATES")
    print("=" * 80)

    renderer = TemplateRenderer()

    # Test R-T-F
    print("\n1. Testing R-T-F Template...")
    rtf = RTFTemplate(
        role="Data Scientist",
        task="Analyze customer churn patterns",
        format="Detailed report with visualizations",
    )
    result = renderer.render_rtf(rtf)
    print("✓ R-T-F template rendered successfully")
    print(f"Preview:\n{result.rendered_prompt[:200]}...")

    # Test T-A-G
    print("\n2. Testing T-A-G Template...")
    tag = TAGTemplate(
        task="Improve website performance",
        action="Analyze and optimize page load times",
        goal="Reduce average load time from 3s to 1s",
    )
    result = renderer.render_tag(tag)
    print("✓ T-A-G template rendered successfully")

    # Test B-A-B
    print("\n3. Testing B-A-B Template...")
    bab = BABTemplate(
        before="Low user engagement on mobile app",
        after="Increase daily active users by 50%",
        bridge="Develop feature enhancement plan",
    )
    result = renderer.render_bab(bab)
    print("✓ B-A-B template rendered successfully")

    # Test C-A-R-E
    print("\n4. Testing C-A-R-E Template...")
    care = CARETemplate(
        context="Launching new SaaS product",
        action="Create go-to-market strategy",
        result="Achieve 1000 signups in first month",
        example="Similar to Slack's initial launch strategy",
    )
    result = renderer.render_care(care)
    print("✓ C-A-R-E template rendered successfully")

    # Test R-I-S-E
    print("\n5. Testing R-I-S-E Template...")
    rise = RISETemplate(
        role="Marketing Strategist",
        input_data="Customer survey data from 500 respondents",
        steps="Analyze data, identify patterns, create action plan",
        expectation="Increase customer satisfaction from 7 to 8.5",
    )
    result = renderer.render_rise(rise)
    print("✓ R-I-S-E template rendered successfully")

    print("\n✅ All prompt templates passed!")


def test_problem_solving():
    """Test problem-solving templates"""
    print("\n" + "=" * 80)
    print("TESTING PROBLEM SOLVING TEMPLATES")
    print("=" * 80)

    renderer = TemplateRenderer()

    # Test Is/Is Not Diagram
    print("\n1. Testing Is/Is Not Diagram...")
    diagram = IsIsNotDiagram(
        problem_description="Website performance issues",
        dimensions=[
            IsIsNotDimension(
                dimension=DimensionType.WHAT,
                is_value="Homepage slow loading",
                is_not_value="Admin panel or API endpoints",
                distinctions="Only affects customer-facing pages",
            ),
            IsIsNotDimension(
                dimension=DimensionType.WHEN,
                is_value="Peak hours 9am-5pm",
                is_not_value="Off-peak hours",
                distinctions="Correlates with traffic volume",
            ),
        ],
        timeline_notes="Started appearing last week",
        change_points=["New CDN provider", "Image optimization disabled"],
    )

    result = renderer.render_is_is_not_diagram(diagram)
    print("✓ Is/Is Not Diagram rendered successfully")
    print(f"Preview:\n{result[:300]}...")

    print("\n✅ Problem-solving templates passed!")


def test_optimization():
    """Test optimization framework"""
    print("\n" + "=" * 80)
    print("TESTING OPTIMIZATION FRAMEWORK")
    print("=" * 80)

    renderer = TemplateRenderer()

    print("\n1. Testing Doing Less Better Results...")

    health_area = LifeArea(
        area=AreaType.HEALTH_FITNESS,
        current_state="Inconsistent exercise routine",
        strategies=["Consistency beats intensity", "Aim for 3 x 30-minute sessions a week"],
        action_items=["Schedule workouts in calendar", "Join local gym", "Track progress weekly"],
        priority_level=9,
    )

    strategy = OptimizationStrategy(
        name="Q1 2024 Goals",
        description="Focus on health and productivity",
        focus_areas=[AreaType.HEALTH_FITNESS, AreaType.WORK_TASKS],
        timeline="January - March 2024",
        health_fitness=health_area,
    )

    optimization = DoingLessBetterResults(strategy=strategy)

    result = renderer.render_optimization_strategy(optimization)
    print("✓ Optimization strategy rendered successfully")
    print(f"Preview:\n{result[:300]}...")

    print("\n✅ Optimization framework passed!")


def main():
    """Run all tests"""
    try:
        test_prompt_templates()
        test_problem_solving()
        test_optimization()

        print("\n" + "=" * 80)
        print("🎉 ALL TESTS PASSED SUCCESSFULLY!")
        print("=" * 80)
        print("\nThe template system is working correctly.")
        print("You can now start the API server with: ./run.sh")
        print("Or: uvicorn src.main:app --reload")

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
