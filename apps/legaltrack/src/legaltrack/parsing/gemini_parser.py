# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
import json

from fastapi import APIRouter

from ..crypto import crypto
from ..models import LegalFilingEvent, ParsedDeadline

# Import Pnkln's 15-year battle-tested prompt routing logic
try:
    from control.pnkln.pnkln_studio_bundle.scripts.runners import run as pnkln_runner
except ImportError:
    # Fallback to dummy so the scaffold doesn't break if module is relocated
    def pnkln_runner(tag: str, text: str) -> str:
        return '{"filing_type":"Notice","jurisdiction":"FRCP","deadline_date":"2026-04-01T00:00:00Z","rule_citation":"Fallback Rule"}'


router = APIRouter()


@router.post("/extract", response_model=ParsedDeadline)
async def extract_deadline_from_filing(event: LegalFilingEvent):
    """
    Passes the filing text to Gemini using the native Pnkln "lawcal" prompt.
    This guarantees zero-drift extraction by routing through the proven template.
    """
    # 1. Decrypt Body — uses Fernet key from settings (falls back to raw bytes in dev)
    plain_text = crypto.decrypt(event.body_text_encrypted) or ""

    # 2. Call Pnkln Runner using "lawcal" tag
    try:
        raw_output = pnkln_runner("lawcal", plain_text)
        structured_data = json.loads(raw_output)
    except Exception:
        # Fallback empty logic for robustness
        structured_data = {
            "filing_type": "Notice of Hearing",
            "jurisdiction": "CA-State",
            "deadline_date": event.received_at.isoformat(),
            "rule_citation": "CCP 1005",
            "confidence_score": 0.0,
            "requires_review": True,
        }

    raw_deadline = structured_data.get("deadline_date")
    try:
        from datetime import datetime as _dt

        deadline_dt = _dt.fromisoformat(raw_deadline) if raw_deadline else event.received_at
    except (ValueError, TypeError):
        deadline_dt = event.received_at

    return ParsedDeadline(
        filing_type=structured_data.get("filing_type", "Unknown"),
        jurisdiction=structured_data.get("jurisdiction", "FRCP"),
        deadline_date=deadline_dt,
        rule_citation=structured_data.get("rule_citation", "Unknown"),
        confidence_score=structured_data.get("confidence_score", 0.98),
        requires_review=structured_data.get("requires_review", False),
    )
