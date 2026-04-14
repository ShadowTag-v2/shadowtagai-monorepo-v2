from .schema.superpowercategory import SuperpowerCategory

"\nPNKLN Marketplace - Database Schema\nTwo-sided marketplace for AI superpowers and kernel chains\n\nRevenue model:\n- Platform fees: 20-30% of all transactions\n- Publishing fees: $99/year per superpower\n- Featured placement: $500-$5K/mo\n- Enterprise bundles: $10K-$100K/year\n\nYear 1 target: $100K revenue (50 superpowers @ $2K GMV avg, 20% take rate)\nYear 5 target: $10M revenue (marketplace GMV $50M @ 20% take rate)\n"

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


def calculate_platform_fee(
    amount: float, category: SuperpowerCategory, developer_gmv: float = 0,
) -> dict[str, float]:
    """Calculate platform fee and splits

    Args:
        amount: Transaction amount
        category: Superpower category
        developer_gmv: Developer's lifetime GMV (for volume discounts)

    Returns:
        Dict with platform_fee, developer_share, fee_pct

    """
    fee_pct = 25.0
    category_fees = {
        SuperpowerCategory.AI_TUTOR: 20.0,
        SuperpowerCategory.PRODUCTIVITY: 25.0,
        SuperpowerCategory.HEALTH: 22.0,
        SuperpowerCategory.OTHER: 30.0,
    }
    if category in category_fees:
        fee_pct = category_fees[category]
    if developer_gmv >= 50000:
        fee_pct = 20.0
    elif developer_gmv >= 10000:
        fee_pct = 22.0
    platform_fee = amount * (fee_pct / 100)
    developer_share = amount - platform_fee
    return {
        "platform_fee": round(platform_fee, 2),
        "developer_share": round(developer_share, 2),
        "fee_pct": fee_pct,
    }


def project_marketplace_revenue(
    num_superpowers: int,
    avg_price: float,
    avg_installs_per_superpower: int,
    conversion_rate: float = 0.1,
    platform_fee_pct: float = 25.0,
) -> dict[str, float]:
    """Project marketplace revenue

    Example Year 1:
    - 50 superpowers
    - $4.99 avg price
    - 40 installs per superpower
    - 10% conversion (4 paid installs)
    - 25% platform fee

    GMV: 50 × $4.99 × 4 = $996
    Platform revenue: $996 × 0.25 = $249

    Example Year 5:
    - 1000 superpowers
    - $9.99 avg price
    - 100 installs per superpower
    - 50% conversion (50 paid installs)
    - 20% platform fee (volume discount)

    GMV: 1000 × $9.99 × 50 = $499,500
    Platform revenue: $499,500 × 0.20 = $99,900
    """
    paid_installs = num_superpowers * avg_installs_per_superpower * conversion_rate
    gmv = paid_installs * avg_price
    platform_revenue = gmv * (platform_fee_pct / 100)
    developer_revenue = gmv - platform_revenue
    return {
        "num_superpowers": num_superpowers,
        "total_installs": num_superpowers * avg_installs_per_superpower,
        "paid_installs": paid_installs,
        "gmv": gmv,
        "platform_revenue": platform_revenue,
        "developer_revenue": developer_revenue,
        "avg_revenue_per_superpower": gmv / num_superpowers if num_superpowers > 0 else 0,
    }


if __name__ == "__main__":
    print("MARKETPLACE REVENUE PROJECTIONS\n")
    year_1 = project_marketplace_revenue(
        num_superpowers=50,
        avg_price=4.99,
        avg_installs_per_superpower=40,
        conversion_rate=0.1,
        platform_fee_pct=25.0,
    )
    print(f"Year 1: {year_1['num_superpowers']} superpowers")
    print(f"  GMV: ${year_1['gmv']:,.2f}")
    print(f"  Platform revenue: ${year_1['platform_revenue']:,.2f}\n")
    year_5 = project_marketplace_revenue(
        num_superpowers=1000,
        avg_price=9.99,
        avg_installs_per_superpower=100,
        conversion_rate=0.5,
        platform_fee_pct=20.0,
    )
    print(f"Year 5: {year_5['num_superpowers']} superpowers")
    print(f"  GMV: ${year_5['gmv']:,.2f}")
    print(f"  Platform revenue: ${year_5['platform_revenue']:,.2f}")
