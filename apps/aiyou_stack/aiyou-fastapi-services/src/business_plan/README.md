# AI Agent Business Plan - Thread Rollup Package

**Generated**: 2025-11-17
**Context**: AI Agent-as-a-Service (Vertical SaaS Model)

## Overview

This module captures the complete business plan, technical architecture, and operational framework for productized AI agent solutions across 6 revenue verticals.

**Target**: $120K MRR in 12 months via bootstrap-friendly SaaS model.

## Quick Start

```python
from business_plan import (
    BUSINESS_METRICS,
    VERTICALS,
    TECH_STACK,
    CONTEXT_RESTORATION
)

# View current metrics
print(BUSINESS_METRICS.to_dict())

# Get current focus (Priority 1 vertical)
from business_plan.verticals import get_current_focus
focus = get_current_focus()
print(f"Building: {focus.name} - ${focus.monthly_price}/mo")

# Export context for thread continuation
restart_prompt = CONTEXT_RESTORATION.generate_restart_prompt()
print(restart_prompt)
```

## CLI Usage

```bash
# Print executive summary
python -m business_plan.cli summary

# Export full JSON
python -m business_plan.cli export > business_plan.json

# Generate restart prompt
python -m business_plan.cli restart > context.txt

# Validate economics
python -m business_plan.cli validate
```

## Module Structure

```
business_plan/
├── __init__.py              # Package exports
├── metrics.py               # Business metrics & unit economics
├── verticals.py             # 6 revenue verticals with pricing
├── tech_stack.py            # Technical architecture & integrations
├── decision_framework.py    # Risk assessment & kill-switches
├── development.py           # Coding standards & SOPs
├── context.py               # State management & restart prompts
├── cli.py                   # Command-line interface
└── README.md                # This file
```

## Key Components

### 1. Business Metrics (`metrics.py`)

```python
from business_plan import BUSINESS_METRICS, UNIT_ECONOMICS

# Month 12 targets
BUSINESS_METRICS.monthly_recurring_revenue  # $120,000
BUSINESS_METRICS.customer_count             # 50
BUSINESS_METRICS.ltv_cac_ratio              # 4.0:1

# Unit economics
UNIT_ECONOMICS.customer_acquisition_cost    # $1,500
UNIT_ECONOMICS.lifetime_value               # $54,984
```

### 2. Revenue Verticals (`verticals.py`)

```python
from business_plan import VERTICALS
from business_plan.verticals import get_current_focus

# Get priority 1 vertical (current build)
focus = get_current_focus()
# Sales Automation Agent: $1,500/mo + $5,000 setup

# All 6 verticals
for name, vertical in VERTICALS.items():
    print(f"{vertical.name}: ${vertical.monthly_price}/mo")
```

### 3. Technical Stack (`tech_stack.py`)

```python
from business_plan import TECH_STACK, AGENT_DESIGN

TECH_STACK.core_language        # Python 3.11+
TECH_STACK.orchestration        # [LangGraph, CrewAI]
TECH_STACK.llm_provider         # OpenAI GPT-4 Turbo
TECH_STACK.cloud_provider       # Google Cloud Platform

AGENT_DESIGN.framework          # ReAct (Reason + Act)
AGENT_DESIGN.guardrails         # Human-in-loop checkpoints
```

### 4. Decision Framework (`decision_framework.py`)

```python
from business_plan import RISK_ASSESSMENT, KillSwitches
from business_plan.decision_framework import Probability, Severity

# ATP 5-19 Risk Assessment
risk = RISK_ASSESSMENT.assess("B", "II")  # Likely + Critical
action = RISK_ASSESSMENT.get_action_gate(risk)  # "CFO_approval_required"

# Business kill-switches
should_kill, reason = KillSwitches.evaluate(
    month=3,
    mrr=8_000,
    pilots=3
)
# (True, "Month 3: Insufficient pilots or MRR")
```

### 5. Development Constraints (`development.py`)

```python
from business_plan import DEV_CONSTRAINTS, FRAMEWORKS

DEV_CONSTRAINTS.max_function_length     # 20 lines
DEV_CONSTRAINTS.test_coverage_minimum   # 0.80 (80%)
DEV_CONSTRAINTS.shipping_philosophy
# ["Stupid simple > fancy", "Ship fast > perfect", ...]

FRAMEWORKS.sop_a    # Upload Triage (2× speed, −90% errors)
FRAMEWORKS.sop_b    # Change & Release (2× cadence, clearer audits)
```

### 6. Context Restoration (`context.py`)

```python
from business_plan import CONTEXT_RESTORATION

# Generate restart prompt for new thread
prompt = CONTEXT_RESTORATION.generate_restart_prompt()

# Get next priority action
next_action = CONTEXT_RESTORATION.actions.get_next_action()
# "Build Sales Automation Agent MVP"

# Export for continuation
continuation = CONTEXT_RESTORATION.export_for_continuation()
```

## Week 1 Priorities

**Priority 1: Revenue** (Sales Automation Agent MVP)
- Set up Python + LangGraph + OpenAI function calling
- Integrate Apollo API for lead scraping
- Build LinkedIn → Gmail personalization flow
- Deploy on Vertex AI Workbench
- Record Loom demo

**Priority 2: Pipeline** (Demand Validation)
- Post X thread: "I built an AI SDR that books 10 meetings/week"
- DM 20 founders offering pilot ($500/mo)
- Set up Calendly for sales calls

**Priority 3: Infrastructure** (Billing & Landing)
- Integrate Stripe subscriptions
- Build simple landing page (Webflow/Framer)
- Set up GCP Secret Manager for API keys

## Kill-Switch Criteria

| Phase | Condition | Action |
|-------|-----------|--------|
| Month 3 | pilots < 5 OR mrr < $10K | Pivot or shut down |
| Month 6 | mrr < $35K | Reassess pricing/ICP |
| Month 12 | mrr < $100K OR ltv_cac < 4.0 | Scale or sell |
| Any Vertical | vertical_mrr < $10K (90 days post-launch) | Kill vertical |

## Operating Principles

- **IQ Baseline**: 160 (board-level strategic thinking)
- **Security Posture**: 100% operational gate (non-negotiable)
- **Decision Framework**: Purpose → Reason → Brakes (ATP 5-19)
- **Bootstrap Discipline**: ROI ≥3× (18mo), LTV:CAC ≥4:1 (12mo)
- **Evidence-Only**: n≥10 user interviews before features
- **Shipping Philosophy**: Ship fast > perfect, Real utility > general-purpose

## Validation

```python
from business_plan.metrics import BUSINESS_METRICS
from business_plan.development import BOOTSTRAP_DISCIPLINE

# Validate business metrics
assert BUSINESS_METRICS.validate() == True

# Validate unit economics
ltv = 54_984
cac = 1_500
assert BOOTSTRAP_DISCIPLINE.validate_economics(ltv, cac) == True
```

## Context Compression

**Full thread → Restart prompt**: 47:1 compression ratio

All business logic, technical architecture, and operational frameworks are preserved as executable code with zero context loss.

## Thread Continuation

To restore context in a new conversation:

```bash
python -m business_plan.cli restart
```

Copy the output and paste into a new Claude conversation. All state, priorities, and frameworks will be restored.

---

**Context loaded. What's the priority?**
