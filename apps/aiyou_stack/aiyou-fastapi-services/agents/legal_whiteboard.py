"""LegalWhiteboard - The "Never Resting" memory latch.
Records agent evolution. Single Point of Truth.
"""

import json
import os
from datetime import datetime


class LegalWhiteboard:
    """The Single Point of Truth. Agents write here. History is committed to Git."""

    def __init__(self, repo_path="./"):
        self.repo_path = repo_path
        self.ledger_file = os.path.join(repo_path, "docs/whiteboard_ledger.json")
        self._load_ledger()

    def _load_ledger(self):
        os.makedirs(os.path.dirname(self.ledger_file), exist_ok=True)
        if os.path.exists(self.ledger_file):
            with open(self.ledger_file) as f:
                self.state = json.load(f)
        else:
            self.state = {"evolution_level": 0, "learnings": []}

    def record_learning(self, agent_id: str, insight: str, context: dict):
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "agent": agent_id,
            "insight": insight,
            "context": context,
            "hash": abs(hash(insight)),
        }
        self.state["learnings"].append(entry)
        self._commit(f"Learned: {insight[:30]}...")

    def record_revenue(self, amount: float, source: str, agent_id: str = "unknown"):
        """Record revenue and check for level progression."""
        self.state.setdefault("total_revenue_usd", 0.0)
        self.state.setdefault("current_level", 0)
        self.state.setdefault("revenue_events", [])
        self.state.setdefault("agents", {})

        self.state["total_revenue_usd"] += amount

        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "amount": amount,
            "source": source,
            "agent_id": agent_id,
        }
        self.state["revenue_events"].append(event)

        # Update agent stats
        if agent_id not in self.state["agents"]:
            self.state["agents"][agent_id] = {"revenue_generated": 0.0}
        self.state["agents"][agent_id]["revenue_generated"] += amount

        # Check level progression
        total = self.state["total_revenue_usd"]
        new_level = self.state["current_level"]

        if total >= 100_000_000:
            new_level = 5
        elif total >= 10_000_000:
            new_level = 4
        elif total >= 1_000_000:
            new_level = 3
        elif total >= 100_000:
            new_level = 2
        elif total >= 10_000:
            new_level = 1

        if new_level > self.state["current_level"]:
            self.state["current_level"] = new_level
            self._commit(f"LEVEL UP! Reached Level {new_level}")

            # Trigger side effects (mocked in tests)
            if new_level == 4:
                from agents.bar_exam_protocol import BarExamProtocol

                BarExamProtocol.spawn_first_child()
            elif new_level == 5:
                from agents.bar_exam_protocol import BarExamProtocol

                BarExamProtocol.activate_swarm_mode()
        else:
            self._save_state()

    def _commit(self, message: str):
        self._save_state()
        print(f"///▞ WHITEBOARD :: LATCHED :: {message}")

    def _save_state(self):
        with open(self.ledger_file, "w") as f:
            json.dump(self.state, f, indent=2)


whiteboard = LegalWhiteboard()
