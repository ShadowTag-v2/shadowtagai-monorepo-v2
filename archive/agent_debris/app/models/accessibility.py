"""
Accessibility and safety compliance models
"""
from enum import Enum, StrEnum
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl


class WCAGLevel(StrEnum):
    """WCAG conformance levels"""
    A = "A"
    AA = "AA"
    AAA = "AAA"


class WCAGPrinciple(StrEnum):
    """WCAG principles"""
    PERCEIVABLE = "perceivable"
    OPERABLE = "operable"
    UNDERSTANDABLE = "understandable"
    ROBUST = "robust"


class AgeGroup(StrEnum):
    """Age groups for safety compliance"""
    UNDER_13 = "under_13"
    TEEN_13_17 = "teen_13_17"
    ADULT_18_PLUS = "adult_18_plus"


class WCAGAuditRequest(BaseModel):
    """WCAG accessibility audit request"""
    url: HttpUrl | None = None
    html_content: str | None = None
    target_level: WCAGLevel = Field(default=WCAGLevel.AA)
    version: str = Field(default="2.2")


class WCAGViolation(BaseModel):
    """WCAG violation"""
    principle: WCAGPrinciple
    guideline: str
    success_criterion: str
    level: WCAGLevel
    description: str
    impact: str  # "critical", "serious", "moderate", "minor"
    element: str | None = None
    remediation: str


class WCAGAuditResponse(BaseModel):
    """WCAG audit response"""
    compliant: bool
    level_achieved: WCAGLevel | None = None
    violations: list[WCAGViolation]
    warnings: list[str] = Field(default_factory=list)
    score: float = Field(..., ge=0.0, le=100.0)
    tested_elements: int


class COPPAComplianceRequest(BaseModel):
    """COPPA compliance check request"""
    user_age: int
    collects_personal_info: bool
    parental_consent_obtained: bool
    data_minimization: bool
    deletion_mechanism: bool
    third_party_disclosure: bool


class COPPAComplianceResponse(BaseModel):
    """COPPA compliance response"""
    compliant: bool
    age_group: AgeGroup
    requires_parental_consent: bool
    violations: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


class AADCComplianceRequest(BaseModel):
    """Age Appropriate Design Code compliance check"""
    user_age: int
    geolocation_enabled: bool
    profiling_enabled: bool
    data_shared_with_third_parties: bool
    privacy_settings_default_high: bool
    parental_controls_available: bool


class AADCComplianceResponse(BaseModel):
    """AADC compliance response"""
    compliant: bool
    age_group: AgeGroup
    violations: list[str] = Field(default_factory=list)
    required_controls: list[str] = Field(default_factory=list)
    age_appropriate_defaults: bool
