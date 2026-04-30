#!/usr/bin/env python3
"""
JR Auto-Validator
Validates tool usage against JR (Purpose/Reasons/Brakes) framework constraints
"""

import argparse
import json
import re

# JR Framework constraints
JR_CONSTRAINTS = {
    "roi_minimum": 3.0,  # 3× ROI minimum
    "ltv_cac_minimum": 4.0,  # 4:1 LTV:CAC minimum
    "p99_latency_ms": 90,  # <90ms p99 latency
    "kill_switch": "required",  # All deployments
    "iteration_weeks": 2,  # Max iteration cycle
    "monthly_burn_max": 65000,  # $65K max monthly burn
    "env_restriction": "vertex",  # Vertex AI Workbench only
}

# Tools that require JR validation
DEPLOYMENT_TOOLS = ["Bash", "Write", "Edit"]
SKIP_VALIDATION_TOOLS = ["Read", "Glob", "Grep", "WebFetch"]


def extract_metrics_from_input(tool_input: str) -> dict:
    """Extract JR-relevant metrics from tool input."""
    metrics = {}

    # ROI extraction
    roi_match = re.search(r"roi[:\s]+([0-9.]+)", tool_input, re.IGNORECASE)
    if roi_match:
        metrics["roi"] = float(roi_match.group(1))

    # LTV:CAC extraction
    ltv_cac_match = re.search(r"ltv[:\s]*cac[:\s]+([0-9.]+)", tool_input, re.IGNORECASE)
    if ltv_cac_match:
        metrics["ltv_cac"] = float(ltv_cac_match.group(1))

    # Latency extraction
    latency_match = re.search(r"p99[:\s]+([0-9]+)\s*ms", tool_input, re.IGNORECASE)
    if latency_match:
        metrics["p99_latency"] = int(latency_match.group(1))

    # Kill switch check
    if "kill" in tool_input.lower() and "switch" in tool_input.lower():
        metrics["has_kill_switch"] = True
    elif "deployment" in tool_input.lower() or "deploy" in tool_input.lower():
        # Deployment without kill switch mention
        metrics["has_kill_switch"] = False

    # Timeline extraction
    timeline_match = re.search(r"([0-9]+)\s*week", tool_input, re.IGNORECASE)
    if timeline_match:
        metrics["timeline_weeks"] = int(timeline_match.group(1))

    # Cost extraction
    cost_match = re.search(r"\$([0-9,]+)k?/mo", tool_input, re.IGNORECASE)
    if cost_match:
        cost_str = cost_match.group(1).replace(",", "")
        cost = float(cost_str)
        if "k" in tool_input.lower():
            cost *= 1000
        metrics["monthly_cost"] = cost

    return metrics


def validate_jr(metrics: dict) -> list[str]:
    """Validate metrics against JR constraints."""
    violations = []

    # ROI check
    if "roi" in metrics and metrics["roi"] < JR_CONSTRAINTS["roi_minimum"]:
        violations.append(f"⚠️ JR VIOLATION: ROI {metrics['roi']}× < {JR_CONSTRAINTS['roi_minimum']}× minimum")

    # LTV:CAC check
    if "ltv_cac" in metrics and metrics["ltv_cac"] < JR_CONSTRAINTS["ltv_cac_minimum"]:
        violations.append(f"⚠️ JR VIOLATION: LTV:CAC {metrics['ltv_cac']}:1 < {JR_CONSTRAINTS['ltv_cac_minimum']}:1 minimum")

    # Latency check
    if "p99_latency" in metrics and metrics["p99_latency"] > JR_CONSTRAINTS["p99_latency_ms"]:
        violations.append(f"⚠️ JR VIOLATION: p99 {metrics['p99_latency']}ms > {JR_CONSTRAINTS['p99_latency_ms']}ms limit")

    # Kill switch check
    if "has_kill_switch" in metrics and not metrics["has_kill_switch"]:
        violations.append("⚠️ JR VIOLATION: No kill switch defined for deployment")

    # Iteration time check
    if "timeline_weeks" in metrics and metrics["timeline_weeks"] > JR_CONSTRAINTS["iteration_weeks"]:
        violations.append(f"⚠️ JR VIOLATION: {metrics['timeline_weeks']} weeks > {JR_CONSTRAINTS['iteration_weeks']} week iteration limit")

    # Burn rate check
    if "monthly_cost" in metrics and metrics["monthly_cost"] > JR_CONSTRAINTS["monthly_burn_max"]:
        violations.append(f"⚠️ JR VIOLATION: ${metrics['monthly_cost']:,.0f}/mo > ${JR_CONSTRAINTS['monthly_burn_max']:,} budget")

    return violations


def main():
    parser = argparse.ArgumentParser(description="Validate tool usage against JR constraints")
    parser.add_argument("--tool", required=True, help="Tool name")
    parser.add_argument("--input", required=True, help="Tool input (JSON)")
    args = parser.parse_args()

    tool_name = args.tool
    tool_input_str = args.input

    # Skip validation for read-only tools
    if tool_name in SKIP_VALIDATION_TOOLS:
        print(json.dumps({"decision": "approve"}))
        return 0

    # Parse tool input
    try:
        tool_input = json.loads(tool_input_str)
        # Convert to string for pattern matching
        tool_input_text = json.dumps(tool_input, indent=2)
    except json.JSONDecodeError:
        # If not JSON, use as-is
        tool_input_text = tool_input_str

    # Extract metrics
    metrics = extract_metrics_from_input(tool_input_text)

    # If no JR-relevant metrics found, approve
    if not metrics:
        print(json.dumps({"decision": "approve"}))
        return 0

    # Validate against JR constraints
    violations = validate_jr(metrics)

    if violations:
        # JR violations detected - block
        output = {"decision": "block", "reason": "\n".join(violations)}
        print(json.dumps(output))
        return 1
    else:
        # JR compliant
        print(json.dumps({"decision": "approve"}))
        return 0


if __name__ == "__main__":
    exit(main())
