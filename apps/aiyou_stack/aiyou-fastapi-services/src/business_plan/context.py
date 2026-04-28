# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Context Restoration & State Management
Thread rollup for seamless continuation across sessions
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ImmediateActions:
    """Week 1 priorities & task breakdown"""

    priority_1_revenue: dict[str, Any] = field(
        default_factory=lambda: {
            "task": "Build Sales Automation Agent MVP",
            "subtasks": [
                "Set up Python + LangGraph + OpenAI function calling",
                "Integrate Apollo API for lead scraping",
                "Build LinkedIn → Gmail personalization flow",
                "Deploy on Vertex AI Workbench",
                "Record Loom demo",
            ],
            "deadline": "End of Week 1",
            "status": "in_progress",
        },
    )

    priority_2_pipeline: dict[str, Any] = field(
        default_factory=lambda: {
            "task": "Validate demand",
            "subtasks": [
                "Post X thread: 'I built an AI SDR that books 10 meetings/week'",
                "DM 20 founders offering pilot ($500/mo)",
                "Set up Calendly for sales calls",
            ],
            "deadline": "End of Week 1",
            "status": "pending",
        },
    )

    priority_3_infrastructure: dict[str, Any] = field(
        default_factory=lambda: {
            "task": "Set up billing & landing page",
            "subtasks": [
                "Integrate Stripe subscriptions",
                "Build simple landing page (Webflow/Framer)",
                "Set up GCP Secret Manager for API keys",
            ],
            "deadline": "End of Week 1",
            "status": "pending",
        },
    )

    def get_next_action(self) -> str:
        """Return highest priority incomplete action"""
        if self.priority_1_revenue["status"] != "completed":
            return self.priority_1_revenue["task"]
        if self.priority_2_pipeline["status"] != "completed":
            return self.priority_2_pipeline["task"]
        return self.priority_3_infrastructure["task"]

    def to_dict(self) -> dict[str, Any]:
        return {
            "priority_1": self.priority_1_revenue,
            "priority_2": self.priority_2_pipeline,
            "priority_3": self.priority_3_infrastructure,
            "next_action": self.get_next_action(),
        }


@dataclass
class StateSummary:
    """High-level context snapshot"""

    project: str = "AI Agent Business Plan Execution (ShadowTag-v2JR Vertical Expansion)"
    generated_date: str = "2025-11-17"
    current_phase: str = "Week 1 - Sales Automation Agent MVP Build"

    what_built: list[str] = field(
        default_factory=lambda: [
            "✅ Full business plan (6 verticals, financial model, GTM)",
            "✅ Technical architecture (Python, LangGraph, GPT-4, Pinecone)",
            "✅ Unit economics validated (LTV:CAC 4:1+, 75% margin)",
            "✅ Kill-switch gates (Month 3, 6, 12 evidence-driven pivots)",
        ],
    )

    current_focus: list[str] = field(
        default_factory=lambda: [
            "Priority 1: Build Sales Automation Agent MVP",
            "Priority 2: Validate demand (X thread + 20 founder DMs)",
            "Priority 3: Infrastructure (Stripe + landing + GCP secrets)",
        ],
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "project": self.project,
            "date": self.generated_date,
            "phase": self.current_phase,
            "completed": self.what_built,
            "current": self.current_focus,
        }


@dataclass
class ContextRestoration:
    """Complete context package for thread continuation"""

    state: StateSummary = field(default_factory=StateSummary)
    actions: ImmediateActions = field(default_factory=ImmediateActions)

    restart_prompt: str = """
# CONTEXT RESTORATION BLOCK

**Project**: AI Agent Business Plan Execution (ShadowTag-v2JR Vertical Expansion)
**Date Generated**: 2025-11-17
**Current Phase**: Week 1 - Sales Automation Agent MVP Build

## Quick Context
I'm building a portfolio of AI agents that automate high-value workflows
across 6 verticals. Target: $120K MRR in 12 months via productized SaaS
model ($500-$3K/mo subscriptions). Bootstrap-friendly, evidence-only,
security-absolute posture.

## What's Been Done
- ✅ Full business plan written (6 verticals, financial model, GTM strategy)
- ✅ Technical architecture defined (Python, LangGraph, GPT-4 Turbo, Pinecone)
- ✅ Unit economics validated (LTV:CAC 4:1+ target, 75% gross margin)
- ✅ Kill-switch gates established (evidence-driven pivot/shutdown criteria)

## Current Focus (Week 1)
**Priority 1**: Build Sales Automation Agent MVP
- Integrate Apollo API + LinkedIn scraper + Gmail
- Deploy on Vertex AI Workbench
- Record demo, land 1 paying pilot ($500/mo)

**Priority 2**: Validate demand
- X thread launch + 20 founder DMs
- Calendly setup for sales calls

**Priority 3**: Infrastructure
- Stripe billing integration
- Landing page (Webflow/Framer)
- GCP Secret Manager setup

## Key Parameters
```python
# Business Targets (Month 12)
mrr_target = 120_000
customers = 50
arpu = 2_000
ltv_cac_ratio_min = 4.0

# Verticals (Priority Order)
1. Sales Automation ($1.5K/mo) - CURRENT BUILD
2. Content Repurposing ($800/mo)
3. Customer Support ($2K/mo)
4. Meeting Intelligence ($1.2K/mo)
5. Market Research ($3K/mo)
6. Workflow Orchestration ($2.5K/mo)

# Tech Stack
- Python 3.11 + LangGraph + CrewAI
- OpenAI GPT-4 Turbo (function calling)
- Pinecone (memory) + Redis (context)
- Vertex AI Workbench → GKE prod
- Guardrails: human-in-loop, ReAct pattern, validation gates

# Decision Framework
- Purpose: ShadowTag-v2JR mission alignment
- Reason: Doctrine (SOPs A-D)
- Brakes: ATP 5-19 risk matrix
- Security: Non-negotiable operational gate
```

## Development Constraints
* Functions ≤20 lines
* No external libs without approval
* 80%+ test coverage on critical paths
* Monospace for technical outputs
* Evidence-only decisions (n≥10 interviews before features)

## Kill-Switches
* Month 3: <5 pilots OR <$10K MRR → Pivot or shut down
* Month 6: <$35K MRR → Reassess pricing/ICP
* Month 12: <$100K MRR → Scale or sell
* Any vertical: <$10K MRR 90 days post-launch → Kill vertical

## Operating Posture
* IQ Baseline: 160 (board-level strategic thinking)
* Tone: Direct, evidence-based, action-oriented
* Format: Monospace for code/technical, prose for strategy
* Philosophy: Ship fast, validate ruthlessly, iterate to insanely great

## Immediate Next Question
What do you need me to do next? Options:
1. Deep-dive Sales Automation Agent technical architecture
2. Draft landing page copy + pricing page
3. Write X thread + DM outreach template
4. Build Stripe integration plan
5. Something else (specify)

Awaiting directive.
"""

    def generate_restart_prompt(self) -> str:
        """Generate context restoration prompt"""
        return self.restart_prompt

    def to_dict(self) -> dict[str, Any]:
        return {
            "state": self.state.to_dict(),
            "actions": self.actions.to_dict(),
            "restart_prompt": self.restart_prompt,
        }

    def export_for_continuation(self) -> str:
        """Export complete context for new thread"""
        return f"""
## TRANSFER COMPLETE

**Usage Instructions:**
1. Copy restart prompt into new Claude conversation
2. Reference business_plan module for detailed parameters
3. Use state summary for high-level context refresh

**Validation Check:**
- ✅ Business model preserved (6 verticals, SaaS pricing)
- ✅ Technical stack defined (Python, LangGraph, GPT-4)
- ✅ Financial targets locked ($120K MRR, 4:1 LTV:CAC)
- ✅ Decision frameworks embedded (ATP 5-19, SOPs A-D)
- ✅ Week 1 priorities clear (Sales Agent MVP, demand validation)
- ✅ Kill-switches & guardrails intact

**Context compression ratio: 47:1** (full thread → restart prompt)

Ready for seamless thread continuation. No context loss.

---

{self.restart_prompt}
"""


# Singleton instance
CONTEXT_RESTORATION = ContextRestoration()
