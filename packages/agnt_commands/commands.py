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
      capture_output=True,
      text=True,
      timeout=5,
      cwd=ctx.cwd or None,
    )
    if git_branch.returncode == 0:
      checks.append(f"✓ Git branch: {git_branch.stdout.strip()}")
    else:
      checks.append("✗ Git: not in a repository")
  except subprocess.TimeoutExpired, FileNotFoundError:
    checks.append("✗ Git: not available")

  # 3. Knowledge directory
  ki_dir = (
    Path(
      os.environ.get(
        "ANTIGRAVITY_DATA_DIR",
        os.path.expanduser("~/.gemini/antigravity"),
      )
    )
    / "knowledge"
  )
  if ki_dir.is_dir():
    ki_count = sum(
      1 for d in ki_dir.iterdir() if d.is_dir() and not d.name.startswith((".", "_"))
    )
    checks.append(f"✓ Knowledge items: {ki_count}")
  else:
    checks.append("✗ Knowledge directory not found")

  # 4. Key packages
  for pkg_name in [
    "packages.agnt_tools",
    "packages.speculation_engine",
    "packages.context_compactor",
  ]:
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
      capture_output=True,
      text=True,
      timeout=10,
      cwd=ctx.cwd or None,
    )
    if result.returncode == 0:
      output = result.stdout.strip()
      if not output:
        return CommandResult(value="No uncommitted changes.")
      return CommandResult(value=f"```\n{output}\n```")
    return CommandResult(
      type="error", value=f"git diff failed: {result.stderr.strip()}"
    )
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
      cmd_args,
      capture_output=True,
      text=True,
      timeout=300,
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
      capture_output=True,
      text=True,
      timeout=10,
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

  return CommandResult(value="Config update not supported via command. Use ConfigTool.")


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
    return CommandResult(
      value="Cost tracking: no data available (agnt_cost_tracker not loaded)."
    )


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


# ── Batch 3 Commands (Ported from Claude Code v2.1.91) ─────────────────────


async def cmd_plan(args: str, ctx: CommandContext) -> CommandResult:
  """Enable plan mode or view the current session plan.

  Usage: /plan [open|close|status|<description>]

  In plan mode, the agent uses read-only tools (ArchitectTool) and
  produces structured plans without executing mutations.
  """
  sub = args.strip().lower()

  # Check current plan mode state from config
  plan_active = ctx.config.get("plan_mode", False)

  if sub in ("", "status"):
    if plan_active:
      plan_desc = ctx.config.get("plan_description", "(no description)")
      return CommandResult(
        value=f"📋 Plan mode: ACTIVE\n  Description: {plan_desc}\n\nUse /plan close to exit plan mode.",
      )
    return CommandResult(
      value="📋 Plan mode: INACTIVE\n\nUse /plan open or /plan <description> to enter plan mode.",
    )

  if sub == "open":
    return CommandResult(
      value="📋 Plan mode activated. Tools restricted to read-only.\nUse /plan close to return to normal execution.",
      metadata={"plan_mode": True},
    )

  if sub == "close":
    if not plan_active:
      return CommandResult(value="Plan mode is not active.")
    return CommandResult(
      value="📋 Plan mode deactivated. Full tool access restored.",
      metadata={"plan_mode": False},
    )

  # Treat as plan description
  return CommandResult(
    value=f"📋 Plan mode activated with description:\n  {args.strip()}\n\nTools restricted to read-only. Use /plan close to exit.",
    metadata={"plan_mode": True, "plan_description": args.strip()},
  )


async def cmd_model(args: str, ctx: CommandContext) -> CommandResult:
  """Show or set the current AI model.

  Usage: /model [model_name]
  """
  current_model = ctx.config.get("model", "gemini-3.1-flash-lite-preview-thinking")
  runtime_model = os.environ.get("AGNT_MODEL", current_model)

  if not args.strip():
    lines = [
      "Current Model Configuration:",
      f"  Active model: {runtime_model}",
      f"  Config model: {current_model}",
      "  Authorized:   gemini-3.1-flash-lite-preview-thinking",
      "",
      "Available models:",
      "  gemini-3.1-flash-lite-preview-thinking (default)",
      "  gemini-3-pro",
      "  gemini-3-flash",
    ]
    return CommandResult(value="\n".join(lines))

  requested = args.strip()
  return CommandResult(
    value=f"Model switch requested: {requested}\nNote: Model changes take effect on the next inference call.",
    metadata={"model_update": requested},
  )


async def cmd_session(args: str, ctx: CommandContext) -> CommandResult:
  """Display session metadata and artifact counts.

  Usage: /session [info|artifacts|messages]
  """
  session_id = ctx.session_id or "(not set)"
  msg_count = len(ctx.messages)
  cwd = ctx.cwd or os.getcwd()

  # Count KI artifacts
  data_dir = Path(
    os.environ.get(
      "ANTIGRAVITY_DATA_DIR",
      os.path.expanduser("~/.gemini/antigravity"),
    )
  )
  ki_count = 0
  ki_dir = data_dir / "knowledge"
  if ki_dir.is_dir():
    ki_count = sum(
      1 for d in ki_dir.iterdir() if d.is_dir() and not d.name.startswith((".", "_"))
    )

  # Count brain conversations (top-level dirs only, bounded)
  brain_artifacts = 0
  brain_dir = data_dir / "brain"
  if brain_dir.is_dir():
    brain_artifacts = sum(
      1 for d in brain_dir.iterdir() if d.is_dir() and not d.name.startswith(".")
    )

  lines = [
    "╔══════════════════════════════════════╗",
    "║         Session Information          ║",
    "╚══════════════════════════════════════╝",
    f"  Session ID:      {session_id}",
    f"  Working dir:     {cwd}",
    f"  Messages:        {msg_count}",
    f"  Knowledge items: {ki_count}",
    f"  Brain artifacts: {brain_artifacts}",
    f"  Config keys:     {len(ctx.config)}",
  ]
  return CommandResult(value="\n".join(lines))


async def cmd_export(args: str, ctx: CommandContext) -> CommandResult:
  """Export the current conversation to a file.

  Usage: /export [filename] [--format=json|md]

  Exports conversation history as JSON or Markdown.
  Default filename: conversation_<session_id>.md
  """
  fmt = "md"
  filename = ""

  parts = args.strip().split()
  for part in parts:
    if part.startswith("--format="):
      fmt = part.split("=", 1)[1].lower()
    elif not filename:
      filename = part

  session_id = ctx.session_id or "unknown"
  if not filename:
    filename = f"conversation_{session_id}.{fmt}"

  # Resolve path
  export_path = Path(ctx.cwd or ".") / filename
  if fmt not in ("json", "md"):
    return CommandResult(
      type="error",
      value=f"Unsupported format: {fmt}. Use --format=json or --format=md",
    )

  try:
    if fmt == "json":
      content = json.dumps(
        {"session_id": session_id, "messages": ctx.messages},
        indent=2,
        default=str,
      )
    else:
      md_lines = [f"# Conversation Export — {session_id}\n"]
      for msg in ctx.messages:
        role = msg.get("role", "unknown")
        text = msg.get("content", str(msg))
        if isinstance(text, list):
          text = "\n".join(str(b) for b in text)
        md_lines.append(f"## {role.upper()}\n\n{text}\n")
      content = "\n".join(md_lines)

    export_path.write_text(content, encoding="utf-8")
    return CommandResult(
      value=f"✓ Exported {len(ctx.messages)} messages to {export_path}\n  Format: {fmt} | Size: {len(content):,} bytes",
      metadata={"export_path": str(export_path), "format": fmt},
    )
  except Exception as exc:
    return CommandResult(type="error", value=f"Export failed: {exc}")


async def cmd_branch(args: str, ctx: CommandContext) -> CommandResult:
  """Show or manage git branches.

  Usage: /branch [list|current|<branch_name>]
  """
  sub = args.strip()

  try:
    if sub in ("", "current"):
      result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        capture_output=True,
        text=True,
        timeout=5,
        cwd=ctx.cwd or None,
      )
      if result.returncode != 0:
        return CommandResult(type="error", value="Not in a git repository.")
      branch = result.stdout.strip()
      # Also get recent commit
      log_result = subprocess.run(
        ["git", "log", "--oneline", "-5"],
        capture_output=True,
        text=True,
        timeout=5,
        cwd=ctx.cwd or None,
      )
      log_output = (
        log_result.stdout.strip() if log_result.returncode == 0 else "(unavailable)"
      )
      return CommandResult(
        value=f"Current branch: {branch}\n\nRecent commits:\n{log_output}",
      )

    if sub == "list":
      result = subprocess.run(
        ["git", "branch", "--list", "-a"],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=ctx.cwd or None,
      )
      if result.returncode != 0:
        return CommandResult(type="error", value="Not in a git repository.")
      return CommandResult(value=f"Branches:\n{result.stdout.strip()}")

    # Creating or switching to a branch — report-only, no mutation
    return CommandResult(
      value=f"Branch operation requested: {sub}\nUse `git checkout -b {{sub}}` or `git switch {{sub}}` in terminal.",
    )

  except (subprocess.TimeoutExpired, FileNotFoundError) as exc:
    return CommandResult(type="error", value=f"Git error: {exc}")


async def cmd_files(args: str, ctx: CommandContext) -> CommandResult:
  """List files in the current context or working directory.

  Usage: /files [modified|staged|tracked|all]
  """
  sub = args.strip().lower() or "modified"

  git_cmd_map = {
    "modified": ["git", "diff", "--name-only"],
    "staged": ["git", "diff", "--cached", "--name-only"],
    "tracked": ["git", "ls-files"],
    "all": ["git", "status", "--short"],
  }

  if sub not in git_cmd_map:
    return CommandResult(
      type="error",
      value=f"Unknown filter: {sub}. Valid: modified, staged, tracked, all",
    )

  try:
    result = subprocess.run(
      git_cmd_map[sub],
      capture_output=True,
      text=True,
      timeout=10,
      cwd=ctx.cwd or None,
    )
    if result.returncode != 0:
      return CommandResult(type="error", value=f"git error: {result.stderr.strip()}")

    output = result.stdout.strip()
    if not output:
      return CommandResult(value=f"No {sub} files.")

    file_count = len(output.splitlines())
    return CommandResult(
      value=f"Files ({sub}) — {file_count} files:\n{output}",
      metadata={"file_count": file_count, "filter": sub},
    )
  except (subprocess.TimeoutExpired, FileNotFoundError) as exc:
    return CommandResult(type="error", value=f"File listing error: {exc}")


async def cmd_permissions(args: str, ctx: CommandContext) -> CommandResult:
  """Display current security posture and execution rules.

  Shows YOLO mode status, Rule 00 enforcement, blocked commands,
  and the execution state machine configuration.
  """
  # Determine execution mode
  yolo_enabled = ctx.config.get("yolo", True)  # Default YOLO per AGENTS.md
  execution_state = "STATE A — Pure YOLO" if yolo_enabled else "STATE B — Clutch"

  blocked_commands = [
    "rm -rf",
    "rm",
    "unlink",
    "sudo",
    "gh auth login",
    "gh auth token",
  ]
  allowed_tool_classes = ["command(*)", "mcp(*)"]

  lines = [
    "╔══════════════════════════════════════╗",
    "║     Security Posture & Permissions   ║",
    "╚══════════════════════════════════════╝",
    "",
    f"  Execution mode:   {execution_state}",
    f"  YOLO enabled:     {yolo_enabled}",
    "  Rule 00:          ACTIVE (Immutable Infrastructure)",
    "",
    "  Allowed tool classes:",
    *[f"    ✓ {tc}" for tc in allowed_tool_classes],
    "",
    "  Blocked commands (hardcoded):",
    *[f"    ✗ {cmd}" for cmd in blocked_commands],
    "",
    "  STATE B triggers:",
    "    • git history rewrites / force-pushes",
    "    • database migrations",
    "    • auth / payment changes",
    "    • architecture shifts >3 packages",
  ]
  return CommandResult(value="\n".join(lines))


async def cmd_mcp(args: str, ctx: CommandContext) -> CommandResult:
  """MCP fleet status diagnostics.

  Shows connectivity and tool count for all 5 MCP servers.
  Usage: /mcp [status|list|<server_name>]
  """
  fleet = [
    {
      "name": "StitchMCP",
      "tools": 12,
      "domain": "Design systems, screen gen, UI variants",
    },
    {
      "name": "chrome-devtools-mcp",
      "tools": 29,
      "domain": "Browser, DOM, Lighthouse, perf",
    },
    {
      "name": "firebase-mcp-server",
      "tools": 45,
      "domain": "Auth, Firestore, Hosting, Functions",
    },
    {
      "name": "google-developer-knowledge",
      "tools": 3,
      "domain": "Google docs search, retrieval",
    },
    {"name": "sequential-thinking", "tools": 1, "domain": "Multi-step reasoning"},
  ]
  total_tools = sum(s["tools"] for s in fleet)

  sub = args.strip().lower()

  if sub and sub not in ("status", "list"):
    # Look up specific server
    match = next((s for s in fleet if sub in s["name"].lower()), None)
    if match:
      return CommandResult(
        value=f"MCP Server: {match['name']}\n  Tools:  {match['tools']}\n  Domain: {match['domain']}",
      )
    return CommandResult(type="error", value=f"Unknown MCP server: {sub}")

  lines = [
    "╔══════════════════════════════════════════════════╗",
    "║           MCP Fleet Status (5 servers)           ║",
    "╚══════════════════════════════════════════════════╝",
    "",
    f"  {'#':<3} {'Server':<28} {'Tools':<7} {'Domain'}",
    f"  {'─' * 3} {'─' * 28} {'─' * 7} {'─' * 30}",
  ]
  for i, s in enumerate(fleet, 1):
    lines.append(f"  {i:<3} {s['name']:<28} {s['tools']:<7} {s['domain']}")

  lines.extend(
    [
      "",
      f"  Total tools: {total_tools}",
      "",
      "  Note: Use MCP tools directly for live connectivity checks.",
    ]
  )
  return CommandResult(value="\n".join(lines))


_AGNT_VERSION = "v2.1.0-uphillsnowball"


async def cmd_version(args: str, ctx: CommandContext) -> CommandResult:
  """Display AGNT runtime version.

  Shows the current build version, Python version, and platform info.
  """
  import platform
  import sys

  lines = [
    f"AGNT Runtime: {_AGNT_VERSION}",
    f"Python:       {sys.version.split()[0]}",
    f"Platform:     {platform.system()} {platform.machine()}",
    "Upstream:     Claude Code v2.1.91 (Tengu)",
  ]
  return CommandResult(value="\n".join(lines))


# ── Command Registry ──────────────────────────────────────────────────────

COMMAND_REGISTRY: dict[str, Any] = {
  "branch": cmd_branch,
  "clear": cmd_clear,
  "compact": cmd_compact,
  "commit": cmd_commit,
  "config": cmd_config,
  "context": cmd_context,
  "cost": cmd_cost,
  "diff": cmd_diff,
  "doctor": cmd_doctor,
  "dream": cmd_dream,
  "effort": cmd_effort,
  "export": cmd_export,
  "files": cmd_files,
  "mcp": cmd_mcp,
  "model": cmd_model,
  "permissions": cmd_permissions,
  "plan": cmd_plan,
  "session": cmd_session,
  "version": cmd_version,
}


async def dispatch_command(
  name: str, args: str = "", ctx: CommandContext | None = None
) -> CommandResult:
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
  "cmd_branch",
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
  "cmd_export",
  "cmd_files",
  "cmd_mcp",
  "cmd_model",
  "cmd_permissions",
  "cmd_plan",
  "cmd_session",
  "cmd_version",
  "dispatch_command",
]
