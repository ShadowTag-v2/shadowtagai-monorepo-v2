# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""IQ 160 performance monitor (Layer 21) and milestone tracker (Layer 19)."""

from __future__ import annotations

from datetime import datetime
from typing import Any


class JudgeArchitectureMonitor:
    """Layer 21: Monitor decision quality under IQ 160 permanent lock."""

    def __init__(self) -> None:
        self.iq_locked = True
        self.iq_lock_level = 160
        self.decision_log: list[dict[str, Any]] = []
        self.iq_160_metrics: dict[str, list[float]] = {
            "decision_accuracy": [],
            "doctrine_alignment": [],
            "regulatory_gap_detection": [],
            "processing_time_ms": [],
        }

    def log_decision(
        self,
        decision_id: str,
        decision_type: str,
        iq_level: int,
        outcome: dict[str, Any],
    ) -> None:
        """Log decision with quality metrics."""
        self.decision_log.append(
            {
                "decision_id": decision_id,
                "decision_type": decision_type,
                "iq_level": iq_level,
                "accuracy": outcome["accuracy"],
                "doctrine_alignment": outcome["doctrine_alignment"],
                "regulatory_gaps_detected": len(outcome["regulatory_gaps"]),
                "processing_time_ms": outcome["processing_time_ms"],
                "timestamp": datetime.now(),
            }
        )

        if iq_level == 160:
            self.iq_160_metrics["decision_accuracy"].append(outcome["accuracy"])
            self.iq_160_metrics["doctrine_alignment"].append(outcome["doctrine_alignment"])
            self.iq_160_metrics["regulatory_gap_detection"].append(len(outcome["regulatory_gaps"]))
            self.iq_160_metrics["processing_time_ms"].append(outcome["processing_time_ms"])

    def get_performance_summary(self) -> dict[str, Any]:
        """Get IQ 160 performance summary."""
        if not self.iq_160_metrics["decision_accuracy"]:
            return {"status": "No IQ 160 decisions logged yet"}

        accs = self.iq_160_metrics["decision_accuracy"]
        align = self.iq_160_metrics["doctrine_alignment"]
        gaps = self.iq_160_metrics["regulatory_gap_detection"]
        times = self.iq_160_metrics["processing_time_ms"]

        return {
            "decision_accuracy_mean": sum(accs) / len(accs),
            "doctrine_alignment_mean": sum(align) / len(align),
            "regulatory_gaps_per_decision": sum(gaps) / len(gaps),
            "processing_time_p50_ms": sorted(times)[len(times) // 2],
            "total_decisions": len(accs),
        }


class MilestoneTracker:
    """Layer 19: 30-60-90 day milestone tracker."""

    async def assess_impact(self, decision: Any) -> dict[str, Any]:
        """Assess decision impact on milestones."""
        return {
            "tasks": ["Update 30-60-90 tracker with new tasks from this decision"],
            "milestone_acceleration": 0,
            "milestone_delay": 0,
        }


__all__ = ["JudgeArchitectureMonitor", "MilestoneTracker"]
