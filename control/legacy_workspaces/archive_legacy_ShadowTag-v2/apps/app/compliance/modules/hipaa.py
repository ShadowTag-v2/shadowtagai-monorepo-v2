# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
HIPAA Compliance Module

Implements the Health Insurance Portability and Accountability Act requirements.
Focus areas:
- Protected Health Information (PHI) handling
- Privacy Rule compliance
- Security Rule compliance
- Business Associate Agreements
- Breach notification

Reference: 45 CFR Parts 160, 162, and 164
"""

import re
from datetime import datetime

from app.compliance.modules.base import ComplianceModule
from app.compliance.registry import register_module
from app.models.compliance import (
    AssessmentInput,
    ComplianceStatus,
    ControlDefinition,
    ControlResult,
    Jurisdiction,
    ModuleMetadata,
    RegulationId,
    RiskTier,
    ValidationRule,
    ValidationViolation,
)


@register_module(RegulationId.HIPAA)
class HIPAAModule(ComplianceModule):
    """
    HIPAA Compliance Module

    Covers the three main HIPAA Rules:
    - Privacy Rule (45 CFR Part 164 Subpart E)
    - Security Rule (45 CFR Part 164 Subpart C)
    - Breach Notification Rule (45 CFR Part 164 Subpart D)
    """

    # PHI identifiers per HIPAA Safe Harbor (18 identifiers)
    PHI_IDENTIFIERS = [
        "name",
        "address",
        "dates",
        "phone",
        "fax",
        "email",
        "ssn",
        "medical_record",
        "health_plan",
        "account_number",
        "license",
        "vehicle_id",
        "device_id",
        "url",
        "ip_address",
        "biometric",
        "photo",
        "other_identifier",
    ]

    # PHI detection patterns
    PHI_PATTERNS = {
        "medical_record": r"\b(MRN|medical\s+record)\s*[:#]?\s*\d+\b",
        "diagnosis": r"\b(diagnosed\s+with|diagnosis[:\s]+|ICD[-\s]?\d+)\b",
        "medication": r"\b(prescribed|medication|rx|dosage)[\s:]+\w+\b",
        "procedure": r"\b(procedure|surgery|treatment)[:\s]+\w+\b",
        "ssn": r"\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b",
        "dob": r"\b(dob|date\s+of\s+birth|born\s+on)[:\s]+\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}\b",
        "health_plan_id": r"\b(member\s+id|policy\s+number|health\s+plan)[:\s#]+\w+\b",
    }

    # Sensitive health conditions
    SENSITIVE_CONDITIONS = [
        "hiv",
        "aids",
        "mental health",
        "psychiatric",
        "substance abuse",
        "addiction",
        "std",
        "genetic",
        "pregnancy",
        "abortion",
    ]

    def _define_metadata(self) -> ModuleMetadata:
        return ModuleMetadata(
            id=RegulationId.HIPAA,
            name="Health Insurance Portability and Accountability Act",
            short_name="HIPAA",
            version="2013.omnibus",
            jurisdiction=Jurisdiction.US,
            description=("Federal law protecting sensitive patient health information from disclosure without patient consent or knowledge."),
            effective_date=datetime(1996, 8, 21),
            articles=[
                "Privacy Rule - Use and Disclosure of PHI",
                "Security Rule - Administrative Safeguards",
                "Security Rule - Physical Safeguards",
                "Security Rule - Technical Safeguards",
                "Breach Notification Rule",
                "Minimum Necessary Standard",
                "Business Associate Requirements",
            ],
            official_url="https://www.hhs.gov/hipaa/index.html",
            pricing_addon_usd=75.0,
        )

    def _define_controls(self) -> list[ControlDefinition]:
        return [
            # Privacy Rule Controls
            ControlDefinition(
                control_id="HIPAA-PR-1",
                name="PHI Use and Disclosure Policies",
                description="Policies governing use and disclosure of PHI",
                article_ref="45 CFR 164.502",
                required_evidence=[
                    "Privacy policies",
                    "Use/disclosure procedures",
                    "Patient consent forms",
                ],
            ),
            ControlDefinition(
                control_id="HIPAA-PR-2",
                name="Minimum Necessary Standard",
                description="Limit PHI access to minimum necessary for intended purpose",
                article_ref="45 CFR 164.502(b)",
                required_evidence=[
                    "Access control documentation",
                    "Role-based access matrix",
                ],
            ),
            ControlDefinition(
                control_id="HIPAA-PR-3",
                name="Patient Rights",
                description="Provide patients right to access, amend, and restrict PHI",
                article_ref="45 CFR 164.520-528",
                required_evidence=[
                    "Patient rights procedures",
                    "Access request forms",
                    "Amendment procedures",
                ],
            ),
            ControlDefinition(
                control_id="HIPAA-PR-4",
                name="Notice of Privacy Practices",
                description="Provide notice of privacy practices to patients",
                article_ref="45 CFR 164.520",
                required_evidence=["NPP document", "Distribution records"],
            ),
            # Security Rule - Administrative Safeguards
            ControlDefinition(
                control_id="HIPAA-AS-1",
                name="Security Management Process",
                description="Risk analysis and risk management program",
                article_ref="45 CFR 164.308(a)(1)",
                required_evidence=[
                    "Risk assessment report",
                    "Risk management plan",
                    "Security policies",
                ],
            ),
            ControlDefinition(
                control_id="HIPAA-AS-2",
                name="Workforce Security",
                description="Ensure appropriate workforce access to ePHI",
                article_ref="45 CFR 164.308(a)(3)",
                required_evidence=[
                    "Authorization procedures",
                    "Workforce clearance",
                    "Termination procedures",
                ],
            ),
            ControlDefinition(
                control_id="HIPAA-AS-3",
                name="Security Awareness Training",
                description="Security awareness and training program",
                article_ref="45 CFR 164.308(a)(5)",
                required_evidence=[
                    "Training program",
                    "Training records",
                    "Security reminders",
                ],
            ),
            ControlDefinition(
                control_id="HIPAA-AS-4",
                name="Contingency Plan",
                description="Data backup, disaster recovery, and emergency mode plans",
                article_ref="45 CFR 164.308(a)(7)",
                required_evidence=[
                    "Backup procedures",
                    "Disaster recovery plan",
                    "Emergency mode procedures",
                ],
            ),
            # Security Rule - Technical Safeguards
            ControlDefinition(
                control_id="HIPAA-TS-1",
                name="Access Control",
                description="Technical policies for electronic access to ePHI",
                article_ref="45 CFR 164.312(a)",
                required_evidence=[
                    "Unique user identification",
                    "Emergency access procedures",
                    "Automatic logoff",
                    "Encryption standards",
                ],
            ),
            ControlDefinition(
                control_id="HIPAA-TS-2",
                name="Audit Controls",
                description="Mechanisms to record and examine system activity",
                article_ref="45 CFR 164.312(b)",
                required_evidence=["Audit logging", "Log review procedures"],
            ),
            ControlDefinition(
                control_id="HIPAA-TS-3",
                name="Transmission Security",
                description="Protect ePHI transmitted over networks",
                article_ref="45 CFR 164.312(e)",
                required_evidence=["Encryption in transit", "Integrity controls"],
            ),
            # Business Associate Requirements
            ControlDefinition(
                control_id="HIPAA-BA-1",
                name="Business Associate Agreements",
                description="Written contracts with business associates handling PHI",
                article_ref="45 CFR 164.502(e)",
                required_evidence=["BAA templates", "Executed BAAs", "BA inventory"],
            ),
            # Breach Notification
            ControlDefinition(
                control_id="HIPAA-BN-1",
                name="Breach Notification Procedures",
                description="Procedures for breach identification and notification",
                article_ref="45 CFR 164.400-414",
                required_evidence=[
                    "Breach assessment procedures",
                    "Notification templates",
                    "Breach log",
                ],
            ),
        ]

    def _define_validation_rules(self) -> list[ValidationRule]:
        return [
            ValidationRule(
                rule_id="HIPAA-VAL-001",
                name="PHI Identifier Detection",
                description="Detect PHI identifiers in content",
                category="phi_exposure",
                severity="critical",
                auto_check=True,
            ),
            ValidationRule(
                rule_id="HIPAA-VAL-002",
                name="Medical Information Detection",
                description="Detect medical diagnoses, procedures, medications",
                category="medical_data",
                severity="critical",
                auto_check=True,
            ),
            ValidationRule(
                rule_id="HIPAA-VAL-003",
                name="Sensitive Condition Detection",
                description="Detect highly sensitive health conditions",
                category="sensitive_phi",
                severity="critical",
                auto_check=True,
            ),
            ValidationRule(
                rule_id="HIPAA-VAL-004",
                name="Minimum Necessary Check",
                description="Check for excess PHI beyond minimum necessary",
                category="minimum_necessary",
                severity="high",
                auto_check=True,
            ),
        ]

    async def assess_control(self, control: ControlDefinition, input_data: AssessmentInput) -> ControlResult:
        """Assess a single HIPAA control."""
        metadata = input_data.metadata

        # PHI Handling check
        if control.control_id == "HIPAA-PR-1":
            if input_data.contains_phi:
                has_policies = metadata.get("privacy_policies_implemented", False)
                if has_policies:
                    return ControlResult(
                        control_id=control.control_id,
                        control_name=control.name,
                        module_id=self.module_id,
                        status=ComplianceStatus.COMPLIANT,
                        score=1.0,
                        evidence="Privacy policies in place for PHI handling",
                    )
                else:
                    return ControlResult(
                        control_id=control.control_id,
                        control_name=control.name,
                        module_id=self.module_id,
                        status=ComplianceStatus.NON_COMPLIANT,
                        score=0.0,
                        findings=["PHI present but privacy policies not documented"],
                        remediation="Implement and document PHI use/disclosure policies",
                    )
            return ControlResult(
                control_id=control.control_id,
                control_name=control.name,
                module_id=self.module_id,
                status=ComplianceStatus.NOT_APPLICABLE,
                score=1.0,
                evidence="No PHI in scope",
            )

        # Minimum Necessary
        if control.control_id == "HIPAA-PR-2":
            if input_data.contains_phi:
                purpose = metadata.get("phi_purpose", "")
                phi_elements = metadata.get("phi_elements", [])
                if purpose and len(phi_elements) <= 3:  # Reasonable limit
                    return ControlResult(
                        control_id=control.control_id,
                        control_name=control.name,
                        module_id=self.module_id,
                        status=ComplianceStatus.COMPLIANT,
                        score=1.0,
                        evidence=f"PHI limited to minimum necessary for: {purpose}",
                    )
                elif len(phi_elements) > 3:
                    return ControlResult(
                        control_id=control.control_id,
                        control_name=control.name,
                        module_id=self.module_id,
                        status=ComplianceStatus.PARTIAL,
                        score=0.5,
                        findings=[f"Multiple PHI elements ({len(phi_elements)}) may exceed minimum necessary"],
                        remediation="Review and limit PHI to minimum necessary for purpose",
                    )

        # Business Associate Agreement
        if control.control_id == "HIPAA-BA-1":
            uses_ba = metadata.get("uses_business_associate", False)
            if uses_ba:
                has_baa = metadata.get("baa_in_place", False)
                if has_baa:
                    return ControlResult(
                        control_id=control.control_id,
                        control_name=control.name,
                        module_id=self.module_id,
                        status=ComplianceStatus.COMPLIANT,
                        score=1.0,
                        evidence="BAA executed with business associate",
                    )
                else:
                    return ControlResult(
                        control_id=control.control_id,
                        control_name=control.name,
                        module_id=self.module_id,
                        status=ComplianceStatus.NON_COMPLIANT,
                        score=0.0,
                        findings=["Business associate used without BAA"],
                        remediation="Execute Business Associate Agreement before sharing PHI",
                    )
            return ControlResult(
                control_id=control.control_id,
                control_name=control.name,
                module_id=self.module_id,
                status=ComplianceStatus.NOT_APPLICABLE,
                score=1.0,
                evidence="No business associates in scope",
            )

        # Encryption (Technical Safeguard)
        if control.control_id == "HIPAA-TS-1":
            if input_data.contains_phi:
                encryption_enabled = metadata.get("encryption_enabled", False)
                if encryption_enabled:
                    return ControlResult(
                        control_id=control.control_id,
                        control_name=control.name,
                        module_id=self.module_id,
                        status=ComplianceStatus.COMPLIANT,
                        score=1.0,
                        evidence="ePHI encryption implemented",
                    )
                else:
                    return ControlResult(
                        control_id=control.control_id,
                        control_name=control.name,
                        module_id=self.module_id,
                        status=ComplianceStatus.NON_COMPLIANT,
                        score=0.0,
                        findings=["ePHI not encrypted"],
                        remediation="Implement encryption for ePHI at rest and in transit",
                    )

        # Default
        return ControlResult(
            control_id=control.control_id,
            control_name=control.name,
            module_id=self.module_id,
            status=ComplianceStatus.PARTIAL,
            score=0.5,
            findings=["Documentation review required"],
            remediation=f"Provide evidence for {control.name}",
        )

    def determine_risk_tier(self, input_data: AssessmentInput) -> RiskTier | None:
        """Determine HIPAA risk tier."""
        # PHI always means HIGH risk
        if input_data.contains_phi:
            # Check for sensitive conditions
            content_type = input_data.content_type.lower()
            for sensitive in self.SENSITIVE_CONDITIONS:
                if sensitive in content_type:
                    return RiskTier.UNACCEPTABLE  # Requires extra protections

            return RiskTier.HIGH

        # Health-related but no PHI
        if input_data.metadata.get("health_context", False):
            return RiskTier.LIMITED

        return RiskTier.MINIMAL

    async def _check_validation_rule(self, rule: ValidationRule, content: str, context: str | None) -> ValidationViolation | None:
        """Check HIPAA validation rules against content."""
        content_lower = content.lower()

        if rule.rule_id == "HIPAA-VAL-001":
            # PHI Identifier Detection
            for phi_type, pattern in self.PHI_PATTERNS.items():
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    return ValidationViolation(
                        module_id=self.module_id,
                        rule_id=rule.rule_id,
                        severity="critical",
                        description=f"PHI detected: {phi_type}",
                        location=match.group(),
                        suggested_fix="De-identify or remove PHI before disclosure",
                        article_reference="HIPAA Privacy Rule - 45 CFR 164.514",
                    )

        if rule.rule_id == "HIPAA-VAL-002":
            # Medical Information Detection
            medical_patterns = [
                (r"\bdiagnos\w*\s+(with|of|:)\s+\w+", "diagnosis"),
                (r"\bprescrib\w*\s+\w+", "prescription"),
                (r"\btreatment\s+(for|of|plan)", "treatment"),
                (r"\bpatient\s+(has|had|is|was)", "patient information"),
            ]
            for pattern, info_type in medical_patterns:
                match = re.search(pattern, content_lower)
                if match:
                    return ValidationViolation(
                        module_id=self.module_id,
                        rule_id=rule.rule_id,
                        severity="critical",
                        description=f"Medical information detected: {info_type}",
                        location=match.group(),
                        suggested_fix="Ensure proper authorization for medical information disclosure",
                        article_reference="HIPAA Privacy Rule - 45 CFR 164.502",
                    )

        if rule.rule_id == "HIPAA-VAL-003":
            # Sensitive Condition Detection
            for condition in self.SENSITIVE_CONDITIONS:
                if condition in content_lower:
                    # Check if it's in a personal context
                    personal_indicators = [
                        "my",
                        "their",
                        "patient",
                        "client",
                        "mr.",
                        "mrs.",
                        "ms.",
                    ]
                    if any(ind in content_lower for ind in personal_indicators):
                        return ValidationViolation(
                            module_id=self.module_id,
                            rule_id=rule.rule_id,
                            severity="critical",
                            description=f"Sensitive health condition detected: {condition}",
                            location=condition,
                            suggested_fix="Extra protections required for sensitive health information",
                            article_reference="HIPAA Privacy Rule - Special Protections",
                        )

        return None
