"""
PNKLN Marketplace - Two-sided platform for AI capabilities

Revenue streams:
- Platform fees: 20-30% of transactions
- Publishing fees: $99/year per superpower
- Featured placement: $500-$5K/mo
- Enterprise bundles: $10K-$100K/year

Year 1 target: $100K (50 superpowers @ $2K GMV avg, 20% take rate)
Year 5 target: $10M (marketplace GMV $50M @ 20% take rate)
"""

from .schema import (
    Developer,
    MarketplaceAnalytics,
    PlatformFeeConfig,
    PricingModel,
    Review,
    Superpower,
    SuperpowerCategory,
    SuperpowerStatus,
    Transaction,
    TransactionStatus,
    UserSuperpower,
    calculate_platform_fee,
    project_marketplace_revenue,
)

__all__ = [
    "Developer",
    "Superpower",
    "Transaction",
    "UserSuperpower",
    "Review",
    "MarketplaceAnalytics",
    "PlatformFeeConfig",
    "SuperpowerCategory",
    "SuperpowerStatus",
    "PricingModel",
    "TransactionStatus",
    "calculate_platform_fee",
    "project_marketplace_revenue",
]
