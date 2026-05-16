# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
ShadowTag v2 - Receipt Chain Module

Blockchain-inspired receipt chain for steganographic operation verification,
audit trails, and provenance tracking.
"""

from .chain import ReceiptChain, Receipt
from .block import Block, BlockHeader
from .verifier import ChainVerifier
from .storage import ChainStorage

__all__ = [
  "ReceiptChain",
  "Receipt",
  "Block",
  "BlockHeader",
  "ChainVerifier",
  "ChainStorage",
]

__version__ = "2.0.0"
