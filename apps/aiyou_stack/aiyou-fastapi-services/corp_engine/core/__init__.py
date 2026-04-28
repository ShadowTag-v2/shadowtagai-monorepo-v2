# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Corp Engine Core - Self-configuring AI engine"""

from .self_config import (
    AIConfigProfile,
    CompanySize,
    IndustryVertical,
    SelfConfiguringEngine,
    self_config_engine,
)

# Convenience aliases
INDUSTRY_CONFIGS = SelfConfiguringEngine.INDUSTRY_CONFIGS


def get_engine() -> SelfConfiguringEngine:
    """Get global self-config engine instance"""
    return self_config_engine


__all__ = [
    "INDUSTRY_CONFIGS",
    "AIConfigProfile",
    "CompanySize",
    "IndustryVertical",
    "SelfConfiguringEngine",
    "get_engine",
    "self_config_engine",
]
