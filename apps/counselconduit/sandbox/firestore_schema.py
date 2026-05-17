# apps/counselconduit/sandbox/firestore_schema.py
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Phase 3 Sandbox Session — Firestore Schema Definitions.

Defines the canonical Firestore document structure for sandbox sessions.
Collection: `firms/{firm_id}/sandbox_sessions/{session_id}`

Each sandbox session tracks:
- Tool execution requests from the LLM
- Attorney review state (pending/approved/rejected)
- Resource usage metrics
- Audit trail for compliance (Heppner S.D.N.Y. 2026)
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any


class SessionStatus(StrEnum):
  """Lifecycle states for a sandbox session."""

  CREATED = "created"
  EXECUTING = "executing"
  PENDING_REVIEW = "pending_review"
  APPROVED = "approved"
  REJECTED = "rejected"
  PARTIAL_APPROVED = "partial_approved"
  EXPIRED = "expired"
  ERROR = "error"


class TrustLevel(StrEnum):
  """Attorney trust levels for tool execution."""

  ZERO = "0"  # Full review required — default
  ONE = "1"  # Auto-approve known-safe tools
  TWO = "2"  # Enterprise custom policy


@dataclass
class ToolCallRecord:
  """Individual tool call within a sandbox session."""

  tool_name: str
  tool_args: dict[str, Any] = field(default_factory=dict)
  output: str = ""
  exit_code: int | None = None
  started_at: str = ""
  completed_at: str = ""
  duration_ms: int = 0
  resource_usage: dict[str, Any] = field(default_factory=dict)

  def to_firestore(self) -> dict[str, Any]:
    """Serialize to Firestore-compatible dict."""
    return asdict(self)


@dataclass
class SandboxSessionDoc:
  """Canonical Firestore document for a sandbox session.

  Collection path: `firms/{firm_id}/sandbox_sessions/{session_id}`
  """

  # Identity
  session_id: str = ""
  firm_id: str = ""
  matter_id: str = ""
  attorney_uid: str = ""

  # Execution context
  model_id: str = "gemini-3.1-flash-lite-preview-thinking"
  prompt_hash: str = ""
  trust_level: TrustLevel = TrustLevel.ZERO

  # State
  status: SessionStatus = SessionStatus.CREATED
  tool_calls: list[ToolCallRecord] = field(default_factory=list)

  # Review
  reviewer_uid: str = ""
  review_decision: str = ""
  review_notes: str = ""
  selected_files: list[str] = field(default_factory=list)

  # Timestamps (ISO 8601)
  created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
  updated_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
  expires_at: str = ""

  # Audit
  audit_log: list[dict[str, Any]] = field(default_factory=list)

  # Resource tracking
  total_cpu_ms: int = 0
  total_memory_mb_peak: int = 0
  total_wall_clock_ms: int = 0

  def to_firestore(self) -> dict[str, Any]:
    """Serialize to Firestore-compatible dict."""
    data = asdict(self)
    data["tool_calls"] = [tc.to_firestore() for tc in self.tool_calls]
    return data

  @classmethod
  def from_firestore(cls, data: dict[str, Any]) -> SandboxSessionDoc:
    """Deserialize from Firestore document."""
    tool_calls_raw = data.pop("tool_calls", [])
    tool_calls = [ToolCallRecord(**tc) for tc in tool_calls_raw]
    return cls(**data, tool_calls=tool_calls)

  def add_audit_entry(self, action: str, actor: str, details: str = "") -> None:
    """Append an audit log entry."""
    self.audit_log.append(
      {
        "action": action,
        "actor": actor,
        "details": details,
        "timestamp": datetime.now(UTC).isoformat(),
      }
    )
    self.updated_at = datetime.now(UTC).isoformat()

  def transition_to(self, new_status: SessionStatus, actor: str = "system") -> None:
    """Transition session status with audit trail."""
    old_status = self.status
    self.status = new_status
    self.add_audit_entry(
      action=f"status_transition:{old_status}→{new_status}",
      actor=actor,
    )


# Firestore Security Rules (reference — deploy via firebase_init)
FIRESTORE_RULES_SNIPPET = """
// Sandbox sessions — scoped to firm
match /firms/{firmId}/sandbox_sessions/{sessionId} {
  allow read: if request.auth != null
    && request.auth.token.firm_id == firmId;
  allow create: if request.auth != null
    && request.auth.token.firm_id == firmId
    && request.auth.token.role in ['attorney', 'admin'];
  allow update: if request.auth != null
    && request.auth.token.firm_id == firmId
    && request.auth.token.role in ['attorney', 'admin']
    && request.resource.data.status in ['pending_review', 'approved', 'rejected', 'partial_approved'];
  allow delete: if false;  // Soft-delete only
}
"""
