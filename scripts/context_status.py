#!/usr/bin/env python3
"""ContextVisualization CLI — sovereign context window status view.

Renders a terminal-friendly dashboard of the current context budget,
token allocation breakdown, and compaction pipeline health.

Usage:
    python scripts/context_status.py                   # Full dashboard
    python scripts/context_status.py --model gemini-3.1-pro  # Override model
    python scripts/context_status.py --json             # Machine-readable
    python scripts/context_status.py --compact           # Compact one-liner

Ported from: Claude Code ContextVisualization.tsx + utils/analyzeContext.ts
Doctrine ref: Context Budget Discipline skill
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

# Ensure packages are importable from repo root
REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))


def _load_heartbeat() -> dict:
    """Read the latest KAIROS heartbeat for runtime context."""
    hb_path = REPO_ROOT / ".beads" / "kairos_heartbeat.json"
    if hb_path.exists():
        try:
            return json.loads(hb_path.read_text())
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def _format_tokens(n: int) -> str:
    """Human-readable token count."""
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)


def _bar(fraction: float, width: int = 40) -> str:
    """Render a progress bar."""
    filled = int(fraction * width)
    empty = width - filled
    # Color-coded: green < 75%, yellow 75-90%, red > 90%
    if fraction > 0.90:
        color = "\033[91m"  # Red
    elif fraction > 0.75:
        color = "\033[93m"  # Yellow
    else:
        color = "\033[92m"  # Green
    reset = "\033[0m"
    return f"{color}{'█' * filled}{'░' * empty}{reset}"


def render_dashboard(model: str = "gemini-3.1-flash-lite-preview-thinking") -> str:
    """Build the full context status dashboard string."""
    lines: list[str] = []

    try:
        from packages.agnt_utils.context_visualizer import (
            get_context_window_for_model,
            AUTOCOMPACT_BUFFER_TOKENS,
        )

        context_window = get_context_window_for_model(model)
        autocompact_buffer = AUTOCOMPACT_BUFFER_TOKENS
    except ImportError:
        context_window = 200_000
        autocompact_buffer = 33_000

    # Load heartbeat for live data
    heartbeat = _load_heartbeat()
    status = heartbeat.get("status", {})

    # ── Header ──
    lines.append("")
    lines.append("\033[1m╔══════════════════════════════════════════════════╗\033[0m")
    lines.append("\033[1m║     🧠  CONTEXT WINDOW STATUS — SOVEREIGN      ║\033[0m")
    lines.append("\033[1m╚══════════════════════════════════════════════════╝\033[0m")
    lines.append("")

    # ── Model & Window ──
    lines.append(f"  \033[1mModel:\033[0m          {model}")
    lines.append(f"  \033[1mContext Window:\033[0m  {_format_tokens(context_window)} tokens")
    lines.append(f"  \033[1mAutocompact:\033[0m    triggers at {_format_tokens(context_window - autocompact_buffer)}")
    lines.append(f"  \033[1mBuffer:\033[0m         {_format_tokens(autocompact_buffer)} reserved")
    lines.append("")

    # ── Token Budget Estimations ──
    lines.append("  \033[1m── Token Budget ──\033[0m")

    # Try to get system prompt size
    prompt_tokens = 0
    try:
        from packages.prompt_assembler import PromptConfig, PromptAssembler
        from packages.token_estimation import estimate_tokens

        config = PromptConfig(cwd=str(REPO_ROOT), model_id=model, is_git_repo=True)
        assembler = PromptAssembler(config)
        prompt_sections = assembler.assemble_sync()
        prompt_text = "\n\n".join(prompt_sections)
        prompt_tokens = estimate_tokens(prompt_text)
    except (ImportError, Exception):
        prompt_tokens = 0

    # Build budget breakdown
    budget_items: list[tuple[str, int, str]] = []

    if prompt_tokens > 0:
        budget_items.append(("System Prompt", prompt_tokens, "static+dynamic"))

    # Estimate tool definitions (rough based on # of tools in MCP config)
    try:
        mcp_config_path = REPO_ROOT / "antigravity-mcp-config.json"
        if mcp_config_path.exists():
            mcp_config = json.loads(mcp_config_path.read_text())
            server_count = len(mcp_config.get("mcpServers", {}))
            tool_tokens_est = server_count * 800  # ~800 tokens per tool def
            budget_items.append(("MCP Tool Defs", tool_tokens_est, f"{server_count} servers"))
    except (json.JSONDecodeError, OSError):
        pass

    budget_items.append(("Autocompact Buffer", autocompact_buffer, "reserved"))

    total_reserved = sum(t for _, t, _ in budget_items)
    available = context_window - total_reserved

    for name, tokens, note in budget_items:
        pct = (tokens / context_window) * 100
        lines.append(f"    {name:<22} {_format_tokens(tokens):>8}  ({pct:4.1f}%)  {note}")

    lines.append(f"    {'─' * 52}")
    lines.append(f"    {'Available for messages':<22} {_format_tokens(available):>8}  ({available / context_window * 100:4.1f}%)")
    lines.append("")

    # ── Utilization Bar ──
    utilization = total_reserved / context_window if context_window > 0 else 0
    lines.append("  \033[1m── Utilization ──\033[0m")
    lines.append(f"    {_bar(utilization)} {utilization * 100:.1f}%")
    lines.append(f"    {_format_tokens(total_reserved)} / {_format_tokens(context_window)}")
    lines.append("")

    # ── KAIROS Health ──
    lines.append("  \033[1m── KAIROS Daemon ──\033[0m")
    if heartbeat:
        ts = heartbeat.get("timestamp", "unknown")
        pid = heartbeat.get("pid", "?")
        lines.append(f"    PID: {pid}  |  Last heartbeat: {ts}")

        # Extract health data from status
        prompt_assembly = status.get("prompt_assembly", "unknown")
        prompt_sections_count = status.get("prompt_sections", "?")
        sleep_guard = "active" if "sleep" not in str(status.get("health", "")).lower() else "N/A"

        lines.append(f"    Prompt Assembly:  {prompt_assembly} ({prompt_sections_count} sections)")
        lines.append(f"    Sleep Guard:     {'🟢 active' if sleep_guard == 'active' else '🔴 inactive'}")
        lines.append(f"    Dream:           {status.get('dream', 'pending')}")
    else:
        lines.append("    ⚠️  No heartbeat found — daemon may not be running")
    lines.append("")

    # ── Prompt Cache Status ──
    lines.append("  \033[1m── Prompt Cache ──\033[0m")
    try:
        from packages.prompt_sections.registry import _SECTION_CACHE

        cached_count = len(_SECTION_CACHE)
        lines.append(f"    Cached sections:  {cached_count}")
        if cached_count > 0:
            for name in list(_SECTION_CACHE.keys())[:10]:
                lines.append(f"      • {name}")
    except (ImportError, Exception):
        lines.append("    Cache inspection unavailable")
    lines.append("")

    # ── Compaction Pipeline ──
    lines.append("  \033[1m── Compaction Pipeline ──\033[0m")
    import importlib.util

    if importlib.util.find_spec("context_compactor") is not None:
        lines.append("    L1: Microcompaction        ✅ available")
        lines.append("    L2: Conversation compact   ✅ available")
        lines.append("    L3: Session memory compact  ✅ available")
        lines.append("    L4: Full pipeline           ✅ available")
    else:
        lines.append("    ⚠️  context_compactor not importable")
    lines.append("")

    # ── IPI Quarantine ──
    lines.append("  \033[1m── IPI Quarantine ──\033[0m")
    quarantine_dir = REPO_ROOT / "vault" / "quarantine"
    if quarantine_dir.exists():
        quarantined = [f for f in quarantine_dir.iterdir() if f.is_file() and f.name != ".gitkeep"]
        lines.append(f"    Files in quarantine: {len(quarantined)}")
    else:
        lines.append("    Quarantine dir: not initialized")
    lines.append("")

    return "\n".join(lines)


def render_compact(model: str = "gemini-3.1-flash-lite-preview-thinking") -> str:
    """One-line compact status."""
    try:
        from packages.agnt_utils.context_visualizer import get_context_window_for_model

        context_window = get_context_window_for_model(model)
    except ImportError:
        context_window = 200_000

    heartbeat = _load_heartbeat()
    status = heartbeat.get("status", {})
    cycle = status.get("cycle", "?")
    assembly = status.get("prompt_assembly", "?")

    return f"[CONTEXT] model={model} window={_format_tokens(context_window)} cycle={cycle} assembly={assembly}"


def render_json(model: str = "gemini-3.1-flash-lite-preview-thinking") -> str:
    """Machine-readable JSON status."""
    try:
        from packages.agnt_utils.context_visualizer import (
            get_context_window_for_model,
            AUTOCOMPACT_BUFFER_TOKENS,
        )

        context_window = get_context_window_for_model(model)
        autocompact_buffer = AUTOCOMPACT_BUFFER_TOKENS
    except ImportError:
        context_window = 200_000
        autocompact_buffer = 33_000

    heartbeat = _load_heartbeat()

    data = {
        "model": model,
        "context_window": context_window,
        "autocompact_buffer": autocompact_buffer,
        "autocompact_threshold": context_window - autocompact_buffer,
        "heartbeat": heartbeat,
    }
    return json.dumps(data, indent=2)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Context Window Status Dashboard",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--model",
        default="gemini-3.1-flash-lite-preview-thinking",
        help="Model identifier for context window resolution",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output machine-readable JSON",
    )
    parser.add_argument(
        "--compact",
        action="store_true",
        help="Output a single-line compact status",
    )
    args = parser.parse_args()

    if args.json_output:
        print(render_json(args.model))
    elif args.compact:
        print(render_compact(args.model))
    else:
        print(render_dashboard(args.model))


if __name__ == "__main__":
    main()
