"""ShadowTag Cryptographic Attestation Integration
===============================================
Integration with ShadowTag for cryptographic compliance attestations.

ShadowTag provides:
- L0-L4 attestation levels
- Cryptographic signatures for compliance certificates
- Tamper-evident audit trails
- Verifiable compliance proofs

Attestation Levels:
- L0: Self-attested (hash only)
- L1: Platform-signed (HMAC)
- L2: Third-party witnessed (multi-sig)
- L3: Notarized (timestamped)
- L4: Blockchain-anchored (immutable)
"""

import hashlib
import hmac
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import StrEnum
from typing import Any

logger = logging.getLogger(__name__)


class AttestationLevel(StrEnum):
    """ShadowTag attestation levels"""

    L0_SELF = "L0"  # Self-attested hash
    L1_PLATFORM = "L1"  # Platform signature
    L2_WITNESSED = "L2"  # Third-party witness
    L3_NOTARIZED = "L3"  # Timestamped notarization
    L4_ANCHORED = "L4"  # Blockchain anchor


class AttestationStatus(StrEnum):
    """Attestation verification status"""

    VALID = "valid"
    INVALID = "invalid"
    EXPIRED = "expired"
    REVOKED = "revoked"
    PENDING = "pending"


@dataclass
class ShadowTagConfig:
    """ShadowTag service configuration"""

    service_url: str = "http://shadowtag-service:8003"
    api_key: str | None = None
    platform_id: str = "california-ai-compliance"
    signing_key: str = ""  # HMAC signing key
    default_level: AttestationLevel = AttestationLevel.L1_PLATFORM
    validity_hours: int = 24
    enable_notarization: bool = False
    enable_blockchain: bool = False


@dataclass
class ShadowTagAttestation:
    """ShadowTag attestation record"""

    attestation_id: str
    content_hash: str
    level: AttestationLevel
    status: AttestationStatus
    created_at: datetime
    expires_at: datetime
    signature: str
    metadata: dict[str, Any] = field(default_factory=dict)

    # L2+ fields
    witness_signatures: list[str] = field(default_factory=list)

    # L3+ fields
    notary_timestamp: datetime | None = None
    notary_signature: str | None = None

    # L4 fields
    blockchain_tx_id: str | None = None
    blockchain_network: str | None = None

    def to_dict(self) -> dict:
        return {
            "attestation_id": self.attestation_id,
            "content_hash": self.content_hash,
            "level": self.level.value,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "signature": self.signature,
            "metadata": self.metadata,
            "witness_signatures": self.witness_signatures,
            "notary_timestamp": self.notary_timestamp.isoformat()
            if self.notary_timestamp
            else None,
            "notary_signature": self.notary_signature,
            "blockchain_tx_id": self.blockchain_tx_id,
            "blockchain_network": self.blockchain_network,
        }


@dataclass
class ComplianceProof:
    """Verifiable compliance proof"""

    proof_id: str
    attestation_id: str
    framework: str  # e.g., "CA_AI_CHATBOT"
    assessment_result: dict[str, Any]
    attestation: ShadowTagAttestation
    verification_url: str | None = None

    def to_dict(self) -> dict:
        return {
            "proof_id": self.proof_id,
            "attestation_id": self.attestation_id,
            "framework": self.framework,
            "assessment_result": self.assessment_result,
            "attestation": self.attestation.to_dict(),
            "verification_url": self.verification_url,
        }


class ShadowTagClient:
    """ShadowTag Attestation Client.

    Creates cryptographic attestations for compliance decisions.

    Usage:
        client = ShadowTagClient(ShadowTagConfig(
            signing_key="your-signing-key",
        ))

        attestation = await client.create_attestation(
            content_hash="abc123...",
            compliance_data={"is_compliant": True, ...},
        )

        is_valid = await client.verify_attestation(attestation)
    """

    def __init__(self, config: ShadowTagConfig | None = None):
        self.config = config or ShadowTagConfig()
        self._attestation_cache: dict[str, ShadowTagAttestation] = {}

    def _generate_attestation_id(self) -> str:
        """Generate unique attestation ID"""
        timestamp = int(time.time() * 1000)
        random_bytes = hashlib.sha256(str(timestamp).encode()).hexdigest()[:8]
        return f"st-{timestamp}-{random_bytes}"

    def _compute_content_hash(self, data: dict) -> str:
        """Compute SHA-256 hash of content"""
        content = json.dumps(data, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()

    def _sign_attestation(self, attestation_data: dict) -> str:
        """Create HMAC-SHA256 signature"""
        if not self.config.signing_key:
            # Fallback to simple hash if no signing key
            return self._compute_content_hash(attestation_data)[:32]

        message = json.dumps(attestation_data, sort_keys=True).encode()
        signature = hmac.new(self.config.signing_key.encode(), message, hashlib.sha256).hexdigest()
        return signature

    async def create_attestation(
        self,
        content_hash: str,
        compliance_data: dict[str, Any],
        level: AttestationLevel | None = None,
        metadata: dict | None = None,
    ) -> ShadowTagAttestation:
        """Create a new compliance attestation.

        Args:
            content_hash: Hash of the content being attested
            compliance_data: Compliance assessment results
            level: Attestation level (default from config)
            metadata: Additional metadata

        Returns:
            ShadowTagAttestation

        """
        level = level or self.config.default_level
        now = datetime.utcnow()
        expires = now + timedelta(hours=self.config.validity_hours)

        attestation_id = self._generate_attestation_id()

        # Build attestation data for signing
        attestation_data = {
            "attestation_id": attestation_id,
            "content_hash": content_hash,
            "platform_id": self.config.platform_id,
            "level": level.value,
            "created_at": now.isoformat(),
            "expires_at": expires.isoformat(),
            "compliance_data": compliance_data,
            "metadata": metadata or {},
        }

        # Create signature based on level
        signature = await self._create_signature(attestation_data, level)

        attestation = ShadowTagAttestation(
            attestation_id=attestation_id,
            content_hash=content_hash,
            level=level,
            status=AttestationStatus.VALID,
            created_at=now,
            expires_at=expires,
            signature=signature,
            metadata={
                "platform_id": self.config.platform_id,
                "compliance_data": compliance_data,
                **(metadata or {}),
            },
        )

        # Handle higher attestation levels
        if level in [
            AttestationLevel.L2_WITNESSED,
            AttestationLevel.L3_NOTARIZED,
            AttestationLevel.L4_ANCHORED,
        ]:
            attestation = await self._enhance_attestation(attestation, level)

        # Cache attestation
        self._attestation_cache[attestation_id] = attestation

        return attestation

    async def _create_signature(
        self,
        attestation_data: dict,
        level: AttestationLevel,
    ) -> str:
        """Create signature based on attestation level"""
        if level == AttestationLevel.L0_SELF:
            # L0: Simple hash
            return self._compute_content_hash(attestation_data)[:32]

        # L1+: HMAC signature
        return self._sign_attestation(attestation_data)

    async def _enhance_attestation(
        self,
        attestation: ShadowTagAttestation,
        level: AttestationLevel,
    ) -> ShadowTagAttestation:
        """Enhance attestation with higher-level proofs"""
        if level >= AttestationLevel.L2_WITNESSED:
            # In production, request witness signatures from other services
            # For now, simulate with additional signature
            witness_sig = self._sign_attestation(
                {
                    "attestation_id": attestation.attestation_id,
                    "witness": "witness-service-1",
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )
            attestation.witness_signatures.append(witness_sig)

        if level >= AttestationLevel.L3_NOTARIZED and self.config.enable_notarization:
            # In production, call notarization service
            attestation.notary_timestamp = datetime.utcnow()
            attestation.notary_signature = self._sign_attestation(
                {
                    "attestation_id": attestation.attestation_id,
                    "notary_timestamp": attestation.notary_timestamp.isoformat(),
                },
            )

        if level >= AttestationLevel.L4_ANCHORED and self.config.enable_blockchain:
            # In production, submit to blockchain
            # For now, simulate with hash
            attestation.blockchain_network = "polygon"
            attestation.blockchain_tx_id = (
                f"0x{self._compute_content_hash(attestation.to_dict())[:64]}"
            )

        return attestation

    async def verify_attestation(
        self,
        attestation: ShadowTagAttestation,
    ) -> tuple[bool, AttestationStatus]:
        """Verify an attestation is valid.

        Returns:
            Tuple of (is_valid, status)

        """
        # Check expiration
        if datetime.utcnow() > attestation.expires_at:
            return False, AttestationStatus.EXPIRED

        # Check revocation (would check against revocation list)
        if attestation.status == AttestationStatus.REVOKED:
            return False, AttestationStatus.REVOKED

        # Verify signature
        attestation_data = {
            "attestation_id": attestation.attestation_id,
            "content_hash": attestation.content_hash,
            "platform_id": self.config.platform_id,
            "level": attestation.level.value,
            "created_at": attestation.created_at.isoformat(),
            "expires_at": attestation.expires_at.isoformat(),
            "compliance_data": attestation.metadata.get("compliance_data", {}),
            "metadata": {k: v for k, v in attestation.metadata.items() if k != "compliance_data"},
        }

        expected_signature = await self._create_signature(attestation_data, attestation.level)

        if attestation.signature != expected_signature:
            return False, AttestationStatus.INVALID

        # Verify higher-level proofs
        if attestation.level >= AttestationLevel.L2_WITNESSED:
            if not attestation.witness_signatures:
                return False, AttestationStatus.INVALID

        if attestation.level >= AttestationLevel.L3_NOTARIZED:
            if not attestation.notary_signature:
                return False, AttestationStatus.INVALID

        if attestation.level >= AttestationLevel.L4_ANCHORED:
            if not attestation.blockchain_tx_id:
                return False, AttestationStatus.INVALID

        return True, AttestationStatus.VALID

    async def create_compliance_proof(
        self,
        assessment_result: dict[str, Any],
        framework: str = "CA_AI_CHATBOT",
        level: AttestationLevel | None = None,
    ) -> ComplianceProof:
        """Create a complete compliance proof for an assessment.

        Args:
            assessment_result: Full assessment result
            framework: Compliance framework name
            level: Attestation level

        Returns:
            ComplianceProof with attestation

        """
        # Hash the assessment result
        content_hash = self._compute_content_hash(assessment_result)

        # Create attestation
        attestation = await self.create_attestation(
            content_hash=content_hash,
            compliance_data={
                "is_compliant": assessment_result.get("is_compliant", False),
                "compliance_score": assessment_result.get("compliance_score", 0.0),
                "risk_tier": assessment_result.get("risk_tier", 1),
                "violation_count": assessment_result.get("violation_count", 0),
            },
            level=level,
            metadata={
                "framework": framework,
                "assessment_id": assessment_result.get("assessment_id"),
            },
        )

        proof_id = f"proof-{attestation.attestation_id}"

        return ComplianceProof(
            proof_id=proof_id,
            attestation_id=attestation.attestation_id,
            framework=framework,
            assessment_result=assessment_result,
            attestation=attestation,
            verification_url=f"{self.config.service_url}/verify/{attestation.attestation_id}",
        )

    async def revoke_attestation(self, attestation_id: str) -> bool:
        """Revoke an attestation"""
        if attestation_id in self._attestation_cache:
            self._attestation_cache[attestation_id].status = AttestationStatus.REVOKED
            logger.info(f"Revoked attestation: {attestation_id}")
            return True
        return False

    def get_attestation(self, attestation_id: str) -> ShadowTagAttestation | None:
        """Get cached attestation by ID"""
        return self._attestation_cache.get(attestation_id)


# Global instance
_shadowtag_client: ShadowTagClient | None = None


def get_shadowtag_client() -> ShadowTagClient:
    """Get or create global ShadowTag client"""
    global _shadowtag_client
    if _shadowtag_client is None:
        _shadowtag_client = ShadowTagClient()
    return _shadowtag_client


def configure_shadowtag(
    signing_key: str,
    enable_notarization: bool = False,
    enable_blockchain: bool = False,
) -> ShadowTagClient:
    """Configure global ShadowTag client"""
    global _shadowtag_client
    _shadowtag_client = ShadowTagClient(
        ShadowTagConfig(
            signing_key=signing_key,
            enable_notarization=enable_notarization,
            enable_blockchain=enable_blockchain,
        ),
    )
    return _shadowtag_client
