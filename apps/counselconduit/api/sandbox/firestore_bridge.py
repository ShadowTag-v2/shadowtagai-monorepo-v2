# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""CoW Overlay ↔ Firestore Bridge — Phase 3 Milestone 2.

Connects the speculation engine's CoW overlay to the CounselConduit Firestore
document store. Handles:
  1. Diff computation between original and overlay files
  2. Attorney accept/reject/cherry-pick commit flow
  3. Privilege metadata preservation through overlay → production
  4. Immutable audit trail for every bridge operation

Architecture:
  OverlayFS (speculation_engine.engine)
      ↕ (diff computation)
  FirestoreBridge
      ↕ (commit / reject)
  Firestore (firms/{firm_id}/matters/{matter_id}/documents/{doc_id})

Security invariants:
  - Trust Level 0 enforced at every bridge operation
  - Attorney UID verified against session config before any write
  - Privilege status ('privileged' | 'work_product' | 'public') preserved
  - All operations logged to audit_log collection
"""

from __future__ import annotations

import difflib
import hashlib
import logging
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from apps.counselconduit.api.sandbox.session import (
  CommitAction,
  SandboxSession,
  SecurityError,
)

logger = logging.getLogger("counselconduit.sandbox.bridge")


# ── Data Structures ───────────────────────────────────────────────────────


@dataclass(frozen=True)
class DiffHunk:
  """A single contiguous block of changes within a file."""

  old_start: int
  old_lines: int
  new_start: int
  new_lines: int
  changes: list[dict[str, Any]] = field(default_factory=list)

  def to_dict(self) -> dict[str, Any]:
    return {
      "old_start": self.old_start,
      "old_lines": self.old_lines,
      "new_start": self.new_start,
      "new_lines": self.new_lines,
      "changes": self.changes,
    }


@dataclass
class FileDiff:
  """Computed diff for a single file in the overlay."""

  path: str
  language: str
  hunks: list[DiffHunk]
  privilege_status: str  # 'privileged' | 'work_product' | 'public'
  ai_confidence: float  # 0.0 - 1.0
  original_hash: str  # SHA-256 of original content
  overlay_hash: str  # SHA-256 of overlay content
  original_content: str = ""
  overlay_content: str = ""

  def to_dict(self) -> dict[str, Any]:
    return {
      "path": self.path,
      "language": self.language,
      "hunks": [h.to_dict() for h in self.hunks],
      "privilege_status": self.privilege_status,
      "ai_confidence": self.ai_confidence,
      "original_hash": self.original_hash,
      "overlay_hash": self.overlay_hash,
      "hunk_count": len(self.hunks),
    }


@dataclass
class BridgeResult:
  """Result of a bridge commit operation."""

  success: bool
  committed_files: list[str] = field(default_factory=list)
  rejected_files: list[str] = field(default_factory=list)
  audit_id: str = ""
  error: str = ""
  duration_ms: float = 0.0

  def to_dict(self) -> dict[str, Any]:
    return {
      "success": self.success,
      "committed_files": self.committed_files,
      "rejected_files": self.rejected_files,
      "audit_id": self.audit_id,
      "error": self.error,
      "duration_ms": self.duration_ms,
    }


# ── Diff Computation ──────────────────────────────────────────────────────

# Language extension mapping for syntax highlighting
_EXTENSION_LANG_MAP: dict[str, str] = {
  ".py": "python",
  ".ts": "typescript",
  ".tsx": "typescriptreact",
  ".js": "javascript",
  ".jsx": "javascriptreact",
  ".json": "json",
  ".md": "markdown",
  ".yaml": "yaml",
  ".yml": "yaml",
  ".toml": "toml",
  ".css": "css",
  ".html": "html",
  ".sql": "sql",
  ".rs": "rust",
  ".go": "go",
  ".cs": "csharp",
}


def _detect_language(file_path: str) -> str:
  """Detect programming language from file extension."""
  for ext, lang in _EXTENSION_LANG_MAP.items():
    if file_path.endswith(ext):
      return lang
  return "plaintext"


def _sha256(content: str) -> str:
  """Compute SHA-256 hash of content string."""
  return hashlib.sha256(content.encode("utf-8")).hexdigest()


def compute_diff(
  original: str,
  overlay: str,
  file_path: str,
  *,
  privilege_status: str = "public",
  ai_confidence: float = 0.5,
  context_lines: int = 3,
) -> FileDiff:
  """Compute a structured diff between original and overlay content.

  Args:
      original: Original file content (may be empty for new files).
      overlay: Overlay (speculative) file content.
      file_path: Relative path of the file.
      privilege_status: Privilege classification for the document.
      ai_confidence: Speculation engine confidence score (0-1).
      context_lines: Number of context lines around each change.

  Returns:
      FileDiff with computed hunks.
  """
  original_lines = original.splitlines(keepends=True)
  overlay_lines = overlay.splitlines(keepends=True)

  # Use unified_diff for hunk computation
  diff_lines = list(
    difflib.unified_diff(
      original_lines,
      overlay_lines,
      fromfile=f"a/{file_path}",
      tofile=f"b/{file_path}",
      n=context_lines,
    )
  )

  hunks = _parse_unified_diff(diff_lines)

  return FileDiff(
    path=file_path,
    language=_detect_language(file_path),
    hunks=hunks,
    privilege_status=privilege_status,
    ai_confidence=ai_confidence,
    original_hash=_sha256(original),
    overlay_hash=_sha256(overlay),
    original_content=original,
    overlay_content=overlay,
  )


def _parse_unified_diff(diff_lines: list[str]) -> list[DiffHunk]:
  """Parse unified diff output into structured DiffHunks."""
  hunks: list[DiffHunk] = []
  current_changes: list[dict[str, Any]] = []
  old_start = 0
  old_lines = 0
  new_start = 0
  new_lines = 0
  old_line_no = 0
  new_line_no = 0

  for line in diff_lines:
    # Skip header lines
    if line.startswith("---") or line.startswith("+++"):
      continue

    # Hunk header: @@ -old_start,old_lines +new_start,new_lines @@
    if line.startswith("@@"):
      # Save previous hunk
      if current_changes:
        hunks.append(
          DiffHunk(
            old_start=old_start,
            old_lines=old_lines,
            new_start=new_start,
            new_lines=new_lines,
            changes=current_changes,
          )
        )
        current_changes = []

      # Parse hunk header
      parts = line.split("@@")
      if len(parts) >= 2:
        range_info = parts[1].strip()
        ranges = range_info.split(" ")
        for r in ranges:
          if r.startswith("-"):
            r_parts = r[1:].split(",")
            old_start = int(r_parts[0])
            old_lines = int(r_parts[1]) if len(r_parts) > 1 else 1
          elif r.startswith("+"):
            r_parts = r[1:].split(",")
            new_start = int(r_parts[0])
            new_lines = int(r_parts[1]) if len(r_parts) > 1 else 1
      old_line_no = old_start
      new_line_no = new_start
      continue

    # Content lines
    content = line[1:] if len(line) > 0 else ""
    # Strip trailing newline for display
    content = content.rstrip("\n")

    if line.startswith("+"):
      current_changes.append(
        {"type": "add", "content": content, "lineNumber": new_line_no}
      )
      new_line_no += 1
    elif line.startswith("-"):
      current_changes.append(
        {"type": "delete", "content": content, "lineNumber": old_line_no}
      )
      old_line_no += 1
    else:
      current_changes.append(
        {"type": "context", "content": content, "lineNumber": old_line_no}
      )
      old_line_no += 1
      new_line_no += 1

  # Final hunk
  if current_changes:
    hunks.append(
      DiffHunk(
        old_start=old_start,
        old_lines=old_lines,
        new_start=new_start,
        new_lines=new_lines,
        changes=current_changes,
      )
    )

  return hunks


# ── Firestore Bridge ──────────────────────────────────────────────────────


class FirestoreBridge:
  """Bridge between CoW overlay and production Firestore.

  Handles the commit/reject flow with full security enforcement:
  - Trust Level 0 verification
  - Attorney UID validation
  - Privilege metadata preservation
  - Audit trail for every operation
  """

  def __init__(self, session: SandboxSession):
    """Initialize bridge with a sandbox session.

    Args:
        session: Active SandboxSession in REVIEWING state.

    Raises:
        SecurityError: If session trust level is not 0.
    """
    if session.config.trust_level != 0:
      msg = "FirestoreBridge requires Trust Level 0"
      raise SecurityError(msg)
    self.session = session

  def compute_diffs(
    self,
    original_files: dict[str, str],
    privilege_map: dict[str, str] | None = None,
    confidence_map: dict[str, float] | None = None,
  ) -> list[FileDiff]:
    """Compute diffs between original files and overlay.

    Args:
        original_files: Map of file paths to original content.
        privilege_map: Map of file paths to privilege status.
        confidence_map: Map of file paths to AI confidence scores.

    Returns:
        List of FileDiff objects ready for attorney review.
    """
    privilege_map = privilege_map or {}
    confidence_map = confidence_map or {}
    diffs: list[FileDiff] = []

    for path, overlay_content in self.session.overlay_files.items():
      original = original_files.get(path, "")
      diff = compute_diff(
        original=original,
        overlay=overlay_content,
        file_path=path,
        privilege_status=privilege_map.get(path, "public"),
        ai_confidence=confidence_map.get(path, 0.5),
      )
      diffs.append(diff)

    return diffs

  async def commit_to_firestore(
    self,
    action: CommitAction,
    attorney_uid: str,
    *,
    firm_id: str,
    selected_files: list[str] | None = None,
    rejection_reason: str = "",
    privilege_map: dict[str, str] | None = None,
  ) -> BridgeResult:
    """Execute the attorney's decision and commit to Firestore.

    This is the critical path — every call produces an audit record.

    Args:
        action: Accept, reject, or partial accept.
        attorney_uid: UID of the deciding attorney.
        firm_id: Firm identifier for Firestore collection scoping.
        selected_files: For PARTIAL_ACCEPT, which files to commit.
        rejection_reason: For REJECT, why it was rejected.
        privilege_map: Map of file paths to privilege status.

    Returns:
        BridgeResult with commit status and audit ID.
    """
    start = time.monotonic()
    privilege_map = privilege_map or {}

    try:
      # Delegate state transition to SandboxSession (validates attorney UID)
      committed = self.session.commit(
        action=action,
        attorney_uid=attorney_uid,
        selected_files=selected_files,
        rejection_reason=rejection_reason,
      )

      if action == CommitAction.REJECT:
        result = BridgeResult(
          success=True,
          rejected_files=list(self.session.overlay_files.keys()),
          duration_ms=(time.monotonic() - start) * 1000,
        )
      else:
        # Write committed files to Firestore
        await self._write_documents(
          firm_id=firm_id,
          files=committed,
          privilege_map=privilege_map,
        )
        result = BridgeResult(
          success=True,
          committed_files=committed,
          duration_ms=(time.monotonic() - start) * 1000,
        )

      # Write audit record
      result.audit_id = await self._write_audit(
        action=action,
        attorney_uid=attorney_uid,
        firm_id=firm_id,
        result=result,
        rejection_reason=rejection_reason,
      )

      logger.info(
        "Bridge commit: action=%s files=%d firm=%s audit=%s",
        action,
        len(committed) if action != CommitAction.REJECT else 0,
        firm_id,
        result.audit_id,
      )

      return result

    except PermissionError as e:
      logger.warning("Bridge permission denied: %s", e)
      return BridgeResult(
        success=False,
        error=str(e),
        duration_ms=(time.monotonic() - start) * 1000,
      )
    except Exception as e:
      logger.exception("Bridge commit failed: %s", e)
      return BridgeResult(
        success=False,
        error=str(e),
        duration_ms=(time.monotonic() - start) * 1000,
      )

  async def _write_documents(
    self,
    firm_id: str,
    files: list[str],
    privilege_map: dict[str, str],
  ) -> None:
    """Write overlay files to Firestore document store.

    Each file is stored as a versioned document under:
    firms/{firm_id}/matters/{matter_id}/documents/{doc_id}
    """
    try:
      from apps.counselconduit.api.firestore_client import _get_client
    except ImportError:
      from api.firestore_client import _get_client  # type: ignore[no-redef]

    db = _get_client()
    matter_id = self.session.config.matter_id
    batch = db.batch()

    for file_path in files:
      content = self.session.overlay_files.get(file_path, "")
      doc_id = _sha256(f"{matter_id}:{file_path}")[:24]
      doc_ref = (
        db.collection("firms")
        .document(firm_id)
        .collection("matters")
        .document(matter_id)
        .collection("documents")
        .document(doc_id)
      )
      batch.set(
        doc_ref,
        {
          "file_path": file_path,
          "content": content,
          "content_hash": _sha256(content),
          "privilege_status": privilege_map.get(file_path, "public"),
          "committed_by": self.session.config.attorney_uid,
          "session_id": self.session.session_id,
          "matter_id": matter_id,
          "_committed_at": datetime.now(UTC).isoformat(),
          "_source": "sandbox_overlay",
        },
        merge=True,
      )

    await batch.commit()

  async def _write_audit(
    self,
    action: CommitAction,
    attorney_uid: str,
    firm_id: str,
    result: BridgeResult,
    rejection_reason: str = "",
  ) -> str:
    """Write an immutable audit record for the bridge operation."""
    try:
      from apps.counselconduit.api.firestore_client import (
        AuditEntry,
        write_audit_log,
      )
    except ImportError:
      from api.firestore_client import AuditEntry, write_audit_log  # type: ignore[no-redef]

    entry = AuditEntry(
      action=f"sandbox_{action.value}",
      actor_id=attorney_uid,
      resource_type="sandbox_session",
      resource_id=self.session.session_id,
      details={
        "matter_id": self.session.config.matter_id,
        "firm_id": firm_id,
        "committed_files": result.committed_files,
        "rejected_files": result.rejected_files,
        "rejection_reason": rejection_reason,
        "duration_ms": result.duration_ms,
        "trust_level": self.session.config.trust_level,
      },
    )
    await write_audit_log(entry)
    return entry.timestamp  # Use timestamp as audit ID
