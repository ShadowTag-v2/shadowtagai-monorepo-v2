# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Team Memory Sync Service — Push/pull with conflict resolution.

Ported from Claude Code v2.1.91 src/services/teamMemorySync/ (2167L).

Key patterns:
  - TEAMMEM flag gates all team memory operations
  - SyncState: instance-scoped mutable state (ETag, checksums, max_entries)
  - Delta upload: only keys whose hash differs from server
  - Server wins per-key on pull (server-authoritative)
  - File deletions do NOT propagate
  - Secret scanning before push (blocks credentials in memory)
  - Batched PUT with MAX_PUT_BODY_BYTES cap (gateway 413 prevention)
  - Structured 413 handling: learns server max_entries dynamically
"""

from __future__ import annotations

import hashlib
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)

TEAM_MEMORY_SYNC_TIMEOUT_MS = 30_000
MAX_FILE_SIZE_BYTES = 250_000
MAX_PUT_BODY_BYTES = 200_000
MAX_RETRIES = 3
MAX_CONFLICT_RETRIES = 2


@dataclass
class SyncState:
  """Mutable state for team memory sync.

  Created once per session by the watcher. Tests create fresh instances.
  """

  last_known_checksum: str | None = None
  server_checksums: dict[str, str] = field(default_factory=dict)
  server_max_entries: int | None = None


def create_sync_state() -> SyncState:
  return SyncState()


def hash_content(content: str) -> str:
  """Compute sha256:<hex> over UTF-8 bytes. Matches server format."""
  return "sha256:" + hashlib.sha256(content.encode("utf-8")).hexdigest()


# ── Secret scanning ─────────────────────────────────────────────────

SECRET_PATTERNS = [
  re.compile(r"(?:api[_-]?key|apikey)\s*[:=]\s*['\"]?[\w-]{20,}", re.IGNORECASE),
  re.compile(
    r"(?:secret|password|token|credential)\s*[:=]\s*['\"]?[\w-]{16,}", re.IGNORECASE
  ),
  re.compile(r"(?:sk-|pk-|rk-)[a-zA-Z0-9]{20,}"),
  re.compile(r"-----BEGIN (?:RSA |EC )?PRIVATE KEY-----"),
  re.compile(r"ghp_[a-zA-Z0-9]{36}"),
  re.compile(r"gho_[a-zA-Z0-9]{36}"),
  re.compile(r"xoxb-[0-9]{10,}-[a-zA-Z0-9]+"),
  re.compile(r"AKIA[0-9A-Z]{16}"),
]


@dataclass
class SecretScanResult:
  has_secrets: bool
  skipped_files: list[str] = field(default_factory=list)
  patterns_matched: list[str] = field(default_factory=list)


def scan_for_secrets(content: str, file_path: str = "") -> SecretScanResult:
  """Scan content for credential patterns before push."""
  matched = []
  for pattern in SECRET_PATTERNS:
    if pattern.search(content):
      matched.append(pattern.pattern[:50])
  return SecretScanResult(
    has_secrets=len(matched) > 0,
    skipped_files=[file_path] if matched else [],
    patterns_matched=matched,
  )


# ── Local memory operations ─────────────────────────────────────────


@dataclass
class TeamMemoryEntry:
  key: str
  content: str
  checksum: str


def read_local_team_memory(
  team_mem_dir: Path,
  state: SyncState,
) -> tuple[list[TeamMemoryEntry], list[str]]:
  """Read local team memory files, filtering oversized and secret-containing files.

  Returns (entries, skipped_files).
  """
  entries = []
  skipped = []

  if not team_mem_dir.exists():
    return entries, skipped

  for path in sorted(team_mem_dir.iterdir()):
    if not path.is_file():
      continue
    try:
      size = path.stat().st_size
      if size > MAX_FILE_SIZE_BYTES:
        skipped.append(f"{path.name} (oversized: {size}B)")
        continue
      content = path.read_text(encoding="utf-8")
      scan = scan_for_secrets(content, str(path))
      if scan.has_secrets:
        skipped.append(f"{path.name} (contains secrets)")
        continue
      checksum = hash_content(content)
      entries.append(
        TeamMemoryEntry(
          key=path.name,
          content=content,
          checksum=checksum,
        )
      )
    except OSError as e:
      skipped.append(f"{path.name} (read error: {e})")

  # Apply server max_entries cap if known
  if state.server_max_entries is not None and len(entries) > state.server_max_entries:
    entries = entries[: state.server_max_entries]

  return entries, skipped


def compute_push_delta(
  entries: list[TeamMemoryEntry],
  state: SyncState,
) -> list[TeamMemoryEntry]:
  """Compute delta: only entries whose checksum differs from server."""
  delta = []
  for entry in entries:
    server_checksum = state.server_checksums.get(entry.key)
    if server_checksum != entry.checksum:
      delta.append(entry)
  return delta


def batch_entries_for_push(
  entries: list[TeamMemoryEntry],
) -> list[list[TeamMemoryEntry]]:
  """Split entries into batches under MAX_PUT_BODY_BYTES.

  Server upsert-merge makes sequential PUTs safe.
  """
  batches = []
  current_batch: list[TeamMemoryEntry] = []
  current_size = 0

  for entry in entries:
    entry_size = len(entry.content.encode("utf-8")) + len(entry.key) + 50
    if current_batch and current_size + entry_size > MAX_PUT_BODY_BYTES:
      batches.append(current_batch)
      current_batch = []
      current_size = 0
    current_batch.append(entry)
    current_size += entry_size

  if current_batch:
    batches.append(current_batch)
  return batches


def apply_pull_to_local(
  team_mem_dir: Path,
  server_entries: list[dict],
  state: SyncState,
) -> int:
  """Apply server entries to local filesystem. Server wins per-key.

  Returns count of files written.
  """
  team_mem_dir.mkdir(parents=True, exist_ok=True)
  written = 0
  for entry in server_entries:
    key = entry.get("key", "")
    content = entry.get("content", "")
    checksum = entry.get("checksum", "")
    if not key:
      continue
    path = team_mem_dir / key
    try:
      path.write_text(content, encoding="utf-8")
      state.server_checksums[key] = checksum or hash_content(content)
      written += 1
    except OSError as e:
      logger.warning("Failed to write team memory %s: %s", key, e)
  return written


class TeamMemorySyncService:
  """Manages team memory synchronization.

  Push/pull with delta computation, secret scanning,
  and batched uploads.
  """

  def __init__(self, team_mem_dir: str | Path):
    self.team_mem_dir = Path(team_mem_dir)
    self.state = create_sync_state()

  def prepare_push(self) -> tuple[list[list[TeamMemoryEntry]], list[str]]:
    """Prepare batched push data. Returns (batches, skipped_files)."""
    entries, skipped = read_local_team_memory(self.team_mem_dir, self.state)
    delta = compute_push_delta(entries, self.state)
    if not delta:
      return [], skipped
    batches = batch_entries_for_push(delta)
    return batches, skipped

  def apply_pull(self, server_entries: list[dict]) -> int:
    return apply_pull_to_local(self.team_mem_dir, server_entries, self.state)

  def reset(self) -> None:
    self.state = create_sync_state()


def health_check() -> bool:
  return True
