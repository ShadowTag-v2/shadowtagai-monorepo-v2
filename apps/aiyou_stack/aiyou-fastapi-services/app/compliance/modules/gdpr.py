# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""GDPR Compliance Module

Implements the General Data Protection Regulation (EU) 2016/679 requirements.
Focus areas:
- Lawful basis for processing
- Data minimization
- Rights of data subjects
- Data protection by design
- Privacy impact assessments
- Cross-border data transfers

Reference: Regulation (EU) 2016/679
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


@register_module(RegulationId.GDPR)
class GDPRModule(ComplianceModule):
    """GDPR Compliance Module

    Covers key GDPR requirements:
    - Article 5: Principles of processing
    - Article 6: Lawfulness of processing
    - Article 12-22: Rights of data subjects
    - Article 25: Data protection by design
    - Article 32: Security of processing
    - Article 35: Data protection impact assessment
    """

    # Personal data categories
    PERSONAL_DATA_INDICATORS = [
        "name",
        "email",
        "address",
        "phone",
        "ip_address",
        "location",
        "device_id",
        "cookie",
        "identifier",
    ]

    # Special category data (Article 9)
    SPECIAL_CATEGORIES = [
        "racial",
        "ethnic",
        "political",
        "religious",
        "trade_union",
        "genetic",
        "biometric",
        "health",
        "sex_life",
        "sexual_orientation",
    ]

    # PII detection patterns
    PII_PATTERNS = {
        "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
        "phone": r"(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}",
        "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
        "credit_card": r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",
        "ip_address": r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",
    }

    def _define_metadata(self) -> ModuleMetadata:
        return ModuleMetadata(
            id=RegulationId.GDPR,
            name="General Data Protection Regulation",
            short_name="GDPR",
            version="2016.679",
            jurisdiction=Jurisdiction.EU,
            description=(
                "Regulation on the protection of natural persons with regard to "
                "the processing of personal data and the free movement of such data."
            ),
            effective_date=datetime(2018, 5, 25),
            articles=[
                "Art 5 - Principles of Processing",
                "Art 6 - Lawfulness of Processing",
                "Art 7 - Conditions for Consent",
                "Art 12-22 - Data Subject Rights",
                "Art 25 - Data Protection by Design",
                "Art 32 - Security of Processing",
                "Art 33-34 - Breach Notification",
                "Art 35 - Data Protection Impact Assessment",
                "Art 44-49 - Cross-border Transfers",
            ],
            official_url="https://eur-lex.europa.eu/eli/reg/2016/679/oj",
            pricing_addon_usd=50.0,
        )

    def _define_controls(self) -> list[ControlDefinition]:
        return [
            # Principles (Art 5)
            ControlDefinition(
                control_id="GDPR-5.1a",
                name="Lawfulness, Fairness, Transparency",
                description="Personal data processed lawfully, fairly, and transparently",
                article_ref="Article 5(1)(a)",
                required_evidence=["Privacy notice", "Lawful basis documentation"],
            ),
            ControlDefinition(
                control_id="GDPR-5.1b",
                name="Purpose Limitation",
                description="Personal data collected for specified, explicit, legitimate purposes",
                article_ref="Article 5(1)(b)",
                required_evidence=["Purpose specification document"],
            ),
            ControlDefinition(
                control_id="GDPR-5.1c",
                name="Data Minimization",
                description="Personal data adequate, relevant, and limited to what is necessary",
                article_ref="Article 5(1)(c)",
                required_evidence=["Data inventory", "Minimization assessment"],
            ),
            ControlDefinition(
                control_id="GDPR-5.1d",
                name="Accuracy",
                description="Personal data accurate and kept up to date",
                article_ref="Article 5(1)(d)",
                required_evidence=["Data quality procedures"],
            ),
            ControlDefinition(
                control_id="GDPR-5.1e",
                name="Storage Limitation",
                description="Personal data kept no longer than necessary",
                article_ref="Article 5(1)(e)",
                required_evidence=["Retention schedule", "Deletion procedures"],
            ),
            ControlDefinition(
                control_id="GDPR-5.1f",
                name="Integrity and Confidentiality",
                description="Personal data processed with appropriate security",
                article_ref="Article 5(1)(f)",
                required_evidence=["Security policy", "Encryption documentation"],
            ),
            # Lawful Basis (Art 6)
            ControlDefinition(
                control_id="GDPR-6.1",
                name="Lawful Basis for Processing",
                description="Processing based on valid lawful basis (consent, contract, etc.)",
                article_ref="Article 6(1)",
                required_evidence=["Lawful basis register", "Consent records"],
            ),
            # Data Subject Rights (Art 12-22)
            ControlDefinition(
                control_id="GDPR-15",
                name="Right of Access",
                description="Data subjects can access their personal data",
                article_ref="Article 15",
                required_evidence=["DSR procedures", "Access request logs"],
            ),
            ControlDefinition(
                control_id="GDPR-17",
                name="Right to Erasure",
                description="Data subjects can request deletion of personal data",
                article_ref="Article 17",
                required_evidence=["Deletion procedures", "Erasure request logs"],
            ),
            ControlDefinition(
                control_id="GDPR-20",
                name="Right to Data Portability",
                description="Data subjects can receive data in portable format",
                article_ref="Article 20",
                required_evidence=["Portability procedures", "Export formats"],
            ),
            # Data Protection by Design (Art 25)
            ControlDefinition(
                control_id="GDPR-25.1",
                name="Data Protection by Design",
                description="Technical and organizational measures implemented by design",
                article_ref="Article 25(1)",
                required_evidence=["Privacy by design documentation"],
            ),
            ControlDefinition(
                control_id="GDPR-25.2",
                name="Data Protection by Default",
                description="Default settings ensure only necessary data is processed",
                article_ref="Article 25(2)",
                required_evidence=["Default configuration documentation"],
            ),
            # Security (Art 32)
            ControlDefinition(
                control_id="GDPR-32",
                name="Security of Processing",
                description="Appropriate technical and organizational security measures",
                article_ref="Article 32",
                required_evidence=["Security assessment", "Encryption standards"],
            ),
            # DPIA (Art 35)
            ControlDefinition(
                control_id="GDPR-35",
                name="Data Protection Impact Assessment",
                description="DPIA conducted for high-risk processing",
                article_ref="Article 35",
                required_evidence=["DPIA report", "Risk mitigation measures"],
            ),
        ]

    def _define_validation_rules(self) -> list[ValidationRule]:
        return [
            ValidationRule(
                rule_id="GDPR-VAL-001",
                name="PII Exposure Detection",
                description="Detect personal identifiable information in content",
                category="data_minimization",
                severity="high",
                auto_check=True,
            ),
            ValidationRule(
                rule_id="GDPR-VAL-002",
                name="Special Category Detection",
                description="Detect special category data exposure",
                category="special_categories",
                severity="critical",
                auto_check=True,
            ),
            ValidationRule(
                rule_id="GDPR-VAL-003",
                name="Consent Reference Check",
                description="Check for proper consent references in data collection context",
                category="lawful_basis",
                severity="medium",
                auto_check=True,
            ),
            ValidationRule(
                rule_id="GDPR-VAL-004",
                name="Cross-Border Transfer Check",
                description="Detect references to data transfers outside EU/EEA",
                category="transfers",
                severity="high",
                auto_check=True,
            ),
        ]

    async def assess_control(
        self,
        control: ControlDefinition,
        input_data: AssessmentInput,
    ) -> ControlResult:
        """Assess a single GDPR control."""
        metadata = input_data.metadata

        # Data Minimization check
        if control.control_id == "GDPR-5.1c":
            if input_data.contains_pii:
                metadata.get("data_categories", [])
                purpose = metadata.get("processing_purpose", "")
                if not purpose:
                    return ControlResult(
                        control_id=control.control_id,
                        control_name=control.name,
                        module_id=self.module_id,
                        status=ComplianceStatus.NON_COMPLIANT,
                        score=0.0,
                        findings=["Processing purpose not specified for PII"],
                        remediation="Document purpose for each data category collected",
                    )
            return ControlResult(
                control_id=control.control_id,
                control_name=control.name,
                module_id=self.module_id,
                status=ComplianceStatus.COMPLIANT,
                score=1.0,
                evidence="Data minimization principles applied",
            )

        # Lawful Basis check
        if control.control_id == "GDPR-6.1":
            lawful_basis = metadata.get("lawful_basis")
            valid_bases = [
                "consent",
                "contract",
                "legal_obligation",
                "vital_interests",
                "public_task",
                "legitimate_interests",
            ]
            if lawful_basis and lawful_basis in valid_bases:
                return ControlResult(
                    control_id=control.control_id,
                    control_name=control.name,
                    module_id=self.module_id,
                    status=ComplianceStatus.COMPLIANT,
                    score=1.0,
                    evidence=f"Lawful basis documented: {lawful_basis}",
                )
            return ControlResult(
                control_id=control.control_id,
                control_name=control.name,
                module_id=self.module_id,
                status=ComplianceStatus.NON_COMPLIANT,
                score=0.0,
                findings=["Valid lawful basis not documented"],
                remediation="Identify and document lawful basis per Article 6(1)",
            )

        # DPIA requirement check
        if control.control_id == "GDPR-35":
            if input_data.contains_pii and input_data.is_high_risk_decision:
                dpia_conducted = metadata.get("dpia_completed", False)
                if dpia_conducted:
                    return ControlResult(
                        control_id=control.control_id,
                        control_name=control.name,
                        module_id=self.module_id,
                        status=ComplianceStatus.COMPLIANT,
                        score=1.0,
                        evidence="DPIA completed for high-risk processing",
                    )
                return ControlResult(
                    control_id=control.control_id,
                    control_name=control.name,
                    module_id=self.module_id,
                    status=ComplianceStatus.NON_COMPLIANT,
                    score=0.0,
                    findings=["DPIA required but not completed"],
                    remediation="Conduct Data Protection Impact Assessment per Article 35",
                )
            return ControlResult(
                control_id=control.control_id,
                control_name=control.name,
                module_id=self.module_id,
                status=ComplianceStatus.NOT_APPLICABLE,
                score=1.0,
                evidence="DPIA not required for this processing activity",
            )

        # Default: Partial compliance
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
        """Determine GDPR processing risk level."""
        # GDPR doesn't use same risk tiers as EU AI Act
        # But we can map to similar levels for consistency

        # Special category data = HIGH
        content_type = input_data.content_type.lower()
        for special in self.SPECIAL_CATEGORIES:
            if special in content_type:
                return RiskTier.HIGH

        # Large scale processing or profiling = HIGH
        if input_data.metadata.get("large_scale_processing", False):
            return RiskTier.HIGH

        if input_data.metadata.get("profiling", False):
            return RiskTier.HIGH

        # PII with high-risk decision = HIGH
        if input_data.contains_pii and input_data.is_high_risk_decision:
            return RiskTier.HIGH

        # Any PII = LIMITED
        if input_data.contains_pii:
            return RiskTier.LIMITED

        return RiskTier.MINIMAL

    async def _check_validation_rule(
        self,
        rule: ValidationRule,
        content: str,
        context: str | None,
    ) -> ValidationViolation | None:
        """Check GDPR validation rules against content."""
        if rule.rule_id == "GDPR-VAL-001":
            # PII Exposure Detection
            for pii_type, pattern in self.PII_PATTERNS.items():
                match = re.search(pattern, content)
                if match:
                    return ValidationViolation(
                        module_id=self.module_id,
                        rule_id=rule.rule_id,
                        severity="high",
                        description=f"Potential {pii_type} detected in content",
                        location=match.group(),
                        suggested_fix=f"Remove or mask {pii_type} data",
                        article_reference="GDPR Article 5(1)(c) - Data Minimization",
                    )

        if rule.rule_id == "GDPR-VAL-002":
            # Special Category Detection
            content_lower = content.lower()
            for category in self.SPECIAL_CATEGORIES:
                if category in content_lower:
                    # Check if it's about personal data
                    personal_context_words = ["my", "their", "patient", "individual", "person"]
                    if any(word in content_lower for word in personal_context_words):
                        return ValidationViolation(
                            module_id=self.module_id,
                            rule_id=rule.rule_id,
                            severity="critical",
                            description=f"Potential special category data ({category}) detected",
                            location=category,
                            suggested_fix="Ensure explicit consent or other valid legal basis for processing",
                            article_reference="GDPR Article 9 - Special Categories",
                        )

        if rule.rule_id == "GDPR-VAL-004":
            # Cross-Border Transfer Check
            non_eu_countries = [
                "united states",
                "us ",
                "china",
                "india",
                "russia",
                "brazil",
                "australia",
                "transfer to",
                "stored in",
            ]
            content_lower = content.lower()
            for term in non_eu_countries:
                if term in content_lower:
                    return ValidationViolation(
                        module_id=self.module_id,
                        rule_id=rule.rule_id,
                        severity="high",
                        description="Potential cross-border data transfer reference detected",
                        location=term,
                        suggested_fix="Ensure appropriate safeguards for international transfers",
                        article_reference="GDPR Articles 44-49 - Transfers",
                    )

        return None
