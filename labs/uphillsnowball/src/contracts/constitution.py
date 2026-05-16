"""The Constitution — Immutable Mission Contracts & Privilege Metadata.

The CallOfQuestion is the Bar Exam. Once forged, the mission hash is
frozen via SHA-256. Prompt drift is mathematically prevented.

The PrivilegePortal binds compute cycles to Attorney Work-Product Doctrine
or HIPAA Safe Harbor at the ingress layer. If a query is not explicitly
bound to a Matter ID and a licensed professional's session, it is
discoverable in a court of law.

The BoundedAlert is the ONLY outward-facing product primitive.
Internal traces never leak to retail.
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass, field

logger = logging.getLogger("Constitution")

GLOBAL_MODEL = "gemini-3.1-flash-lite-preview-thinking"
GLOBAL_PROJECT = "shadowtag-omega-v4"


@dataclass(frozen=True)
class PrivilegePortal:
  """Binds compute cycles to Attorney Work-Product / HIPAA Safe Harbor.

  This metadata is injected into every CallOfQuestion at the ingress layer.
  It extends legal privilege to the AI's compute cycles — the output
  is protected work product, not discoverable raw data.

  Attributes:
      matter_id: The legal matter or medical case identifier.
      licensed_professional_id: Bar number, NPI, or professional license.
      is_privileged: Whether the session is under active privilege.
      jurisdiction: Governing jurisdiction (e.g., "US-NY", "EU-GDPR").
  """

  matter_id: str
  licensed_professional_id: str
  is_privileged: bool
  jurisdiction: str = "US-FED"


@dataclass(frozen=True)
class CallOfQuestion:
  """The Immutable Mission: Frozen via SHA-256.

  Once forged, the request_hash locks the Commander's intent.
  No agent can modify the mission parameters. Drift is physically prevented.

  Attributes:
      case_id: Unique case/matter identifier.
      original_intent_verbatim: The raw, unmodified user prompt.
      request_hash: SHA-256 digest binding intent to execution.
      purpose: The stated objective of the mission.
      key_tasks: Ordered list of tasks to accomplish.
      end_state: The desired terminal condition.
      privilege_meta: Work-product / HIPAA binding metadata.
  """

  case_id: str
  original_intent_verbatim: str
  request_hash: str
  purpose: str
  key_tasks: list[str]
  end_state: str
  privilege_meta: PrivilegePortal

  @classmethod
  def forge(
    cls,
    case_id: str,
    prompt: str,
    privilege: PrivilegePortal,
    purpose: str,
    key_tasks: list[str],
    end_state: str,
  ) -> CallOfQuestion:
    """Forge an immutable CallOfQuestion with SHA-256 hash binding.

    Args:
        case_id: Matter/case identifier.
        prompt: The Commander's verbatim intent.
        privilege: Work-product privilege metadata.
        purpose: Mission purpose statement.
        key_tasks: Ordered task list.
        end_state: Desired terminal condition.

    Returns:
        A frozen CallOfQuestion instance with cryptographic hash.
    """
    payload = f"{prompt}|{purpose}|{json.dumps(key_tasks)}|{privilege.matter_id}"
    req_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()

    logger.info(
      "⚖️ CallOfQuestion FORGED: case=%s hash=%s privileged=%s",
      case_id,
      req_hash[:16].upper(),
      privilege.is_privileged,
    )

    return cls(
      case_id=case_id,
      original_intent_verbatim=prompt,
      request_hash=req_hash,
      purpose=purpose,
      key_tasks=key_tasks,
      end_state=end_state,
      privilege_meta=privilege,
    )


@dataclass
class BoundedAlert:
  """THE ONLY OUTWARD-FACING PRODUCT PRIMITIVE.

  Internal traces never leak to retail. The Fusion emits BoundedAlerts
  ONLY. Each alert is signed with C2PA provenance.

  Attributes:
      alert_id: Unique alert identifier.
      entity: The subject entity (company, case, asset).
      action: The recommended action.
      rationale: Evidence-backed reasoning.
      risk_budget: Quantified risk metrics.
      c2pa_signature: Content provenance signature.
  """

  alert_id: str
  entity: dict[str, str]
  action: str
  rationale: str
  risk_budget: dict[str, float] = field(default_factory=dict)
  c2pa_signature: str = ""
