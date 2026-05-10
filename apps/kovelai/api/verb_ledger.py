"""
Verb Ledger — Action Verb Data Models (Firestore-backed).

Pydantic models for the kinematic action verb analysis pipeline.
These models define the schema for Firestore's `verb_ledger` collection
and provide validation/serialization for the War Room Stage 3 output.

Firestore Collection: verb_ledger
Security: Attorney Work-Product — never exposed to clients.

@see WAR_ROOM_ARCHITECTURE.md — Pipeline architecture
@see legal-prompts.ts — VERB_AUDITOR_PROMPT
"""

from __future__ import annotations

import enum
from datetime import datetime


from pydantic import BaseModel, Field, field_validator

# ═══════════════════════════════════════════════════════════
# Kinematic Classification Taxonomy
# ═══════════════════════════════════════════════════════════


class KinematicClassification(enum.StrEnum):
  """Legal-linguistic verb classification categories."""

  CONTACT_FORCE = "CONTACT_FORCE"
  MOTION_VIOLATION = "MOTION_VIOLATION"
  KNOWLEDGE_STATE = "KNOWLEDGE_STATE"
  PROMISE_CONTRACT = "PROMISE_CONTRACT"
  EMPLOYMENT_ACTION = "EMPLOYMENT_ACTION"
  SPEECH_ACT = "SPEECH_ACT"
  EVIDENCE_ACTION = "EVIDENCE_ACTION"
  DOCUMENT_ACTION = "DOCUMENT_ACTION"


class VerbImpact(enum.StrEnum):
  """Whether the verb strengthens or weakens the client's case."""

  STRENGTHENS = "strengthens"
  WEAKENS = "weakens"
  NEUTRAL = "neutral"


# ═══════════════════════════════════════════════════════════
# Verb Entry
# ═══════════════════════════════════════════════════════════


class VerbEntry(BaseModel):
  """A single kinematic action verb extracted from client transcript."""

  verb: str = Field(
    ...,
    min_length=1,
    max_length=50,
    description="The exact action verb used by the client",
  )
  context: str = Field(
    ...,
    min_length=1,
    max_length=500,
    description="The full sentence containing the verb",
  )
  kinematic_classification: KinematicClassification = Field(
    ...,
    description="Verb classification category",
  )
  cause_of_action: str = Field(
    ...,
    min_length=1,
    max_length=200,
    description="The legal cause of action this verb maps to",
  )
  element_matched: str = Field(
    ...,
    min_length=1,
    max_length=300,
    description="Which legal element this verb satisfies",
  )
  confidence: float = Field(
    ...,
    ge=0.0,
    le=1.0,
    description="Confidence score (0.0-1.0) for the classification",
  )
  strengthens_or_weakens: VerbImpact = Field(
    ...,
    description="Whether this verb strengthens, weakens, or is neutral to the case",
  )

  @field_validator("confidence")
  @classmethod
  def round_confidence(cls, v: float) -> float:
    """Round confidence to 2 decimal places."""
    return round(v, 2)


# ═══════════════════════════════════════════════════════════
# Cause of Action Summary
# ═══════════════════════════════════════════════════════════


class CauseOfActionSummary(BaseModel):
  """Aggregated statistics for a single cause of action."""

  count: int = Field(..., ge=1, description="Number of verbs supporting this COA")
  avg_confidence: float = Field(
    ...,
    ge=0.0,
    le=1.0,
    description="Average confidence across all supporting verbs",
  )


# ═══════════════════════════════════════════════════════════
# Verb Ledger Document (Firestore schema)
# ═══════════════════════════════════════════════════════════


class VerbLedgerDocument(BaseModel):
  """
  Complete verb audit for a single Vent Mode session.

  This is the schema for the `verb_ledger` Firestore collection.
  Each document represents one session's complete verb analysis.
  """

  session_id: str = Field(
    ...,
    min_length=1,
    description="Unique session identifier",
  )
  firm_id: str = Field(
    ...,
    min_length=1,
    description="Law firm identifier (tenant scoped)",
  )
  timestamp: datetime = Field(
    default_factory=datetime.utcnow,
    description="When the analysis was performed (UTC)",
  )
  verbs: list[VerbEntry] = Field(
    default_factory=list,
    description="All extracted kinematic action verbs",
  )
  causes_of_action_summary: dict[str, CauseOfActionSummary] = Field(
    default_factory=dict,
    description="Aggregated cause-of-action statistics",
  )

  def compute_summary(self) -> None:
    """Recompute the causes_of_action_summary from the verb list."""
    raw: dict[str, dict[str, float]] = {}
    for verb in self.verbs:
      coa = verb.cause_of_action
      if coa not in raw:
        raw[coa] = {"total_conf": 0.0, "count": 0.0}
      raw[coa]["count"] += 1
      raw[coa]["total_conf"] += verb.confidence

    self.causes_of_action_summary = {
      coa: CauseOfActionSummary(
        count=int(data["count"]),
        avg_confidence=round(data["total_conf"] / data["count"], 2),
      )
      for coa, data in raw.items()
    }

  def to_firestore_dict(self) -> dict:
    """Serialize to a Firestore-compatible dictionary."""
    data = self.model_dump(mode="json")
    data["timestamp"] = self.timestamp.isoformat()
    return data


# ═══════════════════════════════════════════════════════════
# Citation Entry (Stage 5 output)
# ═══════════════════════════════════════════════════════════


class CitationType(enum.StrEnum):
  """Legal citation classification."""

  STATUTE = "statute"
  CASE = "case"
  REGULATION = "regulation"
  RULE = "rule"
  SECONDARY = "secondary"


class CitationStatus(enum.StrEnum):
  """Citation verification status."""

  VERIFIED = "verified"
  UNVERIFIED = "unverified"
  SUSPECT = "suspect"


class CitationEntry(BaseModel):
  """A single validated legal citation from the Oracle memo."""

  index: int = Field(..., ge=1, description="Citation index number")
  authority: str = Field(
    ...,
    min_length=1,
    description="Full legal authority citation (Bluebook format)",
  )
  type: CitationType = Field(..., description="Type of legal authority")
  citation_format_correct: bool = Field(
    ...,
    description="Whether the citation follows Bluebook format",
  )
  excerpt: str = Field(
    ...,
    description="Key language from the authority",
  )
  relevance_score: float = Field(
    ...,
    ge=0.0,
    le=1.0,
    description="Relevance score (0.0-1.0)",
  )
  status: CitationStatus = Field(
    ...,
    description="Verification status",
  )
  notes: str | None = Field(
    None,
    description="Additional notes or concerns about this citation",
  )


# ═══════════════════════════════════════════════════════════
# Kovel Billing Telemetry
# ═══════════════════════════════════════════════════════════


class KovelBillingTelemetry(BaseModel):
  """
  Billing telemetry for a War Room session.

  Firestore Collection: kovel_billing_telemetry
  NO CHAT TEXT IS STORED — only metadata and financial data.
  """

  firm_id: str
  session_id: str
  pipeline_type: str = "war_room"
  stages_completed: int = Field(..., ge=0, le=7)
  verb_count: int = Field(..., ge=0)
  citation_count: int = Field(..., ge=0)
  model_routed: str
  client_upfront_payment_cents: int = Field(..., ge=0)
  tokens_consumed: int = Field(..., ge=0)
  timestamp: datetime = Field(default_factory=datetime.utcnow)
