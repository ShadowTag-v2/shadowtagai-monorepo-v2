# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Tool Gateway — Monorepo-Bounced Tool Call Mediator.

Routes high-risk agent tool calls through contract validation,
repo oracle queries, and evidence logging before execution.

Architecture:
    Agent Intent → Contract Check → Repo Oracle → Policy Gate → Execute + Evidence

Usage:
    from packages.tool_gateway import ToolGateway

    gw = ToolGateway(repo_root=Path("."))
    decision = gw.check("github.push", context={"branch": "main", "files": 3})
    if decision.allowed:
        # proceed with push
    else:
        print(decision.reason)
"""

from packages.tool_gateway.gateway import Decision, ToolGateway
from packages.tool_gateway.classified_gateway import ClassifiedGateway
from packages.tool_gateway.bash_ast import BashASTAnalyzer, BashASTResult
from packages.tool_gateway.security import SecurityHardening, SecurityCheckResult

__all__ = [
    "ToolGateway", "Decision", "ClassifiedGateway",
    "BashASTAnalyzer", "BashASTResult",
    "SecurityHardening", "SecurityCheckResult",
]
__version__ = "3.0.0"
