# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""ROI Calculator
==============

Comprehensive return on investment calculations for:
- Cell tower GPU deployments
- Starlink integration
- Tesla vehicle mesh
- Defense contracts
- Aviation partnerships
"""

from dataclasses import dataclass


@dataclass
class DeploymentConfig:
    """Deployment configuration parameters"""

    num_cell_towers: int
    num_vehicles: int
    num_satellites: int
    deployment_months: int


@dataclass
class CostStructure:
    """Cost breakdown"""

    capex_per_tower_usd: float = 50_000
    tower_monthly_opex_usd: float = 12_000
    vehicle_integration_cost_usd: float = 500
    satellite_uplink_cost_usd: float = 25_000


@dataclass
class RevenueStructure:
    """Revenue breakdown"""

    tower_monthly_revenue_usd: float = 30_000
    vehicle_monthly_revenue_usd: float = 10.0
    defense_contract_annual_usd: float = 0
    aviation_contract_annual_usd: float = 0


class ROICalculator:
    """Comprehensive ROI calculator for ShadowTag-v4 infrastructure deployments

    Handles multiple revenue streams and deployment scenarios.
    """

    def __init__(
        self,
        config: DeploymentConfig,
        costs: CostStructure | None = None,
        revenue: RevenueStructure | None = None,
    ):
        self.config = config
        self.costs = costs or CostStructure()
        self.revenue = revenue or RevenueStructure()

    def calculate_capex(self) -> dict[str, float]:
        """Calculate capital expenditures"""
        tower_capex = self.config.num_cell_towers * self.costs.capex_per_tower_usd
        vehicle_capex = self.config.num_vehicles * self.costs.vehicle_integration_cost_usd
        satellite_capex = self.config.num_satellites * self.costs.satellite_uplink_cost_usd

        total_capex = tower_capex + vehicle_capex + satellite_capex

        return {
            "tower_capex_usd": tower_capex,
            "vehicle_capex_usd": vehicle_capex,
            "satellite_capex_usd": satellite_capex,
            "total_capex_usd": total_capex,
        }

    def calculate_opex(self) -> dict[str, float]:
        """Calculate operational expenditures"""
        monthly_tower_opex = self.config.num_cell_towers * self.costs.tower_monthly_opex_usd
        monthly_vehicle_opex = self.config.num_vehicles * 2.0  # $2/vehicle/month maintenance

        total_monthly_opex = monthly_tower_opex + monthly_vehicle_opex
        total_cumulative_opex = total_monthly_opex * self.config.deployment_months

        return {
            "monthly_tower_opex_usd": monthly_tower_opex,
            "monthly_vehicle_opex_usd": monthly_vehicle_opex,
            "total_monthly_opex_usd": total_monthly_opex,
            "cumulative_opex_usd": total_cumulative_opex,
        }

    def calculate_revenue(self) -> dict[str, float]:
        """Calculate revenue projections"""
        monthly_tower_revenue = self.config.num_cell_towers * self.revenue.tower_monthly_revenue_usd
        monthly_vehicle_revenue = (
            self.config.num_vehicles * self.revenue.vehicle_monthly_revenue_usd
        )

        total_monthly_revenue = monthly_tower_revenue + monthly_vehicle_revenue

        # Add annual contract revenue (pro-rated monthly)
        monthly_defense_revenue = self.revenue.defense_contract_annual_usd / 12
        monthly_aviation_revenue = self.revenue.aviation_contract_annual_usd / 12

        total_monthly_revenue += monthly_defense_revenue + monthly_aviation_revenue

        cumulative_revenue = total_monthly_revenue * self.config.deployment_months

        return {
            "monthly_tower_revenue_usd": monthly_tower_revenue,
            "monthly_vehicle_revenue_usd": monthly_vehicle_revenue,
            "monthly_defense_revenue_usd": monthly_defense_revenue,
            "monthly_aviation_revenue_usd": monthly_aviation_revenue,
            "total_monthly_revenue_usd": total_monthly_revenue,
            "cumulative_revenue_usd": cumulative_revenue,
        }

    def calculate_roi(self) -> dict:
        """Calculate comprehensive ROI metrics"""
        capex = self.calculate_capex()
        opex = self.calculate_opex()
        revenue = self.calculate_revenue()

        total_investment = capex["total_capex_usd"] + opex["cumulative_opex_usd"]
        net_profit = revenue["cumulative_revenue_usd"] - total_investment
        roi_multiple = (
            revenue["cumulative_revenue_usd"] / total_investment if total_investment > 0 else 0
        )

        # Monthly metrics
        monthly_net = revenue["total_monthly_revenue_usd"] - opex["total_monthly_opex_usd"]
        gross_margin = (
            (monthly_net / revenue["total_monthly_revenue_usd"] * 100)
            if revenue["total_monthly_revenue_usd"] > 0
            else 0
        )

        # Payback period
        payback_months = capex["total_capex_usd"] / monthly_net if monthly_net > 0 else float("inf")

        # IRR approximation (simple annual equivalent)
        years = self.config.deployment_months / 12
        irr_annual = (
            ((revenue["cumulative_revenue_usd"] / total_investment) ** (1 / years) - 1) * 100
            if years > 0 and total_investment > 0
            else 0
        )

        return {
            "investment": {**capex, **opex, "total_investment_usd": total_investment},
            "revenue": revenue,
            "returns": {
                "net_profit_usd": net_profit,
                "roi_multiple": roi_multiple,
                "roi_percent": (roi_multiple - 1) * 100 if roi_multiple > 0 else 0,
                "payback_period_months": payback_months,
                "gross_margin_percent": gross_margin,
                "irr_annual_percent": irr_annual,
            },
            "monthly_metrics": {
                "revenue_usd": revenue["total_monthly_revenue_usd"],
                "opex_usd": opex["total_monthly_opex_usd"],
                "net_income_usd": monthly_net,
                "margin_percent": gross_margin,
            },
        }

    def calculate_pilot_economics(self) -> dict:
        """Calculate economics for pilot deployment

        Pilot: 10 towers, 100 vehicles, 3 months
        """
        pilot_config = DeploymentConfig(
            num_cell_towers=10,
            num_vehicles=100,
            num_satellites=3,
            deployment_months=3,
        )

        pilot_calc = ROICalculator(pilot_config, self.costs, self.revenue)
        return pilot_calc.calculate_roi()

    def calculate_regional_economics(self) -> dict:
        """Calculate economics for regional deployment

        Regional: 100 towers, 10k vehicles, 9 months
        """
        regional_config = DeploymentConfig(
            num_cell_towers=100,
            num_vehicles=10_000,
            num_satellites=5,
            deployment_months=9,
        )

        regional_calc = ROICalculator(regional_config, self.costs, self.revenue)
        return regional_calc.calculate_roi()

    def calculate_national_economics(self) -> dict:
        """Calculate economics for national deployment

        National: 20,000 towers, 1M vehicles, 36 months
        """
        national_config = DeploymentConfig(
            num_cell_towers=20_000,
            num_vehicles=1_000_000,
            num_satellites=20,
            deployment_months=36,
        )

        # Add defense and aviation contracts for national scale
        national_revenue = RevenueStructure(
            tower_monthly_revenue_usd=self.revenue.tower_monthly_revenue_usd,
            vehicle_monthly_revenue_usd=self.revenue.vehicle_monthly_revenue_usd,
            defense_contract_annual_usd=1_200_000_000,  # $1.2B annual
            aviation_contract_annual_usd=120_000_000,  # $120M annual
        )

        national_calc = ROICalculator(national_config, self.costs, national_revenue)
        return national_calc.calculate_roi()

    def calculate_global_economics(self) -> dict:
        """Calculate economics for global deployment

        Global: 100k towers, 10M vehicles, 60 months
        """
        global_config = DeploymentConfig(
            num_cell_towers=100_000,
            num_vehicles=10_000_000,
            num_satellites=100,
            deployment_months=60,
        )

        global_revenue = RevenueStructure(
            tower_monthly_revenue_usd=self.revenue.tower_monthly_revenue_usd,
            vehicle_monthly_revenue_usd=self.revenue.vehicle_monthly_revenue_usd,
            defense_contract_annual_usd=2_000_000_000,
            aviation_contract_annual_usd=200_000_000,
        )

        global_calc = ROICalculator(global_config, self.costs, global_revenue)
        return global_calc.calculate_roi()

    def project_valuation_curve(self) -> list[dict]:
        """Project valuation growth over deployment phases"""
        phases = [
            {
                "phase": "Pilot",
                "months": 3,
                "towers": 10,
                "vehicles": 100,
                "valuation_usd": 54_000_000,
            },
            {
                "phase": "Regional",
                "months": 9,
                "towers": 100,
                "vehicles": 10_000,
                "valuation_usd": 1_800_000_000,
            },
            {
                "phase": "National",
                "months": 36,
                "towers": 20_000,
                "vehicles": 1_000_000,
                "valuation_usd": 5_800_000_000,
            },
            {
                "phase": "Global",
                "months": 60,
                "towers": 100_000,
                "vehicles": 10_000_000,
                "valuation_usd": 21_000_000_000,
            },
        ]

        results = []
        for phase in phases:
            config = DeploymentConfig(
                num_cell_towers=phase["towers"],
                num_vehicles=phase["vehicles"],
                num_satellites=phase["towers"] // 20,
                deployment_months=phase["months"],
            )

            calc = ROICalculator(config, self.costs, self.revenue)
            roi = calc.calculate_roi()

            results.append(
                {
                    "phase": phase["phase"],
                    "months": phase["months"],
                    "deployment": {"towers": phase["towers"], "vehicles": phase["vehicles"]},
                    "economics": roi,
                    "valuation_usd": phase["valuation_usd"],
                },
            )

        return results

    def export_summary(self) -> dict:
        """Export comprehensive ROI summary"""
        return {
            "deployment_config": {
                "cell_towers": self.config.num_cell_towers,
                "vehicles": self.config.num_vehicles,
                "satellites": self.config.num_satellites,
                "deployment_months": self.config.deployment_months,
            },
            "base_case": self.calculate_roi(),
            "scenarios": {
                "pilot": self.calculate_pilot_economics(),
                "regional": self.calculate_regional_economics(),
                "national": self.calculate_national_economics(),
                "global": self.calculate_global_economics(),
            },
            "valuation_curve": self.project_valuation_curve(),
        }
