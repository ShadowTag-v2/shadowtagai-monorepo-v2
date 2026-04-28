# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""BLE Sync Layer
Wearable integration for HRV and biometric data

Supported Devices:
- Oura Ring (HRV, HR, temperature)
- Whoop Band (HRV, HR, strain, recovery)
- Apple Watch (HRV, HR, workout data)
- Generic BLE HR monitors
"""

import asyncio
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class WearableType(StrEnum):
    """Supported wearable types"""

    OURA = "oura"
    WHOOP = "whoop"
    APPLE_WATCH = "apple_watch"
    GENERIC_HRM = "generic_hrm"


@dataclass
class WearableReading:
    """Generic wearable data reading"""

    device_id: str
    device_type: WearableType
    timestamp: datetime
    hr_bpm: float | None = None
    rr_interval_ms: float | None = None
    hrv_rmssd: float | None = None
    battery_percent: int | None = None
    signal_quality: float = 1.0  # 0-1
    metadata: dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class BLEDevice(ABC):
    """Base class for BLE wearable devices"""

    def __init__(self, device_id: str, device_type: WearableType):
        self.device_id = device_id
        self.device_type = device_type
        self.connected = False
        self.last_reading: WearableReading | None = None
        self.connection_quality = 1.0  # 0-1
        self.callbacks: list[Callable] = []

    @abstractmethod
    async def connect(self) -> bool:
        """Establish BLE connection"""

    @abstractmethod
    async def disconnect(self):
        """Disconnect from device"""

    @abstractmethod
    async def read_data(self) -> WearableReading | None:
        """Read current sensor data"""

    def register_callback(self, callback: Callable):
        """Register callback for new data"""
        self.callbacks.append(callback)

    async def _notify_callbacks(self, reading: WearableReading):
        """Notify all registered callbacks"""
        for callback in self.callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(reading)
                else:
                    callback(reading)
            except Exception as e:
                print(f"Callback error: {e}")


class OuraIntegration(BLEDevice):
    """Oura Ring integration

    Features:
    - Real-time HRV via BLE (when in range)
    - Historical data via API
    - Sleep quality scores
    - Readiness scores (recovery metric)

    API: https://cloud.ouraring.com/v2/docs
    """

    def __init__(self, device_id: str, api_token: str | None = None):
        super().__init__(device_id, WearableType.OURA)
        self.api_token = api_token
        self.use_cloud_api = api_token is not None

        # Oura-specific metrics
        self.readiness_score: float | None = None  # 0-100
        self.sleep_score: float | None = None

    async def connect(self) -> bool:
        """Connect to Oura Ring via BLE"""
        # Mock BLE connection
        # In production, use bleak library for BLE
        print(f"[Oura] Connecting to {self.device_id}...")
        await asyncio.sleep(0.5)  # Simulate connection delay

        self.connected = True
        print("[Oura] Connected successfully")
        return True

    async def disconnect(self):
        """Disconnect from Oura"""
        self.connected = False
        print("[Oura] Disconnected")

    async def read_data(self) -> WearableReading | None:
        """Read HRV and HR data from Oura"""
        if not self.connected:
            return None

        # Mock data (in production, read from BLE characteristics)
        # Oura provides HRV in RMSSD format
        reading = WearableReading(
            device_id=self.device_id,
            device_type=self.device_type,
            timestamp=datetime.utcnow(),
            hr_bpm=68.0,  # Mock HR
            rr_interval_ms=882.0,  # 60000/68 ≈ 882ms
            hrv_rmssd=32.5,  # Mock HRV
            battery_percent=75,
            signal_quality=0.95,
            metadata={
                "readiness_score": self.readiness_score or 78,
                "sleep_score": self.sleep_score or 82,
            },
        )

        self.last_reading = reading
        await self._notify_callbacks(reading)
        return reading

    async def fetch_cloud_data(self) -> dict:
        """Fetch historical data from Oura Cloud API"""
        if not self.api_token:
            return {}

        # Mock API call
        # In production: GET https://api.ouraring.com/v2/usercollection/daily_readiness
        await asyncio.sleep(0.2)

        return {
            "readiness_score": 78,
            "sleep_score": 82,
            "hrv_balance": "balanced",
            "recovery_index": 0.85,
        }


class WhoopIntegration(BLEDevice):
    """Whoop Band integration

    Features:
    - Real-time HRV during activities
    - Strain score (0-21)
    - Recovery score (0-100%)
    - Respiratory rate

    API: https://developer.whoop.com/api
    """

    def __init__(self, device_id: str, api_token: str | None = None):
        super().__init__(device_id, WearableType.WHOOP)
        self.api_token = api_token

        # Whoop-specific metrics
        self.strain_score: float | None = None  # 0-21
        self.recovery_percent: float | None = None  # 0-100

    async def connect(self) -> bool:
        """Connect to Whoop Band"""
        print(f"[Whoop] Connecting to {self.device_id}...")
        await asyncio.sleep(0.5)

        self.connected = True
        print("[Whoop] Connected successfully")
        return True

    async def disconnect(self):
        """Disconnect from Whoop"""
        self.connected = False
        print("[Whoop] Disconnected")

    async def read_data(self) -> WearableReading | None:
        """Read Whoop biometric data"""
        if not self.connected:
            return None

        reading = WearableReading(
            device_id=self.device_id,
            device_type=self.device_type,
            timestamp=datetime.utcnow(),
            hr_bpm=72.0,
            rr_interval_ms=833.0,
            hrv_rmssd=28.0,
            battery_percent=60,
            signal_quality=0.92,
            metadata={
                "strain_score": self.strain_score or 8.5,
                "recovery_percent": self.recovery_percent or 68,
                "respiratory_rate": 16.0,  # breaths per minute
            },
        )

        self.last_reading = reading
        await self._notify_callbacks(reading)
        return reading


class AppleWatchIntegration(BLEDevice):
    """Apple Watch integration

    Features:
    - Real-time HR via HealthKit
    - HRV samples (iOS 13+)
    - Workout detection
    - Fall detection context

    Note: Requires iOS app with HealthKit permissions
    """

    def __init__(self, device_id: str):
        super().__init__(device_id, WearableType.APPLE_WATCH)
        self.healthkit_available = False

    async def connect(self) -> bool:
        """Connect to Apple Watch via HealthKit"""
        print(f"[Apple Watch] Connecting to {self.device_id}...")

        # Check if running on iOS with HealthKit access
        # In production, use PyObjC bridge to HealthKit
        await asyncio.sleep(0.3)

        self.connected = True
        self.healthkit_available = True
        print("[Apple Watch] Connected via HealthKit")
        return True

    async def disconnect(self):
        """Disconnect from Apple Watch"""
        self.connected = False
        print("[Apple Watch] Disconnected")

    async def read_data(self) -> WearableReading | None:
        """Read Apple Watch health data"""
        if not self.connected or not self.healthkit_available:
            return None

        # Query HealthKit for latest HR and HRV samples
        # HKQuantityType: .heartRate, .heartRateVariabilitySDNN
        reading = WearableReading(
            device_id=self.device_id,
            device_type=self.device_type,
            timestamp=datetime.utcnow(),
            hr_bpm=70.0,
            rr_interval_ms=857.0,
            hrv_rmssd=30.0,  # Converted from SDNN
            battery_percent=None,  # Not exposed via HealthKit
            signal_quality=0.98,  # Apple Watch has excellent sensors
            metadata={
                "active_energy_burned": 450,  # kcal
                "steps": 8234,
                "stand_hours": 8,
            },
        )

        self.last_reading = reading
        await self._notify_callbacks(reading)
        return reading

    async def query_hrv_samples(self, start_date: datetime, end_date: datetime) -> list[float]:
        """Query historical HRV samples from HealthKit"""
        if not self.healthkit_available:
            return []

        # Mock HRV samples
        # In production: HKSampleQuery for HRV SDNN
        samples = [30.0 + (i % 10) for i in range(10)]  # Mock data
        return samples


class BLESyncManager:
    """Central manager for all BLE wearable connections

    Features:
    - Multi-device support
    - Automatic reconnection
    - Data fusion from multiple sources
    - Battery-aware polling rates
    """

    def __init__(self):
        self.devices: dict[str, BLEDevice] = {}
        self.active_device: BLEDevice | None = None
        self.polling_interval = 5.0  # seconds
        self.running = False

    async def add_device(self, device: BLEDevice) -> bool:
        """Add and connect to wearable device"""
        if device.device_id in self.devices:
            print(f"Device {device.device_id} already registered")
            return False

        # Attempt connection
        success = await device.connect()
        if success:
            self.devices[device.device_id] = device

            # Set as active if first device
            if not self.active_device:
                self.active_device = device

            print(f"Added {device.device_type.value} device: {device.device_id}")

        return success

    async def remove_device(self, device_id: str):
        """Remove and disconnect device"""
        if device_id in self.devices:
            device = self.devices[device_id]
            await device.disconnect()
            del self.devices[device_id]

            if self.active_device and self.active_device.device_id == device_id:
                # Switch to next available device
                self.active_device = next(iter(self.devices.values()), None)

            print(f"Removed device: {device_id}")

    async def start_sync(self):
        """Start continuous syncing from all devices"""
        self.running = True
        print("[BLE Sync] Started continuous sync")

        while self.running:
            # Poll all connected devices
            for device in self.devices.values():
                if device.connected:
                    try:
                        await device.read_data()
                    except Exception as e:
                        print(f"[BLE Sync] Error reading {device.device_id}: {e}")
                        # Attempt reconnection
                        await device.connect()

            await asyncio.sleep(self.polling_interval)

    async def stop_sync(self):
        """Stop syncing"""
        self.running = False
        print("[BLE Sync] Stopped sync")

    def get_latest_reading(self) -> WearableReading | None:
        """Get most recent reading from active device"""
        if self.active_device:
            return self.active_device.last_reading
        return None

    def get_all_readings(self) -> dict[str, WearableReading]:
        """Get latest readings from all devices"""
        return {
            device_id: device.last_reading
            for device_id, device in self.devices.items()
            if device.last_reading is not None
        }

    async def fuse_readings(self) -> dict | None:
        """Fuse data from multiple wearables

        Priority: Apple Watch > Oura > Whoop (sensor quality)
        """
        readings = self.get_all_readings()
        if not readings:
            return None

        # Prioritize Apple Watch if available
        priority_order = [
            WearableType.APPLE_WATCH,
            WearableType.OURA,
            WearableType.WHOOP,
            WearableType.GENERIC_HRM,
        ]

        fused_data = {}

        for device_type in priority_order:
            for reading in readings.values():
                if reading.device_type == device_type:
                    # Use this device's data as primary
                    fused_data["hr_bpm"] = reading.hr_bpm
                    fused_data["hrv_rmssd"] = reading.hrv_rmssd
                    fused_data["rr_interval_ms"] = reading.rr_interval_ms
                    fused_data["primary_device"] = device_type.value
                    fused_data["signal_quality"] = reading.signal_quality
                    fused_data["timestamp"] = reading.timestamp
                    break

            if fused_data:
                break

        # Add supplementary data from other devices
        for reading in readings.values():
            if reading.metadata:
                fused_data.setdefault("supplementary", {})
                fused_data["supplementary"][reading.device_type.value] = reading.metadata

        return fused_data or None

    def set_polling_interval(self, seconds: float):
        """Adjust polling rate (battery vs. latency tradeoff)"""
        self.polling_interval = max(1.0, min(60.0, seconds))
        print(f"[BLE Sync] Polling interval set to {self.polling_interval}s")

    async def optimize_battery(self, enable: bool):
        """Enable battery optimization mode"""
        if enable:
            # Reduce polling rate for battery savings
            self.set_polling_interval(10.0)
            print("[BLE Sync] Battery optimization enabled (10s polling)")
        else:
            # High-frequency polling for real-time fatigue detection
            self.set_polling_interval(5.0)
            print("[BLE Sync] High-frequency mode (5s polling)")


# ============================================================================
# Integration with Fatigue Detection
# ============================================================================


class HRVFatigueIntegration:
    """Integrates BLE wearable data with fatigue detection pipeline

    Automatically feeds HRV data into HRVMonitor
    """

    def __init__(self, ble_manager: BLESyncManager, hrv_monitor):
        """Args:
        ble_manager: BLESyncManager instance
        hrv_monitor: HRVMonitor from sensors module

        """
        self.ble_manager = ble_manager
        self.hrv_monitor = hrv_monitor

        # Register callback on all devices
        for device in ble_manager.devices.values():
            device.register_callback(self._on_wearable_data)

    async def _on_wearable_data(self, reading: WearableReading):
        """Callback when new wearable data arrives"""
        if reading.rr_interval_ms:
            # Feed RR interval to HRV monitor
            self.hrv_monitor.add_rr_interval(reading.rr_interval_ms, reading.timestamp)

    async def start(self):
        """Start automatic HRV monitoring"""
        await self.ble_manager.start_sync()

    async def stop(self):
        """Stop monitoring"""
        await self.ble_manager.stop_sync()
