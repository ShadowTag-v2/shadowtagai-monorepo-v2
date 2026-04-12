"""
AR Glasses Fatigue Detection & Reduction SDK
Dreamlight-style fatigue management for always-on AI eyewear

Core Components:
- Sensor Layer: Blink tracking, pupil dynamics, HRV, IMU
- Edge Compute: Real-time fatigue prediction (100-500ms latency)
- Display Control: Adaptive brightness/hue/contrast adjustments
- Integration: OEM SDK, App-level overlay, Cloud-assisted AI
"""

__version__ = "1.0.0"
__author__ = "PNKLN Core Stack™"

from .ble import AppleWatchIntegration, BLESyncManager, OuraIntegration, WhoopIntegration
from .display import BrightnessAdapter, ContrastModulator, DisplayController, HueShifter
from .integration import (
    AppleVisionProAdapter,
    AppOverlayService,
    CloudAICompanion,
    MetaRayBanAdapter,
    OEMIntegration,
    SamsungARAdapter,
)
from .models import FatiguePredictor, GBDTFatigueModel, LogisticFatigueModel, NeuralFatigueModel
from .sensors import BlinkDetector, HRVMonitor, IMUAnalyzer, PupilTracker, SensorFusion

__all__ = [
    # Sensors
    "BlinkDetector",
    "PupilTracker",
    "HRVMonitor",
    "IMUAnalyzer",
    "SensorFusion",
    # Models
    "FatiguePredictor",
    "LogisticFatigueModel",
    "GBDTFatigueModel",
    "NeuralFatigueModel",
    # Display
    "DisplayController",
    "BrightnessAdapter",
    "HueShifter",
    "ContrastModulator",
    # Integration
    "OEMIntegration",
    "MetaRayBanAdapter",
    "AppleVisionProAdapter",
    "SamsungARAdapter",
    "AppOverlayService",
    "CloudAICompanion",
    # BLE
    "BLESyncManager",
    "OuraIntegration",
    "WhoopIntegration",
    "AppleWatchIntegration",
]
