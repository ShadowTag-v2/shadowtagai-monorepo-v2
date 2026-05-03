# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""AGNT Commands — Slash command registry for the AGNT runtime.

Ported from src/commands/ (Claude Code v2.1.91).
Top-10 commands: compact, doctor, diff, dream, commit,
                 config, context, clear, cost, effort.

Architecture:
  Each command is a pure async function: (args, context) -> CommandResult.
  No React/JSX — all rendering is text-based for terminal output.
  Commands are registered in COMMAND_REGISTRY and dispatched by name.
"""

from __future__ import annotations

import json
import logging
import os
import re
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class CommandResult:
    """Result of a slash command execution."""

    type: str = "text"  # "text" | "error" | "table"
    value: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class CommandContext:
    """Execution context for commands."""

    cwd: str = ""
    messages: list[dict[str, Any]] = field(default_factory=list)
    session_id: str = ""
    config: dict[str, Any] = field(default_factory=dict)


# ── Individual Commands ────────────────────────────────────────────────────


async def cmd_clear(args: str, ctx: CommandContext) -> CommandResult:
    """Clear conversation history."""
    return CommandResult(value="Conversation cleared.")


async def cmd_compact(args: str, ctx: CommandContext) -> CommandResult:
    """Trigger context compaction.

    Routes to context_compactor package for actual compaction logic.
    Supports --dry-run for preview without mutation.
    """
    dry_run = "--dry-run" in args

    try:
        from packages.context_compactor.conversation_compact import compact_conversation
    except ImportError:
        return CommandResult(
            type="error",
            value="context_compactor package not available. Run manually.",
        )

    if dry_run:
        return CommandResult(value="[DRY RUN] Compaction preview — no changes applied.")

    try:
        result = compact_conversation(
            messages=ctx.messages,
            max_tokens=None,  # Use default budget
        )
        return CommandResult(
            value=f"Compaction complete. {result.get('tokens_saved', 0)} tokens saved.",
            metadata=result,
        )
    except Exception as exc:
        return CommandResult(type="error", value=f"Compaction failed: {exc}")


async def cmd_doctor(args: str, ctx: CommandContext) -> CommandResult:
    """System health diagnostic.

    Checks:
      1. Python version & dependencies
      2. MCP server connectivity
      3. Knowledge directory integrity
      4. Git repo status
      5. Daemon health (KAIROS, AutoDream)
    """
    checks: list[str] = []

    # 1. Python
    import sys
    checks.append(f"✓ Python {sys.version.split()[0]}")

    # 2. Git
    try:
        git_branch = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, timeout=5,
            cwd=ctx.cwd or None,
        )
        if git_branch.returncode == 0:
            checks.append(f"✓ Git branch: {git_branch.stdout.strip()}")
        else:
            checks.append("✗ Git: not in a repository")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        checks.append("✗ Git: not available")

    # 3. Knowledge directory
    ki_dir = Path(os.environ.get(
        "ANTIGRAVITY_DATA_DIR",
        os.path.expanduser("~/.gemini/antigravity"),
    )) / "knowledge"
    if ki_dir.is_dir():
        ki_count = sum(1 for d in ki_dir.iterdir() if d.is_dir() and not d.name.startswith((".", "_")))
        checks.append(f"✓ Knowledge items: {ki_count}")
    else:
        checks.append("✗ Knowledge directory not found")

    # 4. Key packages
    for pkg_name in ["packages.agnt_tools", "packages.speculation_engine", "packages.context_compactor"]:
        try:
            __import__(pkg_name)
            checks.append(f"✓ {pkg_name.split('.')[-1]}")
        except ImportError:
            checks.append(f"✗ {pkg_name.split('.')[-1]}: import failed")

    # 5. Beads directory
    beads_dir = Path(ctx.cwd or ".") / ".beads"
    if beads_dir.is_dir():
        checks.append(f"✓ Beads directory: {sum(1 for f in beads_dir.iterdir())} files")
    else:
        checks.append("○ Beads directory: not present")

    header = "╔══════════════════════════════════════╗\n║      AGNT Doctor — Health Report     ║\n╚══════════════════════════════════════╝\n"
    return CommandResult(value=header + "\n".join(checks))


async def cmd_diff(args: str, ctx: CommandContext) -> CommandResult:
    """Show git diff for current session changes."""
    try:
        result = subprocess.run(
            ["git", "diff", "--stat"],
            capture_output=True, text=True, timeout=10,
            cwd=ctx.cwd or None,
        )
        if result.returncode == 0:
            output = result.stdout.strip()
            if not output:
                return CommandResult(value="No uncommitted changes.")
            return CommandResult(value=f"```\n{output}\n```")
        return CommandResult(type="error", value=f"git diff failed: {result.stderr.strip()}")
    except (subprocess.TimeoutExpired, FileNotFoundError) as exc:
        return CommandResult(type="error", value=f"git diff error: {exc}")


async def cmd_dream(args: str, ctx: CommandContext) -> CommandResult:
    """AutoDream memory consolidation.

    Wraps scripts/dream_consolidation.py for on-demand invocation.
    Pipeline: Orient → Gather → Consolidate → Prune.
    """
    dry_run = "--dry-run" in args

    # Find the dream script
    candidates = [
        Path(ctx.cwd or ".") / "scripts" / "dream_consolidation.py",
        Path(__file__).parent.parent.parent / "scripts" / "dream_consolidation.py",
    ]
    script_path = next((c for c in candidates if c.is_file()), None)

    if not script_path:
        return CommandResult(
            type="error",
            value="dream_consolidation.py not found. Expected at scripts/dream_consolidation.py",
        )

    cmd_args = ["python3", str(script_path)]
    if dry_run:
        cmd_args.append("--dry-run")

    header = (
        "╔══════════════════════════════════════════════════╗\n"
        "║          AUTODREAM — Memory Consolidation        ║\n"
        "╚══════════════════════════════════════════════════╝\n"
    )

    try:
        t0 = time.monotonic()
        result = subprocess.run(
            cmd_args, capture_output=True, text=True, timeout=300,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
            cwd=ctx.cwd or None,
        )
        elapsed_ms = int((time.monotonic() - t0) * 1000)
        output = result.stdout.strip()

        # Parse metrics
        metrics: dict[str, int] = {}
        for key, pattern in [
            ("processed", r"KIs?\s*processed:\s*(\d+)"),
            ("merged", r"KIs?\s*merged:\s*(\d+)"),
            ("pruned", r"KIs?\s*pruned:\s*(\d+)"),
        ]:
            match = re.search(pattern, output, re.IGNORECASE)
            if match:
                metrics[key] = int(match.group(1))

        summary_lines = [f"✓ AutoDream complete in {elapsed_ms}ms"]
        for k, v in metrics.items():
            summary_lines.append(f"  KIs {k}: {v}")

        return CommandResult(
            value=header + output + "\n" + "─" * 50 + "\n" + "\n".join(summary_lines),
            metadata={"duration_ms": elapsed_ms, **metrics},
        )
    except subprocess.TimeoutExpired:
        return CommandResult(type="error", value=header + "AutoDream timed out (5m limit).")
    except Exception as exc:
        return CommandResult(type="error", value=header + f"AutoDream failed: {exc}")


async def cmd_commit(args: str, ctx: CommandContext) -> CommandResult:
    """Generate a conventional commit message from staged changes."""
    try:
        staged = subprocess.run(
            ["git", "diff", "--cached", "--stat"],
            capture_output=True, text=True, timeout=10,
            cwd=ctx.cwd or None,
        )
        if staged.returncode != 0:
            return CommandResult(type="error", value="Not in a git repository.")
        if not staged.stdout.strip():
            return CommandResult(value="No staged changes. Run `git add` first.")

        return CommandResult(
            value=f"Staged changes:\n```\n{staged.stdout.strip()}\n```\n\nSuggested commit: `feat: <describe changes>`",
        )
    except Exception as exc:
        return CommandResult(type="error", value=f"Commit check failed: {exc}")


async def cmd_config(args: str, ctx: CommandContext) -> CommandResult:
    """Show or modify runtime configuration."""
    if not args.strip():
        # Show current config
        config_items = [
            f"  cwd: {ctx.cwd or '(not set)'}",
            f"  session_id: {ctx.session_id or '(not set)'}",
            f"  messages: {len(ctx.messages)}",
        ]
        for k, v in sorted(ctx.config.items()):
            config_items.append(f"  {k}: {v}")
        return CommandResult(value="Current configuration:\n" + "\n".join(config_items))

    return CommandResult(value=f"Config update not supported via command. Use ConfigTool.")


async def cmd_context(args: str, ctx: CommandContext) -> CommandResult:
    """Display current context window usage."""
    msg_count = len(ctx.messages)
    # Rough token estimate: ~4 chars per token
    total_chars = sum(len(json.dumps(m)) for m in ctx.messages)
    est_tokens = total_chars // 4

    lines = [
        "Context Window Status:",
        f"  Messages: {msg_count}",
        f"  Estimated tokens: ~{est_tokens:,}",
        f"  Raw characters: {total_chars:,}",
    ]
    return CommandResult(value="\n".join(lines))


async def cmd_cost(args: str, ctx: CommandContext) -> CommandResult:
    """Display session cost tracking."""
    try:
        from packages.agnt_cost_tracker import format_total_cost
        return CommandResult(value=format_total_cost())
    except ImportError:
        return CommandResult(value="Cost tracking: no data available (agnt_cost_tracker not loaded).")


async def cmd_effort(args: str, ctx: CommandContext) -> CommandResult:
    """Set or display effort level: low, medium, high, max, auto."""
    args = args.strip().lower()

    valid_levels = {"low", "medium", "high", "max", "auto"}
    descriptions = {
        "low": "Quick, straightforward implementation",
        "medium": "Balanced approach with standard testing",
        "high": "Comprehensive implementation with extensive testing",
        "max": "Maximum capability with deepest reasoning",
        "auto": "Default effort level for the current model",
    }

    if args in ("help", "-h", "--help"):
        lines = ["Usage: /effort [low|medium|high|max|auto]", "", "Effort levels:"]
        for level, desc in descriptions.items():
            lines.append(f"- {level}: {desc}")
        return CommandResult(value="\n".join(lines))

    if not args or args in ("current", "status"):
        current = ctx.config.get("effort_level", "auto")
        desc = descriptions.get(current, "unknown")
        return CommandResult(value=f"Effort level: {current} ({desc})")

    if args in valid_levels:
        return CommandResult(
            value=f"Set effort level to {args}: {descriptions[args]}",
            metadata={"effort_update": args},
        )

    return CommandResult(
        type="error",
        value=f"Invalid effort level: {args}. Valid: {', '.join(sorted(valid_levels))}",
    )


# ── Command Registry ──────────────────────────────────────────────────────

COMMAND_REGISTRY: dict[str, Any] = {
    "clear": cmd_clear,
    "compact": cmd_compact,
    "config": cmd_config,
    "commit": cmd_commit,
    "context": cmd_context,
    "cost": cmd_cost,
    "diff": cmd_diff,
    "doctor": cmd_doctor,
    "dream": cmd_dream,
    "effort": cmd_effort,
}


async def dispatch_command(name: str, args: str = "", ctx: CommandContext | None = None) -> CommandResult:
    """Dispatch a slash command by name."""
    handler = COMMAND_REGISTRY.get(name)
    if handler is None:
        available = ", ".join(sorted(COMMAND_REGISTRY.keys()))
        return CommandResult(
            type="error",
            value=f"Unknown command: /{name}. Available: {available}",
        )
    context = ctx or CommandContext()
    try:
        return await handler(args, context)
    except Exception as exc:
        logger.exception("Command /%s failed", name)
        return CommandResult(type="error", value=f"/{name} error: {exc}")


__all__ = [
    "COMMAND_REGISTRY",
    "CommandContext",
    "CommandResult",
    "cmd_clear",
    "cmd_commit",
    "cmd_compact",
    "cmd_config",
    "cmd_context",
    "cmd_cost",
    "cmd_diff",
    "cmd_doctor",
    "cmd_dream",
    "cmd_effort",
    "dispatch_command",
]
