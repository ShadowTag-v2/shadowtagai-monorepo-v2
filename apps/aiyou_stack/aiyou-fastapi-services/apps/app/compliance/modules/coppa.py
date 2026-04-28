# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""COPPA Compliance Module

Implements the Children's Online Privacy Protection Act requirements.
Focus areas:
- Parental consent before collecting data from children under 13
- Privacy policy requirements
- Data minimization for children
- Parental access and control rights
- Data retention limits

Reference: 16 CFR Part 312
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


@register_module(RegulationId.COPPA)
class COPPAModule(ComplianceModule):
    """COPPA Compliance Module

    Covers key COPPA requirements for operators of websites/online services
    directed to children under 13 or with actual knowledge of collecting
    personal information from children under 13.

    Key requirements:
    - Verifiable parental consent (VPC)
    - Direct notice to parents
    - Privacy policy requirements
    - Data minimization
    - Parental access rights
    - Data security
    - Data retention limits
    """

    # Personal information categories under COPPA
    PERSONAL_INFO_CATEGORIES = [
        "name",
        "address",
        "email",
        "phone",
        "ssn",
        "photo",
        "video",
        "audio",
        "geolocation",
        "persistent_identifier",
        "screen_name",
    ]

    # Child-directed service indicators
    CHILD_DIRECTED_INDICATORS = [
        "kids",
        "children",
        "child",
        "minor",
        "teen",
        "school",
        "education",
        "learning",
        "game",
        "cartoon",
        "animation",
        "toy",
    ]

    def _define_metadata(self) -> ModuleMetadata:
        return ModuleMetadata(
            id=RegulationId.COPPA,
            name="Children's Online Privacy Protection Act",
            short_name="COPPA",
            version="2013.amended",
            jurisdiction=Jurisdiction.US,
            description=(
                "Federal law protecting children's privacy online by requiring "
                "parental consent before collecting personal information from "
                "children under 13 years of age."
            ),
            effective_date=datetime(2000, 4, 21),
            articles=[
                "16 CFR 312.2 - Definitions",
                "16 CFR 312.3 - Regulation of Operators",
                "16 CFR 312.4 - Notice Requirements",
                "16 CFR 312.5 - Parental Consent",
                "16 CFR 312.6 - Right to Review",
                "16 CFR 312.7 - Prohibition Against Conditioning",
                "16 CFR 312.8 - Confidentiality and Security",
                "16 CFR 312.10 - Data Retention and Deletion",
            ],
            official_url="https://www.ftc.gov/legal-library/browse/rules/childrens-online-privacy-protection-rule-coppa",
            pricing_addon_usd=45.0,
        )

    def _define_controls(self) -> list[ControlDefinition]:
        return [
            # Notice Requirements (312.4)
            ControlDefinition(
                control_id="COPPA-4.1",
                name="Privacy Policy Posting",
                description="Post clear, complete privacy policy on website/service",
                article_ref="16 CFR 312.4(a)",
                required_evidence=[
                    "Privacy policy document",
                    "Link placement documentation",
                ],
            ),
            ControlDefinition(
                control_id="COPPA-4.2",
                name="Direct Notice to Parents",
                description="Provide direct notice to parents before collecting info",
                article_ref="16 CFR 312.4(b)",
                required_evidence=[
                    "Parent notification templates",
                    "Notification delivery logs",
                ],
            ),
            ControlDefinition(
                control_id="COPPA-4.3",
                name="Privacy Policy Content",
                description="Privacy policy includes all required COPPA disclosures",
                article_ref="16 CFR 312.4(d)",
                required_evidence=[
                    "Policy content checklist",
                    "Policy compliance review",
                ],
            ),
            # Parental Consent (312.5)
            ControlDefinition(
                control_id="COPPA-5.1",
                name="Verifiable Parental Consent",
                description="Obtain verifiable parental consent before collection",
                article_ref="16 CFR 312.5(a)",
                required_evidence=[
                    "Consent mechanism documentation",
                    "Verification method description",
                    "Consent records",
                ],
            ),
            ControlDefinition(
                control_id="COPPA-5.2",
                name="Consent Method Validity",
                description="Use FTC-approved method for obtaining consent",
                article_ref="16 CFR 312.5(b)",
                required_evidence=[
                    "Consent method implementation",
                    "Verification process documentation",
                ],
            ),
            # Parental Rights (312.6)
            ControlDefinition(
                control_id="COPPA-6.1",
                name="Right to Review Information",
                description="Allow parents to review child's personal information",
                article_ref="16 CFR 312.6(a)",
                required_evidence=[
                    "Parent access procedures",
                    "Identity verification process",
                ],
            ),
            ControlDefinition(
                control_id="COPPA-6.2",
                name="Right to Delete Information",
                description="Allow parents to request deletion of child's information",
                article_ref="16 CFR 312.6(a)(2)",
                required_evidence=[
                    "Deletion request procedures",
                    "Deletion confirmation process",
                ],
            ),
            ControlDefinition(
                control_id="COPPA-6.3",
                name="Right to Refuse Further Collection",
                description="Allow parents to refuse further collection/use",
                article_ref="16 CFR 312.6(a)(3)",
                required_evidence=[
                    "Opt-out mechanism",
                    "Collection cessation procedures",
                ],
            ),
            # Prohibition Against Conditioning (312.7)
            ControlDefinition(
                control_id="COPPA-7.1",
                name="No Conditioning Participation",
                description="Don't condition participation on disclosure of more info than necessary",
                article_ref="16 CFR 312.7",
                required_evidence=[
                    "Data minimization policy",
                    "Activity participation requirements",
                ],
            ),
            # Confidentiality and Security (312.8)
            ControlDefinition(
                control_id="COPPA-8.1",
                name="Data Security Measures",
                description="Maintain reasonable security for children's information",
                article_ref="16 CFR 312.8",
                required_evidence=[
                    "Security policy",
                    "Security controls documentation",
                    "Incident response plan",
                ],
            ),
            # Data Retention (312.10)
            ControlDefinition(
                control_id="COPPA-10.1",
                name="Data Retention Limits",
                description="Retain data only as long as necessary for purpose collected",
                article_ref="16 CFR 312.10",
                required_evidence=[
                    "Retention policy",
                    "Deletion procedures",
                    "Retention schedule",
                ],
            ),
        ]

    def _define_validation_rules(self) -> list[ValidationRule]:
        return [
            ValidationRule(
                rule_id="COPPA-VAL-001",
                name="Child Data Collection Detection",
                description="Detect potential collection of child personal information",
                category="data_collection",
                severity="critical",
                auto_check=True,
            ),
            ValidationRule(
                rule_id="COPPA-VAL-002",
                name="Child-Directed Content Detection",
                description="Detect content directed at children",
                category="child_directed",
                severity="high",
                auto_check=True,
            ),
            ValidationRule(
                rule_id="COPPA-VAL-003",
                name="Age Verification Check",
                description="Check for age verification before data collection",
                category="age_verification",
                severity="critical",
                auto_check=True,
            ),
            ValidationRule(
                rule_id="COPPA-VAL-004",
                name="Parental Consent Reference",
                description="Check for parental consent references",
                category="consent",
                severity="high",
                auto_check=True,
            ),
        ]

    async def assess_control(
        self,
        control: ControlDefinition,
        input_data: AssessmentInput,
    ) -> ControlResult:
        """Assess a single COPPA control."""
        metadata = input_data.metadata
        user_age = input_data.user_age
        is_child = user_age and user_age < 13

        # Verifiable Parental Consent
        if control.control_id == "COPPA-5.1":
            if is_child:
                has_consent = metadata.get("parental_consent_obtained", False)
                consent_verified = metadata.get("consent_verified", False)
                if has_consent and consent_verified:
                    return ControlResult(
                        control_id=control.control_id,
                        control_name=control.name,
                        module_id=self.module_id,
                        status=ComplianceStatus.COMPLIANT,
                        score=1.0,
                        evidence="Verifiable parental consent obtained and verified",
                    )
                if has_consent:
                    return ControlResult(
                        control_id=control.control_id,
                        control_name=control.name,
                        module_id=self.module_id,
                        status=ComplianceStatus.PARTIAL,
                        score=0.5,
                        findings=["Parental consent obtained but verification incomplete"],
                        remediation="Implement verifiable consent method per 312.5(b)",
                    )
                return ControlResult(
                    control_id=control.control_id,
                    control_name=control.name,
                    module_id=self.module_id,
                    status=ComplianceStatus.NON_COMPLIANT,
                    score=0.0,
                    findings=["Collecting child data without parental consent"],
                    remediation="Obtain verifiable parental consent before collection",
                )
            return ControlResult(
                control_id=control.control_id,
                control_name=control.name,
                module_id=self.module_id,
                status=ComplianceStatus.NOT_APPLICABLE,
                score=1.0,
                evidence="User is 13 or older - COPPA consent not required",
            )

        # Privacy Policy
        if control.control_id == "COPPA-4.1":
            has_policy = metadata.get("privacy_policy_posted", False)
            if has_policy:
                return ControlResult(
                    control_id=control.control_id,
                    control_name=control.name,
                    module_id=self.module_id,
                    status=ComplianceStatus.COMPLIANT,
                    score=1.0,
                    evidence="Privacy policy posted and accessible",
                )
            return ControlResult(
                control_id=control.control_id,
                control_name=control.name,
                module_id=self.module_id,
                status=ComplianceStatus.NON_COMPLIANT,
                score=0.0,
                findings=["COPPA-compliant privacy policy not posted"],
                remediation="Post privacy policy with all COPPA-required disclosures",
            )

        # Data Security
        if control.control_id == "COPPA-8.1":  # noqa: SIM102
            if is_child or metadata.get("child_directed_service", False):
                security_implemented = metadata.get("security_measures_implemented", False)
                if security_implemented:
                    return ControlResult(
                        control_id=control.control_id,
                        control_name=control.name,
                        module_id=self.module_id,
                        status=ComplianceStatus.COMPLIANT,
                        score=1.0,
                        evidence="Security measures implemented for child data",
                    )
                return ControlResult(
                    control_id=control.control_id,
                    control_name=control.name,
                    module_id=self.module_id,
                    status=ComplianceStatus.NON_COMPLIANT,
                    score=0.0,
                    findings=["Inadequate security for children's personal information"],
                    remediation="Implement reasonable security measures per 312.8",
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
        """Determine COPPA risk tier."""
        user_age = input_data.user_age
        metadata = input_data.metadata

        # Child under 13 without consent = UNACCEPTABLE
        if user_age and user_age < 13:
            if not metadata.get("parental_consent_obtained", False):
                return RiskTier.UNACCEPTABLE
            return RiskTier.HIGH

        # Child-directed service = HIGH
        if metadata.get("child_directed_service", False):
            return RiskTier.HIGH

        # Mixed audience = LIMITED
        if metadata.get("mixed_audience", False):
            return RiskTier.LIMITED

        return RiskTier.MINIMAL

    async def _check_validation_rule(
        self,
        rule: ValidationRule,
        content: str,
        context: str | None,
    ) -> ValidationViolation | None:
        """Check COPPA validation rules against content."""
        content_lower = content.lower()

        if rule.rule_id == "COPPA-VAL-001":
            # Child Data Collection Detection
            collection_patterns = [
                r"(collect|gather|obtain)\s+\w*\s*(name|email|address|phone)",
                r"(enter|provide|give)\s+your\s+(name|email|age|birthday)",
                r"(sign\s+up|register|create\s+account)",
            ]
            child_context = any(ind in content_lower for ind in self.CHILD_DIRECTED_INDICATORS)

            for pattern in collection_patterns:
                if re.search(pattern, content_lower) and child_context:
                    return ValidationViolation(
                        module_id=self.module_id,
                        rule_id=rule.rule_id,
                        severity="critical",
                        description="Potential collection of child personal information detected",
                        suggested_fix="Ensure parental consent before collecting information from children under 13",
                        article_reference="COPPA 16 CFR 312.5",
                    )

        if rule.rule_id == "COPPA-VAL-002":
            # Child-Directed Content Detection
            child_indicators_found = sum(
                1 for ind in self.CHILD_DIRECTED_INDICATORS if ind in content_lower
            )
            if child_indicators_found >= 2:
                return ValidationViolation(
                    module_id=self.module_id,
                    rule_id=rule.rule_id,
                    severity="high",
                    description="Content appears to be directed at children",
                    suggested_fix="Apply COPPA protections if service is directed to children under 13",
                    article_reference="COPPA 16 CFR 312.2",
                )

        if rule.rule_id == "COPPA-VAL-003":
            # Age Verification Check
            asks_for_age = any(
                phrase in content_lower
                for phrase in [
                    "how old are you",
                    "enter your age",
                    "date of birth",
                    "birthday",
                    "year you were born",
                ]
            )
            if asks_for_age:
                has_gate = any(
                    phrase in content_lower
                    for phrase in [
                        "must be 13",
                        "13 or older",
                        "age verification",
                        "parental consent",
                        "parent or guardian",
                    ]
                )
                if not has_gate:
                    return ValidationViolation(
                        module_id=self.module_id,
                        rule_id=rule.rule_id,
                        severity="critical",
                        description="Age collection without proper age gate or parental consent mechanism",
                        suggested_fix="Implement age verification and parental consent for users under 13",
                        article_reference="COPPA 16 CFR 312.5",
                    )

        return None
