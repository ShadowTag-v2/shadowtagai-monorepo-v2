# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Pewter Ledger Plan Capping — P1 #8."""

from __future__ import annotations
import logging, time
from dataclasses import dataclass, field
from datetime import UTC, datetime

logger = logging.getLogger("agnt.pewter_ledger")

MAX_DEPTH = 5
MAX_WIDTH = 8
MAX_TASKS = 50
MAX_SECONDS = 120


@dataclass
class PlanTask:
    name: str
    depth: int = 0
    parent: str = ""
    status: str = "pending"
    estimated_minutes: float = 0
    created_at: str = ""


@dataclass
class PlanReport:
    total_tasks: int = 0
    max_depth_used: int = 0
    max_width_used: int = 0
    planning_seconds: float = 0
    is_capped: bool = False
    cap_reason: str = ""
    tasks: list[PlanTask] = field(default_factory=list)


class PewterLedger:
    """Plan capping — prevents runaway decomposition with 4 hard limits."""

    def __init__(self, max_depth=MAX_DEPTH, max_width=MAX_WIDTH, max_tasks=MAX_TASKS, max_seconds=MAX_SECONDS):
        self.max_depth = max_depth
        self.max_width = max_width
        self.max_tasks = max_tasks
        self.max_seconds = max_seconds
        self._tasks: list[PlanTask] = []
        self._start: float = 0
        self._active = False

    def start_planning(self):
        self._start = time.monotonic()
        self._active = True
        self._tasks = []

    def add_task(self, name: str, depth: int = 0, parent: str = "", est_min: float = 0) -> bool:
        if self.is_capped():
            return False
        self._tasks.append(PlanTask(name=name, depth=depth, parent=parent, estimated_minutes=est_min, created_at=datetime.now(UTC).isoformat()))
        return True

    def is_capped(self) -> bool:
        return self._check_caps()[1] != ""

    def force_commit(self) -> PlanReport:
        self._active = False
        capped, reason = self._check_caps()
        return PlanReport(
            total_tasks=len(self._tasks),
            max_depth_used=max((t.depth for t in self._tasks), default=0),
            max_width_used=self._max_width(),
            planning_seconds=time.monotonic() - self._start if self._start else 0,
            is_capped=capped,
            cap_reason=reason,
            tasks=list(self._tasks),
        )

    def _check_caps(self) -> tuple[bool, str]:
        if len(self._tasks) >= self.max_tasks:
            return True, f"Tasks({len(self._tasks)})>={self.max_tasks}"
        d = max((t.depth for t in self._tasks), default=0)
        if d >= self.max_depth:
            return True, f"Depth({d})>={self.max_depth}"
        w = self._max_width()
        if w >= self.max_width:
            return True, f"Width({w})>={self.max_width}"
        if self._active and self._start and time.monotonic() - self._start >= self.max_seconds:
            return True, f"Time>={self.max_seconds}s"
        return False, ""

    def _max_width(self) -> int:
        if not self._tasks:
            return 0
        dc: dict[int, int] = {}
        for t in self._tasks:
            dc[t.depth] = dc.get(t.depth, 0) + 1
        return max(dc.values())
