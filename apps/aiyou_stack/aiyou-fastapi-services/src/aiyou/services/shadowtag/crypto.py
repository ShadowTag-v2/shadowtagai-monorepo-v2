"""ShadowTag cryptographic service.

Implements Ed25519 signing and verification.
"""

import base64
import hashlib

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519


class CryptoService:
    """Cryptographic operations service."""

    @staticmethod
    def generate_key_pair() -> tuple[str, str]:
        """Generate a new Ed25519 key pair (private, public)."""
        private_key = ed25519.Ed25519PrivateKey.generate()
        public_key = private_key.public_key()

        private_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption(),
        )
        public_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw,
        )

        return (
            base64.b64encode(private_bytes).decode("utf-8"),
            base64.b64encode(public_bytes).decode("utf-8"),
        )

    @staticmethod
    def sign_payload(private_key_b64: str, payload: bytes) -> str:
        """Sign a payload with a private key."""
        private_bytes = base64.b64decode(private_key_b64)
        private_key = ed25519.Ed25519PrivateKey.from_private_bytes(private_bytes)

        signature = private_key.sign(payload)
        return base64.b64encode(signature).decode("utf-8")

    @staticmethod
    def verify_signature(public_key_b64: str, payload: bytes, signature_b64: str) -> bool:
        """Verify a signature with a public key."""
        try:
            public_bytes = base64.b64decode(public_key_b64)
            public_key = ed25519.Ed25519PublicKey.from_public_bytes(public_bytes)
            signature = base64.b64decode(signature_b64)

            public_key.verify(signature, payload)
            return True
        except (InvalidSignature, ValueError):
            return False

    @staticmethod
    def hash_payload(data: str) -> str:
        """Create SHA-512 hash of string data."""
        return hashlib.sha512(data.encode("utf-8")).hexdigest()


class ShadowTagVerifier:
    """High-level verifier for content attestation workflows.
    """

    def sign(self, payload: dict, private_key_bytes: bytes) -> dict:
        """Sign a structured payload using Ed25519.
        """
        import json
        import uuid

        # Canonicalize payload to ensure consistent signing
        payload_str = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        payload_actual_bytes = payload_str.encode("utf-8")

        # Ensure private key is string for CryptoService
        try:
            private_key_b64 = private_key_bytes.decode("utf-8")
        except AttributeError:
            private_key_b64 = str(private_key_bytes)

        # Sign
        signature = CryptoService.sign_payload(private_key_b64, payload_actual_bytes)

        return {
            "signature": signature,
            "id": str(uuid.uuid4()),  # Generate unique verification ID
            "timestamp": payload.get("timestamp"),
        }
