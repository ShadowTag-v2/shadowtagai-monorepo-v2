# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""ShadowTag 2.0 Cryptographic Provenance Engine

Provides cryptographic watermarking, content-addressable hashing,
and tamper-evident audit trails for governance decisions.
"""

import hashlib
import json
import logging
from datetime import datetime

from judge6.config import get_config
from judge6.models import ProvenanceStamp, RiskLevel

logger = logging.getLogger(__name__)


class ProvenanceError(Exception):
    """Raised when provenance operations fail."""


class SignatureVerificationError(ProvenanceError):
    """Raised when signature verification fails."""


class ShadowTagEngine:
    """ShadowTag 2.0 Watermarking & Provenance System

    Provides cryptographic guarantees for:
    - Decision provenance (who, what, when, why)
    - Reasoning chain integrity
    - Tamper detection
    - Regulatory audit compliance
    """

    def __init__(self, cor_instance_id: str | None = None):
        """Initialize ShadowTag engine.

        Args:
            cor_instance_id: Unique Cor instance identifier.
                           If None, uses config default.

        """
        config = get_config()
        self.cor_instance_id = cor_instance_id or config.COR_INSTANCE_ID
        self.hash_algorithm = config.provenance.HASH_ALGORITHM
        self.signature_algorithm = config.provenance.SIGNATURE_ALGORITHM
        self.enable_pki = config.provenance.ENABLE_PKI

        logger.info(
            "ShadowTagEngine initialized: instance=%s, hash=%s",
            self.cor_instance_id,
            self.hash_algorithm,
        )

    def generate_stamp(
        self,
        purpose: str,
        reasoning_chain: str,
        risk_level: RiskLevel,
        axioms_verified: list[str],
    ) -> ProvenanceStamp:
        """Generate cryptographic provenance stamp for a decision.

        Args:
            purpose: Declared purpose of the request
            reasoning_chain: Complete reasoning chain
            risk_level: Assessed risk level
            axioms_verified: List of verified axiom IDs

        Returns:
            ProvenanceStamp with cryptographic signatures

        Raises:
            ProvenanceError: If stamp generation fails

        """
        try:
            timestamp = datetime.utcnow().isoformat() + "Z"

            # Generate content-addressable hashes
            purpose_hash = self._compute_hash(purpose)
            reasoning_hash = self._compute_hash(reasoning_chain)

            # Generate cryptographic signature
            signature = self._generate_signature(
                timestamp,
                purpose_hash,
                reasoning_hash,
                axioms_verified,
            )

            stamp = ProvenanceStamp(
                timestamp=timestamp,
                purpose_hash=purpose_hash,
                reasoning_chain_hash=reasoning_hash,
                risk_level=risk_level,
                cor_instance_id=self.cor_instance_id,
                axioms_verified=axioms_verified,
                signature=signature,
            )

            logger.info("Provenance stamp generated: signature=%s...", signature[:16])
            return stamp

        except Exception as e:
            raise ProvenanceError(f"Failed to generate provenance stamp: {e!s}") from e

    def verify_stamp(self, stamp: ProvenanceStamp, purpose: str, reasoning_chain: str) -> bool:
        """Verify cryptographic integrity of provenance stamp.

        Args:
            stamp: Provenance stamp to verify
            purpose: Original purpose string
            reasoning_chain: Original reasoning chain

        Returns:
            True if stamp is valid, False otherwise

        Raises:
            SignatureVerificationError: If verification process fails

        """
        try:
            # Verify purpose hash
            expected_purpose_hash = self._compute_hash(purpose)
            if stamp.purpose_hash != expected_purpose_hash:
                logger.warning("Purpose hash mismatch: tampering detected")
                return False

            # Verify reasoning chain hash
            expected_reasoning_hash = self._compute_hash(reasoning_chain)
            if stamp.reasoning_chain_hash != expected_reasoning_hash:
                logger.warning("Reasoning chain hash mismatch: tampering detected")
                return False

            # Verify signature
            expected_signature = self._generate_signature(
                stamp.timestamp,
                stamp.purpose_hash,
                stamp.reasoning_chain_hash,
                stamp.axioms_verified,
            )

            if stamp.signature != expected_signature:
                logger.warning("Signature mismatch: tampering detected")
                return False

            # Verify Cor instance
            if stamp.cor_instance_id != self.cor_instance_id:
                logger.warning("Cor instance mismatch: cross-instance stamp")
                return False

            logger.info("Provenance stamp verified successfully")
            return True

        except Exception as e:
            raise SignatureVerificationError(f"Stamp verification failed: {e!s}") from e

    def _compute_hash(self, content: str) -> str:
        """Compute cryptographic hash of content.

        Args:
            content: Content to hash

        Returns:
            Hexadecimal hash string

        """
        if self.hash_algorithm == "sha256":
            return hashlib.sha256(content.encode("utf-8")).hexdigest()
        if self.hash_algorithm == "sha512":
            return hashlib.sha512(content.encode("utf-8")).hexdigest()
        raise ProvenanceError(f"Unsupported hash algorithm: {self.hash_algorithm}")

    def _generate_signature(
        self,
        timestamp: str,
        purpose_hash: str,
        reasoning_hash: str,
        axioms_verified: list[str],
    ) -> str:
        """Generate cryptographic signature.

        Note: This is a simplified implementation. Production systems
        should use proper PKI with Ed25519 or RSA signatures.

        Args:
            timestamp: ISO 8601 timestamp
            purpose_hash: Purpose content hash
            reasoning_hash: Reasoning chain hash
            axioms_verified: List of verified axiom IDs

        Returns:
            Cryptographic signature (hex string)

        """
        if self.enable_pki:
            return self._generate_pki_signature(
                timestamp,
                purpose_hash,
                reasoning_hash,
                axioms_verified,
            )
        # Simplified signature for demonstration
        signature_input = self._build_signature_input(
            timestamp,
            purpose_hash,
            reasoning_hash,
            axioms_verified,
        )
        return self._compute_hash(signature_input)

    def _build_signature_input(
        self,
        timestamp: str,
        purpose_hash: str,
        reasoning_hash: str,
        axioms_verified: list[str],
    ) -> str:
        """Build canonical signature input string.

        Args:
            timestamp: ISO 8601 timestamp
            purpose_hash: Purpose content hash
            reasoning_hash: Reasoning chain hash
            axioms_verified: List of verified axiom IDs

        Returns:
            Canonical signature input string

        """
        axioms_str = ",".join(sorted(axioms_verified))
        return f"{timestamp}:{purpose_hash}:{reasoning_hash}:{self.cor_instance_id}:{axioms_str}"

    def _generate_pki_signature(
        self,
        timestamp: str,
        purpose_hash: str,
        reasoning_hash: str,
        axioms_verified: list[str],
    ) -> str:
        """Generate PKI-based cryptographic signature.

        Note: Placeholder for production PKI implementation.

        Args:
            timestamp: ISO 8601 timestamp
            purpose_hash: Purpose content hash
            reasoning_hash: Reasoning chain hash
            axioms_verified: List of verified axiom IDs

        Returns:
            PKI signature (hex string)

        Raises:
            NotImplementedError: PKI not implemented in this version

        """
        # TODO: Implement Ed25519 or RSA signature generation
        raise NotImplementedError(
            "PKI signature generation not implemented. "
            "Set ENABLE_PKI=False in config for demo mode.",
        )

    def export_stamp(self, stamp: ProvenanceStamp) -> str:
        """Export provenance stamp as JSON.

        Args:
            stamp: Provenance stamp to export

        Returns:
            JSON string representation

        """
        return json.dumps(stamp.to_dict(), indent=2)

    def import_stamp(self, json_str: str) -> ProvenanceStamp:
        """Import provenance stamp from JSON.

        Args:
            json_str: JSON string representation

        Returns:
            ProvenanceStamp instance

        Raises:
            ProvenanceError: If import fails

        """
        try:
            data = json.loads(json_str)
            risk_level = RiskLevel(data["risk_level"])

            return ProvenanceStamp(
                timestamp=data["timestamp"],
                purpose_hash=data["purpose_hash"],
                reasoning_chain_hash=data["reasoning_chain_hash"],
                risk_level=risk_level,
                cor_instance_id=data["cor_instance_id"],
                axioms_verified=data["axioms_verified"],
                signature=data["signature"],
            )
        except Exception as e:
            raise ProvenanceError(f"Failed to import stamp: {e!s}") from e
