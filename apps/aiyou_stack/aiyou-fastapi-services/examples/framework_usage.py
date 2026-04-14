"""Example Usage: ShadowTag-v2JR Core Framework
Demonstrates PRISM kernel, business plan, risk assessment, and context management

Author: ShadowTag-v2JR System
Date: 2025-11-17
"""

from src.core import (
    ImmediateAction,
    KillSwitchGates,
    OperatingFramework,
    PicoTrace,
    PrismKernel,
    PrismRuntime,
    RiskProbability,
    RiskSeverity,
    StateSummary,
    TransferPackage,
    VerticalPortfolio,
)


def example_prism_runtime():
    """Example: PRISM runtime execution"""
    print("=" * 60)
    print("PRISM RUNTIME EXECUTION")
    print("=" * 60)

    # Create PiCO trace
    trace = PicoTrace(
        bind_input={"user_request": "Build Sales Agent"},
        direct_flow={"action": "initialize_development"},
        carry_motion={"status": "executing"},
        project_output={"result": "MVP created"},
    )

    # Create PRISM kernel
    kernel = PrismKernel(
        position_sequence=["Week 1", "MVP Build"],
        role_disciplines=["Engineering", "Product"],
        intent_targets=["Revenue", "Customer Acquisition"],
        structure_pipeline=["Design", "Build", "Test", "Deploy"],
        modality_modes=["Development", "Validation"],
    )

    # Initialize runtime
    runtime = PrismRuntime()
    runtime.initialize(trace, kernel)

    # Execute flow
    output = runtime.execute_flow()
    print(f"\nFlow Output: {output}")

    # Get status
    status = runtime.get_status()
    print("\nRuntime Status:")
    for key, value in status.items():
        print(f"  {key}: {value}")


def example_business_plan():
    """Example: Business plan and vertical analysis"""
    print("\n" + "=" * 60)
    print("BUSINESS PLAN ANALYSIS")
    print("=" * 60)

    portfolio = VerticalPortfolio()

    print(f"\nTotal MRR Target: ${portfolio.total_mrr():,}")
    print(f"Total Customers: {portfolio.total_customers()}")

    print("\nVertical Breakdown:")
    for v_type in portfolio.get_priority_order():
        vertical = portfolio.verticals[v_type]
        print(f"\n  {vertical.name}:")
        print(f"    Monthly Price: ${vertical.monthly_price:,}")
        print(f"    Setup Fee: ${vertical.setup_fee:,}")
        print(f"    Target Customers: {vertical.target_customers}")
        print(f"    MRR Contribution: ${vertical.mrr_contribution:,}")
        print(f"    Annual Value: ${vertical.annual_value:,}")


def example_kill_switches():
    """Example: Kill-switch gate evaluation"""
    print("\n" + "=" * 60)
    print("KILL-SWITCH EVALUATION")
    print("=" * 60)

    gates = KillSwitchGates()

    # Scenario 1: Month 3 - Failing
    print("\nScenario 1: Month 3 - Underperforming")
    triggered = gates.check_gates(month=3, mrr=7_000, pilots=3)
    if triggered:
        print(f"  ⚠️  TRIGGER: {triggered[0]}")
    else:
        print("  ✅ PASS")

    # Scenario 2: Month 3 - Passing
    print("\nScenario 2: Month 3 - On Track")
    triggered = gates.check_gates(month=3, mrr=15_000, pilots=8)
    if triggered:
        print(f"  ⚠️  TRIGGER: {triggered[0]}")
    else:
        print("  ✅ PASS")

    # Scenario 3: Month 12 - Evaluation
    print("\nScenario 3: Month 12 - Final Gate")
    triggered = gates.check_gates(month=12, mrr=125_000, ltv_cac=4.5)
    if triggered:
        print(f"  ⚠️  TRIGGER: {triggered[0]}")
    else:
        print("  ✅ PASS - Ready to scale")


def example_risk_assessment():
    """Example: Risk assessment and decision validation"""
    print("\n" + "=" * 60)
    print("RISK ASSESSMENT & DECISION PROTOCOL")
    print("=" * 60)

    framework = OperatingFramework()

    # Scenario 1: Low-risk feature deployment
    print("\nScenario 1: Deploy new analytics dashboard")
    result = framework.assess_action(
        action="Deploy analytics dashboard",
        probability=RiskProbability.D_SELDOM,
        severity=RiskSeverity.III_MODERATE,
        mission_aligned=True,
        doctrine_compliant=True,
    )
    print(f"  Risk Level: {result['risk_level']}")
    print(f"  Action Gate: {result['action_gate']}")
    print(f"  Approved: {result['approved']}")
    print(f"  Message: {result['message']}")

    # Scenario 2: High-risk security change
    print("\nScenario 2: Deploy authentication bypass (testing)")
    result = framework.assess_action(
        action="Deploy auth bypass",
        probability=RiskProbability.A_FREQUENT,
        severity=RiskSeverity.I_CATASTROPHIC,
        mission_aligned=False,
        doctrine_compliant=False,
    )
    print(f"  Risk Level: {result['risk_level']}")
    print(f"  Action Gate: {result['action_gate']}")
    print(f"  Approved: {result['approved']}")
    print(f"  Message: {result['message']}")


def example_code_validation():
    """Example: Code validation against constraints"""
    print("\n" + "=" * 60)
    print("CODE VALIDATION")
    print("=" * 60)

    framework = OperatingFramework()

    # Good code
    print("\nValidating good code:")
    result = framework.validate_code(function_lines=15, test_coverage=0.85)
    print(
        f"  Function length (15 lines): {'✅ PASS' if result['function_length_valid'] else '❌ FAIL'}",
    )
    print(f"  Test coverage (85%): {'✅ PASS' if result['test_coverage_valid'] else '❌ FAIL'}")

    # Bad code
    print("\nValidating problematic code:")
    result = framework.validate_code(function_lines=30, test_coverage=0.60)
    print(
        f"  Function length (30 lines): {'✅ PASS' if result['function_length_valid'] else '❌ FAIL'}",
    )
    print(f"  Test coverage (60%): {'✅ PASS' if result['test_coverage_valid'] else '❌ FAIL'}")
    print("\n  Constraints:")
    print(f"    Max function lines: {result['max_lines']}")
    print(f"    Min test coverage: {result['min_coverage'] * 100}%")


def example_transfer_package():
    """Example: Thread rollup and transfer package"""
    print("\n" + "=" * 60)
    print("TRANSFER PACKAGE CREATION")
    print("=" * 60)

    package = TransferPackage()

    # Create state summary
    state = StateSummary(
        what_built="AI Agent Business Plan Execution",
        core_asset=[
            "Business plan for 6 verticals",
            "Technical architecture (Python, LangGraph, GPT-4)",
            "Financial model (LTV:CAC 4:1, $120K MRR target)",
        ],
        key_verticals=[
            "Sales Automation ($1.5K/mo)",
            "Content Repurposing ($800/mo)",
            "Customer Support ($2K/mo)",
        ],
        technical_foundation={
            "stack": "Python 3.11, LangGraph, CrewAI, GPT-4 Turbo",
            "memory": "Pinecone + Redis",
            "deployment": "Vertex AI → GKE",
        },
        business_model={
            "type": "Vertical SaaS",
            "pricing": "$500-$3K/mo + setup fees",
            "target": "B2B companies with $10K+/mo repetitive work",
        },
        go_to_market={
            "phase_1": "5 pilots, $10K MRR, Sales Agent only",
            "phase_2": "20 customers, $35K MRR",
            "phase_3": "60 customers, $120K MRR",
        },
        critical_frameworks=["ATP 5-19", "SOPs A-D", "Boy Scout Rule"],
    )

    # Create immediate action
    action = ImmediateAction(
        priority=1,
        category="revenue",
        task="Build Sales Automation Agent MVP",
        subtasks=[
            "Set up Python + LangGraph + OpenAI",
            "Integrate Apollo API",
            "Build LinkedIn → Gmail flow",
            "Deploy on Vertex AI Workbench",
            "Record demo",
        ],
        deadline="End of Week 1",
    )

    # Create context
    context = package.create_context(
        state_summary=state,
        metrics={"mrr_target": 120_000, "customers": 50, "ltv_cac": 4.0},
        verticals={"sales": 1500, "content": 800},
        tech_stack={"python": "3.11", "llm": "GPT-4 Turbo"},
        kill_switches={"month_3": "<$10K MRR", "month_12": "<$100K MRR"},
        decision_framework={"purpose": "ShadowTag-v2JR", "reason": "Doctrine"},
        actions=[action],
        principles={"max_function_length": 20, "test_coverage": 0.80},
        frameworks={"ATP_5_19": "Risk matrix", "SOP_C": "Decision protocol"},
    )

    # Create restart prompt
    prompt = package.create_restart_prompt(
        project="AI Agent Business Plan Execution",
        phase="Week 1 - Sales Automation Agent MVP Build",
        context="Building portfolio of AI agents for B2B automation",
        completed=[
            "Business plan written",
            "Tech architecture defined",
            "Unit economics validated",
        ],
        focus={
            "Priority 1": "Build Sales Automation Agent MVP",
            "Priority 2": "Validate demand via X thread + DMs",
            "Priority 3": "Set up Stripe billing",
        },
        parameters={"mrr_target": 120_000, "customers": 50, "ltv_cac_min": 4.0},
        constraints=["Functions ≤20 lines", "80%+ test coverage", "Evidence-only decisions (n≥10)"],
        switches=[
            "Month 3: <5 pilots OR <$10K MRR → Pivot",
            "Month 12: <$100K MRR → Scale or sell",
        ],
        posture={"operating_mode": "strict", "iq_baseline": 160, "security": "non-negotiable"},
        question="What do you need me to do next?",
        options=[
            "Deep-dive Sales Agent architecture",
            "Draft landing page copy",
            "Write X thread template",
            "Build Stripe integration",
        ],
    )

    # Validate
    validation = package.validate()
    print("\nValidation Results:")
    for check, passed in validation.items():
        status = "✅" if passed else "❌"
        print(f"  {status} {check}")

    # Get complete package
    full_package = package.get_package()
    print(f"\nPackage Generated: {full_package['generated']}")
    print(f"Compression Ratio: {full_package['compression_ratio']}")

    # Save to file
    output_file = "/home/user/shadowtag_v4-fastapi-services/transfer_package.json"
    package.save_to_file(output_file)
    print(f"\n✅ Transfer package saved to: {output_file}")


def main():
    """Run all examples"""
    example_prism_runtime()
    example_business_plan()
    example_kill_switches()
    example_risk_assessment()
    example_code_validation()
    example_transfer_package()

    print("\n" + "=" * 60)
    print("ALL EXAMPLES COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()
