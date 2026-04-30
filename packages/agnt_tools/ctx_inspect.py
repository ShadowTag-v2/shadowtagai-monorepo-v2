# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""
Context Inspection Tool (CtxInspectTool)
Equivalent to Claude Code's CtxInspectTool for monitoring token budgeting.
"""

import json


class CtxInspectTool:
    def __init__(self, context_compactor):
        self.name = "ctx_inspect"
        self.compactor = context_compactor

    def inspect_budget(self, current_context: dict) -> str:
        """
        Analyzes the current context window and returns token usage estimates.
        """
        total_chars = len(json.dumps(current_context))
        estimated_tokens = total_chars // 4  # Rough heuristic

        report = [
            "=== Context Budget Inspection ===",
            f"Estimated Tokens Used: ~{estimated_tokens}",
            f"Raw Character Count: {total_chars}",
            "===============================",
        ]
        return "\n".join(report)
