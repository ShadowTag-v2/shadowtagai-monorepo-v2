#!/usr/bin/env python3
"""Business Plan CLI Interface
Query and export business plan parameters
"""

import json
from typing import Any

from .context import CONTEXT_RESTORATION
from .decision_framework import DECISION_PROTOCOL, KillSwitches
from .development import BOOTSTRAP_DISCIPLINE, DEV_CONSTRAINTS, FRAMEWORKS, OPERATING_PRINCIPLES
from .metrics import BUSINESS_METRICS, UNIT_ECONOMICS
from .tech_stack import AGENT_DESIGN, TECH_STACK
from .verticals import VERTICALS, get_current_focus, get_total_mrr


def export_all() -> dict[str, Any]:
    """Export complete business plan as JSON"""
    return {
        "metadata": {
            "project": "AI Agent Business Plan",
            "generated": "2025-11-17",
            "version": "1.0.0",
        },
        "business_metrics": BUSINESS_METRICS.to_dict(),
        "unit_economics": UNIT_ECONOMICS.to_dict(),
        "verticals": {name: v.to_dict() for name, v in VERTICALS.items()},
        "total_mrr": get_total_mrr(),
        "current_focus": get_current_focus().to_dict(),
        "tech_stack": TECH_STACK.to_dict(),
        "agent_design": AGENT_DESIGN.to_dict(),
        "decision_protocol": DECISION_PROTOCOL.to_dict(),
        "kill_switches": KillSwitches.to_dict(),
        "dev_constraints": DEV_CONSTRAINTS.to_dict(),
        "frameworks": FRAMEWORKS.to_dict(),
        "operating_principles": OPERATING_PRINCIPLES.to_dict(),
        "bootstrap_discipline": BOOTSTRAP_DISCIPLINE.to_dict(),
        "context": CONTEXT_RESTORATION.to_dict(),
    }


def print_summary():
    """Print executive summary to console"""
    print("=" * 70)
    print("AI AGENT BUSINESS PLAN - EXECUTIVE SUMMARY")
    print("=" * 70)
    print()

    print("TARGET METRICS (Month 12):")
    print(f"  MRR Target:        ${BUSINESS_METRICS.monthly_recurring_revenue:,}")
    print(f"  Customers:         {BUSINESS_METRICS.customer_count}")
    print(f"  ARPU:              ${BUSINESS_METRICS.average_revenue_per_user:,}")
    print(f"  LTV:CAC Ratio:     {BUSINESS_METRICS.ltv_cac_ratio}:1")
    print(f"  Gross Margin:      {BUSINESS_METRICS.gross_margin * 100:.0f}%")
    print()

    print("CURRENT FOCUS (Priority 1):")
    focus = get_current_focus()
    print(f"  Vertical:          {focus.name}")
    print(f"  Monthly Price:     ${focus.monthly_price:,}")
    print(f"  Setup Fee:         ${focus.setup_fee:,}")
    print(f"  Target Customers:  {focus.target_customers}")
    print(f"  MRR Contribution:  ${focus.mrr_contribution:,}")
    print()

    print("TECH STACK:")
    print(f"  Language:          {TECH_STACK.core_language}")
    print(f"  Orchestration:     {', '.join(TECH_STACK.orchestration)}")
    print(f"  LLM Provider:      {TECH_STACK.llm_provider}")
    print(f"  Cloud:             {TECH_STACK.cloud_provider}")
    print()

    print("WEEK 1 PRIORITIES:")
    actions = CONTEXT_RESTORATION.actions
    print(f"  1. {actions.priority_1_revenue['task']}")
    print(f"  2. {actions.priority_2_pipeline['task']}")
    print(f"  3. {actions.priority_3_infrastructure['task']}")
    print()

    print("KILL-SWITCHES:")
    for switch in KillSwitches.SWITCHES[:3]:
        print(f"  {switch.phase}: {switch.condition}")
        print(f"    → {switch.action}")
    print()

    print("=" * 70)
    print("Context loaded. Ready for execution.")
    print("=" * 70)


def export_restart_prompt() -> str:
    """Export context restoration prompt"""
    return CONTEXT_RESTORATION.export_for_continuation()


def validate_economics() -> bool:
    """Validate business metrics meet constraints"""
    if not BUSINESS_METRICS.validate():
        print("❌ Business metrics validation FAILED")
        return False

    ltv = UNIT_ECONOMICS.lifetime_value
    cac = UNIT_ECONOMICS.customer_acquisition_cost
    if not BOOTSTRAP_DISCIPLINE.validate_economics(ltv, cac):
        print(f"❌ Unit economics validation FAILED (LTV:CAC = {ltv / cac:.2f})")
        return False

    print("✅ All validations passed")
    return True


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print_summary()
        sys.exit(0)

    command = sys.argv[1]

    if command == "export":
        data = export_all()
        print(json.dumps(data, indent=2))

    elif command == "restart":
        print(export_restart_prompt())

    elif command == "validate":
        validate_economics()

    elif command == "summary":
        print_summary()

    else:
        print(f"Unknown command: {command}")
        print("Usage: python -m business_plan.cli [export|restart|validate|summary]")
        sys.exit(1)
