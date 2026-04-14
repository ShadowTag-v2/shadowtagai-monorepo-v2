"""Policy Rule Engine
Internal policy and risk limit enforcement
"""

from ..models.base import Evidence, RiskLimits


class PolicyEngine:
    """Internal policy rule enforcement engine
    Validates decisions against firm-specific policies and risk limits
    """

    def __init__(self):
        """Initialize policy engine"""
        self.policy_db = self._initialize_policies()

    def _initialize_policies(self) -> dict:
        """Initialize policy rule database
        In production, this would load from policy management system
        """
        return {
            "RISK-001": {
                "name": "Position Size Limit",
                "description": "Max position size as % of portfolio",
                "threshold": 10.0,  # %
            },
            "RISK-002": {
                "name": "Concentration Limit",
                "description": "Max exposure to single counterparty",
                "threshold": 15.0,  # %
            },
            "RISK-003": {
                "name": "VaR Limit",
                "description": "Daily Value at Risk limit",
                "threshold": 5000000.0,  # USD
            },
            "RISK-004": {
                "name": "Leverage Limit",
                "description": "Maximum portfolio leverage",
                "threshold": 3.0,  # ratio
            },
            "TRADE-001": {
                "name": "Pre-Trade Approval",
                "description": "Trades above threshold require senior approval",
                "threshold": 10000000.0,  # USD
            },
            "CREDIT-001": {
                "name": "Counterparty Credit Rating",
                "description": "Minimum credit rating for counterparties",
                "threshold": "BBB-",  # S&P rating
            },
        }

    def check_policies(
        self, policy_ids: list[str], evidence: list[Evidence], risk_limits: RiskLimits | None = None,
    ) -> list[str]:
        """Check policy compliance

        Args:
            policy_ids: List of policy IDs to check
            evidence: Supporting evidence
            risk_limits: Risk limit constraints

        Returns:
            List of policy violations (empty if compliant)

        """
        violations = []

        # If no specific policies provided, check all relevant ones
        if not policy_ids:
            policy_ids = list(self.policy_db.keys())

        for policy_id in policy_ids:
            if policy_id not in self.policy_db:
                # Unknown policy - skip
                continue

            violation = self._check_policy(policy_id, evidence, risk_limits)
            if violation:
                violations.append(violation)

        return violations

    def _check_policy(
        self, policy_id: str, evidence: list[Evidence], risk_limits: RiskLimits | None,
    ) -> str | None:
        """Check specific policy

        Returns:
            Violation message if policy violated, None if compliant

        """
        policy = self.policy_db[policy_id]

        if policy_id == "RISK-001":
            return self._check_position_size(evidence, policy)
        if policy_id == "RISK-002":
            return self._check_concentration(evidence, policy)
        if policy_id == "RISK-003":
            return self._check_var_limit(evidence, risk_limits, policy)
        if policy_id == "RISK-004":
            return self._check_leverage_limit(evidence, policy)
        if policy_id == "TRADE-001":
            return self._check_trade_approval(evidence, policy)
        if policy_id == "CREDIT-001":
            return self._check_credit_rating(evidence, policy)
        return None

    def _check_position_size(self, evidence: list[Evidence], policy: dict) -> str | None:
        """Check position size limit"""
        for item in evidence:
            if "position_size_pct" in item.data:
                size_pct = item.data["position_size_pct"]
                if size_pct > policy["threshold"]:
                    return f"{policy['name']}: {size_pct:.1f}% exceeds {policy['threshold']:.1f}% limit"
        return None

    def _check_concentration(self, evidence: list[Evidence], policy: dict) -> str | None:
        """Check concentration limit"""
        for item in evidence:
            if "concentration_pct" in item.data:
                concentration = item.data["concentration_pct"]
                if concentration > policy["threshold"]:
                    return f"{policy['name']}: {concentration:.1f}% exceeds {policy['threshold']:.1f}% limit"
        return None

    def _check_var_limit(
        self, evidence: list[Evidence], risk_limits: RiskLimits | None, policy: dict,
    ) -> str | None:
        """Check VaR limit"""
        # Check risk_limits first
        if risk_limits and risk_limits.var_limit:
            threshold = risk_limits.var_limit
        else:
            threshold = policy["threshold"]

        for item in evidence:
            if "var_95" in item.data:
                var_value = abs(item.data["var_95"])
                if var_value > threshold:
                    return f"{policy['name']}: ${var_value:,.0f} exceeds ${threshold:,.0f} limit"
        return None

    def _check_leverage_limit(self, evidence: list[Evidence], policy: dict) -> str | None:
        """Check leverage limit"""
        for item in evidence:
            if "leverage" in item.data:
                leverage = item.data["leverage"]
                if leverage > policy["threshold"]:
                    return f"{policy['name']}: {leverage:.1f}x exceeds {policy['threshold']:.1f}x limit"
        return None

    def _check_trade_approval(self, evidence: list[Evidence], policy: dict) -> str | None:
        """Check if large trade has required approval"""
        for item in evidence:
            if "trade_size_usd" in item.data:
                trade_size = item.data["trade_size_usd"]
                if trade_size > policy["threshold"]:
                    # Check if approval documented
                    if not item.data.get("senior_approval"):
                        return (
                            f"{policy['name']}: ${trade_size:,.0f} trade requires "
                            f"senior approval (threshold: ${policy['threshold']:,.0f})"
                        )
        return None

    def _check_credit_rating(self, evidence: list[Evidence], policy: dict) -> str | None:
        """Check counterparty credit rating"""
        rating_scale = [
            "AAA",
            "AA+",
            "AA",
            "AA-",
            "A+",
            "A",
            "A-",
            "BBB+",
            "BBB",
            "BBB-",
            "BB+",
            "BB",
            "BB-",
            "B+",
            "B",
            "B-",
            "CCC",
            "CC",
            "C",
            "D",
        ]

        min_rating = policy["threshold"]
        min_index = rating_scale.index(min_rating)

        for item in evidence:
            if "credit_rating" in item.data:
                rating = item.data["credit_rating"]
                if rating in rating_scale:
                    rating_index = rating_scale.index(rating)
                    if rating_index > min_index:  # Lower rating (higher index)
                        return (
                            f"{policy['name']}: Credit rating {rating} below minimum {min_rating}"
                        )
        return None
