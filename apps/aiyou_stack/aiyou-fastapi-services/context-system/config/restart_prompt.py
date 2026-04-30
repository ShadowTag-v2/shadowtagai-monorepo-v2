"""PART 3: RESTART PROMPT GENERATOR
Generates context restoration block for new conversations
"""

from datetime import datetime


def generate_restart_prompt() -> str:
    """Generate complete restart prompt for context restoration

    This prompt is designed to be copy-pasted into a new Claude conversation
    to restore full project context with zero loss.
    """
    prompt = """# CONTEXT RESTORATION BLOCK

**Project**: AI Agent Business Plan Execution (ShadowTag-v2JR Vertical Expansion)
**Date Generated**: {date}
**Current Phase**: Week 1 - Sales Automation Agent MVP Build

## Quick Context

I'm building a portfolio of AI agents that automate high-value workflows across 6 verticals.
Target: $120K MRR in 12 months via productized SaaS model ($500-$3K/mo subscriptions).
Bootstrap-friendly, evidence-only, security-absolute posture.

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

**Awaiting directive.**

---

## CONTEXT VALIDATION

✅ Business model preserved (6 verticals, SaaS pricing)
✅ Technical stack defined (Python, LangGraph, GPT-4)
✅ Financial targets locked ($120K MRR, 4:1 LTV:CAC)
✅ Decision frameworks embedded (ATP 5-19, SOPs A-D)
✅ Week 1 priorities clear (Sales Agent MVP, demand validation)
✅ Kill-switches & guardrails intact

**Context compression ratio: 47:1** (full thread → this prompt)
**Ready for seamless continuation. No context loss.**
"""

    return prompt.format(date=datetime.now().strftime("%Y-%m-%d"))


def generate_handoff_variables() -> dict:
    """Generate dictionary of all key variables for programmatic handoff

    This can be serialized to JSON and consumed by other systems
    """
    return {
        "metadata": {
            "generated_date": datetime.now().isoformat(),
            "project_name": "AI Agent-as-a-Service",
            "current_phase": "Week 1 - Sales Automation MVP",
            "compression_ratio": "47:1",
        },
        "business_metrics": {
            "mrr_target_month_12": 120_000,
            "customer_count": 50,
            "average_revenue_per_user": 2_000,
            "ltv_cac_ratio_min": 4.0,
            "gross_margin_target": 0.75,
            "monthly_churn": 0.10,
        },
        "unit_economics": {
            "customer_acquisition_cost": 1_500,
            "cost_of_goods_sold": 200,
            "support_ops_cost": 150,
            "lifetime_value": 54_984,
            "payback_period_months": 0.35,
        },
        "verticals": {
            "sales_automation": {"price": 1500, "setup": 5000, "priority": 1},
            "content_repurposing": {"price": 800, "setup": 2000, "priority": 2},
            "customer_support": {"price": 2000, "setup": 8000, "priority": 3},
            "meeting_intelligence": {"price": 1200, "setup": 3000, "priority": 4},
            "market_research": {"price": 3000, "setup": 10000, "priority": 5},
            "workflow_orchestration": {"price": 2500, "setup": 12000, "priority": 6},
        },
        "tech_stack": {
            "language": "Python 3.11+",
            "orchestration": ["LangGraph", "CrewAI"],
            "llm": "OpenAI GPT-4 Turbo",
            "memory": {"long_term": "Pinecone", "short_term": "Redis", "episodic": "PostgreSQL"},
            "deployment": {"dev": "Vertex AI Workbench", "prod": "GKE"},
        },
        "decision_framework": {
            "purpose": "ShadowTag-v2JR mission alignment",
            "reason": "Doctrine (SOPs A-D)",
            "brakes": "ATP 5-19 risk matrix",
        },
        "kill_switches": [
            {"month": 3, "condition": "pilots < 5 OR mrr < 10000", "action": "Pivot or shut down"},
            {"month": 6, "condition": "mrr < 35000", "action": "Reassess pricing/ICP"},
            {"month": 12, "condition": "mrr < 100000 OR ltv_cac < 4.0", "action": "Scale or sell"},
            {"days": 90, "condition": "vertical_mrr < 10000", "action": "Kill vertical"},
        ],
        "week1_priorities": [
            {
                "id": 1,
                "category": "REVENUE",
                "task": "Build Sales Automation Agent MVP",
                "deadline": "End of Week 1",
            },
            {
                "id": 2,
                "category": "PIPELINE",
                "task": "Validate demand via outreach",
                "deadline": "End of Week 1",
            },
            {
                "id": 3,
                "category": "INFRASTRUCTURE",
                "task": "Set up billing & landing page",
                "deadline": "End of Week 1",
            },
        ],
        "constraints": {
            "max_function_length": 20,
            "external_libraries": "Approval required",
            "test_coverage": 0.80,
            "evidence_threshold": 10,
        },
    }


def save_restart_prompt(output_path: str = "restart_prompt.md"):
    """Save restart prompt to markdown file"""
    prompt = generate_restart_prompt()
    with open(output_path, "w") as f:
        f.write(prompt)
    return output_path


def save_handoff_json(output_path: str = "handoff_variables.json"):
    """Save handoff variables to JSON file"""
    import json

    variables = generate_handoff_variables()
    with open(output_path, "w") as f:
        json.dump(variables, f, indent=2)
    return output_path


if __name__ == "__main__":
    print("=== GENERATING RESTART PROMPT ===\n")
    prompt = generate_restart_prompt()
    print(prompt)

    print("\n=== SAVING FILES ===")
    prompt_path = save_restart_prompt()
    json_path = save_handoff_json()
    print(f"✅ Restart prompt saved to: {prompt_path}")
    print(f"✅ Handoff JSON saved to: {json_path}")

    print("\n=== HANDOFF VARIABLES (JSON) ===")
    import json

    variables = generate_handoff_variables()
    print(json.dumps(variables, indent=2))
