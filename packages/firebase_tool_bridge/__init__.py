# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

# Copyright 2026 ShadowTag AI. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
"""Firebase Tool Bridge — Client Action Truth for Monorepo OS.

Maps Firebase AI Logic function calls to approved application functions
with evidence logging, risk classification, and ToolGateway compliance.

Architecture:
    Model proposes → Bridge validates → App executes → Bridge logs → SDK returns

Usage:
    from firebase_tool_bridge import ToolBridge, FunctionRegistry, RiskTier

    registry = FunctionRegistry()
    registry.register("fetch_weather", fetch_weather, RiskTier.LOW)
    bridge = ToolBridge(registry)
    result = bridge.handle(function_call)
"""

from firebase_tool_bridge.registry import (
    FunctionRegistry,
    RegisteredFunction,
    RiskTier,
)
from firebase_tool_bridge.bridge import ToolBridge
from firebase_tool_bridge.evidence import EvidenceLogger

__all__ = [
    "EvidenceLogger",
    "FunctionRegistry",
    "RegisteredFunction",
    "RiskTier",
    "ToolBridge",
]

__version__ = "0.1.0"
