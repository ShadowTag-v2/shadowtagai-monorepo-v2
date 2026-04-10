"""
AR Glasses Fatigue Detection - Quick Start Example

This example demonstrates how to use the fatigue detection SDK
to monitor a simulated AR glasses session.
"""

import asyncio
import random
import sys
from datetime import datetime

sys.path.append("/home/user/shadowtag_v4-fastapi-services/src")

from fatigue.ble import BLESyncManager, OuraIntegration
from fatigue.display import DisplayController
from fatigue.integration import AppleVisionProAdapter
from fatigue.models import AdaptiveFatiguePredictor, FatigueSessionTracker
from fatigue.sensors import SensorFusion


async def simulate_ar_session():
    """
    Simulate a 5-minute AR glasses session with fatigue detection

    Simulates:
    - Eye tracking (blink detection, pupil diameter)
    - HRV from Oura Ring
    - Head pose from IMU
    - Real-time fatigue prediction
    - Adaptive display adjustments
    """

    print("=" * 70)
    print("AR Glasses Fatigue Detection - Quick Start")
    print("=" * 70)
    print()

    # ========================================================================
    # 1. Initialize Components
    # ========================================================================

    print("📊 Initializing components...")

    # Sensor fusion (combines all biosignals)
    sensor_fusion = SensorFusion()

    # Fatigue predictor (adaptive model selection)
    fatigue_predictor = AdaptiveFatiguePredictor(device_tier="mid")  # Use GBDT model

    # Display controller (adaptive brightness/hue/contrast)
    display_controller = DisplayController()

    # Session tracker (monitors progression over time)
    session_tracker = FatigueSessionTracker()

    # BLE manager (connect wearables)
    ble_manager = BLESyncManager()

    # AR glasses device (Apple Vision Pro example)
    glasses = AppleVisionProAdapter(device_id="vision_pro_001")

    print("✅ Components initialized")
    print()

    # ========================================================================
    # 2. Connect Devices
    # ========================================================================

    print("🔌 Connecting devices...")

    # Connect to glasses
    await glasses.connect()
    capabilities = await glasses.get_capabilities()
    print("✅ Connected to Apple Vision Pro")
    print(f"   - Eye tracking: {capabilities.has_inward_camera}")
    print(f"   - Display control: {capabilities.has_display_control}")
    print(f"   - Max brightness: {capabilities.max_brightness_nits} nits")

    # Connect to Oura Ring (for HRV)
    oura = OuraIntegration(device_id="oura_ring_001", api_token="demo_token")
    await ble_manager.add_device(oura)
    print("✅ Connected to Oura Ring")

    print()

    # ========================================================================
    # 3. Start Monitoring Session
    # ========================================================================

    print("🎯 Starting fatigue monitoring session...")
    print("   Duration: 5 minutes (simulated)")
    print("   Update interval: 5 seconds")
    print()

    session_start = datetime.utcnow()
    update_count = 0
    total_updates = 60  # 5 minutes * 12 updates/minute

    # Start BLE sync in background
    asyncio.create_task(ble_manager.start_sync())

    # ========================================================================
    # 4. Simulation Loop
    # ========================================================================

    for i in range(total_updates):
        update_count += 1
        elapsed_min = (i * 5) / 60  # 5-second intervals

        # Simulate progressive fatigue (gets worse over time)
        fatigue_progression = i / total_updates  # 0.0 → 1.0

        # ----------------------------------------------------------------------
        # Simulate Sensor Data
        # ----------------------------------------------------------------------

        # Blink detection: Rate decreases with fatigue
        baseline_blink_rate = 15.0  # blinks per minute
        current_blink_rate = baseline_blink_rate - (fatigue_progression * 7)  # Down to 8 bpm

        # Simulate blinks (randomly)
        if random.random() < (current_blink_rate / 60):  # Probability per second
            eye_closure = 1.0  # Blink detected
        else:
            eye_closure = 0.0  # Eyes open

        # Process blink
        blink_reading = sensor_fusion.blink_detector.process_frame(eye_closure, datetime.utcnow())

        # Pupil diameter: Decreases with mental fatigue
        baseline_pupil = 3.5  # mm
        pupil_diameter = baseline_pupil - (fatigue_progression * 1.0)  # Down to 2.5mm
        pupil_diameter += random.gauss(0, 0.1)  # Add noise

        sensor_fusion.pupil_tracker.add_reading(
            left_mm=pupil_diameter + random.gauss(0, 0.05),
            right_mm=pupil_diameter + random.gauss(0, 0.05),
            timestamp=datetime.utcnow(),
        )

        # HRV: RMSSD decreases with stress/fatigue
        baseline_rmssd = 35.0  # ms
        current_rmssd = baseline_rmssd - (fatigue_progression * 15)  # Down to 20ms
        rr_interval = 60000 / (70 + fatigue_progression * 10)  # HR increases slightly

        sensor_fusion.hrv_monitor.add_rr_interval(
            interval_ms=rr_interval, timestamp=datetime.utcnow()
        )

        # Head pose: Forward tilt increases with fatigue
        baseline_tilt = 5.0  # degrees
        head_tilt = baseline_tilt + (fatigue_progression * 15)  # Up to 20°

        sensor_fusion.imu_analyzer.add_reading(
            pitch_deg=head_tilt + random.gauss(0, 1),
            yaw_deg=random.gauss(0, 2),
            roll_deg=random.gauss(0, 1),
            timestamp=datetime.utcnow(),
        )

        # ----------------------------------------------------------------------
        # Get Fatigue Prediction
        # ----------------------------------------------------------------------

        prediction = fatigue_predictor.predict(sensor_fusion)
        session_tracker.add_prediction(prediction)

        # ----------------------------------------------------------------------
        # Update Display
        # ----------------------------------------------------------------------

        adjustment = display_controller.update(sensor_fusion, prediction)
        display_controller.apply_adjustment(adjustment)

        # Apply to glasses device
        display_params = display_controller.get_display_parameters()
        await glasses.set_display_parameters(display_params)

        # ----------------------------------------------------------------------
        # Print Status (every 12 updates = 1 minute)
        # ----------------------------------------------------------------------

        if update_count % 12 == 0 or prediction.level != "fresh":
            print(
                f"⏱️  {elapsed_min:.1f} min | "
                f"Fatigue: {prediction.level.upper():8s} ({prediction.score:.2f}) | "
                f"Blink: {current_blink_rate:.0f} bpm | "
                f"Pupil: {pupil_diameter:.1f}mm | "
                f"HRV: {current_rmssd:.0f}ms | "
                f"Tilt: {head_tilt:.0f}°"
            )

            # Show display adjustments
            if prediction.score > 0.3:
                print(
                    f"   📺 Display: "
                    f"Brightness {display_params['brightness']:.0%}, "
                    f"Hue {display_params['hue_shift_degrees']:.0f}°, "
                    f"Contrast {display_params['contrast']:.2f}x"
                )

            # Show interventions
            if prediction.level in ["severe", "critical"]:
                print(f"   ⚠️  INTERVENTION: {sensor_fusion.get_recommendation()}")
                print()

        # Check if forced break needed
        if session_tracker.should_force_break():
            print()
            print("🛑 MANDATORY BREAK TRIGGERED")
            print("   Severe fatigue detected. Ending session for safety.")
            break

        # Wait 5 seconds (simulated)
        await asyncio.sleep(0.1)  # Sped up for demo (0.1s instead of 5s)

    # ========================================================================
    # 5. End Session & Summary
    # ========================================================================

    print()
    print("=" * 70)
    print("📊 SESSION SUMMARY")
    print("=" * 70)

    session_stats = session_tracker.get_session_stats()

    print(f"Duration:                  {session_stats['session_duration_min']:.1f} minutes")
    print(f"Average fatigue score:     {session_stats['avg_fatigue_score']:.2f}")
    print(f"Peak fatigue score:        {session_stats['max_fatigue_score']:.2f}")
    print(f"Current fatigue score:     {session_stats['current_fatigue_score']:.2f}")
    print(f"Fatigue trend:             {session_stats['fatigue_trend']}")
    print(f"Breaks taken:              {session_stats['breaks_taken']}")
    print(f"Interventions triggered:   {session_stats['interventions_triggered']}")
    print(f"Time in severe fatigue:    {session_stats['time_in_severe_fatigue_min']:.1f} minutes")
    print()

    # Get final sensor metrics
    blink_metrics = sensor_fusion.blink_detector.get_metrics()
    pupil_metrics = sensor_fusion.pupil_tracker.get_metrics()
    hrv_metrics = sensor_fusion.hrv_monitor.get_metrics()
    imu_metrics = sensor_fusion.imu_analyzer.get_metrics()

    print("📈 FINAL SENSOR METRICS")
    print(f"Blink rate:                {blink_metrics.blink_rate:.1f} bpm (baseline: 15)")
    print(f"Incomplete blinks:         {blink_metrics.incomplete_blinks}")
    print(f"Pupil diameter:            {pupil_metrics.avg_diameter:.2f} mm (baseline: 3.5)")
    print(f"HRV RMSSD:                 {hrv_metrics.rmssd:.1f} ms (baseline: 35)")
    print(f"Heart rate:                {hrv_metrics.hr_avg:.0f} bpm")
    print(f"Stress index:              {hrv_metrics.stress_index:.0f}/100")
    print(f"Head tilt:                 {imu_metrics.head_tilt_deg:.1f}° (baseline: 5)")
    print()

    # Get final display state
    final_display = display_controller.current_state
    print("📺 FINAL DISPLAY STATE")
    print(f"Brightness:                {final_display.brightness:.0%}")
    print(f"Hue shift:                 {final_display.hue_shift:.1f}° (negative = warmer)")
    print(f"Contrast:                  {final_display.contrast:.2f}x")
    print(f"Mode:                      {final_display.mode.value}")
    print()

    # Cleanup
    await ble_manager.stop_sync()
    await glasses.disconnect()

    print("✅ Session ended successfully")
    print("=" * 70)


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    print()
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║                                                                      ║")
    print("║       AR Glasses Fatigue Detection SDK - Quick Start Demo           ║")
    print("║                                                                      ║")
    print("║  This demo simulates a 5-minute AR session with progressive         ║")
    print("║  fatigue, showing real-time detection and adaptive display control. ║")
    print("║                                                                      ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")
    print()

    # Run simulation
    asyncio.run(simulate_ar_session())

    print()
    print("🎉 Demo completed!")
    print()
    print("Next Steps:")
    print("  1. Start the API server: uvicorn src.api.fatigue:app --reload --port 8001")
    print("  2. Open API docs: http://localhost:8001/docs")
    print("  3. Read full documentation: docs/architecture/ar-glasses-fatigue-sdk.md")
    print()
