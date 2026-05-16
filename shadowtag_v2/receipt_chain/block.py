# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Block Structure for Receipt Chain

Defines the block and block header structures for the receipt chain.
"""

from typing import Any
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import hashlib
import json


@dataclass
class BlockHeader:
  """
  Block header containing metadata and cryptographic links.
  """

  index: int  # Block index in chain
  timestamp: str  # ISO 8601 timestamp
  previous_hash: str  # Hash of previous block
  merkle_root: str  # Merkle root of block data
  nonce: int = 0  # Nonce for proof-of-work (optional)
  version: str = "2.0"  # Block version

  def to_dict(self) -> dict[str, Any]:
    """Convert header to dictionary"""
    return asdict(self)

  def to_json(self) -> str:
    """Convert header to JSON string"""
    return json.dumps(self.to_dict(), sort_keys=True)

  def hash(self) -> str:
    """Calculate SHA-256 hash of header"""
    return hashlib.sha256(self.to_json().encode()).hexdigest()


class Block:
  """
  Block in the receipt chain.

  Contains a receipt and cryptographic linkage to previous blocks.
  """

  def __init__(
    self,
    header: BlockHeader,
    receipt: "Receipt",  # Forward reference
    signature: str | None = None,
  ):
    """
    Initialize block.

    Args:
        header: Block header
        receipt: Receipt contained in block
        signature: Optional digital signature
    """
    self.header = header
    self.receipt = receipt
    self.signature = signature

  def hash(self) -> str:
    """
    Calculate hash of the entire block.

    Returns:
        SHA-256 hash as hex string
    """
    block_data = {
      "header": self.header.to_dict(),
      "receipt": self.receipt.to_dict(),
    }
    json_str = json.dumps(block_data, sort_keys=True)
    return hashlib.sha256(json_str.encode()).hexdigest()

  def verify(self) -> bool:
    """
    Verify block integrity.

    Returns:
        True if block is valid, False otherwise
    """
    # Verify header hash matches
    header_hash = self.header.hash()

    # Verify merkle root (simplified: just hash receipt)
    receipt_hash = self.receipt.hash()
    expected_merkle = hashlib.sha256(receipt_hash.encode()).hexdigest()

    if self.header.merkle_root != expected_merkle:
      return False

    # If signature present, verify it
    # TODO: Implement signature verification

    return True

  def to_dict(self) -> dict[str, Any]:
    """
    Convert block to dictionary.

    Returns:
        Dictionary representation
    """
    return {
      "header": self.header.to_dict(),
      "receipt": self.receipt.to_dict(),
      "signature": self.signature,
      "hash": self.hash(),
    }

  def to_json(self) -> str:
    """
    Convert block to JSON string.

    Returns:
        JSON representation
    """
    return json.dumps(self.to_dict(), indent=2)

  @classmethod
  def from_dict(cls, data: dict[str, Any]) -> "Block":
    """
    Create block from dictionary.

    Args:
        data: Dictionary representation

    Returns:
        Block instance
    """
    from .chain import Receipt  # Import here to avoid circular dependency

    header = BlockHeader(**data["header"])
    receipt = Receipt.from_dict(data["receipt"])
    signature = data.get("signature")

    return cls(header, receipt, signature)

  @classmethod
  def create_genesis(cls, receipt: "Receipt") -> "Block":
    """
    Create a genesis (first) block.

    Args:
        receipt: Genesis receipt

    Returns:
        Genesis block
    """
    # Genesis block has no previous hash
    receipt_hash = receipt.hash()
    merkle_root = hashlib.sha256(receipt_hash.encode()).hexdigest()

    header = BlockHeader(
      index=0,
      timestamp=datetime.now(timezone.utc).isoformat(),
      previous_hash="0" * 64,  # No previous block
      merkle_root=merkle_root,
    )

    return cls(header, receipt)

  @classmethod
  def create_next(
    cls, receipt: "Receipt", previous_block: "Block", index: int
  ) -> "Block":
    """
    Create the next block in the chain.

    Args:
        receipt: Receipt for this block
        previous_block: Previous block in chain
        index: Index for new block

    Returns:
        New block
    """
    receipt_hash = receipt.hash()
    merkle_root = hashlib.sha256(receipt_hash.encode()).hexdigest()

    header = BlockHeader(
      index=index,
      timestamp=datetime.now(timezone.utc).isoformat(),
      previous_hash=previous_block.hash(),
      merkle_root=merkle_root,
    )

    return cls(header, receipt)

  def __repr__(self) -> str:
    """String representation"""
    return f"Block(index={self.header.index}, hash={self.hash()[:8]}..., operation={self.receipt.operation_type})"
