"""Pure Judge Engine (v0.2)
Risk classification without compliance/policy enforcement
"""

import hashlib
import json
import time
from datetime import datetime
from typing import Any

from ..models.judge import (
    AuditTrail,
    Disposition,
    ExplanationNL,
    JudgeRequest,
    JudgeRuling,
    NumericOverview,
    PrecedentLink,
    Probability,
    Recommendation,
    RiskLevel,
    RiskMatrix,
    Severity,
    TimeBoundary,
)
from .atp_risk import calculate_risk_level
from .feature_synthesis import FeatureSynthesizer


class PureJudge:
    """Pure judge engine - classifies risk, does not enforce policy
    Consumes metrics from upstream, produces risk assessment
    """

    def __init__(self, version: str = "v0.2.0"):
        """Initialize pure judge"""
        self.version = version
        self.synthesizer = FeatureSynthesizer(version=version)

    def judge(self, request: JudgeRequest) -> JudgeRuling:
        """Main judging method: classify risk and provide recommendation

        Args:
            request: Judge request with metrics from upstream

        Returns:
            Judge ruling with risk assessment and recommendation

        Process:
            1. Synthesize features from metrics
            2. Infer ATP 5-19 probability and severity
            3. Calculate risk level from matrix
            4. Determine disposition
            5. Generate controls and explanation
            6. Create audit trail

        """
        start_time = time.time()

        # 1. Synthesize features
        features = self.synthesizer.synthesize(request.metrics, request.flags)

        # 2. Infer ATP 5-19 levels
        probability, prob_confidence = self.synthesizer.infer_probability(features)
        severity, sev_confidence = self.synthesizer.infer_severity(features, request.metrics)

        # 3. Calculate risk level
        risk_level = self._map_to_risk_level(calculate_risk_level(probability, severity))

        # 4. Risk matrix with rationale
        risk_matrix = RiskMatrix(
            probability_class=probability,
            severity_class=severity,
            risk_level=risk_level,
            rationale_summary=self._generate_rationale_summary(
                probability, severity, risk_level, request,
            ),
        )

        # 5. Numeric overview
        numeric_overview = self._generate_numeric_overview(features, request.metrics)

        # 6. Recommendation
        recommendation = self._generate_recommendation(
            risk_level, features, request.flags, prob_confidence, sev_confidence,
        )

        # 7. Precedent links (placeholder - would query history)
        precedent_links = self._find_precedents(request.prior_precedent_ids)

        # 8. Natural language explanation
        explanation_nl = self._generate_explanation(
            request, risk_matrix, features, numeric_overview,
        )

        # 9. Audit trail
        computation_time_ms = (time.time() - start_time) * 1000
        audit_trail = self._create_audit_trail(request, features, computation_time_ms)

        # Construct ruling
        ruling = JudgeRuling(
            decision_id=request.decision_id,
            timestamp=datetime.utcnow(),
            judge_version=self.version,
            risk_matrix=risk_matrix,
            numeric_overview=numeric_overview,
            recommendation=recommendation,
            precedent_links=precedent_links,
            explanation_nl=explanation_nl,
            audit_trail=audit_trail,
        )

        return ruling

    def _map_to_risk_level(self, atp_risk_level) -> RiskLevel:
        """Map ATP 5-19 risk level to enum"""
        from .atp_risk import RiskLevel as ATPRiskLevel

        mapping = {
            ATPRiskLevel.EH: RiskLevel.EXTREME,
            ATPRiskLevel.H: RiskLevel.HIGH,
            ATPRiskLevel.M: RiskLevel.MODERATE,
            ATPRiskLevel.L: RiskLevel.LOW,
        }
        return mapping[atp_risk_level]

    def _generate_rationale_summary(
        self,
        probability: Probability,
        severity: Severity,
        risk_level: RiskLevel,
        request: JudgeRequest,
    ) -> str:
        """Generate concise rationale summary"""
        prob_desc = {
            Probability.A: "Frequent (≥80% probability)",
            Probability.B: "Likely (50-79% probability)",
            Probability.C: "Moderate (20-49% probability)",
            Probability.D: "Seldom (5-19% probability)",
            Probability.E: "Unlikely (<5% probability)",
        }

        sev_desc = {
            Severity.I: ">$10M potential loss",
            Severity.II: "$1M-$10M potential loss",
            Severity.III: "$100K-$1M potential loss",
            Severity.IV: "<$100K potential loss",
        }

        # Extract key metric for context
        context_detail = ""
        if request.metrics.exposure:
            context_detail = f" at {request.metrics.exposure.pct_aum:.1f}% AUM exposure"
        elif request.metrics.tail_risk and request.metrics.tail_risk.var_95:
            context_detail = f" with ${abs(request.metrics.tail_risk.var_95):,.0f} VaR"

        return (
            f"{prob_desc[probability]} of {sev_desc[severity]}"
            f"{context_detail} based on upstream metrics."
        )

    def _generate_numeric_overview(self, features: dict[str, Any], metrics) -> NumericOverview:
        """Generate numeric overview of key metrics"""
        key_metrics = {}

        # Extract most relevant metrics
        if "capital_at_risk" in features:
            key_metrics["capital_at_risk_score"] = features["capital_at_risk"]

        if "var_to_budget" in features:
            key_metrics["var_to_budget_ratio"] = round(features["var_to_budget"], 2)

        if "liquidity_heat" in features:
            key_metrics["liquidity_heat"] = round(features["liquidity_heat"], 1)

        if "exposure_concentration" in features:
            key_metrics["exposure_pct_aum"] = round(features["exposure_concentration"], 1)

        if metrics.tail_risk and metrics.tail_risk.var_95:
            key_metrics["var_95"] = metrics.tail_risk.var_95

        # Determine primary risk driver
        primary_driver = self._identify_primary_driver(features)

        return NumericOverview(key_metrics=key_metrics, primary_risk_driver=primary_driver)

    def _identify_primary_driver(self, features: dict[str, Any]) -> str:
        """Identify primary risk driver from features"""
        drivers = []

        # Score each potential driver
        if features.get("flag_severity", 0) > 50:
            drivers.append(("policy_violation", features["flag_severity"]))

        if features.get("var_to_budget", 0) > 1.0:
            drivers.append(("var_budget_breach", features["var_to_budget"] * 50))

        if features.get("liquidity_heat", 0) > 70:
            drivers.append(("liquidity_stress", features["liquidity_heat"]))

        if features.get("tail_severity", 0) > 60:
            drivers.append(("tail_risk", features["tail_severity"]))

        if features.get("credit_risk_composite", 0) > 70:
            drivers.append(("credit_risk", features["credit_risk_composite"]))

        if features.get("capital_at_risk", 0) > 75:
            drivers.append(("concentration", features["capital_at_risk"]))

        # Return highest scoring driver
        if drivers:
            drivers.sort(key=lambda x: x[1], reverse=True)
            return drivers[0][0]

        return "general_risk"

    def _generate_recommendation(
        self,
        risk_level: RiskLevel,
        features: dict[str, Any],
        flags,
        prob_confidence: float,
        sev_confidence: float,
    ) -> Recommendation:
        """Generate recommendation based on risk level"""
        # Disposition logic
        if flags.regulatory_flags:
            # Regulatory flags = immediate escalate or reject
            disposition = Disposition.REJECT
        elif risk_level == RiskLevel.EXTREME:
            disposition = Disposition.REJECT
        elif risk_level == RiskLevel.HIGH:
            disposition = Disposition.ESCALATE if flags.policy_flags else Disposition.MODIFY
        elif risk_level == RiskLevel.MODERATE:
            disposition = Disposition.MODIFY
        else:  # LOW
            disposition = Disposition.APPROVE

        # Low confidence = escalate
        avg_confidence = (prob_confidence + sev_confidence) / 2
        if avg_confidence < 60 and risk_level in (RiskLevel.HIGH, RiskLevel.EXTREME):
            disposition = Disposition.ESCALATE

        # Generate controls
        required_controls = self._generate_controls(risk_level, features, flags)

        # Time boundaries
        time_boundaries = self._generate_time_boundaries(risk_level, features)

        return Recommendation(
            disposition=disposition,
            required_controls=required_controls,
            time_boundaries=time_boundaries,
        )

    def _generate_controls(
        self, risk_level: RiskLevel, features: dict[str, Any], flags,
    ) -> list[str]:
        """Generate required risk controls"""
        controls = []

        # Risk level based controls
        if risk_level == RiskLevel.EXTREME:
            controls.append("CEO approval required (RA-4 decision)")
            controls.append("Immediate risk committee review")

        elif risk_level == RiskLevel.HIGH:
            controls.append("Senior management approval required (RA-3 decision)")

        # Feature-specific controls
        if features.get("var_to_budget", 0) > 1.0:
            ratio = features["var_to_budget"]
            reduction_pct = int((1 - 1 / ratio) * 100)
            controls.append(f"Reduce position size by {reduction_pct}% to meet VaR budget")

        if features.get("capital_at_risk", 0) > 75:
            controls.append("Reduce position to ≤5% AUM concentration")

        if features.get("liquidity_heat", 0) > 70:
            controls.append("Add protective hedge to mitigate liquidity risk")
            controls.append("Establish staggered exit plan (avoid fire sale)")

        if features.get("tail_severity", 0) > 60:
            controls.append("Implement stop-loss at -10% to limit downside")

        # Flag-based controls
        for flag in flags.regulatory_flags:
            controls.append(f"Resolve regulatory flag: {flag}")

        for flag in flags.policy_flags:
            controls.append(f"Address policy flag: {flag}")

        # Risk monitoring
        if risk_level in (RiskLevel.HIGH, RiskLevel.EXTREME):
            controls.append("Daily risk reporting until position reduced")

        return controls

    def _generate_time_boundaries(
        self, risk_level: RiskLevel, features: dict[str, Any],
    ) -> TimeBoundary | None:
        """Generate time-based review boundaries"""
        if risk_level in (RiskLevel.LOW, RiskLevel.MODERATE):
            # Moderate/low risk = monthly review
            return TimeBoundary(re_review_if="position size increases >20%", reassess_in_days=30)
        if risk_level == RiskLevel.HIGH:
            # High risk = weekly review
            return TimeBoundary(re_review_if="drawdown exceeds 5%", reassess_in_days=7)
        # EXTREME
        # Extreme risk = daily review
        return TimeBoundary(re_review_if="any adverse movement", reassess_in_days=1)

    def _find_precedents(self, precedent_ids: list[str]) -> list[PrecedentLink]:
        """Find similar past decisions (placeholder)"""
        # In production, would query decision history database
        # For MVP, return empty list or mock data
        return []

    def _generate_explanation(
        self,
        request: JudgeRequest,
        risk_matrix: RiskMatrix,
        features: dict[str, Any],
        numeric_overview: NumericOverview,
    ) -> ExplanationNL:
        """Generate natural language explanation"""
        # Short summary (≤3 sentences)
        risk_desc = {
            RiskLevel.EXTREME: "EXTREME risk",
            RiskLevel.HIGH: "HIGH risk",
            RiskLevel.MODERATE: "MODERATE risk",
            RiskLevel.LOW: "LOW risk",
        }

        summary_parts = [
            f"This decision is {risk_desc[risk_matrix.risk_level]} "
            f"({risk_matrix.probability_class.value}-{risk_matrix.severity_class.value}).",
            risk_matrix.rationale_summary,
        ]

        # Add primary driver
        driver_explanations = {
            "var_budget_breach": "VaR budget breach detected",
            "liquidity_stress": "Limited market liquidity creates exit risk",
            "tail_risk": "Fat tail distribution indicates extreme loss potential",
            "credit_risk": "Elevated counterparty credit risk",
            "concentration": "High portfolio concentration",
            "policy_violation": "Policy violations flagged by upstream systems",
            "general_risk": "Multiple risk factors present",
        }

        driver = numeric_overview.primary_risk_driver
        if driver in driver_explanations:
            summary_parts.append(driver_explanations[driver] + ".")

        short_summary = " ".join(summary_parts)

        # Detail bullets (WHAT/WHY/WHERE)
        detail_bullets = []

        # WHAT
        what_bullet = f"WHAT: {request.intent_nl}"
        detail_bullets.append(what_bullet)

        # WHY (risky or safe)
        why_parts = []
        if risk_matrix.risk_level in (RiskLevel.HIGH, RiskLevel.EXTREME):
            why_parts.append("WHY RISKY:")
            if features.get("var_to_budget", 0) > 1.0:
                why_parts.append(
                    f"VaR exceeds budget by {int((features['var_to_budget'] - 1) * 100)}%",
                )
            if features.get("capital_at_risk", 0) > 75:
                why_parts.append("High portfolio concentration")
            if features.get("liquidity_heat", 0) > 70:
                why_parts.append("Limited liquidity for exit")
            if request.flags.policy_flags:
                why_parts.append(f"Policy flags: {', '.join(request.flags.policy_flags)}")
        else:
            why_parts.append("WHY ACCEPTABLE: Risk metrics within acceptable bounds")

        detail_bullets.append(" ".join(why_parts) if len(why_parts) > 1 else why_parts[0])

        # WHERE (uncertainty)
        where_parts = ["WHERE UNCERTAIN:"]
        if not request.metrics.tail_risk:
            where_parts.append("No tail risk metrics provided")
        if not request.metrics.liquidity_metrics:
            where_parts.append("Liquidity conditions unclear")
        if request.metrics.volatility and request.metrics.volatility.regime_tag == "stressed":
            where_parts.append("Market regime volatility uncertain")
        if len(where_parts) == 1:
            where_parts.append("Limited uncertainty with available metrics")

        detail_bullets.append(" ".join(where_parts))

        return ExplanationNL(
            short_summary=short_summary[:500],  # Cap at 500 chars
            detail_bullets=detail_bullets,
        )

    def _create_audit_trail(
        self, request: JudgeRequest, features: dict[str, Any], computation_time_ms: float,
    ) -> AuditTrail:
        """Create audit trail for decision"""
        # Hash input
        input_json = request.model_dump_json()
        input_hash = hashlib.sha256(input_json.encode()).hexdigest()

        # Hash feature vector
        feature_json = json.dumps(features, sort_keys=True)
        feature_vector_hash = hashlib.sha256(feature_json.encode()).hexdigest()

        return AuditTrail(
            input_hash=input_hash, feature_vector_hash=feature_vector_hash, overrides=[],
        )
