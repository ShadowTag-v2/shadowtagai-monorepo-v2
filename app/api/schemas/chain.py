# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Receipt Chain API Schemas"""

from pydantic import BaseModel
from typing import Any


class ChainSummary(BaseModel):
  """Summary of a receipt chain"""

  chain_id: str
  created_at: str
  updated_at: str
  block_count: int
  is_valid: bool


class ReceiptDetail(BaseModel):
  """Detailed receipt information"""

  chain_id: str
  operation_id: str
  operation_type: str
  timestamp: str
  media_type: str
  method: str
  payload_hash: str
  media_hash: str


class VerificationResult(BaseModel):
  """Chain verification result"""

  is_valid: bool
  errors: list[str]
  warnings: list[str]
  details: dict[str, Any]
