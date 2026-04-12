"""Configuration management"""

from .settings import Settings, settings
from .verticals import VerticalConfig, VerticalType, get_vertical_by_name, get_vertical_config

__all__ = [
    "Settings",
    "settings",
    "VerticalType",
    "VerticalConfig",
    "get_vertical_config",
    "get_vertical_by_name",
]
