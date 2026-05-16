# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Adtech compliance API endpoints
Implements VAST 4.x, OM SDK, Privacy Sandbox verification
"""

from fastapi import APIRouter

from app.models.adtech import (
  BrandSafetyCheck,
  BrandSafetyResponse,
  OMSDKVerificationRequest,
  OMSDKVerificationResponse,
  PrivacySandboxComplianceRequest,
  PrivacySandboxComplianceResponse,
  VASTValidationRequest,
  VASTValidationResponse,
  VASTVersion,
)
from app.services.adtech_engine import AdtechEngine

router = APIRouter()
adtech_engine = AdtechEngine()


@router.post("/vast/validate", response_model=VASTValidationResponse)
async def validate_vast(request: VASTValidationRequest):
  """
  Validate VAST XML compliance

  Checks:
  - VAST version compliance (4.0-4.3)
  - XML schema validation
  - Required elements present
  - Viewability tracking events
  - Error handling URLs
  """
  result = await adtech_engine.validate_vast(request)
  return result


@router.post("/omsdk/verify", response_model=OMSDKVerificationResponse)
async def verify_omsdk(request: OMSDKVerificationRequest):
  """
  Verify Open Measurement SDK compliance

  Validates:
  - Ad session configuration
  - Viewability measurement
  - Verification scripts
  - Creative type detection
  - Player state tracking
  """
  result = await adtech_engine.verify_omsdk(request)
  return result


@router.post("/privacy-sandbox/check", response_model=PrivacySandboxComplianceResponse)
async def check_privacy_sandbox(request: PrivacySandboxComplianceRequest):
  """
  Check Privacy Sandbox compliance

  For iOS:
  - SKAdNetwork (SKAN) configuration
  - App Tracking Transparency (ATT)

  For Android:
  - Topics API
  - FLEDGE
  - Attribution Reporting
  """
  result = await adtech_engine.check_privacy_sandbox(request)
  return result


@router.post("/brand-safety/check", response_model=BrandSafetyResponse)
async def check_brand_safety(request: BrandSafetyCheck):
  """
  Check brand safety compliance

  Verifies:
  - Content category classification
  - Blocked category detection
  - Safety score calculation
  - Third-party verification compatibility
  """
  result = await adtech_engine.check_brand_safety(request)
  return result


@router.get("/vast/versions", response_model=list[dict])
async def list_vast_versions():
  """List supported VAST versions"""
  return [
    {"version": VASTVersion.VAST_4_0, "supported": True, "recommended": False},
    {"version": VASTVersion.VAST_4_1, "supported": True, "recommended": False},
    {"version": VASTVersion.VAST_4_2, "supported": True, "recommended": True},
    {"version": VASTVersion.VAST_4_3, "supported": True, "recommended": True},
  ]


@router.get("/standards", response_model=list[dict])
async def list_adtech_standards():
  """List all adtech standards and compliance requirements"""
  return [
    {
      "standard": "VAST",
      "version": "4.3",
      "organization": "IAB",
      "description": "Video Ad Serving Template",
      "required": True,
    },
    {
      "standard": "OM SDK",
      "version": "1.4",
      "organization": "IAB Tech Lab",
      "description": "Open Measurement SDK",
      "required": True,
    },
    {
      "standard": "SIMID",
      "version": "1.1",
      "organization": "IAB",
      "description": "Secure Interactive Media Interface Definition",
      "required": False,
    },
    {
      "standard": "Privacy Sandbox",
      "version": "2024",
      "organization": "Google/Apple",
      "description": "Privacy-preserving advertising APIs",
      "required": True,
    },
    {
      "standard": "SKAdNetwork",
      "version": "4.0",
      "organization": "Apple",
      "description": "iOS attribution framework",
      "required": True,
    },
  ]
