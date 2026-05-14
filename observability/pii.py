# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
from __future__ import annotations

import re
import hashlib
from shared.config import settings

EMAIL_REGEX = re.compile(r"[\w.-]+@[\w.-]+\.\w+")
SSN_REGEX = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
PHONE_REGEX = re.compile(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b")


def redact_pii(text: str) -> str:
    """
    Replaces sensitive data with a deterministic, salted hash.
    Preserves debugging correlations without leaking the actual PII.
    """
    if not isinstance(text, str):
        return text

    salt = settings.pii_salt

    def hasher(match: re.Match) -> str:
        raw = match.group(0)
        h = hashlib.sha256(f"{salt}:{raw}".encode()).hexdigest()[:8]
        return f"[REDACTED-{h}]"

    text = EMAIL_REGEX.sub(hasher, text)
    text = SSN_REGEX.sub(hasher, text)
    text = PHONE_REGEX.sub(hasher, text)

    return text


def scrub_dict(data: dict) -> dict:
    """Recursively scrub values in a dictionary."""
    scrubbed = {}
    for k, v in data.items():
        if isinstance(v, str):
            scrubbed[k] = redact_pii(v)
        elif isinstance(v, dict):
            scrubbed[k] = scrub_dict(v)
        elif isinstance(v, list):
            scrubbed[k] = [redact_pii(i) if isinstance(i, str) else i for i in v]
        else:
            scrubbed[k] = v
    return scrubbed
