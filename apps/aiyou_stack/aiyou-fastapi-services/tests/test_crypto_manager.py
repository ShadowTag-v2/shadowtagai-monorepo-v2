"""Tests for GPTRAM Encryption Key Management
"""

import os
import sys
import tempfile
from pathlib import Path

import pytest

# Add tools directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))

from crypto_manager import KeyManager, get_key_manager


class TestKeyManager:
    """Test suite for KeyManager class"""

    def test_key_generation(self):
        """Test that generated keys are 256-bit (32 bytes)"""
        km = KeyManager()
        key = km._generate_key()

        assert len(key) == 32
        assert isinstance(key, bytes)

    def test_key_derivation(self):
        """Test PBKDF2 key derivation for SQLCipher"""
        km = KeyManager()
        master_key = b"test_master_key_12345678901234567890"  # 32 bytes

        db_key = km.derive_db_key(master_key)

        # SQLCipher expects hex string
        assert isinstance(db_key, str)
        # PBKDF2-HMAC-SHA256 with 32-byte output = 64 hex chars
        assert len(db_key) == 64
        # Should be valid hex
        int(db_key, 16)

    def test_key_derivation_deterministic(self):
        """Test that key derivation is deterministic"""
        km = KeyManager()
        master_key = b"test_key"

        db_key1 = km.derive_db_key(master_key)
        db_key2 = km.derive_db_key(master_key)

        assert db_key1 == db_key2

    def test_different_keys_produce_different_db_keys(self):
        """Test that different master keys produce different DB keys"""
        km = KeyManager()

        key1 = b"key1" + b"0" * 28
        key2 = b"key2" + b"0" * 28

        db_key1 = km.derive_db_key(key1)
        db_key2 = km.derive_db_key(key2)

        assert db_key1 != db_key2

    def test_get_or_create_key_with_env_var(self):
        """Test key retrieval from environment variable"""
        test_key = "test_key_hex_value"
        os.environ["GPTRAM_ENCRYPTION_KEY"] = test_key

        try:
            km = KeyManager()
            key = km.get_or_create_key()

            assert key == test_key.encode("utf-8")
        finally:
            del os.environ["GPTRAM_ENCRYPTION_KEY"]

    def test_key_rotation(self):
        """Test key rotation produces new key"""
        km = KeyManager()

        # Create initial key
        old_key = km.get_or_create_key()

        # Rotate key
        rotated_old, new_key = km.rotate_key()

        # Old key from rotation should match initial key
        assert rotated_old == old_key
        # New key should be different
        assert new_key != old_key
        # Both should be 32 bytes
        assert len(old_key) == 32
        assert len(new_key) == 32

    def test_file_fallback_storage(self):
        """Test key storage in file when keyring unavailable"""
        with tempfile.TemporaryDirectory() as tmpdir:
            key_path = os.path.join(tmpdir, ".test_key")
            km = KeyManager()

            test_key = b"0123456789ABCDEF0123456789ABCDEF"  # 32 bytes
            km._store_in_file(test_key, key_path)

            # Verify file exists
            assert os.path.exists(key_path)

            # Verify permissions (0600 = read/write owner only)
            file_stat = os.stat(key_path)
            permissions = oct(file_stat.st_mode)[-3:]
            assert permissions == "600"

            # Verify content
            stored_key = Path(key_path).read_bytes()
            assert stored_key == test_key

    def test_get_key_manager_factory(self):
        """Test factory function returns KeyManager instance"""
        km = get_key_manager()
        assert isinstance(km, KeyManager)

    def test_vault_configuration(self):
        """Test KeyManager initializes with Vault configuration"""
        vault_addr = "https://vault.example.com:8200"
        km = KeyManager(vault_addr=vault_addr)

        assert km.vault_addr == vault_addr

    def test_key_caching(self):
        """Test that key is cached after first retrieval"""
        os.environ["GPTRAM_ENCRYPTION_KEY"] = "cached_test_key"

        try:
            km = KeyManager()

            # First call
            key1 = km.get_or_create_key()
            # Second call (should use cache)
            key2 = km.get_or_create_key()

            assert key1 is key2  # Same object reference (cached)
        finally:
            del os.environ["GPTRAM_ENCRYPTION_KEY"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
