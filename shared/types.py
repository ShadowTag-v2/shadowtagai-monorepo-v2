# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Literal


class Verdict(str, Enum):
  ALLOW = "allow"
  REJECT = "reject"
  REVIEW = "review"


class DeploymentZone(str, Enum):
  US = "us"
  EU = "eu"
  UK = "uk"
  APAC = "apac"


@dataclass(slots=True)
class PolicyDecision:
  verdict: Verdict
  rule_id: str
  reason: str
  evidence: list[str] = field(default_factory=list)
  confidence: float = 0.0
  metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class RetrievedChunk:
  id: str
  text: str
  score: float
  metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class PromptExecutionRecord:
  prompt_id: str
  prompt_version: str
  agent_id: str
  model: str
  input_hash: str
  output_hash: str
  trace_id: str
  tags: dict[str, str] = field(default_factory=dict)


ActionName = Literal["export_data", "invoke_model", "store_artifact", "route_request"]
