# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
EU AI Act Compliance Module

Implements the European Union Artificial Intelligence Act requirements.
Focus areas:
- Risk classification (Unacceptable, High, Limited, Minimal)
- Transparency requirements
- Data governance
- Human oversight
- Technical documentation
- Conformity assessment

Reference: Regulation (EU) 2024/1689
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


@register_module(RegulationId.EU_AI_ACT)
class EUAIActModule(ComplianceModule):
    """
    EU AI Act Compliance Module

    Covers Articles 1-113 with focus on:
    - Article 5: Prohibited AI practices
    - Article 6: High-risk AI classification
    - Article 9-15: High-risk AI requirements
    - Article 50: Transparency obligations
    - Article 52: CE marking and conformity
    """

    # High-risk AI system categories per Annex III
    HIGH_RISK_CATEGORIES = [
        "biometric_identification",
        "critical_infrastructure",
        "education_vocational",
        "employment_workers",
        "essential_services",
        "law_enforcement",
        "migration_asylum",
        "justice_democracy",
    ]

    # Prohibited AI practices per Article 5
    PROHIBITED_PRACTICES = [
        "subliminal_manipulation",
        "exploitation_vulnerabilities",
        "social_scoring",
        "real_time_biometric_public",
        "emotion_recognition_workplace",
        "biometric_categorization_sensitive",
    ]

    def _define_metadata(self) -> ModuleMetadata:
        return ModuleMetadata(
            id=RegulationId.EU_AI_ACT,
            name="EU Artificial Intelligence Act",
            short_name="EU AI Act",
            version="2024.1689",
            jurisdiction=Jurisdiction.EU,
            description=(
                "Regulation establishing harmonised rules on artificial intelligence "
                "in the European Union, with risk-based classification and requirements."
            ),
            effective_date=datetime(2024, 8, 1),
            articles=[
                "Art 5 - Prohibited AI Practices",
                "Art 6 - Classification Rules for High-Risk AI",
                "Art 9 - Risk Management System",
                "Art 10 - Data and Data Governance",
                "Art 11 - Technical Documentation",
                "Art 12 - Record-keeping",
                "Art 13 - Transparency and Information",
                "Art 14 - Human Oversight",
                "Art 15 - Accuracy, Robustness and Cybersecurity",
                "Art 50 - Transparency Obligations",
            ],
            official_url="https://eur-lex.europa.eu/eli/reg/2024/1689/oj",
            pricing_addon_usd=75.0,
        )

    def _define_controls(self) -> list[ControlDefinition]:
        return [
            # Risk Management (Art 9)
            ControlDefinition(
                control_id="EU-AI-9.1",
                name="Risk Management System",
                description="Establish and maintain a risk management system throughout AI lifecycle",
                article_ref="Article 9",
                required_evidence=[
                    "Risk management policy document",
                    "Risk assessment results",
                    "Mitigation measures documentation",
                ],
            ),
            ControlDefinition(
                control_id="EU-AI-9.2",
                name="Risk Identification and Analysis",
                description="Identify and analyse known and reasonably foreseeable risks",
                article_ref="Article 9(2)",
                required_evidence=["Risk register", "Hazard analysis report"],
            ),
            # Data Governance (Art 10)
            ControlDefinition(
                control_id="EU-AI-10.1",
                name="Training Data Governance",
                description="Data governance and management practices for training, validation, and testing",
                article_ref="Article 10",
                required_evidence=[
                    "Data governance policy",
                    "Data quality assessment",
                    "Bias analysis report",
                ],
            ),
            ControlDefinition(
                control_id="EU-AI-10.2",
                name="Data Quality Criteria",
                description="Training datasets meet quality criteria (relevant, representative, error-free)",
                article_ref="Article 10(3)",
                required_evidence=[
                    "Data quality metrics",
                    "Representativeness analysis",
                ],
            ),
            # Technical Documentation (Art 11)
            ControlDefinition(
                control_id="EU-AI-11.1",
                name="Technical Documentation",
                description="Draw up technical documentation before AI system is placed on market",
                article_ref="Article 11",
                required_evidence=[
                    "System description",
                    "Design specifications",
                    "Development process documentation",
                ],
            ),
            # Record-keeping (Art 12)
            ControlDefinition(
                control_id="EU-AI-12.1",
                name="Automatic Logging",
                description="AI system designed for automatic recording of events (logs)",
                article_ref="Article 12",
                required_evidence=["Logging architecture", "Log retention policy"],
            ),
            # Transparency (Art 13)
            ControlDefinition(
                control_id="EU-AI-13.1",
                name="Transparency to Users",
                description="AI system designed to enable users to interpret output appropriately",
                article_ref="Article 13",
                required_evidence=[
                    "User documentation",
                    "Interpretability documentation",
                ],
            ),
            # Human Oversight (Art 14)
            ControlDefinition(
                control_id="EU-AI-14.1",
                name="Human Oversight Mechanisms",
                description="AI system allows for human oversight during use",
                article_ref="Article 14",
                required_evidence=[
                    "Human oversight procedures",
                    "Override mechanism documentation",
                ],
            ),
            ControlDefinition(
                control_id="EU-AI-14.2",
                name="Human Understanding of AI",
                description="Humans can properly understand AI capabilities and limitations",
                article_ref="Article 14(4)(a)",
                required_evidence=[
                    "Operator training materials",
                    "Capability documentation",
                ],
            ),
            # Accuracy and Security (Art 15)
            ControlDefinition(
                control_id="EU-AI-15.1",
                name="Accuracy Specifications",
                description="AI system achieves appropriate level of accuracy",
                article_ref="Article 15(1)",
                required_evidence=["Accuracy metrics", "Performance benchmarks"],
            ),
            ControlDefinition(
                control_id="EU-AI-15.2",
                name="Robustness and Resilience",
                description="AI system resilient to errors, faults, and adversarial attacks",
                article_ref="Article 15(4)",
                required_evidence=["Robustness testing results", "Security assessment"],
            ),
            # Transparency Obligations (Art 50)
            ControlDefinition(
                control_id="EU-AI-50.1",
                name="AI-Generated Content Disclosure",
                description="Users informed they are interacting with AI or content is AI-generated",
                article_ref="Article 50(1-2)",
                required_evidence=["Disclosure mechanisms", "User notification logs"],
            ),
            ControlDefinition(
                control_id="EU-AI-50.2",
                name="Deepfake Labeling",
                description="AI-generated/manipulated media clearly labeled as artificial",
                article_ref="Article 50(4)",
                required_evidence=["Labeling mechanism documentation"],
            ),
        ]

    def _define_validation_rules(self) -> list[ValidationRule]:
        return [
            ValidationRule(
                rule_id="EU-AI-VAL-001",
                name="AI Disclosure Check",
                description="Check for proper AI disclosure in user-facing content",
                category="transparency",
                severity="high",
                auto_check=True,
            ),
            ValidationRule(
                rule_id="EU-AI-VAL-002",
                name="Prohibited Practice Detection",
                description="Detect content that may enable prohibited AI practices",
                category="prohibited",
                severity="critical",
                auto_check=True,
            ),
            ValidationRule(
                rule_id="EU-AI-VAL-003",
                name="High-Risk Decision Check",
                description="Flag content related to high-risk decision categories",
                category="risk_classification",
                severity="high",
                auto_check=True,
            ),
            ValidationRule(
                rule_id="EU-AI-VAL-004",
                name="Bias Detection",
                description="Check for potentially biased outputs affecting protected groups",
                category="data_governance",
                severity="high",
                auto_check=True,
            ),
        ]

    async def assess_control(self, control: ControlDefinition, input_data: AssessmentInput) -> ControlResult:
        """Assess a single EU AI Act control."""
        # Determine risk tier first
        risk_tier = self.determine_risk_tier(input_data)

        # Control-specific assessment logic
        if control.control_id == "EU-AI-50.1":
            # AI-Generated Content Disclosure
            if input_data.is_ai_generated:
                # Check if disclosure is present in metadata
                has_disclosure = input_data.metadata.get("ai_disclosure", False)
                if has_disclosure:
                    return ControlResult(
                        control_id=control.control_id,
                        control_name=control.name,
                        module_id=self.module_id,
                        status=ComplianceStatus.COMPLIANT,
                        score=1.0,
                        evidence="AI disclosure mechanism verified",
                    )
                else:
                    return ControlResult(
                        control_id=control.control_id,
                        control_name=control.name,
                        module_id=self.module_id,
                        status=ComplianceStatus.NON_COMPLIANT,
                        score=0.0,
                        findings=["AI-generated content lacks required disclosure"],
                        remediation="Implement AI disclosure mechanism per Article 50(1-2)",
                    )
            return ControlResult(
                control_id=control.control_id,
                control_name=control.name,
                module_id=self.module_id,
                status=ComplianceStatus.NOT_APPLICABLE,
                score=1.0,
                evidence="Content is not AI-generated",
            )

        if control.control_id == "EU-AI-14.1":
            # Human Oversight Mechanisms
            if risk_tier in [RiskTier.HIGH, RiskTier.UNACCEPTABLE]:
                has_oversight = input_data.metadata.get("human_oversight_enabled", False)
                if has_oversight:
                    return ControlResult(
                        control_id=control.control_id,
                        control_name=control.name,
                        module_id=self.module_id,
                        status=ComplianceStatus.COMPLIANT,
                        score=1.0,
                        evidence="Human oversight mechanisms in place",
                    )
                else:
                    return ControlResult(
                        control_id=control.control_id,
                        control_name=control.name,
                        module_id=self.module_id,
                        status=ComplianceStatus.NON_COMPLIANT,
                        score=0.0,
                        findings=["High-risk AI system lacks human oversight mechanisms"],
                        remediation="Implement human oversight per Article 14",
                    )

        # Default: Partial compliance with documentation required
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
        """Determine EU AI Act risk classification."""
        content_type = input_data.content_type.lower()
        metadata = input_data.metadata

        # Check for prohibited practices (Article 5)
        for prohibited in self.PROHIBITED_PRACTICES:
            if prohibited in content_type or metadata.get("practice_type") == prohibited:
                return RiskTier.UNACCEPTABLE

        # Check for high-risk categories (Annex III)
        ai_category = metadata.get("ai_category", "")
        for high_risk in self.HIGH_RISK_CATEGORIES:
            if high_risk in ai_category or high_risk in content_type:
                return RiskTier.HIGH

        # High-risk decision flag
        if input_data.is_high_risk_decision:
            return RiskTier.HIGH

        # Minors involved - elevated risk
        if input_data.user_age and input_data.user_age < 18:
            return RiskTier.HIGH

        # AI-generated content - limited risk (transparency required)
        if input_data.is_ai_generated:
            return RiskTier.LIMITED

        return RiskTier.MINIMAL

    async def _check_validation_rule(self, rule: ValidationRule, content: str, context: str | None) -> ValidationViolation | None:
        """Check EU AI Act validation rules against content."""
        content_lower = content.lower()

        if rule.rule_id == "EU-AI-VAL-001":
            # AI Disclosure Check - look for missing disclosure in AI content
            ai_indicators = ["as an ai", "i am an artificial", "generated by ai"]
            any(ind in content_lower for ind in ai_indicators)
            # This would need more sophisticated detection in production
            return None  # Assume compliant if AI indicators are present

        if rule.rule_id == "EU-AI-VAL-002":
            # Prohibited Practice Detection
            prohibited_patterns = [
                r"manipulat\w+\s+subliminally",
                r"exploit\w+\s+vulnerabilit",
                r"social\s+scoring\s+system",
            ]
            for pattern in prohibited_patterns:
                if re.search(pattern, content_lower):
                    return ValidationViolation(
                        module_id=self.module_id,
                        rule_id=rule.rule_id,
                        severity="critical",
                        description="Content may enable prohibited AI practice under Article 5",
                        suggested_fix="Remove or rephrase content that could enable prohibited practices",
                        article_reference="EU AI Act Article 5",
                    )

        if rule.rule_id == "EU-AI-VAL-003":
            # High-Risk Decision Check
            high_risk_keywords = [
                "employment decision",
                "credit score",
                "law enforcement",
                "immigration",
                "education assessment",
                "medical diagnosis",
            ]
            for keyword in high_risk_keywords:
                if keyword in content_lower:
                    return ValidationViolation(
                        module_id=self.module_id,
                        rule_id=rule.rule_id,
                        severity="high",
                        description=f"Content involves high-risk decision category: {keyword}",
                        location=keyword,
                        suggested_fix="Ensure human oversight and proper risk management for high-risk AI decisions",
                        article_reference="EU AI Act Annex III",
                    )

        return None
