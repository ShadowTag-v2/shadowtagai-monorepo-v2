# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
California SB 243 Compliance Module

Implements California Senate Bill 243 - AI harm detection and minor protection.
Focus areas:
- Self-harm detection in AI systems
- Minor protection requirements
- AI safety disclosures
- Parental notification
- Content filtering for minors

Reference: California SB 243 (Enacted 2024)
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


@register_module(RegulationId.CA_SB_243)
class CASB243Module(ComplianceModule):
    """
    California SB 243 Compliance Module

    Focus on AI systems interacting with minors and detecting self-harm:
    - Self-harm and suicide prevention
    - Age verification for AI services
    - Parental consent requirements
    - Content safety for minors
    - AI disclosure to minors
    """

    # Self-harm and crisis keywords for detection
    SELF_HARM_INDICATORS = [
        "suicide",
        "self-harm",
        "self harm",
        "kill myself",
        "end my life",
        "want to die",
        "hurt myself",
        "cutting",
        "overdose",
        "jump off",
        "hang myself",
        "not worth living",
    ]

    # Mental health crisis indicators
    CRISIS_INDICATORS = [
        "crisis",
        "emergency",
        "helpline",
        "hotline",
        "988",
        "suicidal ideation",
        "depression",
        "anxiety attack",
    ]

    # Age-restricted content categories
    AGE_RESTRICTED = [
        "violence",
        "gambling",
        "alcohol",
        "tobacco",
        "adult_content",
        "weapons",
        "drugs",
    ]

    def _define_metadata(self) -> ModuleMetadata:
        return ModuleMetadata(
            id=RegulationId.CA_SB_243,
            name="California SB 243 - AI Minor Protection",
            short_name="CA SB 243",
            version="2024.1",
            jurisdiction=Jurisdiction.US,
            description=("California law requiring AI systems to detect self-harm risks and implement protections for minors interacting with AI."),
            effective_date=datetime(2025, 1, 1),
            articles=[
                "Sec 1 - Self-Harm Detection Requirements",
                "Sec 2 - Age Verification",
                "Sec 3 - Parental Consent",
                "Sec 4 - AI Disclosure to Minors",
                "Sec 5 - Content Safety Measures",
                "Sec 6 - Crisis Response Protocols",
            ],
            official_url="https://leginfo.legislature.ca.gov/faces/billNavClient.xhtml?bill_id=202320240SB243",
            pricing_addon_usd=45.0,
        )

    def _define_controls(self) -> list[ControlDefinition]:
        return [
            # Self-Harm Detection (Sec 1)
            ControlDefinition(
                control_id="SB243-1.1",
                name="Self-Harm Detection System",
                description="AI system capable of detecting self-harm indicators in user input",
                article_ref="Section 1",
                required_evidence=[
                    "Detection algorithm documentation",
                    "Keyword/pattern list",
                    "Detection accuracy metrics",
                ],
            ),
            ControlDefinition(
                control_id="SB243-1.2",
                name="Crisis Response Protocol",
                description="Automated response to detected self-harm with crisis resources",
                article_ref="Section 1",
                required_evidence=[
                    "Response protocol documentation",
                    "Crisis resource database",
                    "Response message templates",
                ],
            ),
            # Age Verification (Sec 2)
            ControlDefinition(
                control_id="SB243-2.1",
                name="Age Verification Mechanism",
                description="Mechanism to verify user age before AI interaction",
                article_ref="Section 2",
                required_evidence=[
                    "Age verification implementation",
                    "Age gate UI documentation",
                ],
            ),
            ControlDefinition(
                control_id="SB243-2.2",
                name="Minor User Identification",
                description="System to identify and flag users under 18",
                article_ref="Section 2",
                required_evidence=["Minor flagging logic", "Age tracking system"],
            ),
            # Parental Consent (Sec 3)
            ControlDefinition(
                control_id="SB243-3.1",
                name="Parental Consent Collection",
                description="Obtain verifiable parental consent for minors under 13",
                article_ref="Section 3",
                required_evidence=[
                    "Consent collection mechanism",
                    "Parent verification process",
                ],
            ),
            ControlDefinition(
                control_id="SB243-3.2",
                name="Parental Notification",
                description="Notify parents of detected risk indicators",
                article_ref="Section 3",
                required_evidence=["Notification system", "Escalation procedures"],
            ),
            # AI Disclosure (Sec 4)
            ControlDefinition(
                control_id="SB243-4.1",
                name="AI Nature Disclosure",
                description="Clear disclosure that user is interacting with AI",
                article_ref="Section 4",
                required_evidence=[
                    "Disclosure language",
                    "Disclosure placement documentation",
                ],
            ),
            ControlDefinition(
                control_id="SB243-4.2",
                name="AI Limitations Disclosure",
                description="Inform minors of AI limitations and not a substitute for human help",
                article_ref="Section 4",
                required_evidence=["Limitations disclosure", "Help-seeking guidance"],
            ),
            # Content Safety (Sec 5)
            ControlDefinition(
                control_id="SB243-5.1",
                name="Age-Appropriate Content Filtering",
                description="Filter inappropriate content for verified minors",
                article_ref="Section 5",
                required_evidence=["Content filtering rules", "Filter testing results"],
            ),
            ControlDefinition(
                control_id="SB243-5.2",
                name="Harmful Content Prevention",
                description="Prevent AI from generating harmful content for minors",
                article_ref="Section 5",
                required_evidence=[
                    "Output filtering documentation",
                    "Safety guardrails",
                ],
            ),
            # Crisis Response (Sec 6)
            ControlDefinition(
                control_id="SB243-6.1",
                name="Crisis Resource Integration",
                description="Integration with crisis hotlines (988 Suicide & Crisis Lifeline)",
                article_ref="Section 6",
                required_evidence=["Crisis resource list", "Integration documentation"],
            ),
        ]

    def _define_validation_rules(self) -> list[ValidationRule]:
        return [
            ValidationRule(
                rule_id="SB243-VAL-001",
                name="Self-Harm Content Detection",
                description="Detect self-harm related content in AI responses",
                category="self_harm",
                severity="critical",
                auto_check=True,
            ),
            ValidationRule(
                rule_id="SB243-VAL-002",
                name="Minor-Inappropriate Content",
                description="Detect content inappropriate for minors",
                category="minor_safety",
                severity="high",
                auto_check=True,
            ),
            ValidationRule(
                rule_id="SB243-VAL-003",
                name="AI Disclosure Presence",
                description="Check for AI nature disclosure in content",
                category="transparency",
                severity="medium",
                auto_check=True,
            ),
            ValidationRule(
                rule_id="SB243-VAL-004",
                name="Crisis Resource Inclusion",
                description="Check for crisis resources when self-harm detected",
                category="crisis_response",
                severity="critical",
                auto_check=True,
            ),
        ]

    async def assess_control(self, control: ControlDefinition, input_data: AssessmentInput) -> ControlResult:
        """Assess a single CA SB 243 control."""
        metadata = input_data.metadata
        user_age = input_data.user_age
        is_minor = user_age and user_age < 18

        # Self-Harm Detection System
        if control.control_id == "SB243-1.1":
            has_detection = metadata.get("self_harm_detection_enabled", False)
            if has_detection:
                return ControlResult(
                    control_id=control.control_id,
                    control_name=control.name,
                    module_id=self.module_id,
                    status=ComplianceStatus.COMPLIANT,
                    score=1.0,
                    evidence="Self-harm detection system implemented",
                )
            else:
                return ControlResult(
                    control_id=control.control_id,
                    control_name=control.name,
                    module_id=self.module_id,
                    status=ComplianceStatus.NON_COMPLIANT,
                    score=0.0,
                    findings=["Self-harm detection not implemented"],
                    remediation="Implement self-harm detection per Section 1",
                )

        # Age Verification
        if control.control_id == "SB243-2.1":
            has_age_verification = metadata.get("age_verification_enabled", False)
            if has_age_verification:
                return ControlResult(
                    control_id=control.control_id,
                    control_name=control.name,
                    module_id=self.module_id,
                    status=ComplianceStatus.COMPLIANT,
                    score=1.0,
                    evidence="Age verification mechanism in place",
                )
            else:
                return ControlResult(
                    control_id=control.control_id,
                    control_name=control.name,
                    module_id=self.module_id,
                    status=ComplianceStatus.NON_COMPLIANT,
                    score=0.0,
                    findings=["Age verification not implemented"],
                    remediation="Implement age verification before AI interaction",
                )

        # Parental Consent for under 13
        if control.control_id == "SB243-3.1":
            if user_age and user_age < 13:
                has_consent = metadata.get("parental_consent_obtained", False)
                if has_consent:
                    return ControlResult(
                        control_id=control.control_id,
                        control_name=control.name,
                        module_id=self.module_id,
                        status=ComplianceStatus.COMPLIANT,
                        score=1.0,
                        evidence="Parental consent obtained for user under 13",
                    )
                else:
                    return ControlResult(
                        control_id=control.control_id,
                        control_name=control.name,
                        module_id=self.module_id,
                        status=ComplianceStatus.NON_COMPLIANT,
                        score=0.0,
                        findings=["Parental consent required but not obtained"],
                        remediation="Obtain verifiable parental consent per Section 3",
                    )
            return ControlResult(
                control_id=control.control_id,
                control_name=control.name,
                module_id=self.module_id,
                status=ComplianceStatus.NOT_APPLICABLE,
                score=1.0,
                evidence="User is 13 or older - parental consent not required",
            )

        # AI Disclosure for minors
        if control.control_id == "SB243-4.1":
            if is_minor:
                has_disclosure = metadata.get("ai_disclosure_shown", False)
                if has_disclosure:
                    return ControlResult(
                        control_id=control.control_id,
                        control_name=control.name,
                        module_id=self.module_id,
                        status=ComplianceStatus.COMPLIANT,
                        score=1.0,
                        evidence="AI disclosure provided to minor",
                    )
                else:
                    return ControlResult(
                        control_id=control.control_id,
                        control_name=control.name,
                        module_id=self.module_id,
                        status=ComplianceStatus.NON_COMPLIANT,
                        score=0.0,
                        findings=["AI disclosure not shown to minor user"],
                        remediation="Display clear AI disclosure per Section 4",
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
        """Determine risk tier based on user age and content."""
        user_age = input_data.user_age

        # Children under 13 = UNACCEPTABLE without consent
        if user_age and user_age < 13:
            if not input_data.metadata.get("parental_consent_obtained", False):
                return RiskTier.UNACCEPTABLE
            return RiskTier.HIGH

        # Minors 13-17 = HIGH
        if user_age and user_age < 18:
            return RiskTier.HIGH

        # Self-harm context = HIGH
        content_type = input_data.content_type.lower()
        if any(indicator in content_type for indicator in ["mental_health", "crisis", "therapy"]):
            return RiskTier.HIGH

        return RiskTier.LIMITED

    async def _check_validation_rule(self, rule: ValidationRule, content: str, context: str | None) -> ValidationViolation | None:
        """Check CA SB 243 validation rules against content."""
        content_lower = content.lower()

        if rule.rule_id == "SB243-VAL-001":
            # Self-Harm Content Detection
            for indicator in self.SELF_HARM_INDICATORS:
                if indicator in content_lower:
                    # Check if crisis resources are present
                    has_resources = any(crisis in content_lower for crisis in self.CRISIS_INDICATORS + ["988", "crisis line", "get help"])
                    if not has_resources:
                        return ValidationViolation(
                            module_id=self.module_id,
                            rule_id=rule.rule_id,
                            severity="critical",
                            description=f"Self-harm content detected without crisis resources: '{indicator}'",
                            location=indicator,
                            suggested_fix="Add crisis resources (988 Lifeline) when self-harm content detected",
                            article_reference="CA SB 243 Section 1, 6",
                        )

        if rule.rule_id == "SB243-VAL-002":
            # Minor-Inappropriate Content
            inappropriate_patterns = [
                r"\b(18\+|adult\s+only|explicit)\b",
                r"\b(gambling|casino|bet\s+on)\b",
                r"\b(alcohol|beer|wine|drunk)\b",
                r"\b(weapon|gun|firearm)\b",
            ]
            for pattern in inappropriate_patterns:
                if re.search(pattern, content_lower):
                    return ValidationViolation(
                        module_id=self.module_id,
                        rule_id=rule.rule_id,
                        severity="high",
                        description="Content may be inappropriate for minors",
                        suggested_fix="Filter age-restricted content for minor users",
                        article_reference="CA SB 243 Section 5",
                    )

        if rule.rule_id == "SB243-VAL-004":
            # Crisis Resource Inclusion when self-harm detected
            has_self_harm = any(ind in content_lower for ind in self.SELF_HARM_INDICATORS)
            if has_self_harm:
                crisis_resources = [
                    "988",
                    "suicide prevention lifeline",
                    "crisis text line",
                    "text home to 741741",
                    "get help",
                    "speak to someone",
                ]
                has_resources = any(res in content_lower for res in crisis_resources)
                if not has_resources:
                    return ValidationViolation(
                        module_id=self.module_id,
                        rule_id=rule.rule_id,
                        severity="critical",
                        description="Self-harm content lacks required crisis resources",
                        suggested_fix="Include 988 Suicide & Crisis Lifeline and other resources",
                        article_reference="CA SB 243 Section 6",
                    )

        return None
