"""Video API Schemas"""

from pydantic import BaseModel
from typing import Optional, Dict, Any


class EncodeRequest(BaseModel):
    """Request schema for video encoding"""
    bits_per_channel: int = 2
    use_encryption: bool = True
    error_correction: bool = True
    create_receipt: bool = True


class EncodeResponse(BaseModel):
    """Response schema for video encoding"""
    success: bool
    output_file: str
    verification_hash: str
    stats: dict[str, Any]
    receipt_id: str | None = None


class DecodeResponse(BaseModel):
    """Response schema for video decoding"""
    success: bool
    payload_file: str
    payload_size: int
    stats: dict[str, Any]
    receipt_id: str | None = None
    integrity_verified: bool


class CapacityResponse(BaseModel):
    """Response schema for capacity estimation"""
    total_bytes: int
    usable_bytes: int
    recommended_max_bytes: int
