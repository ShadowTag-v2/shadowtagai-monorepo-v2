# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

# apps/counselconduit/api/Cor_Claude_Code_6.py
"""Judge 6: Python-First Governance Pipeline.

MVP implementation of the deterministic governance interceptor.
Implements the ATP 5-19 Risk Matrix for all AI outputs.

Pipeline steps (sequential, immutable order):
    1. EXTRACT  → Parse AI output for actionable claims
    2. SCORE    → Risk-score each claim (1-25, ATP 5-19)
    3. GATE     → Block outputs above threshold
    4. ENFORCE  → Apply corrections or require human review

Risk Matrix (ATP 5-19):
    Severity (1-5) × Probability (1-5) = Risk Score (1-25)

    GREEN  (1-9):   Approved automatically
    AMBER  (10-15): Approved with warning flags
    RED    (16-25): BLOCKED — requires human attorney review

NOTE: This is the Python-first MVP. When enterprise clients demand
compiled governance binaries, port to .NET Semantic Kernel Process
Framework (step nodes: Extract→Score→Gate→Enforce).
"""

from __future__ import annotations

import logging
import re
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger("counselconduit.Cor_Claude_Code_6")


class RiskLevel(Enum):
  """ATP 5-19 risk classification."""

  GREEN = "green"  # Auto-approved
  AMBER = "amber"  # Approved with warnings
  RED = "red"  # Blocked


@dataclass
class RiskAssessment:
  """Result of Judge 6 risk evaluation."""

  risk_score: int  # 1-25
  risk_level: RiskLevel
  approved: bool
  flags: list[str] = field(default_factory=list)
  blocked_reason: str = ""
  assessed_at: float = field(default_factory=time.time)


@dataclass
class GovernanceResult:
  """Full governance pipeline output."""

  input_text: str
  output_text: str  # May be modified by enforcement
  assessment: RiskAssessment
  pipeline_ms: int = 0


# ── Risk Patterns ──────────────────────────────────────────────────────────

# Patterns that indicate HIGH risk in legal AI outputs
_HIGH_RISK_PATTERNS: list[tuple[str, str, int]] = [
  (r"\b(guarantee|guaranteed|certainly will)\b", "Absolute guarantee language", 20),
  (r"\b(malpractice|negligence|liable for)\b", "Malpractice risk language", 18),
  (r"\b(not legal advice|disclaimer)\b", "Missing privilege assertion", 5),
  (r"\b(confidential|privileged)\b", "Contains privilege markers (OK)", 2),
  (r"\b(hack|exploit|bypass|circumvent)\b", "Adversarial language detected", 22),
  (r"\b(always|never|impossible|certainly)\b", "Absolute certainty language", 12),
  (r"\bI am (a|an) (lawyer|attorney)\b", "AI impersonating attorney", 25),
  (r"\b(sue|file suit|litigate)\b", "Litigation advice detected", 10),
  (r"\b(HIPAA|GDPR|SOX|FERPA)\b", "Regulatory compliance reference", 8),
]

# Patterns that MUST be present in legal AI output
_REQUIRED_PATTERNS: list[tuple[str, str]] = [
  # No hard requirements for MVP — add as case law evolves
]


# ── Pipeline Steps ─────────────────────────────────────────────────────────


def _step_extract(text: str) -> list[dict[str, Any]]:
  """Step 1: EXTRACT — Parse output for risk-relevant claims."""
  claims = []
  for pattern, label, base_score in _HIGH_RISK_PATTERNS:
    matches = re.findall(pattern, text, re.IGNORECASE)
    if matches:
      claims.append(
        {
          "pattern": label,
          "match_count": len(matches),
          "base_score": base_score,
        }
      )
  return claims


def _step_score(claims: list[dict[str, Any]]) -> tuple[int, list[str]]:
  """Step 2: SCORE — Compute aggregate risk score.

  Uses the highest individual claim score (not sum) because
  a single critical risk should trigger blocking regardless
  of how many safe items exist.
  """
  if not claims:
    return 1, []

  max_score = max(c["base_score"] for c in claims)
  flags = [
    f"{c['pattern']} (score={c['base_score']}, matches={c['match_count']})"
    for c in claims
    if c["base_score"] >= 10
  ]

  return min(max_score, 25), flags


def _step_gate(risk_score: int) -> tuple[RiskLevel, bool, str]:
  """Step 3: GATE — Apply risk threshold."""
  if risk_score <= 9:
    return RiskLevel.GREEN, True, ""
  elif risk_score <= 15:
    return RiskLevel.AMBER, True, ""
  else:
    return (
      RiskLevel.RED,
      False,
      f"Risk score {risk_score} exceeds threshold (15). Requires attorney review.",
    )


def _step_enforce(text: str, risk_level: RiskLevel) -> str:
  """Step 4: ENFORCE — Apply corrections to output.

  For AMBER: Append warning disclosure.
  For RED: Replace with blocked message.
  """
  if risk_level == RiskLevel.GREEN:
    return text

  if risk_level == RiskLevel.AMBER:
    disclaimer = (
      "\n\n---\n⚠️ *This response contains language flagged by the "
      "governance pipeline. Attorney review is recommended before "
      "relying on this analysis.*"
    )
    return text + disclaimer

  # RED — blocked
  return (
    "⛔ This response has been blocked by the Judge 6 governance pipeline. "
    "The AI output contained language that exceeds the ATP 5-19 risk threshold. "
    "Please review the flagged items and consult directly with your attorney."
  )


# ── Main Pipeline ──────────────────────────────────────────────────────────


def evaluate(text: str) -> GovernanceResult:
  """Run the full Judge 6 governance pipeline on AI output.

  This is the main entry point. Call after every Gemini response
  before returning to the client.
  """
  start = time.monotonic()

  # Step 1: Extract
  claims = _step_extract(text)

  # Step 2: Score
  risk_score, flags = _step_score(claims)

  # Step 3: Gate
  risk_level, approved, blocked_reason = _step_gate(risk_score)

  # Step 4: Enforce
  output_text = _step_enforce(text, risk_level)

  elapsed_ms = int((time.monotonic() - start) * 1000)

  assessment = RiskAssessment(
    risk_score=risk_score,
    risk_level=risk_level,
    approved=approved,
    flags=flags,
    blocked_reason=blocked_reason,
  )

  result = GovernanceResult(
    input_text=text,
    output_text=output_text,
    assessment=assessment,
    pipeline_ms=elapsed_ms,
  )

  logger.info(
    "Judge 6 evaluation: score=%d level=%s approved=%s flags=%d",
    risk_score,
    risk_level.value,
    approved,
    len(flags),
  )

  return result
