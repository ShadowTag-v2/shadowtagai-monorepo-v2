# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Bootstrap Constraints Configuration
Enforces operational gates for ShadowTagAi agent platform
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class BootstrapConstraints:
    """Bootstrap operational constraints"""

    # Financial constraints
    monthly_burn_usd: float = 65000.0  # $60-65K/mo
    roi_gate_multiplier: float = 3.0  # ≥3× ROI (18mo)
    roi_gate_months: int = 18
    ltv_cac_ratio: float = 4.0  # ≥4:1 LTV:CAC (12mo)
    ltv_cac_gate_months: int = 12

    # Performance constraints
    sla_p99_ms: int = 90  # p99 ≤90ms
    sla_p50_ms: int = 50  # p50 ≤50ms

    # Security constraints
    security_gate: float = 1.0  # 100% (loss = ONLY mission until restored)

    # Agent operational costs (monthly)
    gemini_flash_min_usd: float = 800.0
    gemini_flash_max_usd: float = 1200.0
    chromadb_hosting_usd: float = 0.0  # Self-hosted
    cloudflare_workers_min_usd: float = 200.0
    cloudflare_workers_max_usd: float = 400.0
    Claude_Code_6_maintenance_usd: float = 0.0  # No ML training yet

    def get_total_operational_cost_range(self) -> tuple[float, float]:
        """Get min/max operational cost range"""
        min_cost = (
            self.gemini_flash_min_usd
            + self.chromadb_hosting_usd
            + self.cloudflare_workers_min_usd
            + self.Claude_Code_6_maintenance_usd
        )
        max_cost = (
            self.gemini_flash_max_usd
            + self.chromadb_hosting_usd
            + self.cloudflare_workers_max_usd
            + self.Claude_Code_6_maintenance_usd
        )
        return min_cost, max_cost

    def calculate_break_even_customers(self, monthly_price: float) -> tuple[int, int]:
        """Calculate break-even customer count"""
        min_cost, max_cost = self.get_total_operational_cost_range()
        min_customers = int(min_cost / monthly_price) + 1
        max_customers = int(max_cost / monthly_price) + 1
        return min_customers, max_customers

    def calculate_break_even_leads(self, price_per_lead: float) -> tuple[int, int]:
        """Calculate break-even lead count"""
        min_cost, max_cost = self.get_total_operational_cost_range()
        min_leads = int(min_cost / price_per_lead) + 1
        max_leads = int(max_cost / price_per_lead) + 1
        return min_leads, max_leads

    def validate_sla(self, latency_ms: float, percentile: str = "p99") -> bool:
        """Validate latency against SLA"""
        if percentile == "p99":
            return latency_ms <= self.sla_p99_ms
        if percentile == "p50":
            return latency_ms <= self.sla_p50_ms
        raise ValueError(f"Unknown percentile: {percentile}")

    def validate_ltv_cac(self, ltv: float, cac: float) -> bool:
        """Validate LTV:CAC ratio meets gate"""
        if cac == 0:
            return True  # Infinite ratio
        ratio = ltv / cac
        return ratio >= self.ltv_cac_ratio

    def validate_roi(self, revenue: float, cost: float) -> bool:
        """Validate ROI meets gate"""
        if cost == 0:
            return True  # Infinite ROI
        roi_multiplier = revenue / cost
        return roi_multiplier >= self.roi_gate_multiplier

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "monthly_burn_usd": self.monthly_burn_usd,
            "roi_gate": f"≥{self.roi_gate_multiplier}× ({self.roi_gate_months}mo)",
            "ltv_cac_gate": f"≥{self.ltv_cac_ratio}:1 ({self.ltv_cac_gate_months}mo)",
            "sla_p99_ms": self.sla_p99_ms,
            "sla_p50_ms": self.sla_p50_ms,
            "security_gate": f"{int(self.security_gate * 100)}%",
            "operational_cost_range": self.get_total_operational_cost_range(),
        }


# Default instance
DEFAULT_CONSTRAINTS = BootstrapConstraints()
