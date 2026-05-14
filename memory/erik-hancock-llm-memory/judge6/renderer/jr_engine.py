# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
from ..uop import PolicyOps, PolicyUOp


class ATP519Patterns:
    SSN = 1
    CCN = 2


class JREngineRenderer:
    """PolicyUOp AST → WASM text format (WAT)"""

    def render(self, policy: PolicyUOp) -> str:
        # Start with WASM module skeleton
        wat = ["(module"]

        # Import ATP_519_scan from host
        wat.append('(import "env" "atp_519_scan" (func $atp_scan (param i32 i32) (result i32)))')

        # Render policy logic
        wat.append(self._render_policy(policy))

        # Export main check function
        wat.append('(export "check_policy" (func $check_policy))')

        wat.append(")")
        return "\n".join(wat)

    def _render_policy(self, policy: PolicyUOp) -> str:
        if policy.op == PolicyOps.CHECK_PII:
            return f"""
            (func $check_policy (param $ctx i32) (result i32)
                (call $atp_scan (local.get $ctx) (i32.const {ATP519Patterns.SSN}))
            )
            """
        # Add more ops as needed
        return ""
