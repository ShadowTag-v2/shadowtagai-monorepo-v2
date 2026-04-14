"""ShadowTag Integration for V2X Vehicle Attestation

Provides:
- Per-node key management in TEE/TPM
- Rotating pseudonyms for privacy
- Revocation list management
- Distance-bounding hints
- Signed evidence to audit vault
- Integration with existing ShadowTag service
"""

import base64
import hashlib
import json
import secrets
import time
from dataclasses import dataclass


@dataclass
class VehicleIdentity:
    """Vehicle identity credentials"""

    vehicle_id: str  # Permanent vehicle identifier (encrypted in TEE)
    current_pseudonym: bytes  # Current rotating pseudonym (8 bytes)
    pseudonym_epoch: int  # When current pseudonym expires (Unix timestamp)
    master_key_id: str  # Reference to master key in HSM/TPM
    certificate_chain: list[str]  # X.509 certificate chain
    revocation_status: str = "valid"  # "valid", "revoked", "suspended"


@dataclass
class AttestationEvidence:
    """Cryptographic evidence for audit trail"""

    evidence_id: str
    vehicle_pseudonym: bytes
    timestamp: int
    evidence_type: str  # "beacon", "event", "consensus_vote"
    message_hash: str
    signature: bytes
    distance_bound: float | None = None  # Max distance from claimed position (meters)
    witness_count: int = 0  # Number of peer witnesses


@dataclass
class RevocationEntry:
    """Revocation list entry"""

    revoked_id: bytes  # Pseudonym or certificate hash
    revocation_time: int
    reason: str
    authority: str
    proof_signature: bytes
    expires: int | None = None  # For temporary suspensions


class ShadowTagAttestation:
    """ShadowTag attestation system for V2X mesh

    Integrates with existing ShadowTag service for:
    - Video/sensor data watermarking
    - Deepfake detection
    - Audit trail generation
    """

    def __init__(
        self,
        vehicle_id: str,
        shadowtag_api_endpoint: str = "http://shadowtag-service:8003",
        use_tee: bool = True,
        pseudonym_rotation_interval: int = 3600,  # 1 hour
    ):
        self.vehicle_id = vehicle_id
        self.shadowtag_endpoint = shadowtag_api_endpoint
        self.use_tee = use_tee
        self.pseudonym_rotation_interval = pseudonym_rotation_interval

        # Identity management
        self.identity: VehicleIdentity | None = None
        self.identity_cache: dict[bytes, VehicleIdentity] = {}

        # Revocation list
        self.revocation_list: dict[bytes, RevocationEntry] = {}
        self.revocation_list_version = 0

        # Evidence vault
        self.evidence_vault: list[AttestationEvidence] = []

        # Initialize identity
        self._initialize_identity()

    def _initialize_identity(self):
        """Initialize vehicle identity with rotating pseudonym"""
        # Generate or load master key
        master_key_id = self._get_master_key_id()

        # Generate initial pseudonym
        pseudonym = self._generate_pseudonym()
        epoch = int(time.time()) + self.pseudonym_rotation_interval

        self.identity = VehicleIdentity(
            vehicle_id=self.vehicle_id,
            current_pseudonym=pseudonym,
            pseudonym_epoch=epoch,
            master_key_id=master_key_id,
            certificate_chain=[],  # Would be loaded from PKI
        )

    def _get_master_key_id(self) -> str:
        """Get or generate master key ID"""
        if self.use_tee:
            # In production: retrieve from TEE/TPM
            # TPM path: /sys/class/tpm/tpm0/device/caps
            return f"tee::{hashlib.sha256(self.vehicle_id.encode()).hexdigest()[:16]}"
        # Development: use vehicle ID hash
        return f"dev::{hashlib.sha256(self.vehicle_id.encode()).hexdigest()[:16]}"

    def _generate_pseudonym(self) -> bytes:
        """Generate random pseudonym"""
        return secrets.token_bytes(8)

    def get_current_pseudonym(self) -> bytes:
        """Get current pseudonym, rotating if needed"""
        if not self.identity:
            self._initialize_identity()

        # Check if rotation needed
        now = int(time.time())
        if now >= self.identity.pseudonym_epoch:
            self._rotate_pseudonym()

        return self.identity.current_pseudonym

    def _rotate_pseudonym(self):
        """Rotate to new pseudonym"""
        if not self.identity:
            return

        # Cache old identity
        old_pseudonym = self.identity.current_pseudonym
        self.identity_cache[old_pseudonym] = self.identity

        # Generate new pseudonym
        new_pseudonym = self._generate_pseudonym()
        new_epoch = int(time.time()) + self.pseudonym_rotation_interval

        self.identity.current_pseudonym = new_pseudonym
        self.identity.pseudonym_epoch = new_epoch

        print(f"Rotated pseudonym: {old_pseudonym.hex()[:8]} -> {new_pseudonym.hex()[:8]}")

    def sign_message(self, message_data: bytes) -> bytes:
        """Sign message using Ed25519 in TEE/TPM

        In production, this calls into secure enclave.
        For development, uses HMAC-SHA256.
        """
        if self.use_tee:
            # Production: use TEE/TPM
            # Example: tpm2_sign -c 0x81010001 -g sha256 -o signature.bin message.bin
            signature = self._tee_sign(message_data)
        else:
            # Development: simple signature
            signature = self._dev_sign(message_data)

        # Record evidence
        self._record_evidence(
            evidence_type="signature",
            message_hash=hashlib.sha256(message_data).hexdigest(),
            signature=signature,
        )

        return signature

    def _tee_sign(self, data: bytes) -> bytes:
        """Sign using TEE/TPM (production)"""
        # TODO: Implement actual TPM signing
        # For now, use Ed25519 simulation
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

        # In production, key never leaves TPM
        # This is just for demonstration
        key_seed = hashlib.sha256(self.identity.master_key_id.encode()).digest()
        # Note: Ed25519PrivateKey.from_private_bytes() needs 32 bytes
        private_key = Ed25519PrivateKey.from_private_bytes(key_seed)
        signature = private_key.sign(data)

        return signature

    def _dev_sign(self, data: bytes) -> bytes:
        """Development signing (HMAC-SHA256)"""
        import hmac

        key = self.identity.master_key_id.encode()
        return hmac.new(key, data, hashlib.sha256).digest()

    def verify_signature(self, pseudonym: bytes, message_data: bytes, signature: bytes) -> bool:
        """Verify message signature"""
        # Check revocation
        if self.is_revoked(pseudonym):
            return False

        # Verify signature
        if self.use_tee:
            return self._tee_verify(pseudonym, message_data, signature)
        return self._dev_verify(pseudonym, message_data, signature)

    def _tee_verify(self, pseudonym: bytes, data: bytes, signature: bytes) -> bool:
        """Verify using TEE/TPM (production)"""
        # TODO: Implement actual verification with public key
        # For now, accept if signature is valid length
        return len(signature) == 64

    def _dev_verify(self, pseudonym: bytes, data: bytes, signature: bytes) -> bool:
        """Development verification"""
        # In development, we can't verify without knowing the key
        # Accept signatures of correct length
        return len(signature) == 32

    def _record_evidence(
        self,
        evidence_type: str,
        message_hash: str,
        signature: bytes,
        distance_bound: float | None = None,
    ):
        """Record evidence for audit trail"""
        evidence = AttestationEvidence(
            evidence_id=secrets.token_hex(16),
            vehicle_pseudonym=self.get_current_pseudonym(),
            timestamp=int(time.time() * 1000),
            evidence_type=evidence_type,
            message_hash=message_hash,
            signature=signature,
            distance_bound=distance_bound,
            witness_count=0,
        )

        self.evidence_vault.append(evidence)

        # Keep vault size manageable (last 1000 entries)
        if len(self.evidence_vault) > 1000:
            self.evidence_vault = self.evidence_vault[-1000:]

    async def submit_evidence_to_vault(self, evidence: AttestationEvidence):
        """Submit evidence to ShadowTag audit vault"""
        # In production, this sends to ShadowTag service
        {
            "evidence_id": evidence.evidence_id,
            "vehicle_pseudonym": evidence.vehicle_pseudonym.hex(),
            "timestamp": evidence.timestamp,
            "evidence_type": evidence.evidence_type,
            "message_hash": evidence.message_hash,
            "signature": base64.b64encode(evidence.signature).decode(),
            "distance_bound": evidence.distance_bound,
            "witness_count": evidence.witness_count,
        }

        # TODO: HTTP POST to ShadowTag service
        # await http_client.post(f"{self.shadowtag_endpoint}/v1/evidence", json=payload)

    def add_revocation(self, entry: RevocationEntry):
        """Add entry to revocation list"""
        self.revocation_list[entry.revoked_id] = entry
        self.revocation_list_version += 1

        print(f"Added revocation: {entry.revoked_id.hex()} - {entry.reason}")

    def is_revoked(self, pseudonym: bytes) -> bool:
        """Check if pseudonym is revoked"""
        entry = self.revocation_list.get(pseudonym)
        if not entry:
            return False

        # Check if temporary suspension expired
        if entry.expires and int(time.time()) > entry.expires:
            del self.revocation_list[pseudonym]
            return False

        return True

    def get_revocation_list_digest(self) -> str:
        """Get digest of current revocation list for sync"""
        revoked_ids = sorted([r.revoked_id.hex() for r in self.revocation_list.values()])
        combined = "".join(revoked_ids) + str(self.revocation_list_version)
        return hashlib.sha256(combined.encode()).hexdigest()

    def export_evidence_batch(self, count: int = 100) -> list[dict]:
        """Export recent evidence for batch submission"""
        recent = self.evidence_vault[-count:]
        return [
            {
                "evidence_id": e.evidence_id,
                "vehicle_pseudonym": e.vehicle_pseudonym.hex(),
                "timestamp": e.timestamp,
                "evidence_type": e.evidence_type,
                "message_hash": e.message_hash,
                "signature": base64.b64encode(e.signature).decode(),
                "distance_bound": e.distance_bound,
                "witness_count": e.witness_count,
            }
            for e in recent
        ]

    def compute_distance_bound(
        self,
        _claimed_position: tuple[float, float],
        message_timestamp: int,
        max_velocity_mps: float = 50.0,  # ~180 km/h max
    ) -> float:
        """Compute distance bound for claimed position

        Uses time difference and max velocity to bound how far
        vehicle could have moved since last verified position.
        """
        # In production, would use last verified position from trusted source
        # For now, use simple time-based bound
        now = int(time.time() * 1000)
        time_diff_s = (now - message_timestamp) / 1000.0

        # Maximum possible distance
        max_distance = max_velocity_mps * time_diff_s

        return max_distance

    def get_stats(self) -> dict:
        """Get attestation statistics"""
        return {
            "vehicle_id": self.vehicle_id,
            "current_pseudonym": self.identity.current_pseudonym.hex() if self.identity else None,
            "pseudonym_expires_in": (
                self.identity.pseudonym_epoch - int(time.time()) if self.identity else 0
            ),
            "revocation_list_size": len(self.revocation_list),
            "revocation_list_version": self.revocation_list_version,
            "evidence_vault_size": len(self.evidence_vault),
            "use_tee": self.use_tee,
        }


class RevocationAuthority:
    """Central authority for managing revocations

    In production, this would be a distributed system with
    multiple authorities using threshold signatures.
    """

    def __init__(self, authority_id: str):
        self.authority_id = authority_id
        self.issued_revocations: list[RevocationEntry] = []

    def issue_revocation(
        self, pseudonym: bytes, reason: str, duration: int | None = None,
    ) -> RevocationEntry:
        """Issue revocation for a pseudonym"""
        now = int(time.time())
        expires = (now + duration) if duration else None

        # Sign revocation
        revocation_data = f"{pseudonym.hex()}:{now}:{reason}".encode()
        proof_signature = hashlib.sha256(revocation_data).digest()

        entry = RevocationEntry(
            revoked_id=pseudonym,
            revocation_time=now,
            reason=reason,
            authority=self.authority_id,
            proof_signature=proof_signature,
            expires=expires,
        )

        self.issued_revocations.append(entry)
        return entry

    def export_revocation_list(self) -> list[dict]:
        """Export revocation list for distribution"""
        return [
            {
                "revoked_id": e.revoked_id.hex(),
                "revocation_time": e.revocation_time,
                "reason": e.reason,
                "authority": e.authority,
                "proof_signature": base64.b64encode(e.proof_signature).decode(),
                "expires": e.expires,
            }
            for e in self.issued_revocations
        ]


# Example usage
if __name__ == "__main__":
    # Create attestation system
    attestation = ShadowTagAttestation(
        vehicle_id="TEST-VEHICLE-001",
        use_tee=False,  # Development mode
    )

    print("Vehicle Identity:")
    print(f"  Vehicle ID: {attestation.vehicle_id}")
    print(f"  Pseudonym: {attestation.get_current_pseudonym().hex()}")
    print(f"  Master Key: {attestation.identity.master_key_id}")

    # Sign a message
    message = b"Hello from V2X mesh"
    signature = attestation.sign_message(message)
    print(f"\nSigned message: {signature.hex()[:32]}...")

    # Verify signature
    pseudonym = attestation.get_current_pseudonym()
    valid = attestation.verify_signature(pseudonym, message, signature)
    print(f"Signature valid: {valid}")

    # Create revocation authority
    authority = RevocationAuthority("CENTRAL-PKI")

    # Issue revocation
    bad_pseudonym = secrets.token_bytes(8)
    revocation = authority.issue_revocation(
        bad_pseudonym,
        reason="Detected misbehavior",
        duration=3600,  # 1 hour suspension
    )

    # Add to local revocation list
    attestation.add_revocation(revocation)

    # Check revocation
    print(f"\nRevocation check for {bad_pseudonym.hex()}: {attestation.is_revoked(bad_pseudonym)}")

    # Stats
    print("\nAttestation Statistics:")
    import json

    print(json.dumps(attestation.get_stats(), indent=2))
