# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""CLI Diagnostics — Tree-based diagnostic output for AGNT commands.

Integrates agnt_utils.treeify into the CLI diagnostic subsystem.
Provides pre-built diagnostic renderers for common operational views:
  - Package status trees
  - MCP server fleet status
  - Test result summaries
  - Telemetry pipeline health

Usage:
    from cli_diagnostics import render_package_tree, render_mcp_status

    print(render_package_tree())
    print(render_mcp_status())
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from agnt_utils.treeify import treeify


def render_package_tree(
    packages_dir: str | Path | None = None,
    *,
    show_sizes: bool = True,
) -> str:
    """Render the packages directory as a CLI tree.

    Args:
        packages_dir: Path to the packages/ directory.
        show_sizes: Whether to show file counts per package.

    Returns:
        A tree string showing all packages and their module counts.
    """
    if packages_dir is None:
        packages_dir = Path(__file__).parent.parent / "packages"

    packages_dir = Path(packages_dir)
    if not packages_dir.exists():
        return "(packages directory not found)"

    tree: dict[str, Any] = {}
    for child in sorted(packages_dir.iterdir()):
        if child.is_dir() and not child.name.startswith((".", "__")):
            py_files = list(child.glob("*.py"))
            if show_sizes:
                tree[child.name] = f"{len(py_files)} modules"
            else:
                tree[child.name] = ""

    return "📦 Packages\n" + treeify(tree, show_values=show_sizes)


def render_mcp_status(
    servers: dict[str, dict[str, Any]] | None = None,
) -> str:
    """Render MCP fleet status as a CLI tree.

    Args:
        servers: Dict of server_name → {status, tools_count, domain}.
            If None, returns a template.

    Returns:
        A tree string showing MCP fleet health.
    """
    if servers is None:
        servers = {
            "StitchMCP": {"status": "⬜ unknown", "tools": 12, "domain": "Design"},
            "chrome-devtools-mcp": {"status": "⬜ unknown", "tools": 29, "domain": "Browser"},
            "firebase-mcp-server": {"status": "⬜ unknown", "tools": 45, "domain": "Firebase"},
            "google-developer-knowledge": {"status": "⬜ unknown", "tools": 3, "domain": "Docs"},
            "sequential-thinking": {"status": "⬜ unknown", "tools": 1, "domain": "Reasoning"},
        }

    tree: dict[str, Any] = {}
    for name, info in servers.items():
        subtree: dict[str, str] = {
            "Status": info.get("status", "unknown"),
            "Tools": str(info.get("tools", 0)),
            "Domain": info.get("domain", ""),
        }
        tree[name] = subtree

    return "🔌 MCP Fleet\n" + treeify(tree)


def render_test_summary(
    results: dict[str, Any] | None = None,
) -> str:
    """Render test results as a CLI tree.

    Args:
        results: Dict with keys: passed, failed, skipped, xfailed, duration.

    Returns:
        A tree string showing test summary.
    """
    if results is None:
        results = {
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "xfailed": 0,
            "duration_s": 0.0,
        }

    status = "✅" if results.get("failed", 0) == 0 else "❌"
    tree: dict[str, str] = {
        "Passed": f"✅ {results.get('passed', 0)}",
        "Failed": f"{'❌' if results.get('failed', 0) > 0 else '✅'} {results.get('failed', 0)}",
        "Skipped": f"⏭️  {results.get('skipped', 0)}",
        "XFailed": f"⚠️  {results.get('xfailed', 0)}",
        "Duration": f"⏱️  {results.get('duration_s', 0):.1f}s",
    }

    return f"{status} Test Results\n" + treeify(tree)


def render_telemetry_health(
    metrics: dict[str, Any] | None = None,
) -> str:
    """Render telemetry pipeline health as a CLI tree.

    Args:
        metrics: Dict with keys like events_emitted, buffer_size, sink_path.

    Returns:
        A tree string showing telemetry pipeline health.
    """
    if metrics is None:
        metrics = {
            "events_emitted": 0,
            "buffer_size": 0,
            "sink_path": ".beads/telemetry.jsonl",
            "enabled": True,
        }

    tree: dict[str, str] = {
        "Events Emitted": str(metrics.get("events_emitted", 0)),
        "Buffer Size": str(metrics.get("buffer_size", 0)),
        "Sink Path": metrics.get("sink_path", "unknown"),
        "Enabled": "✅ Yes" if metrics.get("enabled") else "❌ No",
    }

    return "📡 Telemetry Pipeline\n" + treeify(tree)


def render_diagnostic_report(
    *,
    packages_dir: str | Path | None = None,
    mcp_servers: dict[str, dict[str, Any]] | None = None,
    test_results: dict[str, Any] | None = None,
    telemetry_metrics: dict[str, Any] | None = None,
) -> str:
    """Render a full diagnostic report combining all views.

    Returns:
        A multi-section diagnostic report.
    """
    sections = [
        render_package_tree(packages_dir),
        "",
        render_mcp_status(mcp_servers),
        "",
        render_test_summary(test_results),
        "",
        render_telemetry_health(telemetry_metrics),
    ]
    return "\n".join(sections)
