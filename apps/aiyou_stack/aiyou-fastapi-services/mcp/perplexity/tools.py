# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Perplexity MCP Tools - Standalone tool functions for MCP integration.

These functions can be registered directly with Claude Code's MCP system
or called programmatically from other services.
"""

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# Global manifest path
MANIFEST_PATH = Path("./logs/pnkln/perplexity/manifest.jsonl")


def governance_score(
    request_type: str,
    content: str,
    user_region: str | None = None,
    transaction_value: float | None = None,
) -> dict[str, Any]:
    """Judge 6 governance scoring for Perplexity requests.

    Args:
        request_type: Type of request (purchase, checkout, query, generate)
        content: Request content/query
        user_region: User's region (EU, US-CA, etc.)
        transaction_value: Transaction value in USD

    Returns:
        Dict with decision, risk_score, compliance_flags, reasoning

    """
    import time

    start_time = time.time()

    request_id = hashlib.sha256(f"{content}{time.time()}".encode()).hexdigest()[:16]
    user_context = {"region": user_region} if user_region else {}

    # Compliance domain checks
    compliance_domains = {
        "GDPR": ["eu", "europe", "gdpr", "consent", "pii", "delete"],
        "CCPA": ["california", "ccpa", "opt-out", "sell"],
        "PCI_DSS": ["payment", "card", "credit", "checkout", "paypal", "shopify"],
        "COPPA": ["child", "minor", "kids", "under13"],
        "HIPAA": ["health", "medical", "patient", "hipaa"],
    }

    combined_text = f"{content} {json.dumps(user_context)}".lower()
    compliance_flags = {
        domain: any(kw in combined_text for kw in keywords)
        for domain, keywords in compliance_domains.items()
    }

    # Calculate risk score
    base_risk = {"purchase": 30, "checkout": 40, "query": 10, "generate": 15, "delete": 50}.get(
        request_type.lower(),
        20,
    )

    if transaction_value and transaction_value > 1000:
        base_risk += 25
    elif transaction_value and transaction_value > 100:
        base_risk += 10

    for domain, active in compliance_flags.items():
        if active:
            weights = {"GDPR": 1.5, "CCPA": 1.2, "PCI_DSS": 2.0, "COPPA": 2.5, "HIPAA": 2.0}
            base_risk += int(10 * weights.get(domain, 1.0))

    risk_score = min(base_risk, 100)

    # Decision
    if risk_score <= 25:
        decision, reasoning = "APPROVE", "Low risk - auto-approved"
    elif risk_score <= 50:
        decision, reasoning = "APPROVE", "Medium risk - approved with monitoring"
    elif risk_score <= 75:
        decision, reasoning = "REVIEW", "High risk - requires human review"
    else:
        decision, reasoning = "DENY", "Critical risk - auto-denied"

    active_compliance = [k for k, v in compliance_flags.items() if v]
    if active_compliance:
        reasoning += f" | Compliance: {', '.join(active_compliance)}"

    latency_ms = (time.time() - start_time) * 1000

    return {
        "request_id": request_id,
        "decision": decision,
        "risk_score": risk_score,
        "compliance_flags": compliance_flags,
        "latency_ms": round(latency_ms, 2),
        "reasoning": reasoning,
    }


def watermark_content(
    content: str,
    source: str,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Apply SHADOWTAG cryptographic watermark to content.

    Args:
        content: Content to watermark
        source: Source identifier
        metadata: Additional metadata

    Returns:
        Dict with signature, merkle_root, timestamp

    """
    timestamp = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    full_metadata = {"source": source, "timestamp": timestamp, **(metadata or {})}

    message = json.dumps({"content": content, "metadata": full_metadata}, sort_keys=True)
    signature = f"shadowtag:{hashlib.sha256(message.encode()).hexdigest()}"
    merkle_root = f"sha256:{hashlib.sha256(f'{content}{timestamp}'.encode()).hexdigest()}"

    return {
        "content": content,
        "signature": signature,
        "merkle_root": merkle_root,
        "timestamp": timestamp,
        "metadata": full_metadata,
    }


def log_to_manifest(
    governance_result: dict[str, Any],
    watermark_result: dict[str, Any] | None = None,
    context_id: str = "perplexity_comet",
) -> str:
    """Log transaction to Apertus-compatible JSONL manifest.

    Args:
        governance_result: Result from governance_score
        watermark_result: Optional watermark result
        context_id: Context identifier

    Returns:
        Run ID for the logged entry

    """
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)

    run_id = governance_result.get(
        "request_id",
        hashlib.sha256(str(datetime.now()).encode()).hexdigest()[:16],
    )
    timestamp = datetime.now(UTC).isoformat().replace("+00:00", "Z")

    entry = {
        "run_id": run_id,
        "timestamp": timestamp,
        "context_id": context_id,
        "content": watermark_result.get("content", "") if watermark_result else "",
        "decision": governance_result.get("decision", ""),
        "risk_score": governance_result.get("risk_score", 0),
        "watermark_sig": watermark_result.get("signature", "") if watermark_result else "",
        "safety_scores": {
            "compliance_flags": governance_result.get("compliance_flags", {}),
            "risk_score": governance_result.get("risk_score", 0),
            "decision": governance_result.get("decision", ""),
        },
        "meta": {
            "latency_ms": governance_result.get("latency_ms", 0),
            "reasoning": governance_result.get("reasoning", ""),
            "merkle_root": watermark_result.get("merkle_root", "") if watermark_result else "",
            "source": "perplexity_mcp",
        },
    }

    with open(MANIFEST_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")

    return run_id


def search_manifest(
    query: str,
    context_id: str | None = None,
    decision: str | None = None,
    limit: int = 10,
) -> list[dict[str, Any]]:
    """Search the Apertus manifest for past governance decisions.

    Args:
        query: Search query (searches content and reasoning)
        context_id: Filter by context ID
        decision: Filter by decision (APPROVE, DENY, REVIEW)
        limit: Max results to return

    Returns:
        List of matching manifest entries

    """
    if not MANIFEST_PATH.exists():
        return []

    results = []
    query_lower = query.lower()

    with open(MANIFEST_PATH) as f:
        for line in f:
            try:
                entry = json.loads(line.strip())

                # Apply filters
                if context_id and entry.get("context_id") != context_id:
                    continue
                if decision and entry.get("decision") != decision:
                    continue

                # Search in content and reasoning
                content = entry.get("content", "").lower()
                reasoning = entry.get("meta", {}).get("reasoning", "").lower()

                if query_lower in content or query_lower in reasoning:
                    results.append(entry)

                if len(results) >= limit:
                    break

            except json.JSONDecodeError:
                continue

    return results


# MCP Tool Registration Helper
def get_mcp_tools() -> list[dict[str, Any]]:
    """Get MCP tool definitions for registration."""
    return [
        {
            "name": "perplexity_governance_score",
            "description": "Score a Perplexity request for compliance using Judge 6",
            "function": governance_score,
        },
        {
            "name": "perplexity_watermark",
            "description": "Apply SHADOWTAG watermark to AI content",
            "function": watermark_content,
        },
        {
            "name": "perplexity_log",
            "description": "Log transaction to Apertus manifest",
            "function": log_to_manifest,
        },
        {
            "name": "perplexity_search",
            "description": "Search past governance decisions",
            "function": search_manifest,
        },
    ]


if __name__ == "__main__":
    # Quick test
    print("Testing Perplexity MCP Tools\n")

    # Test governance
    result = governance_score(
        request_type="purchase",
        content="Buy MacBook Pro M3",
        user_region="EU",
        transaction_value=2499.00,
    )
    print(f"Governance: {result['decision']} (risk: {result['risk_score']})")

    # Test watermark
    wm = watermark_content(
        content="The MacBook Pro M3 offers excellent performance...",
        source="perplexity_comet",
    )
    print(f"Watermark: {wm['signature'][:40]}...")

    # Test logging
    run_id = log_to_manifest(result, wm)
    print(f"Logged: {run_id}")

    # Test search
    results = search_manifest("MacBook")
    print(f"Search results: {len(results)} found")
