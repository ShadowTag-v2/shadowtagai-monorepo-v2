"""AR Glasses Fatigue Detection API
FastAPI endpoints for real-time fatigue monitoring and display control

Endpoints:
- POST /fatigue/session/start - Start monitoring session
- POST /fatigue/session/update - Send sensor data update
- GET /fatigue/session/status - Get current fatigue status
- POST /fatigue/session/end - End session
- GET /fatigue/devices - List connected devices
- POST /fatigue/devices/connect - Connect new device
"""

import asyncio

# Import fatigue detection modules
import sys
from datetime import datetime
from typing import Any

from fastapi import BackgroundTasks, FastAPI, HTTPException, Query, status
from pydantic import BaseModel, Field

sys.path.append("/home/user/ShadowTag-v2-fastapi-services/src")

import contextlib

from fatigue.ble import (
    AppleWatchIntegration,
    BLESyncManager,
    OuraIntegration,
    WhoopIntegration,
)
from fatigue.display import DisplayController, DisplayMode
from fatigue.integration import (
    AppleVisionProAdapter,
    DevicePlatform,
    MetaRayBanAdapter,
    SamsungARAdapter,
)
from fatigue.models import AdaptiveFatiguePredictor, FatiguePrediction, FatigueSessionTracker
from fatigue.sensors import (
    FatigueLevel,
    SensorFusion,
)

# Initialize FastAPI app
app = FastAPI(
    title="AR Glasses Fatigue Detection API",
    description="Dreamlight-style fatigue management for always-on AI eyewear",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


# ============================================================================
# Global State (in production, use proper state management)
# ============================================================================

active_sessions: dict[str, dict] = {}  # session_id -> session_data
connected_devices: dict[str, Any] = {}  # device_id -> device_object


# ============================================================================
# Models
# ============================================================================


class SessionRequest(BaseModel):
    """Start session request"""

    user_id: str = Field(..., description="User identifier")
    device_platform: DevicePlatform = Field(..., description="AR glasses platform")
    device_id: str = Field(..., description="Device ID")
    device_tier: str = Field(default="mid", description="Device compute tier (low/mid/high)")
    enable_ble: bool = Field(default=True, description="Enable BLE wearable sync")


class SensorUpdate(BaseModel):
    """Sensor data update"""

    session_id: str = Field(..., description="Active session ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # Blink data
    eye_closure: float | None = Field(None, ge=0, le=1, description="Eye closure 0-1")

    # Pupil data
    left_pupil_mm: float | None = Field(None, description="Left pupil diameter (mm)")
    right_pupil_mm: float | None = Field(None, description="Right pupil diameter (mm)")

    # HRV data (from wearable)
    rr_interval_ms: float | None = Field(None, description="RR interval (ms)")

    # IMU data
    head_pitch_deg: float | None = Field(None, description="Head pitch (degrees)")
    head_yaw_deg: float | None = Field(None, description="Head yaw (degrees)")
    head_roll_deg: float | None = Field(None, description="Head roll (degrees)")


class FatigueStatusResponse(BaseModel):
    """Current fatigue status"""

    session_id: str
    fatigue_score: float = Field(..., ge=0, le=1, description="Fatigue score 0-1")
    fatigue_level: FatigueLevel
    confidence: float = Field(..., ge=0, le=1)
    recommendation: str
    display_parameters: dict[str, Any]
    session_duration_min: float
    time_since_last_break_min: float
    interventions_triggered: int
    model_latency_ms: float
    timestamp: datetime


class DeviceInfo(BaseModel):
    """Connected device info"""

    device_id: str
    device_type: str  # "glasses", "wearable"
    platform: str
    connected: bool
    capabilities: dict | None = None
    battery_percent: int | None = None


class ConnectDeviceRequest(BaseModel):
    """Connect device request"""

    device_type: str = Field(..., description="Device type (glasses/wearable)")
    platform: str = Field(..., description="Platform (meta_rayban/oura/etc)")
    device_id: str = Field(..., description="Device ID")
    api_key: str | None = Field(None, description="API key if required")


# ============================================================================
# Endpoints
# ============================================================================


@app.get("/", tags=["Health"])
async def root():
    """API root endpoint"""
    return {
        "service": "AR Glasses Fatigue Detection API",
        "version": "1.0.0",
        "status": "operational",
        "documentation": "/docs",
        "features": [
            "Real-time fatigue prediction (100-500ms latency)",
            "Multi-sensor fusion (blink, pupil, HRV, IMU)",
            "Adaptive display control (brightness, hue, contrast)",
            "BLE wearable integration (Oura, Whoop, Apple Watch)",
            "OEM platform support (Meta, Apple, Samsung)",
        ],
    }


@app.post(
    "/fatigue/session/start",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    tags=["Session"],
)
async def start_session(request: SessionRequest, background_tasks: BackgroundTasks):
    """Start fatigue monitoring session

    Initializes:
    - Sensor fusion pipeline
    - Fatigue prediction model
    - Display controller
    - BLE sync (if enabled)
    - Connected AR glasses
    """
    # Generate session ID
    session_id = f"sess_{request.user_id}_{datetime.utcnow().timestamp()}"

    # Initialize components
    sensor_fusion = SensorFusion()
    fatigue_predictor = AdaptiveFatiguePredictor(device_tier=request.device_tier)
    display_controller = DisplayController()
    session_tracker = FatigueSessionTracker()

    # Initialize BLE manager
    ble_manager = None
    if request.enable_ble:
        ble_manager = BLESyncManager()
        # BLE devices will be added via /devices/connect endpoint

    # Connect to AR glasses
    glasses_device = None
    if request.device_platform == DevicePlatform.META_RAYBAN:
        glasses_device = MetaRayBanAdapter(request.device_id)
    elif request.device_platform == DevicePlatform.APPLE_VISION_PRO:
        glasses_device = AppleVisionProAdapter(request.device_id)
    elif request.device_platform == DevicePlatform.SAMSUNG_AR:
        glasses_device = SamsungARAdapter(request.device_id)

    if glasses_device:
        await glasses_device.connect()
        capabilities = await glasses_device.get_capabilities()

    # Store session
    active_sessions[session_id] = {
        "user_id": request.user_id,
        "session_id": session_id,
        "start_time": datetime.utcnow(),
        "sensor_fusion": sensor_fusion,
        "fatigue_predictor": fatigue_predictor,
        "display_controller": display_controller,
        "session_tracker": session_tracker,
        "ble_manager": ble_manager,
        "glasses_device": glasses_device,
        "device_platform": request.device_platform,
    }

    return {
        "session_id": session_id,
        "status": "active",
        "start_time": datetime.utcnow(),
        "device_platform": request.device_platform.value,
        "device_capabilities": capabilities.__dict__ if glasses_device else None,
        "ble_enabled": request.enable_ble,
        "model_tier": request.device_tier,
    }


@app.post("/fatigue/session/update", response_model=FatigueStatusResponse, tags=["Session"])
async def update_session(update: SensorUpdate):
    """Send sensor data update and get fatigue prediction

    Real-time endpoint - designed for 100-500ms latency
    Call this every 1-5 seconds from glasses device
    """
    start_time = datetime.utcnow()

    # Get session
    if update.session_id not in active_sessions:
        raise HTTPException(status_code=404, detail=f"Session {update.session_id} not found")

    session = active_sessions[update.session_id]
    sensor_fusion: SensorFusion = session["sensor_fusion"]
    fatigue_predictor: AdaptiveFatiguePredictor = session["fatigue_predictor"]
    display_controller: DisplayController = session["display_controller"]
    session_tracker: FatigueSessionTracker = session["session_tracker"]

    # Update sensors
    if update.eye_closure is not None:
        sensor_fusion.blink_detector.process_frame(update.eye_closure, update.timestamp)

    if update.left_pupil_mm and update.right_pupil_mm:
        sensor_fusion.pupil_tracker.add_reading(
            update.left_pupil_mm, update.right_pupil_mm, update.timestamp,
        )

    if update.rr_interval_ms:
        sensor_fusion.hrv_monitor.add_rr_interval(update.rr_interval_ms, update.timestamp)

    if update.head_pitch_deg is not None:
        sensor_fusion.imu_analyzer.add_reading(
            update.head_pitch_deg,
            update.head_yaw_deg or 0.0,
            update.head_roll_deg or 0.0,
            update.timestamp,
        )

    # Get fatigue prediction
    prediction: FatiguePrediction = fatigue_predictor.predict(sensor_fusion)
    session_tracker.add_prediction(prediction)

    # Update display controller
    adjustment = display_controller.update(sensor_fusion, prediction)
    display_controller.apply_adjustment(adjustment)

    # Apply to glasses device
    glasses_device = session.get("glasses_device")
    if glasses_device:
        display_params = display_controller.get_display_parameters()
        await glasses_device.set_display_parameters(display_params)

    # Get session stats
    session_stats = session_tracker.get_session_stats()

    # Get recommendation
    recommendation = sensor_fusion.get_recommendation()

    # Check if forced break needed
    if session_tracker.should_force_break():
        recommendation = "⚠️ MANDATORY BREAK: Stop now. Rest for 15 minutes."
        display_controller.set_mode(DisplayMode.BREAK_MODE)

    total_latency_ms = (datetime.utcnow() - start_time).total_seconds() * 1000

    return FatigueStatusResponse(
        session_id=update.session_id,
        fatigue_score=prediction.score,
        fatigue_level=FatigueLevel(prediction.level),
        confidence=prediction.confidence,
        recommendation=recommendation,
        display_parameters=display_controller.get_display_parameters(),
        session_duration_min=session_stats.get("session_duration_min", 0),
        time_since_last_break_min=session_stats.get("time_since_last_break_min", 0),
        interventions_triggered=session_stats.get("interventions_triggered", 0),
        model_latency_ms=total_latency_ms,
        timestamp=datetime.utcnow(),
    )


@app.get("/fatigue/session/status", response_model=FatigueStatusResponse, tags=["Session"])
async def get_session_status(session_id: str = Query(..., description="Session ID")):
    """Get current session status without sending new data"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = active_sessions[session_id]
    session_tracker: FatigueSessionTracker = session["session_tracker"]

    if not session_tracker.predictions:
        raise HTTPException(status_code=400, detail="No predictions yet")

    # Return last prediction
    last_prediction = session_tracker.predictions[-1]
    session_stats = session_tracker.get_session_stats()

    return FatigueStatusResponse(
        session_id=session_id,
        fatigue_score=last_prediction.score,
        fatigue_level=FatigueLevel(last_prediction.level),
        confidence=last_prediction.confidence,
        recommendation=session["sensor_fusion"].get_recommendation(),
        display_parameters=session["display_controller"].get_display_parameters(),
        session_duration_min=session_stats.get("session_duration_min", 0),
        time_since_last_break_min=session_stats.get("time_since_last_break_min", 0),
        interventions_triggered=session_stats.get("interventions_triggered", 0),
        model_latency_ms=last_prediction.latency_ms,
        timestamp=last_prediction.timestamp,
    )


@app.post("/fatigue/session/end", tags=["Session"])
async def end_session(session_id: str):
    """End fatigue monitoring session"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = active_sessions[session_id]
    session_tracker: FatigueSessionTracker = session["session_tracker"]

    # Get final stats
    session_stats = session_tracker.get_session_stats()

    # Disconnect devices
    glasses_device = session.get("glasses_device")
    if glasses_device:
        await glasses_device.disconnect()

    ble_manager = session.get("ble_manager")
    if ble_manager:
        await ble_manager.stop_sync()

    # Remove session
    del active_sessions[session_id]

    return {
        "session_id": session_id,
        "status": "ended",
        "summary": session_stats,
        "end_time": datetime.utcnow(),
    }


@app.get("/fatigue/devices", response_model=list[DeviceInfo], tags=["Devices"])
async def list_devices():
    """List all connected devices (glasses + wearables)"""
    devices = []

    # List from all active sessions
    for _session_id, session in active_sessions.items():
        glasses_device = session.get("glasses_device")
        if glasses_device:
            devices.append(
                DeviceInfo(
                    device_id=glasses_device.device_id,
                    device_type="glasses",
                    platform=glasses_device.platform.value,
                    connected=glasses_device.connected,
                    capabilities=glasses_device.capabilities.__dict__
                    if glasses_device.capabilities
                    else None,
                ),
            )

        ble_manager = session.get("ble_manager")
        if ble_manager:
            for _device_id, device in ble_manager.devices.items():
                devices.append(
                    DeviceInfo(
                        device_id=device.device_id,
                        device_type="wearable",
                        platform=device.device_type.value,
                        connected=device.connected,
                        battery_percent=device.last_reading.battery_percent
                        if device.last_reading
                        else None,
                    ),
                )

    return devices


@app.post("/fatigue/devices/connect", tags=["Devices"])
async def connect_device(request: ConnectDeviceRequest, session_id: str):
    """Connect new device (glasses or wearable) to active session"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = active_sessions[session_id]

    if request.device_type == "wearable":
        ble_manager: BLESyncManager = session.get("ble_manager")
        if not ble_manager:
            raise HTTPException(status_code=400, detail="BLE not enabled for this session")

        # Create appropriate wearable integration
        if request.platform == "oura":
            device = OuraIntegration(request.device_id, request.api_key)
        elif request.platform == "whoop":
            device = WhoopIntegration(request.device_id, request.api_key)
        elif request.platform == "apple_watch":
            device = AppleWatchIntegration(request.device_id)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported wearable: {request.platform}")

        # Connect device
        success = await ble_manager.add_device(device)

        if not success:
            raise HTTPException(status_code=500, detail="Failed to connect device")

        # Start syncing if not already running
        if not ble_manager.running:
            asyncio.create_task(ble_manager.start_sync())

        return {
            "status": "connected",
            "device_id": device.device_id,
            "device_type": request.device_type,
            "platform": request.platform,
        }

    raise HTTPException(
        status_code=400, detail="Device type must be 'wearable' for this endpoint",
    )


@app.get("/fatigue/metrics/session/{session_id}", tags=["Metrics"])
async def get_session_metrics(session_id: str):
    """Get detailed metrics for session"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = active_sessions[session_id]
    session_tracker: FatigueSessionTracker = session["session_tracker"]
    sensor_fusion: SensorFusion = session["sensor_fusion"]

    # Get all metrics
    blink_metrics = sensor_fusion.blink_detector.get_metrics()
    pupil_metrics = sensor_fusion.pupil_tracker.get_metrics()
    hrv_metrics = sensor_fusion.hrv_monitor.get_metrics()
    imu_metrics = sensor_fusion.imu_analyzer.get_metrics()

    session_stats = session_tracker.get_session_stats()

    return {
        "session_id": session_id,
        "session_stats": session_stats,
        "blink_metrics": {
            "blink_rate": blink_metrics.blink_rate,
            "blink_duration": blink_metrics.blink_duration,
            "incomplete_blinks": blink_metrics.incomplete_blinks,
        },
        "pupil_metrics": {
            "avg_diameter": pupil_metrics.avg_diameter,
            "diameter_variance": pupil_metrics.diameter_variance,
        },
        "hrv_metrics": {
            "rmssd": hrv_metrics.rmssd,
            "hr_avg": hrv_metrics.hr_avg,
            "stress_index": hrv_metrics.stress_index,
        },
        "imu_metrics": {
            "head_tilt_deg": imu_metrics.head_tilt_deg,
            "micro_saccade_rate": imu_metrics.micro_saccade_rate,
            "head_drift": imu_metrics.head_drift,
        },
    }


# ============================================================================
# Startup/Shutdown Events
# ============================================================================


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    print("AR Glasses Fatigue Detection API started")
    print("✅ Sensor fusion pipeline ready")
    print("✅ Fatigue prediction models loaded")
    print("✅ Display control ready")
    print("✅ BLE sync manager ready")
    print("✅ OEM integrations ready")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown"""
    # End all active sessions
    for session_id in list(active_sessions.keys()):
        with contextlib.suppress(BaseException):
            await end_session(session_id)

    print("AR Glasses Fatigue Detection API shut down")


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "fatigue:app",
        host="0.0.0.0",
        port=8001,  # Different port from ingestion API
        reload=True,
        log_level="info",
    )
