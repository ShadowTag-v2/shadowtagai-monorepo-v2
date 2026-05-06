# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

# Copyright 2026 ShadowTagAI. All rights reserved.
"""
Encryption — Item 12: AES-256-GCM encryption for sensitive KIs.

Encrypts the artifact content of SECRET-classified KIs while keeping
metadata (name, type, status, tags) readable.

Key derivation:
  - From MEMORY_ENCRYPTION_KEY env var (hex string or passphrase → PBKDF2)
"""

from __future__ import annotations

import base64
import hashlib
import os

# Use stdlib for PBKDF2, optional cryptography for AES-GCM
try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM

    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False


ENCRYPTION_KEY_ENV = "MEMORY_ENCRYPTION_KEY"
SALT = b"shadowtag-ki-engine-v1"  # Static salt for PBKDF2
NONCE_SIZE = 12  # AES-GCM standard nonce size


def _derive_key(passphrase: str) -> bytes:
    """Derive a 32-byte AES-256 key from a passphrase using PBKDF2.

    If the passphrase is a 64-char hex string, treat it as raw key.
    Otherwise, derive via PBKDF2-HMAC-SHA256.
    """
    # Check if it's already a hex key
    if len(passphrase) == 64:
        try:
            return bytes.fromhex(passphrase)
        except ValueError:
            pass  # Not hex, use PBKDF2

    return hashlib.pbkdf2_hmac(
        "sha256",
        passphrase.encode("utf-8"),
        SALT,
        iterations=100_000,
        dklen=32,
    )


def get_encryption_key() -> bytes | None:
    """Get the encryption key from environment.

    Returns None if not configured or cryptography not installed.
    """
    if not HAS_CRYPTO:
        return None

    key_str = os.environ.get(ENCRYPTION_KEY_ENV)
    if not key_str:
        return None

    return _derive_key(key_str)


def encrypt_content(plaintext: str, key: bytes | None = None) -> str:
    """Encrypt artifact content using AES-256-GCM.

    Args:
        plaintext: The content to encrypt.
        key: 32-byte AES key. If None, reads from environment.

    Returns:
        Base64-encoded ciphertext with format: "ENC:v1:{nonce}:{ciphertext}"

    Raises:
        RuntimeError: If encryption is not available or key is missing.
    """
    if not HAS_CRYPTO:
        raise RuntimeError("cryptography package not installed. Install with: pip install cryptography")

    if key is None:
        key = get_encryption_key()
    if key is None:
        raise RuntimeError(f"Encryption key not set. Set {ENCRYPTION_KEY_ENV} environment variable.")

    nonce = os.urandom(NONCE_SIZE)
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)

    nonce_b64 = base64.b64encode(nonce).decode("ascii")
    ct_b64 = base64.b64encode(ciphertext).decode("ascii")

    return f"ENC:v1:{nonce_b64}:{ct_b64}"


def decrypt_content(encrypted: str, key: bytes | None = None) -> str:
    """Decrypt AES-256-GCM encrypted content.

    Args:
        encrypted: Encrypted string in format "ENC:v1:{nonce}:{ciphertext}".
        key: 32-byte AES key. If None, reads from environment.

    Returns:
        Decrypted plaintext.

    Raises:
        RuntimeError: If decryption fails or key is missing.
        ValueError: If encrypted string format is invalid.
    """
    if not HAS_CRYPTO:
        raise RuntimeError("cryptography package not installed")

    if key is None:
        key = get_encryption_key()
    if key is None:
        raise RuntimeError(f"Encryption key not set. Set {ENCRYPTION_KEY_ENV} environment variable.")

    parts = encrypted.split(":")
    if len(parts) != 4 or parts[0] != "ENC" or parts[1] != "v1":
        raise ValueError("Invalid encrypted format. Expected 'ENC:v1:{nonce}:{ciphertext}'")

    nonce = base64.b64decode(parts[2])
    ciphertext = base64.b64decode(parts[3])

    aesgcm = AESGCM(key)
    plaintext = aesgcm.decrypt(nonce, ciphertext, None)

    return plaintext.decode("utf-8")


def is_encrypted(content: str) -> bool:
    """Check if content is encrypted."""
    return content.startswith("ENC:v1:")
