"""
FinJudge Decision Engine
Core logic for financial governance decision-making
"""

import time
from datetime import datetime

import uuid_utils as uuid

from ..models.base import (
    AuditTrail,
    ComplianceFlag,
    ComplianceStatus,
    Condition,
    DecisionOutcome,
    DecisionRequest,
    DecisionRuling,
    Evidence,
    EvidenceType,
    FinancialImpact,
    Probability,
    QuantitativeRisk,
    Rationale,
    RiskAssessment,
    RiskLevel,
    Severity,
)
from ..rules.compliance import ComplianceEngine
from ..rules.policy import PolicyEngine
from .atp_risk import (
    assess_probability_from_percentage,
    assess_residual_risk,
    assess_severity_from_loss,
    calculate_risk_level,
    get_risk_description,
)


class DecisionEngine:
    """
    Core decision engine for FinJudge rulings
    Orchestrates risk assessment, compliance checking, and ruling synthesis
    """

    def __init__(self, model_version: str = "v0.1.0"):
        """
        Initialize decision engine

        Args:
            model_version: FinJudge version identifier
        """
        self.model_version = model_version
        self.compliance_engine = ComplianceEngine()
        self.policy_engine = PolicyEngine()

    def evaluate(self, request: DecisionRequest) -> DecisionRuling:
        """
        Main evaluation method: produce ruling from request

        Args:
            request: Decision request

        Returns:
            Decision ruling

        Process:
            1. Validate evidence completeness
            2. Assess risk (ATP 5-19)
            3. Check compliance
            4. Apply policy rules
            5. Synthesize decision
            6. Generate ruling
        """
        start_time = time.time()

        # Track rules applied
        rules_applied = []

        # 1. Validate evidence
        evidence_score = self._assess_evidence_quality(request.evidence)

        # 2. Risk assessment
        risk_assessment = self._assess_risk(request)
        rules_applied.append("ATP-5-19-Risk-Matrix")

        # 3. Compliance check
        compliance_flags = self.compliance_engine.check_compliance(
            request.decision_type, request.constraints.regulatory, request.evidence
        )
        rules_applied.extend([f"Compliance-{flag.regulation}" for flag in compliance_flags])

        # 4. Policy rules
        policy_violations = self.policy_engine.check_policies(
            request.constraints.policy_rules, request.evidence, request.constraints.risk_limits
        )
        rules_applied.extend(request.constraints.policy_rules)

        # 5. Synthesize decision
        decision, confidence = self._synthesize_decision(
            risk_assessment, compliance_flags, policy_violations, evidence_score
        )

        # 6. Generate rationale
        rationale = self._generate_rationale(
            request,
            risk_assessment,
            compliance_flags,
            policy_violations,
            evidence_score,
            confidence,
        )

        # 7. Determine conditions
        conditions = self._generate_conditions(
            decision, risk_assessment, compliance_flags, policy_violations
        )

        # 8. Next steps
        next_steps = self._generate_next_steps(decision, risk_assessment, compliance_flags)

        # 9. Financial impact (if estimable)
        financial_impact = self._estimate_financial_impact(request.evidence)

        # Computation time
        computation_time_ms = (time.time() - start_time) * 1000

        # Build audit trail
        audit_trail = AuditTrail(
            evidence_reviewed=len(request.evidence),
            rules_applied=rules_applied,
            computation_time_ms=computation_time_ms,
            model_version=self.model_version,
        )

        # Construct ruling
        ruling = DecisionRuling(
            ruling_id=uuid.uuid7(),
            request_id=request.request_id,
            timestamp=datetime.utcnow(),
            decision=decision,
            rationale=rationale,
            risk_assessment=risk_assessment,
            confidence=confidence,
            conditions=conditions,
            next_steps=next_steps,
            audit_trail=audit_trail,
            compliance_flags=compliance_flags,
            financial_impact=financial_impact,
        )

        return ruling

    def _assess_evidence_quality(self, evidence: list[Evidence]) -> float:
        """
        Assess overall evidence quality

        Args:
            evidence: List of evidence items

        Returns:
            Quality score (0-100)
        """
        if not evidence:
            return 0.0

        # Weight evidence by type importance
        type_weights = {
            EvidenceType.MARKET_DATA: 1.0,
            EvidenceType.RISK_METRIC: 1.2,
            EvidenceType.COMPLIANCE_DOC: 1.5,
            EvidenceType.REGULATORY_FILING: 1.5,
            EvidenceType.MODEL_OUTPUT: 1.0,
            EvidenceType.PRECEDENT: 1.1,
            EvidenceType.HISTORICAL_PERFORMANCE: 0.9,
            EvidenceType.CREDIT_RATING: 1.3,
        }

        weighted_sum = 0.0
        weight_total = 0.0

        for item in evidence:
            weight = type_weights.get(item.type, 1.0)
            weighted_sum += item.confidence * weight
            weight_total += weight

        return weighted_sum / weight_total if weight_total > 0 else 0.0

    def _assess_risk(self, request: DecisionRequest) -> RiskAssessment:
        """
        Assess risk using ATP 5-19 framework

        Args:
            request: Decision request

        Returns:
            Risk assessment
        """
        # Extract risk metrics from evidence
        probability_pct = 50.0  # Default: occasional
        loss_usd = 500_000.0  # Default: moderate severity
        var_95_usd = None
        expected_loss_usd = None
        worst_case_usd = None

        for item in request.evidence:
            if item.type == EvidenceType.RISK_METRIC:
                data = item.data
                if "probability" in data:
                    probability_pct = float(data["probability"])
                if "expected_loss" in data:
                    loss_usd = float(data["expected_loss"])
                if "var_95" in data:
                    var_95_usd = float(data["var_95"])
                    loss_usd = max(loss_usd, var_95_usd)  # Use higher value
                if "worst_case" in data:
                    worst_case_usd = float(data["worst_case"])

        # Calculate ATP 5-19 levels
        probability = assess_probability_from_percentage(probability_pct)
        severity = assess_severity_from_loss(loss_usd)
        risk_level = calculate_risk_level(probability, severity)

        # Generate mitigation measures
        mitigation = self._generate_mitigation(risk_level, severity, request)

        # Estimate residual risk (assume 60% mitigation effectiveness)
        residual_risk = assess_residual_risk(risk_level, 60.0)

        # Quantitative risk
        quantitative = QuantitativeRisk(
            var_95=var_95_usd,
            expected_loss=expected_loss_usd or loss_usd,
            worst_case=worst_case_usd or loss_usd * 2.5,
        )

        return RiskAssessment(
            probability=probability,
            severity=severity,
            level=risk_level,
            mitigation=mitigation,
            residual_risk=residual_risk,
            quantitative=quantitative,
        )

    def _generate_mitigation(
        self, risk_level: RiskLevel, severity: Severity, request: DecisionRequest
    ) -> list[str]:
        """Generate risk mitigation measures"""
        mitigation = []

        if risk_level in (RiskLevel.EH, RiskLevel.H):
            mitigation.append("Mandatory senior management review required")

        if severity in (Severity.I, Severity.II):
            mitigation.append("Reduce position size by 30-50%")
            mitigation.append("Implement real-time monitoring with automatic alerts")

        if request.constraints.risk_limits and request.constraints.risk_limits.stop_loss:
            mitigation.append(f"Enforce stop-loss at {request.constraints.risk_limits.stop_loss}")

        if risk_level != RiskLevel.L:
            mitigation.append("Daily risk reporting to risk committee")

        return mitigation

    def _synthesize_decision(
        self,
        risk_assessment: RiskAssessment,
        compliance_flags: list[ComplianceFlag],
        policy_violations: list[str],
        evidence_score: float,
    ) -> tuple[DecisionOutcome, float]:
        """
        Synthesize final decision from all inputs

        Args:
            risk_assessment: ATP 5-19 risk assessment
            compliance_flags: Regulatory compliance issues
            policy_violations: Policy rule violations
            evidence_score: Evidence quality score

        Returns:
            Tuple of (decision, confidence)
        """
        # Compliance violations = immediate deny
        has_violations = any(flag.status == ComplianceStatus.VIOLATION for flag in compliance_flags)
        if has_violations:
            return DecisionOutcome.DENY, 95.0

        # Policy violations
        if policy_violations:
            return DecisionOutcome.DENY, 90.0

        # Risk-based decision
        risk_level = risk_assessment.level

        # Low evidence quality = defer or escalate
        if evidence_score < 50:
            if risk_level in (RiskLevel.EH, RiskLevel.H):
                return DecisionOutcome.DENY, 75.0
            else:
                return DecisionOutcome.DEFER, 60.0

        # Decision matrix
        if risk_level == RiskLevel.EH:
            decision = DecisionOutcome.DENY
            confidence = 92.0
        elif risk_level == RiskLevel.H:
            decision = DecisionOutcome.APPROVE_WITH_CONDITIONS
            confidence = 85.0
        elif risk_level == RiskLevel.M:
            decision = DecisionOutcome.APPROVE_WITH_CONDITIONS
            confidence = 88.0
        else:  # L
            decision = DecisionOutcome.APPROVE
            confidence = 93.0

        # Adjust confidence by evidence quality
        confidence = confidence * (0.7 + 0.3 * (evidence_score / 100))

        # Cap confidence warnings
        has_warnings = any(flag.status == ComplianceStatus.WARNING for flag in compliance_flags)
        if has_warnings:
            confidence = min(confidence, 85.0)

        return decision, round(confidence, 1)

    def _generate_rationale(
        self,
        request: DecisionRequest,
        risk_assessment: RiskAssessment,
        compliance_flags: list[ComplianceFlag],
        policy_violations: list[str],
        evidence_score: float,
        confidence: float,
    ) -> Rationale:
        """Generate Supreme Court-style rationale"""

        # Summary paragraph
        "approve" if request.decision_type.value.endswith("approval") else "assess"
        risk_desc = get_risk_description(risk_assessment.level)

        summary = (
            f"Upon thorough review of the {request.decision_type.value} request "
            f"for {request.context.entity}, this ruling finds the assessed risk level "
            f"to be {risk_assessment.level.value} ({risk_desc}). "
            f"The ATP 5-19 framework assigns probability {risk_assessment.probability.value} "
            f"(~{self._prob_to_pct(risk_assessment.probability)}% likelihood) and "
            f"severity {risk_assessment.severity.value} ({self._sev_to_usd(risk_assessment.severity)}). "
        )

        if compliance_flags:
            compliant_count = sum(
                1 for f in compliance_flags if f.status == ComplianceStatus.COMPLIANT
            )
            summary += (
                f"Compliance review covered {len(compliance_flags)} regulations, "
                f"with {compliant_count} showing full compliance. "
            )

        summary += (
            f"Evidence quality scored {evidence_score:.1f}/100 across {len(request.evidence)} items. "
            f"This ruling carries {confidence:.1f}% confidence."
        )

        # Key factors
        key_factors = []
        key_factors.append(f"Risk level: {risk_assessment.level.value} ({risk_desc})")

        if evidence_score >= 80:
            key_factors.append(f"High-quality evidence (score: {evidence_score:.1f}/100)")
        elif evidence_score < 60:
            key_factors.append(f"Limited evidence quality (score: {evidence_score:.1f}/100)")

        for flag in compliance_flags:
            if flag.status == ComplianceStatus.VIOLATION:
                key_factors.append(f"VIOLATION: {flag.regulation} - {flag.details}")
            elif flag.status == ComplianceStatus.WARNING:
                key_factors.append(f"Warning: {flag.regulation} requires attention")

        if policy_violations:
            key_factors.append(f"Policy violations detected: {', '.join(policy_violations)}")

        if risk_assessment.mitigation:
            key_factors.append(
                f"Mitigation measures available: {len(risk_assessment.mitigation)} identified"
            )

        # Precedents (placeholder - would query ruling history)
        precedents = []

        # Dissent (if confidence < 80)
        dissent = None
        if confidence < 80:
            dissent = (
                f"Minority opinion notes that confidence level {confidence:.1f}% "
                "falls below the 80% threshold typically required for high-conviction rulings. "
                "Additional evidence or analysis may be warranted before final approval."
            )

        # Legal basis
        legal_basis = compliance_flags[0].regulation if compliance_flags else []
        if isinstance(legal_basis, str):
            legal_basis = [legal_basis]
        if request.constraints.regulatory:
            legal_basis.extend(request.constraints.regulatory)

        return Rationale(
            summary=summary,
            key_factors=key_factors,
            precedents=precedents,
            dissent=dissent,
            legal_basis=list(set(legal_basis)),  # Deduplicate
        )

    def _generate_conditions(
        self,
        decision: DecisionOutcome,
        risk_assessment: RiskAssessment,
        compliance_flags: list[ComplianceFlag],
        policy_violations: list[str],
    ) -> list[Condition]:
        """Generate approval conditions"""
        conditions = []

        if decision != DecisionOutcome.APPROVE_WITH_CONDITIONS:
            return conditions

        # Risk-based conditions
        if risk_assessment.level in (RiskLevel.H, RiskLevel.EH):
            conditions.append(
                Condition(
                    condition="Senior management sign-off required",
                    mandatory=True,
                    responsible_party="Risk Committee",
                )
            )

        for mitigation in risk_assessment.mitigation:
            conditions.append(
                Condition(condition=mitigation, mandatory=True, responsible_party="Trading Desk")
            )

        # Compliance warnings
        for flag in compliance_flags:
            if flag.status == ComplianceStatus.WARNING:
                conditions.append(
                    Condition(
                        condition=f"Address compliance warning: {flag.details}",
                        mandatory=False,
                        responsible_party="Compliance Team",
                    )
                )

        return conditions

    def _generate_next_steps(
        self,
        decision: DecisionOutcome,
        risk_assessment: RiskAssessment,
        compliance_flags: list[ComplianceFlag],
    ) -> list[str]:
        """Generate recommended next steps"""
        steps = []

        if decision == DecisionOutcome.APPROVE:
            steps.append("Proceed with execution as planned")
            steps.append("Monitor position per standard risk protocols")

        elif decision == DecisionOutcome.APPROVE_WITH_CONDITIONS:
            steps.append("Implement all mandatory conditions before proceeding")
            steps.append("Document condition compliance in audit trail")
            steps.append("Escalate to risk committee if conditions cannot be met")

        elif decision == DecisionOutcome.DENY:
            steps.append("Do not proceed with proposed action")
            steps.append("Review denial rationale with stakeholders")
            steps.append("Consider alternative approaches if business need persists")

        elif decision == DecisionOutcome.ESCALATE:
            steps.append("Escalate to senior risk management for final determination")
            steps.append("Gather additional evidence to improve confidence")

        elif decision == DecisionOutcome.DEFER:
            steps.append("Gather additional evidence before re-submission")
            steps.append("Address evidence quality gaps identified in rationale")

        # Risk-specific steps
        if risk_assessment.level in (RiskLevel.H, RiskLevel.EH):
            steps.append("Implement enhanced monitoring with daily risk reporting")

        return steps

    def _estimate_financial_impact(self, evidence: list[Evidence]) -> FinancialImpact | None:
        """Estimate financial impact from evidence"""
        estimated_pnl = None
        capital_requirement = None
        cost = None

        for item in evidence:
            if item.type == EvidenceType.RISK_METRIC:
                data = item.data
                if "expected_pnl" in data:
                    estimated_pnl = float(data["expected_pnl"])
                if "capital_requirement" in data:
                    capital_requirement = float(data["capital_requirement"])
                if "transaction_cost" in data:
                    cost = float(data["transaction_cost"])

        if any(x is not None for x in [estimated_pnl, capital_requirement, cost]):
            return FinancialImpact(
                estimated_pnl=estimated_pnl, capital_requirement=capital_requirement, cost=cost
            )

        return None

    def _prob_to_pct(self, prob: Probability) -> str:
        """Convert probability enum to percentage range"""
        ranges = {
            Probability.A: "80-100",
            Probability.B: "50-79",
            Probability.C: "20-49",
            Probability.D: "5-19",
            Probability.E: "0-5",
        }
        return ranges[prob]

    def _sev_to_usd(self, sev: Severity) -> str:
        """Convert severity enum to USD range"""
        ranges = {
            Severity.I: ">$10M loss",
            Severity.II: "$1M-$10M loss",
            Severity.III: "$100K-$1M loss",
            Severity.IV: "<$100K loss",
        }
        return ranges[sev]
