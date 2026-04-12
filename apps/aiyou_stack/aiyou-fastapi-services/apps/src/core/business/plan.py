"""
AI Agent Business Plan - Core Parameters & Models
Vertical SaaS Model for AI Agent-as-a-Service

Author: ShadowTag-v2JR System
Date: 2025-11-17
"""

from dataclasses import dataclass, field
from enum import Enum


class VerticalType(Enum):
    """AI Agent vertical categories"""

    SALES_AUTOMATION = "sales_automation"
    CONTENT_REPURPOSING = "content_repurposing"
    CUSTOMER_SUPPORT = "customer_support"
    MEETING_INTELLIGENCE = "meeting_intelligence"
    MARKET_RESEARCH = "market_research"
    WORKFLOW_ORCHESTRATION = "workflow_orchestration"


@dataclass
class BusinessMetrics:
    """Month 12 target metrics"""

    monthly_recurring_revenue: int = 120_000
    customer_count: int = 50
    average_revenue_per_user: int = 2_000
    ltv_cac_ratio: float = 4.0
    gross_margin: float = 0.75
    churn_monthly: float = 0.10

    # Unit economics
    customer_acquisition_cost: int = 1_500
    cost_of_goods_sold_per_customer: int = 200
    support_ops_cost_per_customer: int = 150
    lifetime_value: int = 54_984
    payback_period_months: float = 0.35


@dataclass
class Vertical:
    """AI Agent vertical configuration"""

    name: str
    vertical_type: VerticalType
    monthly_price: int
    setup_fee: int
    target_customers: int
    mrr_contribution: int

    @property
    def annual_value(self) -> int:
        """Calculate annual value"""
        return (self.monthly_price * 12 * self.target_customers) + (
            self.setup_fee * self.target_customers
        )


class VerticalPortfolio:
    """AI Agent vertical portfolio manager"""

    def __init__(self):
        self.verticals: dict[VerticalType, Vertical] = {
            VerticalType.SALES_AUTOMATION: Vertical(
                name="Sales Automation",
                vertical_type=VerticalType.SALES_AUTOMATION,
                monthly_price=1500,
                setup_fee=5000,
                target_customers=15,
                mrr_contribution=22_500,
            ),
            VerticalType.CONTENT_REPURPOSING: Vertical(
                name="Content Repurposing",
                vertical_type=VerticalType.CONTENT_REPURPOSING,
                monthly_price=800,
                setup_fee=2000,
                target_customers=10,
                mrr_contribution=8_000,
            ),
            VerticalType.CUSTOMER_SUPPORT: Vertical(
                name="Customer Support Triage",
                vertical_type=VerticalType.CUSTOMER_SUPPORT,
                monthly_price=2000,
                setup_fee=8000,
                target_customers=8,
                mrr_contribution=16_000,
            ),
            VerticalType.MEETING_INTELLIGENCE: Vertical(
                name="Meeting Intelligence",
                vertical_type=VerticalType.MEETING_INTELLIGENCE,
                monthly_price=1200,
                setup_fee=3000,
                target_customers=12,
                mrr_contribution=14_400,
            ),
            VerticalType.MARKET_RESEARCH: Vertical(
                name="Market Research",
                vertical_type=VerticalType.MARKET_RESEARCH,
                monthly_price=3000,
                setup_fee=10000,
                target_customers=3,
                mrr_contribution=9_000,
            ),
            VerticalType.WORKFLOW_ORCHESTRATION: Vertical(
                name="Workflow Orchestration",
                vertical_type=VerticalType.WORKFLOW_ORCHESTRATION,
                monthly_price=2500,
                setup_fee=12000,
                target_customers=2,
                mrr_contribution=5_000,
            ),
        }

    def total_mrr(self) -> int:
        """Calculate total MRR"""
        return sum(v.mrr_contribution for v in self.verticals.values())

    def total_customers(self) -> int:
        """Calculate total customers"""
        return sum(v.target_customers for v in self.verticals.values())

    def get_priority_order(self) -> list[VerticalType]:
        """Get verticals in priority order"""
        return [
            VerticalType.SALES_AUTOMATION,
            VerticalType.CONTENT_REPURPOSING,
            VerticalType.CUSTOMER_SUPPORT,
            VerticalType.MEETING_INTELLIGENCE,
            VerticalType.MARKET_RESEARCH,
            VerticalType.WORKFLOW_ORCHESTRATION,
        ]


@dataclass
class TechStack:
    """Technical architecture stack"""

    core_language: str = "Python 3.11+"
    orchestration: list[str] = field(default_factory=lambda: ["LangGraph", "CrewAI"])
    llm_provider: str = "OpenAI GPT-4 Turbo"

    memory_layer: dict[str, str] = field(
        default_factory=lambda: {
            "long_term": "Pinecone",
            "short_term": "Redis",
            "episodic": "Custom PostgreSQL schema",
        }
    )

    deployment: dict[str, str] = field(
        default_factory=lambda: {
            "dev": "Vertex AI Workbench",
            "prod": "GKE (Google Kubernetes Engine)",
        }
    )

    security: list[str] = field(
        default_factory=lambda: [
            "GCP Secret Manager",
            "Encryption at rest/transit",
            "SOC 2 Type II (Month 18 target)",
        ]
    )

    monitoring: str = "Datadog + custom dashboards"


@dataclass
class AgentDesignPattern:
    """Agent architecture pattern"""

    framework: str = "ReAct (Reason + Act)"
    memory_types: list[str] = field(default_factory=lambda: ["short_term", "long_term", "episodic"])
    guardrails: list[str] = field(
        default_factory=lambda: [
            "Human-in-loop checkpoints",
            "Task manager loops",
            "Hallucination detection",
            "Output validation",
        ]
    )
    tools: str = "Custom API wrappers (Notion, Slack, HubSpot, Apollo, etc.)"


@dataclass
class KillSwitch:
    """Kill-switch criteria for pivot/shutdown"""

    month: int
    mrr_threshold: int | None = None
    pilot_threshold: int | None = None
    ltv_cac_threshold: float | None = None
    action: str = ""

    def evaluate(
        self, current_mrr: int, current_pilots: int = 0, current_ltv_cac: float = 0.0
    ) -> bool:
        """Check if kill-switch triggered"""
        triggers = []

        if self.mrr_threshold and current_mrr < self.mrr_threshold:
            triggers.append(f"MRR ${current_mrr} < ${self.mrr_threshold}")

        if self.pilot_threshold and current_pilots < self.pilot_threshold:
            triggers.append(f"Pilots {current_pilots} < {self.pilot_threshold}")

        if self.ltv_cac_threshold and current_ltv_cac < self.ltv_cac_threshold:
            triggers.append(f"LTV:CAC {current_ltv_cac} < {self.ltv_cac_threshold}")

        return len(triggers) > 0


class KillSwitchGates:
    """Kill-switch gate manager"""

    def __init__(self):
        self.gates = [
            KillSwitch(
                month=3,
                pilot_threshold=5,
                mrr_threshold=10_000,
                action="Pivot vertical or shut down",
            ),
            KillSwitch(month=6, mrr_threshold=35_000, action="Reassess pricing/ICP"),
            KillSwitch(
                month=12,
                mrr_threshold=100_000,
                ltv_cac_threshold=4.0,
                action="Scale or sell",
            ),
        ]

    def check_gates(self, month: int, mrr: int, pilots: int = 0, ltv_cac: float = 0.0) -> list[str]:
        """Check all gates for given month"""
        triggered = []

        for gate in self.gates:
            if gate.month == month and gate.evaluate(mrr, pilots, ltv_cac):
                triggered.append(gate.action)

        return triggered
