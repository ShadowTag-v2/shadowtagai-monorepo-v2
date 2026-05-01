# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Sandbox Session — Isolated CoW overlay lifecycle for attorney review.

Each sandbox session:
  1. Creates an isolated CoW overlay bound to a CounselConduit matter ID
  2. Runs speculation orchestrator within the overlay
  3. Presents diff-view to attorney for review
  4. Accepts/rejects/cherry-picks edits into production Firestore

Security invariants (Phase 3 §5):
  - Trust Level 0 — bypass_permissions is NEVER enabled
  - Matter-scoped isolation — one overlay per matter ID
  - Attorney-only commit — verified attorney UID required
  - Full audit trail — all operations logged to .beads/
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import StrEnum, auto
from typing import Any, Protocol, runtime_checkable


class SessionState(StrEnum):
    """State machine for sandbox session lifecycle."""

    CREATED = auto()
    SPECULATING = auto()
    REVIEWING = auto()
    COMMITTING = auto()
    COMMITTED = auto()
    REJECTED = auto()
    EXPIRED = auto()
    ERROR = auto()


class CommitAction(StrEnum):
    """Attorney decision on sandbox overlay."""

    ACCEPT = auto()
    REJECT = auto()
    PARTIAL_ACCEPT = auto()


@dataclass(frozen=True)
class SessionConfig:
    """Configuration for a sandbox session.

    Attributes:
        matter_id: CounselConduit matter identifier for privilege tracking.
        attorney_uid: Firebase Auth UID of the reviewing attorney.
        ttl_seconds: Session time-to-live (default: 30 minutes).
        max_overlay_files: Maximum files in the CoW overlay.
        trust_level: Fixed at 0 — bypass_permissions is BANNED.
    """

    matter_id: str
    attorney_uid: str
    ttl_seconds: int = 1800  # 30 minutes
    max_overlay_files: int = 50
    trust_level: int = 0  # IMMUTABLE: Trust Level 0 for sandbox sessions


@dataclass
class SandboxSession:
    """Manages the lifecycle of an isolated CoW overlay session.

    Thread-safe session management with deterministic state transitions:
      CREATED → SPECULATING → REVIEWING → COMMITTING → COMMITTED
                                        ↘ REJECTED
                              (timeout)  → EXPIRED
    """

    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    config: SessionConfig = field(default_factory=lambda: SessionConfig(matter_id="", attorney_uid=""))
    state: SessionState = SessionState.CREATED
    created_at: float = field(default_factory=time.time)
    overlay_files: dict[str, str] = field(default_factory=dict)
    diff_summary: list[dict[str, Any]] = field(default_factory=list)
    rejection_reason: str = ""
    committed_files: list[str] = field(default_factory=list)

    # --- Lifecycle Methods ---

    def start_speculation(self) -> None:
        """Transition to SPECULATING phase.

        Raises:
            ValueError: If session is not in CREATED state.
            RuntimeError: If session has expired.
        """
        self._check_expiry()
        if self.state != SessionState.CREATED:
            msg = f"Cannot start speculation from state {self.state}"
            raise ValueError(msg)
        # SECURITY: Enforce Trust Level 0
        if self.config.trust_level != 0:
            msg = "Sandbox sessions MUST use Trust Level 0"
            raise SecurityError(msg)
        self.state = SessionState.SPECULATING

    def present_for_review(self, overlay_files: dict[str, str], diff_summary: list[dict[str, Any]]) -> None:
        """Transition to REVIEWING phase with overlay results.

        Args:
            overlay_files: Map of file paths to overlay content.
            diff_summary: Structured diff for attorney UI rendering.

        Raises:
            ValueError: If not in SPECULATING state.
            RuntimeError: If session has expired.
        """
        self._check_expiry()
        if self.state != SessionState.SPECULATING:
            msg = f"Cannot present for review from state {self.state}"
            raise ValueError(msg)
        if len(overlay_files) > self.config.max_overlay_files:
            msg = f"Overlay has {len(overlay_files)} files, max is {self.config.max_overlay_files}"
            raise ValueError(msg)
        self.overlay_files = overlay_files
        self.diff_summary = diff_summary
        self.state = SessionState.REVIEWING

    def commit(
        self,
        action: CommitAction,
        attorney_uid: str,
        *,
        selected_files: list[str] | None = None,
        rejection_reason: str = "",
    ) -> list[str]:
        """Execute attorney decision on overlay.

        Args:
            action: Accept, reject, or partial accept.
            attorney_uid: UID of the deciding attorney (verified against config).
            selected_files: For PARTIAL_ACCEPT, which files to commit.
            rejection_reason: For REJECT, why it was rejected (model tuning).

        Returns:
            List of file paths that were committed (empty for REJECT).

        Raises:
            ValueError: If not in REVIEWING state.
            PermissionError: If attorney_uid doesn't match.
            RuntimeError: If session has expired.
        """
        self._check_expiry()
        if self.state != SessionState.REVIEWING:
            msg = f"Cannot commit from state {self.state}"
            raise ValueError(msg)

        # SECURITY: Attorney-only commit
        if attorney_uid != self.config.attorney_uid:
            msg = "Only the assigned attorney can commit sandbox changes"
            raise PermissionError(msg)

        self.state = SessionState.COMMITTING

        if action == CommitAction.REJECT:
            self.state = SessionState.REJECTED
            self.rejection_reason = rejection_reason
            return []

        if action == CommitAction.PARTIAL_ACCEPT:
            files_to_commit = [f for f in (selected_files or []) if f in self.overlay_files]
        else:
            files_to_commit = list(self.overlay_files.keys())

        self.committed_files = files_to_commit
        self.state = SessionState.COMMITTED
        return files_to_commit

    def to_audit_record(self) -> dict[str, Any]:
        """Serialize session state for .beads/ evidence trail."""
        return {
            "session_id": self.session_id,
            "matter_id": self.config.matter_id,
            "attorney_uid": self.config.attorney_uid,
            "state": self.state,
            "created_at": self.created_at,
            "ttl_seconds": self.config.ttl_seconds,
            "overlay_file_count": len(self.overlay_files),
            "committed_file_count": len(self.committed_files),
            "rejection_reason": self.rejection_reason,
            "trust_level": self.config.trust_level,
        }

    # --- Internal ---

    def _check_expiry(self) -> None:
        """Abort session if TTL exceeded."""
        elapsed = time.time() - self.created_at
        if elapsed > self.config.ttl_seconds:
            self.state = SessionState.EXPIRED
            msg = f"Session {self.session_id} expired after {elapsed:.0f}s (TTL: {self.config.ttl_seconds}s)"
            raise RuntimeError(msg)


class SecurityError(Exception):
    """Raised when sandbox security invariants are violated."""


@runtime_checkable
class AbstractSessionStore(Protocol):
    """Protocol defining the session store interface.

    Any session store (Firestore, Redis, in-memory for tests) must
    implement these methods. The API layer depends on this protocol,
    not on concrete implementations.

    Phase 4 M3: Extracted to formalize the contract and enable
    removal of the legacy _active_sessions in-memory fallback.
    """

    async def create_session(self, session: SandboxSession) -> str:
        """Persist a new sandbox session. Returns session_id."""
        ...

    async def get_session(self, session_id: str) -> SandboxSession | None:
        """Load a session by ID. Returns None if not found or expired."""
        ...

    async def update_state(
        self,
        session_id: str,
        new_state: SessionState,
        *,
        extra_fields: dict[str, Any] | None = None,
    ) -> None:
        """Update session state."""
        ...

    async def update_overlay(
        self,
        session_id: str,
        overlay_files: dict[str, str],
        diff_summary: list[dict[str, Any]],
    ) -> None:
        """Update overlay files and transition to REVIEWING."""
        ...

    async def record_decision(
        self,
        session_id: str,
        *,
        action: CommitAction,
        attorney_uid: str,
        firm_id: str,
        selected_files: list[str] | None = None,
        rejection_reason: str = "",
        result_summary: dict[str, Any] | None = None,
    ) -> str:
        """Record an immutable decision. Returns decision ID."""
        ...

    async def get_decisions(self, session_id: str) -> list[dict[str, Any]]:
        """Retrieve all decisions for a session."""
        ...

    async def expire_session(self, session_id: str) -> None:
        """Mark a session as expired (soft delete)."""
        ...

    async def session_exists(self, session_id: str) -> bool:
        """Check if a session document exists."""
        ...

    async def list_active_sessions(
        self,
        attorney_uid: str | None = None,
        matter_id: str | None = None,
        *,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """List active (non-terminal) sessions."""
        ...
