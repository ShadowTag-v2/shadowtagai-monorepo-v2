# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Audio API Schemas"""

from typing import Any

from pydantic import BaseModel


class EncodeRequest(BaseModel):
    """Request schema for audio encoding"""

    method: str = "lsb"
    bits_per_sample: int = 1
    use_encryption: bool = True
    create_receipt: bool = True


class EncodeResponse(BaseModel):
    """Response schema for audio encoding"""

    success: bool
    output_file: str
    stats: dict[str, Any]
    receipt_id: str | None = None


class DecodeResponse(BaseModel):
    """Response schema for audio decoding"""

    success: bool
    payload_file: str
    payload_size: int
    stats: dict[str, Any]
    receipt_id: str | None = None
    integrity_verified: bool
