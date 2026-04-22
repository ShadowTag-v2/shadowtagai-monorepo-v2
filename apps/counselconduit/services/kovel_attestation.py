# Copyright 2026 ShadowTag AI. All rights reserved.
# SPDX-License-Identifier: Proprietary
"""HMAC-SHA256 Kovel Attestation Receipt Generator.

Generates cryptographic attestation receipts per privileged session
to prove that communications occurred under attorney-client privilege
per United States v. Heppner (S.D.N.Y., Feb. 10, 2026).

Each receipt contains:
- Session ID
- Tenant ID (law firm)
- User ID (attorney or client)
- Timestamp (ISO 8601)
- Content hash (SHA-256 of session transcript)
- HMAC signature (keyed with tenant-specific secret)
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class KovelAttestation:
    """A Kovel attestation receipt proving privileged communication."""

    attestation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str = ""
    tenant_id: str = ""
    user_id: str = ""
    timestamp: str = field(
        default_factory=lambda: datetime.now(UTC).isoformat()
    )
    content_hash: str = ""  # SHA-256 of session content
    hmac_signature: str = ""  # HMAC-SHA256 of the receipt
    privilege_basis: str = "Kovel (United States v. Heppner, S.D.N.Y. 2026)"

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary for Firestore storage."""
        return {
            "attestation_id": self.attestation_id,
            "session_id": self.session_id,
            "tenant_id": self.tenant_id,
            "user_id": self.user_id,
            "timestamp": self.timestamp,
            "content_hash": self.content_hash,
            "hmac_signature": self.hmac_signature,
            "privilege_basis": self.privilege_basis,
        }


class KovelAttestationService:
    """Generates and verifies Kovel attestation receipts.

    Security:
    - HMAC-SHA256 signatures using tenant-specific secrets
    - SHA-256 content hashing for transcript integrity
    - Immutable receipts stored in Firestore
    """

    def __init__(self, secret_key: bytes | None = None) -> None:
        """Initialize with a signing key.

        Args:
            secret_key: The HMAC signing key. In production, fetched
                from GCP Secret Manager per tenant.
        """
        self._secret_key = secret_key or b"dev-only-key-replace-in-production"

    def generate_content_hash(self, content: str) -> str:
        """Generate SHA-256 hash of session content.

        Args:
            content: The session transcript or content to hash.

        Returns:
            Hex-encoded SHA-256 hash.
        """
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def generate_hmac(self, data: str) -> str:
        """Generate HMAC-SHA256 signature.

        Args:
            data: The data to sign.

        Returns:
            Hex-encoded HMAC-SHA256 signature.
        """
        return hmac.new(
            self._secret_key,
            data.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    def create_attestation(
        self,
        *,
        session_id: str,
        tenant_id: str,
        user_id: str,
        transcript_content: str,
    ) -> KovelAttestation:
        """Create a complete Kovel attestation receipt.

        Args:
            session_id: The session this attestation covers.
            tenant_id: The law firm tenant ID.
            user_id: The authenticated user (attorney/client).
            transcript_content: The session transcript to attest.

        Returns:
            A fully signed KovelAttestation receipt.
        """
        content_hash = self.generate_content_hash(transcript_content)

        attestation = KovelAttestation(
            session_id=session_id,
            tenant_id=tenant_id,
            user_id=user_id,
            content_hash=content_hash,
        )

        # Sign the canonical receipt data
        canonical = json.dumps(
            {
                "attestation_id": attestation.attestation_id,
                "session_id": attestation.session_id,
                "tenant_id": attestation.tenant_id,
                "user_id": attestation.user_id,
                "timestamp": attestation.timestamp,
                "content_hash": attestation.content_hash,
            },
            sort_keys=True,
        )
        attestation.hmac_signature = self.generate_hmac(canonical)

        logger.info(
            "Kovel attestation created: id=%s session=%s tenant=%s",
            attestation.attestation_id,
            session_id,
            tenant_id,
        )
        return attestation

    def verify_attestation(self, attestation: KovelAttestation) -> bool:
        """Verify the HMAC signature of an attestation receipt.

        Args:
            attestation: The attestation to verify.

        Returns:
            True if the signature is valid.
        """
        canonical = json.dumps(
            {
                "attestation_id": attestation.attestation_id,
                "session_id": attestation.session_id,
                "tenant_id": attestation.tenant_id,
                "user_id": attestation.user_id,
                "timestamp": attestation.timestamp,
                "content_hash": attestation.content_hash,
            },
            sort_keys=True,
        )
        expected = self.generate_hmac(canonical)
        return hmac.compare_digest(attestation.hmac_signature, expected)
