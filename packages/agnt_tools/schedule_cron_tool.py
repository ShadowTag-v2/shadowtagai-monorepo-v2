# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""ScheduleCronTool — Agent-callable cron job scheduler.

Ported from: Claude Code src/tools/ScheduleCronTool/prompt.ts
Reference: Kairos Ultraplan P0 #1

Allows the agent to schedule deferred tasks (Dream consolidation, lint
sweeps, test runs) as one-shot or recurring jobs. Uses launchd on macOS
as the native scheduler backend (no crontab dependency).

The tool writes launchd plist files and loads them via launchctl. Jobs
include a jitter offset (0-300s) to prevent thundering herd when
multiple agents schedule simultaneous work.

Usage:
    from packages.agnt_tools.schedule_cron_tool import ScheduleCronTool
    tool = ScheduleCronTool()
    result = tool.schedule(
        job_name="dream_consolidation",
        command="python scripts/dream_consolidation.py",
        interval_seconds=86400,
        jitter_seconds=300,
    )
"""

from __future__ import annotations

import json
import logging
import os
import random
import subprocess
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

logger = logging.getLogger("agnt.schedule_cron_tool")

# --- Constants ---------------------------------------------------------------

PLIST_DIR = Path.home() / "Library" / "LaunchAgents"
JOB_PREFIX = "com.shadowtag.agnt"
MAX_INTERVAL_SECONDS = 604800  # 1 week
MIN_INTERVAL_SECONDS = 60  # 1 minute
DEFAULT_JITTER_SECONDS = 300  # 5 minutes
BEADS_DIR = (
  Path(
    os.environ.get(
      "REPO_ROOT",
      os.path.expanduser("~/.gemini/antigravity/Monorepo-Uphillsnowball"),
    )
  )
  / ".beads"
)


# --- Data Models -------------------------------------------------------------


@dataclass
class ScheduleResult:
  """Result of a ScheduleCronTool execution."""

  job_name: str
  plist_path: str
  interval_seconds: int
  jitter_applied: int
  effective_interval: int
  loaded: bool
  scheduled_at: str
  error: str = ""


@dataclass
class JobInfo:
  """Info about an existing scheduled job."""

  job_name: str
  label: str
  interval_seconds: int
  command: str
  loaded: bool


# --- Tool Implementation -----------------------------------------------------


class ScheduleCronTool:
  """Agent-callable tool for scheduling deferred work.

  Manages launchd plist-based scheduling on macOS. Each job gets
  a unique label (com.shadowtag.agnt.<name>) and a jittered interval
  to prevent simultaneous execution storms.

  The tool maintains a registry in .beads/scheduled_jobs.json for
  introspection and cleanup.
  """

  name = "ScheduleCronTool"
  description = "Schedule a deferred task as a one-shot or recurring job. Uses macOS launchd as the scheduler backend."

  def __init__(self) -> None:
    self._registry_path = BEADS_DIR / "scheduled_jobs.json"
    BEADS_DIR.mkdir(parents=True, exist_ok=True)

  def schedule(
    self,
    job_name: str,
    command: str,
    interval_seconds: int = 86400,
    jitter_seconds: int = DEFAULT_JITTER_SECONDS,
    one_shot: bool = False,
  ) -> ScheduleResult:
    """Schedule a job via launchd.

    Args:
        job_name: Short identifier (e.g., 'dream_consolidation').
        command: Full shell command to execute.
        interval_seconds: How often to run (clamped to [60, 604800]).
        jitter_seconds: Max random jitter added to interval.
        one_shot: If True, run once then unload.

    Returns:
        ScheduleResult with plist path and load status.
    """
    # Sanitize
    job_name = job_name.replace(" ", "_").replace("/", "_")
    label = f"{JOB_PREFIX}.{job_name}"

    # Clamp interval
    interval_seconds = max(
      MIN_INTERVAL_SECONDS,
      min(interval_seconds, MAX_INTERVAL_SECONDS),
    )

    # Apply jitter
    jitter = random.randint(0, jitter_seconds)
    effective_interval = interval_seconds + jitter

    # Build plist
    PLIST_DIR.mkdir(parents=True, exist_ok=True)
    plist_path = PLIST_DIR / f"{label}.plist"

    plist_content = self._build_plist(
      label=label,
      command=command,
      interval=effective_interval,
      one_shot=one_shot,
    )

    # Write plist
    plist_path.write_text(plist_content)
    logger.info(
      "ScheduleCronTool: wrote plist %s (interval=%ds, jitter=%ds)",
      plist_path,
      interval_seconds,
      jitter,
    )

    # Load via launchctl
    loaded = self._load_job(label, plist_path)

    # Update registry
    self._update_registry(
      job_name=job_name,
      label=label,
      interval_seconds=interval_seconds,
      command=command,
      plist_path=str(plist_path),
    )

    return ScheduleResult(
      job_name=job_name,
      plist_path=str(plist_path),
      interval_seconds=interval_seconds,
      jitter_applied=jitter,
      effective_interval=effective_interval,
      loaded=loaded,
      scheduled_at=datetime.now(UTC).isoformat(),
    )

  def unschedule(self, job_name: str) -> bool:
    """Remove a scheduled job.

    Args:
        job_name: The job name used during scheduling.

    Returns:
        True if successfully unloaded and removed.
    """
    label = f"{JOB_PREFIX}.{job_name}"
    plist_path = PLIST_DIR / f"{label}.plist"

    # Unload
    try:
      subprocess.run(
        ["launchctl", "bootout", f"gui/{os.getuid()}", str(plist_path)],
        capture_output=True,
        timeout=10,
      )
    except subprocess.TimeoutExpired, FileNotFoundError:
      pass

    # Remove plist
    if plist_path.exists():
      plist_path.unlink()

    # Update registry
    self._remove_from_registry(job_name)

    logger.info("ScheduleCronTool: unscheduled %s", label)
    return True

  def list_jobs(self) -> list[JobInfo]:
    """List all registered scheduled jobs."""
    registry = self._load_registry()
    jobs = []
    for name, info in registry.items():
      label = info.get("label", "")
      # Check if loaded
      loaded = self._is_loaded(label)
      jobs.append(
        JobInfo(
          job_name=name,
          label=label,
          interval_seconds=info.get("interval_seconds", 0),
          command=info.get("command", ""),
          loaded=loaded,
        )
      )
    return jobs

  # --- Private Methods -----------------------------------------------------

  def _build_plist(
    self,
    label: str,
    command: str,
    interval: int,
    one_shot: bool,
  ) -> str:
    """Generate a launchd plist XML string."""
    plist = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>{label}</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/zsh</string>
        <string>-c</string>
        <string>{command}</string>
    </array>
    <key>StartInterval</key>
    <integer>{interval}</integer>
    <key>RunAtLoad</key>
    <{"true" if one_shot else "false"}/>
    <key>StandardOutPath</key>
    <string>/tmp/{label}.stdout.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/{label}.stderr.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/opt/homebrew/bin</string>
        <key>HOME</key>
        <string>{Path.home()}</string>
    </dict>
</dict>
</plist>"""
    return plist

  def _load_job(self, label: str, plist_path: Path) -> bool:
    """Load a plist into launchd."""
    # First unload if exists
    try:
      subprocess.run(
        ["launchctl", "bootout", f"gui/{os.getuid()}", str(plist_path)],
        capture_output=True,
        timeout=10,
      )
    except subprocess.TimeoutExpired, FileNotFoundError:
      pass

    # Load
    try:
      result = subprocess.run(
        ["launchctl", "bootstrap", f"gui/{os.getuid()}", str(plist_path)],
        capture_output=True,
        text=True,
        timeout=10,
      )
      loaded = result.returncode == 0
      if loaded:
        logger.info("ScheduleCronTool: loaded %s", label)
      else:
        logger.warning(
          "ScheduleCronTool: failed to load %s: %s",
          label,
          result.stderr.strip(),
        )
      return loaded
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
      logger.warning("ScheduleCronTool: launchctl error: %s", e)
      return False

  def _is_loaded(self, label: str) -> bool:
    """Check if a job is currently loaded in launchd."""
    try:
      result = subprocess.run(
        ["launchctl", "print", f"gui/{os.getuid()}/{label}"],
        capture_output=True,
        timeout=5,
      )
      return result.returncode == 0
    except subprocess.TimeoutExpired, FileNotFoundError:
      return False

  def _load_registry(self) -> dict:
    """Load the job registry from .beads/."""
    if self._registry_path.exists():
      try:
        return json.loads(self._registry_path.read_text())
      except json.JSONDecodeError, OSError:
        return {}
    return {}

  def _update_registry(
    self,
    job_name: str,
    label: str,
    interval_seconds: int,
    command: str,
    plist_path: str,
  ) -> None:
    """Update the job registry."""
    registry = self._load_registry()
    registry[job_name] = {
      "label": label,
      "interval_seconds": interval_seconds,
      "command": command,
      "plist_path": plist_path,
      "updated_at": datetime.now(UTC).isoformat(),
    }
    self._registry_path.write_text(json.dumps(registry, indent=2))

  def _remove_from_registry(self, job_name: str) -> None:
    """Remove a job from the registry."""
    registry = self._load_registry()
    registry.pop(job_name, None)
    self._registry_path.write_text(json.dumps(registry, indent=2))
