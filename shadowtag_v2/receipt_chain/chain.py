# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Receipt Chain Implementation

Provides a blockchain-inspired chain structure for tracking steganographic
operations with cryptographic verification.
"""

from typing import Any
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

from .block import Block


@dataclass
class Receipt:
  """
  Receipt for a steganographic operation.

  Contains metadata and verification information for tracking
  encoding/decoding operations.
  """

  operation_id: str  # Unique operation identifier
  operation_type: str  # encode, decode, verify
  timestamp: str  # ISO 8601 timestamp
  media_type: str  # video, audio, image
  method: str  # Steganography method used
  payload_hash: str  # SHA-256 hash of payload
  media_hash: str  # SHA-256 hash of media file
  metadata: dict[str, Any] = field(default_factory=dict)
  signature: str | None = None  # Optional digital signature

  def to_dict(self) -> dict[str, Any]:
    """Convert receipt to dictionary"""
    return asdict(self)

  def to_json(self) -> str:
    """Convert receipt to JSON string"""
    return json.dumps(self.to_dict(), sort_keys=True)

  def hash(self) -> str:
    """Calculate SHA-256 hash of receipt"""
    return hashlib.sha256(self.to_json().encode()).hexdigest()

  @classmethod
  def from_dict(cls, data: dict[str, Any]) -> "Receipt":
    """Create receipt from dictionary"""
    return cls(**data)


class ReceiptChain:
  """
  Blockchain-inspired chain of receipts for steganographic operations.

  Provides:
  - Immutable audit trail
  - Cryptographic verification
  - Operation provenance tracking
  - Tamper detection
  """

  def __init__(self, chain_id: str | None = None):
    """
    Initialize a new receipt chain.

    Args:
        chain_id: Unique identifier for this chain. Auto-generated if None.
    """
    self.chain_id = chain_id or self._generate_chain_id()
    self.blocks: list[Block] = []
    self._create_genesis_block()

  def _generate_chain_id(self) -> str:
    """Generate a unique chain ID"""
    timestamp = datetime.now(timezone.utc).isoformat()
    data = f"chain_{timestamp}".encode()
    return hashlib.sha256(data).hexdigest()[:16]

  def _create_genesis_block(self) -> None:
    """Create the genesis (first) block in the chain"""
    genesis_receipt = Receipt(
      operation_id="genesis",
      operation_type="init",
      timestamp=datetime.now(timezone.utc).isoformat(),
      media_type="none",
      method="none",
      payload_hash="0" * 64,
      media_hash="0" * 64,
      metadata={"chain_id": self.chain_id, "version": "2.0"},
    )

    genesis_block = Block.create_genesis(genesis_receipt)
    self.blocks.append(genesis_block)

  def add_receipt(self, receipt: Receipt) -> Block:
    """
    Add a new receipt to the chain.

    Args:
        receipt: Receipt to add

    Returns:
        The newly created block

    Raises:
        ValueError: If chain is in invalid state
    """
    if not self.blocks:
      raise ValueError("Chain has no genesis block")

    # Get previous block
    previous_block = self.blocks[-1]

    # Create new block
    index = len(self.blocks)
    block = Block.create_next(receipt, previous_block, index)

    # Add to chain
    self.blocks.append(block)

    return block

  def verify_chain(self) -> bool:
    """
    Verify the integrity of the entire chain.

    Returns:
        True if chain is valid, False otherwise
    """
    if not self.blocks:
      return False

    # Verify genesis block
    if not self.blocks[0].verify():
      return False

    # Verify each subsequent block
    for i in range(1, len(self.blocks)):
      current_block = self.blocks[i]
      previous_block = self.blocks[i - 1]

      # Verify block itself
      if not current_block.verify():
        return False

      # Verify chain linkage
      if current_block.header.previous_hash != previous_block.hash():
        return False

      # Verify index sequence
      if current_block.header.index != i:
        return False

    return True

  def get_receipt(self, operation_id: str) -> Receipt | None:
    """
    Retrieve a receipt by operation ID.

    Args:
        operation_id: Operation ID to search for

    Returns:
        Receipt if found, None otherwise
    """
    for block in self.blocks:
      if block.receipt.operation_id == operation_id:
        return block.receipt
    return None

  def get_receipts_by_type(self, operation_type: str) -> list[Receipt]:
    """
    Get all receipts of a specific operation type.

    Args:
        operation_type: Type to filter by

    Returns:
        List of matching receipts
    """
    return [
      block.receipt
      for block in self.blocks
      if block.receipt.operation_type == operation_type
    ]

  def get_receipts_by_media_type(self, media_type: str) -> list[Receipt]:
    """
    Get all receipts for a specific media type.

    Args:
        media_type: Media type to filter by

    Returns:
        List of matching receipts
    """
    return [
      block.receipt for block in self.blocks if block.receipt.media_type == media_type
    ]

  def get_chain_summary(self) -> dict[str, Any]:
    """
    Get summary statistics for the chain.

    Returns:
        Dictionary with chain statistics
    """
    if not self.blocks:
      return {"error": "Empty chain"}

    operation_types = {}
    media_types = {}

    for block in self.blocks[1:]:  # Skip genesis
      op_type = block.receipt.operation_type
      media_type = block.receipt.media_type

      operation_types[op_type] = operation_types.get(op_type, 0) + 1
      media_types[media_type] = media_types.get(media_type, 0) + 1

    return {
      "chain_id": self.chain_id,
      "total_blocks": len(self.blocks),
      "total_receipts": len(self.blocks) - 1,  # Exclude genesis
      "operation_types": operation_types,
      "media_types": media_types,
      "is_valid": self.verify_chain(),
      "created": self.blocks[0].header.timestamp,
      "last_updated": self.blocks[-1].header.timestamp if self.blocks else None,
    }

  def export_to_dict(self) -> dict[str, Any]:
    """
    Export chain to dictionary.

    Returns:
        Dictionary representation of chain
    """
    return {
      "chain_id": self.chain_id,
      "blocks": [block.to_dict() for block in self.blocks],
    }

  def export_to_json(self, filepath: Path | None = None) -> str:
    """
    Export chain to JSON.

    Args:
        filepath: Optional path to save JSON file

    Returns:
        JSON string representation
    """
    json_str = json.dumps(self.export_to_dict(), indent=2)

    if filepath:
      filepath.write_text(json_str)

    return json_str

  @classmethod
  def import_from_dict(cls, data: dict[str, Any]) -> "ReceiptChain":
    """
    Import chain from dictionary.

    Args:
        data: Dictionary representation

    Returns:
        Reconstructed ReceiptChain

    Raises:
        ValueError: If data is invalid
    """
    chain = cls.__new__(cls)  # Create without calling __init__
    chain.chain_id = data["chain_id"]
    chain.blocks = [Block.from_dict(block_data) for block_data in data["blocks"]]

    # Verify imported chain
    if not chain.verify_chain():
      raise ValueError("Imported chain is invalid")

    return chain

  @classmethod
  def import_from_json(cls, json_str: str) -> "ReceiptChain":
    """
    Import chain from JSON string.

    Args:
        json_str: JSON string representation

    Returns:
        Reconstructed ReceiptChain
    """
    data = json.loads(json_str)
    return cls.import_from_dict(data)

  def __len__(self) -> int:
    """Return number of blocks in chain"""
    return len(self.blocks)

  def __getitem__(self, index: int) -> Block:
    """Get block by index"""
    return self.blocks[index]
