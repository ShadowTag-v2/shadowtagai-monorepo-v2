# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Pydantic models for API requests and responses."""

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class MediaType(str, Enum):
    """Supported media types."""

    VIDEO = "video"
    AUDIO = "audio"


class ChainType(str, Enum):
    """Supported blockchain networks."""

    POLYGON = "polygon"
    ETHEREUM = "ethereum"
    POLYGON_MUMBAI = "polygon-mumbai"
    SEPOLIA = "sepolia"


class EmbedRequest(BaseModel):
    """Request model for watermark embedding."""

    prompt: str = Field(..., description="Prompt text to embed", min_length=1)
    media_type: MediaType = Field(..., description="Media type (video or audio)")
    create_receipt: bool = Field(False, description="Create blockchain receipt")
    chain: ChainType | None = Field(None, description="Blockchain network")


class EmbedResponse(BaseModel):
    """Response model for watermark embedding."""

    ok: bool
    message: str
    output_filename: str
    watermark_result: dict[str, Any]
    blockchain_receipt: dict[str, Any] | None = None


class VerifyRequest(BaseModel):
    """Request model for watermark verification."""

    expected_prompt: str = Field(..., description="Expected prompt text")
    media_type: MediaType = Field(..., description="Media type (video or audio)")
    verify_receipt: bool = Field(False, description="Verify blockchain receipt")
    chain: ChainType | None = Field(None, description="Blockchain network")
    tx_hash: str | None = Field(None, description="Transaction hash to verify")


class VerifyResponse(BaseModel):
    """Response model for watermark verification."""

    ok: bool
    verified: bool
    message: str
    extracted_hash: str
    expected_hash: str | None = None
    bit_error_rate: float | None = None
    blockchain_receipt: dict[str, Any] | None = None


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str
    blockchain_enabled: bool
    vertex_enabled: bool


class ErrorResponse(BaseModel):
    """Error response model."""

    ok: bool = False
    error: str
    detail: str | None = None
