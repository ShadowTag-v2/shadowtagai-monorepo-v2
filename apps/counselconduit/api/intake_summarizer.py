# apps/counselconduit/api/intake_summarizer.py
"""Intake Summary Extraction Model for Vent Mode.

After a Vent Mode session ends, this module analyzes the full transcript
to extract a structured legal intake summary. The summary is saved as
a "matter brief" for the attorney's review.

Uses litellm for model routing with prompt repetition for accuracy.
Outputs: key facts, legal issues, emotional state, urgency, suggested actions.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger("counselconduit.intake_summarizer")


class Urgency(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class EmotionalState(str, Enum):
    CALM = "calm"
    ANXIOUS = "anxious"
    FRUSTRATED = "frustrated"
    DISTRESSED = "distressed"
    ANGRY = "angry"


@dataclass
class IntakeSummary:
    """Structured legal intake summary extracted from Vent Mode transcript."""

    session_id: str
    client_name: str = ""
    key_facts: list[str] = field(default_factory=list)
    legal_issues: list[str] = field(default_factory=list)
    opposing_parties: list[str] = field(default_factory=list)
    emotional_state: EmotionalState = EmotionalState.CALM
    urgency: Urgency = Urgency.MODERATE
    suggested_actions: list[str] = field(default_factory=list)
    potential_claims: list[str] = field(default_factory=list)
    jurisdiction_hints: list[str] = field(default_factory=list)
    raw_summary: str = ""
    confidence: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "client_name": self.client_name,
            "key_facts": self.key_facts,
            "legal_issues": self.legal_issues,
            "opposing_parties": self.opposing_parties,
            "emotional_state": self.emotional_state.value,
            "urgency": self.urgency.value,
            "suggested_actions": self.suggested_actions,
            "potential_claims": self.potential_claims,
            "jurisdiction_hints": self.jurisdiction_hints,
            "raw_summary": self.raw_summary,
            "confidence": self.confidence,
        }


# ── System Prompts (structurally isolated from user input — OWASP LLM01) ──


_EXTRACTION_SYSTEM_PROMPT = """You are a legal intake analyst. Your role is to review a confidential client conversation transcript and extract a structured intake summary for the supervising attorney.

IMPORTANT RULES:
1. Extract ONLY what the client explicitly stated. Do not infer or fabricate facts.
2. Flag uncertainty with hedging language ("client mentioned", "appears to involve").
3. Identify all legal issues, even tangential ones.
4. Assess emotional state based on language intensity, not topic sensitivity.
5. Rate urgency based on statute of limitations, imminent deadlines, or safety concerns.
6. Output VALID JSON matching the specified schema.

OUTPUT SCHEMA:
{
  "client_name": "string or empty if not mentioned",
  "key_facts": ["fact1", "fact2", ...],
  "legal_issues": ["issue1", "issue2", ...],
  "opposing_parties": ["party1", ...],
  "emotional_state": "calm|anxious|frustrated|distressed|angry",
  "urgency": "low|moderate|high|critical",
  "suggested_actions": ["action1", "action2", ...],
  "potential_claims": ["claim1", ...],
  "jurisdiction_hints": ["state or court hints", ...],
  "raw_summary": "2-3 sentence plain language summary",
  "confidence": 0.0-1.0
}"""


async def extract_intake_summary(
    session_id: str,
    transcript: list[dict[str, str]],
    model_override: str | None = None,
) -> IntakeSummary:
    """Extract a structured intake summary from a Vent Mode transcript.

    Args:
        session_id: The Vent Mode session ID.
        transcript: List of {"role": "client"|"ai", "content": "..."} messages.
        model_override: Optional model ID. Defaults to gemini-2.0-flash-lite.

    Returns:
        IntakeSummary dataclass with extracted fields.
    """
    model = model_override or "gemini/gemini-2.0-flash-lite"

    # Format transcript for analysis
    formatted = "\n".join(f"[{msg['role'].upper()}]: {msg['content']}" for msg in transcript)

    user_prompt = f"""Analyze this confidential client intake session and extract a structured summary.

TRANSCRIPT:
---
{formatted}
---

Extract the intake summary as valid JSON."""

    # Apply prompt repetition for non-reasoning models (arXiv 2512.14982)
    is_non_reasoning = not any(kw in model.lower() for kw in ["thinking", "r1", "reasoning"])
    if is_non_reasoning:
        user_prompt = f"{user_prompt}\n\nREPEAT INSTRUCTION: Extract the intake summary as valid JSON matching the specified schema."

    try:
        import litellm

        response = await litellm.acompletion(
            model=model,
            messages=[
                {"role": "system", "content": _EXTRACTION_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.1,  # Low temp for structured extraction
            response_format={"type": "json_object"},
        )

        raw = response.choices[0].message.content
        data = json.loads(raw)

        summary = IntakeSummary(
            session_id=session_id,
            client_name=data.get("client_name", ""),
            key_facts=data.get("key_facts", []),
            legal_issues=data.get("legal_issues", []),
            opposing_parties=data.get("opposing_parties", []),
            emotional_state=EmotionalState(data.get("emotional_state", "calm")),
            urgency=Urgency(data.get("urgency", "moderate")),
            suggested_actions=data.get("suggested_actions", []),
            potential_claims=data.get("potential_claims", []),
            jurisdiction_hints=data.get("jurisdiction_hints", []),
            raw_summary=data.get("raw_summary", ""),
            confidence=float(data.get("confidence", 0.0)),
        )

        logger.info(
            "Intake summary extracted: session=%s issues=%d urgency=%s confidence=%.2f",
            session_id,
            len(summary.legal_issues),
            summary.urgency.value,
            summary.confidence,
        )
        return summary

    except ImportError:
        logger.warning("litellm not installed — returning placeholder summary")
        return IntakeSummary(
            session_id=session_id,
            raw_summary="Intake summary pending — litellm not installed.",
            confidence=0.0,
        )
    except json.JSONDecodeError as e:
        logger.error("Failed to parse intake JSON: %s", e)
        return IntakeSummary(
            session_id=session_id,
            raw_summary="Intake extraction failed — invalid JSON response.",
            confidence=0.0,
        )
    except Exception as e:
        logger.error("Intake extraction failed: %s", e)
        return IntakeSummary(
            session_id=session_id,
            raw_summary=f"Intake extraction error: {e}",
            confidence=0.0,
        )
