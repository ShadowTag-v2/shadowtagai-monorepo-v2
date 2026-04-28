# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Adtech compliance models"""

from enum import StrEnum

from pydantic import BaseModel, Field, HttpUrl


class VASTVersion(StrEnum):
    """VAST protocol versions"""

    VAST_4_0 = "4.0"
    VAST_4_1 = "4.1"
    VAST_4_2 = "4.2"
    VAST_4_3 = "4.3"


class AdFormat(StrEnum):
    """Ad format types"""

    LINEAR = "linear"
    NON_LINEAR = "non_linear"
    COMPANION = "companion"


class PrivacySandboxAPI(StrEnum):
    """Privacy Sandbox APIs"""

    TOPICS = "topics"
    FLEDGE = "fledge"
    ATTRIBUTION_REPORTING = "attribution_reporting"


class VASTValidationRequest(BaseModel):
    """Request to validate VAST XML"""

    vast_xml: str = Field(..., description="VAST XML to validate")
    version: VASTVersion = Field(default=VASTVersion.VAST_4_3)
    strict_mode: bool = Field(default=True)


class VASTValidationResponse(BaseModel):
    """VAST validation response"""

    valid: bool
    version_detected: VASTVersion
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    ad_format: AdFormat | None = None
    duration: int | None = None
    tracking_events: list[str] = Field(default_factory=list)
    viewability_compliant: bool


class OMSDKVerificationRequest(BaseModel):
    """Open Measurement SDK verification request"""

    ad_session_id: str
    creative_url: HttpUrl
    impression_url: HttpUrl | None = None
    verification_scripts: list[HttpUrl] = Field(default_factory=list)


class OMSDKVerificationResponse(BaseModel):
    """OM SDK verification response"""

    session_id: str
    viewability_verified: bool
    viewable_percentage: float = Field(..., ge=0.0, le=100.0)
    audible: bool
    player_state: str
    creative_type: str
    errors: list[str] = Field(default_factory=list)


class PrivacySandboxComplianceRequest(BaseModel):
    """Privacy Sandbox compliance check"""

    platform: str = Field(..., description="Platform: ios or android")
    apis_used: list[PrivacySandboxAPI]
    user_consent: bool
    third_party_cookies: bool = Field(default=False)


class PrivacySandboxComplianceResponse(BaseModel):
    """Privacy Sandbox compliance response"""

    compliant: bool
    platform: str
    apis_validated: dict[str, bool]
    warnings: list[str] = Field(default_factory=list)
    migration_required: bool
    skan_configured: bool  # For iOS
    topics_configured: bool  # For Android


class BrandSafetyCheck(BaseModel):
    """Brand safety verification"""

    content_id: str
    creative_url: HttpUrl | None = None
    category_tags: list[str] = Field(default_factory=list)


class BrandSafetyResponse(BaseModel):
    """Brand safety check response"""

    safe: bool
    safety_score: float = Field(..., ge=0.0, le=1.0)
    blocked_categories: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    recommended_action: str
