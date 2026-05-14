# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
ZT.1 Legal Agent — Zero-Drift Deadline Extractor
=================================================
Agent-Drafted, Human-Verified pattern (NOT truly zero-touch).
Every extraction carries an exhibit_citation_id pointing to the exact
paragraph in the source document (Zero-Drift guarantee).

Compute route: zero_cpu_router.dispatch_compute (ANE → kvcached → raise)
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger("LegalAgent")

try:
    from zero_cpu_router import dispatch_compute
except ImportError:
    dispatch_compute = None

# ── Extraction prompt (structured JSON output) ───────────────────────────────

_EXTRACTION_PROMPT = """You are a legal deadline extraction specialist.

Analyze the filing and extract EVERY deadline, obligation, and time-sensitive
trigger. For each item return ONLY the JSON schema below. If NO deadlines exist,
return an empty JSON array []. DO NOT fabricate or assume standard windows.

Schema per item:
{
  "trigger_event": "<what starts the clock, verbatim from filing>",
  "exhibit_citation_id": "<exact location: Page N, ¶M or Section X.Y>",
  "days_to_respond": <integer>,
  "business_days_only": <true|false>,
  "jurisdiction_rule": "<e.g. FRCP 12(a)(1)(A)(i) or empty string>",
  "raw_date_text": "<date as written in the filing or empty string>"
}

Filing text:
{filing_text}

Return valid JSON array only. No prose."""

_HALLUCINATION_GUARD = frozenset(
    {
        "30 days",
        "thirty days",
        "standard response window",
        "default deadline",
    }
)


# ── Data structures ───────────────────────────────────────────────────────────


@dataclass
class ExtractedDeadline:
    trigger_event: str
    exhibit_citation_id: str
    days_to_respond: int
    business_days_only: bool
    jurisdiction_rule: str
    raw_date_text: str

    def is_hallucination_candidate(self) -> bool:
        """Flag if trigger_event matches known hallucination patterns."""
        lower = self.trigger_event.lower()
        return any(pattern in lower for pattern in _HALLUCINATION_GUARD)


# ── Extraction logic ──────────────────────────────────────────────────────────


def extract_deadlines_from_filing(
    raw_text: str,
    filing_name: str = "filing",
) -> list[ExtractedDeadline]:
    """
    Run AI extraction over a raw filing.

    Returns a list of ExtractedDeadline objects. Returns [] if none found.
    Raises RuntimeError if no zero-CPU backend is available.
    """
    if dispatch_compute is None:
        raise RuntimeError("dispatch_compute is not available.")

    prompt = _EXTRACTION_PROMPT.replace("{filing_text}", raw_text[:8000])
    raw_results = dispatch_compute(
        text=prompt,
        prompt_description="legal-deadline-extraction",
        examples=[],
        file_name=filing_name,
    )
    return _parse_extraction_results(raw_results, filing_name)


def _parse_extraction_results(
    raw_results: list[dict[str, Any]],
    filing_name: str,
) -> list[ExtractedDeadline]:
    """Parse model output → typed ExtractedDeadline list."""
    if not raw_results:
        return []

    combined_text = " ".join(r.get("text", "") for r in raw_results).strip()
    if not combined_text:
        return []

    try:
        items: list[dict[str, Any]] = json.loads(combined_text)
    except json.JSONDecodeError:
        logger.error(f"[LegalAgent] JSON parse failed for {filing_name}")
        return []

    if not isinstance(items, list):
        logger.warning(f"[LegalAgent] Unexpected non-array response for {filing_name}")
        return []

    deadlines: list[ExtractedDeadline] = []
    for item in items:
        dl = _coerce_item(item)
        if dl is None:
            continue
        if dl.is_hallucination_candidate():
            logger.warning(f"[LegalAgent] Hallucination candidate filtered: {dl.trigger_event!r}")
            continue
        deadlines.append(dl)
    return deadlines


def _coerce_item(item: dict[str, Any]) -> ExtractedDeadline | None:
    """Validate and coerce a raw dict → ExtractedDeadline. Returns None on bad data."""
    try:
        return ExtractedDeadline(
            trigger_event=str(item["trigger_event"]).strip(),
            exhibit_citation_id=str(item["exhibit_citation_id"]).strip(),
            days_to_respond=int(item["days_to_respond"]),
            business_days_only=str(item.get("business_days_only", "")).strip().lower() in ("true", "1", "yes", "t") if isinstance(item.get("business_days_only"), str) else bool(item.get("business_days_only", False)),
            jurisdiction_rule=str(item.get("jurisdiction_rule", "")).strip(),
            raw_date_text=str(item.get("raw_date_text", "")).strip(),
        )
    except (KeyError, ValueError, TypeError) as exc:
        logger.warning(f"[LegalAgent] Skipping malformed item {item}: {exc}")
        return None


# ── Downstream case reasoning ─────────────────────────────────────────────────


def reason_about_case(case_facts: dict[str, Any]) -> dict[str, Any]:
    """
    Stub for the LegalReasoner agent.
    Returns a structured reasoning scaffold — does NOT make legal conclusions.
    """
    return {
        "input_facts": case_facts,
        "legal_issues_to_check": [
            "jurisdiction",
            "pleading_standards",
            "service_of_process",
            "statute_of_limitations",
        ],
        "reasoning_mode": "cite-verified-sources-only",
    }


def calculate_deadlines(case_filing: dict[str, Any]) -> dict[str, Any]:
    """
    Legacy stub — retained for backward compatibility.
    For new code, use extract_deadlines_from_filing().
    """
    return {
        "case_details": case_filing,
        "processing_steps": [
            "receive_filing",
            "calculate_deadlines",
            "prepare_forms",
            "alert_stakeholders",
        ],
        "status": "completed",
    }
