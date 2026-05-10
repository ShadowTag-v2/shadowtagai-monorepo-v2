"""Digital Services Act (DSA) Compliance Module

Implements the EU Digital Services Act requirements for online platforms.
Focus areas:
- Content moderation
- Transparency reporting
- Notice-and-action procedures
- Recommender system transparency
- Advertising transparency
- VLOP/VLOSE specific obligations

Reference: Regulation (EU) 2022/2065
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


@register_module(RegulationId.DSA)
class DSAModule(ComplianceModule):
    """Digital Services Act Compliance Module

    Covers DSA requirements for:
    - Intermediary service providers
    - Hosting services
    - Online platforms
    - Very Large Online Platforms (VLOPs)
    """

    # Illegal content categories per DSA
    ILLEGAL_CONTENT_TYPES = [
        "hate_speech",
        "terrorism",
        "child_abuse",
        "counterfeit_goods",
        "illegal_products",
        "disinformation",
    ]

    def _define_metadata(self) -> ModuleMetadata:
        return ModuleMetadata(
            id=RegulationId.DSA,
            name="Digital Services Act",
            short_name="DSA",
            version="2022.2065",
            jurisdiction=Jurisdiction.EU,
            description=(
                "Regulation on a Single Market For Digital Services and amending "
                "Directive 2000/31/EC (Digital Services Act)."
            ),
            effective_date=datetime(2024, 2, 17),
            articles=[
                "Art 14 - Notice and Action Mechanisms",
                "Art 15 - Statement of Reasons",
                "Art 16 - Notification of Illegal Content",
                "Art 20 - Internal Complaint-Handling",
                "Art 22 - Trusted Flaggers",
                "Art 27 - Recommender System Transparency",
                "Art 26 - Advertising Transparency",
                "Art 34-35 - Risk Assessment (VLOPs)",
                "Art 37 - Independent Audit (VLOPs)",
                "Art 40 - Data Access (VLOPs)",
            ],
            official_url="https://eur-lex.europa.eu/eli/reg/2022/2065/oj",
            pricing_addon_usd=60.0,
        )

    def _define_controls(self) -> list[ControlDefinition]:
        return [
            # Notice and Action (Art 14-16)
            ControlDefinition(
                control_id="DSA-14",
                name="Notice and Action Mechanism",
                description="Mechanism for users to notify illegal content",
                article_ref="Article 14",
                required_evidence=[
                    "Notice submission interface",
                    "Notice handling procedures",
                    "Response time metrics",
                ],
            ),
            ControlDefinition(
                control_id="DSA-15",
                name="Statement of Reasons",
                description="Provide clear statements for content moderation decisions",
                article_ref="Article 15",
                required_evidence=["Statement template", "Decision notification system"],
            ),
            # Internal Complaint Handling (Art 20)
            ControlDefinition(
                control_id="DSA-20",
                name="Internal Complaint-Handling",
                description="Free and easy-to-use complaint mechanism for content decisions",
                article_ref="Article 20",
                required_evidence=[
                    "Complaint system documentation",
                    "Appeal procedures",
                    "Response time SLAs",
                ],
            ),
            # Trusted Flaggers (Art 22)
            ControlDefinition(
                control_id="DSA-22",
                name="Trusted Flaggers",
                description="Priority processing for trusted flagger notifications",
                article_ref="Article 22",
                required_evidence=["Trusted flagger program", "Priority queue documentation"],
            ),
            # Advertising Transparency (Art 26)
            ControlDefinition(
                control_id="DSA-26.1",
                name="Advertising Identification",
                description="Clear and unambiguous advertising labeling",
                article_ref="Article 26(1)",
                required_evidence=["Ad labeling standards", "Implementation examples"],
            ),
            ControlDefinition(
                control_id="DSA-26.2",
                name="Advertising Parameters",
                description="Disclosure of main targeting parameters",
                article_ref="Article 26(2)",
                required_evidence=["Targeting disclosure documentation"],
            ),
            # Recommender Transparency (Art 27)
            ControlDefinition(
                control_id="DSA-27",
                name="Recommender System Transparency",
                description="Clear terms on recommender system parameters",
                article_ref="Article 27",
                required_evidence=["Recommender system documentation", "User-facing explanation"],
            ),
            # VLOP-specific: Risk Assessment (Art 34-35)
            ControlDefinition(
                control_id="DSA-34",
                name="Systemic Risk Assessment",
                description="Identify and analyze systemic risks (VLOPs only)",
                article_ref="Article 34",
                required_evidence=["Risk assessment report", "Mitigation measures"],
            ),
            ControlDefinition(
                control_id="DSA-35",
                name="Risk Mitigation",
                description="Reasonable, proportionate mitigation measures",
                article_ref="Article 35",
                required_evidence=["Mitigation implementation", "Effectiveness metrics"],
            ),
            # VLOP-specific: Independent Audit (Art 37)
            ControlDefinition(
                control_id="DSA-37",
                name="Independent Audit",
                description="Annual independent audit of DSA compliance",
                article_ref="Article 37",
                required_evidence=["Audit report", "Auditor independence declaration"],
            ),
            # Transparency Reporting (Art 15, 24, 42)
            ControlDefinition(
                control_id="DSA-42",
                name="Transparency Reports",
                description="Publish regular transparency reports",
                article_ref="Article 42",
                required_evidence=[
                    "Published transparency report",
                    "Content moderation statistics",
                ],
            ),
        ]

    def _define_validation_rules(self) -> list[ValidationRule]:
        return [
            ValidationRule(
                rule_id="DSA-VAL-001",
                name="Illegal Content Detection",
                description="Detect potentially illegal content types",
                category="content_moderation",
                severity="critical",
                auto_check=True,
            ),
            ValidationRule(
                rule_id="DSA-VAL-002",
                name="Advertisement Labeling Check",
                description="Check for proper advertisement identification",
                category="advertising",
                severity="high",
                auto_check=True,
            ),
            ValidationRule(
                rule_id="DSA-VAL-003",
                name="Recommender Disclosure Check",
                description="Check for recommender system transparency",
                category="transparency",
                severity="medium",
                auto_check=True,
            ),
            ValidationRule(
                rule_id="DSA-VAL-004",
                name="Disinformation Detection",
                description="Detect potential disinformation patterns",
                category="systemic_risk",
                severity="high",
                auto_check=True,
            ),
        ]

    async def assess_control(
        self,
        control: ControlDefinition,
        input_data: AssessmentInput,
    ) -> ControlResult:
        """Assess a single DSA control."""
        metadata = input_data.metadata
        is_vlop = metadata.get("is_vlop", False)

        # VLOP-specific controls
        if control.control_id in ["DSA-34", "DSA-35", "DSA-37"] and not is_vlop:
            return ControlResult(
                control_id=control.control_id,
                control_name=control.name,
                module_id=self.module_id,
                status=ComplianceStatus.NOT_APPLICABLE,
                score=1.0,
                evidence="Control only applies to VLOPs/VLOSEs",
            )

        # Notice and Action mechanism
        if control.control_id == "DSA-14":
            has_notice_mechanism = metadata.get("notice_mechanism_implemented", False)
            if has_notice_mechanism:
                return ControlResult(
                    control_id=control.control_id,
                    control_name=control.name,
                    module_id=self.module_id,
                    status=ComplianceStatus.COMPLIANT,
                    score=1.0,
                    evidence="Notice and action mechanism verified",
                )
            return ControlResult(
                control_id=control.control_id,
                control_name=control.name,
                module_id=self.module_id,
                status=ComplianceStatus.NON_COMPLIANT,
                score=0.0,
                findings=["Notice and action mechanism not implemented"],
                remediation="Implement user notification system per Article 14",
            )

        # Advertising identification
        if control.control_id == "DSA-26.1":
            content_type = input_data.content_type.lower()
            if "advertisement" in content_type or "ad" in content_type:
                ad_labeled = metadata.get("advertisement_labeled", False)
                if ad_labeled:
                    return ControlResult(
                        control_id=control.control_id,
                        control_name=control.name,
                        module_id=self.module_id,
                        status=ComplianceStatus.COMPLIANT,
                        score=1.0,
                        evidence="Advertisement properly labeled",
                    )
                return ControlResult(
                    control_id=control.control_id,
                    control_name=control.name,
                    module_id=self.module_id,
                    status=ComplianceStatus.NON_COMPLIANT,
                    score=0.0,
                    findings=["Advertisement not clearly labeled"],
                    remediation="Add clear 'Advertisement' label per Article 26(1)",
                )
            return ControlResult(
                control_id=control.control_id,
                control_name=control.name,
                module_id=self.module_id,
                status=ComplianceStatus.NOT_APPLICABLE,
                score=1.0,
                evidence="Content is not advertising",
            )

        # Recommender transparency
        if control.control_id == "DSA-27":
            has_recommender = metadata.get("uses_recommender_system", False)
            if has_recommender:
                transparency_documented = metadata.get("recommender_transparency", False)
                if transparency_documented:
                    return ControlResult(
                        control_id=control.control_id,
                        control_name=control.name,
                        module_id=self.module_id,
                        status=ComplianceStatus.COMPLIANT,
                        score=1.0,
                        evidence="Recommender system parameters disclosed",
                    )
                return ControlResult(
                    control_id=control.control_id,
                    control_name=control.name,
                    module_id=self.module_id,
                    status=ComplianceStatus.NON_COMPLIANT,
                    score=0.0,
                    findings=["Recommender system parameters not disclosed"],
                    remediation="Document and disclose ranking parameters per Article 27",
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
        """Determine DSA systemic risk level."""
        metadata = input_data.metadata

        # VLOP/VLOSE = HIGH by default
        if metadata.get("is_vlop", False):
            return RiskTier.HIGH

        # Content moderation context
        content_type = input_data.content_type.lower()
        for illegal_type in self.ILLEGAL_CONTENT_TYPES:
            if illegal_type in content_type:
                return RiskTier.HIGH

        # Advertising targeting minors
        if input_data.user_age and input_data.user_age < 18:  # noqa: SIM102
            if "advertisement" in content_type:
                return RiskTier.HIGH

        # Recommender systems have elevated risk
        if metadata.get("uses_recommender_system", False):
            return RiskTier.LIMITED

        return RiskTier.MINIMAL

    async def _check_validation_rule(
        self,
        rule: ValidationRule,
        content: str,
        context: str | None,
    ) -> ValidationViolation | None:
        """Check DSA validation rules against content."""
        content_lower = content.lower()

        if rule.rule_id == "DSA-VAL-001":
            # Illegal Content Detection
            illegal_patterns = {
                "hate_speech": [r"hate\s+\w+", r"kill\s+all", r"exterminate"],
                "terrorism": [r"terrorist\s+attack", r"bomb\s+threat", r"jihad"],
                "counterfeit": [r"fake\s+\w+\s+for\s+sale", r"replica\s+\w+"],
            }
            for category, patterns in illegal_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, content_lower):
                        return ValidationViolation(
                            module_id=self.module_id,
                            rule_id=rule.rule_id,
                            severity="critical",
                            description=f"Potential illegal content detected: {category}",
                            suggested_fix="Review and moderate content per DSA requirements",
                            article_reference="DSA Article 14-16",
                        )

        if rule.rule_id == "DSA-VAL-002":
            # Advertisement Labeling Check
            ad_indicators = ["sponsored", "paid promotion", "advertisement", "buy now", "shop now"]
            has_ad_content = any(ind in content_lower for ind in ad_indicators)
            if has_ad_content:
                proper_labels = ["#ad", "[advertisement]", "sponsored content", "paid partnership"]
                has_label = any(label in content_lower for label in proper_labels)
                if not has_label:
                    return ValidationViolation(
                        module_id=self.module_id,
                        rule_id=rule.rule_id,
                        severity="high",
                        description="Commercial content may lack proper advertisement labeling",
                        suggested_fix="Add clear advertisement disclosure (e.g., '#ad', '[Advertisement]')",
                        article_reference="DSA Article 26(1)",
                    )

        if rule.rule_id == "DSA-VAL-004":
            # Disinformation Detection
            disinfo_patterns = [
                r"fake\s+news",
                r"they\s+don't\s+want\s+you\s+to\s+know",
                r"mainstream\s+media\s+lies",
                r"100%\s+guaranteed\s+cure",
            ]
            for pattern in disinfo_patterns:
                if re.search(pattern, content_lower):
                    return ValidationViolation(
                        module_id=self.module_id,
                        rule_id=rule.rule_id,
                        severity="high",
                        description="Content may contain disinformation patterns",
                        suggested_fix="Review content for accuracy and add appropriate context",
                        article_reference="DSA Article 34-35 (Systemic Risks)",
                    )

        return None
