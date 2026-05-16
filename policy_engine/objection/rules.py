# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
from __future__ import annotations

REJECTION_RULES = {
    "intent_alignment": "Reject if the diff changes the mission or user-intended behavior without an explicit flag or migration note.",
    "legal_claims": "Reject if the diff introduces unqualified legal conclusions, guarantees, or advice phrased as certainty.",
    "security_regression": "Reject if secrets, raw PII, or unsigned artifact paths are introduced.",
    "jurisdiction_bypass": "Reject if region checks, export controls, or sovereignty constraints are removed or bypassed.",
}
