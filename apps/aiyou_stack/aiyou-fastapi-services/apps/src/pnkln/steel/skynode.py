"""SkyNode Architecture - The Steel
Defines the physical infrastructure classes for Sovereign Compute.
"""

from dataclasses import dataclass
from enum import Enum


class NodeType(Enum):
    NUCLEAR = "NuclearNode"  # Titan Class
    RIG = "RigNode"  # Trident Class
    TOWER = "TowerNode"  # Scout Class


@dataclass
class SkyNodeSpec:
    name: str
    type: NodeType
    capacity_mw: float
    latency_ms: int
    cooling_type: str
    power_source: str
    revenue_multiplier: float = 1.0  # Base rate


class NuclearNode:
    """Titan Class - GW Scale Training Clusters"""

    def __init__(self, name: str, mw: float):
        self.spec = SkyNodeSpec(
            name=name,
            type=NodeType.NUCLEAR,
            capacity_mw=mw,
            latency_ms=20,  # Centralized
            cooling_type="Seawater/Once-Through",
            power_source="Direct HVAC Turbine Tap",
        )

    def calculate_revenue(self, base_rate_per_mw_hr: float) -> float:
        # 95% Utilization assumed for baseload training
        hours = 8760
        utilization = 0.99
        return self.spec.capacity_mw * base_rate_per_mw_hr * hours * utilization


class RigNode:
    """Trident Class - Offshore Data Havens"""

    def __init__(self, name: str, mw: float):
        self.spec = SkyNodeSpec(
            name=name,
            type=NodeType.RIG,
            capacity_mw=mw,
            latency_ms=40,  # Sat Link
            cooling_type="Seawater Loop",
            power_source="Flare Gas / Turbine",
        )

    def calculate_revenue(self, base_rate_per_mw_hr: float) -> float:
        # Sovereign Premium (Unregulated)
        premium = 1.5
        hours = 8760
        utilization = 0.90
        return self.spec.capacity_mw * (base_rate_per_mw_hr * premium) * hours * utilization


class TowerNode:
    """Scout Class - 5ms Edge Inference"""

    def __init__(self, name: str, kw: float):
        self.spec = SkyNodeSpec(
            name=name,
            type=NodeType.TOWER,
            capacity_mw=kw / 1000.0,  # Convert kW to MW
            latency_ms=5,
            cooling_type="Passive 2-Phase",
            power_source="-48V DC Telecom",
        )

    def calculate_revenue(self, base_rate_per_mw_hr: float) -> float:
        # Low Latency Premium
        premium = 2.0
        hours = 8760
        utilization = 0.60  # Bursty inference
        return self.spec.capacity_mw * (base_rate_per_mw_hr * premium) * hours * utilization
