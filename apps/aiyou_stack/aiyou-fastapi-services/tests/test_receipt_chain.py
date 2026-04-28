# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Tests for receipt_chain module."""

import json
from unittest.mock import MagicMock, patch

import pytest
from hypothesis import given
from hypothesis import strategies as st
from shadowtag_v2.receipt_chain import (
    BlockchainConfig,
    ChainType,
    create_blockchain_receipt,
    prompt_hash,
    verify_blockchain_receipt,
)


class TestPromptHash:
    """Tests for prompt_hash function."""

    def test_deterministic(self):
        """Hash should be deterministic."""
        h1 = prompt_hash("test")
        h2 = prompt_hash("test")
        assert h1 == h2

    def test_hex_format(self):
        """Should return hex string."""
        h = prompt_hash("test")
        assert isinstance(h, str)
        assert len(h) == 64  # SHA-256 = 32 bytes = 64 hex chars

    def test_different_prompts(self):
        """Different prompts should produce different hashes."""
        h1 = prompt_hash("prompt A")
        h2 = prompt_hash("prompt B")
        assert h1 != h2

    @given(st.text(min_size=1))
    def test_property_consistency(self, prompt: str):
        """Hash should be consistent."""
        h1 = prompt_hash(prompt)
        h2 = prompt_hash(prompt)
        assert h1 == h2


class TestChainType:
    """Tests for ChainType enum."""

    def test_chain_types(self):
        """Should have expected chain types."""
        assert ChainType.POLYGON == "polygon"
        assert ChainType.ETHEREUM == "ethereum"
        assert ChainType.POLYGON_MUMBAI == "polygon-mumbai"
        assert ChainType.SEPOLIA == "sepolia"


class TestBlockchainConfig:
    """Tests for BlockchainConfig."""

    def test_default_config(self):
        """Should have sensible defaults."""
        config = BlockchainConfig()
        assert config.chain == ChainType.POLYGON
        assert config.gas_limit > 0
        assert ChainType.POLYGON in config.chain_id_map
        assert ChainType.POLYGON in config.rpc_url_map

    def test_custom_config(self):
        """Should allow custom configuration."""
        config = BlockchainConfig(
            chain=ChainType.ETHEREUM,
            gas_limit=100000,
            max_fee_gwei=50,
        )
        assert config.chain == ChainType.ETHEREUM
        assert config.gas_limit == 100000
        assert config.max_fee_gwei == 50

    def test_chain_id_mapping(self):
        """Should have correct chain IDs."""
        config = BlockchainConfig()
        assert config.chain_id_map[ChainType.POLYGON] == 137
        assert config.chain_id_map[ChainType.ETHEREUM] == 1
        assert config.chain_id_map[ChainType.POLYGON_MUMBAI] == 80001
        assert config.chain_id_map[ChainType.SEPOLIA] == 11155111


class TestCreateBlockchainReceipt:
    """Tests for create_blockchain_receipt function."""

    @patch("shadowtag_v2.receipt_chain.Web3")
    @patch("shadowtag_v2.receipt_chain.Account")
    def test_create_receipt_with_private_key(self, mock_account, mock_web3):
        """Should create receipt with private key."""
        # Setup mocks
        mock_w3_instance = MagicMock()
        mock_web3.return_value = mock_w3_instance
        mock_w3_instance.is_connected.return_value = True
        mock_w3_instance.eth.get_transaction_count.return_value = 0
        mock_w3_instance.eth.gas_price = 30000000000
        mock_w3_instance.to_wei.side_effect = lambda v, u: int(v * 1e9)

        mock_acct = MagicMock()
        mock_acct.address = "0x1234567890123456789012345678901234567890"
        mock_account.from_key.return_value = mock_acct

        signed_tx = MagicMock()
        signed_tx.rawTransaction = bytes.fromhex("abcd" * 16)
        mock_acct.sign_transaction.return_value = signed_tx

        mock_w3_instance.eth.send_raw_transaction.return_value = bytes.fromhex("1234" * 16)

        # Test
        config = BlockchainConfig(
            private_key="0x" + "a" * 64,
            chain=ChainType.POLYGON,
        )

        result = create_blockchain_receipt("test prompt", config)

        assert result["ok"] is True
        assert "tx_hash" in result
        assert "prompt_hash" in result
        assert result["chain"] == "polygon"
        assert "timestamp" in result

    def test_missing_credentials(self):
        """Should raise error if no credentials provided."""
        config = BlockchainConfig()

        with pytest.raises(ValueError, match="Must provide either private_key"):
            create_blockchain_receipt("test", config)

    @patch("shadowtag_v2.receipt_chain.Web3")
    def test_connection_failure(self, mock_web3):
        """Should raise error if cannot connect to RPC."""
        mock_w3_instance = MagicMock()
        mock_web3.return_value = mock_w3_instance
        mock_w3_instance.is_connected.return_value = False

        config = BlockchainConfig(private_key="0x" + "a" * 64)

        with pytest.raises(Exception, match="Cannot connect"):
            create_blockchain_receipt("test", config)

    @patch("shadowtag_v2.receipt_chain._get_private_key_from_gcp")
    @patch("shadowtag_v2.receipt_chain.Web3")
    @patch("shadowtag_v2.receipt_chain.Account")
    def test_create_receipt_with_gcp_secret(self, mock_account, mock_web3, mock_gcp_secret):
        """Should create receipt with GCP Secret Manager."""
        # Mock GCP secret retrieval
        mock_gcp_secret.return_value = "0x" + "b" * 64

        # Setup Web3 mocks
        mock_w3_instance = MagicMock()
        mock_web3.return_value = mock_w3_instance
        mock_w3_instance.is_connected.return_value = True
        mock_w3_instance.eth.get_transaction_count.return_value = 0
        mock_w3_instance.eth.gas_price = 30000000000
        mock_w3_instance.to_wei.side_effect = lambda v, u: int(v * 1e9)

        mock_acct = MagicMock()
        mock_acct.address = "0xabcd"
        mock_account.from_key.return_value = mock_acct

        signed_tx = MagicMock()
        signed_tx.rawTransaction = bytes.fromhex("abcd" * 16)
        mock_acct.sign_transaction.return_value = signed_tx

        mock_w3_instance.eth.send_raw_transaction.return_value = bytes.fromhex("5678" * 16)

        # Test
        config = BlockchainConfig(
            gcp_secret_name="blockchain-key",
            gcp_project_id="test-project",
        )

        result = create_blockchain_receipt("test", config)

        assert result["ok"] is True
        mock_gcp_secret.assert_called_once_with("blockchain-key", "test-project")


class TestVerifyBlockchainReceipt:
    """Tests for verify_blockchain_receipt function."""

    @patch("shadowtag_v2.receipt_chain.Web3")
    def test_verify_receipt_success(self, mock_web3):
        """Should verify receipt successfully."""
        prompt = "test prompt"
        phash = prompt_hash(prompt)

        # Mock transaction data
        receipt_data = {
            "prompt_hash": phash,
            "timestamp": "2025-01-01T00:00:00+00:00",
            "chain": "polygon",
        }
        tx_data = json.dumps(receipt_data, separators=(",", ":"))

        mock_w3_instance = MagicMock()
        mock_web3.return_value = mock_w3_instance
        mock_w3_instance.is_connected.return_value = True

        mock_tx = {
            "input": "0x" + tx_data.encode("utf-8").hex(),
            "blockNumber": 12345,
        }
        mock_w3_instance.eth.get_transaction.return_value = mock_tx

        mock_block = {"timestamp": 1704067200}
        mock_w3_instance.eth.get_block.return_value = mock_block

        # Test
        config = BlockchainConfig()
        result = verify_blockchain_receipt("0xabcd", prompt, config)

        assert result["ok"] is True
        assert result["verified"] is True
        assert result["expected_hash"] == phash
        assert result["stored_hash"] == phash

    @patch("shadowtag_v2.receipt_chain.Web3")
    def test_verify_receipt_mismatch(self, mock_web3):
        """Should detect hash mismatch."""
        wrong_hash = prompt_hash("wrong prompt")

        receipt_data = {
            "prompt_hash": wrong_hash,
            "timestamp": "2025-01-01T00:00:00+00:00",
        }
        tx_data = json.dumps(receipt_data)

        mock_w3_instance = MagicMock()
        mock_web3.return_value = mock_w3_instance
        mock_w3_instance.is_connected.return_value = True

        mock_tx = {
            "input": "0x" + tx_data.encode("utf-8").hex(),
            "blockNumber": 12345,
        }
        mock_w3_instance.eth.get_transaction.return_value = mock_tx

        mock_block = {"timestamp": 1704067200}
        mock_w3_instance.eth.get_block.return_value = mock_block

        config = BlockchainConfig()
        result = verify_blockchain_receipt("0xabcd", "correct prompt", config)

        assert result["ok"] is True
        assert result["verified"] is False

    @patch("shadowtag_v2.receipt_chain.Web3")
    def test_invalid_transaction_data(self, mock_web3):
        """Should handle invalid transaction data."""
        mock_w3_instance = MagicMock()
        mock_web3.return_value = mock_w3_instance
        mock_w3_instance.is_connected.return_value = True

        mock_tx = {
            "input": "0x123456",  # Invalid JSON
            "blockNumber": 12345,
        }
        mock_w3_instance.eth.get_transaction.return_value = mock_tx

        config = BlockchainConfig()
        result = verify_blockchain_receipt("0xabcd", "test", config)

        assert result["ok"] is False
        assert result["verified"] is False
        assert "error" in result


class TestGCPSecretIntegration:
    """Tests for GCP Secret Manager integration."""

    @patch("shadowtag_v2.receipt_chain.secretmanager")
    def test_get_private_key_from_gcp(self, mock_secretmanager):
        """Should retrieve private key from GCP."""
        from shadowtag_v2.receipt_chain import _get_private_key_from_gcp

        # Mock GCP client
        mock_client = MagicMock()
        mock_secretmanager.SecretManagerServiceClient.return_value = mock_client

        mock_response = MagicMock()
        mock_response.payload.data = b"0xabcdef123456"
        mock_client.access_secret_version.return_value = mock_response

        # Test
        key = _get_private_key_from_gcp("test-secret", "test-project")

        assert key == "0xabcdef123456"
        mock_client.access_secret_version.assert_called_once()

    def test_missing_gcp_library(self):
        """Should raise error if google-cloud-secret-manager not installed."""
        from shadowtag_v2.receipt_chain import _get_private_key_from_gcp

        with patch.dict("sys.modules", {"google.cloud": None}):  # noqa: SIM117
            with pytest.raises(ImportError, match="google-cloud-secret-manager required"):
                _get_private_key_from_gcp("test", "project")
