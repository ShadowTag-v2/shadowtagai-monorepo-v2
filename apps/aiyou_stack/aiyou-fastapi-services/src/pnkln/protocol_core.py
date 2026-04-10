"""
PNKLN CORE PROTOCOL V2.0 (Real Mode)
-----------------------------------
This module implements the core Pnkln logic blocks:
1. Verdict Engine (p-verdict)

Original Source: 'Pacific Edge Protocol' Dump.
"""


# ---------------------------------------------------------
# P-VERDICT-CORE: Task Flow with Locks/Escrows
# ---------------------------------------------------------


class Verdict:
    def __init__(self):
        self.q = []

    def add(self, t, dl, prio):
        """Add task to queue. t=tag, dl=deadline, prio=priority."""
        self.q.append({"t": t, "dl": dl, "p": prio, "k": 0, "d": False})

    def tick(self, now):
        """Update task escalation status (k)."""
        for i in self.q:
            if i["d"]:
                continue
            if now >= i["dl"]:
                i["k"] = 2  # Locked/Escalated
            elif (i["dl"] - now) <= 900:
                i["k"] = 1  # Warning

    def next_task(self):
        """Get next highest priority/escalated task."""
        u = [x for x in self.q if not x["d"]]
        u.sort(key=lambda x: (-x["k"], -x["p"]))
        return u[0] if u else None

    def done(self, t):
        """Mark task as done."""
        for i in self.q:
            if i["t"] == t:
                i["d"] = True
                return True
        return False
