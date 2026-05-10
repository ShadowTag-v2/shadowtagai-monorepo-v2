# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""AGNT Classifier API — Structured wrapper around TwoStageClassifier.

Provides AGNTClassifier (full structured classifier) and ClassifierVerdict enum
for use by the ClassifiedGateway and other downstream consumers.

Reference: AGNT STATE B Spec P2.1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from agnt_classifier.classifier import TwoStageClassifier
from agnt_classifier.allowlist import is_allowlisted

logger = logging.getLogger(__name__)


class ClassifierVerdict(StrEnum):
  """Verdict from the two-stage classification pipeline."""

  ALLOW = "allow"
  BLOCK = "block"
  ERROR = "error"


@dataclass(frozen=True)
class ClassifierResult:
  """Structured result from classification."""

  verdict: ClassifierVerdict
  stage: int = 0
  reasoning: str = ""
  errors: list[str] = field(default_factory=list)


class AGNTClassifier:
  """Full classifier combining allowlist check + two-stage classification.

  Pipeline:
      1. Check allowlist → auto-ALLOW if tool is safe
      2. Run TwoStageClassifier → ALLOW or BLOCK
      3. On error → ClassifierVerdict.ERROR (fail-closed)
  """

  def __init__(self) -> None:
    self._two_stage = TwoStageClassifier()

  def classify(
    self,
    tool_id: str,
    tool_input: dict[str, Any] | None = None,
    context: dict[str, Any] | None = None,
  ) -> ClassifierResult:
    """Classify a tool call."""
    tool_input = tool_input or {}

    # Fast path: allowlisted tools skip classifier
    if is_allowlisted(tool_id):
      return ClassifierResult(
        verdict=ClassifierVerdict.ALLOW,
        stage=0,
        reasoning=f"Tool '{tool_id}' is in SAFE_ALLOWLIST.",
      )

    # Build query from tool_id + input
    query_parts = [tool_id]
    if cmd := tool_input.get("CommandLine") or tool_input.get("command"):
      query_parts.append(str(cmd))
    query = " ".join(query_parts)

    try:
      result = self._two_stage.classify(query)
    except Exception as e:
      logger.error("Classifier error: %s", e)
      return ClassifierResult(
        verdict=ClassifierVerdict.ERROR,
        stage=0,
        reasoning="",
        errors=[str(e)],
      )

    if result == "ALLOW":
      return ClassifierResult(
        verdict=ClassifierVerdict.ALLOW,
        stage=1,
        reasoning=f"Two-stage classifier ALLOWED tool '{tool_id}'.",
      )

    return ClassifierResult(
      verdict=ClassifierVerdict.BLOCK,
      stage=2,
      reasoning=f"Two-stage classifier BLOCKED tool '{tool_id}'.",
    )
