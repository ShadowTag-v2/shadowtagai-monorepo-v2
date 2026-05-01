# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""CounselConduit Sandbox Session API — Phase 4.

Provides isolated CoW overlay sessions for attorney review of AI-generated
document edits before committing to production Firestore.

Architecture:
  ┌─────────────┐    ┌──────────────┐    ┌────────────┐
  │ Attorney UI  │───▶│ SandboxSession│───▶│ CoW Overlay │
  │ (diff view)  │    │ (30min TTL)  │    │ (isolated)  │
  └─────────────┘    └──────────────┘    └──────┬─────┘
                                                 │
  ┌─────────────┐    ┌──────────────┐           ▼
  │ Accept/     │───▶│ Firestore    │    ┌───────────┐
  │ Reject      │    │ Commit       │◀───│ Diff View  │
  └─────────────┘    └──────────────┘    └───────────┘

  Phase 4 additions:
  - FirestoreSessionStore: Persistent session storage with 30-day TTL
  - SecurityError: Dedicated exception for trust-level violations

Public API:
  - SandboxSession: Session lifecycle management
  - SessionConfig: Configuration dataclass
  - SessionState: State machine for session lifecycle
  - CommitAction: Accept/Reject/PartialAccept enum
  - FirestoreSessionStore: Firestore-backed session persistence
  - SecurityError: Trust-level violation exception
"""

from apps.counselconduit.api.sandbox.firestore_session_store import (
    FirestoreSessionStore,
)
from apps.counselconduit.api.sandbox.session import (
    CommitAction,
    SandboxSession,
    SecurityError,
    SessionConfig,
    SessionState,
)

__all__ = [
    "CommitAction",
    "FirestoreSessionStore",
    "SandboxSession",
    "SecurityError",
    "SessionConfig",
    "SessionState",
]
