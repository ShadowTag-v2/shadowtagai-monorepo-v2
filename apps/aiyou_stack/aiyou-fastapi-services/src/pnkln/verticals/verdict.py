# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Pnkln Verdict Vertical
Task scheduler enforcing flow with locks/escrows and time escalations.
"""

from __future__ import annotations

from typing import Any


class Verdict:
    """Verdict Task Scheduler.
    Enforces task flow, deadlines (dl), and priorities (prio).
    Escalates kernel (k) state based on time proximity.
    """

    def __init__(self) -> None:
        self.q: list[dict[str, Any]] = []

    def add(self, t: str, dl: float, prio: int) -> None:
        """Add a task to the queue.
        t: Task ID/Name
        dl: Deadline (timestamp)
        prio: Priority (higher is more important)
        """
        self.q.append(
            {
                "t": t,
                "dl": dl,
                "p": prio,
                "k": 0,  # Kernel state: 0=Normal, 1=Urgent, 2=Overdue
                "d": False,  # Done flag
            },
        )

    def tick(self, now: float) -> None:
        """Update task states based on current time.
        Escalates 'k' (kernel) level as deadline approaches.
        """
        for i in self.q:
            if i["d"]:
                continue

            if now >= i["dl"]:
                i["k"] = 2  # Overdue
            elif (i["dl"] - now) <= 900:  # 15 minutes warning
                i["k"] = 1  # Urgent

    def next(self) -> dict[str, Any] | None:
        """Get the next highest priority task.
        Sorts by Kernel State (desc) then Priority (desc).
        """
        u = [x for x in self.q if not x["d"]]
        # Sort: Primary=k (desc), Secondary=p (desc)
        u.sort(key=lambda x: (-x["k"], -x["p"]))

        return u[0] if u else None

    def done(self, t: str) -> bool:
        """Mark a task as done."""
        for i in self.q:
            if i["t"] == t:
                i["d"] = True
                return True
        return False


# Global Instance
V = Verdict()
