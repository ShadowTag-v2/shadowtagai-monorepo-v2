"""
LegalWhiteboard - The "Never Resting" memory latch.
Records agent evolution. Single Point of Truth.
"""

import os
from datetime import datetime
import json


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
            "hash": abs(hash(insight))
        }
        self.state["learnings"].append(entry)
        self._commit(f"Learned: {insight[:30]}...")

    def _commit(self, message: str):
        with open(self.ledger_file, 'w') as f:
            json.dump(self.state, f, indent=2)
        print(f"///▞ WHITEBOARD :: LATCHED :: {message}")
