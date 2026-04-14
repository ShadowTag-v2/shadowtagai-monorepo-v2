"""Display Control Layer
Adaptive brightness, hue, and contrast adjustments for fatigue reduction

Mechanics (Dreamliner-style):
- Imperceptible micro-adjustments (user doesn't notice changes)
- Continuous oscillations to reduce cognitive monotony
- Evidence-based interventions (blink triggering, circadian alignment)
"""

import math
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

import numpy as np


class DisplayMode(StrEnum):
    """Display adaptation modes"""

    NORMAL = "normal"  # No adaptation
    FATIGUE_AWARE = "fatigue_aware"  # Continuous micro-adjustments
    BREAK_MODE = "break_mode"  # Strong interventions
    NIGHT_MODE = "night_mode"  # Circadian-aligned (warm, dim)


@dataclass
class DisplayState:
    """Current display parameters"""

    brightness: float  # 0.0-1.0 (0=off, 1=max)
    hue_shift: float  # -30 to +30 degrees (negative=warmer/amber, positive=cooler/blue)
    contrast: float  # 0.5-1.5 (1.0=normal)
    saturation: float  # 0.0-1.0 (1.0=full color)
    timestamp: datetime
    mode: DisplayMode


@dataclass
class DisplayAdjustment:
    """Recommended display adjustment"""

    delta_brightness: float  # Change from current
    delta_hue: float
    delta_contrast: float
    delta_saturation: float
    duration_seconds: float  # How long to apply adjustment
    reason: str  # Why this adjustment was made


class BrightnessAdapter:
    """Adaptive brightness control

    Strategies:
    - Reduce brightness when pupil constriction detected (reduce strain)
    - Gradual transitions (mimic Dreamliner cabin lighting)
    - Maintain minimum visibility threshold
    """

    def __init__(self, min_brightness: float = 0.15, max_brightness: float = 1.0):
        self.min_brightness = min_brightness
        self.max_brightness = max_brightness
        self.current_brightness = 0.7  # Default comfortable level
        self.ambient_light_level = 0.5  # Mock ambient sensor (0=dark, 1=bright)

    def set_ambient_light(self, level: float):
        """Update ambient light level from sensor"""
        self.ambient_light_level = np.clip(level, 0.0, 1.0)

    def calculate_adjustment(
        self, fatigue_score: float, pupil_diameter: float,
    ) -> tuple[float, str]:
        """Calculate brightness adjustment

        Args:
            fatigue_score: 0-1 fatigue level
            pupil_diameter: mm (2-8 range)

        Returns:
            (target_brightness, reason)

        """
        # Base brightness from ambient light
        # Dark environment = lower brightness, bright = higher
        base_brightness = 0.3 + (self.ambient_light_level * 0.4)

        # Fatigue adjustment: reduce brightness to ease strain
        fatigue_adjustment = -0.15 * fatigue_score

        # Pupil adjustment: small pupils = too bright, reduce
        # Normal pupil in moderate light: 3-5mm
        if pupil_diameter < 3.0:
            pupil_adjustment = -0.1  # Pupils constricted, too bright
        elif pupil_diameter > 5.5:
            pupil_adjustment = 0.1  # Pupils dilated, too dim
        else:
            pupil_adjustment = 0.0

        # Combine adjustments
        target = base_brightness + fatigue_adjustment + pupil_adjustment
        target = np.clip(target, self.min_brightness, self.max_brightness)

        # Generate reason
        reasons = []
        if abs(fatigue_adjustment) > 0.05:
            reasons.append(f"fatigue reduction (-{abs(fatigue_adjustment):.0%})")
        if abs(pupil_adjustment) > 0.05:
            reasons.append(f"pupil adaptation ({'dim' if pupil_adjustment > 0 else 'bright'})")

        reason = "; ".join(reasons) if reasons else "ambient light optimization"

        return target, reason

    def apply_gradual_transition(self, target: float, duration_seconds: float = 2.0) -> float:
        """Gradually transition to target brightness

        Dreamliner-style: slow enough to be imperceptible

        Returns:
            delta_brightness for this step

        """
        delta = target - self.current_brightness

        # Limit change rate (max 10% per second)
        max_delta = 0.1 * (duration_seconds / 1.0)
        if abs(delta) > max_delta:
            delta = math.copysign(max_delta, delta)

        return delta


class HueShifter:
    """Adaptive hue/color temperature control

    Strategies:
    - Warm shift (amber) to reduce blue light exposure
    - Trigger natural blinking via subtle contrast changes
    - Circadian alignment (warmer in evening)
    - Micro-oscillations to prevent visual adaptation
    """

    def __init__(self):
        self.current_hue_shift = 0.0  # degrees
        self.base_warm_shift = -5.0  # Slight warm bias by default
        self.oscillation_amplitude = 2.0  # degrees
        self.oscillation_period = 30.0  # seconds

    def calculate_adjustment(
        self, fatigue_score: float, blink_rate: float, time_of_day_hour: int,
    ) -> tuple[float, str]:
        """Calculate hue shift adjustment

        Args:
            fatigue_score: 0-1
            blink_rate: blinks per minute
            time_of_day_hour: 0-23

        Returns:
            (target_hue_shift, reason)

        """
        # Base warm shift
        target_shift = self.base_warm_shift

        # Fatigue shift: warmer = less stimulating, easier on eyes
        fatigue_shift = -10.0 * fatigue_score  # Up to -10° warmer

        # Low blink rate: add warmth to trigger blinking response
        if blink_rate < 10:
            blink_shift = -5.0
            reason_blink = "low blink rate compensation"
        else:
            blink_shift = 0.0
            reason_blink = None

        # Circadian alignment: warmer in evening/night
        # Peak warmth at 22:00, coolest at 12:00
        hour_radians = (time_of_day_hour / 24.0) * 2 * math.pi
        circadian_shift = -8.0 * math.cos(hour_radians - (22 / 24 * 2 * math.pi))

        # Micro-oscillation (imperceptible, prevents adaptation)
        time_since_epoch = (datetime.utcnow() - datetime(2024, 1, 1)).total_seconds()
        oscillation = self.oscillation_amplitude * math.sin(
            2 * math.pi * time_since_epoch / self.oscillation_period,
        )

        # Combine all shifts
        target_shift += fatigue_shift + blink_shift + circadian_shift + oscillation

        # Clamp to reasonable range (-30° to +10°)
        target_shift = np.clip(target_shift, -30.0, 10.0)

        # Build reason string
        reasons = []
        if abs(fatigue_shift) > 2:
            reasons.append(f"fatigue warmth ({abs(fatigue_shift):.0f}°)")
        if blink_shift < 0:
            reasons.append(reason_blink)
        if abs(circadian_shift) > 3:
            reasons.append("circadian alignment")

        reason = "; ".join(filter(None, reasons)) or "baseline optimization"

        return target_shift, reason

    def trigger_blink_pulse(self) -> DisplayAdjustment:
        """Trigger blink via brief contrast fade

        Evidence: subtle fade triggers reflexive blink response
        """
        return DisplayAdjustment(
            delta_brightness=0.0,
            delta_hue=0.0,
            delta_contrast=-0.15,  # Brief 15% contrast reduction
            delta_saturation=-0.1,
            duration_seconds=0.3,  # 300ms pulse
            reason="blink trigger pulse",
        )


class ContrastModulator:
    """Adaptive contrast control

    Strategies:
    - Reduce contrast during fatigue (less visual stress)
    - Micro-oscillations for cognitive variety
    - Boost contrast for alertness if needed
    """

    def __init__(self):
        self.current_contrast = 1.0  # Normal
        self.min_contrast = 0.7
        self.max_contrast = 1.3

    def calculate_adjustment(
        self, fatigue_score: float, session_duration_min: float,
    ) -> tuple[float, str]:
        """Calculate contrast adjustment"""
        # Base contrast
        target = 1.0

        # Reduce contrast with fatigue
        fatigue_reduction = -0.2 * fatigue_score
        target += fatigue_reduction

        # Long session: add micro-oscillation to reduce monotony
        if session_duration_min > 20:
            time_since_epoch = (datetime.utcnow() - datetime(2024, 1, 1)).total_seconds()
            # 20-30 minute oscillation period
            oscillation = 0.08 * math.sin(2 * math.pi * time_since_epoch / (25 * 60))
            target += oscillation
            reason_osc = "monotony reduction"
        else:
            reason_osc = None

        # Clamp
        target = np.clip(target, self.min_contrast, self.max_contrast)

        reasons = []
        if abs(fatigue_reduction) > 0.05:
            reasons.append(f"fatigue reduction ({abs(fatigue_reduction):.0%})")
        if reason_osc:
            reasons.append(reason_osc)

        reason = "; ".join(filter(None, reasons)) or "baseline"

        return target, reason


class DisplayController:
    """Master display control system

    Coordinates all display adaptations based on fatigue state
    Implements Dreamliner-style imperceptible adjustments
    """

    def __init__(self):
        self.brightness_adapter = BrightnessAdapter()
        self.hue_shifter = HueShifter()
        self.contrast_modulator = ContrastModulator()

        self.current_state = DisplayState(
            brightness=0.7,
            hue_shift=0.0,
            contrast=1.0,
            saturation=1.0,
            timestamp=datetime.utcnow(),
            mode=DisplayMode.NORMAL,
        )

        self.mode = DisplayMode.FATIGUE_AWARE
        self.last_blink_trigger = datetime.utcnow()

    def update(self, sensor_fusion, fatigue_prediction) -> DisplayAdjustment:
        """Calculate display adjustment based on current state

        Args:
            sensor_fusion: SensorFusion object
            fatigue_prediction: FatiguePrediction object

        Returns:
            DisplayAdjustment to apply

        """
        # Extract metrics
        blink_metrics = sensor_fusion.blink_detector.get_metrics()
        pupil_metrics = sensor_fusion.pupil_tracker.get_metrics()
        fatigue_score = fatigue_prediction.score

        now = datetime.utcnow()
        time_of_day = now.hour

        # Get session duration (placeholder - would track in session manager)
        session_duration_min = 30.0

        # Calculate adjustments for each component
        target_brightness, brightness_reason = self.brightness_adapter.calculate_adjustment(
            fatigue_score, pupil_metrics.avg_diameter,
        )

        target_hue, hue_reason = self.hue_shifter.calculate_adjustment(
            fatigue_score, blink_metrics.blink_rate, time_of_day,
        )

        target_contrast, contrast_reason = self.contrast_modulator.calculate_adjustment(
            fatigue_score, session_duration_min,
        )

        # Check if blink trigger needed
        time_since_blink_trigger = (now - self.last_blink_trigger).total_seconds()
        needs_blink_trigger = blink_metrics.blink_rate < 8 and time_since_blink_trigger > 10

        if needs_blink_trigger:
            self.last_blink_trigger = now
            return self.hue_shifter.trigger_blink_pulse()

        # Calculate deltas from current state
        delta_brightness = self.brightness_adapter.apply_gradual_transition(
            target_brightness, duration_seconds=2.0,
        )

        delta_hue = target_hue - self.current_state.hue_shift
        delta_contrast = target_contrast - self.current_state.contrast

        # Build comprehensive reason
        reasons = [
            f"brightness: {brightness_reason}",
            f"hue: {hue_reason}",
            f"contrast: {contrast_reason}",
        ]

        adjustment = DisplayAdjustment(
            delta_brightness=delta_brightness,
            delta_hue=delta_hue,
            delta_contrast=delta_contrast,
            delta_saturation=0.0,  # Keep saturation normal for now
            duration_seconds=2.0,  # Gradual 2-second transition
            reason=" | ".join(reasons),
        )

        return adjustment

    def apply_adjustment(self, adjustment: DisplayAdjustment):
        """Apply adjustment to current state"""
        self.current_state = DisplayState(
            brightness=np.clip(
                self.current_state.brightness + adjustment.delta_brightness, 0.0, 1.0,
            ),
            hue_shift=np.clip(self.current_state.hue_shift + adjustment.delta_hue, -30.0, 10.0),
            contrast=np.clip(self.current_state.contrast + adjustment.delta_contrast, 0.5, 1.5),
            saturation=np.clip(
                self.current_state.saturation + adjustment.delta_saturation, 0.0, 1.0,
            ),
            timestamp=datetime.utcnow(),
            mode=self.mode,
        )

    def set_mode(self, mode: DisplayMode):
        """Change display mode"""
        self.mode = mode

        if mode == DisplayMode.BREAK_MODE:
            # Strong interventions for forced break
            self.current_state.brightness = 0.3
            self.current_state.hue_shift = -20.0  # Very warm
            self.current_state.saturation = 0.5  # Desaturated

        elif mode == DisplayMode.NIGHT_MODE:
            # Circadian-friendly evening mode
            self.current_state.brightness = 0.4
            self.current_state.hue_shift = -15.0
            self.current_state.saturation = 0.8

        elif mode == DisplayMode.NORMAL:
            # Reset to defaults
            self.current_state.brightness = 0.7
            self.current_state.hue_shift = 0.0
            self.current_state.contrast = 1.0
            self.current_state.saturation = 1.0

    def get_display_parameters(self) -> dict:
        """Get display parameters in hardware-specific format

        Returns format compatible with OEM SDKs (Meta, Apple, Samsung)
        """
        # Convert to standard RGB adjustment matrix
        # (simplified - actual implementation would use full color transform)

        brightness_factor = self.current_state.brightness
        contrast_factor = self.current_state.contrast
        saturation_factor = self.current_state.saturation

        # Hue shift: convert degrees to RGB adjustment
        # Negative = warmer (reduce blue, boost red/amber)
        # Positive = cooler (boost blue)
        hue_deg = self.current_state.hue_shift

        if hue_deg < 0:  # Warm shift
            warmth = abs(hue_deg) / 30.0  # Normalize to 0-1
            rgb_adjustment = {
                "red": 1.0 + (0.1 * warmth),
                "green": 1.0 + (0.05 * warmth),
                "blue": 1.0 - (0.3 * warmth),  # Reduce blue significantly
            }
        else:  # Cool shift
            coolness = hue_deg / 10.0
            rgb_adjustment = {
                "red": 1.0 - (0.1 * coolness),
                "green": 1.0,
                "blue": 1.0 + (0.2 * coolness),
            }

        return {
            "brightness": brightness_factor,
            "contrast": contrast_factor,
            "saturation": saturation_factor,
            "rgb_adjustment": rgb_adjustment,
            "hue_shift_degrees": hue_deg,
            "timestamp": self.current_state.timestamp.isoformat(),
            "mode": self.current_state.mode.value,
            # OEM-specific formats
            "meta_format": {
                "brightness_percent": int(brightness_factor * 100),
                "tint_kelvin": int(6500 - (hue_deg * 50)),  # 6500K = neutral
            },
            "apple_format": {
                "brightness": brightness_factor,
                "white_point": {
                    "x": 0.313 - (hue_deg / 1000),  # D65 x coordinate adjusted
                    "y": 0.329,
                },
            },
            "samsung_format": {
                "brightness_nits": int(brightness_factor * 500),  # Max 500 nits
                "color_temp_kelvin": int(6500 - (hue_deg * 50)),
            },
        }
