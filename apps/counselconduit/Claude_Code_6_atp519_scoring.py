# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

# Judge 6 — ATP 5-19 Risk Scoring Template
# ==========================================
# Stable process skeleton beneath Judge 6 enforcement.
# Every risk decision MUST be scored through this 7-step framework.
# Reference: U.S. Army ATP 5-19, Composite Risk Management
#
# Usage:
#   Each CounselConduit API decision that touches privilege, billing,
#   model routing, or data retention MUST complete all 7 steps.

## Step 1: Identify Hazards
# What could go wrong? What are the threat vectors?
# - Prompt injection via user input
# - Privilege boundary violation
# - Data exfiltration via model output
# - Billing fraud via session manipulation
# - GDPR violation via retention failure

## Step 2: Assess Hazards (Severity × Probability)
# | Severity | Probability | Risk Level |
# |----------|-------------|------------|
# | Catastrophic | Frequent | EXTREMELY HIGH |
# | Critical | Likely | HIGH |
# | Moderate | Occasional | MEDIUM |
# | Negligible | Unlikely | LOW |

## Step 3: Develop Controls
# For each hazard, define a specific control:
# - Input validation (Zod/Pydantic schema)
# - Rate limiting (per-user, per-endpoint)
# - Kovel attestation (cryptographic hash)
# - Judge 6 policy gate (mandatory)
# - Token budget cap (per-session)
# - Audit log (structured, no PII)

## Step 4: Make Risk Decisions
# Authority levels:
# - LOW risk: Developer can accept
# - MEDIUM risk: Tech Lead review required
# - HIGH risk: CTO (Founder) approval required
# - EXTREMELY HIGH risk: BLOCK — do not proceed

## Step 5: Implement Controls
# Controls are NOT advisory — they are code:
# - `Claude_Code_6.evaluate()` on every model routing decision
# - `prompt_guard.scan()` on every user input
# - `kovel_attestation.generate()` on every privileged session
# - `stripe_handler.verify_webhook()` on every payment event

## Step 6: Supervise and Evaluate
# Continuous monitoring:
# - Cloud Monitoring alert policies (7 active)
# - Error budget dashboard
# - Uptime checks (counselconduit + hosting targets)
# - Dream consolidation daemon (nightly KI review)
# - Loop steward daemon (5-min autonomous checks)

## Step 7: Assess Residual Risk
# After controls are implemented, re-score:
# - If residual risk > MEDIUM: escalate to Step 4
# - If residual risk <= LOW: document and proceed
# - Log to RISK_REGISTER.md with sequential risk number

# ─── Scoring Function ───────────────────────────────────────

SEVERITY_LEVELS = {
    "catastrophic": 4,  # Loss of privilege, data breach, legal liability
    "critical": 3,  # Service outage, billing error, compliance gap
    "moderate": 2,  # Degraded service, minor data inconsistency
    "negligible": 1,  # Cosmetic, logging gap, non-functional
}

PROBABILITY_LEVELS = {
    "frequent": 4,  # Happens on most requests
    "likely": 3,  # Happens weekly
    "occasional": 2,  # Happens monthly
    "unlikely": 1,  # Rare edge case
}

RISK_MATRIX = {
    (4, 4): "EXTREMELY_HIGH",
    (4, 3): "EXTREMELY_HIGH",
    (4, 2): "HIGH",
    (4, 1): "HIGH",
    (3, 4): "EXTREMELY_HIGH",
    (3, 3): "HIGH",
    (3, 2): "HIGH",
    (3, 1): "MEDIUM",
    (2, 4): "HIGH",
    (2, 3): "MEDIUM",
    (2, 2): "MEDIUM",
    (2, 1): "LOW",
    (1, 4): "MEDIUM",
    (1, 3): "LOW",
    (1, 2): "LOW",
    (1, 1): "LOW",
}


def score_risk(severity: str, probability: str) -> dict:
    """Score a risk using the ATP 5-19 matrix.

    Args:
        severity: One of 'catastrophic', 'critical', 'moderate', 'negligible'
        probability: One of 'frequent', 'likely', 'occasional', 'unlikely'

    Returns:
        dict with risk_level, severity_score, probability_score, action
    """
    sev = SEVERITY_LEVELS.get(severity.lower(), 0)
    prob = PROBABILITY_LEVELS.get(probability.lower(), 0)

    if sev == 0 or prob == 0:
        return {"error": f"Invalid severity '{severity}' or probability '{probability}'"}

    level = RISK_MATRIX.get((sev, prob), "UNKNOWN")

    actions = {
        "EXTREMELY_HIGH": "BLOCK — do not proceed. CTO approval + full mitigation required.",
        "HIGH": "CTO review required. Implement all controls before proceeding.",
        "MEDIUM": "Tech Lead review. Implement primary controls.",
        "LOW": "Developer can accept. Document and proceed.",
    }

    return {
        "risk_level": level,
        "severity": severity,
        "severity_score": sev,
        "probability": probability,
        "probability_score": prob,
        "action": actions.get(level, "UNKNOWN"),
    }


if __name__ == "__main__":
    # Example: Prompt injection on model routing
    result = score_risk("critical", "likely")
    print(f"Risk: {result['risk_level']} — {result['action']}")

    # Example: Cosmetic UI bug
    result = score_risk("negligible", "unlikely")
    print(f"Risk: {result['risk_level']} — {result['action']}")
