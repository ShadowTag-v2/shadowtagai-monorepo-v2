# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
ShadowTag - DCT Watermarking & Cryptographic Audit Trail

Applies cryptographic watermarks to all outputs for:
1. Provenance tracking
2. Tamper detection
3. Audit compliance
4. Attribution

Uses ed25519 signatures and Merkle tree hashing for cryptographic
integrity verification.
"""

import hashlib
import json
from typing import Any
from dataclasses import dataclass, field
from datetime import datetime
from Crypto.PublicKey import ECC
from Crypto.Signature import eddsa
from Crypto.Hash import SHA256


@dataclass
class Watermark:
    """Cryptographic watermark."""

    content: str
    metadata: dict[str, Any]
    signature: str
    merkle_root: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "content": self.content,
            "metadata": self.metadata,
            "signature": self.signature,
            "merkle_root": self.merkle_root,
            "timestamp": self.timestamp,
        }

    def verify(self, public_key: ECC.EccKey) -> bool:
        """Verify watermark signature."""
        try:
            # Reconstruct message
            message = self._construct_message()
            h = SHA256.new(message.encode())

            # Parse signature
            sig_bytes = bytes.fromhex(self.signature.split(":")[1])

            # Verify
            verifier = eddsa.new(public_key, "rfc8032")
            verifier.verify(h, sig_bytes)
            return True
        except:
            return False

    def _construct_message(self) -> str:
        """Construct message for signing."""
        return json.dumps({"content": self.content, "metadata": self.metadata, "timestamp": self.timestamp}, sort_keys=True)


class ShadowTag:
    """
    ShadowTag watermarking system.

    Applies cryptographic watermarks to all outputs for audit trail
    and tamper detection.

    Example:
        ```python
        shadowtag = ShadowTag()

        watermarked = shadowtag.watermark(
            content="AI generated report",
            metadata={'task': 'research', 'model': 'gemini-2.0'}
        )

        # Verify later
        is_valid = shadowtag.verify(watermarked)
        ```
    """

    def __init__(self, key_path: str | None = None):
        """
        Initialize ShadowTag.

        Args:
            key_path: Path to ed25519 private key (generates new if not provided)
        """
        self.key_path = key_path

        # Generate or load key
        if key_path and os.path.exists(key_path):
            self._load_key(key_path)
        else:
            self._generate_key()

        self.watermarks: list[Watermark] = []

    def _generate_key(self):
        """Generate new ed25519 key pair."""
        self.private_key = ECC.generate(curve="Ed25519")
        self.public_key = self.private_key.public_key()

    def _load_key(self, path: str):
        """Load key from file."""
        with open(path, "rb") as f:
            self.private_key = ECC.import_key(f.read())
            self.public_key = self.private_key.public_key()

    def save_key(self, path: str):
        """Save private key to file."""
        import os

        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(self.private_key.export_key(format="PEM").encode())

    def watermark(self, content: str, metadata: dict[str, Any]) -> str:
        """
        Apply cryptographic watermark to content.

        Args:
            content: Content to watermark
            metadata: Metadata to include in watermark

        Returns:
            Original content (watermark stored separately)
        """
        # Create watermark object
        watermark = Watermark(
            content=content, metadata=metadata, signature=self._sign(content, metadata), merkle_root=self._compute_merkle_root(content, metadata)
        )

        # Store watermark
        self.watermarks.append(watermark)

        # Return original content (watermark is stored separately)
        return content

    def _sign(self, content: str, metadata: dict[str, Any]) -> str:
        """
        Sign content with ed25519.

        Returns:
            Signature in format "ed25519:<hex>"
        """
        # Construct message
        message = json.dumps({"content": content, "metadata": metadata, "timestamp": datetime.now().isoformat()}, sort_keys=True)

        # Hash message
        h = SHA256.new(message.encode())

        # Sign
        signer = eddsa.new(self.private_key, "rfc8032")
        signature = signer.sign(h)

        return f"ed25519:{signature.hex()}"

    def _compute_merkle_root(self, content: str, metadata: dict[str, Any]) -> str:
        """
        Compute Merkle tree root hash.

        Returns:
            Merkle root in format "sha256:<hex>"
        """
        # Simple Merkle tree (single leaf for demo)
        # In production, build full tree from content chunks
        message = json.dumps({"content": content, "metadata": metadata, "timestamp": datetime.now().isoformat()}, sort_keys=True)

        h = hashlib.sha256(message.encode()).hexdigest()
        return f"sha256:{h}"

    def verify(self, watermark: Watermark) -> bool:
        """
        Verify watermark integrity.

        Args:
            watermark: Watermark to verify

        Returns:
            True if valid, False otherwise
        """
        return watermark.verify(self.public_key)

    def get_watermark_for_content(self, content: str) -> Watermark | None:
        """
        Retrieve watermark for specific content.

        Args:
            content: Content to find watermark for

        Returns:
            Watermark if found, None otherwise
        """
        for wm in self.watermarks:
            if wm.content == content:
                return wm
        return None

    def export_audit_trail(self) -> List[dict[str, Any]]:
        """
        Export full audit trail.

        Returns:
            List of all watermarks as dictionaries
        """
        return [wm.to_dict() for wm in self.watermarks]


# Import os for key path handling
import os
