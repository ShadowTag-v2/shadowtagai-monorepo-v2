# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
# SPDX-License-Identifier: Proprietary
"""Judge 6 — ATP 5-19 Risk Scoring Module.

Canonical scoring engine for CounselConduit risk decisions.
Every risk decision touching privilege, billing, model routing,
or data retention MUST be scored through this framework.

Reference: U.S. Army ATP 5-19, Composite Risk Management
"""

from __future__ import annotations

# ── Severity Levels ─────────────────────────────────────────
SEVERITY_LEVELS: dict[str, int] = {
  "catastrophic": 4,  # Loss of privilege, data breach, legal liability
  "critical": 3,  # Service outage, billing error, compliance gap
  "moderate": 2,  # Degraded service, minor data inconsistency
  "negligible": 1,  # Cosmetic, logging gap, non-functional
}

# ── Probability Levels ──────────────────────────────────────
PROBABILITY_LEVELS: dict[str, int] = {
  "frequent": 4,  # Happens on most requests
  "likely": 3,  # Happens weekly
  "occasional": 2,  # Happens monthly
  "unlikely": 1,  # Rare edge case
}

# ── 4×4 Risk Matrix (severity_score, probability_score) → level
RISK_MATRIX: dict[tuple[int, int], str] = {
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

# ── Action Authority Map ────────────────────────────────────
_ACTIONS: dict[str, str] = {
  "EXTREMELY_HIGH": "BLOCK — do not proceed. CTO approval + full mitigation required.",
  "HIGH": "CTO review required. Implement all controls before proceeding.",
  "MEDIUM": "Tech Lead review. Implement primary controls.",
  "LOW": "Developer can accept. Document and proceed.",
}


def score_risk(severity: str, probability: str) -> dict:
  """Score a risk using the ATP 5-19 matrix.

  Args:
      severity: One of 'catastrophic', 'critical', 'moderate', 'negligible'
      probability: One of 'frequent', 'likely', 'occasional', 'unlikely'

  Returns:
      dict with risk_level, severity, severity_score, probability,
      probability_score, and action fields.  Returns an error dict
      if either input is invalid.
  """
  sev = SEVERITY_LEVELS.get(severity.lower(), 0)
  prob = PROBABILITY_LEVELS.get(probability.lower(), 0)

  if sev == 0 or prob == 0:
    return {"error": f"Invalid severity '{severity}' or probability '{probability}'"}

  level = RISK_MATRIX.get((sev, prob), "UNKNOWN")

  return {
    "risk_level": level,
    "severity": severity,
    "severity_score": sev,
    "probability": probability,
    "probability_score": prob,
    "action": _ACTIONS.get(level, "UNKNOWN"),
  }
