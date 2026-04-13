"""
Layer 21: IQ 160 Lock Performance Monitoring
=============================================

Extracted from layers.py monolith per Rich Hickey doctrine.
"""

import logging
from datetime import datetime
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)


# ============================================================================
# LAYER 21: IQ 160 LOCK PERFORMANCE MONITORING
# ============================================================================


class JudgeArchitectureMonitor:
    """
    Layer 21: Monitor decision quality under IQ 160 permanent lock.

    Tracks:
    - Decision accuracy (82% baseline → 95% target)
    - Doctrine alignment (70% baseline → 95% target)
    - Regulatory gap detection (60% → 90%)
    - Processing time (speed vs quality tradeoff)
    """

    def __init__(self):
        self.iq_locked = True
        self.iq_lock_level = 160
        self.decision_log = []
        self.iq_160_metrics = {
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
    ):
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

        return {
            "decision_accuracy_mean": float(np.mean(self.iq_160_metrics["decision_accuracy"])),
            "doctrine_alignment_mean": float(np.mean(self.iq_160_metrics["doctrine_alignment"])),
            "regulatory_gaps_per_decision": float(
                np.mean(self.iq_160_metrics["regulatory_gap_detection"])
            ),
            "processing_time_p50_ms": float(
                np.percentile(self.iq_160_metrics["processing_time_ms"], 50)
            ),
            "processing_time_p95_ms": float(
                np.percentile(self.iq_160_metrics["processing_time_ms"], 95)
            ),
            "total_decisions": len(self.iq_160_metrics["decision_accuracy"]),
        }
