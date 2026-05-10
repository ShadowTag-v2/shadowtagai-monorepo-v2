"""AutoDream consolidation engine.

Ported from Claude Code ``src/services/autoDream/``.

This module implements the full gate+lock+prompt system:

1. **ConsolidationLock** — file-based lock whose mtime IS lastConsolidatedAt.
   Body is the holder's PID. Self-heals via stale PID detection (1-hour TTL).

2. **check_dream_gates** — runs the 3-gate cascade (time → sessions → lock)
   to determine if consolidation should fire.

3. **build_consolidation_prompt** — generates the 4-phase consolidation
   prompt (Orient → Gather → Consolidate → Prune).

4. **record_consolidation** — stamps the lock file after manual /dream.
"""

from __future__ import annotations

import glob
import logging
import os
import time
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)

# Lock file name inside the memory directory
LOCK_FILE = ".consolidate-lock"

# Stale past this even if the PID is live (PID reuse guard)
HOLDER_STALE_MS = 60 * 60 * 1000  # 1 hour in milliseconds

# Scan throttle: when time-gate passes but session-gate doesn't
SESSION_SCAN_INTERVAL_MS = 10 * 60 * 1000  # 10 minutes

# Memory entrypoint filename
ENTRYPOINT_NAME = "CLAUDE.md"
MAX_ENTRYPOINT_LINES = 100


@dataclass
class AutoDreamConfig:
  """Thresholds for dream triggering."""

  min_hours: float = 24.0
  min_sessions: int = 5


@dataclass
class AutoDreamResult:
  """Result of a dream gate check."""

  should_fire: bool
  reason: str
  hours_since: float = 0.0
  sessions_found: int = 0
  session_ids: list[str] = field(default_factory=list)
  prior_mtime: float = 0.0


class ConsolidationLock:
  """File-based consolidation lock.

  The lock file's mtime IS lastConsolidatedAt. The body contains
  the holder's PID. This allows dead-PID detection and self-healing.

  Ported from ``consolidationLock.ts``.
  """

  def __init__(self, memory_dir: str) -> None:
    self._memory_dir = memory_dir
    self._lock_path = os.path.join(memory_dir, LOCK_FILE)

  @property
  def lock_path(self) -> str:
    return self._lock_path

  def read_last_consolidated_at(self) -> float:
    """mtime of the lock file = lastConsolidatedAt. 0 if absent.

    Per-turn cost: one stat.
    """
    try:
      s = os.stat(self._lock_path)
      return s.st_mtime * 1000  # Convert to milliseconds
    except FileNotFoundError:
      return 0.0

  def try_acquire(self) -> float | None:
    """Acquire the lock.

    Returns the pre-acquire mtime (for rollback), or None if blocked.
    """
    mtime_ms: float | None = None
    holder_pid: int | None = None

    try:
      s = os.stat(self._lock_path)
      mtime_ms = s.st_mtime * 1000

      with open(self._lock_path) as f:
        raw = f.read().strip()
        parsed = int(raw) if raw.isdigit() else None
        holder_pid = parsed
    except FileNotFoundError, ValueError, OSError:
      pass  # No prior lock

    # Check if lock is held by a live process
    if (
      mtime_ms is not None
      and (time.time() * 1000 - mtime_ms) < HOLDER_STALE_MS
      and holder_pid is not None
      and _is_process_running(holder_pid)
    ):
      logger.debug(
        "[autoDream] lock held by live PID %d (mtime %ds ago)",
        holder_pid,
        int((time.time() * 1000 - mtime_ms) / 1000),
      )
      return None
      # Dead PID or unparseable body — reclaim

    # Memory dir may not exist yet
    os.makedirs(self._memory_dir, exist_ok=True)

    # Write our PID
    with open(self._lock_path, "w") as f:
      f.write(str(os.getpid()))

    # Two reclaimers both write → last wins. Verify we hold it.
    try:
      with open(self._lock_path) as f:
        verify = f.read().strip()
    except OSError:
      return None

    if verify != str(os.getpid()):
      return None

    return mtime_ms if mtime_ms is not None else 0.0

  def rollback(self, prior_mtime: float) -> None:
    """Rewind mtime to pre-acquire after a failed consolidation.

    ``prior_mtime`` 0 → remove the file (restore no-file state).
    """
    try:
      if prior_mtime == 0:
        os.unlink(self._lock_path)
        return

      # Clear PID body
      with open(self._lock_path, "w") as f:
        f.write("")

      # Restore mtime
      t = prior_mtime / 1000  # utimes wants seconds
      os.utime(self._lock_path, (t, t))
    except OSError as exc:
      logger.debug(
        "[autoDream] rollback failed: %s — next trigger delayed to min_hours",
        exc,
      )

  def record(self) -> None:
    """Stamp from manual /dream. Optimistic — fires at prompt-build time."""
    try:
      os.makedirs(self._memory_dir, exist_ok=True)
      with open(self._lock_path, "w") as f:
        f.write(str(os.getpid()))
    except OSError as exc:
      logger.debug("[autoDream] record failed: %s", exc)


def check_dream_gates(
  memory_dir: str,
  transcript_dir: str,
  *,
  config: AutoDreamConfig | None = None,
  current_session_id: str | None = None,
  force: bool = False,
) -> AutoDreamResult:
  """Run the 3-gate cascade to determine if consolidation should fire.

  Gates (cheapest first):
      1. Time: hours since last consolidation >= min_hours
      2. Sessions: transcript count with mtime > last_consolidated >= min_sessions
      3. Lock: no other process mid-consolidation

  Parameters
  ----------
  memory_dir:
      Path to the memory directory (e.g., ``~/.claude/memory/``).
  transcript_dir:
      Path to the session transcript directory.
  config:
      Thresholds. Uses defaults (24h, 5 sessions) if not provided.
  current_session_id:
      Session to exclude from the session count (it's always recent).
  force:
      Bypass time/session gates (but NOT the lock).
  """
  cfg = config or AutoDreamConfig()
  lock = ConsolidationLock(memory_dir)

  # --- Time gate ---
  last_at = lock.read_last_consolidated_at()
  hours_since = (time.time() * 1000 - last_at) / 3_600_000

  if not force and hours_since < cfg.min_hours:
    return AutoDreamResult(
      should_fire=False,
      reason=f"time_gate: {hours_since:.1f}h < {cfg.min_hours}h",
      hours_since=hours_since,
    )

  # --- Session gate ---
  session_ids = _list_sessions_touched_since(transcript_dir, last_at)

  # Exclude current session
  if current_session_id:
    session_ids = [sid for sid in session_ids if sid != current_session_id]

  if not force and len(session_ids) < cfg.min_sessions:
    return AutoDreamResult(
      should_fire=False,
      reason=f"session_gate: {len(session_ids)} < {cfg.min_sessions}",
      hours_since=hours_since,
      sessions_found=len(session_ids),
    )

  # --- Lock gate ---
  if not force:
    prior_mtime = lock.try_acquire()
    if prior_mtime is None:
      return AutoDreamResult(
        should_fire=False,
        reason="lock_gate: held by another process",
        hours_since=hours_since,
        sessions_found=len(session_ids),
      )
  else:
    prior_mtime = last_at

  return AutoDreamResult(
    should_fire=True,
    reason=f"all_gates_passed: {hours_since:.1f}h, {len(session_ids)} sessions",
    hours_since=hours_since,
    sessions_found=len(session_ids),
    session_ids=session_ids,
    prior_mtime=prior_mtime,
  )


def record_consolidation(memory_dir: str) -> None:
  """Stamp from manual /dream."""
  lock = ConsolidationLock(memory_dir)
  lock.record()


def build_consolidation_prompt(
  memory_root: str,
  transcript_dir: str,
  extra: str = "",
) -> str:
  """Generate the 4-phase consolidation prompt.

  Ported from ``consolidationPrompt.ts``.
  """
  return f"""# Dream: Memory Consolidation

You are performing a dream — a reflective pass over your memory files. \
Synthesize what you've learned recently into durable, well-organized \
memories so that future sessions can orient quickly.

Memory directory: `{memory_root}`
The directory exists. You may create new files or modify existing ones.

Session transcripts: `{transcript_dir}` \
(large JSONL files — grep narrowly, don't read whole files)

---

## Phase 1 — Orient

- `ls` the memory directory to see what already exists
- Read `{ENTRYPOINT_NAME}` to understand the current index
- Skim existing topic files so you improve them rather than creating duplicates
- If `logs/` or `sessions/` subdirectories exist, review recent entries there

## Phase 2 — Gather recent signal

Look for new information worth persisting. Sources in rough priority order:

1. **Daily logs** (`logs/YYYY/MM/YYYY-MM-DD.md`) if present
2. **Existing memories that drifted** — facts that contradict something \
you see in the codebase now
3. **Transcript search** — if you need specific context, grep the JSONL \
transcripts for narrow terms:
   `grep -rn "<narrow term>" {transcript_dir}/ --include="*.jsonl" | tail -50`

Don't exhaustively read transcripts. Look only for things you already \
suspect matter.

## Phase 3 — Consolidate

For each thing worth remembering, write or update a memory file at the \
top level of the memory directory.

Focus on:
- Merging new signal into existing topic files rather than creating \
near-duplicates
- Converting relative dates ("yesterday", "last week") to absolute dates \
so they remain interpretable after time passes
- Deleting contradicted facts — if today's investigation disproves an old \
memory, fix it at the source

## Phase 4 — Prune and index

Update `{ENTRYPOINT_NAME}` so it stays under {MAX_ENTRYPOINT_LINES} lines \
AND under ~25KB. It's an **index**, not a dump — each entry should be one \
line under ~150 characters: `- [Title](file.md) — one-line hook`. Never \
write memory content directly into it.

- Remove pointers to memories that are now stale, wrong, or superseded
- Demote verbose entries: if an index line is over ~200 chars, it's \
carrying content that belongs in the topic file — shorten the line, \
move the detail
- Add pointers to newly important memories
- Resolve contradictions — if two files disagree, fix the wrong one

---

Return a brief summary of what you consolidated, updated, or pruned. \
If nothing changed (memories are already tight), say so.{_extra_section(extra)}"""


def _extra_section(extra: str) -> str:
  if not extra:
    return ""
  return f"\n\n## Additional context\n\n{extra}"


def _list_sessions_touched_since(transcript_dir: str, since_ms: float) -> list[str]:
  """Session IDs with mtime after since_ms.

  Scans for JSONL transcript files, excludes agent-*.jsonl.
  """
  since_s = since_ms / 1000
  session_ids: list[str] = []

  try:
    pattern = os.path.join(transcript_dir, "**", "*.jsonl")
    for filepath in glob.glob(pattern, recursive=True):
      basename = os.path.basename(filepath)
      # Exclude agent transcripts
      if basename.startswith("agent-"):
        continue
      try:
        st = os.stat(filepath)
        if st.st_mtime > since_s:
          # Extract session ID from filename
          session_id = Path(filepath).stem
          session_ids.append(session_id)
      except OSError:
        continue
  except OSError:
    pass

  return session_ids


def _is_process_running(pid: int) -> bool:
  """Check if a process is running by sending signal 0."""
  try:
    os.kill(pid, 0)
    return True
  except ProcessLookupError, PermissionError:
    return False
  except OSError:
    return False
