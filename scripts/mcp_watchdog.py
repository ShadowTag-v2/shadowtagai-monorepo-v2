#!/usr/bin/env python3
"""MCP Watchdog — Native macOS background monitor for MCP server health.

Auto-discovers running MCP processes via `ps` regex matching, then polls every
3 seconds.  When a server drops, it fires a native macOS push notification
(with "Basso" alert sound).  When a new server appears, it fires a "Glass"
chime confirmation.

Designed to run as a VS Code background task (see .vscode/tasks.json).
Zero CPU impact at idle (~0.01% per poll cycle).
"""

from __future__ import annotations

import re
import subprocess
import sys
import time

# ── Process Discovery ────────────────────────────────────────────────────────

# Patterns that positively identify an MCP server process
_MCP_PATTERN = re.compile(
  r"(mcp|modelcontextprotocol|sequential-thinking|firebase-tools\s+mcp)",
  re.IGNORECASE,
)

# Patterns that identify THIS script or other false positives
_EXCLUDE_PATTERN = re.compile(
  r"(mcp_watchdog\.py|grep|rg\s|ps\s+-eo)",
  re.IGNORECASE,
)

_POLL_INTERVAL_SECONDS = 3


def get_mcp_processes() -> dict[str, str]:
  """Return {pid: friendly_name} for all running MCP server processes."""
  try:
    out = subprocess.check_output(
      ["ps", "-eo", "pid,command"],
      stderr=subprocess.DEVNULL,
    ).decode("utf-8", errors="replace")
  except Exception:
    return {}

  procs: dict[str, str] = {}
  for line in out.splitlines():
    if not _MCP_PATTERN.search(line):
      continue
    if _EXCLUDE_PATTERN.search(line):
      continue

    parts = line.strip().split(maxsplit=1)
    if len(parts) != 2:
      continue

    pid, cmd = parts

    # Extract a friendly name from the command string
    name_match = re.search(
      r"([^\s/]+(?:mcp|sequential-thinking)[^\s/]*)",
      cmd,
      re.IGNORECASE,
    )
    name = name_match.group(1) if name_match else "MCP Server"
    procs[pid] = name

  return procs


# ── macOS Notifications ──────────────────────────────────────────────────────


def send_macos_notification(
  title: str,
  message: str,
  sound: str = "Basso",
) -> None:
  """Trigger a native macOS desktop notification via osascript."""
  safe_title = title.replace('"', '\\"')
  safe_msg = message.replace('"', '\\"')
  apple_script = (
    f'display notification "{safe_msg}" with title "{safe_title}" sound name "{sound}"'
  )
  subprocess.run(
    ["osascript", "-e", apple_script],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
  )


# ── Main Loop ────────────────────────────────────────────────────────────────


def main() -> None:
  print("🛡️ Antigravity MCP Watchdog started.", flush=True)

  known_procs = get_mcp_processes()
  print(f"📡 Found {len(known_procs)} running MCP servers.", flush=True)
  for pid, name in sorted(known_procs.items()):
    print(f"   ├─ [PID {pid}] {name}", flush=True)

  while True:
    time.sleep(_POLL_INTERVAL_SECONDS)
    current_procs = get_mcp_processes()

    # 🚨 Detect crashed / stopped servers
    for pid, name in known_procs.items():
      if pid not in current_procs:
        msg = f"❌ [PID {pid}] {name} went offline!"
        print(msg, flush=True)
        send_macos_notification(
          "🚨 MCP Server Crashed",
          f"The '{name}' server has died or disconnected.",
          "Basso",
        )

    # ✅ Detect newly started servers
    for pid, name in current_procs.items():
      if pid not in known_procs:
        msg = f"✅ [PID {pid}] {name} came online."
        print(msg, flush=True)
        send_macos_notification(
          "✅ MCP Server Online",
          f"The '{name}' server connected successfully.",
          "Glass",
        )

    known_procs = current_procs


if __name__ == "__main__":
  try:
    main()
  except KeyboardInterrupt:
    print("\n🛡️ MCP Watchdog stopped.", flush=True)
    sys.exit(0)
