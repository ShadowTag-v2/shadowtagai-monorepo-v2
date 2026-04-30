"""Business Plan Module - Usage Examples
Demonstrates querying metrics, verticals, tech stack, and context restoration
"""

from . import (
    AGENT_DESIGN,
    BUSINESS_METRICS,
    CONTEXT_RESTORATION,
    DEV_CONSTRAINTS,
    TECH_STACK,
    UNIT_ECONOMICS,
    KillSwitches,
)
from .decision_framework import RiskAssessment
from .verticals import get_current_focus, get_total_mrr


def example_1_metrics():
    """Query business metrics and unit economics"""
    print("=" * 70)
    print("EXAMPLE 1: Business Metrics Query")
    print("=" * 70)

    print("\nMonth 12 Targets:")
    print(f"  MRR: ${BUSINESS_METRICS.monthly_recurring_revenue:,}")
    print(f"  Customers: {BUSINESS_METRICS.customer_count}")
    print(f"  ARPU: ${BUSINESS_METRICS.average_revenue_per_user:,}")
    print(f"  LTV:CAC Ratio: {BUSINESS_METRICS.ltv_cac_ratio}:1")
    print(f"  Valid: {BUSINESS_METRICS.validate()}")

    print("\nUnit Economics:")
    print(f"  CAC: ${UNIT_ECONOMICS.customer_acquisition_cost:,}")
    print(f"  LTV: ${UNIT_ECONOMICS.lifetime_value:,}")
    print(f"  Monthly Cost/Customer: ${UNIT_ECONOMICS.monthly_cost_per_customer}")
    print(f"  Contribution Margin: {UNIT_ECONOMICS.contribution_margin:.1%}")
    print()


def example_2_verticals():
    """Explore revenue verticals"""
    print("=" * 70)
    print("EXAMPLE 2: Revenue Verticals")
    print("=" * 70)

    print("\nCurrent Focus (Priority 1):")
    focus = get_current_focus()
    print(f"  Name: {focus.name}")
    print(f"  Price: ${focus.monthly_price}/mo + ${focus.setup_fee} setup")
    print(f"  Target: {focus.target_customers} customers")
    print(f"  MRR: ${focus.mrr_contribution:,}")

    print("\nAll Verticals (by priority):")
    from .verticals import get_vertical_by_priority

    for v in get_vertical_by_priority():
        print(f"  {v.priority}. {v.name}")
        print(
            f"     ${v.monthly_price}/mo | {v.target_customers} customers | "
            f"${v.mrr_contribution:,} MRR",
        )

    print(f"\nTotal MRR Target: ${get_total_mrr():,}")
    print()


def example_3_tech_stack():
    """View technical architecture"""
    print("=" * 70)
    print("EXAMPLE 3: Technical Stack")
    print("=" * 70)

    print("\nCore Stack:")
    print(f"  Language: {TECH_STACK.core_language}")
    print(f"  Orchestration: {', '.join(TECH_STACK.orchestration)}")
    print(f"  LLM: {TECH_STACK.llm_provider}")
    print(f"  Cloud: {TECH_STACK.cloud_provider}")

    print("\nMemory Layer:")
    for mem_type, tech in TECH_STACK.memory_layer.items():
        print(f"  {mem_type}: {tech}")

    print("\nAgent Design:")
    print(f"  Framework: {AGENT_DESIGN.framework}")
    print(f"  Guardrails: {len(AGENT_DESIGN.guardrails)}")
    for guardrail in AGENT_DESIGN.guardrails:
        print(f"    - {guardrail}")
    print()


def example_4_risk_assessment():
    """Demonstrate ATP 5-19 risk framework"""
    print("=" * 70)
    print("EXAMPLE 4: Risk Assessment (ATP 5-19)")
    print("=" * 70)

    risk_assessor = RiskAssessment()

    scenarios = [
        ("A", "I", "Deploy untested code to production"),
        ("B", "II", "Launch new vertical without pilot"),
        ("C", "III", "Add feature without user interviews"),
        ("E", "IV", "Update documentation"),
    ]

    print("\nRisk Scenarios:")
    for prob, sev, scenario in scenarios:
        risk = risk_assessor.assess(prob, sev)
        action = risk_assessor.get_action_gate(risk)
        print(f"  [{prob}×{sev}] {scenario}")
        print(f"    Risk: {risk.value} → {action}")
    print()


def example_5_kill_switches():
    """Check kill-switch gates"""
    print("=" * 70)
    print("EXAMPLE 5: Kill-Switch Evaluation")
    print("=" * 70)

    test_cases = [
        (3, 8_000, 3, 0.0),  # Month 3: Failed
        (3, 12_000, 5, 0.0),  # Month 3: Passed
        (6, 30_000, 0, 0.0),  # Month 6: Failed
        (12, 120_000, 0, 5.2),  # Month 12: Passed
    ]

    print("\nKill-Switch Tests:")
    for month, mrr, pilots, ltv_cac in test_cases:
        should_kill, reason = KillSwitches.evaluate(month, mrr, pilots, ltv_cac)
        status = "❌ KILL" if should_kill else "✅ PASS"
        print(f"  Month {month} | ${mrr:,} MRR | {pilots} pilots | {ltv_cac:.1f} LTV:CAC")
        print(f"    {status}: {reason}")
    print()


def example_6_constraints():
    """Show development constraints"""
    print("=" * 70)
    print("EXAMPLE 6: Development Constraints")
    print("=" * 70)

    print("\nCode Quality:")
    print(f"  Max function length: {DEV_CONSTRAINTS.max_function_length} lines")
    print(f"  Min test coverage: {DEV_CONSTRAINTS.test_coverage_minimum * 100:.0f}%")
    print(
        f"  External libs: {'Approval required' if DEV_CONSTRAINTS.external_libraries_approval else 'Allowed'}",
    )

    print("\nShipping Philosophy:")
    for principle in DEV_CONSTRAINTS.shipping_philosophy:
        print(f"  • {principle}")

    print("\nGuardrails:")
    for guardrail in DEV_CONSTRAINTS.guardrails:
        print(f"  • {guardrail}")
    print()


def example_7_context_restoration():
    """Generate restart prompt"""
    print("=" * 70)
    print("EXAMPLE 7: Context Restoration")
    print("=" * 70)

    print("\nNext Action:")
    next_action = CONTEXT_RESTORATION.actions.get_next_action()
    print(f"  {next_action}")

    print("\nWeek 1 Priorities:")
    for i, priority in enumerate(
        [
            CONTEXT_RESTORATION.actions.priority_1_revenue,
            CONTEXT_RESTORATION.actions.priority_2_pipeline,
            CONTEXT_RESTORATION.actions.priority_3_infrastructure,
        ],
        1,
    ):
        print(f"  {i}. {priority['task']} ({priority['status']})")

    print("\nRestart Prompt Length:")
    prompt = CONTEXT_RESTORATION.generate_restart_prompt()
    print(f"  {len(prompt)} characters")
    print(f"  {len(prompt.split())} words")

    print("\n[First 300 chars of restart prompt]:")
    print(prompt[:300] + "...")
    print()


def run_all_examples():
    """Execute all examples"""
    example_1_metrics()
    example_2_verticals()
    example_3_tech_stack()
    example_4_risk_assessment()
    example_5_kill_switches()
    example_6_constraints()
    example_7_context_restoration()

    print("=" * 70)
    print("All examples completed successfully.")
    print("=" * 70)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        example_num = sys.argv[1]
        examples = {
            "1": example_1_metrics,
            "2": example_2_verticals,
            "3": example_3_tech_stack,
            "4": example_4_risk_assessment,
            "5": example_5_kill_switches,
            "6": example_6_constraints,
            "7": example_7_context_restoration,
        }
        if example_num in examples:
            examples[example_num]()
        else:
            print(f"Unknown example: {example_num}")
            print("Usage: python examples.py [1-7]")
    else:
        run_all_examples()
