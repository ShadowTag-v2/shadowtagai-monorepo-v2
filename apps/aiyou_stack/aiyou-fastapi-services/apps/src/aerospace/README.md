# Aerospace Module API Reference

## Overview

The `src.aerospace` module provides comprehensive tooling for modeling, valuing, and deploying AiY's aerospace expansion strategy.

## Installation

```python

# Module is part of shadowtag_v4-fastapi-services

from src.aerospace import (
    AerospaceBusinessPlan,
    EnterpriseValuationModel,
    EdgeMeshArchitecture,
    ROICalculator
)

```

## Core Classes

### `AerospaceBusinessPlan`

Models the complete 7-phase aerospace rollout (2025-2031).

**Example**:

```python
from src.aerospace import AerospaceBusinessPlan

plan = AerospaceBusinessPlan()

# Access specific phase

phase3 = plan.get_phase(3)  # OEM Partnerships
print(f"Investment: ${phase3.estimated_cost_usd:,.0f}")
print(f"Expected ROI: {phase3.roi:.1%}")

# Get financial summary

summary = plan.financial_summary
print(f"Total Investment: ${summary.total_investment_usd:,.0f}")
print(f"Founder Value (60%): ${summary.founder_retained_value_usd:,.0f}")

# Export complete plan

plan_dict = plan.export_to_dict()

```

**Methods**:

- `get_phase(number: int) -> Phase`: Get specific phase details

- `get_current_phase(date: datetime) -> Phase`: Determine current phase

- `calculate_projected_value(year: int) -> float`: Calculate valuation for target year

- `generate_launch_order_summary() -> List[str]`: Get launch sequence

- `export_to_dict() -> Dict`: Export complete plan as dictionary

### `EnterpriseValuationModel`

Multi-scenario enterprise valuation with Monte Carlo simulation.

**Example**:

```python
from src.aerospace import EnterpriseValuationModel, MarketScenario

valuation = EnterpriseValuationModel(target_year=2030)

# Calculate total enterprise value

total_ev = valuation.calculate_total_enterprise_value(MarketScenario.BASE)
print(f"Enterprise Value: ${total_ev:,.0f}")

# Run Monte Carlo simulation

mc_result = valuation.run_monte_carlo(iterations=10_000)
print(f"Median Valuation: ${mc_result.percentile_50:,.0f}")
print(f"P(≥$12B): {mc_result.probability_above_threshold[12_000_000_000]:.1%}")

# Calculate founder value

founder = valuation.calculate_founder_value(equity_percent=60.0)
print(f"Founder Equity: ${founder['founder_equity_value_usd']:,.0f}")
print(f"Annual Cash Flow: ${founder['founder_annual_cash_usd']:,.0f}")

```

**Methods**:

- `calculate_total_enterprise_value(scenario) -> float`: Calculate total EV

- `calculate_division_value(division_key, scenario) -> float`: Single division value

- `run_monte_carlo(iterations, threshold) -> MonteCarloResult`: Run simulation

- `calculate_founder_value(equity_percent) -> Dict`: Founder economics

- `project_timeline() -> List[Dict]`: Valuation timeline 2025-2031

### `EdgeMeshArchitecture`

Models the Starlink + CoreWeave + Tesla unified edge mesh.

**Example**:

```python
from src.aerospace import EdgeMeshArchitecture

mesh = EdgeMeshArchitecture()

# Add cell tower nodes

for i in range(100):
    mesh.add_tower_node(
        tower_id=f"TOWER-{i:04d}",
        location={"lat": 37.7 + i*0.01, "lon": -122.4 + i*0.01},
        gpu_config="l40s_dual",              # 2× L40S GPUs
        uplink_config="starlink_standard",   # Ka-band uplink
        coverage_radius_km=5.0
    )

# Add vehicle nodes

for i in range(10_000):
    mesh.add_vehicle_node(
        vehicle_id=f"TESLA-{i:06d}",
        hw_version="HW6",
        revenue_per_month_usd=10.0
    )

# Calculate metrics

print(f"Total Compute: {mesh.calculate_total_compute_tflops():,.0f} TFLOPS")
print(f"Coverage: {mesh.calculate_coverage_area_km2():,.0f} km²")
print(f"Monthly Revenue: ${mesh.calculate_monthly_revenue_usd():,.0f}")

# Latency analysis

latency_improvement = mesh.estimate_latency_improvement_vs_cloud()
print(f"Latency Improvement: {latency_improvement['improvement_percent']:.1f}%")

# ROI projection

roi = mesh.project_deployment_roi(
    num_towers=100,
    num_vehicles=10_000,
    months=36
)
print(f"3-Year ROI: {roi['returns']['roi_multiple']:.2f}x")

```

**GPU Configurations**:

- `l40s_dual`: 2× L40S (180 TFLOPS, $2.40/hr)

- `l40s_quad`: 4× L40S (360 TFLOPS, $4.80/hr)

- `h100_single`: 1× H100 (200 TFLOPS, $3.50/hr)

- `h100_dual`: 2× H100 (400 TFLOPS, $7.00/hr)

**Uplink Configurations**:

- `starlink_standard`: 10 Gbps, 25ms, $25k CAPEX

- `starlink_enterprise`: 50 Gbps, 20ms, $75k CAPEX

- `v_band_nextgen`: 100 Gbps, 15ms, $150k CAPEX

- `hybrid_redundant`: 60 Gbps, 20ms, 98% resilience, $100k CAPEX

**Methods**:

- `add_tower_node(...) -> CellTowerNode`: Add cell tower

- `add_vehicle_node(...) -> VehicleNode`: Add vehicle

- `calculate_total_compute_tflops() -> float`: Aggregate compute

- `calculate_monthly_opex_usd() -> float`: Monthly costs

- `calculate_monthly_revenue_usd(arpu) -> float`: Monthly revenue

- `estimate_latency_improvement_vs_cloud() -> Dict`: Latency metrics

- `project_deployment_roi(...) -> Dict`: ROI projection

### `ROICalculator`

Comprehensive ROI calculations across deployment scales.

**Example**:

```python
from src.aerospace.economics import ROICalculator, DeploymentConfig

# Define deployment

config = DeploymentConfig(
    num_cell_towers=20_000,
    num_vehicles=1_000_000,
    num_satellites=20,
    deployment_months=36
)

calculator = ROICalculator(config)

# Calculate ROI

roi = calculator.calculate_roi()
print(f"Total Investment: ${roi['investment']['total_investment_usd']:,.0f}")
print(f"Net Profit: ${roi['returns']['net_profit_usd']:,.0f}")
print(f"ROI Multiple: {roi['returns']['roi_multiple']:.2f}x")
print(f"Payback Period: {roi['returns']['payback_period_months']:.1f} months")

# Pre-built scenarios

pilot_roi = calculator.calculate_pilot_economics()        # 10 towers, 3 months
regional_roi = calculator.calculate_regional_economics()  # 100 towers, 9 months
national_roi = calculator.calculate_national_economics()  # 20k towers, 36 months
global_roi = calculator.calculate_global_economics()      # 100k towers, 60 months

```

**Methods**:

- `calculate_roi() -> Dict`: Full ROI calculation

- `calculate_pilot_economics() -> Dict`: Pilot scale (10 towers)

- `calculate_regional_economics() -> Dict`: Regional scale (100 towers)

- `calculate_national_economics() -> Dict`: National scale (20k towers)

- `calculate_global_economics() -> Dict`: Global scale (100k towers)

- `project_valuation_curve() -> List[Dict]`: Valuation growth timeline

## Data Structures

### `Phase`

Single business plan phase.

**Fields**:

- `number: int`: Phase number (1-7)

- `name: str`: Phase name

- `quarter: str`: Target quarter

- `year: int`: Target year

- `objective: str`: Phase objective

- `deliverables: List[str]`: Key deliverables

- `estimated_cost_usd: float`: Investment required

- `expected_contracts_usd: float`: Expected revenue/contracts

- `post_phase_valuation_usd: float`: Post-phase valuation

- `partners: List[str]`: Key partners

- `status: PhaseStatus`: Current status

- `roi: float`: Calculated ROI (property)

### `Division`

Business division for valuation.

**Fields**:

- `name: str`: Division name

- `arr_usd: float`: Annual recurring revenue

- `ebitda_margin: float`: EBITDA margin (0.0-1.0)

- `revenue_multiple: float`: Revenue multiple for valuation

- `ebitda_multiple: float`: EBITDA multiple for valuation

- `contribution_percent: float`: % of total enterprise value

### `CellTowerNode`

Cell tower edge compute node.

**Fields**:

- `tower_id: str`: Unique tower identifier

- `location: Dict[str, float]`: {"lat": x, "lon": y}

- `gpu_pod: GPUPod`: GPU configuration

- `uplink: SatelliteUplink`: Satellite uplink configuration

- `fiber_backhaul_gbps: int`: Fiber bandwidth

- `coverage_radius_km: float`: Coverage radius

- `monthly_tower_lease_usd: float`: Tower lease cost

- `total_monthly_cost_usd: float`: Total monthly cost (property)

- `total_bandwidth_gbps: float`: Combined bandwidth (property)

### `VehicleNode`

Tesla vehicle edge node.

**Fields**:

- `vehicle_id: str`: Unique vehicle identifier

- `hw_version: str`: Hardware version ("HW5" or "HW6")

- `gpu_tflops: int`: GPU compute capacity (~40 TFLOPS)

- `revenue_per_month_usd: float`: Monthly compute revenue

- `active_hours_per_day: int`: Active compute hours (default 8)

## Enumerations

### `PhaseStatus`

```python
class PhaseStatus(Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DELAYED = "delayed"

```

### `MarketScenario`

```python
class MarketScenario(Enum):
    BEAR = "bear"     # Conservative, 70% ARR, 12× EBITDA
    BASE = "base"     # Expected, 100% ARR, 20× EBITDA
    BULL = "bull"     # Optimistic, 130% ARR, 25× EBITDA

```

### `UplinkType`

```python
class UplinkType(Enum):
    KA_BAND = "ka_band"           # Starlink standard (26.5-40 GHz)
    KU_BAND = "ku_band"           # Traditional satellite (12-18 GHz)
    V_BAND = "v_band"             # Next-gen high-throughput (40-75 GHz)
    LASER_OPTICAL = "laser_optical"  # Inter-satellite laser links
    HYBRID = "hybrid"             # Multi-band redundancy

```

## Complete Example

```python
#!/usr/bin/env python3

"""Complete aerospace analysis example"""

from src.aerospace import (
    AerospaceBusinessPlan,
    EnterpriseValuationModel,
    EdgeMeshArchitecture,
    ROICalculator
)
from src.aerospace.economics import DeploymentConfig

# 1. Business Plan Analysis

plan = AerospaceBusinessPlan()
print(f"Total Investment (2025-2030): ${plan.financial_summary.total_investment_usd:,.0f}")
print(f"Expected Valuation (2031): ${plan.financial_summary.aggregate_valuation_usd:,.0f}")

# 2. Enterprise Valuation

valuation = EnterpriseValuationModel(target_year=2030)
mc = valuation.run_monte_carlo()
print(f"\nValuation Range:")
print(f"  10th %ile: ${mc.percentile_10:,.0f}")
print(f"  50th %ile: ${mc.percentile_50:,.0f}")
print(f"  90th %ile: ${mc.percentile_90:,.0f}")

# 3. Edge Mesh Deployment

mesh = EdgeMeshArchitecture()

# Add infrastructure

for i in range(100):
    mesh.add_tower_node(
        tower_id=f"TOWER-{i:04d}",
        location={"lat": 37.7, "lon": -122.4},
        gpu_config="l40s_dual",
        uplink_config="starlink_standard"
    )

for i in range(10_000):
    mesh.add_vehicle_node(f"TESLA-{i:06d}", hw_version="HW6")

print(f"\nEdge Mesh:")
print(f"  Total Compute: {mesh.calculate_total_compute_tflops():,.0f} TFLOPS")
print(f"  Monthly Revenue: ${mesh.calculate_monthly_revenue_usd():,.0f}")

# 4. ROI Calculation

config = DeploymentConfig(
    num_cell_towers=20_000,
    num_vehicles=1_000_000,
    num_satellites=20,
    deployment_months=36
)

calculator = ROICalculator(config)
roi = calculator.calculate_roi()

print(f"\nNational Deployment ROI (36 months):")
print(f"  Investment: ${roi['investment']['total_investment_usd']:,.0f}")
print(f"  Revenue: ${roi['revenue']['cumulative_revenue_usd']:,.0f}")
print(f"  Net Profit: ${roi['returns']['net_profit_usd']:,.0f}")
print(f"  ROI: {roi['returns']['roi_multiple']:.2f}x")
print(f"  Payback: {roi['returns']['payback_period_months']:.1f} months")

```

## See Also

- [Complete Business Plan](../../docs/aerospace/COR-19-AEROSPACE-PLAN.md)

- [Interactive Demo](../../examples/aerospace_demo.py)

- [Main README](../../README.md)
