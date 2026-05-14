# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Semantic Compression for Audit Trails
Compress rich context into compact, human-readable semantic summaries
Target: 10:1 compression ratio while preserving decision-critical information
"""

import hashlib
import json
from typing import Any
from datetime import datetime, timezone


def compress_audit_trail(
    action_type: str, context: dict[str, Any], decision: str, risk_level: str, approval_required: bool, approval_authority: str = None
) -> str:
    """
    Compress audit context into semantic summary

    Examples:
        - "50K_wire→new_vendor→no_PO→high_risk→CFO_gate"
        - "contract_review→$2M→3yr_term→legal_approved→ALLOW"
        - "fraud_flag→card_4532→geo_mismatch→BLOCK"

    Args:
        action_type: Type of action being evaluated
        context: Full context dictionary
        decision: ALLOW or BLOCK
        risk_level: Risk level (EH/H/M/L)
        approval_required: Whether approval is required
        approval_authority: Required approval authority

    Returns:
        Compact semantic summary string
    """
    components = []

    # Add action type (abbreviated)
    components.append(_abbreviate_action(action_type))

    # Extract and compress key context elements
    if "amount_usd" in context or "amount" in context:
        amount = context.get("amount_usd") or context.get("amount")
        components.append(_format_amount(amount))

    if "vendor" in context or "vendor_id" in context or "vendor_status" in context:
        vendor_status = context.get("vendor_status", "unknown")
        components.append(f"{vendor_status}_vendor")

    if "purchase_order" in context or "po_number" in context:
        po = context.get("purchase_order") or context.get("po_number")
        if po:
            components.append(f"PO_{po}")
        else:
            components.append("no_PO")

    if "contract_value" in context:
        components.append(_format_amount(context["contract_value"]))

    if "duration" in context or "term_months" in context:
        duration = context.get("duration") or context.get("term_months")
        components.append(f"{duration}mo_term")

    if "case_type" in context:
        components.append(context["case_type"])

    if "compliance_area" in context:
        components.append(context["compliance_area"])

    if "fraud_score" in context:
        score = context["fraud_score"]
        if score > 0.8:
            components.append("fraud_high")
        elif score > 0.5:
            components.append("fraud_med")
        else:
            components.append("fraud_low")

    # Add risk level
    components.append(f"{risk_level}_risk")

    # Add approval gate
    if approval_required and approval_authority:
        components.append(f"{approval_authority.lower().replace(' ', '_')}_gate")
    else:
        components.append("auto_gate")

    # Add final decision
    components.append(decision)

    return "→".join(components)


def _abbreviate_action(action: str) -> str:
    """Abbreviate action types for compression"""
    abbrev = {
        "wire_transfer": "wire",
        "contract_approval": "contract",
        "legal_review": "legal",
        "fraud_check": "fraud",
        "payment_authorization": "payment",
        "vendor_onboarding": "vendor_onboard",
        "case_assessment": "case",
        "compliance_check": "compliance",
    }
    return abbrev.get(action.lower(), action[:10])


def _format_amount(amount: float) -> str:
    """Format monetary amounts for compression"""
    if amount >= 1_000_000:
        return f"${amount / 1_000_000:.1f}M"
    elif amount >= 1_000:
        return f"${amount / 1_000:.0f}K"
    else:
        return f"${amount:.0f}"


def decompress_audit_trail(semantic_summary: str) -> dict[str, Any]:
    """
    Decompress semantic summary back into structured data

    This is a best-effort reconstruction and won't recover all original data.
    Full context should be stored encrypted alongside the semantic summary.

    Args:
        semantic_summary: Compressed semantic string

    Returns:
        Dictionary of extracted components
    """
    components = semantic_summary.split("→")

    result = {
        "action": components[0] if components else "unknown",
        "components": components,
        "decision": components[-1] if components else "unknown",
    }

    # Extract known patterns
    for component in components:
        if "_risk" in component:
            result["risk_level"] = component.replace("_risk", "")
        elif "_gate" in component:
            result["approval_gate"] = component.replace("_gate", "")
        elif component.startswith("$"):
            result["amount"] = component
        elif component.startswith("PO_"):
            result["purchase_order"] = component.replace("PO_", "")
        elif "vendor" in component:
            result["vendor_status"] = component.replace("_vendor", "")
        elif "fraud_" in component:
            result["fraud_level"] = component.replace("fraud_", "")

    return result


def generate_trail_id(judge_type: str, request_id: str, timestamp: datetime = None) -> str:
    """
    Generate unique trail ID

    Format: trail_YYYYMMDD_type_hash

    Args:
        judge_type: Judge vertical type
        request_id: Original request ID
        timestamp: Trail timestamp (default: now)

    Returns:
        Unique trail ID
    """
    if timestamp is None:
        timestamp = datetime.now(timezone.utc)

    date_str = timestamp.strftime("%Y%m%d")
    type_abbrev = judge_type[:4].lower()

    # Generate short hash from request_id
    hash_bytes = hashlib.sha256(request_id.encode()).digest()
    short_hash = hash_bytes[:4].hex()

    return f"trail_{date_str}_{type_abbrev}_{short_hash}"


def calculate_compression_ratio(original_context: dict[str, Any], semantic_summary: str) -> float:
    """
    Calculate compression ratio

    Args:
        original_context: Full context dictionary
        semantic_summary: Compressed semantic summary

    Returns:
        Compression ratio (original_size / compressed_size)
    """
    original_size = len(json.dumps(original_context))
    compressed_size = len(semantic_summary)

    if compressed_size == 0:
        return 0.0

    return original_size / compressed_size


def validate_semantic_trail(semantic_summary: str) -> bool:
    """
    Validate semantic trail format

    Args:
        semantic_summary: Semantic summary to validate

    Returns:
        True if valid format
    """
    if not semantic_summary:
        return False

    components = semantic_summary.split("→")

    # Must have at least: action → risk → decision
    if len(components) < 3:
        return False

    # Last component should be ALLOW or BLOCK
    if components[-1] not in ["ALLOW", "BLOCK"]:
        return False

    # Should have a risk indicator
    has_risk = any("_risk" in c for c in components)
    if not has_risk:
        return False

    return True


__all__ = [
    "compress_audit_trail",
    "decompress_audit_trail",
    "generate_trail_id",
    "calculate_compression_ratio",
    "validate_semantic_trail",
]
