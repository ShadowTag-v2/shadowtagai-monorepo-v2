# Copyright 2026 ShadowTagAI. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
"""Firebase Tool Bridge — Client Action Truth for Monorepo OS.

Maps Firebase AI Logic function calls to approved application functions
with evidence logging, risk classification, and ToolGateway compliance.

Architecture:
    Model proposes → Bridge validates → App executes → Bridge logs → SDK returns

Usage:
    from firebase_tool_bridge import ToolBridge, FunctionRegistry, RiskTier
    from firebase_tool_bridge.declarations import registry_to_declarations
    from firebase_tool_bridge.firebase_chat_loop import FirebaseChatLoop
    from firebase_tool_bridge.remote_config import ModelConfig

    registry = FunctionRegistry()
    registry.register("fetch_weather", fetch_weather, RiskTier.LOW)
    bridge = ToolBridge(registry)

    # Generate Firebase-compatible tool declarations
    declarations = registry_to_declarations(registry)

    # Configure model parameters via Remote Config
    config = ModelConfig.from_remote_config(template)
"""

from firebase_tool_bridge.bridge import BridgeResult, CallStatus, ToolBridge
from firebase_tool_bridge.declarations import (
    function_to_declaration,
    registry_to_declarations,
)
from firebase_tool_bridge.evidence import EvidenceLogger
from firebase_tool_bridge.firebase_chat_loop import (
    ChatLoopResult,
    FirebaseChatLoop,
    FunctionCallPart,
    FunctionResponsePart,
    ModelResponse,
)
from firebase_tool_bridge.registry import (
    FunctionRegistry,
    RegisteredFunction,
    RiskTier,
)
from firebase_tool_bridge.remote_config import ModelConfig
from firebase_tool_bridge.workspace_confirmation import (
    OfflineConfirmationProvider,
    SovereignConfirmationProvider,
    WorkspaceCLIConfirmationProvider,
)
from firebase_tool_bridge.confirmation_providers import (
    AllowlistConfirmationProvider,
    FirebaseAuthConfirmationProvider,
    SlackConfirmationProvider,
)

__all__ = [
    "AllowlistConfirmationProvider",
    "BridgeResult",
    "CallStatus",
    "ChatLoopResult",
    "EvidenceLogger",
    "FirebaseAuthConfirmationProvider",
    "FirebaseChatLoop",
    "FunctionCallPart",
    "FunctionRegistry",
    "FunctionResponsePart",
    "ModelConfig",
    "ModelResponse",
    "OfflineConfirmationProvider",
    "RegisteredFunction",
    "RiskTier",
    "SlackConfirmationProvider",
    "SovereignConfirmationProvider",
    "ToolBridge",
    "WorkspaceCLIConfirmationProvider",
    "function_to_declaration",
    "registry_to_declarations",
]

__version__ = "0.3.0"
