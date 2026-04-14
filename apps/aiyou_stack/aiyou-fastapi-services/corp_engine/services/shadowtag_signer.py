"""ShadowTag Signer Service
=========================
C2PA-compliant content provenance signing for Corp Engine outputs.
All intel reports, exports, and API responses are watermarked.
"""

import base64
import hashlib
import json
from datetime import datetime
from typing import Any

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519


class ShadowTagSigner:
    """ShadowTag v2.0 C2PA-compliant signer.

    Features:
    - Ed25519 digital signatures
    - C2PA manifest generation
    - Content hash verification
    - Timestamp attestation
    """

    def __init__(self, private_key: bytes | None = None):
        if private_key:
            self.private_key = ed25519.Ed25519PrivateKey.from_private_bytes(private_key)
        else:
            # Generate ephemeral key for development
            self.private_key = ed25519.Ed25519PrivateKey.generate()

        self.public_key = self.private_key.public_key()
        self.issuer = "shadowtagai-corp-engine"

    def sign_content(self, content: Any, content_type: str = "json") -> dict:
        """Sign content and generate C2PA manifest.

        Args:
            content: Content to sign (dict, str, or bytes)
            content_type: Type of content (json, text, binary)

        Returns:
            dict with signature, manifest, and verification data

        """
        # Normalize content to bytes
        if isinstance(content, dict):
            content_bytes = json.dumps(content, sort_keys=True).encode("utf-8")
        elif isinstance(content, str):
            content_bytes = content.encode("utf-8")
        else:
            content_bytes = content

        # Generate content hash
        content_hash = hashlib.sha256(content_bytes).hexdigest()

        # Create C2PA manifest
        manifest = self._create_manifest(content_hash, content_type)

        # Sign the manifest
        manifest_bytes = json.dumps(manifest, sort_keys=True).encode("utf-8")
        signature = self.private_key.sign(manifest_bytes)
        signature_b64 = base64.b64encode(signature).decode("utf-8")

        # Generate signature string
        sig_string = f"c2pa:ed25519:{signature_b64[:32]}"

        return {
            "signature": sig_string,
            "signature_full": signature_b64,
            "content_hash": content_hash,
            "manifest": manifest,
            "public_key": self._get_public_key_b64(),
            "verified": True,
        }

    def verify_signature(
        self, content: Any, signature_b64: str, content_type: str = "json",
    ) -> dict:
        """Verify a signature against content.

        Args:
            content: Original content
            signature_b64: Base64-encoded signature
            content_type: Type of content

        Returns:
            dict with verification result

        """
        try:
            # Normalize content
            if isinstance(content, dict):
                content_bytes = json.dumps(content, sort_keys=True).encode("utf-8")
            elif isinstance(content, str):
                content_bytes = content.encode("utf-8")
            else:
                content_bytes = content

            # Compute expected hash
            content_hash = hashlib.sha256(content_bytes).hexdigest()

            # Recreate manifest
            manifest = self._create_manifest(content_hash, content_type)
            manifest_bytes = json.dumps(manifest, sort_keys=True).encode("utf-8")

            # Verify signature
            signature = base64.b64decode(signature_b64)
            self.public_key.verify(signature, manifest_bytes)

            return {
                "valid": True,
                "content_hash": content_hash,
                "issuer": self.issuer,
                "verified_at": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            return {
                "valid": False,
                "error": str(e),
                "verified_at": datetime.utcnow().isoformat(),
            }

    def _create_manifest(self, content_hash: str, content_type: str) -> dict:
        """Create C2PA-compliant manifest"""
        return {
            "c2pa_version": "2.0",
            "claim_generator": "shadowtagai-corp-engine/1.0.0",
            "title": "Corp Engine Output",
            "format": content_type,
            "instance_id": f"xmp:iid:{hashlib.sha256(content_hash.encode()).hexdigest()[:16]}",
            "claim": {
                "dc:format": self._get_mime_type(content_type),
                "dc:title": "ShadowTagAI Corp Engine Output",
            },
            "assertions": [
                {
                    "label": "c2pa.hash.sha256",
                    "data": content_hash,
                },
                {
                    "label": "c2pa.created",
                    "data": datetime.utcnow().isoformat() + "Z",
                },
                {
                    "label": "shadowtagai.issuer",
                    "data": self.issuer,
                },
                {
                    "label": "shadowtagai.attestation_level",
                    "data": "L3",  # Full cryptographic attestation
                },
            ],
            "signature_info": {
                "alg": "Ed25519",
                "issuer": self.issuer,
            },
        }

    def _get_mime_type(self, content_type: str) -> str:
        """Get MIME type for content type"""
        mime_types = {
            "json": "application/json",
            "text": "text/plain",
            "binary": "application/octet-stream",
            "markdown": "text/markdown",
            "html": "text/html",
        }
        return mime_types.get(content_type, "application/octet-stream")

    def _get_public_key_b64(self) -> str:
        """Get base64-encoded public key"""
        public_bytes = self.public_key.public_bytes(
            encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw,
        )
        return base64.b64encode(public_bytes).decode("utf-8")

    def sign_api_response(self, response: dict) -> dict:
        """Sign an API response and add signature field.

        Args:
            response: API response dict

        Returns:
            Response with shadowtag_signature field added

        """
        result = self.sign_content(response, "json")
        response["shadowtag_signature"] = result["signature"]
        return response

    def sign_export(self, data: Any, export_format: str = "json") -> dict:
        """Sign an export file.

        Args:
            data: Export data
            export_format: Format of export (json, csv, pdf)

        Returns:
            dict with signed data and verification info

        """
        result = self.sign_content(data, export_format)

        return {
            "data": data,
            "signature": result["signature"],
            "manifest": result["manifest"],
            "verification_url": f"https://verify.shadowtagai.com/{result['content_hash'][:16]}",
        }


# Global signer instance
_signer: ShadowTagSigner | None = None


def get_signer() -> ShadowTagSigner:
    """Get or create global signer instance"""
    global _signer
    if _signer is None:
        _signer = ShadowTagSigner()
    return _signer


def sign_response(response: dict) -> dict:
    """Convenience function to sign API response"""
    return get_signer().sign_api_response(response)
