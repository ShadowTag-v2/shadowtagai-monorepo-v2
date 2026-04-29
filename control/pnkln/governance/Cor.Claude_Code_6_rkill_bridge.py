# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""RKILL ↔ Cor.Claude_Code_6Engine bridge.

Provides ``RkillNotifier`` — a sync callable that satisfies the
``ceo_notifier: Callable[[GovernanceDecision], None]`` slot on
``Cor.Claude_Code_6Engine``.

When enforcement reaches L5_LOCKOUT, ``RkillNotifier`` fires
``RkillProtocol.execute()`` asynchronously:
  - Inside a running asyncio event loop (FastAPI/uvicorn): schedules
    via ``asyncio.ensure_future`` so it doesn't block the gate.
  - In a sync context (CLI, test, batch): runs via ``asyncio.run``.

Use ``build_engine()`` from ``Cor.Claude_Code_6_factory`` rather than instantiating
this class directly.
"""

from __future__ import annotations

import asyncio
import logging

from .Cor.Claude_Code_6_core import EnforcementLevel, GovernanceDecision
from .rkill import RkillConfig, RkillProtocol

logger = logging.getLogger("Cor.Claude_Code_6_rkill_bridge")


class RkillNotifier:
    """Sync ceo_notifier that auto-triggers RKILL on L5_LOCKOUT verdicts."""

    def __init__(self, cfg: RkillConfig) -> None:
        self._protocol = RkillProtocol(cfg)

    def __call__(self, decision: GovernanceDecision) -> None:
        if not decision.control:
            return
        if decision.control.enforcement_level < EnforcementLevel.L5_LOCKOUT:
            # L4_CONTAIN only notifies CEO — no lockout.
            logger.warning(
                "[bridge] CEO notified (L4): violation=%s decision=%s",
                decision.event.violation_type.value,
                decision.decision_id,
            )
            return

        logger.critical(
            "[bridge] L5_LOCKOUT — scheduling RKILL: violation=%s decision=%s",
            decision.event.violation_type.value,
            decision.decision_id,
        )
        triggered_by = f"Cor.Claude_Code_6-auto:{decision.event.violation_type.value}"
        self._fire(triggered_by)

    def _fire(self, triggered_by: str) -> None:
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self._protocol.execute(triggered_by))
        except RuntimeError:
            # No running loop — sync context (CLI, test).
            asyncio.run(self._protocol.execute(triggered_by))
