"""Compliance-related schemas"""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.audit_log import ActionType
from app.models.consent import ConsentMethod, ConsentType
from app.models.data_retention import DataCategory, DeletionRule


# Audit Log Schemas
class AuditLogResponse(BaseModel):
    """Schema for audit log response"""

    id: uuid.UUID
    user_id: uuid.UUID | None
    user_email: str | None
    action: ActionType
    resource_type: str
    resource_id: str | None
    description: str | None
    ip_address: str | None
    request_method: str | None
    request_path: str | None
    status_code: int | None
    success: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AuditLogListResponse(BaseModel):
    """Schema for paginated audit log list"""

    total: int
    page: int
    page_size: int
    logs: list[AuditLogResponse]


# Consent Schemas
class ConsentCreate(BaseModel):
    """Schema for creating consent record"""

    user_id: uuid.UUID
    consent_type: ConsentType
    consent_method: ConsentMethod
    is_granted: bool = True
    consent_text: str | None = None
    consent_version: str | None = "1.0"
    purpose: str | None = None


class ConsentUpdate(BaseModel):
    """Schema for updating consent"""

    is_granted: bool
    revoked_at: datetime | None = None


class ConsentResponse(BaseModel):
    """Schema for consent response"""

    id: uuid.UUID
    user_id: uuid.UUID
    user_email: str | None
    consent_type: ConsentType
    consent_method: ConsentMethod
    is_granted: bool
    is_active: bool
    granted_at: str
    expires_at: str | None
    revoked_at: str | None
    consent_version: str | None
    purpose: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Data Retention Schemas
class DataRetentionPolicyResponse(BaseModel):
    """Schema for data retention policy response"""

    id: uuid.UUID
    policy_name: str
    data_category: DataCategory
    retention_days: int
    deletion_rule: DeletionRule
    is_active: bool
    legal_requirement: str | None
    jurisdiction: str | None
    description: str | None
    gdpr_compliant: bool
    ccpa_compliant: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Compliance Check Schemas
class ComplianceCheckRequest(BaseModel):
    """Request schema for compliance check"""

    check_type: str = Field(
        ...,
        description="Type of compliance check: gdpr, ccpa, data_retention, consent",
    )
    resource_type: str | None = Field(None, description="Type of resource to check")
    resource_id: str | None = Field(None, description="ID of specific resource")
    code_snippet: str | None = Field(None, description="Code to analyze for compliance")
    endpoint_path: str | None = Field(None, description="API endpoint to check")


class ComplianceIssue(BaseModel):
    """Individual compliance issue"""

    severity: str = Field(..., description="critical, high, medium, low")
    issue_type: str
    description: str
    recommendation: str
    regulation: str  # GDPR, CCPA, etc.
    article: str | None = None  # Specific article/section


class ComplianceCheckResponse(BaseModel):
    """Response schema for compliance check"""

    check_id: uuid.UUID
    check_type: str
    is_compliant: bool
    compliance_score: int = Field(..., ge=0, le=100)
    issues: list[ComplianceIssue]
    recommendations: list[str]
    summary: str
    checked_at: datetime
    regulations_checked: list[str]


# Cookie Consent Schemas
class CookieConsentRequest(BaseModel):
    """Request for cookie consent"""

    necessary: bool = True  # Always required
    functional: bool = False
    analytics: bool = False
    advertising: bool = False


class CookieConsentResponse(BaseModel):
    """Response for cookie consent"""

    consent_id: uuid.UUID
    necessary: bool
    functional: bool
    analytics: bool
    advertising: bool
    timestamp: datetime


# Privacy Request Schemas
class PrivacyRequest(BaseModel):
    """User privacy request (GDPR/CCPA)"""

    request_type: str = Field(..., description="access, delete, export, rectify, restrict, object")
    user_email: EmailStr
    description: str | None = None


class PrivacyRequestResponse(BaseModel):
    """Response for privacy request"""

    request_id: uuid.UUID
    request_type: str
    status: str  # pending, in_progress, completed, rejected
    created_at: datetime
    expected_completion: datetime | None
    message: str


# Compliance Report Schemas
class ComplianceReport(BaseModel):
    """Comprehensive compliance report"""

    report_id: uuid.UUID
    generated_at: datetime
    period_start: datetime
    period_end: datetime
    total_users: int
    gdpr_users: int
    ccpa_users: int
    consent_records: int
    audit_logs: int
    privacy_requests: int
    compliance_score: int
    issues_found: int
    critical_issues: int
    recommendations: list[str]


# Data Processing Agreement Schema
class DataProcessingAgreement(BaseModel):
    """Data Processing Agreement (DPA) information"""

    dpa_id: uuid.UUID
    processor_name: str
    data_categories: list[str]
    processing_purposes: list[str]
    retention_period: str
    security_measures: list[str]
    sub_processors: list[str]
    dpa_signed_date: datetime | None
    is_active: bool
