# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""CounselConduit Sandbox Session API.

Phase 3 entry point — provides isolated CoW overlay sessions for attorney
review of AI-generated document edits before committing to production Firestore.

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

Public API:
  - SandboxSession: Session lifecycle management
  - SessionConfig: Configuration dataclass
  - SessionState: State machine for session lifecycle
  - CommitAction: Accept/Reject/PartialAccept enum
"""

from apps.counselconduit.api.sandbox.session import (
    CommitAction,
    SandboxSession,
    SessionConfig,
    SessionState,
)

__all__ = [
    "SandboxSession",
    "SessionConfig",
    "SessionState",
    "CommitAction",
]
