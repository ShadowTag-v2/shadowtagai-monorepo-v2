# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""OrbStack Sandbox — Isolated container execution for code verification.

Architecture (ported from Claude Code speculation.ts patterns):
  - Copy-on-Write Overlay: Workspace files are mounted read-only;
    all writes go to an ephemeral overlay directory.
  - Container Lifecycle: Deterministic create → execute → verify → destroy.
  - Filesystem Merge: Validated overlay changes are surgically copied back
    to the host workspace (speculation.ts `copyOverlayToMain` pattern).
  - Security: Tool whitelist enforcement, timeout, resource limits.

Public API:
  - SandboxConfig: Container configuration
  - SandboxResult: Execution result with overlay diff
  - ContainerLifecycle: State enum for container lifecycle
  - SandboxEngine: Main orchestrator
  - create_sandbox: Convenience factory
"""

from orbstack_sandbox.engine import (
    ContainerLifecycle,
    SandboxConfig,
    SandboxEngine,
    SandboxResult,
    create_sandbox,
)
from orbstack_sandbox.overlay import (
    OverlayDiff,
    OverlayManager,
)

__all__ = [
    # Core engine
    "SandboxEngine",
    "SandboxConfig",
    "SandboxResult",
    "ContainerLifecycle",
    "create_sandbox",
    # Overlay management
    "OverlayManager",
    "OverlayDiff",
]
