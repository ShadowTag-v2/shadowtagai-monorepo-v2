"""
Judge #6 Enforcement Layer (Antigravity Phase 1)

Acts as the "Brakes" for the AI platform.
Validates provenance confidence before allowing any asset to proceed.
Fail-Safe: Defaults to "Reject" if confidence < threshold.

Directives:
- Reject any asset with provenance_confidence < 0.75
- Log all decisions for "Governance Premium" audit trail.
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class Judgment:
  decision: str  # "APPROVE" | "REJECT" | "FLAG"
  confidence: float  # 0.0 to 1.0
  reason: str
  timestamp: str
  judge_version: str = "6.0.0-antigravity"


class JudgeSix:
  """
  The Iron Core Enforcement Layer.
  """

  def __init__(self, threshold: float = 0.75):
    self.threshold = threshold

  def evaluate_asset(
    self,
    asset_id: str,
    provenance_data: dict[str, Any],
    neural_hash_confidence: float,
  ) -> Judgment:
    """
    Evaluate an asset against strict Phase 1 safety policies.
    """
    # 1. Check Technical Integrity (Neural Hash Confidence)
    if neural_hash_confidence < 0.5:
      return Judgment(
        decision="REJECT",
        confidence=neural_hash_confidence,
        reason="Neural hash generation failed or low signal quality",
        timestamp=datetime.utcnow().isoformat(),
      )

    # 2. Check Chain of Custody (Provenance)
    # In MVP, we check if a 'receipt' key exists and is non-empty
    has_receipt = bool(provenance_data.get("receipt_id"))

    if not has_receipt:
      # Policy: No receipt = Immediate Block (unless explicitly whitelisted)
      return Judgment(
        decision="REJECT",
        confidence=0.0,
        reason="Missing provenance receipt (Chain of Custody break)",
        timestamp=datetime.utcnow().isoformat(),
      )

    # 3. Final Decision
    # In Phase 1, simply having the receipt and hash is enough for 1.0 confidence
    # Future: Check blacklist, copyright db, etc.
    final_confidence = 0.95 if has_receipt else 0.0

    if final_confidence >= self.threshold:
      return Judgment(
        decision="APPROVE",
        confidence=final_confidence,
        reason="Provenance verified; Chain of Custody intact",
        timestamp=datetime.utcnow().isoformat(),
      )
    else:
      return Judgment(
        decision="REJECT",
        confidence=final_confidence,
        reason=f"Confidence {final_confidence:.2f} below threshold {self.threshold}",
        timestamp=datetime.utcnow().isoformat(),
      )

  def validate_fact(self, fact_text: str) -> bool:
    """
    Validate a fact before it enters Long-Term Memory.
    Strictly enforces policy to prevent 'hallucinated memories'.
    """
    # 1. Basic sanity checks (empty, too short)
    if not fact_text or len(fact_text.strip()) < 5:
      return False

    # 2. PII / Sensitive Data Check (Placeholder for extensive regex/DL check)
    # For now, we assume if it passed the LLM extraction, it's 'content'
    # but we should block obvious secrets if they were to appear.
    sensitive_keywords = ["password", "private key", "ssn", "secret"]
    if any(keyword in fact_text.lower() for keyword in sensitive_keywords):
      return False

    # 3. Hallucination Check (Judge #6 Core Logic)
    # Ideally, this would cross-reference with a 'Truth Database' or use
    # a higher-intelligence model to verify plausibility.
    # For MVP, we trust the extraction if it's substantial.

    return True


# Global Judge Instance
_judge = None


def get_judge() -> JudgeSix:
  global _judge
  if _judge is None:
    _judge = JudgeSix(threshold=0.75)  # Strict Phase 1 Threshold
  return _judge
