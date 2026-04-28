# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""PART 1: STATE SUMMARY
Context: AI Agent Business Plan Development
Generated: 2025-11-17
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class ProjectState:
    """Core project state and progress tracking"""

    project_name: str = "AI Agent-as-a-Service (Vertical SaaS Model)"
    generated_date: datetime = datetime(2025, 11, 17)

    # What We Built
    core_assets: list[str] = None

    def __post_init__(self):
        if self.core_assets is None:
            self.core_assets = [
                "Comprehensive business plan for productized AI agent solutions across 6 revenue verticals",
                "Bootstrap-friendly path to $120K MRR in 12 months",
                "Technical architecture using production-ready stack (not vaporware)",
                "Financial model with unit economics (LTV:CAC ≥4:1, ROI ≥3× in 18mo)",
            ]


@dataclass
class RevenueVertical:
    """Revenue vertical definition"""

    name: str
    monthly_price: int
    setup_fee: int
    description: str
    priority: int


class VerticalRegistry:
    """Registry of all revenue verticals"""

    VERTICALS = {
        "sales_automation": RevenueVertical(
            name="Sales Automation Agent",
            monthly_price=1500,
            setup_fee=5000,
            description="Scrape/qualify/personalize outbound",
            priority=1,
        ),
        "content_repurposing": RevenueVertical(
            name="Content Repurposing Agent",
            monthly_price=800,
            setup_fee=2000,
            description="Long-form → multi-platform distribution",
            priority=2,
        ),
        "customer_support": RevenueVertical(
            name="Customer Support Triage",
            monthly_price=2000,
            setup_fee=8000,
            description="Auto-handle 80% of tickets",
            priority=3,
        ),
        "meeting_intelligence": RevenueVertical(
            name="Meeting Intelligence",
            monthly_price=1200,
            setup_fee=3000,
            description="Record → summarize → action items",
            priority=4,
        ),
        "market_research": RevenueVertical(
            name="Market Research",
            monthly_price=3000,
            setup_fee=10000,
            description="Competitive intelligence automation",
            priority=5,
        ),
        "workflow_orchestration": RevenueVertical(
            name="Workflow Orchestration",
            monthly_price=2500,
            setup_fee=12000,
            description="Connect fragmented tool stacks",
            priority=6,
        ),
    }


@dataclass
class TechnicalFoundation:
    """Technical stack and architecture"""

    stack: dict[str, str] = None
    memory_architecture: dict[str, str] = None
    deployment: dict[str, str] = None
    security: list[str] = None
    pattern: str = "ReAct + episodic memory + human-in-loop guardrails"

    def __post_init__(self):
        if self.stack is None:
            self.stack = {
                "language": "Python 3.11+",
                "orchestration": "LangGraph + CrewAI",
                "llm": "GPT-4 Turbo",
                "function_calling": "OpenAI",
            }

        if self.memory_architecture is None:
            self.memory_architecture = {
                "long_term": "Pinecone",
                "short_term": "Redis",
                "episodic": "Custom PostgreSQL schema",
            }

        if self.deployment is None:
            self.deployment = {
                "dev": "Vertex AI Workbench",
                "prod": "GKE (Google Kubernetes Engine)",
            }

        if self.security is None:
            self.security = [
                "GCP Secret Manager",
                "Encryption at rest/transit",
                "SOC 2 Type II (Month 18 target)",
                "Audit trails",
            ]


@dataclass
class BusinessModel:
    """Business model and monetization strategy"""

    model_type: str = "Tiered SaaS"
    price_range: str = "$500-$3K/mo"
    setup_fees: str = "$2K-$15K"
    target: str = "B2B companies bleeding $10K+/mo on repetitive knowledge work"
    positioning: str = "Productized service (not custom dev, not pure SaaS)"
    bootstrap_constraint: str = "No funding until unit economics proven"


@dataclass
class GTMPhase:
    """Go-to-market phase definition"""

    phase: int
    timeline: str
    target_pilots: int
    target_mrr: int
    verticals_live: int
    key_milestone: str


class GTMStrategy:
    """Go-to-market execution plan"""

    PHASES = [
        GTMPhase(
            phase=1,
            timeline="Mo 1-3",
            target_pilots=5,
            target_mrr=10_000,
            verticals_live=1,
            key_milestone="Sales Agent only",
        ),
        GTMPhase(
            phase=2,
            timeline="Mo 4-6",
            target_pilots=20,
            target_mrr=35_000,
            verticals_live=2,
            key_milestone="Add Content Agent",
        ),
        GTMPhase(
            phase=3,
            timeline="Mo 7-12",
            target_pilots=60,
            target_mrr=120_000,
            verticals_live=4,
            key_milestone="4 verticals live",
        ),
    ]


class CriticalFrameworks:
    """Applied decision and operational frameworks"""

    PURPOSE_REASON_BRAKES = {
        "purpose": "ShadowTag-v2JR mission alignment",
        "reason": "Doctrine (SOPs A-D)",
        "brakes": "Military risk assessment (ATP 5-19) for decision gates",
    }

    REVENUE_DOCTRINE = "Every feature = 'Does this make money faster?'"

    BOY_SCOUT_RULE = "Ship clean, war-game architectures, document with beauty"

    SECURITY_ABSOLUTE = "100% operational gate (non-negotiable)"

    EVIDENCE_ONLY = "No assumptions without n≥10 user interviews"

    CONSTRAINTS = {
        "max_function_length": 20,  # lines
        "external_libraries": "Approval required",
        "test_coverage": 0.80,  # 80% minimum
        "output_format": "monospace for technical content",
    }


def get_state_summary() -> dict:
    """Generate complete state summary"""
    return {
        "project": ProjectState(),
        "verticals": VerticalRegistry.VERTICALS,
        "technical": TechnicalFoundation(),
        "business_model": BusinessModel(),
        "gtm_strategy": GTMStrategy.PHASES,
        "frameworks": {
            "purpose_reason_brakes": CriticalFrameworks.PURPOSE_REASON_BRAKES,
            "revenue_doctrine": CriticalFrameworks.REVENUE_DOCTRINE,
            "boy_scout_rule": CriticalFrameworks.BOY_SCOUT_RULE,
            "security_absolute": CriticalFrameworks.SECURITY_ABSOLUTE,
            "evidence_only": CriticalFrameworks.EVIDENCE_ONLY,
            "constraints": CriticalFrameworks.CONSTRAINTS,
        },
        "generated": datetime.now().isoformat(),
        "status": "ACTIVE",
    }


if __name__ == "__main__":
    import json

    state = get_state_summary()
    print(json.dumps(state, indent=2, default=str))
