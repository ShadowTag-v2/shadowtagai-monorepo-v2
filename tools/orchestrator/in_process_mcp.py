"""Native MCP Bypass — in_process_mcp.py

JSON-RPC IPC overhead deprecated for internal Python tools.
This module wraps tool functions for in-process execution,
bypassing the stdio/SSE transport layer when the tool
implementation is available locally.

Use case: Memory, filesystem, and orchestrator tools that
don't need network transport.
"""

from __future__ import annotations

import importlib
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone, UTC
from typing import Any
from collections.abc import Callable


@dataclass
class ToolResult:
    """Result from an in-process tool execution."""

    tool_name: str
    success: bool
    result: Any = None
    error: str | None = None
    elapsed_ms: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


# Registry of in-process tool implementations
_TOOL_REGISTRY: dict[str, Callable[..., Any]] = {}


def register_tool(name: str, func: Callable[..., Any]) -> None:
    """Register a tool function for in-process execution.

    Args:
        name: Tool name (e.g., "memory_index", "compact_context").
        func: The callable that implements the tool.
    """
    _TOOL_REGISTRY[name] = func


def execute_tool(name: str, **kwargs: Any) -> ToolResult:
    """Execute a registered tool in-process (no IPC overhead).

    Args:
        name: Registered tool name.
        **kwargs: Tool parameters.

    Returns:
        ToolResult with success/failure and timing.
    """
    func = _TOOL_REGISTRY.get(name)
    if func is None:
        return ToolResult(
            tool_name=name,
            success=False,
            error=f"Tool '{name}' not registered. Available: {list(_TOOL_REGISTRY.keys())}",
        )

    start = time.monotonic()
    try:
        result = func(**kwargs)
        elapsed = (time.monotonic() - start) * 1000
        return ToolResult(
            tool_name=name,
            success=True,
            result=result,
            elapsed_ms=round(elapsed, 2),
        )
    except Exception as exc:
        elapsed = (time.monotonic() - start) * 1000
        return ToolResult(
            tool_name=name,
            success=False,
            error=str(exc),
            elapsed_ms=round(elapsed, 2),
        )


def auto_register_orchestrator_tools() -> list[str]:
    """Auto-discover and register all orchestrator tools.

    Scans the tools/orchestrator/ directory for modules with
    callable entry points.
    """
    registered: list[str] = []
    tool_modules = {
        "memory_index": ("tools.orchestrator.memory_indexer", "index_file_context"),
        "memory_get": ("tools.orchestrator.memory_indexer", "get_hot_context"),
        "memory_clear": ("tools.orchestrator.memory_indexer", "clear_hot_context"),
        "compact_stale": (
            "tools.orchestrator.compaction_engine",
            "compact_stale_tool_results",
        ),
        "compact_auto": ("tools.orchestrator.compaction_engine", "auto_compact"),
        "compact_breaker_status": (
            "tools.orchestrator.compaction_engine",
            "get_breaker_status",
        ),
        "fork_plan": ("tools.orchestrator.session_forking", "plan_forks"),
        "fork_start": ("tools.orchestrator.session_forking", "start_fork"),
        "fork_complete": ("tools.orchestrator.session_forking", "complete_fork"),
    }

    for tool_name, (module_path, func_name) in tool_modules.items():
        try:
            module = importlib.import_module(module_path)
            func = getattr(module, func_name)
            register_tool(tool_name, func)
            registered.append(tool_name)
        except (ImportError, AttributeError) as exc:
            # Log but don't fail — graceful degradation
            register_tool(
                tool_name,
                lambda _exc=str(exc), **kw: f"UNAVAILABLE: {_exc}",
            )

    return registered


def list_tools() -> dict[str, str]:
    """List all registered tools with their callable info."""
    return {name: f"{func.__module__}.{func.__qualname__}" if hasattr(func, "__module__") else str(func) for name, func in _TOOL_REGISTRY.items()}


if __name__ == "__main__":
    # Self-test
    registered = auto_register_orchestrator_tools()
    print(f"Registered {len(registered)} tools: {registered}")
    print(f"Tool list: {list_tools()}")

    # Test in-process execution
    result = execute_tool(
        "memory_index",
        file_path="test.py",
        start_line=1,
        end_line=10,
        summary="Test file",
    )
    print(f"Execution result: {result}")
