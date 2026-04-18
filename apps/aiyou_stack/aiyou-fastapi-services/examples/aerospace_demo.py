#!/usr/bin/env python3
"""Aerospace Module Demo
=====================

Demonstrates the Cor.19 Aerospace Expansion capabilities:
- Business plan modeling
- Enterprise valuation with Monte Carlo
- Edge mesh architecture
- ROI calculations
"""

from src.aerospace import (
    AerospaceBusinessPlan,
    EdgeMeshArchitecture,
    EnterpriseValuationModel,
    ROICalculator,
)
from src.aerospace.economics import DeploymentConfig


def demo_business_plan():
    """Demonstrate business plan generation"""
    print("\n" + "=" * 70)
    print("AEROSPACE BUSINESS PLAN - 7 PHASES (2025-2031)")
    print("=" * 70 + "\n")

    plan = AerospaceBusinessPlan()

    # Display all phases
    for phase in plan.phases:
        print(f"Phase {phase.number}: {phase.name} ({phase.quarter} {phase.year})")
        print(f"  Objective: {phase.objective}")
        print(f"  Investment: ${phase.estimated_cost_usd:,.0f}")
        print(f"  Expected Contracts: ${phase.expected_contracts_usd:,.0f}")
        print(f"  Post-Phase Valuation: ${phase.post_phase_valuation_usd:,.0f}")
        print(f"  ROI: {phase.roi:.1%}")
        print()

    # Financial summary
    summary = plan.financial_summary
    print("\nFINANCIAL SUMMARY (2025-2030):")
    print(f"  Total Investment: ${summary.total_investment_usd:,.0f}")
    print(f"  Cumulative ARR: ${summary.cumulative_arr_usd:,.0f}")
    print(f"  Aggregate Valuation: ${summary.aggregate_valuation_usd:,.0f}")
    print(f"  Integrated Uplift: ${summary.integrated_uplift_usd:,.0f}")
    print(f"  Founder Equity (60%): ${summary.founder_retained_value_usd:,.0f}")
    print(f"  Total Return: {summary.total_return_multiple:.1f}x")


def demo_enterprise_valuation():
    """Demonstrate enterprise valuation with Monte Carlo"""
    print("\n" + "=" * 70)
    print("ENTERPRISE VALUATION MODEL (2030)")
    print("=" * 70 + "\n")

    valuation = EnterpriseValuationModel(target_year=2030)

    # Division breakdown
    print("DIVISIONS:")
    for key, div in valuation.divisions.items():
        val = valuation.calculate_division_value(key)
        print(f"  {div.name}:")
        print(f"    ARR: ${div.arr_usd:,.0f}")
        print(f"    EBITDA Margin: {div.ebitda_margin:.1%}")
        print(f"    Valuation: ${val:,.0f}")
        print(f"    Contribution: {div.contribution_percent:.1f}%")
        print()

    # Monte Carlo simulation
    print("\nMONTE CARLO SIMULATION (10,000 iterations):")
    mc = valuation.run_monte_carlo()
    print(f"  10th Percentile (Bear): ${mc.percentile_10:,.0f}")
    print(f"  50th Percentile (Base): ${mc.percentile_50:,.0f}")
    print(f"  90th Percentile (Bull): ${mc.percentile_90:,.0f}")
    print(f"  Mean: ${mc.mean:,.0f}")
    print(f"  Std Dev: ${mc.std_dev:,.0f}")
    print(f"\n  Probability ≥ $12B: {mc.probability_above_threshold.get(12_000_000_000, 0):.1%}")
    print(f"  Probability ≥ $20B: {mc.probability_above_threshold.get(20_000_000_000, 0):.1%}")

    # Founder value
    print("\nFOUNDER VALUE (60% equity):")
    founder = valuation.calculate_founder_value()
    print(f"  Enterprise Value: ${founder['total_enterprise_value_usd']:,.0f}")
    print(f"  Founder Equity: ${founder['founder_equity_value_usd']:,.0f}")
    print(f"  Annual Cash Flow: ${founder['founder_annual_cash_usd']:,.0f}")


def demo_edge_mesh():
    """Demonstrate edge mesh architecture"""
    print("\n" + "=" * 70)
    print("EDGE MESH ARCHITECTURE - Starlink + CoreWeave + Tesla")
    print("=" * 70 + "\n")

    mesh = EdgeMeshArchitecture()

    # Deploy regional network
    print("Deploying regional network: 100 towers + 10,000 vehicles\n")

    for i in range(100):
        mesh.add_tower_node(
            tower_id=f"TOWER-US-{i:04d}",
            location={"lat": 37.7 + (i % 10) * 0.1, "lon": -122.4 + (i // 10) * 0.1},
            gpu_config="l40s_dual",
            uplink_config="starlink_standard",
            coverage_radius_km=5.0,
        )

    for i in range(10_000):
        mesh.add_vehicle_node(vehicle_id=f"TESLA-HW6-{i:06d}", hw_version="HW6")

    # Architecture stats
    print("ARCHITECTURE STATS:")
    print(f"  Cell Tower Nodes: {len(mesh.tower_nodes)}")
    print(f"  Vehicle Nodes: {len(mesh.vehicle_nodes)}")
    print(f"  Total Compute: {mesh.calculate_total_compute_tflops():,.0f} TFLOPS")
    print(f"  Coverage Area: {mesh.calculate_coverage_area_km2():,.0f} km²")

    # Economics
    print("\nECONOMICS:")
    print(f"  Monthly OPEX: ${mesh.calculate_monthly_opex_usd():,.0f}")
    print(f"  Monthly Revenue: ${mesh.calculate_monthly_revenue_usd():,.0f}")

    # Latency improvement
    print("\nLATENCY IMPROVEMENT:")
    latency = mesh.estimate_latency_improvement_vs_cloud()
    print(f"  Cloud Baseline: {latency['cloud_baseline_ms']:.0f}ms")
    print(f"  Edge Mesh: {latency['edge_mesh_ms']:.0f}ms")
    print(f"  Improvement: {latency['improvement_percent']:.1f}% faster")

    # Starlink enhancement
    print("\nSTARLINK ENHANCEMENT:")
    starlink = mesh.calculate_starlink_latency_reduction()
    print(f"  Starlink Only: {starlink['starlink_baseline_ms']:.0f}ms")
    print(f"  + Tower GPU: {starlink['with_tower_gpu_ms']:.0f}ms")
    print(f"  Reduction: {starlink['reduction_percent']:.1f}%")

    # ROI projection
    print("\nROI PROJECTION (36 months):")
    roi = mesh.project_deployment_roi(num_towers=100, num_vehicles=10_000, months=36)
    print(f"  Total CAPEX: ${roi['investment']['total_capex_usd']:,.0f}")
    print(f"  Monthly OPEX: ${roi['investment']['monthly_opex_usd']:,.0f}")
    print(f"  Monthly Revenue: ${roi['revenue']['monthly_revenue_usd']:,.0f}")
    print(f"  Net Profit (36mo): ${roi['returns']['net_profit_usd']:,.0f}")
    print(f"  ROI Multiple: {roi['returns']['roi_multiple']:.2f}x")
    print(f"  Payback Period: {roi['returns']['payback_period_months']:.1f} months")
    print(f"  Gross Margin: {roi['returns']['gross_margin_percent']:.1f}%")


def demo_roi_calculator():
    """Demonstrate ROI calculator across deployment scales"""
    print("\n" + "=" * 70)
    print("ROI CALCULATOR - Deployment Scenarios")
    print("=" * 70 + "\n")

    # National scale deployment
    config = DeploymentConfig(
        num_cell_towers=20_000,
        num_vehicles=1_000_000,
        num_satellites=20,
        deployment_months=36,
    )

    calculator = ROICalculator(config)

    # Show all scenarios
    scenarios = calculator.export_summary()

    print("DEPLOYMENT SCENARIOS:\n")

    for scenario_name, scenario_data in scenarios["scenarios"].items():
        print(f"{scenario_name.upper()}:")
        print(f"  Total Investment: ${scenario_data['investment']['total_investment_usd']:,.0f}")
        print(f"  Cumulative Revenue: ${scenario_data['revenue']['cumulative_revenue_usd']:,.0f}")
        print(f"  Net Profit: ${scenario_data['returns']['net_profit_usd']:,.0f}")
        print(f"  ROI: {scenario_data['returns']['roi_percent']:.1f}%")
        print(f"  Payback: {scenario_data['returns']['payback_period_months']:.1f} months")
        print(f"  Gross Margin: {scenario_data['returns']['gross_margin_percent']:.1f}%")
        print()

    # Valuation curve
    print("\nVALUATION GROWTH CURVE:")
    for phase in scenarios["valuation_curve"]:
        print(f"  {phase['phase']:10s} ({phase['months']:2d} mo): ${phase['valuation_usd']:>12,}")


def main():
    """Run all demos"""
    print("\n" + "=" * 70)
    print("COR.19 AEROSPACE EXPANSION - COMPREHENSIVE DEMO")
    print("=" * 70)

    try:
        demo_business_plan()
        demo_enterprise_valuation()
        demo_edge_mesh()
        demo_roi_calculator()

        print("\n" + "=" * 70)
        print("DEMO COMPLETE")
        print("=" * 70 + "\n")

        print("Next Steps:")
        print("  1. Review docs/aerospace/COR-19-AEROSPACE-PLAN.md")
        print("  2. Execute Q4 2025 foundation setup ($150k)")
        print("  3. Apply for NASA UAM and FAA CLEEN grants")
        print("  4. Secure CoreWeave GPU credits")
        print("  5. Begin AiJR Aviation Kernel development (Q1 2026)")
        print("\nStatus: ✅ Ready for Implementation\n")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
