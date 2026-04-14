"""Compliance Rule Engine
Regulatory compliance checking for financial decisions
"""

from ..models.base import ComplianceFlag, ComplianceStatus, DecisionType, Evidence


class ComplianceEngine:
    """Regulatory compliance checking engine
    Validates decisions against financial regulations
    """

    def __init__(self):
        """Initialize compliance engine with regulatory rules"""
        self.regulation_db = self._initialize_regulations()

    def _initialize_regulations(self) -> dict:
        """Initialize regulatory rule database
        In production, this would load from external compliance system
        """
        return {
            "SEC Rule 15c3-1": {
                "name": "Net Capital Rule",
                "description": "Broker-dealer minimum net capital requirements",
                "applicable_types": [DecisionType.TRADE_APPROVAL, DecisionType.PORTFOLIO_REBALANCE],
            },
            "MiFID II": {
                "name": "Markets in Financial Instruments Directive II",
                "description": "EU trading transparency and investor protection",
                "applicable_types": [DecisionType.TRADE_APPROVAL, DecisionType.COMPLIANCE_CHECK],
            },
            "Dodd-Frank": {
                "name": "Dodd-Frank Wall Street Reform Act",
                "description": "U.S. financial regulatory reform",
                "applicable_types": [
                    DecisionType.RISK_ASSESSMENT,
                    DecisionType.COUNTERPARTY_APPROVAL,
                ],
            },
            "FINRA Rule 4210": {
                "name": "Margin Requirements",
                "description": "Margin requirements for securities transactions",
                "applicable_types": [DecisionType.TRADE_APPROVAL],
            },
            "Regulation T": {
                "name": "Federal Reserve Margin Requirements",
                "description": "Credit by brokers and dealers",
                "applicable_types": [DecisionType.TRADE_APPROVAL],
            },
            "Basel III": {
                "name": "Basel III Capital Requirements",
                "description": "International banking capital and liquidity standards",
                "applicable_types": [DecisionType.RISK_ASSESSMENT, DecisionType.LIMIT_BREACH],
            },
        }

    def check_compliance(
        self, decision_type: DecisionType, regulations: list[str], evidence: list[Evidence],
    ) -> list[ComplianceFlag]:
        """Check compliance with specified regulations

        Args:
            decision_type: Type of decision being evaluated
            regulations: List of regulation identifiers to check
            evidence: Supporting evidence for compliance checks

        Returns:
            List of compliance flags

        """
        flags = []

        # If no regulations specified, check applicable defaults
        if not regulations:
            regulations = self._get_applicable_regulations(decision_type)

        for regulation in regulations:
            flag = self._check_regulation(regulation, decision_type, evidence)
            if flag:
                flags.append(flag)

        # If no flags generated, add default compliant flag
        if not flags and regulations:
            flags.append(
                ComplianceFlag(
                    regulation="General Compliance",
                    status=ComplianceStatus.COMPLIANT,
                    details="No specific regulatory violations detected",
                ),
            )

        return flags

    def _get_applicable_regulations(self, decision_type: DecisionType) -> list[str]:
        """Get regulations applicable to decision type"""
        applicable = []
        for reg_id, reg_info in self.regulation_db.items():
            if decision_type in reg_info["applicable_types"]:
                applicable.append(reg_id)
        return applicable

    def _check_regulation(
        self, regulation: str, decision_type: DecisionType, evidence: list[Evidence],
    ) -> ComplianceFlag | None:
        """Check specific regulation compliance

        In production, this would integrate with:
        - Regulatory compliance databases
        - Real-time rule engines
        - External compliance APIs
        """
        # Check if regulation exists in database
        if regulation not in self.regulation_db:
            return ComplianceFlag(
                regulation=regulation,
                status=ComplianceStatus.UNCLEAR,
                details=f"Regulation {regulation} not found in compliance database",
            )

        reg_info = self.regulation_db[regulation]

        # Check if regulation applies to this decision type
        if decision_type not in reg_info["applicable_types"]:
            return ComplianceFlag(
                regulation=regulation,
                status=ComplianceStatus.COMPLIANT,
                details=f"{regulation} not applicable to {decision_type.value}",
            )

        # Perform regulation-specific checks
        if regulation == "SEC Rule 15c3-1":
            return self._check_sec_15c3_1(evidence)
        if regulation == "MiFID II":
            return self._check_mifid_ii(evidence)
        if regulation == "Dodd-Frank":
            return self._check_dodd_frank(evidence)
        if regulation == "FINRA Rule 4210":
            return self._check_finra_4210(evidence)
        if regulation == "Regulation T":
            return self._check_regulation_t(evidence)
        if regulation == "Basel III":
            return self._check_basel_iii(evidence)
        # Default: assume compliant if no specific check
        return ComplianceFlag(
            regulation=regulation,
            status=ComplianceStatus.COMPLIANT,
            details=f"{reg_info['name']} check passed (default)",
        )

    # ========================================================================
    # Regulation-Specific Checks
    # ========================================================================

    def _check_sec_15c3_1(self, evidence: list[Evidence]) -> ComplianceFlag:
        """Check SEC Rule 15c3-1 (Net Capital Rule)
        Ensures broker-dealers maintain minimum net capital
        """
        # In production: query firm's net capital from accounting system
        # For MVP: simplified check based on evidence

        for item in evidence:
            if "net_capital" in item.data:
                net_capital = item.data["net_capital"]
                required_capital = item.data.get("required_capital", 250000)

                if net_capital < required_capital:
                    return ComplianceFlag(
                        regulation="SEC Rule 15c3-1",
                        status=ComplianceStatus.VIOLATION,
                        details=f"Net capital ${net_capital:,.0f} below required ${required_capital:,.0f}",
                    )

        return ComplianceFlag(
            regulation="SEC Rule 15c3-1",
            status=ComplianceStatus.COMPLIANT,
            details="Net capital requirements satisfied",
        )

    def _check_mifid_ii(self, evidence: list[Evidence]) -> ComplianceFlag:
        """Check MiFID II compliance
        EU trading transparency and best execution requirements
        """
        # Check for best execution evidence
        has_best_execution = any("best_execution" in item.data for item in evidence)

        if not has_best_execution:
            return ComplianceFlag(
                regulation="MiFID II",
                status=ComplianceStatus.WARNING,
                details="No best execution analysis provided (required for EU trades)",
            )

        return ComplianceFlag(
            regulation="MiFID II",
            status=ComplianceStatus.COMPLIANT,
            details="MiFID II transparency and execution requirements met",
        )

    def _check_dodd_frank(self, evidence: list[Evidence]) -> ComplianceFlag:
        """Check Dodd-Frank compliance
        Focus on systemic risk and swap dealer requirements
        """
        # Check if counterparty is properly documented
        for item in evidence:
            if "counterparty" in item.data:
                counterparty = item.data["counterparty"]
                if not counterparty.get("kyc_complete"):
                    return ComplianceFlag(
                        regulation="Dodd-Frank",
                        status=ComplianceStatus.VIOLATION,
                        details="KYC not complete for counterparty (Dodd-Frank Title VII required)",
                    )

        return ComplianceFlag(
            regulation="Dodd-Frank",
            status=ComplianceStatus.COMPLIANT,
            details="Dodd-Frank counterparty and risk requirements met",
        )

    def _check_finra_4210(self, evidence: list[Evidence]) -> ComplianceFlag:
        """Check FINRA Rule 4210 (Margin Requirements)
        """
        for item in evidence:
            if "margin" in item.data:
                margin_posted = item.data["margin"].get("posted", 0)
                margin_required = item.data["margin"].get("required", 0)

                if margin_posted < margin_required:
                    return ComplianceFlag(
                        regulation="FINRA Rule 4210",
                        status=ComplianceStatus.VIOLATION,
                        details=f"Margin shortfall: ${margin_required - margin_posted:,.0f}",
                    )

        return ComplianceFlag(
            regulation="FINRA Rule 4210",
            status=ComplianceStatus.COMPLIANT,
            details="Margin requirements satisfied",
        )

    def _check_regulation_t(self, evidence: list[Evidence]) -> ComplianceFlag:
        """Check Federal Reserve Regulation T
        Credit extension by brokers
        """
        # Simplified: check if leverage within limits
        for item in evidence:
            if "leverage" in item.data:
                leverage = item.data["leverage"]
                max_leverage = 2.0  # Reg T allows 50% margin (2:1 leverage)

                if leverage > max_leverage:
                    return ComplianceFlag(
                        regulation="Regulation T",
                        status=ComplianceStatus.VIOLATION,
                        details=f"Leverage {leverage:.1f}x exceeds Reg T limit of {max_leverage}x",
                    )

        return ComplianceFlag(
            regulation="Regulation T",
            status=ComplianceStatus.COMPLIANT,
            details="Credit extension within Regulation T limits",
        )

    def _check_basel_iii(self, evidence: list[Evidence]) -> ComplianceFlag:
        """Check Basel III capital and liquidity requirements
        """
        for item in evidence:
            if "capital_ratio" in item.data:
                tier1_ratio = item.data["capital_ratio"].get("tier1", 0)
                min_tier1 = 6.0  # Basel III minimum

                if tier1_ratio < min_tier1:
                    return ComplianceFlag(
                        regulation="Basel III",
                        status=ComplianceStatus.VIOLATION,
                        details=f"Tier 1 capital ratio {tier1_ratio:.1f}% below {min_tier1}% minimum",
                    )

        return ComplianceFlag(
            regulation="Basel III",
            status=ComplianceStatus.COMPLIANT,
            details="Basel III capital adequacy requirements met",
        )
