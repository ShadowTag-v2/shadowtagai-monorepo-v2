# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Content provenance and C2PA models"""

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, HttpUrl


class ContentType(StrEnum):
    """Content types"""

    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    TEXT = "text"


class ManifestAction(StrEnum):
    """C2PA manifest actions"""

    CREATED = "c2pa.created"
    EDITED = "c2pa.edited"
    FILTERED = "c2pa.filtered"
    TRANSCODED = "c2pa.transcoded"
    AI_GENERATED = "c2pa.ai_generated"
    AI_TRAINING = "c2pa.ai_training"


class C2PAVerificationRequest(BaseModel):
    """Request to verify C2PA content credentials"""

    content_url: HttpUrl | None = None
    content_data: str | None = Field(None, description="Base64 encoded content")
    content_type: ContentType


class C2PAAssertion(BaseModel):
    """C2PA assertion"""

    label: str
    data: dict[str, Any]
    timestamp: datetime | None = None


class C2PAManifest(BaseModel):
    """C2PA manifest"""

    claim_generator: str
    title: str | None = None
    format: str
    instance_id: str
    assertions: list[C2PAAssertion]
    ingredients: list[dict[str, Any]] = Field(default_factory=list)
    signature: str | None = None


class C2PAVerificationResponse(BaseModel):
    """C2PA verification response"""

    verified: bool
    has_credentials: bool
    manifest: C2PAManifest | None = None
    chain_of_custody: list[dict[str, Any]] = Field(default_factory=list)
    ai_generated: bool
    ai_training_allowed: bool
    errors: list[str] = Field(default_factory=list)
    tampered: bool
    signature_valid: bool


class ContentProvenanceRequest(BaseModel):
    """Request to create content provenance record"""

    content_id: str
    content_type: ContentType
    creator_id: str
    action: ManifestAction
    metadata: dict[str, Any] = Field(default_factory=dict)
    parent_content_id: str | None = None


class ContentProvenanceResponse(BaseModel):
    """Content provenance response"""

    provenance_id: str
    content_id: str
    timestamp: datetime
    manifest_url: HttpUrl | None = None
    credential_status: str
    blockchain_tx: str | None = None


class WatermarkRequest(BaseModel):
    """Request to watermark content"""

    content_path: str
    content_type: ContentType
    metadata: dict[str, Any] = Field(default_factory=dict)
    output_path: str | None = None


class WatermarkResponse(BaseModel):
    """Watermark response"""

    content_path: str
    watermarked: bool
    watermark_payload: str
    audit_trail: dict[str, Any]
    timestamp: datetime
