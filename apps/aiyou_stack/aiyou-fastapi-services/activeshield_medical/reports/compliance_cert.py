"""
Compliance Certificate Generator
=================================

Generates formal compliance certificates for ActiveShieldMedical clients.
These certificates serve as evidence of due diligence for:
- Litigation defense
- Insurance claims
- Regulatory audits
- Contract compliance
"""

import hashlib
from datetime import datetime
from typing import Any


class ComplianceCertificateGenerator:
    """
    Generates compliance certificates for ActiveShieldMedical sessions.

    Certificate Types:
    1. Session Certificate - Per-session compliance attestation
    2. Periodic Certificate - Weekly/Monthly compliance summary
    3. Incident Report - Specific violation/crisis documentation
    4. Audit Package - Full evidence export for legal
    """

    CERTIFICATE_VERSION = "1.0"

    def __init__(self):
        self._issued_certificates: list[dict[str, Any]] = []

    def generate_session_certificate(
        self,
        session_id: str,
        customer_name: str,
        metrics: dict[str, Any],
        frameworks_checked: list[str],
    ) -> dict[str, Any]:
        """
        Generate certificate for a single session.

        Args:
            session_id: The session identifier
            customer_name: Client/customer name
            metrics: Session compliance metrics
            frameworks_checked: List of frameworks validated

        Returns:
            Formal certificate document
        """
        cert_id = self._generate_cert_id(session_id)
        issued_at = datetime.utcnow()

        # Determine compliance status
        violations = metrics.get("violations", 0)
        compliance_status = "FULLY_COMPLIANT" if violations == 0 else "COMPLIANT_WITH_FINDINGS"

        certificate = {
            "certificate_type": "SESSION_COMPLIANCE",
            "certificate_id": cert_id,
            "version": self.CERTIFICATE_VERSION,
            "session_id": session_id,
            "customer_name": customer_name,
            "issued_at": issued_at.isoformat(),
            "valid_until": None,  # Session certs don't expire
            "compliance_status": compliance_status,
            "frameworks_validated": frameworks_checked,
            "metrics_summary": {
                "total_checks": metrics.get("total_checks", 0),
                "passed_checks": metrics.get("passed_checks", 0),
                "compliance_rate": metrics.get("compliance_rate", 100.0),
                "violations": violations,
                "warnings": metrics.get("warnings", 0),
                "crisis_interventions": metrics.get("crisis_interventions", 0),
            },
            "attestation": self._generate_attestation(
                session_id,
                customer_name,
                compliance_status,
                frameworks_checked,
            ),
            "legal_disclaimer": (
                "This certificate attests that the referenced session was processed "
                "through ActiveShieldMedical's compliance framework. This certificate "
                "does not guarantee absolute compliance with all applicable laws and "
                "regulations. Clients remain responsible for their own compliance obligations."
            ),
            "verification": {
                "hash": self._generate_verification_hash(cert_id, session_id, issued_at),
                "method": "SHA-256",
                "verify_url": f"https://activeshieldmedical.com/verify/{cert_id}",
            },
        }

        self._issued_certificates.append(certificate)
        return certificate

    def generate_periodic_certificate(
        self,
        customer_id: str,
        customer_name: str,
        period_start: datetime,
        period_end: datetime,
        aggregate_metrics: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Generate periodic (weekly/monthly) compliance certificate.
        """
        cert_id = self._generate_cert_id(f"{customer_id}:{period_start.isoformat()}")
        issued_at = datetime.utcnow()

        total_sessions = aggregate_metrics.get("total_sessions", 0)
        compliant_sessions = aggregate_metrics.get("compliant_sessions", 0)
        overall_rate = (compliant_sessions / total_sessions * 100) if total_sessions > 0 else 100.0

        certificate = {
            "certificate_type": "PERIODIC_COMPLIANCE",
            "certificate_id": cert_id,
            "version": self.CERTIFICATE_VERSION,
            "customer_id": customer_id,
            "customer_name": customer_name,
            "issued_at": issued_at.isoformat(),
            "period": {
                "start": period_start.isoformat(),
                "end": period_end.isoformat(),
                "duration_days": (period_end - period_start).days,
            },
            "compliance_summary": {
                "total_sessions": total_sessions,
                "compliant_sessions": compliant_sessions,
                "non_compliant_sessions": total_sessions - compliant_sessions,
                "overall_compliance_rate": round(overall_rate, 2),
            },
            "event_summary": {
                "total_checks": aggregate_metrics.get("total_checks", 0),
                "violations": aggregate_metrics.get("total_violations", 0),
                "crisis_events": aggregate_metrics.get("crisis_events", 0),
                "human_escalations": aggregate_metrics.get("human_escalations", 0),
            },
            "frameworks_coverage": {
                "SB_243": aggregate_metrics.get("sb243_checks", 0),
                "HIPAA": aggregate_metrics.get("hipaa_checks", 0),
                "CCPA": aggregate_metrics.get("ccpa_checks", 0),
            },
            "attestation": (
                f"This certifies that {customer_name} utilized ActiveShieldMedical's "
                f"compliance framework for {total_sessions} sessions during the period "
                f"{period_start.strftime('%B %d, %Y')} to {period_end.strftime('%B %d, %Y')}. "
                f"Overall compliance rate: {overall_rate:.1f}%."
            ),
            "verification": {
                "hash": self._generate_verification_hash(cert_id, customer_id, issued_at),
                "method": "SHA-256",
            },
        }

        self._issued_certificates.append(certificate)
        return certificate

    def generate_incident_report(
        self,
        incident_id: str,
        session_id: str,
        customer_name: str,
        incident_type: str,
        incident_details: dict[str, Any],
        remediation_taken: list[str],
    ) -> dict[str, Any]:
        """
        Generate incident report for compliance violation or crisis.
        """
        cert_id = self._generate_cert_id(f"incident:{incident_id}")
        issued_at = datetime.utcnow()

        report = {
            "report_type": "INCIDENT_REPORT",
            "report_id": cert_id,
            "incident_id": incident_id,
            "session_id": session_id,
            "customer_name": customer_name,
            "issued_at": issued_at.isoformat(),
            "incident": {
                "type": incident_type,
                "severity": incident_details.get("severity", "unknown"),
                "detected_at": incident_details.get("detected_at"),
                "description": incident_details.get("description"),
            },
            "detection": {
                "component": incident_details.get("detecting_component"),
                "rule_triggered": incident_details.get("rule_id"),
                "confidence": incident_details.get("confidence"),
            },
            "response": {
                "action_taken": incident_details.get("action_taken"),
                "escalated_to_human": incident_details.get("escalated", False),
                "crisis_protocol_activated": incident_details.get("crisis_protocol", False),
            },
            "remediation": {
                "steps_taken": remediation_taken,
                "resolved": incident_details.get("resolved", False),
                "resolved_at": incident_details.get("resolved_at"),
            },
            "regulatory_implications": {
                "frameworks_affected": incident_details.get("frameworks_affected", []),
                "reportable": incident_details.get("reportable", False),
                "notification_required": incident_details.get("notification_required", False),
            },
            "verification": {
                "hash": self._generate_verification_hash(cert_id, incident_id, issued_at),
            },
        }

        self._issued_certificates.append(report)
        return report

    def _generate_attestation(
        self,
        session_id: str,
        customer_name: str,
        status: str,
        frameworks: list[str],
    ) -> str:
        """Generate formal attestation statement"""
        frameworks_str = ", ".join(frameworks)
        return (
            f"ActiveShieldMedical hereby attests that session '{session_id}' "
            f"for {customer_name} was processed through our three-tier defense "
            f"architecture (pre-hoc, mid-hoc, post-hoc) and validated against "
            f"the following regulatory frameworks: {frameworks_str}. "
            f"Compliance status: {status.replace('_', ' ')}."
        )

    def _generate_cert_id(self, seed: str) -> str:
        """Generate unique certificate ID"""
        timestamp = datetime.utcnow().isoformat()
        content = f"cert:{seed}:{timestamp}"
        return f"ASM-{hashlib.sha256(content.encode()).hexdigest()[:12].upper()}"

    def _generate_verification_hash(
        self,
        cert_id: str,
        reference: str,
        issued_at: datetime,
    ) -> str:
        """Generate verification hash for certificate"""
        content = f"{cert_id}:{reference}:{issued_at.isoformat()}"
        return hashlib.sha256(content.encode()).hexdigest()

    def get_issued_certificates(
        self,
        cert_type: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Get list of issued certificates"""
        certs = self._issued_certificates
        if cert_type:
            certs = [c for c in certs if c.get("certificate_type") == cert_type]
        return certs[-limit:]


# Global instance
cert_generator = ComplianceCertificateGenerator()
