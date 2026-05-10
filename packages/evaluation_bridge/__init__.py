# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Evaluation Bridge — Surgical build-merge cycles for Deep Research.

Maps the OrbStack Sandbox to the EXECUTING and VERIFYING phases of
the DeepResearchEngine.  Runs a gate pipeline:

  1. BUILD: Compile / install dependencies in sandbox
  2. TEST:  Run test suite in sandbox
  3. LINT:  Run ruff/biome in sandbox
  4. MERGE: Apply verified overlay changes to workspace

Each gate produces a pass/fail signal.  All gates must pass before
merge is authorized.

Public API:
  - EvaluationConfig: Gate configuration
  - EvaluationResult: Aggregated gate results
  - GateResult: Single gate pass/fail
  - EvaluationBridge: Main orchestrator
"""

from evaluation_bridge.bridge import (
  EvaluationBridge,
  EvaluationConfig,
  EvaluationResult,
  GateResult,
  GateType,
)

__all__ = [
  "EvaluationBridge",
  "EvaluationConfig",
  "EvaluationResult",
  "GateResult",
  "GateType",
]
