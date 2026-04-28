# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""JR Engine, Token Router, Confidence Monitor, and scoring modules"""

from .confidence_monitor import (
    ActionType,
    ConfidenceLevel,
    ConfidenceMonitor,
    ConfidenceResult,
    SOPCDecisionProtocol,
    analyze_confidence,
    check_lowest_confidence,
)
from .jr_engine import JREngine, classify_tier, score_content
from .token_router import (
    LongShortRouter,
    ModelTier,
    RoutingDecision,
    TokenRouterPipeline,
    calculate_token_entropy,
    estimate_routing_cost,
    route_token,
)

__all__ = [
    # JR Engine
    "JREngine",
    "score_content",
    "classify_tier",
    # Token Router
    "LongShortRouter",
    "TokenRouterPipeline",
    "ModelTier",
    "RoutingDecision",
    "route_token",
    "calculate_token_entropy",
    "estimate_routing_cost",
    # Confidence Monitor (SOP-C)
    "ConfidenceMonitor",
    "SOPCDecisionProtocol",
    "ConfidenceLevel",
    "ActionType",
    "ConfidenceResult",
    "analyze_confidence",
    "check_lowest_confidence",
]
