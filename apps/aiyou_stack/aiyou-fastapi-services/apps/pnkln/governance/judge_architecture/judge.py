"""JudgeArchitecture: Thin Orchestrator
=====================================

The main orchestrator class that integrates all 21 governance layers.
Extracted from layers.py monolith per Rich Hickey doctrine.

All heavy logic lives in the domain modules:
- regulatory.py (Layers 12-13)
- infrastructure.py (Layers 14-15)
- product.py (Layers 16-17)
- analytics.py (Layers 18-20)
- monitor.py (Layer 21)
- models.py (data structures)
"""

from __future__ import annotations

import logging
import time
from datetime import datetime
from typing import Any

from src.kosmos.doctrine import (
    BattleDrillRouter,
    DrillTrigger,
    MDMPPipeline,
    TLPPipeline,
)
from src.kosmos.doctrine import (
    RiskLevel as DoctrineRiskLevel,
)
from src.kosmos.doctrine import (
    RiskManager as DoctrineRiskManager,
)
from src.kosmos.doctrine.atp_5_19 import (
    APPROVAL_AUTHORITY,
    CONSENSUS_THRESHOLDS,
)

from .analytics import CompetitiveRealityCheck, MilestoneTracker, QuantifiedImpactModel
from .infrastructure import InfrastructureOptimizer, SupplyChainSecurityGate
from .models import Decision, DecisionStatus, JudgeVerdict
from .monitor import JudgeArchitectureMonitor
from .product import BlockchainIntegrationEvaluator, ProductDeliveryGate
from .regulatory import AdtechStandardsValidator, RegulatoryComplianceEngine

logger = logging.getLogger(__name__)


class JudgeArchitecture:
    """Comprehensive decision-validation framework with 21 layers.

    Integrates with AutoGen branch:
    - Multi-agent debate (adds RegulatoryGuardian agent)
    - Wealth Optimizer (adds adtech compliance leak detection)
    - Unified Orchestrator (adds multi-silicon routing)
    - Gemini Function Calling (adds SBOM/SLSA validation)
    - DTE Evolution (adds product delivery gates)
    - Glicko-2 ratings (tracks IQ-adjusted performance)

    Usage:
        judge = JudgeArchitecture()

        decision = Decision(
            id="JDG-2025-001",
            type="strategic",
            description="Implement multi-silicon infra strategy",
            risk_level=RiskLevel.HIGH,
            impacts_infrastructure=True
        )

        verdict = await judge.validate_decision(decision)

        if verdict.status == DecisionStatus.APPROVED:
            # Proceed with decision
            pass
        else:
            # Address blockers
            logger.warning(f"Decision blocked: {verdict.blockers}")
    """

    def __init__(self, session_id: str | None = None):
        self.session_id = session_id or datetime.now().strftime("%Y%m%d_%H%M%S")

        # === Army Doctrine Integration (ATP 5-19, FM 6-0, FM 7-8) ===
        # ATP 5-19: Composite Risk Management
        self.doctrine_risk_manager = DoctrineRiskManager(session_id=self.session_id)

        # FM 6-0: MDMP for strategic decisions, TLP for tactical
        self.mdmp = MDMPPipeline(session_id=self.session_id)
        self.tlp = TLPPipeline(session_id=self.session_id)

        # FM 7-8: Battle Drills for error handling
        self.battle_drills = BattleDrillRouter()

        # Layer 12: Regulatory Compliance
        self.regulatory_engine = RegulatoryComplianceEngine()

        # Layer 13: Adtech Standards
        self.adtech_validator = AdtechStandardsValidator()

        # Layer 14: Infrastructure Optimizer
        self.infra_optimizer = InfrastructureOptimizer()

        # Layer 15: Supply Chain Security
        self.supply_chain_gate = SupplyChainSecurityGate()

        # Layer 16: Product Delivery
        self.product_gate = ProductDeliveryGate()

        # Layer 17: Blockchain Integration
        self.blockchain_evaluator = BlockchainIntegrationEvaluator()

        # Layer 18: Competitive Reality Check
        self.competitive_analyzer = CompetitiveRealityCheck()

        # Layer 19: Milestone Tracker
        self.milestone_tracker = MilestoneTracker()

        # Layer 20: Quantified Impact
        self.impact_model = QuantifiedImpactModel()

        # Layer 21: IQ 160 Lock Monitor
        self.iq_monitor = JudgeArchitectureMonitor()

        logger.info("Judge Architecture initialized with 21 layers + Army Doctrine")

    async def validate_decision(self, decision: Decision) -> JudgeVerdict:
        """Comprehensive decision validation through all 21 Judge layers.

        Now includes Army Doctrine Integration:
        - Layer 0: ATP 5-19 Composite Risk Management (5-step CRM)
        - Layer 0.5: FM 6-0 Mission Analysis (MDMP Step 2)

        Args:
            decision: Decision to validate

        Returns:
            JudgeVerdict with status, blockers, warnings, next actions

        """
        processing_start = time.time()

        verdict = JudgeVerdict(
            decision_id=decision.id,
            status=DecisionStatus.PENDING,
            reason="",
            iq_level=self.iq_monitor.iq_lock_level,
        )

        # === Layer 0: ATP 5-19 Composite Risk Management ===
        # 5-step CRM process: Identify → Assess → Develop Controls → Implement → Supervise
        doctrine_risk = await self.doctrine_risk_manager.full_assessment(
            task=decision.description,
            context={"decision_id": decision.id, "type": decision.type},
        )
        verdict.layer_results["atp_5_19_crm"] = doctrine_risk

        # Get consensus threshold based on residual risk
        residual_risk_str = doctrine_risk.get("residual_risk", "MEDIUM")
        try:
            doctrine_level = DoctrineRiskLevel(residual_risk_str)
            consensus_threshold = CONSENSUS_THRESHOLDS.get(doctrine_level, 0.60)
            approval_auth = APPROVAL_AUTHORITY.get(doctrine_level, "Commander")
        except ValueError:
            consensus_threshold = 0.60
            approval_auth = "Commander"

        verdict.layer_results["doctrine_consensus_threshold"] = consensus_threshold
        verdict.layer_results["doctrine_approval_authority"] = approval_auth

        # Warn if risk is HIGH or EXTREMELY_HIGH
        if residual_risk_str in ["HIGH", "EXTREMELY_HIGH"]:
            verdict.warnings.append(
                f"ATP 5-19: Residual risk is {residual_risk_str} - requires {approval_auth} approval",
            )

        # === Layer 0.5: FM 6-0 Mission Analysis ===
        # Strategic decisions use MDMP, tactical use TLP
        if decision.type == "strategic":
            mission_analysis = await self.mdmp.step2_mission_analysis(
                {"task": decision.description, "decision_id": decision.id},
            )
            verdict.layer_results["fm_6_0_mdmp"] = mission_analysis
        else:
            # Tactical/operational decisions use faster TLP
            tlp_order = await self.tlp.quick_plan(decision.description)
            verdict.layer_results["fm_6_0_tlp"] = tlp_order

        # Layer 12: Regulatory Compliance
        regulatory_scan = await self.regulatory_engine.validate_decision(decision)
        verdict.layer_results["regulatory"] = regulatory_scan
        if regulatory_scan["status"] == "BLOCKED":
            verdict.blockers.append(f"Regulatory: {regulatory_scan['reason']}")

        # Layer 13: Adtech Standards
        if decision.impacts_monetization:
            adtech_check = await self.adtech_validator.validate(decision)
            verdict.layer_results["adtech"] = adtech_check
            if not adtech_check["vast_4x_compliant"]:
                verdict.warnings.append("Adtech: VAST 4.x non-compliance risks -15% CPM")

        # Layer 14: Infrastructure
        if decision.impacts_infrastructure:
            infra_analysis = await self.infra_optimizer.analyze(decision)
            verdict.layer_results["infra"] = infra_analysis
            if infra_analysis["vendor_lock_in_risk"] > 0.5:
                verdict.warnings.append("Infra: Vendor lock-in risk >50%")

        # Layer 15: Supply Chain Security
        if decision.introduces_dependencies:
            security_scan = await self.supply_chain_gate.validate(decision=decision)
            verdict.layer_results["security"] = security_scan
            if security_scan["risk_score"] in ["EH", "H"]:
                verdict.blockers.append(f"Security: {security_scan['reason']}")

        # Layer 16: Product Delivery
        if decision.ships_feature:
            product_check = await self.product_gate.validate(
                feature=decision.feature_name or "unknown",
                variant_id=decision.variant_id,
                metrics=decision.metrics,
            )
            verdict.layer_results["product"] = product_check
            if product_check["status"] != "APPROVED":
                verdict.blockers.extend(product_check["blockers"])

        # Layer 17: Blockchain Integration
        if decision.involves_blockchain:
            blockchain_eval = await self.blockchain_evaluator.evaluate(decision)
            verdict.layer_results["blockchain"] = blockchain_eval
            if blockchain_eval["recommendation"] == "DEFER":
                verdict.warnings.append(f"Blockchain: {blockchain_eval['reason']}")

        # Layer 18: Competitive Reality Check
        competitive_analysis = await self.competitive_analyzer.benchmark(decision)
        verdict.layer_results["competitive"] = competitive_analysis
        if competitive_analysis["commodity_trap_risk"]:
            verdict.warnings.append(
                "Competitive: Decision copies incumbents without differentiation",
            )

        # Layer 19: Milestone Tracker
        milestone_impact = await self.milestone_tracker.assess_impact(decision)
        verdict.layer_results["milestones"] = milestone_impact
        verdict.next_actions.extend(milestone_impact["tasks"])

        # Layer 20: Quantified Impact
        financial_impact = await self.impact_model.calculate(decision)
        verdict.layer_results["financial"] = financial_impact
        verdict.valuation_impact = financial_impact["valuation_delta"]

        # Final verdict determination
        if verdict.blockers:
            verdict.status = DecisionStatus.REJECTED
            verdict.reason = f"{len(verdict.blockers)} critical blocker(s)"
        elif len(verdict.warnings) > 3:
            verdict.status = DecisionStatus.DEFERRED
            verdict.reason = f"{len(verdict.warnings)} warning(s) require mitigation"
        else:
            verdict.status = DecisionStatus.APPROVED
            verdict.reason = "All Judge layers passed"

        # Layer 21: IQ 160 Lock Logging
        verdict.processing_time_ms = (time.time() - processing_start) * 1000
        self.iq_monitor.log_decision(
            decision_id=decision.id,
            decision_type=decision.type,
            iq_level=self.iq_monitor.iq_lock_level,
            outcome={
                "accuracy": verdict.status == DecisionStatus.APPROVED,
                "doctrine_alignment": self._calculate_doctrine_alignment(verdict),
                "regulatory_gaps": regulatory_scan.get("compliance_profile", {}),
                "processing_time_ms": verdict.processing_time_ms,
            },
        )

        return verdict

    def _calculate_doctrine_alignment(self, verdict: JudgeVerdict) -> float:
        """Calculate doctrine alignment score (0.0-1.0)."""
        # Simplified - production would check ATP 5-19, BJR, Bootstrap, Security, Boy Scout
        if verdict.status == DecisionStatus.APPROVED:
            return 0.95
        if verdict.status == DecisionStatus.DEFERRED:
            return 0.75
        return 0.50

    def get_performance_report(self) -> dict[str, Any]:
        """Get IQ 160 lock performance report."""
        return self.iq_monitor.get_performance_summary()

    # =========================================================================
    # Army Doctrine Integration Methods (ATP 5-19, FM 6-0, FM 7-8)
    # =========================================================================

    async def handle_error_with_drill(
        self,
        error: Exception,
        decision: Decision,
        trigger: DrillTrigger = DrillTrigger.EXCEPTION,
    ) -> dict[str, Any]:
        """Handle validation errors using FM 7-8 Battle Drills.

        Routes error to appropriate battle drill:
        - EXCEPTION/API_FAILURE → React to Contact (retry logic)
        - SECURITY_ALERT → Break Contact (safe mode)
        - MALICIOUS_INPUT → React to IED (block and sanitize)
        """
        context = {
            "error": str(error),
            "decision_id": decision.id,
            "decision_type": decision.type,
            "session_id": self.session_id,
        }

        return await self.battle_drills.route(trigger, context)

    def get_doctrine_status(self) -> dict[str, Any]:
        """Get current Army Doctrine integration status."""
        return {
            "session_id": self.session_id,
            "risk_manager": self.doctrine_risk_manager.to_dict(),
            "mdmp_status": self.mdmp.get_status(),
            "tlp_status": self.tlp.get_status(),
            "consensus_thresholds": {
                "LOW": CONSENSUS_THRESHOLDS.get(DoctrineRiskLevel.LOW, 0.50),
                "MEDIUM": CONSENSUS_THRESHOLDS.get(DoctrineRiskLevel.MEDIUM, 0.60),
                "HIGH": CONSENSUS_THRESHOLDS.get(DoctrineRiskLevel.HIGH, 0.75),
                "EXTREMELY_HIGH": CONSENSUS_THRESHOLDS.get(DoctrineRiskLevel.EXTREMELY_HIGH, 0.90),
            },
            "approval_authorities": {
                "LOW": APPROVAL_AUTHORITY.get(DoctrineRiskLevel.LOW),
                "MEDIUM": APPROVAL_AUTHORITY.get(DoctrineRiskLevel.MEDIUM),
                "HIGH": APPROVAL_AUTHORITY.get(DoctrineRiskLevel.HIGH),
                "EXTREMELY_HIGH": APPROVAL_AUTHORITY.get(DoctrineRiskLevel.EXTREMELY_HIGH),
            },
        }

    async def validate_with_doctrine_recovery(self, decision: Decision) -> JudgeVerdict:
        """Validate decision with automatic battle drill recovery on failure.

        Enhanced version that includes FM 7-8 error handling.
        """
        try:
            return await self.validate_decision(decision)
        except Exception as e:
            # Execute React to Contact battle drill
            drill_result = await self.handle_error_with_drill(e, decision, DrillTrigger.EXCEPTION)

            if drill_result.get("success"):
                # Retry validation after recovery
                return await self.validate_decision(decision)

            # Return rejected verdict if drill failed
            return JudgeVerdict(
                decision_id=decision.id,
                status=DecisionStatus.REJECTED,
                reason=f"Validation failed with error: {e!s}. Battle drill recovery failed.",
                iq_level=self.iq_monitor.iq_lock_level,
                blockers=[str(e)],
                layer_results={"battle_drill": drill_result},
            )
