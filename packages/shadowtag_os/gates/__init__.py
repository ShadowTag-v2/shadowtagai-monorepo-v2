# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Quality gates subsystem — re-exports from src/gates."""

from packages.shadowtag_os.gates.gate_adapter import GateAdapter, GateCheckResult

__all__ = [
    "GateAdapter",
    "GateCheckResult",
]
