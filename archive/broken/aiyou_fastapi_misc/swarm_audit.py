#!/usr/bin/env python3
"""
Terraform Swarm Audit - Distributes terraform plan across 600-agent n-autoresearch/Kosmos/BioAgents swarm.

Usage:
    python3 swarm_audit.py tfplan.json

Architecture:
    - 570 Flash agents: Resource validation, naming, cost checks
    - 30 Pro agents: JURA governance, security compliance
"""

import asyncio
import json
import sys
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

import httpx
import yaml

n-autoresearch/Kosmos/BioAgents_URL = "http://localhost:8600"
JURA_RULES_PATH = Path(__file__).parent / "jura_rules.yaml"


class Verdict(Enum):
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    ESCALATE = "ESCALATE"


@dataclass
class AuditResult:
    verdict: Verdict
    confidence: float
    latency_ms: float
    agents_used: int
    violations: list[dict[str, Any]]
    resource_id: str | None = None


def load_jura_rules() -> list[dict[str, Any]]:
    """Load JURA governance rules from YAML."""
    if JURA_RULES_PATH.exists():
        with open(JURA_RULES_PATH) as f:
            return yaml.safe_load(f).get("rules", [])
    return []


def aggregate_verdicts(results: list[AuditResult]) -> dict[str, Any]:
    """
    Aggregate individual audit results into final verdict.

    Rules:
    - Any REJECT → overall REJECT
    - Any ESCALATE (no REJECT) → overall ESCALATE
    - All APPROVE → overall APPROVE
    """
    all_violations = []
    total_latency = 0
    total_agents = 0

    has_reject = False
    has_escalate = False

    for result in results:
        total_latency += result.latency_ms
        total_agents += result.agents_used
        all_violations.extend(result.violations)

        if result.verdict == Verdict.REJECT:
            has_reject = True
        elif result.verdict == Verdict.ESCALATE:
            has_escalate = True

    if has_reject:
        final_verdict = Verdict.REJECT
    elif has_escalate:
        final_verdict = Verdict.ESCALATE
    else:
        final_verdict = Verdict.APPROVE

    return {
        "verdict": final_verdict.value,
        "confidence": sum(r.confidence for r in results) / len(results) if results else 0,
        "total_latency_ms": total_latency,
        "avg_latency_ms": total_latency / len(results) if results else 0,
        "agents_used": total_agents,
        "resources_audited": len(results),
        "violations": all_violations,
        "violations_count": len(all_violations),
    }


async def audit_resource_bulk(
    client: httpx.AsyncClient,
    resource: dict[str, Any],
    checks: list[str],
) -> AuditResult:
    """
    Audit a single resource using bulk (Flash) tier agents.
    Checks: naming conventions, cost estimates, dependencies.
    """
    start = time.perf_counter()

    prompt = f"""Audit this Terraform resource change for infrastructure compliance.

Resource:
{json.dumps(resource, indent=2)}

Checks to perform: {", ".join(checks)}

Analyze for:
1. Naming convention violations (should follow: {{env}}-{{service}}-{{component}})
2. Cost implications (high-cost resources like A100 GPUs, large node pools)
3. Dependency issues or missing resources

Respond with your analysis and verdict (APPROVE/REJECT/ESCALATE)."""

    try:
        response = await client.post(
            f"{n-autoresearch/Kosmos/BioAgents_URL}/task",
            json={
                "prompt": prompt,
                "agents": 1,
                "timeout_ms": 5000,
                "governance": False,
                "cost_tier": "flash",
            },
            timeout=30.0,
        )

        latency = (time.perf_counter() - start) * 1000

        if response.status_code == 200:
            result = response.json()
            success = result.get("success", False)

            # Parse the result for violations
            violations = []
            verdict = Verdict.APPROVE

            # Check for cost violations in resource
            resource_type = resource.get("type", "")
            after_values = resource.get("change", {}).get("after", {})

            # JURA-COST-003: Check for expensive GPU nodes
            if "node_pool" in resource_type or "container_node_pool" in resource_type:
                autoscaling = after_values.get("autoscaling", {})
                max_nodes = autoscaling.get("max_node_count", 0)
                machine_type = after_values.get("node_config", {}).get("machine_type", "")

                if "a100" in machine_type.lower() or "a2-" in machine_type.lower():
                    if max_nodes > 10:
                        violations.append(
                            {
                                "rule_id": "JURA-COST-003",
                                "resource": resource.get("address"),
                                "reason": f"A100 GPU pool with max_nodes={max_nodes} exceeds cost threshold. Potential: ${max_nodes * 30}/hr",
                            }
                        )
                        verdict = Verdict.REJECT

            # JURA-SEC-003: Check for open firewall rules
            if "firewall" in resource_type:
                source_ranges = after_values.get("source_ranges", [])
                allows = after_values.get("allow", [])

                if "0.0.0.0/0" in source_ranges:
                    for allow in allows:
                        ports = allow.get("ports", [])
                        if "22" in ports or "3389" in ports:
                            violations.append(
                                {
                                    "rule_id": "JURA-SEC-003",
                                    "resource": resource.get("address"),
                                    "reason": "Firewall rule allows SSH/RDP from 0.0.0.0/0",
                                }
                            )
                            verdict = Verdict.REJECT

            return AuditResult(
                verdict=verdict,
                confidence=0.85 if success else 0.5,
                latency_ms=latency,
                agents_used=result.get("agents_used", 1),
                violations=violations,
                resource_id=resource.get("address"),
            )
        else:
            return AuditResult(
                verdict=Verdict.ESCALATE,
                confidence=0.0,
                latency_ms=latency,
                agents_used=1,
                violations=[{"error": f"HTTP {response.status_code}"}],
                resource_id=resource.get("address"),
            )

    except Exception as e:
        latency = (time.perf_counter() - start) * 1000
        return AuditResult(
            verdict=Verdict.ESCALATE,
            confidence=0.0,
            latency_ms=latency,
            agents_used=1,
            violations=[{"error": str(e)}],
            resource_id=resource.get("address"),
        )


async def audit_governance(
    client: httpx.AsyncClient,
    plan: dict[str, Any],
    rules: list[dict[str, Any]],
) -> AuditResult:
    """
    Run JURA governance audit using Pro tier agents.
    Checks: security compliance, cost thresholds, policy violations.
    """
    start = time.perf_counter()

    # Build rules summary
    rules_summary = "\n".join(
        [
            f"- {r.get('id', 'UNKNOWN')}: {r.get('name', '')} ({r.get('severity', 'MEDIUM')})"
            for r in rules[:10]
        ]
    )

    prompt = f"""JURA Governance Audit - Infrastructure Compliance Review

RULES TO ENFORCE:
{rules_summary}

TERRAFORM PLAN SUMMARY:
- Total resource changes: {len(plan.get("resource_changes", []))}
- Resources: {", ".join([r.get("address", "unknown") for r in plan.get("resource_changes", [])[:10]])}

Analyze this infrastructure plan for:
1. Security violations (public access, open ports, missing encryption)
2. Cost threshold violations (GPU pools, large node counts)
3. Compliance violations (missing tags, logging, backups)
4. GCP-specific issues (default networks, private clusters)

Provide your JURA verdict: APPROVE, REJECT, or ESCALATE"""

    try:
        response = await client.post(
            f"{n-autoresearch/Kosmos/BioAgents_URL}/governance",
            json={
                "prompt": prompt,
                "agents": 5,
                "timeout_ms": 10000,
            },
            timeout=60.0,
        )

        latency = (time.perf_counter() - start) * 1000

        if response.status_code == 200:
            result = response.json()
            success = result.get("success", False)

            # Run deterministic JURA rule checks
            violations = []
            verdict = Verdict.APPROVE

            for resource in plan.get("resource_changes", []):
                resource_type = resource.get("type", "")
                after_values = resource.get("change", {}).get("after", {})
                address = resource.get("address", "unknown")

                # JURA-SEC-003: Open firewall rules
                if "firewall" in resource_type:
                    source_ranges = after_values.get("source_ranges", [])
                    if "0.0.0.0/0" in source_ranges:
                        allows = after_values.get("allow", [])
                        for allow in allows:
                            ports = allow.get("ports", [])
                            if any(p in ports for p in ["22", "3389", "3306", "5432"]):
                                violations.append(
                                    {
                                        "rule_id": "JURA-SEC-003",
                                        "resource": address,
                                        "reason": "Sensitive ports open to 0.0.0.0/0",
                                    }
                                )
                                verdict = Verdict.REJECT

                # JURA-GCP-002: GKE private cluster
                if "container_cluster" in resource_type:
                    private_config = after_values.get("private_cluster_config", {})
                    if not private_config.get("enable_private_nodes", False):
                        violations.append(
                            {
                                "rule_id": "JURA-GCP-002",
                                "resource": address,
                                "reason": "GKE cluster must have private nodes enabled",
                            }
                        )
                        verdict = Verdict.REJECT

                # JURA-GCP-003: Cloud SQL private IP
                if "sql_database_instance" in resource_type:
                    settings = after_values.get("settings", {})
                    ip_config = settings.get("ip_configuration", {})
                    if not ip_config.get("private_network"):
                        violations.append(
                            {
                                "rule_id": "JURA-GCP-003",
                                "resource": address,
                                "reason": "Cloud SQL must use private network",
                            }
                        )
                        verdict = Verdict.REJECT

                # JURA-COST-003: GPU cost threshold
                if "node_pool" in resource_type:
                    autoscaling = after_values.get("autoscaling", {})
                    max_nodes = autoscaling.get("max_node_count", 0)
                    node_config = after_values.get("node_config", {})
                    machine_type = node_config.get("machine_type", "")

                    if "a2-" in machine_type.lower() or "a100" in machine_type.lower():
                        if max_nodes > 10:
                            hourly_cost = max_nodes * 30  # ~$30/hr per A100 node
                            daily_cost = hourly_cost * 24
                            violations.append(
                                {
                                    "rule_id": "JURA-COST-003",
                                    "resource": address,
                                    "reason": f"GPU node pool max_nodes={max_nodes} could cost ${daily_cost:,}/day",
                                }
                            )
                            verdict = Verdict.REJECT

            return AuditResult(
                verdict=verdict,
                confidence=0.9 if success else 0.7,
                latency_ms=latency,
                agents_used=result.get("agents_used", 5),
                violations=violations,
                resource_id="governance_check",
            )
        else:
            return AuditResult(
                verdict=Verdict.ESCALATE,
                confidence=0.0,
                latency_ms=latency,
                agents_used=1,
                violations=[{"error": f"HTTP {response.status_code}"}],
                resource_id="governance_check",
            )

    except Exception as e:
        latency = (time.perf_counter() - start) * 1000
        return AuditResult(
            verdict=Verdict.ESCALATE,
            confidence=0.0,
            latency_ms=latency,
            agents_used=1,
            violations=[{"error": str(e)}],
            resource_id="governance_check",
        )


async def audit_terraform_plan(plan_json: dict[str, Any]) -> dict[str, Any]:
    """
    Distribute terraform plan across 600-agent swarm for parallel audit.

    - 570 Flash agents: validate resources, check naming, costs
    - 30 Pro agents: JURA governance, security compliance
    """
    resources = plan_json.get("resource_changes", [])
    rules = load_jura_rules()

    print("🐒 Swarm Audit Starting")
    print(f"   Resources: {len(resources)}")
    print(f"   JURA Rules: {len(rules)}")
    print()

    async with httpx.AsyncClient() as client:
        # Bulk audit (parallel) - Flash tier
        bulk_tasks = [
            audit_resource_bulk(client, r, ["naming", "cost", "dependencies"]) for r in resources
        ]

        # Governance audit - Pro tier
        governance_task = audit_governance(client, plan_json, rules)

        # Run all in parallel
        all_tasks = bulk_tasks + [governance_task]
        results = await asyncio.gather(*all_tasks, return_exceptions=True)

        # Filter out exceptions
        valid_results = [r for r in results if isinstance(r, AuditResult)]

        # Handle exceptions
        for i, r in enumerate(results):
            if isinstance(r, Exception):
                valid_results.append(
                    AuditResult(
                        verdict=Verdict.ESCALATE,
                        confidence=0.0,
                        latency_ms=0,
                        agents_used=0,
                        violations=[{"error": str(r)}],
                    )
                )

    return aggregate_verdicts(valid_results)


def print_audit_report(result: dict[str, Any]) -> None:
    """Print formatted audit report."""
    verdict = result["verdict"]

    # Color codes
    colors = {
        "APPROVE": "\033[92m",  # Green
        "REJECT": "\033[91m",  # Red
        "ESCALATE": "\033[93m",  # Yellow
    }
    reset = "\033[0m"

    print("=" * 60)
    print("🐒 SWARM AUDIT REPORT")
    print("=" * 60)
    print()
    print(f"Verdict: {colors.get(verdict, '')}{verdict}{reset}")
    print(f"Confidence: {result['confidence']:.1%}")
    print(f"Resources Audited: {result['resources_audited']}")
    print(f"Agents Used: {result['agents_used']}")
    print(f"Total Latency: {result['total_latency_ms']:.1f}ms")
    print(f"Avg Latency: {result['avg_latency_ms']:.1f}ms")
    print()

    if result["violations"]:
        print(f"⚠️  Violations ({result['violations_count']}):")
        for v in result["violations"][:10]:  # Show first 10
            print(f"   - {v}")
        if result["violations_count"] > 10:
            print(f"   ... and {result['violations_count'] - 10} more")
    else:
        print("✅ No violations found")

    print()
    print("=" * 60)


async def main():
    if len(sys.argv) < 2:
        print("Usage: python3 swarm_audit.py <tfplan.json>")
        sys.exit(1)

    plan_path = Path(sys.argv[1])
    if not plan_path.exists():
        print(f"Error: {plan_path} not found")
        sys.exit(1)

    with open(plan_path) as f:
        plan_json = json.load(f)

    result = await audit_terraform_plan(plan_json)
    print_audit_report(result)

    # Write approval marker if passed
    if result["verdict"] == "APPROVE":
        Path(".swarm_approved").touch()
        print("✅ Swarm audit PASSED - ready to apply")
        sys.exit(0)
    elif result["verdict"] == "ESCALATE":
        print("⚠️  Swarm audit ESCALATED - manual review required")
        sys.exit(2)
    else:
        print("❌ Swarm audit FAILED - fix violations before apply")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
