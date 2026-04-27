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

__all__ = ["ToolGateway", "Decision"]
__version__ = "1.0.0"
