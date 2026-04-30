"""ATP 5-19 Risk Assessment Engine
U.S. Army Techniques Publication 5-19 risk management framework adapted for finance
"""

from ..models.base import Probability, RiskLevel, Severity

# ============================================================================
# ATP 5-19 Risk Matrix
# ============================================================================

# Risk Level Matrix: [Probability][Severity] -> RiskLevel
# Rows: Probability (A-E), Columns: Severity (I-IV)
RISK_MATRIX: dict[tuple[Probability, Severity], RiskLevel] = {
    # Probability A (Frequent: ≥80%)
    (Probability.A, Severity.I): RiskLevel.EH,
    (Probability.A, Severity.II): RiskLevel.EH,
    (Probability.A, Severity.III): RiskLevel.H,
    (Probability.A, Severity.IV): RiskLevel.M,
    # Probability B (Likely: 50-79%)
    (Probability.B, Severity.I): RiskLevel.EH,
    (Probability.B, Severity.II): RiskLevel.H,
    (Probability.B, Severity.III): RiskLevel.M,
    (Probability.B, Severity.IV): RiskLevel.L,
    # Probability C (Occasional: 20-49%)
    (Probability.C, Severity.I): RiskLevel.H,
    (Probability.C, Severity.II): RiskLevel.M,
    (Probability.C, Severity.III): RiskLevel.M,
    (Probability.C, Severity.IV): RiskLevel.L,
    # Probability D (Seldom: 5-19%)
    (Probability.D, Severity.I): RiskLevel.M,
    (Probability.D, Severity.II): RiskLevel.M,
    (Probability.D, Severity.III): RiskLevel.L,
    (Probability.D, Severity.IV): RiskLevel.L,
    # Probability E (Unlikely: <5%)
    (Probability.E, Severity.I): RiskLevel.M,
    (Probability.E, Severity.II): RiskLevel.L,
    (Probability.E, Severity.III): RiskLevel.L,
    (Probability.E, Severity.IV): RiskLevel.L,
}


# ============================================================================
# Probability Assessment
# ============================================================================


def assess_probability_from_percentage(percentage: float) -> Probability:
    """Convert percentage probability to ATP 5-19 level

    Args:
        percentage: Probability as percentage (0-100)

    Returns:
        Probability level (A-E)

    Raises:
        ValueError: If percentage out of range

    """
    if not 0 <= percentage <= 100:
        raise ValueError(f"Probability percentage must be 0-100, got {percentage}")

    if percentage >= 80:
        return Probability.A  # Frequent
    if percentage >= 50:
        return Probability.B  # Likely
    if percentage >= 20:
        return Probability.C  # Occasional
    if percentage >= 5:
        return Probability.D  # Seldom
    return Probability.E  # Unlikely


def assess_probability_from_frequency(occurrences: int, total: int) -> Probability:
    """Assess probability from historical frequency

    Args:
        occurrences: Number of times event occurred
        total: Total observations

    Returns:
        Probability level (A-E)

    Raises:
        ValueError: If invalid inputs

    """
    if total <= 0:
        raise ValueError(f"Total must be positive, got {total}")
    if occurrences < 0:
        raise ValueError(f"Occurrences must be non-negative, got {occurrences}")

    percentage = (occurrences / total) * 100
    return assess_probability_from_percentage(percentage)


# ============================================================================
# Severity Assessment
# ============================================================================


def assess_severity_from_loss(loss_usd: float) -> Severity:
    """Convert potential loss to ATP 5-19 severity level

    Args:
        loss_usd: Potential loss in USD

    Returns:
        Severity level (I-IV)

    Severity Thresholds (Financial):
        I (Catastrophic): >$10M loss, regulatory sanctions, reputational collapse
        II (Critical): $1M-$10M loss, material breach
        III (Moderate): $100K-$1M loss, minor violations
        IV (Negligible): <$100K loss, no violations

    """
    loss_abs = abs(loss_usd)

    if loss_abs > 10_000_000:
        return Severity.I  # Catastrophic
    if loss_abs > 1_000_000:
        return Severity.II  # Critical
    if loss_abs > 100_000:
        return Severity.III  # Moderate
    return Severity.IV  # Negligible


def assess_severity_from_var(var_usd: float, portfolio_value: float) -> Severity:
    """Assess severity from Value at Risk relative to portfolio

    Args:
        var_usd: Value at Risk (95% confidence)
        portfolio_value: Total portfolio value

    Returns:
        Severity level (I-IV)

    """
    if portfolio_value <= 0:
        raise ValueError(f"Portfolio value must be positive, got {portfolio_value}")

    var_percentage = (abs(var_usd) / portfolio_value) * 100

    # Thresholds based on % of portfolio at risk
    if var_percentage > 20:
        return Severity.I  # Catastrophic: >20% portfolio at risk
    if var_percentage > 5:
        return Severity.II  # Critical: 5-20% at risk
    if var_percentage > 1:
        return Severity.III  # Moderate: 1-5% at risk
    return Severity.IV  # Negligible: <1% at risk


# ============================================================================
# Risk Level Calculation
# ============================================================================


def calculate_risk_level(probability: Probability, severity: Severity) -> RiskLevel:
    """Calculate risk level from probability and severity using ATP 5-19 matrix

    Args:
        probability: Probability level (A-E)
        severity: Severity level (I-IV)

    Returns:
        Risk level (EH/H/M/L)

    """
    return RISK_MATRIX[(probability, severity)]


def calculate_risk_from_loss(
    probability_pct: float,
    loss_usd: float,
) -> tuple[Probability, Severity, RiskLevel]:
    """Calculate full risk assessment from probability and loss

    Args:
        probability_pct: Probability as percentage (0-100)
        loss_usd: Potential loss in USD

    Returns:
        Tuple of (Probability, Severity, RiskLevel)

    """
    prob = assess_probability_from_percentage(probability_pct)
    sev = assess_severity_from_loss(loss_usd)
    risk = calculate_risk_level(prob, sev)
    return prob, sev, risk


def calculate_risk_from_var(
    probability_pct: float,
    var_usd: float,
    portfolio_value: float,
) -> tuple[Probability, Severity, RiskLevel]:
    """Calculate risk assessment from VaR metrics

    Args:
        probability_pct: Probability as percentage (0-100)
        var_usd: Value at Risk
        portfolio_value: Total portfolio value

    Returns:
        Tuple of (Probability, Severity, RiskLevel)

    """
    prob = assess_probability_from_percentage(probability_pct)
    sev = assess_severity_from_var(var_usd, portfolio_value)
    risk = calculate_risk_level(prob, sev)
    return prob, sev, risk


# ============================================================================
# Risk Mitigation
# ============================================================================


def assess_residual_risk(original_risk: RiskLevel, mitigation_effectiveness: float) -> RiskLevel:
    """Estimate residual risk after mitigation measures

    Args:
        original_risk: Risk level before mitigation
        mitigation_effectiveness: Effectiveness percentage (0-100)

    Returns:
        Residual risk level

    Logic:
        - <50% effective: No change
        - 50-75%: Reduce by 1 level
        - >75%: Reduce by 2 levels

    """
    if not 0 <= mitigation_effectiveness <= 100:
        raise ValueError(f"Mitigation effectiveness must be 0-100, got {mitigation_effectiveness}")

    # Risk level hierarchy: EH > H > M > L
    risk_order = [RiskLevel.EH, RiskLevel.H, RiskLevel.M, RiskLevel.L]
    current_index = risk_order.index(original_risk)

    if mitigation_effectiveness >= 75:
        # Highly effective: reduce by 2 levels
        reduction = 2
    elif mitigation_effectiveness >= 50:
        # Moderately effective: reduce by 1 level
        reduction = 1
    else:
        # Minimally effective: no change
        reduction = 0

    # Apply reduction (capped at L = lowest risk)
    new_index = min(current_index + reduction, len(risk_order) - 1)
    return risk_order[new_index]


# ============================================================================
# Decision Support
# ============================================================================


def recommend_action(risk_level: RiskLevel, confidence: float) -> str:
    """Recommend action based on risk level and confidence

    Args:
        risk_level: Assessed risk level
        confidence: Confidence in assessment (0-100)

    Returns:
        Action recommendation

    """
    # High confidence recommendations
    if confidence >= 80:
        if risk_level == RiskLevel.EH:
            return "DENY - Extremely high risk"
        if risk_level == RiskLevel.H:
            return "APPROVE_WITH_CONDITIONS - High risk requires mitigation"
        if risk_level == RiskLevel.M:
            return "APPROVE_WITH_CONDITIONS - Moderate risk, monitor closely"
        # L
        return "APPROVE - Low risk"

    # Medium confidence recommendations
    if confidence >= 60:
        if risk_level in (RiskLevel.EH, RiskLevel.H):
            return "ESCALATE - High risk with uncertain confidence"
        if risk_level == RiskLevel.M:
            return "APPROVE_WITH_CONDITIONS - Moderate risk, additional review"
        # L
        return "APPROVE - Low risk"

    # Low confidence recommendations
    if risk_level in (RiskLevel.EH, RiskLevel.H):
        return "DENY - Cannot approve high risk with low confidence"
    return "DEFER - Requires additional analysis"


def get_risk_description(risk_level: RiskLevel) -> str:
    """Get human-readable risk level description"""
    descriptions = {
        RiskLevel.EH: "Extremely High - Immediate action required, likely unacceptable",
        RiskLevel.H: "High - Priority attention, mitigation mandatory",
        RiskLevel.M: "Medium - Management attention needed, mitigation recommended",
        RiskLevel.L: "Low - Acceptable with routine monitoring",
    }
    return descriptions[risk_level]


# ============================================================================
# Validation
# ============================================================================


def validate_risk_assessment(
    probability: Probability,
    severity: Severity,
    risk_level: RiskLevel,
) -> bool:
    """Validate that risk level matches ATP 5-19 matrix

    Args:
        probability: Probability level
        severity: Severity level
        risk_level: Claimed risk level

    Returns:
        True if valid, False otherwise

    """
    expected = calculate_risk_level(probability, severity)
    return expected == risk_level
