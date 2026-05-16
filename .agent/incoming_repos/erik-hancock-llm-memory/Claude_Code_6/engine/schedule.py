# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from typing import Any

from ..uop import JREngineAST, PolicyUOp


class EnforcementItem:
    """Atomic governance decision (executable in <90ms)"""

    def __init__(self, ast: JREngineAST, bufs: tuple[Any, ...], latency_budget_ms: int):
        self.ast = ast
        self.bufs = bufs
        self.latency_budget_ms = latency_budget_ms


class GovernanceScheduler:
    """Break policy graph → executable chunks"""

    def schedule(self, uop: PolicyUOp) -> list[EnforcementItem]:
        # Topological sort to respect dependencies
        sorted_ops = self._topo_sort(uop)

        # Greedy fusion: merge sequential ops if under latency budget
        chunks = []
        current_chunk = []
        current_latency_estimate_ms = 0

        for op in sorted_ops:
            op_latency = self._estimate_latency(op)

            if current_latency_estimate_ms + op_latency < 80:  # 10ms buffer
                current_chunk.append(op)
                current_latency_estimate_ms += op_latency
            else:
                # Flush current chunk
                chunks.append(
                    EnforcementItem(
                        ast=self._merge_ops(current_chunk),
                        bufs=(),  # Placeholder
                        latency_budget_ms=90,
                    )
                )
                current_chunk = [op]
                current_latency_estimate_ms = op_latency

        # Flush final chunk
        if current_chunk:
            chunks.append(
                EnforcementItem(
                    ast=self._merge_ops(current_chunk),
                    bufs=(),  # Placeholder
                    latency_budget_ms=90,
                )
            )

        return chunks

    def _topo_sort(self, uop: PolicyUOp) -> list[PolicyUOp]:
        # Simple recursive DFS for topo sort
        visited = set()
        result = []

        def visit(node):
            if node in visited:
                return
            visited.add(node)
            for inp in node.inputs:
                visit(inp)
            result.append(node)

        visit(uop)
        return result

    def _estimate_latency(self, op: PolicyUOp) -> int:
        return op.ast.estimated_latency_ms

    def _merge_ops(self, ops: list[PolicyUOp]) -> JREngineAST:
        # Placeholder for AST merging logic
        # In real impl, this would combine ASTs into a single module
        # For now, just return the AST of the first op or a fused placeholder
        return ops[0].ast
