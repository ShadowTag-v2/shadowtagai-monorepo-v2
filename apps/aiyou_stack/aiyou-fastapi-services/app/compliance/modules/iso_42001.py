"""
ISO/IEC 42001 Compliance Module

Implements the ISO/IEC 42001:2023 AI Management System (AIMS) requirements.
Focus areas:
- Context of the organization
- Leadership and commitment
- Planning for AI management
- Support and resources
- Operation of AI systems
- Performance evaluation
- Improvement

Reference: ISO/IEC 42001:2023
"""

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


@register_module(RegulationId.ISO_42001)
class ISO42001Module(ComplianceModule):
    """
    ISO/IEC 42001 AI Management System Module

    Implements the requirements for establishing, implementing,
    maintaining, and continually improving an AI management system (AIMS).

    Follows the ISO management system structure (Clauses 4-10):
    - Clause 4: Context of the organization
    - Clause 5: Leadership
    - Clause 6: Planning
    - Clause 7: Support
    - Clause 8: Operation
    - Clause 9: Performance evaluation
    - Clause 10: Improvement
    """

    # ISO 42001 Control Domains
    CONTROL_DOMAINS = [
        "policies_for_ai",
        "internal_organization",
        "resources_for_ai",
        "ai_system_impact_assessment",
        "ai_system_lifecycle",
        "data_for_ai",
        "system_performance",
        "third_party_considerations",
    ]

    def _define_metadata(self) -> ModuleMetadata:
        return ModuleMetadata(
            id=RegulationId.ISO_42001,
            name="ISO/IEC 42001 AI Management System",
            short_name="ISO 42001",
            version="2023",
            jurisdiction=Jurisdiction.GLOBAL,
            description=(
                "International standard specifying requirements for establishing, "
                "implementing, maintaining, and continually improving an AI management "
                "system within organizations."
            ),
            effective_date=datetime(2023, 12, 18),
            articles=[
                "Clause 4 - Context of the Organization",
                "Clause 5 - Leadership",
                "Clause 6 - Planning",
                "Clause 7 - Support",
                "Clause 8 - Operation",
                "Clause 9 - Performance Evaluation",
                "Clause 10 - Improvement",
                "Annex A - AI Controls Reference",
            ],
            official_url="https://www.iso.org/standard/81230.html",
            pricing_addon_usd=65.0,
        )

    def _define_controls(self) -> list[ControlDefinition]:
        return [
            # Clause 4: Context of the Organization
            ControlDefinition(
                control_id="ISO42001-4.1",
                name="Understanding the Organization",
                description="Determine external and internal issues relevant to AI",
                article_ref="Clause 4.1",
                required_evidence=["Context analysis document", "SWOT or PESTLE analysis"],
            ),
            ControlDefinition(
                control_id="ISO42001-4.2",
                name="Interested Parties",
                description="Identify interested parties and their requirements",
                article_ref="Clause 4.2",
                required_evidence=["Stakeholder register", "Requirements matrix"],
            ),
            ControlDefinition(
                control_id="ISO42001-4.3",
                name="AIMS Scope",
                description="Define the scope of the AI management system",
                article_ref="Clause 4.3",
                required_evidence=["Scope statement", "Boundary definitions"],
            ),
            ControlDefinition(
                control_id="ISO42001-4.4",
                name="AI Management System",
                description="Establish, implement, maintain, and improve the AIMS",
                article_ref="Clause 4.4",
                required_evidence=["AIMS documentation", "Process documentation"],
            ),
            # Clause 5: Leadership
            ControlDefinition(
                control_id="ISO42001-5.1",
                name="Leadership and Commitment",
                description="Top management demonstrates leadership for AIMS",
                article_ref="Clause 5.1",
                required_evidence=[
                    "Management commitment statement",
                    "Resource allocation evidence",
                ],
            ),
            ControlDefinition(
                control_id="ISO42001-5.2",
                name="AI Policy",
                description="Establish appropriate AI policy",
                article_ref="Clause 5.2",
                required_evidence=["AI policy document", "Policy communication records"],
            ),
            ControlDefinition(
                control_id="ISO42001-5.3",
                name="Roles and Responsibilities",
                description="Assign roles, responsibilities, and authorities",
                article_ref="Clause 5.3",
                required_evidence=["Role definitions", "Organization chart", "Authority matrix"],
            ),
            # Clause 6: Planning
            ControlDefinition(
                control_id="ISO42001-6.1",
                name="Risk and Opportunity Assessment",
                description="Address risks and opportunities for AIMS",
                article_ref="Clause 6.1",
                required_evidence=["Risk assessment", "Opportunity register", "Treatment plans"],
            ),
            ControlDefinition(
                control_id="ISO42001-6.2",
                name="AI Objectives",
                description="Establish measurable AI objectives",
                article_ref="Clause 6.2",
                required_evidence=["AI objectives", "KPIs and metrics"],
            ),
            ControlDefinition(
                control_id="ISO42001-6.3",
                name="Planning of Changes",
                description="Plan changes to AIMS in a controlled manner",
                article_ref="Clause 6.3",
                required_evidence=["Change management process", "Change log"],
            ),
            # Clause 7: Support
            ControlDefinition(
                control_id="ISO42001-7.1",
                name="Resources",
                description="Determine and provide necessary resources",
                article_ref="Clause 7.1",
                required_evidence=["Resource plan", "Budget allocation"],
            ),
            ControlDefinition(
                control_id="ISO42001-7.2",
                name="Competence",
                description="Ensure competence of personnel affecting AI",
                article_ref="Clause 7.2",
                required_evidence=["Competence requirements", "Training records"],
            ),
            ControlDefinition(
                control_id="ISO42001-7.3",
                name="Awareness",
                description="Ensure personnel are aware of AI policy and AIMS",
                article_ref="Clause 7.3",
                required_evidence=["Awareness program", "Communication records"],
            ),
            ControlDefinition(
                control_id="ISO42001-7.4",
                name="Communication",
                description="Determine internal and external communications",
                article_ref="Clause 7.4",
                required_evidence=["Communication plan", "Communication matrix"],
            ),
            ControlDefinition(
                control_id="ISO42001-7.5",
                name="Documented Information",
                description="Control documented information required by AIMS",
                article_ref="Clause 7.5",
                required_evidence=["Document control procedure", "Document register"],
            ),
            # Clause 8: Operation
            ControlDefinition(
                control_id="ISO42001-8.1",
                name="Operational Planning and Control",
                description="Plan, implement, and control AI processes",
                article_ref="Clause 8.1",
                required_evidence=["Operational procedures", "Process documentation"],
            ),
            ControlDefinition(
                control_id="ISO42001-8.2",
                name="AI System Impact Assessment",
                description="Conduct impact assessments for AI systems",
                article_ref="Clause 8.2",
                required_evidence=["Impact assessment reports", "Risk-benefit analysis"],
            ),
            ControlDefinition(
                control_id="ISO42001-8.3",
                name="AI System Lifecycle",
                description="Manage AI systems throughout their lifecycle",
                article_ref="Clause 8.3",
                required_evidence=["Lifecycle management plan", "Development documentation"],
            ),
            ControlDefinition(
                control_id="ISO42001-8.4",
                name="Third-Party Considerations",
                description="Manage third-party AI components and services",
                article_ref="Clause 8.4",
                required_evidence=["Vendor assessments", "Third-party agreements"],
            ),
            # Clause 9: Performance Evaluation
            ControlDefinition(
                control_id="ISO42001-9.1",
                name="Monitoring and Measurement",
                description="Monitor, measure, analyze, and evaluate AIMS",
                article_ref="Clause 9.1",
                required_evidence=["Monitoring procedures", "Measurement results"],
            ),
            ControlDefinition(
                control_id="ISO42001-9.2",
                name="Internal Audit",
                description="Conduct internal audits of AIMS",
                article_ref="Clause 9.2",
                required_evidence=["Audit program", "Audit reports"],
            ),
            ControlDefinition(
                control_id="ISO42001-9.3",
                name="Management Review",
                description="Review AIMS at planned intervals",
                article_ref="Clause 9.3",
                required_evidence=["Review meeting minutes", "Review outputs"],
            ),
            # Clause 10: Improvement
            ControlDefinition(
                control_id="ISO42001-10.1",
                name="Continual Improvement",
                description="Continually improve AIMS effectiveness",
                article_ref="Clause 10.1",
                required_evidence=["Improvement initiatives", "Improvement tracking"],
            ),
            ControlDefinition(
                control_id="ISO42001-10.2",
                name="Nonconformity and Corrective Action",
                description="React to nonconformities and take corrective action",
                article_ref="Clause 10.2",
                required_evidence=["Nonconformity register", "Corrective action records"],
            ),
        ]

    def _define_validation_rules(self) -> list[ValidationRule]:
        return [
            ValidationRule(
                rule_id="ISO42001-VAL-001",
                name="Policy Alignment Check",
                description="Check for alignment with AI policy requirements",
                category="governance",
                severity="medium",
                auto_check=True,
            ),
            ValidationRule(
                rule_id="ISO42001-VAL-002",
                name="Lifecycle Consideration",
                description="Check for lifecycle management considerations",
                category="operation",
                severity="medium",
                auto_check=True,
            ),
            ValidationRule(
                rule_id="ISO42001-VAL-003",
                name="Third-Party Risk Check",
                description="Check for third-party AI component risks",
                category="third_party",
                severity="high",
                auto_check=True,
            ),
        ]

    async def assess_control(
        self, control: ControlDefinition, input_data: AssessmentInput
    ) -> ControlResult:
        """Assess a single ISO 42001 control."""
        metadata = input_data.metadata

        # Clause 5.2 - AI Policy
        if control.control_id == "ISO42001-5.2":
            has_policy = metadata.get("ai_policy_established", False)
            policy_communicated = metadata.get("ai_policy_communicated", False)
            if has_policy and policy_communicated:
                return ControlResult(
                    control_id=control.control_id,
                    control_name=control.name,
                    module_id=self.module_id,
                    status=ComplianceStatus.COMPLIANT,
                    score=1.0,
                    evidence="AI policy established and communicated",
                )
            elif has_policy:
                return ControlResult(
                    control_id=control.control_id,
                    control_name=control.name,
                    module_id=self.module_id,
                    status=ComplianceStatus.PARTIAL,
                    score=0.6,
                    findings=["AI policy exists but communication incomplete"],
                    remediation="Communicate AI policy to all relevant parties",
                )
            else:
                return ControlResult(
                    control_id=control.control_id,
                    control_name=control.name,
                    module_id=self.module_id,
                    status=ComplianceStatus.NON_COMPLIANT,
                    score=0.0,
                    findings=["AI policy not established"],
                    remediation="Establish and document AI policy per Clause 5.2",
                )

        # Clause 8.2 - Impact Assessment
        if control.control_id == "ISO42001-8.2":
            impact_assessed = metadata.get("impact_assessment_completed", False)
            if impact_assessed:
                return ControlResult(
                    control_id=control.control_id,
                    control_name=control.name,
                    module_id=self.module_id,
                    status=ComplianceStatus.COMPLIANT,
                    score=1.0,
                    evidence="AI system impact assessment completed",
                )
            else:
                return ControlResult(
                    control_id=control.control_id,
                    control_name=control.name,
                    module_id=self.module_id,
                    status=ComplianceStatus.NON_COMPLIANT,
                    score=0.0,
                    findings=["Impact assessment not conducted"],
                    remediation="Conduct AI system impact assessment per Clause 8.2",
                )

        # Clause 9.2 - Internal Audit
        if control.control_id == "ISO42001-9.2":
            audit_conducted = metadata.get("internal_audit_conducted", False)
            audit_date = metadata.get("last_audit_date")
            if audit_conducted and audit_date:
                return ControlResult(
                    control_id=control.control_id,
                    control_name=control.name,
                    module_id=self.module_id,
                    status=ComplianceStatus.COMPLIANT,
                    score=1.0,
                    evidence=f"Internal audit conducted: {audit_date}",
                )
            else:
                return ControlResult(
                    control_id=control.control_id,
                    control_name=control.name,
                    module_id=self.module_id,
                    status=ComplianceStatus.PARTIAL,
                    score=0.3,
                    findings=["Internal audit program not fully implemented"],
                    remediation="Establish and conduct internal audits per Clause 9.2",
                )

        # Default
        return ControlResult(
            control_id=control.control_id,
            control_name=control.name,
            module_id=self.module_id,
            status=ComplianceStatus.PARTIAL,
            score=0.5,
            findings=["Evidence required for assessment"],
            remediation=f"Provide evidence for {control.name}",
        )

    def determine_risk_tier(self, input_data: AssessmentInput) -> RiskTier | None:
        """Determine risk tier based on ISO 42001 assessment."""
        metadata = input_data.metadata

        # Check AIMS maturity
        aims_maturity = metadata.get("aims_maturity_level", 0)
        if aims_maturity < 2:
            return RiskTier.HIGH
        elif aims_maturity < 3:
            return RiskTier.LIMITED

        # Check for high-impact AI
        if input_data.is_high_risk_decision:
            return RiskTier.HIGH

        # Check third-party dependencies
        third_party_count = metadata.get("third_party_ai_components", 0)
        if third_party_count > 3:
            return RiskTier.LIMITED

        return RiskTier.MINIMAL

    async def _check_validation_rule(
        self, rule: ValidationRule, content: str, context: str | None
    ) -> ValidationViolation | None:
        """Check ISO 42001 validation rules."""
        content_lower = content.lower()

        if rule.rule_id == "ISO42001-VAL-003":
            # Third-Party Risk Check
            third_party_indicators = [
                "third-party",
                "third party",
                "vendor",
                "supplier",
                "external api",
                "cloud service",
                "outsourced",
                "bought from",
                "licensed from",
            ]
            for indicator in third_party_indicators:
                if indicator in content_lower:
                    return ValidationViolation(
                        module_id=self.module_id,
                        rule_id=rule.rule_id,
                        severity="high",
                        description=f"Third-party AI component reference detected: '{indicator}'",
                        location=indicator,
                        suggested_fix="Ensure third-party AI components are assessed per Clause 8.4",
                        article_reference="ISO 42001 Clause 8.4",
                    )

        return None

    def calculate_certification_readiness(self, clause_scores: dict[str, float]) -> dict:
        """Calculate certification readiness based on clause scores."""
        required_clauses = ["4", "5", "6", "7", "8", "9", "10"]

        scores_by_clause = {}
        for clause in required_clauses:
            clause_controls = [
                v for k, v in clause_scores.items() if k.startswith(f"ISO42001-{clause}")
            ]
            if clause_controls:
                scores_by_clause[f"Clause {clause}"] = sum(clause_controls) / len(clause_controls)
            else:
                scores_by_clause[f"Clause {clause}"] = 0.0

        overall_score = sum(scores_by_clause.values()) / len(scores_by_clause)
        min_score = min(scores_by_clause.values())

        return {
            "clause_scores": scores_by_clause,
            "overall_score": overall_score,
            "min_clause_score": min_score,
            "certification_ready": min_score >= 0.70 and overall_score >= 0.80,
            "gaps": [clause for clause, score in scores_by_clause.items() if score < 0.70],
        }
