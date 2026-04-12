"""
Sensor Layer - Biosignal Detection
Handles blink tracking, pupil dynamics, HRV monitoring, and IMU analysis
"""

from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import StrEnum

import numpy as np


class FatigueLevel(StrEnum):
    """Fatigue classification levels"""

    FRESH = "fresh"  # No fatigue detected
    MILD = "mild"  # Early fatigue signs
    MODERATE = "moderate"  # Clear fatigue indicators
    SEVERE = "severe"  # High fatigue, intervention needed
    CRITICAL = "critical"  # Dangerous levels, stop usage


@dataclass
class SensorReading:
    """Base sensor reading with timestamp"""

    timestamp: datetime
    value: float
    confidence: float = 1.0  # 0-1 confidence in reading
    metadata: dict = field(default_factory=dict)


@dataclass
class BlinkMetrics:
    """Blink detection metrics"""

    blink_rate: float  # blinks per minute
    blink_duration: float  # avg milliseconds
    incomplete_blinks: int  # count in last minute
    last_blink: datetime
    baseline_rate: float = 15.0  # normal: 15-20 bpm


class BlinkDetector:
    """
    Detects blink rate and patterns from eye-tracking cameras

    Fatigue Indicators:
    - Reduced blink rate (<10 bpm = screen-induced dry eye)
    - Increased incomplete blinks
    - Prolonged blink duration (>200ms)
    """

    def __init__(self, window_seconds: int = 60, baseline_rate: float = 15.0):
        self.window_seconds = window_seconds
        self.baseline_rate = baseline_rate
        self.blink_events: deque = deque(maxlen=100)  # last 100 blinks
        self.incomplete_blinks: deque = deque(maxlen=50)

    def process_frame(self, eye_closure: float, timestamp: datetime) -> SensorReading | None:
        """
        Process single video frame for blink detection

        Args:
            eye_closure: 0.0 (fully open) to 1.0 (fully closed)
            timestamp: Frame timestamp

        Returns:
            SensorReading if blink detected, else None
        """
        # Blink detection threshold (>0.7 = likely blink)
        if eye_closure > 0.7:
            # Check if this is a new blink (>100ms since last)
            if (
                not self.blink_events
                or (timestamp - self.blink_events[-1]["start"]).total_seconds() > 0.1
            ):
                blink_event = {
                    "start": timestamp,
                    "end": None,
                    "peak_closure": eye_closure,
                    "complete": False,
                }
                self.blink_events.append(blink_event)

        # Close ongoing blink when eye reopens
        elif self.blink_events and self.blink_events[-1]["end"] is None:
            blink = self.blink_events[-1]
            blink["end"] = timestamp
            duration_ms = (blink["end"] - blink["start"]).total_seconds() * 1000

            # Classify blink completeness
            if duration_ms >= 100 and duration_ms <= 400:
                blink["complete"] = True
            else:
                self.incomplete_blinks.append(timestamp)

            return SensorReading(
                timestamp=timestamp,
                value=duration_ms,
                confidence=0.9 if blink["complete"] else 0.6,
                metadata={"complete": blink["complete"]},
            )

        return None

    def get_metrics(self) -> BlinkMetrics:
        """Calculate current blink metrics"""
        now = datetime.utcnow()
        recent_window = now - timedelta(seconds=self.window_seconds)

        # Filter recent blinks
        recent_blinks = [b for b in self.blink_events if b["end"] and b["end"] >= recent_window]

        recent_incomplete = [b for b in self.incomplete_blinks if b >= recent_window]

        # Calculate metrics
        blink_rate = (len(recent_blinks) / self.window_seconds) * 60  # per minute

        avg_duration = (
            np.mean([(b["end"] - b["start"]).total_seconds() * 1000 for b in recent_blinks])
            if recent_blinks
            else 0.0
        )

        last_blink = recent_blinks[-1]["end"] if recent_blinks else None

        return BlinkMetrics(
            blink_rate=blink_rate,
            blink_duration=avg_duration,
            incomplete_blinks=len(recent_incomplete),
            last_blink=last_blink or now,
            baseline_rate=self.baseline_rate,
        )

    def get_fatigue_score(self) -> float:
        """
        Calculate fatigue score from blink metrics

        Returns:
            0.0 (fresh) to 1.0 (critical fatigue)
        """
        metrics = self.get_metrics()
        score = 0.0

        # Low blink rate penalty (dry eyes, intense focus)
        if metrics.blink_rate < 10:
            score += 0.3
        elif metrics.blink_rate < 12:
            score += 0.15

        # Incomplete blinks penalty
        if metrics.incomplete_blinks > 3:
            score += 0.2
        elif metrics.incomplete_blinks > 1:
            score += 0.1

        # Prolonged blink duration penalty (drowsiness)
        if metrics.blink_duration > 300:
            score += 0.3
        elif metrics.blink_duration > 200:
            score += 0.15

        # Time since last blink penalty (>10s = forgot to blink)
        time_since_blink = (datetime.utcnow() - metrics.last_blink).total_seconds()
        if time_since_blink > 10:
            score += 0.2

        return min(1.0, score)


@dataclass
class PupilMetrics:
    """Pupil diameter metrics"""

    left_diameter: float  # millimeters
    right_diameter: float
    avg_diameter: float
    diameter_variance: float  # std dev over window
    baseline_diameter: float = 3.5  # normal: 3-5mm in moderate light


class PupilTracker:
    """
    Tracks pupil diameter changes for fatigue detection

    Fatigue Indicators:
    - Reduced pupil diameter (constriction from mental fatigue)
    - High variance (unstable autonomic regulation)
    - Slow light reflex response
    """

    def __init__(self, window_seconds: int = 30):
        self.window_seconds = window_seconds
        self.readings: deque = deque(maxlen=300)  # 10Hz for 30s = 300 samples

    def add_reading(self, left_mm: float, right_mm: float, timestamp: datetime):
        """Add pupil diameter reading"""
        self.readings.append(
            {
                "timestamp": timestamp,
                "left": left_mm,
                "right": right_mm,
                "avg": (left_mm + right_mm) / 2,
            }
        )

    def get_metrics(self) -> PupilMetrics:
        """Calculate pupil metrics"""
        if not self.readings:
            return PupilMetrics(0, 0, 0, 0)

        recent = list(self.readings)
        left_avg = np.mean([r["left"] for r in recent])
        right_avg = np.mean([r["right"] for r in recent])
        avg_diameter = np.mean([r["avg"] for r in recent])
        variance = np.std([r["avg"] for r in recent])

        return PupilMetrics(
            left_diameter=left_avg,
            right_diameter=right_avg,
            avg_diameter=avg_diameter,
            diameter_variance=variance,
        )

    def get_fatigue_score(self) -> float:
        """Calculate fatigue from pupil dynamics (0-1)"""
        metrics = self.get_metrics()
        score = 0.0

        # Small pupils (mental fatigue, parasympathetic dominance)
        if metrics.avg_diameter < 2.5:
            score += 0.3
        elif metrics.avg_diameter < 3.0:
            score += 0.15

        # High variance (unstable regulation)
        if metrics.diameter_variance > 0.5:
            score += 0.2

        # Asymmetry between eyes
        asymmetry = abs(metrics.left_diameter - metrics.right_diameter)
        if asymmetry > 0.5:
            score += 0.15

        return min(1.0, score)


@dataclass
class HRVMetrics:
    """Heart Rate Variability metrics"""

    rmssd: float  # Root Mean Square of Successive Differences (ms)
    sdnn: float  # Standard Deviation of NN intervals (ms)
    hr_avg: float  # Average heart rate (bpm)
    stress_index: float  # 0-100 (higher = more stress)


class HRVMonitor:
    """
    Monitors HRV via BLE-connected wearable

    Fatigue Indicators:
    - Low RMSSD (<20ms = high stress/fatigue)
    - High resting HR (>80 bpm when seated)
    - Increasing stress index over session
    """

    def __init__(self):
        self.rr_intervals: deque = deque(maxlen=120)  # 2 min of RR intervals

    def add_rr_interval(self, interval_ms: float, timestamp: datetime):
        """Add RR interval reading from wearable"""
        self.rr_intervals.append({"timestamp": timestamp, "interval": interval_ms})

    def get_metrics(self) -> HRVMetrics:
        """Calculate HRV metrics"""
        if len(self.rr_intervals) < 10:
            return HRVMetrics(0, 0, 0, 0)

        intervals = [r["interval"] for r in self.rr_intervals]

        # RMSSD (parasympathetic activity)
        successive_diffs = np.diff(intervals)
        rmssd = np.sqrt(np.mean(successive_diffs**2))

        # SDNN (overall HRV)
        sdnn = np.std(intervals)

        # Heart rate
        hr_avg = 60000 / np.mean(intervals)  # bpm

        # Stress index (inverse of RMSSD, normalized)
        stress_index = max(0, min(100, (50 - rmssd) * 2))

        return HRVMetrics(rmssd=rmssd, sdnn=sdnn, hr_avg=hr_avg, stress_index=stress_index)

    def get_fatigue_score(self) -> float:
        """Calculate fatigue from HRV (0-1)"""
        metrics = self.get_metrics()
        score = 0.0

        # Low HRV (high stress/fatigue)
        if metrics.rmssd < 15:
            score += 0.4
        elif metrics.rmssd < 25:
            score += 0.2

        # Elevated HR at rest
        if metrics.hr_avg > 85:
            score += 0.3
        elif metrics.hr_avg > 75:
            score += 0.15

        # High stress index
        if metrics.stress_index > 70:
            score += 0.3

        return min(1.0, score)


@dataclass
class IMUMetrics:
    """Inertial Measurement Unit metrics"""

    head_tilt_deg: float  # Forward tilt angle
    micro_saccade_rate: float  # per minute
    head_drift: float  # accumulated drift over 5 min


class IMUAnalyzer:
    """
    Analyzes head posture and micro-movements

    Fatigue Indicators:
    - Increasing forward head tilt (neck fatigue)
    - Reduced micro-saccades (reduced alertness)
    - Head drift/sway (postural fatigue)
    """

    def __init__(self):
        self.tilt_readings: deque = deque(maxlen=300)
        self.position_history: deque = deque(maxlen=3000)  # 5min at 10Hz

    def add_reading(self, pitch_deg: float, yaw_deg: float, roll_deg: float, timestamp: datetime):
        """Add IMU reading"""
        self.tilt_readings.append(
            {
                "timestamp": timestamp,
                "pitch": pitch_deg,
                "yaw": yaw_deg,
                "roll": roll_deg,
            }
        )

    def get_metrics(self) -> IMUMetrics:
        """Calculate IMU metrics"""
        if not self.tilt_readings:
            return IMUMetrics(0, 0, 0)

        recent = list(self.tilt_readings)

        # Average forward tilt (positive pitch)
        avg_tilt = np.mean([r["pitch"] for r in recent])

        # Micro-saccade detection (quick head movements)
        yaw_changes = np.diff([r["yaw"] for r in recent])
        micro_saccades = np.sum(np.abs(yaw_changes) > 2)  # >2° changes
        micro_saccade_rate = (micro_saccades / len(recent)) * 600  # per minute

        # Head drift (total position variance)
        pitch_std = np.std([r["pitch"] for r in recent])
        yaw_std = np.std([r["yaw"] for r in recent])
        head_drift = np.sqrt(pitch_std**2 + yaw_std**2)

        return IMUMetrics(
            head_tilt_deg=avg_tilt,
            micro_saccade_rate=micro_saccade_rate,
            head_drift=head_drift,
        )

    def get_fatigue_score(self) -> float:
        """Calculate fatigue from IMU (0-1)"""
        metrics = self.get_metrics()
        score = 0.0

        # Forward head tilt (neck fatigue)
        if metrics.head_tilt_deg > 20:
            score += 0.3
        elif metrics.head_tilt_deg > 10:
            score += 0.15

        # Low micro-saccade rate (reduced alertness)
        if metrics.micro_saccade_rate < 5:
            score += 0.2

        # Excessive head drift (postural instability)
        if metrics.head_drift > 15:
            score += 0.25

        return min(1.0, score)


class SensorFusion:
    """
    Fuses all sensor inputs for comprehensive fatigue assessment

    Weights:
    - Blink: 30% (most reliable short-term indicator)
    - Pupil: 20% (good for mental fatigue)
    - HRV: 30% (best overall stress/fatigue marker)
    - IMU: 20% (physical fatigue, posture)
    """

    def __init__(self):
        self.blink_detector = BlinkDetector()
        self.pupil_tracker = PupilTracker()
        self.hrv_monitor = HRVMonitor()
        self.imu_analyzer = IMUAnalyzer()

        # Sensor weights (must sum to 1.0)
        self.weights = {"blink": 0.30, "pupil": 0.20, "hrv": 0.30, "imu": 0.20}

    def get_fused_fatigue_score(self) -> tuple[float, dict[str, float]]:
        """
        Calculate weighted fatigue score from all sensors

        Returns:
            (fused_score, individual_scores)
        """
        scores = {
            "blink": self.blink_detector.get_fatigue_score(),
            "pupil": self.pupil_tracker.get_fatigue_score(),
            "hrv": self.hrv_monitor.get_fatigue_score(),
            "imu": self.imu_analyzer.get_fatigue_score(),
        }

        # Weighted fusion
        fused_score = sum(scores[sensor] * weight for sensor, weight in self.weights.items())

        return fused_score, scores

    def get_fatigue_level(self) -> FatigueLevel:
        """Classify fatigue level"""
        score, _ = self.get_fused_fatigue_score()

        if score < 0.2:
            return FatigueLevel.FRESH
        elif score < 0.4:
            return FatigueLevel.MILD
        elif score < 0.6:
            return FatigueLevel.MODERATE
        elif score < 0.8:
            return FatigueLevel.SEVERE
        else:
            return FatigueLevel.CRITICAL

    def get_recommendation(self) -> str:
        """Get actionable recommendation based on fatigue level"""
        level = self.get_fatigue_level()

        recommendations = {
            FatigueLevel.FRESH: "Continue current session. No intervention needed.",
            FatigueLevel.MILD: "Take a 20-second break to blink and refocus eyes.",
            FatigueLevel.MODERATE: "Reduce screen brightness. Take 2-minute break within 10 minutes.",
            FatigueLevel.SEVERE: "Stop current task. Take 5-minute break immediately. Hydrate.",
            FatigueLevel.CRITICAL: "End session NOW. Risk of eye strain injury. Rest for 15+ minutes.",
        }

        return recommendations[level]
