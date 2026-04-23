"""PART 2: BUSINESS METRICS & UNIT ECONOMICS
Key Parameters & Variables
"""

from dataclasses import dataclass, field


@dataclass
class BusinessMetrics:
    """Month 12 target metrics"""

    # Core Metrics
    monthly_recurring_revenue: int = 120_000  # $120K MRR
    customer_count: int = 50  # Conservative case
    average_revenue_per_user: int = 2_000  # $2K ARPU
    ltv_cac_ratio: float = 4.0  # Minimum acceptable
    gross_margin: float = 0.75  # 75% target
    churn_monthly: float = 0.10  # 10% monthly churn assumption

    # Unit Economics
    customer_acquisition_cost: int = 1_500  # Early-stage CAC
    cost_of_goods_sold_per_customer: int = 200  # OpenAI API + infra per mo
    support_ops_cost_per_customer: int = 150  # CS/ops allocation
    lifetime_value: int = 54_984  # 24-month retention @ $2,291/mo effective
    payback_period_months: float = 0.35  # Optimistic; reality ~3-6mo

    def calculate_total_cogs(self) -> int:
        """Calculate total COGS per customer"""
        return self.cost_of_goods_sold_per_customer + self.support_ops_cost_per_customer

    def calculate_gross_profit_per_customer(self) -> int:
        """Calculate gross profit per customer monthly"""
        return self.average_revenue_per_user - self.calculate_total_cogs()

    def validate_ltv_cac(self) -> bool:
        """Validate LTV:CAC ratio meets minimum threshold"""
        return self.ltv_cac_ratio >= 4.0

    def calculate_annual_churn_rate(self) -> float:
        """Calculate annual churn from monthly rate"""
        return 1 - ((1 - self.churn_monthly) ** 12)


@dataclass
class VerticalMetrics:
    """Revenue metrics per vertical"""

    monthly_price: int
    setup_fee: int
    target_customers: int
    mrr_contribution: int = field(init=False)

    def __post_init__(self):
        self.mrr_contribution = self.monthly_price * self.target_customers

    def calculate_arr(self) -> int:
        """Calculate ARR for this vertical"""
        return self.mrr_contribution * 12

    def calculate_first_year_revenue(self) -> int:
        """Calculate first year revenue including setup fees"""
        return self.calculate_arr() + (self.setup_fee * self.target_customers)


class VerticalRevenueTargets:
    """Month 12 revenue targets by vertical"""

    VERTICALS: dict[str, VerticalMetrics] = {
        "sales_automation": VerticalMetrics(
            monthly_price=1500,
            setup_fee=5000,
            target_customers=15,  # 30% of customer base
        ),
        "content_repurposing": VerticalMetrics(
            monthly_price=800,
            setup_fee=2000,
            target_customers=10,
        ),
        "customer_support": VerticalMetrics(monthly_price=2000, setup_fee=8000, target_customers=8),
        "meeting_intelligence": VerticalMetrics(
            monthly_price=1200,
            setup_fee=3000,
            target_customers=12,
        ),
        "market_research": VerticalMetrics(monthly_price=3000, setup_fee=10000, target_customers=3),
        "workflow_orchestration": VerticalMetrics(
            monthly_price=2500,
            setup_fee=12000,
            target_customers=2,
        ),
    }

    @classmethod
    def calculate_total_mrr(cls) -> int:
        """Calculate total MRR across all verticals"""
        return sum(v.mrr_contribution for v in cls.VERTICALS.values())

    @classmethod
    def calculate_total_customers(cls) -> int:
        """Calculate total customers across all verticals"""
        return sum(v.target_customers for v in cls.VERTICALS.values())

    @classmethod
    def calculate_total_arr(cls) -> int:
        """Calculate total ARR across all verticals"""
        return cls.calculate_total_mrr() * 12

    @classmethod
    def calculate_blended_arpu(cls) -> float:
        """Calculate blended ARPU across all verticals"""
        total_mrr = cls.calculate_total_mrr()
        total_customers = cls.calculate_total_customers()
        return total_mrr / total_customers if total_customers > 0 else 0


@dataclass
class KillSwitchCriteria:
    """Decision gate criteria for pivot/shutdown"""

    month: int
    condition: str
    action: str
    severity: str  # EH, H, M, L (from ATP 5-19)


class KillSwitches:
    """Evidence-based kill-switch gates"""

    GATES = [
        KillSwitchCriteria(
            month=3,
            condition="pilots < 5 OR mrr < 10_000",
            action="Pivot vertical or shut down",
            severity="EH",  # Extremely High risk
        ),
        KillSwitchCriteria(
            month=6,
            condition="mrr < 35_000",
            action="Reassess pricing/ICP",
            severity="H",  # High risk
        ),
        KillSwitchCriteria(
            month=12,
            condition="mrr < 100_000 OR ltv_cac < 4.0",
            action="Scale or sell",
            severity="EH",  # Extremely High risk
        ),
        KillSwitchCriteria(
            month=90,  # days post-launch per vertical
            condition="vertical_mrr < 10_000",
            action="Kill vertical (no sunk cost fallacy)",
            severity="H",  # High risk
        ),
    ]

    @classmethod
    def evaluate_gate(
        cls,
        current_month: int,
        current_mrr: int,
        pilot_count: int = 0,
        ltv_cac: float = 0,
    ) -> dict:
        """Evaluate if any kill-switch criteria are met"""
        triggered_gates = []

        for gate in cls.GATES:
            if gate.month == 3 and current_month >= 3:
                if pilot_count < 5 or current_mrr < 10_000:
                    triggered_gates.append(
                        {
                            "gate": gate.month,
                            "triggered": True,
                            "action": gate.action,
                            "severity": gate.severity,
                        },
                    )

            elif gate.month == 6 and current_month >= 6:
                if current_mrr < 35_000:
                    triggered_gates.append(
                        {
                            "gate": gate.month,
                            "triggered": True,
                            "action": gate.action,
                            "severity": gate.severity,
                        },
                    )

            elif gate.month == 12 and current_month >= 12:  # noqa: SIM102
                if current_mrr < 100_000 or ltv_cac < 4.0:
                    triggered_gates.append(
                        {
                            "gate": gate.month,
                            "triggered": True,
                            "action": gate.action,
                            "severity": gate.severity,
                        },
                    )

        return {
            "triggered": len(triggered_gates) > 0,
            "gates": triggered_gates,
            "recommendation": triggered_gates[0]["action"]
            if triggered_gates
            else "Continue execution",
        }


def generate_metrics_report() -> dict:
    """Generate comprehensive metrics report"""
    base_metrics = BusinessMetrics()
    vertical_targets = VerticalRevenueTargets()

    return {
        "base_metrics": {
            "mrr_target": base_metrics.monthly_recurring_revenue,
            "customers": base_metrics.customer_count,
            "arpu": base_metrics.average_revenue_per_user,
            "ltv_cac_ratio": base_metrics.ltv_cac_ratio,
            "gross_margin": base_metrics.gross_margin,
            "monthly_churn": base_metrics.churn_monthly,
            "cac": base_metrics.customer_acquisition_cost,
            "cogs_per_customer": base_metrics.calculate_total_cogs(),
            "gross_profit_per_customer": base_metrics.calculate_gross_profit_per_customer(),
            "ltv": base_metrics.lifetime_value,
            "ltv_cac_valid": base_metrics.validate_ltv_cac(),
        },
        "vertical_breakdown": {
            name: {
                "monthly_price": metrics.monthly_price,
                "setup_fee": metrics.setup_fee,
                "target_customers": metrics.target_customers,
                "mrr_contribution": metrics.mrr_contribution,
                "arr": metrics.calculate_arr(),
                "first_year_revenue": metrics.calculate_first_year_revenue(),
            }
            for name, metrics in vertical_targets.VERTICALS.items()
        },
        "totals": {
            "total_mrr": vertical_targets.calculate_total_mrr(),
            "total_arr": vertical_targets.calculate_total_arr(),
            "total_customers": vertical_targets.calculate_total_customers(),
            "blended_arpu": vertical_targets.calculate_blended_arpu(),
        },
        "kill_switches": [
            {
                "month": gate.month,
                "condition": gate.condition,
                "action": gate.action,
                "severity": gate.severity,
            }
            for gate in KillSwitches.GATES
        ],
    }


if __name__ == "__main__":
    import json

    report = generate_metrics_report()
    print(json.dumps(report, indent=2))
