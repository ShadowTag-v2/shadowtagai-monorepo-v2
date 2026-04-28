# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import logging

logger = logging.getLogger(__name__)


class DynamicPricingEngine:
    """Plugging the $50k/mo Pricing Leak.
    We replace static SaaS tiers with an automated, compute-aware dynamic pricing model based on case volume.
    """

    def __init__(self, base_rate_usd: float = 99.0):
        self.base_rate_usd = base_rate_usd
        self.cost_per_filing = 15.0  # High value enterprise routing fee

    def calculate_monthly_invoice(
        self,
        firm_id: str,
        filings_processed: int,
        api_calls_made: int,
    ) -> float:
        """Determines the true value provided and prices accordingly to capture consumer surplus."""
        if filings_processed > 500:
            logger.info(f"Pricing Engine: Enterprise Tier activated for Firm {firm_id}")
            # Volume discount + API SLA access
            total_cost = 5000.0 + (api_calls_made * 0.05)
        else:
            logger.info(f"Pricing Engine: Standard Tier activated for Firm {firm_id}")
            total_cost = self.base_rate_usd + (filings_processed * self.cost_per_filing)

        return round(total_cost, 2)
