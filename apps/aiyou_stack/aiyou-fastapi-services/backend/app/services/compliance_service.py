"""Compliance Service - Business logic for compliance operations
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import and_, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.audit_log import ActionType, AuditLog
from app.models.consent import ConsentMethod, ConsentType, UserConsent
from app.models.data_retention import DataCategory, DataRetentionPolicy
from app.services.agents.compliance_expert import ComplianceExpertAgent

logger = logging.getLogger(__name__)


class ComplianceService:
    """Service for handling compliance-related operations"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.agent = ComplianceExpertAgent()

    # Audit Log Methods
    async def create_audit_log(
        self,
        action: ActionType,
        resource_type: str,
        user_id: uuid.UUID | None = None,
        user_email: str | None = None,
        resource_id: str | None = None,
        description: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        request_method: str | None = None,
        request_path: str | None = None,
        status_code: int | None = None,
        success: str = "success",
        error_message: str | None = None,
        changes: dict[str, Any] | None = None,
    ) -> AuditLog:
        """Create an audit log entry"""
        # Calculate retention date based on policy
        retention_date = datetime.utcnow() + timedelta(days=settings.AUDIT_LOG_RETENTION_DAYS)

        audit_log = AuditLog(
            user_id=user_id,
            user_email=user_email,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            description=description,
            changes=changes,
            ip_address=ip_address,
            user_agent=user_agent,
            request_method=request_method,
            request_path=request_path,
            status_code=status_code,
            success=success,
            error_message=error_message,
            retention_until=retention_date.isoformat(),
        )

        self.db.add(audit_log)
        await self.db.commit()
        await self.db.refresh(audit_log)

        logger.info(f"Audit log created: {action} on {resource_type} by {user_email}")
        return audit_log

    async def get_audit_logs(
        self,
        user_id: uuid.UUID | None = None,
        action: ActionType | None = None,
        resource_type: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[AuditLog], int]:
        """Get audit logs with filtering"""
        query = select(AuditLog)

        # Apply filters
        filters = []
        if user_id:
            filters.append(AuditLog.user_id == user_id)
        if action:
            filters.append(AuditLog.action == action)
        if resource_type:
            filters.append(AuditLog.resource_type == resource_type)
        if start_date:
            filters.append(AuditLog.created_at >= start_date)
        if end_date:
            filters.append(AuditLog.created_at <= end_date)

        if filters:
            query = query.where(and_(*filters))

        # Get total count
        count_query = select(AuditLog).where(and_(*filters)) if filters else select(AuditLog)
        total_result = await self.db.execute(count_query)
        total = len(total_result.scalars().all())

        # Apply pagination and ordering
        query = query.order_by(desc(AuditLog.created_at)).limit(limit).offset(offset)

        result = await self.db.execute(query)
        logs = result.scalars().all()

        return logs, total

    # Consent Methods
    async def create_consent(
        self,
        user_id: uuid.UUID,
        consent_type: ConsentType,
        consent_method: ConsentMethod,
        is_granted: bool = True,
        user_email: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        consent_text: str | None = None,
        consent_version: str = "1.0",
        purpose: str | None = None,
    ) -> UserConsent:
        """Create a consent record"""
        expires_at = None
        if is_granted and settings.CONSENT_EXPIRY_DAYS > 0:
            expires_at = (
                datetime.utcnow() + timedelta(days=settings.CONSENT_EXPIRY_DAYS)
            ).isoformat()

        consent = UserConsent(
            user_id=user_id,
            user_email=user_email,
            consent_type=consent_type,
            consent_method=consent_method,
            is_granted=is_granted,
            granted_at=datetime.utcnow().isoformat(),
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent,
            consent_text=consent_text,
            consent_version=consent_version,
            purpose=purpose,
        )

        self.db.add(consent)
        await self.db.commit()
        await self.db.refresh(consent)

        # Create audit log
        await self.create_audit_log(
            action=ActionType.CONSENT_GRANTED if is_granted else ActionType.CONSENT_REVOKED,
            resource_type="consent",
            user_id=user_id,
            user_email=user_email,
            resource_id=str(consent.id),
            description=f"Consent {consent_type.value} {'granted' if is_granted else 'revoked'}",
            ip_address=ip_address,
            user_agent=user_agent,
        )

        logger.info(f"Consent created: {consent_type} for user {user_id}")
        return consent

    async def get_user_consents(
        self, user_id: uuid.UUID, consent_type: ConsentType | None = None, active_only: bool = True,
    ) -> list[UserConsent]:
        """Get user's consent records"""
        query = select(UserConsent).where(UserConsent.user_id == user_id)

        if consent_type:
            query = query.where(UserConsent.consent_type == consent_type)

        if active_only:
            query = query.where(
                and_(
                    UserConsent.is_active,
                    UserConsent.is_granted,
                    UserConsent.revoked_at is None,
                ),
            )

        result = await self.db.execute(query)
        consents = result.scalars().all()

        return consents

    async def revoke_consent(self, consent_id: uuid.UUID, user_id: uuid.UUID) -> UserConsent:
        """Revoke a consent"""
        query = select(UserConsent).where(
            and_(UserConsent.id == consent_id, UserConsent.user_id == user_id),
        )
        result = await self.db.execute(query)
        consent = result.scalar_one_or_none()

        if not consent:
            raise ValueError("Consent not found")

        consent.is_granted = False
        consent.is_active = False
        consent.revoked_at = datetime.utcnow().isoformat()

        await self.db.commit()
        await self.db.refresh(consent)

        # Create audit log
        await self.create_audit_log(
            action=ActionType.CONSENT_REVOKED,
            resource_type="consent",
            user_id=user_id,
            resource_id=str(consent_id),
            description=f"Consent {consent.consent_type.value} revoked",
        )

        logger.info(f"Consent revoked: {consent_id}")
        return consent

    # Data Retention Methods
    async def get_retention_policies(
        self, data_category: DataCategory | None = None, active_only: bool = True,
    ) -> list[DataRetentionPolicy]:
        """Get data retention policies"""
        query = select(DataRetentionPolicy)

        if data_category:
            query = query.where(DataRetentionPolicy.data_category == data_category)

        if active_only:
            query = query.where(DataRetentionPolicy.is_active)

        result = await self.db.execute(query)
        policies = result.scalars().all()

        return policies

    # AI-Powered Compliance Analysis
    async def analyze_endpoint_compliance(
        self, endpoint_code: str, endpoint_path: str, request_method: str = "GET",
    ) -> dict[str, Any]:
        """Use AI agent to analyze endpoint for compliance"""
        result = await self.agent.analyze_endpoint(
            endpoint_code=endpoint_code, endpoint_path=endpoint_path, request_method=request_method,
        )

        # Log the compliance check
        await self.create_audit_log(
            action=ActionType.COMPLIANCE_CHECK,
            resource_type="endpoint",
            resource_id=endpoint_path,
            description=f"Compliance check for {request_method} {endpoint_path}",
            success="success" if result.get("is_compliant") else "failure",
        )

        return result

    async def check_consent_requirements(
        self, user_location: str, data_categories: list[str], processing_purposes: list[str],
    ) -> dict[str, Any]:
        """Check what consent is required"""
        result = await self.agent.check_consent_requirements(
            user_location=user_location,
            data_categories=data_categories,
            processing_purposes=processing_purposes,
        )

        return result

    async def generate_compliance_report(
        self, start_date: datetime, end_date: datetime,
    ) -> dict[str, Any]:
        """Generate comprehensive compliance report"""
        # Get audit logs for period
        logs, total_logs = await self.get_audit_logs(
            start_date=start_date, end_date=end_date, limit=10000,
        )

        # Get consent records
        consent_query = select(UserConsent).where(
            UserConsent.created_at >= start_date, UserConsent.created_at <= end_date,
        )
        consent_result = await self.db.execute(consent_query)
        consents = consent_result.scalars().all()

        report = {
            "report_id": uuid.uuid4(),
            "generated_at": datetime.utcnow(),
            "period_start": start_date,
            "period_end": end_date,
            "audit_logs": total_logs,
            "consent_records": len(consents),
            "consent_granted": len([c for c in consents if c.is_granted]),
            "consent_revoked": len([c for c in consents if not c.is_granted]),
            "summary": f"Compliance report for {start_date.date()} to {end_date.date()}",
        }

        return report
