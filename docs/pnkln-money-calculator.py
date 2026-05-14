#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
PNKLN Ultrathink Money Calculator

Calculates financial impact across 6 technical work streams and integrated platform.
Run scenarios, adjust assumptions, project exit valuations.

Usage:
    python docs/pnkln-money-calculator.py
    python docs/pnkln-money-calculator.py --conservative
    python docs/pnkln-money-calculator.py --aggressive
"""

import argparse
from dataclasses import dataclass
from typing import Dict


@dataclass
class WorkStream:
    name: str
    arr: float
    margin: float
    cost_savings: float = 0

    @property
    def profit(self) -> float:
        return (self.arr * self.margin) + self.cost_savings

    @property
    def total_impact(self) -> float:
        return self.arr + self.cost_savings


def calculate_10fingers_score(scores: dict[str, int]) -> float:
    """Calculate 10 Fingers weighted viability score"""
    weights = {
        "MarketDemand": 1.3,
        "OfferMix": 1.1,
        "TechLeverage": 1.1,
        "DistributionDensity": 1.1,
        "PricingPower": 1.0,
        "LaborTraining": 1.1,
        "Marketing": 1.0,
        "RiskCompliance": 1.0,
        "ScalingModel": 1.1,
        "ExitAsset": 1.0,
    }

    weighted_sum = sum(scores[k] * weights[k] for k in scores)
    max_possible = sum(10 * weights[k] for k in weights)

    return round(100 * weighted_sum / max_possible, 1)


def calculate_baseline_scenario() -> dict:
    """Baseline: Realistic market penetration assumptions"""

    work_streams = {
        "kernel_chaining": WorkStream(
            name="Kernel Chaining Architecture",
            arr=2_310_000,  # 70% of $3.3M potential
            margin=0.80,
        ),
        "gemini_migration": WorkStream(name="Autogen → Gemini Migration", arr=420_000, margin=0.90, cost_savings=102_000),
        "superpowers_marketplace": WorkStream(name="Superpowers Marketplace", arr=1_152_000, margin=0.76),
        "intelligence_pipeline": WorkStream(
            name="PNKLN Intelligence Pipeline",
            arr=936_000,  # 60% of $1.56M potential
            margin=0.44,
        ),
        "devtools": WorkStream(name="Cursor/ESLint Hybrid", arr=330_000, margin=0.73, cost_savings=225_000),
        "llm_serving": WorkStream(name="LLM Serving Efficiency", arr=1_020_000, margin=0.60, cost_savings=120_000),
    }

    # Baseline existing ventures
    baseline_ventures = {
        "swiper": WorkStream(
            name="Swiper Platform",
            arr=480_000,  # 10 retailers @ $4K/mo
            margin=0.65,
        ),
        "ai_agents": WorkStream(
            name="AI Agent Platform",
            arr=1_440_000,  # $120K MRR
            margin=0.75,
        ),
    }

    return {"work_streams": work_streams, "baseline_ventures": baseline_ventures}


def calculate_conservative_scenario() -> dict:
    """Conservative: 50% penetration, lower margins"""

    work_streams = {
        "kernel_chaining": WorkStream(
            name="Kernel Chaining Architecture",
            arr=1_650_000,  # 50% of potential
            margin=0.70,
        ),
        "gemini_migration": WorkStream(name="Autogen → Gemini Migration", arr=210_000, margin=0.85, cost_savings=80_000),
        "superpowers_marketplace": WorkStream(name="Superpowers Marketplace", arr=576_000, margin=0.65),
        "intelligence_pipeline": WorkStream(name="PNKLN Intelligence Pipeline", arr=468_000, margin=0.35),
        "devtools": WorkStream(name="Cursor/ESLint Hybrid", arr=165_000, margin=0.65, cost_savings=150_000),
        "llm_serving": WorkStream(name="LLM Serving Efficiency", arr=510_000, margin=0.50, cost_savings=90_000),
    }

    baseline_ventures = {
        "swiper": WorkStream(
            name="Swiper Platform",
            arr=240_000,  # 5 retailers
            margin=0.55,
        ),
        "ai_agents": WorkStream(
            name="AI Agent Platform",
            arr=960_000,  # $80K MRR
            margin=0.70,
        ),
    }

    return {"work_streams": work_streams, "baseline_ventures": baseline_ventures}


def calculate_aggressive_scenario() -> dict:
    """Aggressive: 90% penetration, premium pricing"""

    work_streams = {
        "kernel_chaining": WorkStream(
            name="Kernel Chaining Architecture",
            arr=4_620_000,  # 2× baseline (enterprise focus)
            margin=0.85,
        ),
        "gemini_migration": WorkStream(name="Autogen → Gemini Migration", arr=800_000, margin=0.92, cost_savings=120_000),
        "superpowers_marketplace": WorkStream(name="Superpowers Marketplace", arr=2_304_000, margin=0.80),
        "intelligence_pipeline": WorkStream(name="PNKLN Intelligence Pipeline", arr=1_872_000, margin=0.50),
        "devtools": WorkStream(name="Cursor/ESLint Hybrid", arr=600_000, margin=0.78, cost_savings=300_000),
        "llm_serving": WorkStream(name="LLM Serving Efficiency", arr=2_040_000, margin=0.68, cost_savings=150_000),
    }

    baseline_ventures = {
        "swiper": WorkStream(
            name="Swiper Platform",
            arr=960_000,  # 20 retailers
            margin=0.70,
        ),
        "ai_agents": WorkStream(
            name="AI Agent Platform",
            arr=2_400_000,  # $200K MRR
            margin=0.80,
        ),
    }

    return {"work_streams": work_streams, "baseline_ventures": baseline_ventures}


def print_scenario_analysis(scenario_name: str, data: dict):
    """Print financial analysis for a scenario"""

    print("=" * 80)
    print(f"PNKLN ULTRATHINK MONEY ANALYSIS - {scenario_name.upper()} SCENARIO")
    print("=" * 80)
    print()

    # Work streams analysis
    print("📊 WORK STREAMS REVENUE BREAKDOWN")
    print("-" * 80)

    total_arr = 0
    total_profit = 0

    for ws in data["work_streams"].values():
        total_arr += ws.arr
        total_profit += ws.profit

        print(f"{ws.name:40} | ARR: ${ws.arr:>12,.0f} | Profit: ${ws.profit:>12,.0f} | Margin: {ws.margin:.0%}")
        if ws.cost_savings > 0:
            print(f"{'':40} | Cost Savings: ${ws.cost_savings:>12,.0f}")

    print("-" * 80)
    print(f"{'WORK STREAMS TOTAL':40} | ARR: ${total_arr:>12,.0f} | Profit: ${total_profit:>12,.0f}")
    print()

    # Baseline ventures
    print("📊 BASELINE VENTURES (Swiper + AI Agents)")
    print("-" * 80)

    baseline_arr = 0
    baseline_profit = 0

    for bv in data["baseline_ventures"].values():
        baseline_arr += bv.arr
        baseline_profit += bv.profit

        print(f"{bv.name:40} | ARR: ${bv.arr:>12,.0f} | Profit: ${bv.profit:>12,.0f} | Margin: {bv.margin:.0%}")

    print("-" * 80)
    print(f"{'BASELINE TOTAL':40} | ARR: ${baseline_arr:>12,.0f} | Profit: ${baseline_profit:>12,.0f}")
    print()

    # Integrated platform
    print("🎯 INTEGRATED PLATFORM (Work Streams + Baseline)")
    print("-" * 80)

    integrated_arr = total_arr + baseline_arr
    integrated_profit = total_profit + baseline_profit
    integrated_margin = integrated_profit / integrated_arr if integrated_arr > 0 else 0

    print(f"{'Total ARR':40} | ${integrated_arr:>12,.0f}")
    print(f"{'Total Profit':40} | ${integrated_profit:>12,.0f}")
    print(f"{'Blended Margin':40} | {integrated_margin:>12.1%}")
    print()

    # Exit valuation
    print("💰 EXIT VALUATION ESTIMATES")
    print("-" * 80)

    valuation_10x_arr = integrated_arr * 10
    valuation_15x_profit = integrated_profit * 15
    valuation_blended = (valuation_10x_arr + valuation_15x_profit) / 2

    print(f"{'10× ARR Multiple':40} | ${valuation_10x_arr:>12,.0f}")
    print(f"{'15× Profit Multiple':40} | ${valuation_15x_profit:>12,.0f}")
    print(f"{'Blended (Average)':40} | ${valuation_blended:>12,.0f}")
    print()

    # 10 Fingers score
    print("📈 10 FINGERS VIABILITY SCORE")
    print("-" * 80)

    if scenario_name == "baseline":
        scores = {
            "MarketDemand": 9,
            "OfferMix": 9,
            "TechLeverage": 9,
            "DistributionDensity": 8,
            "PricingPower": 9,
            "LaborTraining": 7,
            "Marketing": 8,
            "RiskCompliance": 8,
            "ScalingModel": 8,
            "ExitAsset": 8,
        }
    elif scenario_name == "conservative":
        scores = {
            "MarketDemand": 7,
            "OfferMix": 7,
            "TechLeverage": 8,
            "DistributionDensity": 8,
            "PricingPower": 7,
            "LaborTraining": 6,
            "Marketing": 6,
            "RiskCompliance": 7,
            "ScalingModel": 6,
            "ExitAsset": 6,
        }
    else:  # aggressive
        scores = {
            "MarketDemand": 10,
            "OfferMix": 10,
            "TechLeverage": 10,
            "DistributionDensity": 9,
            "PricingPower": 10,
            "LaborTraining": 8,
            "Marketing": 9,
            "RiskCompliance": 8,
            "ScalingModel": 9,
            "ExitAsset": 9,
        }

    viability_score = calculate_10fingers_score(scores)

    for finger, score in scores.items():
        status = "✅" if score >= 8 else "⚠️" if score >= 6 else "❌"
        print(f"{finger:25} | {score:2}/10 | {status}")

    print("-" * 80)
    print(f"{'FINAL VIABILITY SCORE':40} | {viability_score:>12.1f} / 100")

    if viability_score >= 75.0:
        verdict = "🟢 GO"
    elif viability_score >= 60.0:
        verdict = "🟡 CONDITIONAL"
    else:
        verdict = "🔴 HOLD"

    print(f"{'VERDICT':40} | {verdict}")
    print()

    # Summary
    print("=" * 80)
    print(f"SUMMARY: {scenario_name.upper()} SCENARIO")
    print("=" * 80)
    print(f"Total ARR: ${integrated_arr:,.0f}")
    print(f"Net Profit: ${integrated_profit:,.0f} ({integrated_margin:.1%} margin)")
    print(f"Exit Valuation: ${valuation_blended:,.0f} (blended)")
    print(f"Viability Score: {viability_score}/100 ({verdict})")
    print()


def print_comparison_table(scenarios: dict):
    """Print comparison table across all scenarios"""

    print("=" * 80)
    print("SCENARIO COMPARISON")
    print("=" * 80)
    print()

    # Calculate totals for each scenario
    results = {}

    for name, data in scenarios.items():
        ws_arr = sum(ws.arr for ws in data["work_streams"].values())
        ws_profit = sum(ws.profit for ws in data["work_streams"].values())

        bv_arr = sum(bv.arr for bv in data["baseline_ventures"].values())
        bv_profit = sum(bv.profit for bv in data["baseline_ventures"].values())

        total_arr = ws_arr + bv_arr
        total_profit = ws_profit + bv_profit
        margin = total_profit / total_arr if total_arr > 0 else 0

        valuation_10x = total_arr * 10
        valuation_15x = total_profit * 15
        valuation_blended = (valuation_10x + valuation_15x) / 2

        results[name] = {"arr": total_arr, "profit": total_profit, "margin": margin, "valuation": valuation_blended}

    # Print table
    print(f"{'Metric':<30} | {'Conservative':>15} | {'Baseline':>15} | {'Aggressive':>15}")
    print("-" * 80)

    print(
        f"{'Total ARR':<30} | ${results['conservative']['arr']:>14,.0f} | ${results['baseline']['arr']:>14,.0f} | ${results['aggressive']['arr']:>14,.0f}"
    )
    print(
        f"{'Net Profit':<30} | ${results['conservative']['profit']:>14,.0f} | ${results['baseline']['profit']:>14,.0f} | ${results['aggressive']['profit']:>14,.0f}"
    )
    print(
        f"{'Margin':<30} | {results['conservative']['margin']:>14.1%} | {results['baseline']['margin']:>14.1%} | {results['aggressive']['margin']:>14.1%}"
    )
    print(
        f"{'Exit Valuation':<30} | ${results['conservative']['valuation']:>14,.0f} | ${results['baseline']['valuation']:>14,.0f} | ${results['aggressive']['valuation']:>14,.0f}"
    )
    print()

    print("🎯 RECOMMENDATION: Focus on BASELINE scenario execution")
    print("   - Conservative: Safety net if market is slow")
    print("   - Baseline: Realistic with 70% penetration")
    print("   - Aggressive: Upside if enterprise traction is strong")
    print()


def main():
    parser = argparse.ArgumentParser(description="PNKLN Ultrathink Money Calculator")
    parser.add_argument(
        "--scenario", choices=["conservative", "baseline", "aggressive", "all"], default="all", help="Which scenario to calculate (default: all)"
    )

    args = parser.parse_args()

    scenarios = {
        "conservative": calculate_conservative_scenario(),
        "baseline": calculate_baseline_scenario(),
        "aggressive": calculate_aggressive_scenario(),
    }

    if args.scenario == "all":
        # Print each scenario
        for name, data in scenarios.items():
            print_scenario_analysis(name, data)
            print("\n\n")

        # Print comparison
        print_comparison_table(scenarios)
    else:
        # Print single scenario
        print_scenario_analysis(args.scenario, scenarios[args.scenario])


if __name__ == "__main__":
    main()
