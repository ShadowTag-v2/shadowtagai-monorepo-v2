# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Configuration management"""

from .settings import Settings, settings
from .verticals import VerticalConfig, VerticalType, get_vertical_by_name, get_vertical_config

__all__ = [
    "Settings",
    "VerticalConfig",
    "VerticalType",
    "get_vertical_by_name",
    "get_vertical_config",
    "settings",
]
