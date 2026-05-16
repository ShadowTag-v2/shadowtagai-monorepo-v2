# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from enum import Enum, auto
from typing import Any


class PolicyOps(Enum):
    CHECK_PII = auto()
    CHECK_RATE_LIMIT = auto()
    CHECK_CONTENT = auto()
    AND = auto()


class JREngineAST:
    def __init__(self, op: PolicyOps, args: Any = None):
        self.op = op
        self.args = args
        self.wasm_size = 100  # Mock size
        self.estimated_latency_ms = 10  # Mock latency


class PolicyUOp:
    def __init__(self, op: PolicyOps, inputs: list[PolicyUOp] | None = None, ast: JREngineAST | None = None):
        self.op = op
        self.inputs = inputs or []
        self.ast = ast or JREngineAST(op)
