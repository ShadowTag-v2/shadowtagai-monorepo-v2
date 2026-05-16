# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
# agents/legal_whiteboard.py
import json
from datetime import datetime, UTC
from pathlib import Path

WHITEBOARD_PATH = Path(__file__).parent.parent / "whiteboard" / "legal_state.json"


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
            except json.JSONDecodeError:
                self._init_state()
        else:
            self._init_state()

    def _init_state(self):
        self.state = {
            "version": "0.1.0",
            "level": 0,
            "last_updated": None,
            "beads": [],  # Tactical lessons learned (Memory Beads)
            "thinking_traces": [],  # Gemini Thinking traces
            "patterns": [],
            "optimizations": [],
            "self_improvements": [],
            "spawned_agents": [],
            "performance_log": [],
        }

    def _save(self):
        self.state["last_updated"] = datetime.now(UTC).isoformat() + "Z"
        WHITEBOARD_PATH.parent.mkdir(parents=True, exist_ok=True)
        WHITEBOARD_PATH.write_text(json.dumps(self.state, indent=2))

    def record_bead(self, insight: str, source: str = "task", thinking_trace: str = None):
        """Records a 'memory bead' and optional thinking trace."""
        entry = {"insight": insight, "source": source, "ts": datetime.now(UTC).isoformat() + "Z"}
        if thinking_trace:
            entry["thinking_trace"] = thinking_trace
            self.state["thinking_traces"].append({"id": len(self.state["beads"]), "trace": thinking_trace})
        self.state["beads"].append(entry)
        self._save()

    def record_pattern(self, pattern: str, accuracy: float):
        self.state["patterns"].append({"pattern": pattern, "accuracy": accuracy, "ts": datetime.now(UTC).isoformat() + "Z"})
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
            {"task": task, "latency_ms": latency_ms, "cost_usd": cost_usd, "ts": datetime.now(UTC).isoformat() + "Z"}
        )
        self._save()


# Global singleton
whiteboard = LegalWhiteboard()
