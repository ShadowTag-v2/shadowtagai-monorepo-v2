# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Current Objectives - Week 1 Execution Priorities
Immediate action items with clear deliverables and deadlines
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta


@dataclass
class SubTask:
    """Individual subtask within a priority"""

    description: str
    estimated_hours: float
    owner: str = "Founder"
    completed: bool = False


@dataclass
class Priority:
    """Week 1 priority with subtasks"""

    id: int
    category: str
    task: str
    subtasks: list[SubTask]
    deadline: str
    success_criteria: str
    blockers: list[str] = field(default_factory=list)


class Week1Priorities:
    """Week 1 immediate action plan"""

    PRIORITIES = [
        Priority(
            id=1,
            category="REVENUE",
            task="Build Sales Automation Agent MVP",
            subtasks=[
                SubTask(
                    description="Set up Python + LangGraph + OpenAI function calling",
                    estimated_hours=4.0,
                ),
                SubTask(description="Integrate Apollo API for lead scraping", estimated_hours=6.0),
                SubTask(
                    description="Build LinkedIn → Gmail personalization flow",
                    estimated_hours=8.0,
                ),
                SubTask(description="Deploy on Vertex AI Workbench", estimated_hours=4.0),
                SubTask(description="Record Loom demo (5-min walkthrough)", estimated_hours=2.0),
            ],
            deadline="End of Week 1",
            success_criteria="Working demo that scrapes 100 leads, personalizes 10 emails, sends via Gmail",
            blockers=[
                "Apollo API access (requires paid account)",
                "GCP Vertex AI Workbench setup",
                "OpenAI API credits",
            ],
        ),
        Priority(
            id=2,
            category="PIPELINE",
            task="Validate demand via outreach",
            subtasks=[
                SubTask(
                    description="Write X thread: 'I built an AI SDR that books 10 meetings/week'",
                    estimated_hours=1.0,
                ),
                SubTask(description="DM 20 founders offering pilot ($500/mo)", estimated_hours=3.0),
                SubTask(description="Set up Calendly for sales calls", estimated_hours=0.5),
                SubTask(description="Prepare pilot onboarding doc (1-pager)", estimated_hours=1.0),
            ],
            deadline="End of Week 1",
            success_criteria="3+ qualified sales call bookings, 1 pilot commitment ($500/mo)",
            blockers=["X/Twitter account setup", "Founder DM list (need target ICP list)"],
        ),
        Priority(
            id=3,
            category="INFRASTRUCTURE",
            task="Set up billing & landing page",
            subtasks=[
                SubTask(
                    description="Integrate Stripe subscriptions ($500, $1.5K, $3K tiers)",
                    estimated_hours=4.0,
                ),
                SubTask(
                    description="Build simple landing page (Webflow/Framer)",
                    estimated_hours=6.0,
                ),
                SubTask(description="Set up GCP Secret Manager for API keys", estimated_hours=2.0),
                SubTask(
                    description="Create pilot agreement template (1-page PDF)",
                    estimated_hours=1.0,
                ),
            ],
            deadline="End of Week 1",
            success_criteria="Live landing page, Stripe checkout working, secrets secured",
            blockers=["Stripe account approval (can take 1-2 days)", "GCP billing account setup"],
        ),
    ]

    @classmethod
    def get_total_hours(cls) -> float:
        """Calculate total estimated hours for Week 1"""
        return sum(
            sum(subtask.estimated_hours for subtask in priority.subtasks)
            for priority in cls.PRIORITIES
        )

    @classmethod
    def get_completion_percentage(cls) -> float:
        """Calculate completion percentage"""
        total_tasks = sum(len(p.subtasks) for p in cls.PRIORITIES)
        completed_tasks = sum(sum(1 for st in p.subtasks if st.completed) for p in cls.PRIORITIES)
        return (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

    @classmethod
    def get_critical_path(cls) -> list[str]:
        """Identify critical path (dependencies)"""
        return [
            "GCP setup → Vertex AI deployment",
            "Apollo API → Lead scraping → Email personalization",
            "Demo video → X thread → DM outreach",
            "Landing page → Stripe integration → Pilot agreement",
            "Sales calls → Pilot commitment → Revenue",
        ]


@dataclass
class WeeklyGoal:
    """Week-level goal and success metric"""

    week: int
    mrr_target: int
    customer_target: int
    key_milestone: str
    blocker_resolution: list[str]


class PhaseTimeline:
    """12-month phase timeline with weekly breakdown"""

    PHASE_1_WEEKS = [
        WeeklyGoal(
            week=1,
            mrr_target=0,
            customer_target=0,
            key_milestone="Sales Agent MVP live, 1 pilot commitment",
            blocker_resolution=[
                "GCP account setup",
                "Apollo API access",
                "Stripe account approval",
            ],
        ),
        WeeklyGoal(
            week=2,
            mrr_target=500,
            customer_target=1,
            key_milestone="First paying pilot live, onboarding complete",
            blocker_resolution=[
                "Pilot feedback loop established",
                "Bug fixes from Week 1 deployment",
            ],
        ),
        WeeklyGoal(
            week=3,
            mrr_target=1500,
            customer_target=3,
            key_milestone="3 pilots live, outbound engine scaling",
            blocker_resolution=["Automate onboarding workflow", "Build customer dashboard"],
        ),
        WeeklyGoal(
            week=4,
            mrr_target=2500,
            customer_target=5,
            key_milestone="5 pilots live, Month 1 kill-switch evaluation",
            blocker_resolution=[
                "Reach $2.5K MRR or reassess ICP/pricing",
                "Document learnings for pivot if needed",
            ],
        ),
    ]


def generate_week1_action_plan() -> dict:
    """Generate actionable Week 1 execution plan"""
    return {
        "week": 1,
        "start_date": datetime.now().isoformat(),
        "end_date": (datetime.now() + timedelta(days=7)).isoformat(),
        "total_estimated_hours": Week1Priorities.get_total_hours(),
        "priorities": [
            {
                "id": p.id,
                "category": p.category,
                "task": p.task,
                "subtasks": [
                    {
                        "description": st.description,
                        "estimated_hours": st.estimated_hours,
                        "owner": st.owner,
                        "completed": st.completed,
                    }
                    for st in p.subtasks
                ],
                "deadline": p.deadline,
                "success_criteria": p.success_criteria,
                "blockers": p.blockers,
            }
            for p in Week1Priorities.PRIORITIES
        ],
        "critical_path": Week1Priorities.get_critical_path(),
        "completion_percentage": Week1Priorities.get_completion_percentage(),
        "phase_1_timeline": [
            {
                "week": wg.week,
                "mrr_target": wg.mrr_target,
                "customer_target": wg.customer_target,
                "key_milestone": wg.key_milestone,
                "blocker_resolution": wg.blocker_resolution,
            }
            for wg in PhaseTimeline.PHASE_1_WEEKS
        ],
    }


def get_immediate_next_action() -> dict:
    """Get the very next action to take right now"""
    return {
        "action": "Set up Python development environment",
        "command": "python3.11 -m venv venv && source venv/bin/activate && pip install langgraph openai pinecone-client redis anthropic",
        "estimated_minutes": 15,
        "success_criteria": "Virtual environment active, all core dependencies installed",
        "next_after_this": "Configure GCP Vertex AI Workbench instance",
        "blocker_check": [
            "Python 3.11+ installed? (python3.11 --version)",
            "GCP account active? (gcloud auth list)",
            "OpenAI API key ready? (check dashboard)",
        ],
    }


if __name__ == "__main__":
    import json

    plan = generate_week1_action_plan()
    next_action = get_immediate_next_action()

    print("=== WEEK 1 ACTION PLAN ===")
    print(json.dumps(plan, indent=2))
    print("\n=== IMMEDIATE NEXT ACTION ===")
    print(json.dumps(next_action, indent=2))
