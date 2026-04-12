"""
Business Metrics & Unit Economics
Target State: Month 12 Financial Model
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class BusinessMetrics:
    """Month 12 Target Metrics"""

    monthly_recurring_revenue: int = 120_000  # $120K MRR target
    customer_count: int = 50  # Conservative case
    average_revenue_per_user: int = 2_000  # $2K ARPU
    ltv_cac_ratio: float = 4.0  # Minimum acceptable ratio
    gross_margin: float = 0.75  # 75% target
    churn_monthly: float = 0.10  # 10% monthly churn assumption

    def validate(self) -> bool:
        """Validate metrics against constraints"""
        if self.ltv_cac_ratio < 4.0:
            return False
        if self.gross_margin < 0.70:
            return False
        return not self.churn_monthly > 0.12

    def to_dict(self) -> dict[str, Any]:
        return {
            "mrr": self.monthly_recurring_revenue,
            "customers": self.customer_count,
            "arpu": self.average_revenue_per_user,
            "ltv_cac": self.ltv_cac_ratio,
            "margin": self.gross_margin,
            "churn": self.churn_monthly,
            "valid": self.validate(),
        }


@dataclass
class UnitEconomics:
    """Cost structure per customer"""

    customer_acquisition_cost: int = 1_500  # Early-stage CAC
    cost_of_goods_sold_per_customer: int = 200  # OpenAI API + infra/mo
    support_ops_cost_per_customer: int = 150  # CS/ops allocation
    lifetime_value: int = 54_984  # 24-month retention @ $2,291/mo
    payback_period_months: float = 0.35  # Optimistic; reality ~3-6mo

    @property
    def monthly_cost_per_customer(self) -> int:
        """Total monthly cost"""
        return self.cost_of_goods_sold_per_customer + self.support_ops_cost_per_customer

    @property
    def contribution_margin(self) -> float:
        """Per-customer contribution"""
        arpu = 2000  # From BusinessMetrics
        return (arpu - self.monthly_cost_per_customer) / arpu

    def to_dict(self) -> dict[str, Any]:
        return {
            "cac": self.customer_acquisition_cost,
            "cogs": self.cost_of_goods_sold_per_customer,
            "support_cost": self.support_ops_cost_per_customer,
            "ltv": self.lifetime_value,
            "payback_months": self.payback_period_months,
            "monthly_cost": self.monthly_cost_per_customer,
            "contribution_margin": self.contribution_margin,
        }


# Singleton instances
BUSINESS_METRICS = BusinessMetrics()
UNIT_ECONOMICS = UnitEconomics()
