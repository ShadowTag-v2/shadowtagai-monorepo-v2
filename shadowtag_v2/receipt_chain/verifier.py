# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Chain Verifier

Provides advanced verification and validation capabilities for receipt chains.
"""

from typing import List, Dict, Any, Tuple
from datetime import datetime

from .chain import ReceiptChain, Receipt


class VerificationResult:
    """Result of chain verification"""

    def __init__(self):
        self.is_valid = True
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.details: dict[str, Any] = {}

    def add_error(self, error: str) -> None:
        """Add an error (invalidates result)"""
        self.is_valid = False
        self.errors.append(error)

    def add_warning(self, warning: str) -> None:
        """Add a warning (doesn't invalidate result)"""
        self.warnings.append(warning)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "is_valid": self.is_valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "details": self.details,
        }


class ChainVerifier:
    """
    Advanced verification and validation for receipt chains.

    Provides:
    - Structural integrity checks
    - Cryptographic verification
    - Temporal consistency validation
    - Anomaly detection
    """

    def __init__(self):
        """Initialize verifier"""
        pass

    def verify_chain(self, chain: ReceiptChain) -> VerificationResult:
        """
        Perform comprehensive chain verification.

        Args:
            chain: Chain to verify

        Returns:
            VerificationResult with detailed findings
        """
        result = VerificationResult()

        # Check basic structure
        self._verify_structure(chain, result)

        # Check cryptographic integrity
        self._verify_cryptography(chain, result)

        # Check temporal consistency
        self._verify_temporal(chain, result)

        # Check receipt integrity
        self._verify_receipts(chain, result)

        # Calculate statistics
        result.details = self._calculate_statistics(chain)

        return result

    def _verify_structure(self, chain: ReceiptChain, result: VerificationResult) -> None:
        """Verify chain structure"""
        if not chain.blocks:
            result.add_error("Chain has no blocks")
            return

        # Verify genesis block
        if chain.blocks[0].header.index != 0:
            result.add_error("Genesis block index is not 0")

        if chain.blocks[0].header.previous_hash != "0" * 64:
            result.add_error("Genesis block has invalid previous_hash")

        # Verify index sequence
        for i, block in enumerate(chain.blocks):
            if block.header.index != i:
                result.add_error(f"Block {i} has incorrect index: {block.header.index}")

    def _verify_cryptography(self, chain: ReceiptChain, result: VerificationResult) -> None:
        """Verify cryptographic integrity"""
        for i, block in enumerate(chain.blocks):
            # Verify block hash
            if not block.verify():
                result.add_error(f"Block {i} failed verification")

            # Verify chain linkage (except genesis)
            if i > 0:
                previous_block = chain.blocks[i - 1]
                if block.header.previous_hash != previous_block.hash():
                    result.add_error(f"Block {i} has invalid previous_hash linkage")

    def _verify_temporal(self, chain: ReceiptChain, result: VerificationResult) -> None:
        """Verify temporal consistency"""
        for i in range(1, len(chain.blocks)):
            current_time = datetime.fromisoformat(chain.blocks[i].header.timestamp)
            previous_time = datetime.fromisoformat(chain.blocks[i - 1].header.timestamp)

            # Timestamps should be monotonically increasing
            if current_time < previous_time:
                result.add_warning(f"Block {i} timestamp is earlier than previous block")

            # Check for suspiciously large time gaps (>1 year)
            time_gap = (current_time - previous_time).days
            if time_gap > 365:
                result.add_warning(f"Block {i} has large time gap ({time_gap} days) from previous block")

    def _verify_receipts(self, chain: ReceiptChain, result: VerificationResult) -> None:
        """Verify receipt integrity"""
        operation_ids = set()

        for i, block in enumerate(chain.blocks):
            receipt = block.receipt

            # Check for duplicate operation IDs
            if receipt.operation_id in operation_ids:
                result.add_warning(f"Duplicate operation_id found: {receipt.operation_id}")
            operation_ids.add(receipt.operation_id)

            # Verify hash formats (64 hex chars)
            if len(receipt.payload_hash) != 64:
                result.add_error(f"Block {i} has invalid payload_hash length")

            if len(receipt.media_hash) != 64:
                result.add_error(f"Block {i} has invalid media_hash length")

    def _calculate_statistics(self, chain: ReceiptChain) -> dict[str, Any]:
        """Calculate chain statistics"""
        if not chain.blocks:
            return {}

        stats = {
            "total_blocks": len(chain.blocks),
            "genesis_time": chain.blocks[0].header.timestamp,
            "latest_time": chain.blocks[-1].header.timestamp,
        }

        if len(chain.blocks) > 1:
            first_time = datetime.fromisoformat(chain.blocks[0].header.timestamp)
            last_time = datetime.fromisoformat(chain.blocks[-1].header.timestamp)
            chain_age_days = (last_time - first_time).days
            stats["chain_age_days"] = chain_age_days

        return stats

    def verify_receipt_pair(self, encode_receipt: Receipt, decode_receipt: Receipt) -> tuple[bool, list[str]]:
        """
        Verify that an encode/decode receipt pair is consistent.

        Args:
            encode_receipt: Encoding operation receipt
            decode_receipt: Decoding operation receipt

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        # Check operation types
        if encode_receipt.operation_type != "encode":
            errors.append("First receipt is not an encode operation")

        if decode_receipt.operation_type != "decode":
            errors.append("Second receipt is not a decode operation")

        # Check payload hashes match
        if encode_receipt.payload_hash != decode_receipt.payload_hash:
            errors.append("Payload hashes do not match")

        # Check media hashes match
        if encode_receipt.media_hash != decode_receipt.media_hash:
            errors.append("Media hashes do not match")

        # Check media types match
        if encode_receipt.media_type != decode_receipt.media_type:
            errors.append("Media types do not match")

        # Check methods match
        if encode_receipt.method != decode_receipt.method:
            errors.append("Encoding methods do not match")

        is_valid = len(errors) == 0
        return is_valid, errors
