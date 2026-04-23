"""Compliance API endpoints"""

import uuid
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.compliance.policies import (
    COMPLIANCE_POLICIES,
    CCPAPolicies,
    CookiePolicy,
    GDPRPolicies,
)
from app.db.session import get_db
from app.models.audit_log import ActionType
from app.models.consent import ConsentType
from app.models.data_retention import DataCategory
from app.schemas.compliance import (
    AuditLogListResponse,
    ComplianceCheckRequest,
    ComplianceCheckResponse,
    ComplianceIssue,
    ConsentCreate,
    ConsentResponse,
    DataRetentionPolicyResponse,
    PrivacyRequest,
    PrivacyRequestResponse,
)
from app.services.compliance_service import ComplianceService

router = APIRouter(prefix="/compliance", tags=["Compliance"])


# Audit Logs
@router.get("/audit-logs", response_model=AuditLogListResponse)
async def get_audit_logs(
    user_id: str | None = Query(None),
    action: ActionType | None = Query(None),
    resource_type: str | None = Query(None),
    start_date: datetime | None = Query(None),
    end_date: datetime | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Get audit logs with filtering and pagination"""
    service = ComplianceService(db)

    user_uuid = uuid.UUID(user_id) if user_id else None
    offset = (page - 1) * page_size

    logs, total = await service.get_audit_logs(
        user_id=user_uuid,
        action=action,
        resource_type=resource_type,
        start_date=start_date,
        end_date=end_date,
        limit=page_size,
        offset=offset,
    )

    return AuditLogListResponse(
        total=total,
        page=page,
        page_size=page_size,
        logs=logs,
    )


# Consent Management
@router.post("/consent", response_model=ConsentResponse, status_code=201)
async def create_consent(
    consent_data: ConsentCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new consent record"""
    service = ComplianceService(db)

    consent = await service.create_consent(
        user_id=consent_data.user_id,
        consent_type=consent_data.consent_type,
        consent_method=consent_data.consent_method,
        is_granted=consent_data.is_granted,
        consent_text=consent_data.consent_text,
        consent_version=consent_data.consent_version,
        purpose=consent_data.purpose,
    )

    return consent


@router.get("/consent/{user_id}", response_model=list[ConsentResponse])
async def get_user_consents(
    user_id: str,
    consent_type: ConsentType | None = Query(None),
    active_only: bool = Query(True),
    db: AsyncSession = Depends(get_db),
):
    """Get user's consent records"""
    service = ComplianceService(db)

    user_uuid = uuid.UUID(user_id)
    consents = await service.get_user_consents(
        user_id=user_uuid,
        consent_type=consent_type,
        active_only=active_only,
    )

    return consents


@router.delete("/consent/{consent_id}", response_model=ConsentResponse)
async def revoke_consent(
    consent_id: str,
    user_id: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """Revoke a consent"""
    service = ComplianceService(db)

    try:
        consent = await service.revoke_consent(
            consent_id=uuid.UUID(consent_id),
            user_id=uuid.UUID(user_id),
        )
        return consent
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


# Data Retention Policies
@router.get("/retention-policies", response_model=list[DataRetentionPolicyResponse])
async def get_retention_policies(
    data_category: DataCategory | None = Query(None),
    active_only: bool = Query(True),
    db: AsyncSession = Depends(get_db),
):
    """Get data retention policies"""
    service = ComplianceService(db)

    policies = await service.get_retention_policies(
        data_category=data_category,
        active_only=active_only,
    )

    return policies


# AI-Powered Compliance Checks
@router.post("/check", response_model=ComplianceCheckResponse)
async def check_compliance(
    request: ComplianceCheckRequest,
    db: AsyncSession = Depends(get_db),
):
    """Perform AI-powered compliance check"""
    service = ComplianceService(db)

    if request.endpoint_path and request.code_snippet:
        # Analyze endpoint
        result = await service.analyze_endpoint_compliance(
            endpoint_code=request.code_snippet,
            endpoint_path=request.endpoint_path,
            request_method="GET",
        )
    elif request.check_type == "consent":
        # Check consent requirements
        result = await service.check_consent_requirements(
            user_location=request.resource_id or "EU",
            data_categories=["personal_data"],
            processing_purposes=["analytics"],
        )
    else:
        raise HTTPException(status_code=400, detail="Invalid compliance check request")

    # Convert to response format
    issues = []
    for issue in result.get("issues", []):
        issues.append(
            ComplianceIssue(
                severity=issue.get("severity", "medium"),
                issue_type=issue.get("issue_type", "compliance"),
                description=issue.get("description", ""),
                recommendation=issue.get("recommendation", ""),
                regulation=issue.get("regulation", "GENERAL"),
                article=issue.get("article"),
            ),
        )

    return ComplianceCheckResponse(
        check_id=uuid.uuid4(),
        check_type=request.check_type,
        is_compliant=result.get("is_compliant", False),
        compliance_score=result.get("compliance_score", 0),
        issues=issues,
        recommendations=result.get("recommendations", []),
        summary=result.get("summary", "Compliance check completed"),
        checked_at=datetime.utcnow(),
        regulations_checked=["GDPR", "CCPA"],
    )


# Privacy Requests (GDPR/CCPA)
@router.post("/privacy-request", response_model=PrivacyRequestResponse)
async def submit_privacy_request(
    request: PrivacyRequest,
    db: AsyncSession = Depends(get_db),
):
    """Submit a privacy request (data access, deletion, etc.)"""
    service = ComplianceService(db)

    # Create audit log for privacy request
    await service.create_audit_log(
        action=ActionType.DATA_EXPORT
        if request.request_type == "export"
        else ActionType.DATA_DELETION,
        resource_type="privacy_request",
        user_email=request.user_email,
        description=f"Privacy request: {request.request_type}",
    )

    request_id = uuid.uuid4()
    expected_completion = datetime.utcnow() + timedelta(days=30)  # GDPR: 30 days

    return PrivacyRequestResponse(
        request_id=request_id,
        request_type=request.request_type,
        status="pending",
        created_at=datetime.utcnow(),
        expected_completion=expected_completion,
        message=f"Privacy request submitted successfully. We will process your {request.request_type} request within 30 days.",
    )


# Compliance Report
@router.get("/report")
async def generate_compliance_report(
    start_date: datetime | None = Query(None),
    end_date: datetime | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Generate compliance report"""
    service = ComplianceService(db)

    if not start_date:
        start_date = datetime.utcnow() - timedelta(days=30)
    if not end_date:
        end_date = datetime.utcnow()

    report = await service.generate_compliance_report(
        start_date=start_date,
        end_date=end_date,
    )

    return report


# Compliance Policies Information
@router.get("/policies")
async def get_compliance_policies():
    """Get all compliance policies"""
    return {
        "policies": [
            {
                "name": p.name,
                "regulation": p.regulation.value,
                "description": p.description,
                "required": p.required,
                "jurisdictions": p.jurisdictions,
            }
            for p in COMPLIANCE_POLICIES
        ],
    }


@router.get("/policies/gdpr")
async def get_gdpr_policies():
    """Get GDPR compliance policies"""
    return {
        "lawful_bases": GDPRPolicies.get_lawful_bases(),
        "user_rights": {k.value: v for k, v in GDPRPolicies.get_user_rights().items()},
        "data_protection_principles": GDPRPolicies.get_data_protection_principles(),
        "consent_requirements": GDPRPolicies.get_consent_requirements(),
        "breach_notification": GDPRPolicies.get_breach_notification_requirements(),
    }


@router.get("/policies/ccpa")
async def get_ccpa_policies():
    """Get CCPA compliance policies"""
    return {
        "consumer_rights": CCPAPolicies.get_consumer_rights(),
        "disclosure_requirements": CCPAPolicies.get_disclosure_requirements(),
        "response_times": CCPAPolicies.get_request_response_times(),
        "do_not_sell": CCPAPolicies.get_do_not_sell_requirements(),
    }


@router.get("/policies/cookies")
async def get_cookie_policies():
    """Get cookie compliance policies"""
    return {
        "categories": CookiePolicy.get_cookie_categories(),
        "consent_requirements": CookiePolicy.get_consent_requirements(),
    }
