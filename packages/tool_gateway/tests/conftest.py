# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Pytest conftest for tool_gateway package tests.

Adds the packages/ directory to sys.path so that tool_gateway
can be imported without pip install -e.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add packages/ to sys.path for standalone pytest discovery
_packages_dir = str(Path(__file__).resolve().parent.parent.parent)
if _packages_dir not in sys.path:
    sys.path.insert(0, _packages_dir)
