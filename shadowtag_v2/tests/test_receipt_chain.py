# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Tests for receipt_chain module
"""

from datetime import datetime
from pathlib import Path
import tempfile

from shadowtag_v2.receipt_chain import (
    ReceiptChain,
    Receipt,
    Block,
    ChainVerifier,
    ChainStorage,
)


class TestReceipt:
    """Tests for Receipt"""

    def test_receipt_creation(self):
        """Test creating a receipt"""
        receipt = Receipt(
            operation_id="test_op_001",
            operation_type="encode",
            timestamp=datetime.utcnow().isoformat(),
            media_type="video",
            method="lsb",
            payload_hash="a" * 64,
            media_hash="b" * 64,
        )

        assert receipt.operation_id == "test_op_001"
        assert receipt.operation_type == "encode"

    def test_receipt_hash(self):
        """Test receipt hash calculation"""
        receipt = Receipt(
            operation_id="test_op_001",
            operation_type="encode",
            timestamp="2024-01-01T00:00:00",
            media_type="video",
            method="lsb",
            payload_hash="a" * 64,
            media_hash="b" * 64,
        )

        hash1 = receipt.hash()
        hash2 = receipt.hash()

        # Hash should be deterministic
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA-256 hex

    def test_receipt_serialization(self):
        """Test receipt to_dict and from_dict"""
        receipt = Receipt(
            operation_id="test_op_001",
            operation_type="encode",
            timestamp="2024-01-01T00:00:00",
            media_type="video",
            method="lsb",
            payload_hash="a" * 64,
            media_hash="b" * 64,
        )

        # Serialize
        data = receipt.to_dict()
        assert isinstance(data, dict)

        # Deserialize
        recovered = Receipt.from_dict(data)
        assert recovered.operation_id == receipt.operation_id
        assert recovered.payload_hash == receipt.payload_hash


class TestBlock:
    """Tests for Block"""

    def test_genesis_block_creation(self):
        """Test creating genesis block"""
        receipt = Receipt(
            operation_id="genesis",
            operation_type="init",
            timestamp=datetime.utcnow().isoformat(),
            media_type="none",
            method="none",
            payload_hash="0" * 64,
            media_hash="0" * 64,
        )

        block = Block.create_genesis(receipt)

        assert block.header.index == 0
        assert block.header.previous_hash == "0" * 64
        assert block.verify()

    def test_block_hash_deterministic(self):
        """Test block hash is deterministic"""
        receipt = Receipt(
            operation_id="test",
            operation_type="encode",
            timestamp="2024-01-01T00:00:00",
            media_type="video",
            method="lsb",
            payload_hash="a" * 64,
            media_hash="b" * 64,
        )

        block = Block.create_genesis(receipt)

        hash1 = block.hash()
        hash2 = block.hash()

        assert hash1 == hash2

    def test_block_chain_linkage(self):
        """Test blocks link correctly"""
        receipt1 = Receipt(
            operation_id="op1",
            operation_type="encode",
            timestamp=datetime.utcnow().isoformat(),
            media_type="video",
            method="lsb",
            payload_hash="a" * 64,
            media_hash="b" * 64,
        )

        receipt2 = Receipt(
            operation_id="op2",
            operation_type="decode",
            timestamp=datetime.utcnow().isoformat(),
            media_type="video",
            method="lsb",
            payload_hash="c" * 64,
            media_hash="d" * 64,
        )

        block1 = Block.create_genesis(receipt1)
        block2 = Block.create_next(receipt2, block1, 1)

        assert block2.header.previous_hash == block1.hash()
        assert block2.header.index == 1


class TestReceiptChain:
    """Tests for ReceiptChain"""

    def test_chain_initialization(self):
        """Test chain initializes with genesis block"""
        chain = ReceiptChain()

        assert len(chain) == 1
        assert chain[0].receipt.operation_type == "init"

    def test_add_receipt(self):
        """Test adding receipts to chain"""
        chain = ReceiptChain()

        receipt = Receipt(
            operation_id="op1",
            operation_type="encode",
            timestamp=datetime.utcnow().isoformat(),
            media_type="video",
            method="lsb",
            payload_hash="a" * 64,
            media_hash="b" * 64,
        )

        block = chain.add_receipt(receipt)

        assert len(chain) == 2
        assert block.header.index == 1
        assert chain.verify_chain()

    def test_chain_verification(self):
        """Test chain verification"""
        chain = ReceiptChain()

        # Add several receipts
        for i in range(5):
            receipt = Receipt(
                operation_id=f"op{i}",
                operation_type="encode",
                timestamp=datetime.utcnow().isoformat(),
                media_type="video",
                method="lsb",
                payload_hash="a" * 64,
                media_hash="b" * 64,
            )
            chain.add_receipt(receipt)

        # Chain should be valid
        assert chain.verify_chain()

        # Tamper with a block
        chain.blocks[2].receipt.payload_hash = "tampered" * 8

        # Chain should now be invalid
        assert not chain.blocks[2].verify()

    def test_get_receipt(self):
        """Test retrieving receipt by operation ID"""
        chain = ReceiptChain()

        receipt = Receipt(
            operation_id="unique_op",
            operation_type="encode",
            timestamp=datetime.utcnow().isoformat(),
            media_type="video",
            method="lsb",
            payload_hash="a" * 64,
            media_hash="b" * 64,
        )

        chain.add_receipt(receipt)

        # Retrieve
        found = chain.get_receipt("unique_op")
        assert found is not None
        assert found.operation_id == "unique_op"

        # Non-existent
        not_found = chain.get_receipt("nonexistent")
        assert not_found is None

    def test_chain_export_import(self):
        """Test exporting and importing chain"""
        chain = ReceiptChain()

        # Add some receipts
        for i in range(3):
            receipt = Receipt(
                operation_id=f"op{i}",
                operation_type="encode",
                timestamp=datetime.utcnow().isoformat(),
                media_type="video",
                method="lsb",
                payload_hash="a" * 64,
                media_hash="b" * 64,
            )
            chain.add_receipt(receipt)

        # Export
        json_str = chain.export_to_json()
        assert isinstance(json_str, str)

        # Import
        imported_chain = ReceiptChain.import_from_json(json_str)
        assert len(imported_chain) == len(chain)
        assert imported_chain.chain_id == chain.chain_id
        assert imported_chain.verify_chain()


class TestChainVerifier:
    """Tests for ChainVerifier"""

    def test_verify_valid_chain(self):
        """Test verifying a valid chain"""
        chain = ReceiptChain()

        for i in range(3):
            receipt = Receipt(
                operation_id=f"op{i}",
                operation_type="encode",
                timestamp=datetime.utcnow().isoformat(),
                media_type="video",
                method="lsb",
                payload_hash="a" * 64,
                media_hash="b" * 64,
            )
            chain.add_receipt(receipt)

        verifier = ChainVerifier()
        result = verifier.verify_chain(chain)

        assert result.is_valid
        assert len(result.errors) == 0

    def test_verify_receipt_pair(self):
        """Test verifying encode/decode receipt pair"""
        encode_receipt = Receipt(
            operation_id="encode_op",
            operation_type="encode",
            timestamp=datetime.utcnow().isoformat(),
            media_type="video",
            method="lsb",
            payload_hash="a" * 64,
            media_hash="b" * 64,
        )

        decode_receipt = Receipt(
            operation_id="decode_op",
            operation_type="decode",
            timestamp=datetime.utcnow().isoformat(),
            media_type="video",
            method="lsb",
            payload_hash="a" * 64,  # Same payload
            media_hash="b" * 64,  # Same media
        )

        verifier = ChainVerifier()
        is_valid, errors = verifier.verify_receipt_pair(encode_receipt, decode_receipt)

        assert is_valid
        assert len(errors) == 0


class TestChainStorage:
    """Tests for ChainStorage"""

    def test_storage_initialization(self):
        """Test storage initializes correctly"""
        with ChainStorage() as storage:
            assert storage.conn is not None

    def test_save_and_load_chain(self):
        """Test saving and loading chain"""
        chain = ReceiptChain()

        # Add receipt
        receipt = Receipt(
            operation_id="op1",
            operation_type="encode",
            timestamp=datetime.utcnow().isoformat(),
            media_type="video",
            method="lsb",
            payload_hash="a" * 64,
            media_hash="b" * 64,
        )
        chain.add_receipt(receipt)

        with ChainStorage() as storage:
            # Save
            storage.save_chain(chain)

            # Load
            loaded = storage.load_chain(chain.chain_id)
            assert loaded is not None
            assert len(loaded) == len(chain)
            assert loaded.chain_id == chain.chain_id

    def test_list_chains(self):
        """Test listing all chains"""
        with ChainStorage() as storage:
            # Create and save multiple chains
            for i in range(3):
                chain = ReceiptChain()
                storage.save_chain(chain)

            # List
            chains = storage.list_chains()
            assert len(chains) >= 3

    def test_search_receipts(self):
        """Test searching for receipts"""
        chain = ReceiptChain()

        receipt = Receipt(
            operation_id="searchable_op",
            operation_type="encode",
            timestamp=datetime.utcnow().isoformat(),
            media_type="audio",
            method="phase",
            payload_hash="a" * 64,
            media_hash="b" * 64,
        )
        chain.add_receipt(receipt)

        with ChainStorage() as storage:
            storage.save_chain(chain)

            # Search by operation_id
            results = storage.search_receipts(operation_id="searchable_op")
            assert len(results) == 1
            assert results[0]["operation_id"] == "searchable_op"

            # Search by media_type
            results = storage.search_receipts(media_type="audio")
            assert len(results) >= 1

    def test_export_import_file(self):
        """Test exporting and importing chain to/from file"""
        chain = ReceiptChain()

        receipt = Receipt(
            operation_id="op1",
            operation_type="encode",
            timestamp=datetime.utcnow().isoformat(),
            media_type="video",
            method="lsb",
            payload_hash="a" * 64,
            media_hash="b" * 64,
        )
        chain.add_receipt(receipt)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            temp_path = Path(f.name)

        try:
            with ChainStorage() as storage:
                storage.save_chain(chain)

                # Export
                success = storage.export_chain_to_file(chain.chain_id, temp_path)
                assert success
                assert temp_path.exists()

                # Import
                imported_id = storage.import_chain_from_file(temp_path)
                assert imported_id == chain.chain_id

        finally:
            if temp_path.exists():
                temp_path.unlink()
