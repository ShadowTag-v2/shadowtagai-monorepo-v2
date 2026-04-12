"""
Enterprise Valuation Model
==========================

Comprehensive valuation engine for ShadowTag-v4 aerospace and infrastructure divisions.
Supports multiple valuation methods, scenario modeling, and integrated uplift calculations.
"""

import random
from dataclasses import dataclass, field
from enum import Enum


class ValuationMethod(Enum):
    """Valuation calculation methods"""

    REVENUE_MULTIPLE = "revenue_multiple"
    EBITDA_MULTIPLE = "ebitda_multiple"
    DCF = "dcf"  # Discounted Cash Flow
    COMPARABLE_COMPANIES = "comparable_companies"
    VENTURE_CAPITAL = "venture_capital"


class MarketScenario(Enum):
    """Market scenario assumptions"""

    BEAR = "bear"
    BASE = "base"
    BULL = "bull"


@dataclass
class Division:
    """Single business division"""

    name: str
    arr_usd: float  # Annual Recurring Revenue
    ebitda_margin: float  # 0.0 - 1.0
    revenue_multiple: float = 10.0
    ebitda_multiple: float = 20.0
    contribution_percent: float = 0.0  # % of total enterprise value

    @property
    def ebitda_usd(self) -> float:
        """Calculate EBITDA"""
        return self.arr_usd * self.ebitda_margin

    @property
    def valuation_revenue_method(self) -> float:
        """Valuation using revenue multiple"""
        return self.arr_usd * self.revenue_multiple

    @property
    def valuation_ebitda_method(self) -> float:
        """Valuation using EBITDA multiple"""
        return self.ebitda_usd * self.ebitda_multiple

    @property
    def valuation_blended(self) -> float:
        """Blended valuation (70% EBITDA, 30% revenue)"""
        return (self.valuation_ebitda_method * 0.7) + (self.valuation_revenue_method * 0.3)


@dataclass
class MonteCarloResult:
    """Monte Carlo simulation result"""

    percentile_10: float
    percentile_25: float
    percentile_50: float  # Median
    percentile_75: float
    percentile_90: float
    mean: float
    std_dev: float
    probability_above_threshold: dict[float, float] = field(default_factory=dict)


class EnterpriseValuationModel:
    """
    Comprehensive enterprise valuation for ShadowTag-v4

    Integrates:
    - Infrastructure Mesh (Starlink + CoreWeave + Telecom + Vehicles + Buoys)
    - ShadowTag-v4 Digital (Search / Mall / Media / VR Social)
    - Defense & PNT (Dual-use contracts / AI verification)
    - Family Foundation + Physical Assets
    """

    def __init__(self, target_year: int = 2030):
        self.target_year = target_year
        self.divisions = self._initialize_divisions()
        self.scenarios = self._initialize_scenarios()

    def _initialize_divisions(self) -> dict[str, Division]:
        """Initialize business divisions with Year 5 (2030) projections"""
        return {
            "infrastructure_mesh": Division(
                name="Infrastructure Mesh",
                arr_usd=10_000_000_000,  # $10B ARR
                ebitda_margin=0.84,
                ebitda_multiple=20.0,
                contribution_percent=54.2,  # $168B / $310B
            ),
            "ShadowTag-v2_digital": Division(
                name="ShadowTag-v4 Digital",
                arr_usd=6_000_000_000,  # $6B ARR
                ebitda_margin=0.80,
                ebitda_multiple=20.0,
                contribution_percent=31.0,  # $96B / $310B
            ),
            "defense_pnt": Division(
                name="Defense & PNT",
                arr_usd=2_000_000_000,  # $2B ARR
                ebitda_margin=0.80,
                ebitda_multiple=20.0,
                contribution_percent=10.3,  # $32B / $310B
            ),
            "foundation_assets": Division(
                name="Family Foundation + Physical Assets",
                arr_usd=0,  # Asset-based, not revenue
                ebitda_margin=0.0,
                ebitda_multiple=0.0,
                contribution_percent=3.2,  # $10B / $310B
            ),
        }

    def _initialize_scenarios(self) -> dict[MarketScenario, dict]:
        """Initialize market scenario assumptions"""
        return {
            MarketScenario.BEAR: {
                "arr_multiplier": 0.7,
                "ebitda_multiple": 12.0,
                "probability": 0.15,
            },
            MarketScenario.BASE: {
                "arr_multiplier": 1.0,
                "ebitda_multiple": 20.0,
                "probability": 0.70,
            },
            MarketScenario.BULL: {
                "arr_multiplier": 1.3,
                "ebitda_multiple": 25.0,
                "probability": 0.15,
            },
        }

    def calculate_division_value(
        self, division_key: str, scenario: MarketScenario = MarketScenario.BASE
    ) -> float:
        """Calculate single division valuation"""
        division = self.divisions[division_key]

        if division_key == "foundation_assets":
            return 10_000_000_000  # Fixed asset value

        # Apply scenario adjustments
        scenario_params = self.scenarios[scenario]
        adjusted_arr = division.arr_usd * scenario_params["arr_multiplier"]
        adjusted_ebitda_multiple = scenario_params["ebitda_multiple"]

        ebitda = adjusted_arr * division.ebitda_margin
        return ebitda * adjusted_ebitda_multiple

    def calculate_total_enterprise_value(
        self, scenario: MarketScenario = MarketScenario.BASE
    ) -> float:
        """Calculate total enterprise value across all divisions"""
        total = 0.0
        for division_key in self.divisions:
            total += self.calculate_division_value(division_key, scenario)
        return total

    def calculate_aerospace_contribution(
        self, scenario: MarketScenario = MarketScenario.BASE
    ) -> float:
        """Calculate aerospace division contribution to enterprise value"""
        # Aerospace is part of defense_pnt + infrastructure_mesh
        defense_value = self.calculate_division_value("defense_pnt", scenario)
        # Aerospace contributes ~$90-100B uplift to integrated value
        aerospace_uplift = 95_000_000_000
        return aerospace_uplift

    def run_monte_carlo(
        self, iterations: int = 10_000, target_valuation_usd: float = 12_000_000_000
    ) -> MonteCarloResult:
        """
        Run Monte Carlo simulation for valuation range

        Args:
            iterations: Number of simulation runs
            target_valuation_usd: Threshold for probability calculation
        """
        results = []

        for _ in range(iterations):
            # Random scenario selection weighted by probability
            scenario_choice = random.choices(
                list(MarketScenario),
                weights=[self.scenarios[s]["probability"] for s in MarketScenario],
            )[0]

            # Add randomness to ARR (±15%)
            arr_variance = random.uniform(0.85, 1.15)

            # Calculate valuation
            total_value = 0.0
            for division_key in self.divisions:
                base_value = self.calculate_division_value(division_key, scenario_choice)
                total_value += base_value * arr_variance

            results.append(total_value)

        # Sort for percentile calculations
        results_sorted = sorted(results)
        n = len(results_sorted)

        # Calculate percentiles
        p10 = results_sorted[int(n * 0.10)]
        p25 = results_sorted[int(n * 0.25)]
        p50 = results_sorted[int(n * 0.50)]
        p75 = results_sorted[int(n * 0.75)]
        p90 = results_sorted[int(n * 0.90)]

        # Calculate mean and std dev
        mean = sum(results) / n
        variance = sum((x - mean) ** 2 for x in results) / n
        std_dev = variance**0.5

        # Calculate probability above thresholds
        prob_above = {
            target_valuation_usd: sum(1 for r in results if r >= target_valuation_usd) / n,
            20_000_000_000: sum(1 for r in results if r >= 20_000_000_000) / n,
            50_000_000_000: sum(1 for r in results if r >= 50_000_000_000) / n,
            100_000_000_000: sum(1 for r in results if r >= 100_000_000_000) / n,
        }

        return MonteCarloResult(
            percentile_10=p10,
            percentile_25=p25,
            percentile_50=p50,
            percentile_75=p75,
            percentile_90=p90,
            mean=mean,
            std_dev=std_dev,
            probability_above_threshold=prob_above,
        )

    def calculate_founder_value(
        self,
        equity_percent: float = 60.0,
        scenario: MarketScenario = MarketScenario.BASE,
    ) -> dict:
        """
        Calculate founder equity value and cash flow

        Args:
            equity_percent: Founder equity percentage (default 60%)
            scenario: Market scenario
        """
        total_ev = self.calculate_total_enterprise_value(scenario)
        total_arr = sum(div.arr_usd for div in self.divisions.values() if div.arr_usd > 0)
        total_ebitda = sum(div.ebitda_usd for div in self.divisions.values())

        founder_equity_value = total_ev * (equity_percent / 100)
        annual_free_cash_flow = total_ebitda * 0.85  # 85% FCF conversion
        founder_annual_cash = annual_free_cash_flow * (equity_percent / 100)

        return {
            "total_enterprise_value_usd": total_ev,
            "founder_equity_percent": equity_percent,
            "founder_equity_value_usd": founder_equity_value,
            "total_arr_usd": total_arr,
            "total_ebitda_usd": total_ebitda,
            "annual_free_cash_flow_usd": annual_free_cash_flow,
            "founder_annual_cash_usd": founder_annual_cash,
            "scenario": scenario.value,
        }

    def project_timeline(self) -> list[dict]:
        """Project valuation timeline (2025-2031)"""
        timeline = [
            {"year": 2025, "phase": "Seed", "valuation_usd": 50_000_000},
            {"year": 2026, "phase": "Series A", "valuation_usd": 300_000_000},
            {"year": 2027, "phase": "Series B", "valuation_usd": 4_500_000_000},
            {"year": 2028, "phase": "Series C", "valuation_usd": 8_500_000_000},
            {"year": 2029, "phase": "Series D", "valuation_usd": 12_500_000_000},
            {"year": 2030, "phase": "Pre-IPO", "valuation_usd": 18_000_000_000},
            {
                "year": 2031,
                "phase": "IPO + Integration",
                "valuation_usd": 310_000_000_000,
            },
        ]
        return timeline

    def export_valuation_summary(self) -> dict:
        """Export comprehensive valuation summary"""
        monte_carlo = self.run_monte_carlo()

        return {
            "target_year": self.target_year,
            "divisions": {
                key: {
                    "name": div.name,
                    "arr_usd": div.arr_usd,
                    "ebitda_usd": div.ebitda_usd,
                    "ebitda_margin_percent": div.ebitda_margin * 100,
                    "valuation_usd": self.calculate_division_value(key),
                    "contribution_percent": div.contribution_percent,
                }
                for key, div in self.divisions.items()
            },
            "scenarios": {
                scenario.value: {
                    "total_enterprise_value_usd": self.calculate_total_enterprise_value(scenario),
                    "probability": self.scenarios[scenario]["probability"],
                }
                for scenario in MarketScenario
            },
            "monte_carlo_simulation": {
                "iterations": 10_000,
                "percentile_10_usd": monte_carlo.percentile_10,
                "percentile_50_median_usd": monte_carlo.percentile_50,
                "percentile_90_usd": monte_carlo.percentile_90,
                "mean_usd": monte_carlo.mean,
                "std_dev_usd": monte_carlo.std_dev,
                "probability_ge_12b": monte_carlo.probability_above_threshold.get(
                    12_000_000_000, 0
                ),
                "probability_ge_20b": monte_carlo.probability_above_threshold.get(
                    20_000_000_000, 0
                ),
            },
            "founder_value": self.calculate_founder_value(),
            "aerospace_contribution_usd": self.calculate_aerospace_contribution(),
            "timeline": self.project_timeline(),
        }
