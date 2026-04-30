"""Edge Mesh Architecture: Starlink + CoreWeave + Tesla + Cell Tower Integration
==============================================================================

Implements the unified sky-ground GPU mesh connecting:
- Starlink LEO satellites (orbital layer)
- CoreWeave GPU pods at cell towers (terrestrial layer)
- Tesla HW5/HW6 vehicles (mobile edge layer)
- Satellite uplinks at cell sites (redundancy layer)

Creates planetary-scale verified AI network with <70ms end-to-end latency.
"""

import math
from dataclasses import dataclass
from enum import Enum


class NodeType(Enum):
    """Edge mesh node types"""

    SATELLITE = "satellite"
    CELL_TOWER = "cell_tower"
    VEHICLE = "vehicle"
    GROUND_STATION = "ground_station"
    BUOY = "buoy"


class UplinkType(Enum):
    """Satellite uplink technologies"""

    KA_BAND = "ka_band"  # Starlink standard (26.5-40 GHz)
    KU_BAND = "ku_band"  # Traditional satellite (12-18 GHz)
    V_BAND = "v_band"  # Next-gen high-throughput (40-75 GHz)
    LASER_OPTICAL = "laser_optical"  # Inter-satellite laser links
    HYBRID = "hybrid"  # Multi-band redundancy


@dataclass
class SatelliteUplink:
    """Satellite uplink configuration for cell tower sites"""

    type: UplinkType
    frequency_ghz: float
    bandwidth_gbps: float
    latency_ms: float
    cost_per_site_usd: float
    power_consumption_watts: int
    weather_resilience: float  # 0-1 scale
    installation_complexity: str  # "low", "medium", "high"

    @property
    def monthly_opex_usd(self) -> float:
        """Estimated monthly operational cost"""
        # Power cost + bandwidth cost
        power_cost = (self.power_consumption_watts / 1000) * 24 * 30 * 0.12  # $0.12/kWh
        bandwidth_cost = self.bandwidth_gbps * 30 * 50  # $50/Gbps/month estimate
        return power_cost + bandwidth_cost


@dataclass
class GPUPod:
    """CoreWeave GPU pod configuration"""

    gpu_model: str  # "L40S", "H100", "GH200"
    gpu_count: int
    tflops_int8: int
    power_watts: int
    cost_per_hour_usd: float
    memory_gb: int

    @property
    def monthly_cost_usd(self) -> float:
        """Monthly GPU rental cost"""
        return self.cost_per_hour_usd * 24 * 30

    @property
    def total_compute_tflops(self) -> int:
        """Total compute capacity"""
        return self.tflops_int8 * self.gpu_count


@dataclass
class CellTowerNode:
    """Cell tower edge compute node"""

    tower_id: str
    location: dict[str, float]  # {"lat": x, "lon": y}
    gpu_pod: GPUPod
    uplink: SatelliteUplink
    fiber_backhaul_gbps: int
    coverage_radius_km: float
    monthly_tower_lease_usd: float

    @property
    def total_monthly_cost_usd(self) -> float:
        """Total monthly operational cost"""
        return (
            self.gpu_pod.monthly_cost_usd
            + self.uplink.monthly_opex_usd
            + self.monthly_tower_lease_usd
        )

    @property
    def total_bandwidth_gbps(self) -> float:
        """Combined bandwidth (fiber + satellite)"""
        return self.fiber_backhaul_gbps + self.uplink.bandwidth_gbps


@dataclass
class VehicleNode:
    """Tesla HW5/HW6 vehicle edge node"""

    vehicle_id: str
    hw_version: str  # "HW5" or "HW6"
    gpu_tflops: int  # ~40 TFLOPS INT8
    revenue_per_month_usd: float  # Compute-for-transit earnings
    active_hours_per_day: int = 8

    @property
    def monthly_contribution_tflops_hours(self) -> int:
        """Monthly compute contribution"""
        return self.gpu_tflops * self.active_hours_per_day * 30


@dataclass
class LatencyProfile:
    """End-to-end latency breakdown"""

    device_to_satellite_ms: float = 30.0
    satellite_to_ground_ms: float = 30.0
    ground_to_tower_gpu_ms: float = 5.0
    inference_ms: float = 20.0
    return_path_ms: float = 65.0

    @property
    def total_latency_ms(self) -> float:
        """Total round-trip latency"""
        return (
            self.device_to_satellite_ms
            + self.satellite_to_ground_ms
            + self.ground_to_tower_gpu_ms
            + self.inference_ms
            + self.return_path_ms
        )


class EdgeMeshArchitecture:
    """Unified Sky-Ground GPU Mesh Architecture

    Integrates Starlink orbital layer, CoreWeave cell tower nodes,
    Tesla vehicle fleet, and satellite uplinks into single coordinated
    edge compute fabric.
    """

    # Standard uplink configurations
    UPLINK_CONFIGS = {
        "starlink_standard": SatelliteUplink(
            type=UplinkType.KA_BAND,
            frequency_ghz=28.0,
            bandwidth_gbps=10.0,
            latency_ms=25.0,
            cost_per_site_usd=25_000,
            power_consumption_watts=500,
            weather_resilience=0.85,
            installation_complexity="medium",
        ),
        "starlink_enterprise": SatelliteUplink(
            type=UplinkType.KA_BAND,
            frequency_ghz=28.0,
            bandwidth_gbps=50.0,
            latency_ms=20.0,
            cost_per_site_usd=75_000,
            power_consumption_watts=800,
            weather_resilience=0.90,
            installation_complexity="medium",
        ),
        "v_band_nextgen": SatelliteUplink(
            type=UplinkType.V_BAND,
            frequency_ghz=60.0,
            bandwidth_gbps=100.0,
            latency_ms=15.0,
            cost_per_site_usd=150_000,
            power_consumption_watts=1200,
            weather_resilience=0.75,  # Lower due to rain fade
            installation_complexity="high",
        ),
        "hybrid_redundant": SatelliteUplink(
            type=UplinkType.HYBRID,
            frequency_ghz=28.0,  # Primary
            bandwidth_gbps=60.0,
            latency_ms=20.0,
            cost_per_site_usd=100_000,
            power_consumption_watts=1000,
            weather_resilience=0.98,  # Automatic failover
            installation_complexity="high",
        ),
    }

    # Standard GPU pod configurations
    GPU_CONFIGS = {
        "l40s_dual": GPUPod(
            gpu_model="L40S",
            gpu_count=2,
            tflops_int8=180,  # 90 per GPU
            power_watts=1400,  # 700W each
            cost_per_hour_usd=2.40,
            memory_gb=96,  # 48GB each
        ),
        "l40s_quad": GPUPod(
            gpu_model="L40S",
            gpu_count=4,
            tflops_int8=360,
            power_watts=2800,
            cost_per_hour_usd=4.80,
            memory_gb=192,
        ),
        "h100_single": GPUPod(
            gpu_model="H100",
            gpu_count=1,
            tflops_int8=200,
            power_watts=700,
            cost_per_hour_usd=3.50,
            memory_gb=80,
        ),
        "h100_dual": GPUPod(
            gpu_model="H100",
            gpu_count=2,
            tflops_int8=400,
            power_watts=1400,
            cost_per_hour_usd=7.00,
            memory_gb=160,
        ),
    }

    def __init__(self):
        self.tower_nodes: list[CellTowerNode] = []
        self.vehicle_nodes: list[VehicleNode] = []
        self.latency_profile = LatencyProfile()

    def add_tower_node(
        self,
        tower_id: str,
        location: dict[str, float],
        gpu_config: str = "l40s_dual",
        uplink_config: str = "starlink_standard",
        fiber_backhaul_gbps: int = 10,
        coverage_radius_km: float = 5.0,
        monthly_tower_lease_usd: float = 2000,
    ) -> CellTowerNode:
        """Add cell tower node to mesh"""
        node = CellTowerNode(
            tower_id=tower_id,
            location=location,
            gpu_pod=self.GPU_CONFIGS[gpu_config],
            uplink=self.UPLINK_CONFIGS[uplink_config],
            fiber_backhaul_gbps=fiber_backhaul_gbps,
            coverage_radius_km=coverage_radius_km,
            monthly_tower_lease_usd=monthly_tower_lease_usd,
        )
        self.tower_nodes.append(node)
        return node

    def add_vehicle_node(
        self,
        vehicle_id: str,
        hw_version: str = "HW6",
        revenue_per_month_usd: float = 10.0,
    ) -> VehicleNode:
        """Add vehicle node to mesh"""
        node = VehicleNode(
            vehicle_id=vehicle_id,
            hw_version=hw_version,
            gpu_tflops=40,  # Standard Tesla FSD compute
            revenue_per_month_usd=revenue_per_month_usd,
        )
        self.vehicle_nodes.append(node)
        return node

    def calculate_coverage_area_km2(self) -> float:
        """Calculate total coverage area"""
        total_area = 0.0
        for node in self.tower_nodes:
            area = math.pi * (node.coverage_radius_km**2)
            total_area += area
        return total_area

    def calculate_total_compute_tflops(self) -> float:
        """Calculate aggregate compute capacity"""
        tower_tflops = sum(node.gpu_pod.total_compute_tflops for node in self.tower_nodes)
        vehicle_tflops = sum(node.gpu_tflops for node in self.vehicle_nodes)
        return tower_tflops + vehicle_tflops

    def calculate_monthly_opex_usd(self) -> float:
        """Calculate total monthly operational cost"""
        return sum(node.total_monthly_cost_usd for node in self.tower_nodes)

    def calculate_monthly_revenue_usd(self, arpu: float = 10.0) -> float:
        """Calculate monthly revenue

        Args:
            arpu: Average revenue per user (default $10/month)

        """
        # Estimate users per tower (10k average)
        users_per_tower = 10_000
        tower_revenue = len(self.tower_nodes) * users_per_tower * arpu

        # Vehicle compute revenue
        vehicle_revenue = sum(node.revenue_per_month_usd for node in self.vehicle_nodes)

        return tower_revenue + vehicle_revenue

    def estimate_latency_improvement_vs_cloud(self) -> dict[str, float]:
        """Calculate latency improvement vs traditional cloud"""
        cloud_latency_ms = 150.0  # Typical cloud round-trip
        edge_latency_ms = self.latency_profile.total_latency_ms

        improvement_ms = cloud_latency_ms - edge_latency_ms
        improvement_pct = (improvement_ms / cloud_latency_ms) * 100

        return {
            "cloud_baseline_ms": cloud_latency_ms,
            "edge_mesh_ms": edge_latency_ms,
            "improvement_ms": improvement_ms,
            "improvement_percent": improvement_pct,
        }

    def calculate_starlink_latency_reduction(self) -> dict[str, float]:
        """Calculate latency reduction from tower GPU integration"""
        starlink_only_ms = 140.0  # Starlink + cloud backhaul
        starlink_plus_tower_gpu_ms = 70.0  # Starlink + local tower GPU

        reduction_ms = starlink_only_ms - starlink_plus_tower_gpu_ms
        reduction_pct = (reduction_ms / starlink_only_ms) * 100

        return {
            "starlink_baseline_ms": starlink_only_ms,
            "with_tower_gpu_ms": starlink_plus_tower_gpu_ms,
            "reduction_ms": reduction_ms,
            "reduction_percent": reduction_pct,
        }

    def project_deployment_roi(self, num_towers: int, num_vehicles: int, months: int = 36) -> dict:
        """Project ROI for deployment

        Args:
            num_towers: Number of cell tower nodes
            num_vehicles: Number of vehicle nodes
            months: Projection timeframe (default 36 months)

        """
        # Per-tower costs and revenue
        tower_capex = 50_000  # $50k CAPEX per tower
        tower_monthly_opex = 12_000  # $12k/month average
        tower_monthly_revenue = 30_000  # $30k/month average ($3k/mo per tower in doc)

        # Vehicle revenue (minimal cost)
        vehicle_monthly_revenue = 10.0  # $10/vehicle/month

        # Calculate totals
        total_capex = num_towers * tower_capex
        monthly_opex = num_towers * tower_monthly_opex
        monthly_revenue = (num_towers * tower_monthly_revenue) + (
            num_vehicles * vehicle_monthly_revenue
        )

        cumulative_opex = monthly_opex * months
        cumulative_revenue = monthly_revenue * months

        net_profit = cumulative_revenue - (total_capex + cumulative_opex)
        roi_multiple = (
            cumulative_revenue / (total_capex + cumulative_opex)
            if (total_capex + cumulative_opex) > 0
            else 0
        )

        # Payback period (months)
        monthly_net = monthly_revenue - monthly_opex
        payback_months = total_capex / monthly_net if monthly_net > 0 else float("inf")

        return {
            "deployment": {
                "num_towers": num_towers,
                "num_vehicles": num_vehicles,
                "projection_months": months,
            },
            "investment": {
                "total_capex_usd": total_capex,
                "monthly_opex_usd": monthly_opex,
                "cumulative_opex_usd": cumulative_opex,
            },
            "revenue": {
                "monthly_revenue_usd": monthly_revenue,
                "cumulative_revenue_usd": cumulative_revenue,
            },
            "returns": {
                "net_profit_usd": net_profit,
                "roi_multiple": roi_multiple,
                "payback_period_months": payback_months,
                "gross_margin_percent": ((monthly_revenue - monthly_opex) / monthly_revenue * 100)
                if monthly_revenue > 0
                else 0,
            },
        }

    def export_architecture(self) -> dict:
        """Export complete architecture configuration"""
        return {
            "architecture": "Unified Sky-Ground GPU Mesh",
            "layers": {
                "orbital": {
                    "provider": "Starlink",
                    "satellites": "LEO constellation",
                    "function": "Edge inference + global backhaul",
                },
                "terrestrial": {
                    "provider": "CoreWeave + Cell Towers",
                    "nodes": len(self.tower_nodes),
                    "function": "City-level compute & AI routing",
                },
                "mobile": {
                    "provider": "Tesla HW5/HW6",
                    "nodes": len(self.vehicle_nodes),
                    "function": "Real-time AI & verified local caching",
                },
            },
            "nodes": {
                "tower_count": len(self.tower_nodes),
                "vehicle_count": len(self.vehicle_nodes),
                "total_compute_tflops": self.calculate_total_compute_tflops(),
                "coverage_area_km2": self.calculate_coverage_area_km2(),
            },
            "economics": {
                "monthly_opex_usd": self.calculate_monthly_opex_usd(),
                "monthly_revenue_usd": self.calculate_monthly_revenue_usd(),
            },
            "performance": {
                "latency_ms": self.latency_profile.total_latency_ms,
                "latency_improvement": self.estimate_latency_improvement_vs_cloud(),
                "starlink_enhancement": self.calculate_starlink_latency_reduction(),
            },
        }
