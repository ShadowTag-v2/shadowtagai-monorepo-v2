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
    "SelfConfiguringEngine",
    "self_config_engine",
    "get_engine",
    "INDUSTRY_CONFIGS",
    "IndustryVertical",
    "CompanySize",
    "AIConfigProfile",
]
