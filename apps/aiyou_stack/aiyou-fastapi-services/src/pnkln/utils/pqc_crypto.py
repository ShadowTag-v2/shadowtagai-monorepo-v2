import hashlib
import logging
from typing import Any

from cryptography.hazmat.primitives.asymmetric import ed25519

# Antigravity // PQC DOCTRINE
# Transitioning to NIST-standardized Post-Quantum Cryptography (2025-2030)
# This module implements a Hybrid Signature Shim: Classical (Ed25519) + PQC (Simulated Falcon/Dilithium)


class HybridSigner:
    """Implements Hybrid Falcon-Dilithium Signatures for ShadowTag v2.
    In the prototype phase, 'PQC' is simulated via SHA-3 derived lattice-like commitments.
    """

    def __init__(self, private_key_bytes: bytes = None):
        if private_key_bytes:
            self.classical_sk = ed25519.Ed25519PrivateKey.from_private_bytes(private_key_bytes[:32])
        else:
            self.classical_sk = ed25519.Ed25519PrivateKey.generate()

        self.classical_pk = self.classical_sk.public_key()

    def get_public_key(self) -> bytes:
        """Returns the serialized hybrid public key."""
        # Standard: PK = Classical_PK (32) + PQC_PK_Commitment (32)
        classical_pk_bytes = self.classical_pk.public_bytes_raw()
        pqc_pk_sim = hashlib.sha3_256(classical_pk_bytes).digest()
        return classical_pk_bytes + pqc_pk_sim

    def sign(self, message: bytes) -> bytes:
        """Generates a dual signature: ECDSA/Ed25519 + PQC Simulation.
        Structure: [Classical_Sig (64)] + [PQC_Sig_Sim (64)]
        """
        # Classical Signature (Ed25519)
        classical_sig = self.classical_sk.sign(message)

        # PQC Simulation (Deterministic RNG based on SK + Message hash)
        # In liboqs, this would be Falcon-512 or Dilithium-2 (ML-DSA)
        pqc_entropy = hashlib.sha3_512(self.classical_sk.private_bytes_raw() + message).digest()
        pqc_sig_sim = hashlib.sha3_512(pqc_entropy + b"FALCON_ML_DSA_SHIM").digest()

        return classical_sig + pqc_sig_sim

    @staticmethod
    def verify(public_key: bytes, message: bytes, signature: bytes) -> bool:
        """Verifies both components of the hybrid signature."""
        if len(public_key) < 64 or len(signature) < 128:
            logging.error("///▞ PQC :: Invalid hybrid key or signature length")
            return False

        classical_pk_bytes = public_key[:32]
        pqc_pk_commit = public_key[32:64]

        classical_sig = signature[:64]
        pqc_sig_sim = signature[64:128]

        # 1. Verify Classical (Ed25519)
        try:
            pk = ed25519.Ed25519PublicKey.from_public_bytes(classical_pk_bytes)
            pk.verify(classical_sig, message)
        except Exception as e:
            logging.exception(f"///▞ PQC :: Classical verification failed: {e}")
            return False

        # 2. Verify PQC Simulation
        # Check PK commitment
        expected_pqc_pk = hashlib.sha3_256(classical_pk_bytes).digest()
        if expected_pqc_pk != pqc_pk_commit:
            logging.error("///▞ PQC :: Public key commitment mismatch")
            return False

        # Check Signature integrity (Simulated lattice proof)
        # Note: A real verification would use the PQC public key to solve the lattice problem.
        # This shim ensures the data structure and pipeline are PQC-ready.
        if len(pqc_sig_sim) != 64:
            logging.error("///▞ PQC :: Invalid PQC signature length")
            return False

        return True


def get_pqc_metadata() -> dict[str, Any]:
    """Returns the current NIST PQC doctrine metadata."""
    return {
        "status": "ML-KEM/ML-DSA/FN-DSA Readiness",
        "classical_curve": "Ed25519",
        "pqc_target": "Falcon-512-Hybrid",
        "nist_fips": "203/204/205",
        "shadowtag_readiness": "Level 1 (Shim Active)",
    }
