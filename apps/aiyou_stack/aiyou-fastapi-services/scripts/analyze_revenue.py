#!/usr/bin/env python3
"""
Revenue Analysis Script
Generates a detailed financial analysis report based on the Revenue Model.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from src.pnkln_agents.config.revenue_model import DEFAULT_REVENUE_MODEL, PricingTier


def format_currency(amount):
    return f"${amount:,.2f}"


def analyze_revenue():
    model = DEFAULT_REVENUE_MODEL
    data = model.to_dict()

    print("=== PNKLN Financial Analysis Report ===")
    print(f"Target CAC: {format_currency(model.target_cac_usd)}")
    print(f"Avg Customer Lifetime: {model.average_customer_lifetime_months} months")
    print("-" * 40)

    for tier_name, tier_data in data["tiers"].items():
        if tier_name == "usage":
            continue

        print(f"\nTier: {tier_name.upper().replace('_', ' ')}")
        print(f"  Monthly Price: {format_currency(tier_data['monthly_price_usd'])}")
        print(f"  Target Customer: {tier_data['target_customer']}")
        print(f"  LTV: {format_currency(tier_data['ltv'])}")
        print(f"  LTV:CAC Ratio: {tier_data['ltv_cac_ratio']:.2f}x")

        # Break-even analysis
        break_even_days = model.calculate_break_even_timeline_days(PricingTier[tier_name.upper()])
        print(f"  Break-even Timeline: {break_even_days} days")

        # Revenue Projections (Annualized)
        annual_revenue = tier_data["monthly_price_usd"] * 12
        print(f"  Annual Revenue/Customer: {format_currency(annual_revenue)}")

    print("\n=== Usage-Based Revenue ===")
    print(
        f"  Price per Validated Lead: {format_currency(data['tiers']['usage']['price_per_validated_lead'])}"
    )

    print("\n=== Competitive Baseline ===")
    from src.pnkln_agents.config.revenue_model import COMPETITIVE_BASELINE

    for comp, details in COMPETITIVE_BASELINE.items():
        print(f"  Competitor: {comp}")
        print(f"  Price: {format_currency(details['monthly_price_usd'])}")
        print(f"  Gaps: {', '.join(details['gaps'])}")


if __name__ == "__main__":
    analyze_revenue()
