# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

class Verdict:
    def __init__(self):
        self.q = []

    def add(self, t, dl, prio):
        """Add task with deadline and priority."""
        self.q.append({"t": t, "dl": dl, "p": prio, "k": 0, "d": False})

    def tick(self, now):
        """Update priorities based on deadline proximity."""
        for i in self.q:
            if i["d"]:
                continue
            if now >= i["dl"]:
                i["k"] = 2  # Overdue
            elif (i["dl"] - now) <= 900:
                i["k"] = 1  # Urgent (15m)

    def next(self):
        """Get next highest priority task."""
        u = [x for x in self.q if not x["d"]]
        if not u:
            return None
        # Sort by urgency (k) descending, then priority (p) descending
        u.sort(key=lambda x: (-x["k"], -x["p"]))
        return u[0]

    def done(self, t):
        """Mark task as done."""
        for i in self.q:
            if i["t"] == t:
                i["d"] = True
                return True
        return False
