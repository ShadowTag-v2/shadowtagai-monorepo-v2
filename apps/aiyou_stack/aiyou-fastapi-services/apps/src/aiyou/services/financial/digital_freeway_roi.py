"""Digital Freeway ROI Calculator
==============================

Traffic congestion and accident cost savings ROI calculator for:
- Tesla (OEM/Vehicle Manufacturer)
- Waymo (Autonomous Fleet Operator)
- DOT (Government Transportation Department)

Data Sources:
- INRIX 2024 Global Traffic Scorecard (Congestion costs)
- NHTSA Economic & Societal Impact Report 2019 (Crash costs)
- Tesla Q1 2024 Autopilot Safety Data (Baseline crash rates)
"""

from dataclasses import dataclass
from enum import StrEnum


class CustomerType(StrEnum):
    """Customer type for ROI calculation presets"""

    TESLA = "tesla"
    WAYMO = "waymo"
    DOT = "dot"


@dataclass
class CongestionData:
    """INRIX 2024 Global Traffic Scorecard Data
    Source: https://inrix.com/press-releases/2024-global-traffic-scorecard-us/
    """

    # Hours lost to congestion per driver annually
    US_AVG_HOURS: float = 43.0
    LA_HOURS: float = 88.0
    NYC_CHICAGO_HOURS: float = 102.0

    # Cost per driver annually (USD)
    US_AVG_COST: float = 771.0
    LA_COST: float = 1575.0
    NYC_CHICAGO_COST: float = 1826.0

    # National total congestion cost (USD)
    NATIONAL_TOTAL_COST: float = 74_000_000_000.0  # $74B

    # Source citation
    SOURCE: str = "INRIX 2024 Global Traffic Scorecard"
    SOURCE_URL: str = "https://inrix.com/press-releases/2024-global-traffic-scorecard-us/"


@dataclass
class CrashData:
    """NHTSA Economic & Societal Impact Report 2019
    Source: https://rosap.ntl.bts.gov/view/dot/78698
    """

    # Total economic crash cost 2019 (USD)
    NATIONAL_ECONOMIC_COST: float = 340_000_000_000.0  # $340B

    # US vehicles registered in 2024
    US_VEHICLES: int = 286_000_000

    # Cost per vehicle per year (derived: $340B / 286M vehicles)
    COST_PER_VEHICLE: float = 1189.0  # ~$1,189/vehicle/year

    # Source citation
    SOURCE: str = "NHTSA Economic & Societal Impact of Motor Vehicle Crashes, 2019"
    SOURCE_URL: str = "https://rosap.ntl.bts.gov/view/dot/78698"


@dataclass
class TeslaAutopilotData:
    """Tesla Q1 2024 Autopilot Safety Data
    Source: https://insideevs.com/news/720730/tesla-autopilot-crash-data-2024q1/
    """

    # Miles per crash on Autopilot
    AUTOPILOT_MILES_PER_CRASH: float = 7_630_000.0  # 7.63M miles

    # Source citation
    SOURCE: str = "Tesla Q1 2024 Autopilot Safety Data"
    SOURCE_URL: str = "https://insideevs.com/news/720730/tesla-autopilot-crash-data-2024q1/"


@dataclass
class PricingStructure:
    """Digital Freeway pricing structure"""

    MONTHLY_FEE_PER_VEHICLE: float = 2.0  # $2/vehicle/month
    ANNUAL_FEE_PER_VEHICLE: float = 24.0  # $24/vehicle/year
    GROSS_MARGIN: float = 0.85  # 85% gross margin


@dataclass
class CustomerPresets:
    """Default reduction percentages by customer type"""

    # Tesla: OEM integration, moderate conservative estimates
    TESLA_CONGESTION_PCT: float = 0.20  # 20%
    TESLA_CRASH_PCT: float = 0.05  # 5%

    # Waymo: Autonomous fleet, higher coordination potential
    WAYMO_CONGESTION_PCT: float = 0.25  # 25%
    WAYMO_CRASH_PCT: float = 0.07  # 7%

    # DOT: Government conservative estimates
    DOT_CONGESTION_PCT: float = 0.15  # 15%
    DOT_CRASH_PCT: float = 0.03  # 3%


class DigitalFreewayROICalculator:
    """Comprehensive ROI calculator for Digital Freeway traffic coordination platform.

    Calculates savings from:
    1. Congestion reduction (15-30% of annual congestion cost)
    2. Crash/accident reduction (2-10% of annual crash cost)

    Compares against platform fee of $2/vehicle/month ($24/year)
    """

    def __init__(self):
        self.congestion = CongestionData()
        self.crash = CrashData()
        self.tesla_data = TeslaAutopilotData()
        self.pricing = PricingStructure()
        self.presets = CustomerPresets()

    def get_preset(self, customer_type: CustomerType) -> dict[str, float]:
        """Get default reduction percentages for customer type"""
        presets = {
            CustomerType.TESLA: {
                "congestion_reduction_pct": self.presets.TESLA_CONGESTION_PCT,
                "crash_reduction_pct": self.presets.TESLA_CRASH_PCT,
                "focus_metric": "driver_roi_multiple",
                "description": "OEM vehicle manufacturer integration",
            },
            CustomerType.WAYMO: {
                "congestion_reduction_pct": self.presets.WAYMO_CONGESTION_PCT,
                "crash_reduction_pct": self.presets.WAYMO_CRASH_PCT,
                "focus_metric": "fleet_economics",
                "description": "Autonomous fleet operator",
            },
            CustomerType.DOT: {
                "congestion_reduction_pct": self.presets.DOT_CONGESTION_PCT,
                "crash_reduction_pct": self.presets.DOT_CRASH_PCT,
                "focus_metric": "national_savings",
                "description": "Government transportation department",
            },
        }
        return presets[customer_type]

    def calculate_congestion_savings(
        self,
        congestion_reduction_pct: float,
        location: str = "us_avg",
    ) -> dict[str, float]:
        """Calculate congestion cost savings per driver per year.

        Args:
            congestion_reduction_pct: Reduction percentage (0.10 to 0.30)
            location: One of "us_avg", "la", "nyc_chicago"

        Returns:
            Dict with savings calculations

        """
        location_costs = {
            "us_avg": self.congestion.US_AVG_COST,
            "la": self.congestion.LA_COST,
            "nyc_chicago": self.congestion.NYC_CHICAGO_COST,
        }

        location_hours = {
            "us_avg": self.congestion.US_AVG_HOURS,
            "la": self.congestion.LA_HOURS,
            "nyc_chicago": self.congestion.NYC_CHICAGO_HOURS,
        }

        base_cost = location_costs.get(location, self.congestion.US_AVG_COST)
        base_hours = location_hours.get(location, self.congestion.US_AVG_HOURS)

        annual_savings = base_cost * congestion_reduction_pct
        hours_saved = base_hours * congestion_reduction_pct

        return {
            "location": location,
            "base_annual_cost_usd": base_cost,
            "base_hours_lost": base_hours,
            "reduction_pct": congestion_reduction_pct,
            "annual_savings_usd": round(annual_savings, 2),
            "hours_saved": round(hours_saved, 1),
        }

    def calculate_crash_savings(self, crash_reduction_pct: float) -> dict[str, float]:
        """Calculate crash/accident cost savings per vehicle per year.

        Args:
            crash_reduction_pct: Reduction percentage (0.02 to 0.10)

        Returns:
            Dict with savings calculations

        """
        annual_savings = self.crash.COST_PER_VEHICLE * crash_reduction_pct

        return {
            "base_cost_per_vehicle_usd": self.crash.COST_PER_VEHICLE,
            "reduction_pct": crash_reduction_pct,
            "annual_savings_usd": round(annual_savings, 2),
        }

    def calculate_per_vehicle_roi(
        self,
        congestion_reduction_pct: float,
        crash_reduction_pct: float,
        location: str = "us_avg",
    ) -> dict:
        """Calculate comprehensive per-vehicle ROI.

        Args:
            congestion_reduction_pct: 0.10 to 0.30 (10% to 30%)
            crash_reduction_pct: 0.02 to 0.10 (2% to 10%)
            location: Geographic location for congestion data

        Returns:
            Comprehensive ROI breakdown

        """
        congestion = self.calculate_congestion_savings(congestion_reduction_pct, location)
        crash = self.calculate_crash_savings(crash_reduction_pct)

        total_savings = congestion["annual_savings_usd"] + crash["annual_savings_usd"]
        annual_fee = self.pricing.ANNUAL_FEE_PER_VEHICLE
        roi_multiple = total_savings / annual_fee if annual_fee > 0 else 0
        net_savings = total_savings - annual_fee

        return {
            "congestion_savings": congestion,
            "crash_savings": crash,
            "totals": {
                "annual_savings_usd": round(total_savings, 2),
                "annual_fee_usd": annual_fee,
                "net_savings_usd": round(net_savings, 2),
                "roi_multiple": round(roi_multiple, 1),
                "roi_percent": round((roi_multiple - 1) * 100, 0),
            },
        }

    def calculate_fleet_roi(
        self,
        fleet_size: int,
        congestion_reduction_pct: float,
        crash_reduction_pct: float,
        location: str = "us_avg",
    ) -> dict:
        """Calculate ROI for an entire fleet.

        Args:
            fleet_size: Number of vehicles in fleet
            congestion_reduction_pct: 0.10 to 0.30
            crash_reduction_pct: 0.02 to 0.10
            location: Geographic location

        Returns:
            Fleet-level ROI metrics

        """
        per_vehicle = self.calculate_per_vehicle_roi(
            congestion_reduction_pct,
            crash_reduction_pct,
            location,
        )

        annual_revenue = self.pricing.ANNUAL_FEE_PER_VEHICLE * fleet_size
        gross_profit = annual_revenue * self.pricing.GROSS_MARGIN
        fleet_savings = per_vehicle["totals"]["annual_savings_usd"] * fleet_size
        value_unlocked_ratio = fleet_savings / annual_revenue if annual_revenue > 0 else 0

        return {
            "fleet_size": fleet_size,
            "per_vehicle": per_vehicle,
            "fleet_metrics": {
                "annual_revenue_usd": round(annual_revenue, 2),
                "gross_profit_usd": round(gross_profit, 2),
                "gross_margin_pct": self.pricing.GROSS_MARGIN * 100,
                "fleet_total_savings_usd": round(fleet_savings, 2),
                "value_unlocked_ratio": round(value_unlocked_ratio, 1),
            },
        }

    def calculate_national_impact(
        self,
        congestion_reduction_pct: float,
        crash_reduction_pct: float,
        adoption_pct: float = 1.0,
    ) -> dict:
        """Calculate national-level impact for DOT/government stakeholders.

        Args:
            congestion_reduction_pct: 0.10 to 0.30
            crash_reduction_pct: 0.02 to 0.10
            adoption_pct: Percentage of vehicles adopting (0.0 to 1.0)

        Returns:
            National impact metrics in billions USD

        """
        congestion_savings = (
            self.congestion.NATIONAL_TOTAL_COST * congestion_reduction_pct * adoption_pct
        )
        crash_savings = self.crash.NATIONAL_ECONOMIC_COST * crash_reduction_pct * adoption_pct
        total_savings = congestion_savings + crash_savings

        vehicles_participating = int(self.crash.US_VEHICLES * adoption_pct)
        total_revenue = vehicles_participating * self.pricing.ANNUAL_FEE_PER_VEHICLE

        return {
            "adoption_pct": adoption_pct * 100,
            "vehicles_participating": vehicles_participating,
            "congestion": {
                "base_national_cost_usd": self.congestion.NATIONAL_TOTAL_COST,
                "reduction_pct": congestion_reduction_pct * 100,
                "savings_usd": round(congestion_savings, 2),
                "savings_billions": round(congestion_savings / 1_000_000_000, 2),
            },
            "crash": {
                "base_national_cost_usd": self.crash.NATIONAL_ECONOMIC_COST,
                "reduction_pct": crash_reduction_pct * 100,
                "savings_usd": round(crash_savings, 2),
                "savings_billions": round(crash_savings / 1_000_000_000, 2),
            },
            "totals": {
                "total_savings_usd": round(total_savings, 2),
                "total_savings_billions": round(total_savings / 1_000_000_000, 2),
                "platform_revenue_usd": round(total_revenue, 2),
                "platform_revenue_billions": round(total_revenue / 1_000_000_000, 2),
                "value_created_ratio": round(total_savings / total_revenue, 1)
                if total_revenue > 0
                else 0,
            },
        }

    def calculate_scenario_comparison(
        self,
        fleet_size: int = 1_000_000,
        location: str = "us_avg",
    ) -> dict:
        """Calculate conservative, mid, and aggressive scenarios.

        Returns:
            Comparison of all three scenarios

        """
        scenarios = {
            "conservative": {
                "congestion_pct": 0.15,
                "crash_pct": 0.02,
                "description": "15% congestion + 2% crash reduction",
            },
            "mid": {
                "congestion_pct": 0.20,
                "crash_pct": 0.05,
                "description": "20% congestion + 5% crash reduction",
            },
            "aggressive": {
                "congestion_pct": 0.30,
                "crash_pct": 0.10,
                "description": "30% congestion + 10% crash reduction",
            },
        }

        results = {}
        for name, params in scenarios.items():
            roi = self.calculate_fleet_roi(
                fleet_size=fleet_size,
                congestion_reduction_pct=params["congestion_pct"],
                crash_reduction_pct=params["crash_pct"],
                location=location,
            )
            results[name] = {
                "description": params["description"],
                "congestion_reduction_pct": params["congestion_pct"] * 100,
                "crash_reduction_pct": params["crash_pct"] * 100,
                "per_vehicle_savings_usd": roi["per_vehicle"]["totals"]["annual_savings_usd"],
                "per_vehicle_roi_multiple": roi["per_vehicle"]["totals"]["roi_multiple"],
                "fleet_total_savings_usd": roi["fleet_metrics"]["fleet_total_savings_usd"],
                "platform_revenue_usd": roi["fleet_metrics"]["annual_revenue_usd"],
                "value_unlocked_ratio": roi["fleet_metrics"]["value_unlocked_ratio"],
            }

        return {"fleet_size": fleet_size, "location": location, "scenarios": results}

    def get_all_sources(self) -> list[dict[str, str]]:
        """Get all data sources with citations"""
        return [
            {
                "id": 1,
                "name": self.congestion.SOURCE,
                "url": self.congestion.SOURCE_URL,
                "data": "U.S. congestion costs: $74B total, $771/driver avg, $1,575 LA, $1,826 NYC/Chicago",
            },
            {
                "id": 2,
                "name": self.crash.SOURCE,
                "url": self.crash.SOURCE_URL,
                "data": "Motor vehicle crash economic cost: $340B (2019), ~$1,189/vehicle/year",
            },
            {
                "id": 3,
                "name": self.tesla_data.SOURCE,
                "url": self.tesla_data.SOURCE_URL,
                "data": "Tesla Autopilot: 1 crash per 7.63M miles (Q1 2024)",
            },
        ]

    def generate_one_pager(
        self,
        customer_type: CustomerType,
        fleet_size: int = 1_000_000,
        congestion_reduction_pct: float | None = None,
        crash_reduction_pct: float | None = None,
        location: str = "us_avg",
    ) -> dict:
        """Generate complete one-pager ROI data for a customer type.

        Args:
            customer_type: TESLA, WAYMO, or DOT
            fleet_size: Number of vehicles
            congestion_reduction_pct: Override default (or use preset)
            crash_reduction_pct: Override default (or use preset)
            location: Geographic location

        Returns:
            Complete one-pager data structure

        """
        preset = self.get_preset(customer_type)

        # Use provided values or fall back to presets
        cong_pct = (
            congestion_reduction_pct
            if congestion_reduction_pct is not None
            else preset["congestion_reduction_pct"]
        )
        crash_pct = (
            crash_reduction_pct
            if crash_reduction_pct is not None
            else preset["crash_reduction_pct"]
        )

        fleet_roi = self.calculate_fleet_roi(
            fleet_size=fleet_size,
            congestion_reduction_pct=cong_pct,
            crash_reduction_pct=crash_pct,
            location=location,
        )

        national = self.calculate_national_impact(cong_pct, crash_pct)
        scenarios = self.calculate_scenario_comparison(fleet_size, location)

        return {
            "customer": {
                "type": customer_type.value,
                "description": preset["description"],
                "focus_metric": preset["focus_metric"],
            },
            "parameters": {
                "fleet_size": fleet_size,
                "location": location,
                "congestion_reduction_pct": cong_pct * 100,
                "crash_reduction_pct": crash_pct * 100,
            },
            "roi": fleet_roi,
            "national_impact": national,
            "scenario_comparison": scenarios,
            "pricing": {
                "monthly_fee_usd": self.pricing.MONTHLY_FEE_PER_VEHICLE,
                "annual_fee_usd": self.pricing.ANNUAL_FEE_PER_VEHICLE,
                "gross_margin_pct": self.pricing.GROSS_MARGIN * 100,
            },
            "sources": self.get_all_sources(),
        }
