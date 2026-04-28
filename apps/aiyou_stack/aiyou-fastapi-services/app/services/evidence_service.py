# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Evidence Service

Generates compliance dossiers and audit reports.
Implements Compliance-as-Documentation™ approach.

Report Types:
- EU AI Act CE-style dossiers
- GDPR Privacy Impact Reports
- DSA Platform Audit Reports
- CA SB 243 AI Harm Detection Audits
- HIPAA Conformance Logs
"""

import hashlib
import json
import logging
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from app.compliance.registry import get_registry
from app.infrastructure.shadowtag_ledger import get_shadowtag_ledger
from app.models.compliance import (
    ComplianceAssessmentResult,
    ComplianceDossier,
    EvidenceArtifact,
    ModuleResult,
    RegulationId,
)

logger = logging.getLogger(__name__)


class EvidenceService:
    """Service for generating compliance evidence and documentation.

    Produces audit-ready reports with cryptographic attestation
    via ShadowTag ledger integration.
    """

    REPORT_TEMPLATES = {
        RegulationId.EU_AI_ACT: "eu_ai_act_dossier",
        RegulationId.GDPR: "gdpr_pia_report",
        RegulationId.DSA: "dsa_platform_audit",
        RegulationId.CA_SB_243: "sb243_harm_audit",
        RegulationId.HIPAA: "hipaa_conformance",
    }

    def __init__(self):
        """Initialize the evidence service."""
        self._registry = get_registry()
        self._ledger = get_shadowtag_ledger()
        logger.info("EvidenceService initialized")

    async def create_dossier(
        self,
        organization_name: str,
        system_name: str,
        system_description: str,
        modules: list[RegulationId],
        assessment_result: ComplianceAssessmentResult | None = None,
    ) -> ComplianceDossier:
        """Create a compliance dossier for an organization.

        Args:
            organization_name: Name of the organization
            system_name: Name of the AI system
            system_description: Description of the AI system
            modules: List of regulation modules covered
            assessment_result: Optional latest assessment result

        Returns:
            ComplianceDossier with all documentation

        """
        dossier_id = str(uuid4())

        dossier = ComplianceDossier(
            dossier_id=dossier_id,
            organization_name=organization_name,
            system_name=system_name,
            system_description=system_description,
            modules=modules,
            latest_assessment=assessment_result,
            artifacts=[],
            shadowtag_chain=[],
        )

        # Record dossier creation in ledger
        entry = await self._ledger.record_event(
            event_type="dossier_created",
            resource_id=dossier_id,
            resource_type="compliance_dossier",
            data={
                "organization": organization_name,
                "system": system_name,
                "modules": [m.value for m in modules],
            },
        )
        dossier.shadowtag_chain.append(entry.entry_id)

        logger.info(f"Created dossier {dossier_id} for {organization_name}")
        return dossier

    async def add_evidence(
        self,
        dossier: ComplianceDossier,
        artifact_type: str,
        name: str,
        description: str,
        content: Any,
        linked_controls: list[str] = None,
    ) -> EvidenceArtifact:
        """Add evidence artifact to a dossier.

        Args:
            dossier: The dossier to add evidence to
            artifact_type: Type of artifact (document, log, screenshot, etc.)
            name: Artifact name
            description: Artifact description
            content: Artifact content (will be hashed)
            linked_controls: Control IDs this evidence supports

        Returns:
            EvidenceArtifact with hash

        """
        artifact_id = str(uuid4())

        # Hash the content
        if isinstance(content, (str, bytes)):
            content_hash = hashlib.sha256(
                content if isinstance(content, bytes) else content.encode(),
            ).hexdigest()
        else:
            content_hash = hashlib.sha256(
                json.dumps(content, sort_keys=True, default=str).encode(),
            ).hexdigest()

        artifact = EvidenceArtifact(
            artifact_id=artifact_id,
            artifact_type=artifact_type,
            name=name,
            description=description,
            sha256_hash=content_hash,
            linked_controls=linked_controls or [],
        )

        dossier.artifacts.append(artifact)

        # Record in ledger
        entry = await self._ledger.record_evidence(
            artifact_id=artifact_id,
            artifact_type=artifact_type,
            metadata={
                "dossier_id": dossier.dossier_id,
                "name": name,
                "content_hash": content_hash,
            },
        )
        dossier.shadowtag_chain.append(entry.entry_id)

        logger.debug(f"Added evidence artifact {artifact_id} to dossier {dossier.dossier_id}")
        return artifact

    async def attest_dossier(
        self,
        dossier: ComplianceDossier,
        signatory: str,
        signature: str,
    ) -> ComplianceDossier:
        """Attest to a compliance dossier.

        Adds cryptographic attestation that the signatory has reviewed
        and approved the dossier contents.

        Args:
            dossier: The dossier to attest
            signatory: Name/ID of the signatory
            signature: Digital signature or attestation statement

        Returns:
            Updated dossier with attestation

        """
        signature_hash = hashlib.sha256(signature.encode()).hexdigest()

        dossier.attestation_date = datetime.now(UTC)
        dossier.attestation_signatory = signatory
        dossier.attestation_signature_hash = signature_hash

        # Record attestation in ledger
        entry = await self._ledger.record_attestation(
            dossier_id=dossier.dossier_id,
            signatory=signatory,
            signature_hash=signature_hash,
        )
        dossier.shadowtag_chain.append(entry.entry_id)

        logger.info(f"Dossier {dossier.dossier_id} attested by {signatory}")
        return dossier

    async def generate_report(
        self,
        assessment_result: ComplianceAssessmentResult,
        report_type: str = "full",
    ) -> dict[str, Any]:
        """Generate a compliance report from assessment results.

        Args:
            assessment_result: The assessment result to report on
            report_type: Type of report (full, summary, executive)

        Returns:
            Report structure with all sections

        """
        report = {
            "report_id": str(uuid4()),
            "generated_at": datetime.now(UTC).isoformat(),
            "report_type": report_type,
            "assessment_id": assessment_result.assessment_id,
            "overall_status": assessment_result.overall_status.value,
            "overall_score": assessment_result.overall_score,
            "sections": [],
        }

        # Executive Summary
        report["sections"].append(
            {
                "title": "Executive Summary",
                "content": self._generate_executive_summary(assessment_result),
            },
        )

        # Scope and Methodology
        report["sections"].append(
            {
                "title": "Scope and Methodology",
                "content": self._generate_scope_section(assessment_result),
            },
        )

        # Per-module results
        for module_result in assessment_result.modules_assessed:
            report["sections"].append(
                {
                    "title": f"{module_result.module_name} Assessment",
                    "module_id": module_result.module_id.value,
                    "status": module_result.status.value,
                    "score": module_result.compliance_score,
                    "controls": [
                        {
                            "control_id": c.control_id,
                            "name": c.control_name,
                            "status": c.status.value,
                            "score": c.score,
                            "findings": c.findings,
                            "remediation": c.remediation,
                        }
                        for c in module_result.control_results
                    ],
                    "recommendations": module_result.recommendations,
                },
            )

        # Critical Findings
        if assessment_result.critical_findings:
            report["sections"].append(
                {"title": "Critical Findings", "findings": assessment_result.critical_findings},
            )

        # Recommendations
        report["sections"].append(
            {"title": "Recommendations", "items": assessment_result.recommendations},
        )

        # Audit Trail
        report["sections"].append(
            {
                "title": "Audit Trail",
                "audit_hash": assessment_result.audit_hash,
                "timestamp": assessment_result.timestamp.isoformat(),
            },
        )

        # Record report generation in ledger
        await self._ledger.record_event(
            event_type="report_generated",
            resource_id=report["report_id"],
            resource_type="compliance_report",
            data={
                "assessment_id": assessment_result.assessment_id,
                "report_type": report_type,
                "overall_score": assessment_result.overall_score,
            },
        )

        return report

    def _generate_executive_summary(self, result: ComplianceAssessmentResult) -> str:
        """Generate executive summary text."""
        module_names = [m.module_name for m in result.modules_assessed]

        if result.overall_score >= 0.9:
            status_text = "demonstrates strong compliance"
        elif result.overall_score >= 0.7:
            status_text = "shows adequate compliance with room for improvement"
        elif result.overall_score >= 0.5:
            status_text = "requires significant remediation efforts"
        else:
            status_text = "has critical compliance gaps requiring immediate attention"

        summary = (
            f"This compliance assessment evaluated the system against "
            f"{len(module_names)} regulatory framework{'s' if len(module_names) > 1 else ''}: "
            f"{', '.join(module_names)}. "
            f"\n\n"
            f"The overall compliance score is {result.overall_score:.0%}, which "
            f"{status_text}. "
            f"\n\n"
            f"Of {result.total_controls} controls assessed, "
            f"{result.total_compliant} are compliant, and "
            f"{result.total_non_compliant} require remediation."
        )

        if result.requires_human_review:
            summary += "\n\n**Note:** This assessment requires human review before finalizing."

        return summary

    def _generate_scope_section(self, result: ComplianceAssessmentResult) -> str:
        """Generate scope and methodology section."""
        return (
            f"**Assessment Date:** {result.timestamp.strftime('%Y-%m-%d %H:%M UTC')}\n\n"
            f"**Frameworks Assessed:**\n"
            + "\n".join(f"- {m.module_name}" for m in result.modules_assessed)
            + "\n\n"
            "**Methodology:**\n"
            "This assessment was performed using the ActiveShield Modular Compliance "
            "Framework (MCF), which implements automated control validation against "
            "selected regulatory requirements. The assessment follows the "
            "Compliance-as-Documentation approach, providing cryptographic proof "
            "of assessment activities via ShadowTag audit logging."
        )

    async def generate_module_report(
        self,
        module_result: ModuleResult,
        include_checklist: bool = True,
    ) -> dict[str, Any]:
        """Generate a detailed report for a single module.

        Args:
            module_result: The module assessment result
            include_checklist: Whether to include the compliance checklist

        Returns:
            Module-specific report

        """
        report = {
            "report_id": str(uuid4()),
            "generated_at": datetime.now(UTC).isoformat(),
            "module_id": module_result.module_id.value,
            "module_name": module_result.module_name,
            "status": module_result.status.value,
            "compliance_score": module_result.compliance_score,
            "risk_tier": module_result.risk_tier.value if module_result.risk_tier else None,
            "controls_summary": {
                "total": module_result.controls_assessed,
                "compliant": module_result.controls_compliant,
                "non_compliant": module_result.controls_non_compliant,
                "partial": module_result.controls_partial,
            },
            "control_details": [
                {
                    "control_id": c.control_id,
                    "name": c.control_name,
                    "status": c.status.value,
                    "score": c.score,
                    "evidence": c.evidence,
                    "findings": c.findings,
                    "remediation": c.remediation,
                }
                for c in module_result.control_results
            ],
            "recommendations": module_result.recommendations,
            "requires_human_review": module_result.requires_human_review,
        }

        if include_checklist:
            module = self._registry.get_module(module_result.module_id)
            if module:
                report["checklist"] = module.generate_checklist()

        return report

    async def get_audit_proof(self, assessment_id: str) -> dict[str, Any]:
        """Get cryptographic audit proof for an assessment.

        Returns the chain of custody proof from ShadowTag ledger.
        """
        entries = await self._ledger.get_entries_for_resource(assessment_id)

        if not entries:
            return {"error": "No audit entries found", "assessment_id": assessment_id}

        return {
            "assessment_id": assessment_id,
            "audit_entries": len(entries),
            "chain_proof": [
                {
                    "entry_id": e.entry_id,
                    "timestamp": e.timestamp,
                    "event_type": e.event_type,
                    "data_hash": e.data_hash,
                    "previous_hash": e.previous_hash,
                }
                for e in entries
            ],
            "verification_url": f"https://audit.activeshield.ai/verify/{assessment_id}",
        }


# Singleton instance
_evidence_service: EvidenceService | None = None


def get_evidence_service() -> EvidenceService:
    """Get or create the evidence service singleton."""
    global _evidence_service
    if _evidence_service is None:
        _evidence_service = EvidenceService()
    return _evidence_service
