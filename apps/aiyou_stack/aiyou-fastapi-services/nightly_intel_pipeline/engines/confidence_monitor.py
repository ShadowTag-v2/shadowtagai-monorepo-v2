"""Confidence Monitor - SOP-C Decision Protocol
Lowest-Confidence Check for Auto-Triggering Branch/Review

PRISM Integration: Identifies lowest-confidence tokens to predict errors
with 75% accuracy. Triggers automatic review or branching at critical points.

Based on Ultrathink synthesis for PNKLN quality control.
"""

import math
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Union

import structlog

try:
    import numpy as np

    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

logger = structlog.get_logger(__name__)


class ConfidenceLevel(Enum):
    """Confidence level classifications"""

    CRITICAL = "critical"  # Requires immediate review
    LOW = "low"  # Needs attention
    MODERATE = "moderate"  # Acceptable
    HIGH = "high"  # Confident
    VERY_HIGH = "very_high"  # Highly confident


class ActionType(Enum):
    """Actions triggered by confidence monitoring"""

    PROCEED = "proceed"  # Continue normally
    FLAG_REVIEW = "flag_review"  # Flag for human review
    BRANCH = "branch"  # Create alternative branch
    ESCALATE = "escalate"  # Escalate to senior model
    REJECT = "reject"  # Reject and retry


@dataclass
class ConfidenceResult:
    """Result of confidence analysis"""

    overall_confidence: float
    min_confidence: float
    min_confidence_position: int
    level: ConfidenceLevel
    action: ActionType
    critical_positions: list[int]
    reasoning: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "overall_confidence": self.overall_confidence,
            "min_confidence": self.min_confidence,
            "min_confidence_position": self.min_confidence_position,
            "level": self.level.value,
            "action": self.action.value,
            "critical_positions": self.critical_positions,
            "reasoning": self.reasoning,
            "metadata": self.metadata,
        }


@dataclass
class MonitoringStats:
    """Statistics from confidence monitoring"""

    total_analyzed: int = 0
    critical_count: int = 0
    low_count: int = 0
    reviews_triggered: int = 0
    branches_created: int = 0
    escalations: int = 0
    average_confidence: float = 0.0
    error_prediction_accuracy: float = 0.75  # Target: 75%

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "total_analyzed": self.total_analyzed,
            "critical_count": self.critical_count,
            "low_count": self.low_count,
            "reviews_triggered": self.reviews_triggered,
            "branches_created": self.branches_created,
            "escalations": self.escalations,
            "average_confidence": self.average_confidence,
            "error_prediction_accuracy": self.error_prediction_accuracy,
        }


# Confidence Monitor Configuration
CONFIDENCE_CONFIG = {
    # Thresholds for confidence levels
    "thresholds": {
        "critical": 0.3,  # Below this = critical
        "low": 0.5,  # Below this = low
        "moderate": 0.7,  # Below this = moderate
        "high": 0.9,  # Below this = high, above = very_high
    },
    # Action triggers
    "actions": {
        "critical_action": ActionType.ESCALATE,
        "low_action": ActionType.FLAG_REVIEW,
        "multiple_critical_threshold": 3,  # Number of critical positions to trigger branch
        "branch_action": ActionType.BRANCH,
    },
    # Analysis settings
    "analysis": {
        "window_size": 10,  # Tokens to consider around minimum
        "cumulative_threshold": 0.4,  # Cumulative low-confidence threshold
        "track_positions": True,  # Track position of low-confidence tokens
        "max_critical_positions": 10,  # Maximum positions to track
    },
    # SOP-C Integration
    "sop_c": {
        "enabled": True,
        "error_prediction_target": 0.75,  # 75% error prediction accuracy
        "auto_branch_threshold": 0.25,  # Auto-branch below this confidence
        "review_queue_size": 100,  # Maximum review queue size
    },
}


class ConfidenceMonitor:
    """SOP-C Confidence Monitor

    Monitors token-level confidence to identify potential errors before they occur.
    Implements the Lowest-Confidence Check for 75% error prediction accuracy.

    Key Features:
    - Token-level confidence analysis
    - Critical position identification
    - Automatic action triggering (review, branch, escalate)
    - Error prediction tracking

    PRISM Integration:
    - Auto-trigger branch at lowest-confidence tokens
    - 75% error prediction accuracy target
    - SOP-C Decision Protocol compliance

    Usage:
        monitor = ConfidenceMonitor()
        result = monitor.analyze(logits)
        if result.action == ActionType.ESCALATE:
            # Handle escalation
    """

    def __init__(
        self,
        config: dict | None = None,
        on_critical: Callable[[ConfidenceResult], None] | None = None,
        on_low: Callable[[ConfidenceResult], None] | None = None,
    ):
        """Initialize Confidence Monitor

        Args:
            config: Optional configuration override
            on_critical: Callback for critical confidence events
            on_low: Callback for low confidence events

        """
        self.config = config or CONFIDENCE_CONFIG
        self.thresholds = self.config["thresholds"]
        self.actions = self.config["actions"]
        self.analysis = self.config["analysis"]
        self.sop_c = self.config["sop_c"]

        # Callbacks
        self.on_critical = on_critical
        self.on_low = on_low

        # Statistics
        self._stats = MonitoringStats()
        self._confidence_history: list[float] = []
        self._error_predictions: list[tuple[int, bool]] = []  # (position, was_error)

        # Review queue
        self._review_queue: list[ConfidenceResult] = []

        logger.info(
            "confidence_monitor_initialized",
            critical_threshold=self.thresholds["critical"],
            sop_c_enabled=self.sop_c["enabled"],
        )

    def analyze(
        self,
        logits: Union[list, "np.ndarray"] | None = None,
        probs: Union[list, "np.ndarray"] | None = None,
        confidences: list[float] | None = None,
        context: str | None = None,
        sequence_id: str | None = None,
    ) -> ConfidenceResult:
        """Analyze confidence levels and determine action

        Args:
            logits: Model output logits [seq_len, vocab_size] or [batch, seq_len, vocab_size]
            probs: Probability distribution (alternative to logits)
            confidences: Pre-computed confidence scores
            context: Optional context for analysis
            sequence_id: Optional identifier for tracking

        Returns:
            ConfidenceResult with analysis and recommended action

        """
        # Compute confidence scores
        if confidences is not None:
            conf_scores = confidences
        elif logits is not None:
            conf_scores = self._compute_confidence_from_logits(logits)
        elif probs is not None:
            conf_scores = self._compute_confidence_from_probs(probs)
        else:
            raise ValueError("Must provide logits, probs, or confidences")

        # Find minimum confidence and position
        min_conf = min(conf_scores)
        min_pos = conf_scores.index(min_conf)
        overall_conf = sum(conf_scores) / len(conf_scores)

        # Find all critical positions
        critical_positions = [i for i, c in enumerate(conf_scores) if c < self.thresholds["low"]][
            : self.analysis["max_critical_positions"]
        ]

        # Determine confidence level
        level = self._classify_level(min_conf)

        # Determine action
        action = self._determine_action(level, critical_positions)

        # Build reasoning
        reasoning = self._build_reasoning(
            min_conf,
            min_pos,
            level,
            action,
            len(critical_positions),
            context,
        )

        # Create result
        result = ConfidenceResult(
            overall_confidence=overall_conf,
            min_confidence=min_conf,
            min_confidence_position=min_pos,
            level=level,
            action=action,
            critical_positions=critical_positions,
            reasoning=reasoning,
            metadata={
                "sequence_id": sequence_id,
                "context": context,
                "token_count": len(conf_scores),
                "timestamp": datetime.now().isoformat(),
            },
        )

        # Update statistics
        self._update_stats(result)

        # Trigger callbacks
        self._trigger_callbacks(result)

        # Add to review queue if needed
        if action in [ActionType.FLAG_REVIEW, ActionType.BRANCH, ActionType.ESCALATE]:
            self._add_to_review_queue(result)

        logger.debug(
            "confidence_analyzed",
            min_confidence=f"{min_conf:.3f}",
            level=level.value,
            action=action.value,
            critical_count=len(critical_positions),
        )

        return result

    def _compute_confidence_from_logits(self, logits: Union[list, "np.ndarray"]) -> list[float]:
        """Compute confidence scores from logits"""
        if NUMPY_AVAILABLE:
            logits = np.array(logits)

            # Handle different shapes
            if len(logits.shape) == 3:
                # [batch, seq_len, vocab] - take first batch
                logits = logits[0]

            # Softmax to get probabilities
            exp_logits = np.exp(logits - np.max(logits, axis=-1, keepdims=True))
            probs = exp_logits / np.sum(exp_logits, axis=-1, keepdims=True)

            # Confidence = max probability (how certain is the model)
            confidences = np.max(probs, axis=-1).tolist()
        else:
            # Pure Python fallback
            confidences = []
            for token_logits in logits:
                if isinstance(token_logits, (list, tuple)):
                    max_logit = max(token_logits)
                    exp_logits = [math.exp(l - max_logit) for l in token_logits]  # noqa: E741
                    sum_exp = sum(exp_logits)
                    probs = [e / sum_exp for e in exp_logits]
                    confidences.append(max(probs))
                else:
                    confidences.append(float(token_logits))

        return confidences

    def _compute_confidence_from_probs(self, probs: Union[list, "np.ndarray"]) -> list[float]:
        """Compute confidence scores from probabilities"""
        if NUMPY_AVAILABLE:
            probs = np.array(probs)
            if len(probs.shape) == 3:
                probs = probs[0]
            return np.max(probs, axis=-1).tolist()
        return [max(p) if isinstance(p, (list, tuple)) else float(p) for p in probs]

    def _classify_level(self, min_confidence: float) -> ConfidenceLevel:
        """Classify confidence level"""
        if min_confidence < self.thresholds["critical"]:
            return ConfidenceLevel.CRITICAL
        if min_confidence < self.thresholds["low"]:
            return ConfidenceLevel.LOW
        if min_confidence < self.thresholds["moderate"]:
            return ConfidenceLevel.MODERATE
        if min_confidence < self.thresholds["high"]:
            return ConfidenceLevel.HIGH
        return ConfidenceLevel.VERY_HIGH

    def _determine_action(
        self,
        level: ConfidenceLevel,
        critical_positions: list[int],
    ) -> ActionType:
        """Determine action based on confidence level"""
        # Check for multiple critical positions
        if len(critical_positions) >= self.actions["multiple_critical_threshold"]:
            return self.actions["branch_action"]

        # SOP-C auto-branch
        if self.sop_c["enabled"] and level == ConfidenceLevel.CRITICAL:
            return ActionType.ESCALATE

        # Level-based actions
        if level == ConfidenceLevel.CRITICAL:
            return self.actions["critical_action"]
        if level == ConfidenceLevel.LOW:
            return self.actions["low_action"]
        return ActionType.PROCEED

    def _build_reasoning(
        self,
        min_conf: float,
        min_pos: int,
        level: ConfidenceLevel,
        action: ActionType,
        critical_count: int,
        context: str | None,
    ) -> str:
        """Build human-readable reasoning"""
        parts = [
            f"Minimum confidence {min_conf:.1%} at position {min_pos}.",
            f"Confidence level: {level.value.upper()}.",
        ]

        if critical_count > 1:
            parts.append(f"Found {critical_count} critical positions.")

        if action != ActionType.PROCEED:
            action_reasons = {
                ActionType.FLAG_REVIEW: "Flagged for human review due to low confidence.",
                ActionType.BRANCH: f"Creating alternative branch ({critical_count} critical points).",
                ActionType.ESCALATE: "Escalating to senior model (SOP-C protocol).",
                ActionType.REJECT: "Rejecting output for retry.",
            }
            parts.append(action_reasons.get(action, ""))

        if context:
            parts.append(f"Context: {context}")

        return " ".join(parts)

    def _update_stats(self, result: ConfidenceResult):
        """Update monitoring statistics"""
        self._stats.total_analyzed += 1
        self._confidence_history.append(result.min_confidence)

        if result.level == ConfidenceLevel.CRITICAL:
            self._stats.critical_count += 1
        elif result.level == ConfidenceLevel.LOW:
            self._stats.low_count += 1

        if result.action == ActionType.FLAG_REVIEW:
            self._stats.reviews_triggered += 1
        elif result.action == ActionType.BRANCH:
            self._stats.branches_created += 1
        elif result.action == ActionType.ESCALATE:
            self._stats.escalations += 1

        # Update running average
        if self._confidence_history:
            self._stats.average_confidence = sum(self._confidence_history) / len(
                self._confidence_history,
            )

        # Limit history size
        max_history = 10000
        if len(self._confidence_history) > max_history:
            self._confidence_history = self._confidence_history[-max_history:]

    def _trigger_callbacks(self, result: ConfidenceResult):
        """Trigger registered callbacks"""
        try:
            if result.level == ConfidenceLevel.CRITICAL and self.on_critical:
                self.on_critical(result)
            elif result.level == ConfidenceLevel.LOW and self.on_low:
                self.on_low(result)
        except Exception as e:
            logger.error("callback_error", error=str(e))

    def _add_to_review_queue(self, result: ConfidenceResult):
        """Add result to review queue"""
        if len(self._review_queue) >= self.sop_c["review_queue_size"]:
            self._review_queue.pop(0)  # Remove oldest
        self._review_queue.append(result)

    def get_review_queue(self) -> list[ConfidenceResult]:
        """Get current review queue"""
        return self._review_queue.copy()

    def clear_review_queue(self):
        """Clear review queue"""
        self._review_queue = []

    def record_error_outcome(self, position: int, was_error: bool):
        """Record actual error outcome for accuracy tracking

        Args:
            position: Position that was flagged
            was_error: Whether it actually was an error

        """
        self._error_predictions.append((position, was_error))

        # Limit history
        if len(self._error_predictions) > 1000:
            self._error_predictions = self._error_predictions[-1000:]

        # Update accuracy
        if self._error_predictions:
            correct = sum(1 for _, was in self._error_predictions if was)
            self._stats.error_prediction_accuracy = correct / len(self._error_predictions)

    def get_stats(self) -> MonitoringStats:
        """Get current monitoring statistics"""
        return self._stats

    def get_stats_dict(self) -> dict:
        """Get statistics as dictionary"""
        return self._stats.to_dict()

    def reset_stats(self):
        """Reset statistics"""
        self._stats = MonitoringStats()
        self._confidence_history = []
        self._error_predictions = []

    def generate_report(self) -> str:
        """Generate monitoring report"""
        stats = self._stats

        report = f"""
# Confidence Monitor Report
Generated: {datetime.now().isoformat()}

## Summary Statistics
- Total Sequences Analyzed: {stats.total_analyzed:,}
- Critical Confidence Events: {stats.critical_count:,}
- Low Confidence Events: {stats.low_count:,}
- Average Confidence: {stats.average_confidence:.1%}

## Actions Triggered
- Reviews Flagged: {stats.reviews_triggered:,}
- Branches Created: {stats.branches_created:,}
- Escalations: {stats.escalations:,}

## SOP-C Performance
- Error Prediction Accuracy: {stats.error_prediction_accuracy:.1%}
- Target Accuracy: {self.sop_c["error_prediction_target"]:.1%}
- Review Queue Size: {len(self._review_queue)}/{self.sop_c["review_queue_size"]}

## Configuration
- Critical Threshold: {self.thresholds["critical"]:.1%}
- Low Threshold: {self.thresholds["low"]:.1%}
- Auto-Branch Threshold: {self.sop_c["auto_branch_threshold"]:.1%}
"""
        return report.strip()


class SOPCDecisionProtocol:
    """SOP-C Decision Protocol Implementation

    Implements the full Standard Operating Procedure for Confidence-based
    decision making with branching and review capabilities.
    """

    def __init__(
        self,
        monitor: ConfidenceMonitor | None = None,
        branch_handler: Callable[[ConfidenceResult], Any] | None = None,
        escalation_handler: Callable[[ConfidenceResult], Any] | None = None,
    ):
        """Initialize SOP-C Protocol

        Args:
            monitor: ConfidenceMonitor instance
            branch_handler: Handler for branch creation
            escalation_handler: Handler for escalations

        """
        self.monitor = monitor or ConfidenceMonitor()
        self.branch_handler = branch_handler
        self.escalation_handler = escalation_handler

        self._decision_log: list[dict] = []

    def execute(
        self,
        logits: Union[list, "np.ndarray"],
        context: str = "inference",
        sequence_id: str | None = None,
    ) -> dict:
        """Execute SOP-C decision protocol

        Args:
            logits: Model output logits
            context: Execution context
            sequence_id: Sequence identifier

        Returns:
            Decision result with action taken

        """
        # Analyze confidence
        result = self.monitor.analyze(logits=logits, context=context, sequence_id=sequence_id)

        # Execute action
        action_result = None

        if result.action == ActionType.BRANCH and self.branch_handler:
            action_result = self.branch_handler(result)
        elif result.action == ActionType.ESCALATE and self.escalation_handler:
            action_result = self.escalation_handler(result)

        # Log decision
        decision = {
            "timestamp": datetime.now().isoformat(),
            "sequence_id": sequence_id,
            "context": context,
            "confidence": result.min_confidence,
            "level": result.level.value,
            "action": result.action.value,
            "action_result": action_result,
        }
        self._decision_log.append(decision)

        # Limit log size
        if len(self._decision_log) > 10000:
            self._decision_log = self._decision_log[-10000:]

        return decision

    def get_decision_log(self) -> list[dict]:
        """Get decision log"""
        return self._decision_log.copy()

    def clear_decision_log(self):
        """Clear decision log"""
        self._decision_log = []


# Convenience functions
def analyze_confidence(
    logits: Union[list, "np.ndarray"],
    threshold: float = 0.3,
) -> ConfidenceResult:
    """Quick confidence analysis

    Usage:
        result = analyze_confidence(model_logits)
        if result.action != ActionType.PROCEED:
            handle_low_confidence(result)
    """
    config = CONFIDENCE_CONFIG.copy()
    config["thresholds"]["critical"] = threshold
    monitor = ConfidenceMonitor(config=config)
    return monitor.analyze(logits=logits)


def check_lowest_confidence(
    confidences: list[float],
    threshold: float = 0.3,
) -> tuple[bool, int, float]:
    """Check for lowest confidence token

    Returns:
        Tuple of (needs_review, position, confidence)

    Usage:
        needs_review, pos, conf = check_lowest_confidence([0.9, 0.2, 0.8])
        # needs_review=True, pos=1, conf=0.2

    """
    min_conf = min(confidences)
    min_pos = confidences.index(min_conf)
    needs_review = min_conf < threshold

    return needs_review, min_pos, min_conf
