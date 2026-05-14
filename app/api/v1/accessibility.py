# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Accessibility and safety compliance API endpoints
Implements WCAG 2.2, COPPA, and Age Appropriate Design Code
"""

from fastapi import APIRouter

from app.models.accessibility import (
    WCAGAuditRequest,
    WCAGAuditResponse,
    COPPAComplianceRequest,
    COPPAComplianceResponse,
    AADCComplianceRequest,
    AADCComplianceResponse,
    WCAGLevel,
    WCAGPrinciple,
)
from app.services.accessibility_engine import AccessibilityEngine

router = APIRouter()
accessibility_engine = AccessibilityEngine()


@router.post("/wcag/audit", response_model=WCAGAuditResponse)
async def audit_wcag(request: WCAGAuditRequest):
    """
    WCAG 2.2 accessibility audit

    Checks conformance to:
    - Level A (minimum)
    - Level AA (mid-range)
    - Level AAA (highest)

    Covers 4 principles:
    - Perceivable
    - Operable
    - Understandable
    - Robust
    """
    result = await accessibility_engine.audit_wcag(request)
    return result


@router.post("/coppa/check", response_model=COPPAComplianceResponse)
async def check_coppa(request: COPPAComplianceRequest):
    """
    COPPA compliance check

    Verifies:
    - Age verification (under 13)
    - Parental consent requirements
    - Data minimization
    - Deletion mechanisms
    - Third-party disclosure limits
    """
    result = await accessibility_engine.check_coppa(request)
    return result


@router.post("/aadc/check", response_model=AADCComplianceResponse)
async def check_aadc(request: AADCComplianceRequest):
    """
    Age Appropriate Design Code (UK) compliance check

    Verifies:
    - Age-appropriate privacy settings
    - Data collection limits
    - Geolocation controls
    - Profiling restrictions
    - Parental controls
    """
    result = await accessibility_engine.check_aadc(request)
    return result


@router.get("/wcag/principles", response_model=list[dict])
async def list_wcag_principles():
    """List WCAG principles and guidelines"""
    return [
        {
            "principle": WCAGPrinciple.PERCEIVABLE,
            "description": "Information and UI components must be presentable",
            "guidelines": ["Text Alternatives", "Time-based Media", "Adaptable", "Distinguishable"],
        },
        {
            "principle": WCAGPrinciple.OPERABLE,
            "description": "UI components and navigation must be operable",
            "guidelines": ["Keyboard Accessible", "Enough Time", "Seizures and Physical Reactions", "Navigable", "Input Modalities"],
        },
        {
            "principle": WCAGPrinciple.UNDERSTANDABLE,
            "description": "Information and operation must be understandable",
            "guidelines": ["Readable", "Predictable", "Input Assistance"],
        },
        {"principle": WCAGPrinciple.ROBUST, "description": "Content must be robust enough for various user agents", "guidelines": ["Compatible"]},
    ]


@router.get("/wcag/levels", response_model=list[dict])
async def list_wcag_levels():
    """List WCAG conformance levels"""
    return [
        {"level": WCAGLevel.A, "description": "Minimum level of conformance", "required_for": "Basic accessibility"},
        {"level": WCAGLevel.AA, "description": "Mid-range conformance (recommended)", "required_for": "Government sites, most commercial sites"},
        {"level": WCAGLevel.AAA, "description": "Highest level of conformance", "required_for": "Specialized accessibility needs"},
    ]
