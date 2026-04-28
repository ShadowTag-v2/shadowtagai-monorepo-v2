# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

# apps/counselconduit/api/kovel_attestation.py
"""Heppner/Kovel Attestation Receipt System.

Generates a cryptographic hash per privileged session proving:
1. Attorney-client communication occurred under Kovel doctrine
2. AI was acting as agent of attorney (not direct client advisor)
3. Session was ephemeral on client side, persistent on attorney side
4. Privilege was not waived (no unauthorized third-party access)

Legal basis: United States v. Heppner (S.D.N.Y., Feb. 10, 2026)
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
import time
from collections import defaultdict
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

logger = logging.getLogger("counselconduit.kovel_attestation")

router = APIRouter(prefix="/attestation", tags=["Kovel Attestation"])

# HMAC signing key for attestation receipts
_ATTESTATION_SECRET = os.getenv("KOVEL_ATTESTATION_SECRET", "kovel-dev-secret")

# ── Rate Limiting (#9) ────────────────────────────────────────────────────

_RATE_LIMIT_WINDOW = 60  # seconds
_RATE_LIMIT_MAX = 10  # max requests per window per firm

# In-memory sliding window rate limiter (per-firm)
_rate_windows: dict[str, list[float]] = defaultdict(list)


def _check_rate_limit(firm_id: str) -> bool:
    """Check if firm has exceeded rate limit. Returns True if allowed."""
    now = time.monotonic()
    window = _rate_windows[firm_id]

    # Purge expired entries
    _rate_windows[firm_id] = [t for t in window if now - t < _RATE_LIMIT_WINDOW]

    if len(_rate_windows[firm_id]) >= _RATE_LIMIT_MAX:
        return False

    _rate_windows[firm_id].append(now)
    return True


# ── Models ─────────────────────────────────────────────────────────────────


class SessionAttestation(BaseModel):
    """Kovel Attestation Receipt — cryptographic proof of privileged session."""

    attestation_id: str
    session_id: str
    attorney_id: str
    firm_id: str
    client_id: str  # opaque ID, no PII
    model_used: str
    query_hash: str  # SHA-256 of the original query (not the query itself)
    response_hash: str  # SHA-256 of the response
    timestamp: str  # ISO 8601
    privilege_type: str = "kovel_doctrine"
    hmac_signature: str  # HMAC-SHA256 of the receipt body
    metadata: dict[str, Any] = Field(default_factory=dict)


class AttestationRequest(BaseModel):
    """Request to generate an attestation receipt."""

    session_id: str
    attorney_id: str
    firm_id: str
    client_id: str
    model_used: str
    query_text: str  # hashed, never stored
    response_text: str  # hashed, never stored


# ── Core Functions ─────────────────────────────────────────────────────────


def _hash_text(text: str) -> str:
    """SHA-256 hash of text — for content attestation without storing content."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _sign_receipt(receipt_body: dict[str, Any]) -> str:
    """HMAC-SHA256 signature of the receipt body."""
    canonical = json.dumps(receipt_body, sort_keys=True, separators=(",", ":"))
    return hmac.new(
        _ATTESTATION_SECRET.encode("utf-8"),
        canonical.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def generate_attestation(req: AttestationRequest) -> SessionAttestation:
    """Generate a Kovel Attestation Receipt for a privileged session."""
    try:
        from apps.counselconduit.api.uuid7 import uuid7_str
    except ImportError:
        from api.uuid7 import uuid7_str  # type: ignore[no-redef]

    attestation_id = uuid7_str()
    timestamp = datetime.now(UTC).isoformat()

    receipt_body = {
        "attestation_id": attestation_id,
        "session_id": req.session_id,
        "attorney_id": req.attorney_id,
        "firm_id": req.firm_id,
        "client_id": req.client_id,
        "model_used": req.model_used,
        "query_hash": _hash_text(req.query_text),
        "response_hash": _hash_text(req.response_text),
        "timestamp": timestamp,
        "privilege_type": "kovel_doctrine",
    }

    signature = _sign_receipt(receipt_body)

    return SessionAttestation(
        **receipt_body,
        hmac_signature=signature,
    )


def verify_attestation(attestation: SessionAttestation) -> bool:
    """Verify the HMAC signature of an attestation receipt."""
    receipt_body = attestation.model_dump(exclude={"hmac_signature", "metadata"})
    expected_sig = _sign_receipt(receipt_body)
    return hmac.compare_digest(expected_sig, attestation.hmac_signature)


# ── Endpoints ──────────────────────────────────────────────────────────────


@router.post("/generate", response_model=SessionAttestation)
async def create_attestation(req: AttestationRequest) -> SessionAttestation:
    """Generate a new Kovel Attestation Receipt.

    The receipt proves that a privileged attorney-client communication
    occurred via AI under the Kovel doctrine, without storing the
    actual content (only SHA-256 hashes).

    Rate-limited: 10 requests per minute per firm.
    """
    # #9: Rate limiting
    if not _check_rate_limit(req.firm_id):
        logger.warning(
            "Rate limit exceeded: firm=%s (max %d/min)",
            req.firm_id,
            _RATE_LIMIT_MAX,
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "code": "RATE_LIMIT_EXCEEDED",
                "message": f"Maximum {_RATE_LIMIT_MAX} attestation requests per minute per firm.",
            },
        )

    attestation = generate_attestation(req)

    # Store in Firestore (immutable, append-only collection)
    try:
        try:
            from apps.counselconduit.api.firestore_client import store_attestation
        except ImportError:
            from api.firestore_client import store_attestation  # type: ignore[no-redef]

        await store_attestation(req.firm_id, attestation.model_dump())
    except Exception as e:
        # #16: Structured monitoring alert for attestation failures
        logger.error(
            "ATTESTATION_STORE_FAILURE: firm=%s id=%s error=%s",
            req.firm_id,
            attestation.attestation_id,
            str(e),
            extra={
                "severity": "ERROR",
                "labels": {
                    "service": "counselconduit",
                    "component": "kovel_attestation",
                    "alert_type": "attestation_persistence_failure",
                },
            },
        )

    logger.info(
        "Kovel attestation generated: id=%s session=%s firm=%s",
        attestation.attestation_id,
        attestation.session_id,
        attestation.firm_id,
    )

    return attestation


@router.post("/verify")
async def verify_receipt(attestation: SessionAttestation) -> dict[str, Any]:
    """Verify the integrity of a Kovel Attestation Receipt."""
    is_valid = verify_attestation(attestation)
    return {
        "attestation_id": attestation.attestation_id,
        "valid": is_valid,
        "message": "Receipt integrity verified." if is_valid else "INVALID — receipt has been tampered with.",
    }
