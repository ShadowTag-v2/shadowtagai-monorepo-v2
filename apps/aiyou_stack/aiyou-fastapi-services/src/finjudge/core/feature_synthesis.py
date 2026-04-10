"""
Feature Synthesis Layer
Derives risk signals from upstream metrics
"""

from typing import Any

from ..models.judge import Flags, Metrics, Probability, Severity


class FeatureSynthesizer:
    """
    Synthesizes risk features from raw metrics
    All transformations are deterministic and versioned
    """

    def __init__(self, version: str = "v0.2.0"):
        """Initialize feature synthesizer"""
        self.version = version

    def synthesize(self, metrics: Metrics, flags: Flags) -> dict[str, Any]:
        """
        Synthesize all features from metrics

        Args:
            metrics: Upstream metrics
            flags: Upstream flags

        Returns:
            Feature dict with derived signals
        """
        features = {}

        # Capital at risk
        if metrics.exposure:
            features["capital_at_risk"] = self._capital_at_risk(
                metrics.exposure.notional, metrics.exposure.pct_aum
            )

        # VaR to budget ratio
        if metrics.tail_risk and metrics.tail_risk.var_95:
            # Assume default budget of 5% AUM if not specified
            default_var_limit = 5_000_000  # $5M default
            features["var_to_budget"] = self._var_to_budget(
                metrics.tail_risk.var_95, metrics.custom.get("var_limit", default_var_limit)
            )

        # Liquidity heat score
        if metrics.liquidity_metrics:
            features["liquidity_heat"] = self._liquidity_heat(
                metrics.liquidity_metrics.spread_bps,
                metrics.liquidity_metrics.depth_score,
                metrics.liquidity_metrics.days_to_liquidate,
            )

        # Volatility regime indicator
        if metrics.volatility:
            features["regime_indicator"] = self._regime_indicator(
                metrics.volatility.regime_tag,
                metrics.volatility.realized_vol,
                metrics.volatility.implied_vol,
            )

        # Credit risk composite
        if metrics.credit_metrics:
            features["credit_risk_composite"] = self._credit_risk_composite(
                metrics.credit_metrics.pd, metrics.credit_metrics.lgd, metrics.credit_metrics.ead
            )

        # Tail risk severity
        if metrics.pnl_distribution_summary:
            features["tail_severity"] = self._tail_severity(
                metrics.pnl_distribution_summary.skew, metrics.pnl_distribution_summary.kurtosis
            )

        # Flag severity
        features["flag_severity"] = self._flag_severity(flags)

        # Exposure concentration
        if metrics.exposure:
            features["exposure_concentration"] = metrics.exposure.pct_aum

        return features

    def _capital_at_risk(self, notional: float, pct_aum: float) -> float:
        """
        Calculate capital at risk score

        Args:
            notional: Notional exposure (USD)
            pct_aum: % of AUM

        Returns:
            Capital at risk score (0-100)
        """
        # Score based on % AUM concentration
        if pct_aum > 20:
            return 100.0  # Extreme concentration
        elif pct_aum > 10:
            return 75.0  # High concentration
        elif pct_aum > 5:
            return 50.0  # Moderate concentration
        elif pct_aum > 2:
            return 25.0  # Low concentration
        else:
            return 10.0  # Minimal concentration

    def _var_to_budget(self, var_usd: float, var_limit: float) -> float:
        """
        Calculate VaR to budget ratio

        Args:
            var_usd: Value at Risk (USD)
            var_limit: VaR limit/budget (USD)

        Returns:
            Ratio (>1.0 = exceeding budget)
        """
        if var_limit <= 0:
            return 0.0
        return abs(var_usd) / var_limit

    def _liquidity_heat(
        self, spread_bps: float | None, depth_score: float | None, days_to_liquidate: float | None
    ) -> float:
        """
        Calculate liquidity heat score

        Args:
            spread_bps: Bid-ask spread (basis points)
            depth_score: Market depth (0-100)
            days_to_liquidate: Days to liquidate position

        Returns:
            Liquidity heat score (0-100, higher = less liquid)
        """
        heat_components = []

        # Spread component
        if spread_bps is not None:
            if spread_bps > 100:
                heat_components.append(100.0)
            elif spread_bps > 50:
                heat_components.append(75.0)
            elif spread_bps > 20:
                heat_components.append(50.0)
            elif spread_bps > 10:
                heat_components.append(25.0)
            else:
                heat_components.append(10.0)

        # Depth component (inverted - low depth = high heat)
        if depth_score is not None:
            heat_components.append(100.0 - depth_score)

        # Days to liquidate component
        if days_to_liquidate is not None:
            if days_to_liquidate > 10:
                heat_components.append(100.0)
            elif days_to_liquidate > 5:
                heat_components.append(75.0)
            elif days_to_liquidate > 2:
                heat_components.append(50.0)
            elif days_to_liquidate > 1:
                heat_components.append(25.0)
            else:
                heat_components.append(10.0)

        if not heat_components:
            return 50.0  # Default: moderate heat

        return sum(heat_components) / len(heat_components)

    def _regime_indicator(
        self, regime_tag: str | None, realized_vol: float | None, implied_vol: float | None
    ) -> str:
        """
        Determine volatility regime

        Args:
            regime_tag: Regime tag from upstream
            realized_vol: Realized volatility
            implied_vol: Implied volatility

        Returns:
            Regime indicator (low_vol, normal, high_vol, stressed)
        """
        if regime_tag:
            return regime_tag

        # Infer from vol metrics
        if realized_vol is not None:
            if realized_vol > 0.50:
                return "stressed"
            elif realized_vol > 0.30:
                return "high_vol"
            elif realized_vol > 0.15:
                return "normal"
            else:
                return "low_vol"

        return "normal"  # Default

    def _credit_risk_composite(
        self, pd: float | None, lgd: float | None, ead: float | None
    ) -> float:
        """
        Calculate composite credit risk score

        Args:
            pd: Probability of default
            lgd: Loss given default
            ead: Exposure at default

        Returns:
            Credit risk score (0-100)
        """
        if pd is None:
            return 50.0  # Unknown credit risk

        # Expected loss = PD × LGD × EAD (normalized)

        # PD thresholds
        if pd > 0.10:  # >10% default probability
            return 100.0
        elif pd > 0.05:  # 5-10%
            return 75.0
        elif pd > 0.02:  # 2-5%
            return 50.0
        elif pd > 0.01:  # 1-2%
            return 25.0
        else:
            return 10.0

    def _tail_severity(self, skew: float, kurtosis: float) -> float:
        """
        Calculate tail severity from distribution moments

        Args:
            skew: Skewness (negative = left tail)
            kurtosis: Kurtosis (>3 = fat tails)

        Returns:
            Tail severity score (0-100)
        """
        severity = 0.0

        # Negative skew adds severity (left tail risk)
        if skew < -1.0:
            severity += 50.0
        elif skew < -0.5:
            severity += 30.0
        elif skew < 0:
            severity += 10.0

        # Excess kurtosis adds severity (fat tails)
        excess_kurt = kurtosis - 3.0
        if excess_kurt > 3.0:
            severity += 50.0
        elif excess_kurt > 1.0:
            severity += 30.0
        elif excess_kurt > 0:
            severity += 10.0

        return min(severity, 100.0)

    def _flag_severity(self, flags: Flags) -> float:
        """
        Calculate severity from flags

        Args:
            flags: Upstream flags

        Returns:
            Flag severity score (0-100)
        """
        severity = 0.0

        # Regulatory flags are most severe
        if flags.regulatory_flags:
            severity += 50.0 * len(flags.regulatory_flags)

        # Policy flags are moderately severe
        if flags.policy_flags:
            severity += 25.0 * len(flags.policy_flags)

        return min(severity, 100.0)

    def infer_probability(self, features: dict[str, Any]) -> tuple[Probability, float]:
        """
        Infer ATP 5-19 probability from features

        Args:
            features: Synthesized features

        Returns:
            Tuple of (Probability level, confidence score)
        """
        # Default: moderate probability
        probability_score = 30.0  # Default to C (20-49%)
        confidence = 60.0

        # Adjust based on features
        if "var_to_budget" in features:
            var_ratio = features["var_to_budget"]
            if var_ratio > 1.5:
                probability_score = 85.0  # A (Frequent)
                confidence = 90.0
            elif var_ratio > 1.0:
                probability_score = 65.0  # B (Likely)
                confidence = 85.0
            elif var_ratio > 0.5:
                probability_score = 35.0  # C (Occasional)
                confidence = 75.0
            elif var_ratio > 0.2:
                probability_score = 12.0  # D (Seldom)
                confidence = 70.0
            else:
                probability_score = 3.0  # E (Unlikely)
                confidence = 80.0

        # Regime adjustment
        if features.get("regime_indicator") == "stressed":
            probability_score *= 1.5
            probability_score = min(probability_score, 95.0)

        # Flag adjustment
        if features.get("flag_severity", 0) > 50:
            probability_score *= 1.3
            probability_score = min(probability_score, 95.0)

        # Map to ATP 5-19 levels
        if probability_score >= 80:
            return Probability.A, confidence
        elif probability_score >= 50:
            return Probability.B, confidence
        elif probability_score >= 20:
            return Probability.C, confidence
        elif probability_score >= 5:
            return Probability.D, confidence
        else:
            return Probability.E, confidence

    def infer_severity(self, features: dict[str, Any], metrics: Metrics) -> tuple[Severity, float]:
        """
        Infer ATP 5-19 severity from features

        Args:
            features: Synthesized features
            metrics: Original metrics

        Returns:
            Tuple of (Severity level, confidence score)
        """
        # Default: moderate severity
        max_loss_usd = 500_000.0
        confidence = 60.0

        # Extract loss estimates
        if metrics.tail_risk and metrics.tail_risk.var_95:
            max_loss_usd = abs(metrics.tail_risk.var_95)
            confidence = 85.0
        elif metrics.tail_risk and metrics.tail_risk.cvar_95:
            max_loss_usd = abs(metrics.tail_risk.cvar_95)
            confidence = 80.0
        elif metrics.exposure:
            # Estimate as 20% of notional if no VaR
            max_loss_usd = metrics.exposure.notional * 0.2
            confidence = 50.0

        # Adjust for leverage
        if metrics.exposure and metrics.exposure.leverage_ratio > 1.0:
            max_loss_usd *= metrics.exposure.leverage_ratio

        # Map to ATP 5-19 severity levels
        if max_loss_usd > 10_000_000:
            return Severity.I, confidence  # Catastrophic
        elif max_loss_usd > 1_000_000:
            return Severity.II, confidence  # Critical
        elif max_loss_usd > 100_000:
            return Severity.III, confidence  # Moderate
        else:
            return Severity.IV, confidence  # Negligible
