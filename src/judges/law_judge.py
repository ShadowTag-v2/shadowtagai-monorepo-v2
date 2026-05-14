# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
LawJudge - Legal Compliance Validation
Binary ALLOW/BLOCK decisions for legal compliance and regulatory actions

Primary Use Cases:
- Regulatory compliance validation
- Contract clause approval
- Policy compliance checks
- Data privacy assessments (GDPR, CCPA)
- EU AI Act compliance validation
"""

from typing import Any
from src.judges.base_judge import BaseJudge
from src.judges.models import JudgeRequest, JudgeDecision, JudgeType
from src.risk_matrix import Probability, Severity


class LawJudge(BaseJudge):
    """
    Legal compliance judge

    Evaluates:
    - Regulatory compliance (EU AI Act, GDPR, CCPA, etc.)
    - Contract legal review
    - Policy adherence
    - Data privacy compliance
    - Export control compliance
    """

    def __init__(self):
        super().__init__(JudgeType.LAW)
        self.high_risk_ai_systems = [
            "biometric_identification",
            "critical_infrastructure",
            "law_enforcement",
            "education_scoring",
            "employment_decisions",
        ]

    def evaluate_action(self, request: JudgeRequest) -> dict[str, Any]:
        """
        Evaluate legal compliance action

        Decision logic:
        1. Regulatory framework identification
        2. Compliance requirements mapping
        3. Risk classification (EU AI Act)
        4. Documentation validation
        5. Approval authority determination
        """
        context = request.context
        action_type = request.action_type

        # Extract compliance parameters
        compliance_area = context.get("compliance_area", "unknown")
        ai_system_type = context.get("ai_system_type", None)
        has_legal_review = context.get("legal_review_completed", False)
        has_dpia = context.get("dpia_completed", False)  # Data Protection Impact Assessment
        jurisdiction = context.get("jurisdiction", "US")
        contract_value = context.get("contract_value_usd", 0)

        # Decision rules
        decision = JudgeDecision.ALLOW
        reasoning_parts = []

        # Rule 1: EU AI Act compliance
        if compliance_area == "eu_ai_act":
            if ai_system_type in self.high_risk_ai_systems:
                if not has_legal_review:
                    decision = JudgeDecision.BLOCK
                    reasoning_parts.append(f"High-risk AI system ({ai_system_type}) requires legal review - BLOCK")
                else:
                    reasoning_parts.append("High-risk AI system approved after legal review")
            else:
                reasoning_parts.append("Limited/minimal risk AI system - streamlined approval")

        # Rule 2: GDPR compliance
        elif compliance_area == "gdpr" or jurisdiction == "EU":
            if not has_dpia and context.get("processes_personal_data", False):
                decision = JudgeDecision.BLOCK
                reasoning_parts.append("GDPR: DPIA required for personal data processing - BLOCK")
            elif has_dpia:
                reasoning_parts.append("GDPR: DPIA completed, may proceed")

        # Rule 3: Contract compliance
        elif action_type == "contract_approval":
            if contract_value >= 1_000_000 and not has_legal_review:
                decision = JudgeDecision.BLOCK
                reasoning_parts.append("High-value contract requires legal review - BLOCK")
            elif has_legal_review:
                reasoning_parts.append("Contract legal review completed")

        # Rule 4: California SB 53 transparency requirements
        elif compliance_area == "ca_sb53":
            has_transparency_disclosure = context.get("transparency_disclosure", False)
            if not has_transparency_disclosure:
                decision = JudgeDecision.BLOCK
                reasoning_parts.append("CA SB 53: AI transparency disclosure required - BLOCK")

        # Rule 5: Export control compliance
        elif compliance_area == "export_control":
            destination_country = context.get("destination_country", "US")
            restricted_countries = ["CN", "RU", "IR", "KP"]
            if destination_country in restricted_countries:
                if not context.get("export_license", False):
                    decision = JudgeDecision.BLOCK
                    reasoning_parts.append(f"Export to {destination_country} requires license - BLOCK")

        # Build reasoning
        if not reasoning_parts:
            reasoning = f"{action_type} - {compliance_area} compliance check passed"
        else:
            reasoning = "; ".join(reasoning_parts)

        return {
            "decision": decision,
            "reasoning": reasoning,
            "metadata": {
                "compliance_area": compliance_area,
                "jurisdiction": jurisdiction,
                "legal_review": has_legal_review,
                "dpia_completed": has_dpia,
                "ai_system_type": ai_system_type,
            },
        }

    def extract_risk_factors(self, request: JudgeRequest, evaluation: dict[str, Any]) -> tuple[Probability, Severity, str, list[str]]:
        """
        Extract ATP 5-19 risk factors for legal compliance

        Probability factors:
        - Legal review completion
        - Documentation completeness
        - Regulatory clarity
        - Historical compliance record

        Severity factors:
        - Regulatory penalties (fines)
        - Reputational damage
        - Business continuity impact
        - Criminal liability risk
        """
        context = request.context
        compliance_area = context.get("compliance_area", "unknown")
        has_legal_review = context.get("legal_review_completed", False)
        ai_system_type = context.get("ai_system_type", None)

        # Determine probability
        if not has_legal_review:
            probability = Probability.B  # Likely (70-90% chance of violation)
        elif ai_system_type in self.high_risk_ai_systems:
            probability = Probability.C  # Possible (complex regulations)
        else:
            probability = Probability.D  # Unlikely

        # Determine severity based on compliance area
        # EU AI Act: Up to €30M or 6% global revenue
        # GDPR: Up to €20M or 4% global revenue
        # California SB 53: Civil penalties + injunctive relief
        if compliance_area == "eu_ai_act" and ai_system_type in self.high_risk_ai_systems:
            severity = Severity.I  # Catastrophic (€30M fine + criminal liability)
        elif compliance_area in ["gdpr", "eu_ai_act"]:
            severity = Severity.II  # Critical (€20M fine + reputation)
        elif compliance_area == "ca_sb53":
            severity = Severity.III  # Moderate (civil penalties)
        elif compliance_area == "export_control":
            severity = Severity.I  # Catastrophic (criminal penalties)
        else:
            severity = Severity.III  # Moderate

        # Rationale
        rationale = (
            f"Legal compliance: {compliance_area}. "
            f"{'Legal review completed' if has_legal_review else 'No legal review'}. "
            f"Risk of regulatory violation, fines, and reputational damage."
        )

        # Mitigations
        mitigations = []
        if not has_legal_review:
            mitigations.append("Obtain legal counsel review and opinion")
        if compliance_area == "gdpr" and not context.get("dpia_completed", False):
            mitigations.append("Complete Data Protection Impact Assessment (DPIA)")
        if compliance_area == "eu_ai_act":
            mitigations.append("Conduct AI risk assessment per EU AI Act Article 9")
            mitigations.append("Establish conformity assessment procedure")
            mitigations.append("Implement technical documentation requirements")
        if compliance_area == "ca_sb53":
            mitigations.append("Prepare AI transparency disclosure documentation")
            mitigations.append("Publish model cards and performance metrics")
        mitigations.append("Document compliance decision for audit trail")
        mitigations.append("Obtain senior legal counsel sign-off")

        return probability, severity, rationale, mitigations


__all__ = ["LawJudge"]
