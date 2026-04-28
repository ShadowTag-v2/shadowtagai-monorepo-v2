# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from enum import StrEnum

from pydantic import BaseModel


class PricingTier(StrEnum):
    FREE = "free"
    SOLO = "solo"
    TEAM = "team"
    ENTERPRISE = "enterprise"
    PLATFORM_API = "platform_api"
    WHITE_LABEL = "white_label"


class TierConfig(BaseModel):
    monthly_price: float
    request_limit_daily: int
    sla_uptime: float
    support_level: str
    features: list[str]


# MONEY CHANGES: Updated Pricing Strategy
# Source: docs/MONEY_CHANGES_ANALYSIS.md
PRICING_CONFIG = {
    PricingTier.FREE: TierConfig(
        monthly_price=0.0,
        request_limit_daily=100,
        sla_uptime=0.0,
        support_level="community",
        features=["basic_deadlines"],
    ),
    PricingTier.SOLO: TierConfig(
        monthly_price=29.0,  # Increased from $9 for higher ARPU
        request_limit_daily=1000,
        sla_uptime=0.99,
        support_level="email",
        features=["basic_deadlines", "memory_persistence"],
    ),
    PricingTier.TEAM: TierConfig(
        monthly_price=99.0,
        request_limit_daily=10000,
        sla_uptime=0.995,
        support_level="priority",
        features=["basic_deadlines", "memory_persistence", "4_llm_orchestration"],
    ),
    PricingTier.ENTERPRISE: TierConfig(
        monthly_price=779.0,  # FIXED: Plugged the $50k leak (was $599)
        request_limit_daily=100000,
        sla_uptime=0.9999,
        support_level="24/7_dedicated",
        features=["all", "real_time_latency", "judge_6_validation"],
    ),
    PricingTier.PLATFORM_API: TierConfig(
        monthly_price=0.0,  # Usage based
        request_limit_daily=1000000,
        sla_uptime=0.999,
        support_level="developer",
        features=["kernel_chain_access", "gemini_functions"],
    ),
}

# API Usage Costs (Per Unit)
# Source: docs/MONEY_CHANGES_ANALYSIS.md - Kernel Chaining Economics
API_COSTS = {
    "decision_simple": 0.0003,  # Kernel chain (98.5% cheaper)
    "decision_complex": 0.005,  # Multi-agent/Ultrathink
    "workflow_enterprise": 0.05,  # Full business analysis
    "memory_storage_GB": 0.10,  # Per GB/month
}

# Wealth Leak Thresholds
MIN_ENTERPRISE_PRICE = 700.0
