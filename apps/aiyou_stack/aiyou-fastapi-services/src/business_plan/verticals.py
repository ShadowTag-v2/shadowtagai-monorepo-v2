"""
Vertical Revenue Models
6 productized AI agent solutions with pricing & targets
"""

from dataclasses import dataclass
from enum import Enum


class VerticalType(Enum):
    """Revenue vertical categories"""

    SALES_AUTOMATION = "sales_automation"
    CONTENT_REPURPOSING = "content_repurposing"
    CUSTOMER_SUPPORT = "customer_support"
    MEETING_INTELLIGENCE = "meeting_intelligence"
    MARKET_RESEARCH = "market_research"
    WORKFLOW_ORCHESTRATION = "workflow_orchestration"


@dataclass
class VerticalRevenue:
    """Revenue model for a single vertical"""

    name: str
    monthly_price: int
    setup_fee: int
    target_customers: int
    description: str
    priority: int  # 1 = highest

    @property
    def mrr_contribution(self) -> int:
        """Monthly recurring revenue"""
        return self.monthly_price * self.target_customers

    @property
    def annual_recurring_revenue(self) -> int:
        """ARR contribution"""
        return self.mrr_contribution * 12

    @property
    def first_year_revenue(self) -> int:
        """Setup fees + 12 months MRR"""
        return self.setup_fee * self.target_customers + self.annual_recurring_revenue

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "monthly_price": self.monthly_price,
            "setup_fee": self.setup_fee,
            "target_customers": self.target_customers,
            "mrr": self.mrr_contribution,
            "arr": self.annual_recurring_revenue,
            "first_year": self.first_year_revenue,
            "priority": self.priority,
        }


# Define all 6 verticals
VERTICALS: dict[str, VerticalRevenue] = {
    VerticalType.SALES_AUTOMATION.value: VerticalRevenue(
        name="Sales Automation Agent",
        monthly_price=1500,
        setup_fee=5000,
        target_customers=15,
        description="Scrape/qualify/personalize outbound - Apollo + LinkedIn + Gmail",
        priority=1,  # CURRENT BUILD - Week 1 focus
    ),
    VerticalType.CONTENT_REPURPOSING.value: VerticalRevenue(
        name="Content Repurposing Agent",
        monthly_price=800,
        setup_fee=2000,
        target_customers=10,
        description="Long-form → multi-platform distribution",
        priority=2,
    ),
    VerticalType.CUSTOMER_SUPPORT.value: VerticalRevenue(
        name="Customer Support Triage",
        monthly_price=2000,
        setup_fee=8000,
        target_customers=8,
        description="Auto-handle 80% of tickets with context",
        priority=3,
    ),
    VerticalType.MEETING_INTELLIGENCE.value: VerticalRevenue(
        name="Meeting Intelligence Agent",
        monthly_price=1200,
        setup_fee=3000,
        target_customers=12,
        description="Record → summarize → action items + CRM sync",
        priority=4,
    ),
    VerticalType.MARKET_RESEARCH.value: VerticalRevenue(
        name="Market Research Agent",
        monthly_price=3000,
        setup_fee=10000,
        target_customers=3,
        description="Competitive intelligence automation",
        priority=5,
    ),
    VerticalType.WORKFLOW_ORCHESTRATION.value: VerticalRevenue(
        name="Workflow Orchestration Agent",
        monthly_price=2500,
        setup_fee=12000,
        target_customers=2,
        description="Connect fragmented tool stacks (Zapier killer)",
        priority=6,
    ),
}


def get_total_mrr() -> int:
    """Calculate total MRR across all verticals"""
    return sum(v.mrr_contribution for v in VERTICALS.values())


def get_total_customers() -> int:
    """Total customer count target"""
    return sum(v.target_customers for v in VERTICALS.values())


def get_vertical_by_priority() -> list[VerticalRevenue]:
    """Return verticals sorted by priority"""
    return sorted(VERTICALS.values(), key=lambda v: v.priority)


def get_current_focus() -> VerticalRevenue:
    """Get priority 1 vertical (current build)"""
    return VERTICALS[VerticalType.SALES_AUTOMATION.value]


# Validate totals match business metrics
assert get_total_customers() == 50, "Customer count mismatch"
# Total MRR is ~$75K from defined targets (buffer for upsells/enterprise)
