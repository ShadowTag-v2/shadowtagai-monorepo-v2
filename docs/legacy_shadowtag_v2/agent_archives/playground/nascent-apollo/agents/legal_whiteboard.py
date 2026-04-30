# agents/legal_whiteboard.py
import json
from datetime import datetime
from pathlib import Path

# Adjusted path to be relative to the workspace root if run from agents/
# Assuming this runs from project root context usually, but using distinct absolute path safety is valid.
# Usage: Persisted in Git.
WHITEBOARD_PATH = Path("whiteboard/legal_state.json")


class LegalWhiteboard:
    """Single source of truth for the evolving legal agent. Persisted in Git."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load()
        return cls._instance

    def _load(self):
        if WHITEBOARD_PATH.exists():
            try:
                self.state = json.loads(WHITEBOARD_PATH.read_text())
            except:
                self._init_state()
        else:
            self._init_state()

    def _init_state(self):
        self.state = {
            "version": "0.1.0",
            "level": 0,
            "last_updated": None,
            "knowledge": [],
            "patterns": [],
            "optimizations": [],
            "self_improvements": [],
            "spawned_agents": [],
            "performance_log": [],
        }
        self._save()

    def _save(self):
        self.state["last_updated"] = datetime.utcnow().isoformat() + "Z"
        if not WHITEBOARD_PATH.parent.exists():
            WHITEBOARD_PATH.parent.mkdir(parents=True, exist_ok=True)
        WHITEBOARD_PATH.write_text(json.dumps(self.state, indent=2))

    def record_knowledge(self, insight: str, source: str = "task"):
        self.state["knowledge"].append({"insight": insight, "source": source, "ts": datetime.utcnow().isoformat() + "Z"})
        self._save()

    def record_pattern(self, pattern: str, accuracy: float):
        self.state["patterns"].append({"pattern": pattern, "accuracy": accuracy, "ts": datetime.utcnow().isoformat() + "Z"})
        if self.state["level"] < 1 and len(self.state["patterns"]) >= 10:
            self.state["level"] = 1
        self._save()

    def propose_optimization(self, suggestion: str, projected_roi: float):
        entry = {"suggestion": suggestion, "projected_roi": projected_roi, "applied": False}
        self.state["optimizations"].append(entry)
        if self.state["level"] < 2:
            self.state["level"] = 2
        self._save()
        return entry

    def mark_applied(self, optimization_id: int):
        if optimization_id < len(self.state["optimizations"]):
            self.state["optimizations"][optimization_id]["applied"] = True
            if self.state["level"] < 3:
                self.state["level"] = 3
            self._save()

    def log_performance(self, task: str, latency_ms: float, cost_usd: float):
        self.state["performance_log"].append(
            {"task": task, "latency_ms": latency_ms, "cost_usd": cost_usd, "ts": datetime.utcnow().isoformat() + "Z"}
        )
        self._save()


# Global singleton
whiteboard = LegalWhiteboard()
