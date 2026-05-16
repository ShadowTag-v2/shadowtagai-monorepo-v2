# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""AGNT XML Two-Stage Classifier — Package Init.

Reference: AGNT STATE B Spec P2.1, P2.3, P5.1, P6.1
"""

from agnt_classifier.classifier import XMLClassifier, TwoStageClassifier
from agnt_classifier.allowlist import SAFE_ALLOWLIST, is_allowlisted
from agnt_classifier.agnt_api import AGNTClassifier, ClassifierVerdict, ClassifierResult
from agnt_classifier.bridge import ClassifiedGateway, GatewayAction, GatewayResult
from agnt_classifier.mcp_policy import (
  MCPPolicyConfig,
  MCPServerInfo,
  PolicyEntry,
  PolicyResult,
  get_default_agnt_policy,
  is_mcp_server_allowed_by_policy,
  filter_servers_by_policy,
)
from agnt_classifier.chain_depth_limiter import (
  ChainDepthLimiter,
  ChainState,
  EscalationLevel,
)
from agnt_classifier.diagnostics import (
  ClassifierDiagnostics,
  DiagnosticCheck,
  DiagnosticStatus,
  run_classifier_diagnostics,
)

__all__ = [
  # Core classifier
  "XMLClassifier",
  "TwoStageClassifier",
  "AGNTClassifier",
  "ClassifierVerdict",
  "ClassifierResult",
  "SAFE_ALLOWLIST",
  "is_allowlisted",
  # Bridge / Gateway
  "ClassifiedGateway",
  "GatewayAction",
  "GatewayResult",
  # MCP Policy
  "MCPPolicyConfig",
  "MCPServerInfo",
  "PolicyEntry",
  "PolicyResult",
  "get_default_agnt_policy",
  "is_mcp_server_allowed_by_policy",
  "filter_servers_by_policy",
  # Chain Depth Limiter (Judge 6)
  "ChainDepthLimiter",
  "ChainState",
  "EscalationLevel",
  # Diagnostics
  "ClassifierDiagnostics",
  "DiagnosticCheck",
  "DiagnosticStatus",
  "run_classifier_diagnostics",
]
