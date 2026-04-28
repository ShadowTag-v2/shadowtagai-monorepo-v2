# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Digital Freeway Coordination API
Pure software coordination layer for autonomous vehicles.
"""

import os
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import BackgroundTasks, FastAPI
from google.cloud import pubsub_v1
from pydantic import BaseModel

# Configuration
PROJECT_ID = os.getenv("GCP_PROJECT_ID", "shadowtag-omega-v2")
TELEMETRY_TOPIC = os.getenv("TELEMETRY_TOPIC", "vehicle-telemetry")
COORDINATION_TOPIC = os.getenv("COORDINATION_TOPIC", "coordination-vectors")


# Models
class VehicleTelemetry(BaseModel):
    """Incoming vehicle telemetry data."""

    vehicle_id: str
    timestamp: datetime
    latitude: float
    longitude: float
    speed_mps: float  # meters per second
    heading: float  # degrees 0-360
    acceleration: float | None = 0.0
    lane: int | None = None


class CoordinationVector(BaseModel):
    """Outgoing coordination recommendation."""

    vehicle_id: str
    timestamp: datetime
    recommended_speed_mps: float
    throttle_adjustment: float  # -1.0 to 1.0
    lane_change: str | None = None  # "left", "right", or None
    confidence: float  # 0.0 to 1.0


class HealthResponse(BaseModel):
    status: str
    version: str
    agents_active: int
    vehicles_tracked: int


# State
class CoordinationState:
    def __init__(self):
        self.vehicles: dict[str, VehicleTelemetry] = {}
        self.publisher: pubsub_v1.PublisherClient | None = None

    async def init_pubsub(self):
        """Initialize Pub/Sub client."""
        try:
            self.publisher = pubsub_v1.PublisherClient()
        except Exception as e:
            print(f"Pub/Sub init failed (running locally?): {e}")

    def update_vehicle(self, telemetry: VehicleTelemetry):
        """Update vehicle state."""
        self.vehicles[telemetry.vehicle_id] = telemetry

    def get_vehicle_count(self) -> int:
        return len(self.vehicles)


state = CoordinationState()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    await state.init_pubsub()
    print(f"Digital Freeway API started - Project: {PROJECT_ID}")
    yield
    # Shutdown
    print("Digital Freeway API shutting down")


# FastAPI App
app = FastAPI(
    title="Digital Freeway Coordination API",
    description="Pure software coordination layer for autonomous vehicles",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version="0.1.0",
        agents_active=3,  # Ingest, Optimize, Output
        vehicles_tracked=state.get_vehicle_count(),
    )


@app.post("/telemetry", response_model=CoordinationVector)
async def receive_telemetry(telemetry: VehicleTelemetry, background_tasks: BackgroundTasks):
    """Receive vehicle telemetry and return coordination vector.

    This is the main API endpoint - vehicles send their state,
    we return optimal behavior recommendations.
    """
    # Update state
    state.update_vehicle(telemetry)

    # TODO: Replace with actual agent chain
    # For now, simple speed recommendation
    coordination = await compute_coordination(telemetry)

    # Publish to Pub/Sub in background (non-blocking)
    if state.publisher:
        background_tasks.add_task(publish_coordination, coordination)

    return coordination


async def compute_coordination(telemetry: VehicleTelemetry) -> CoordinationVector:
    """Compute coordination vector for a vehicle.

    TODO: This will be replaced by the 3-agent chain:
    1. Ingest Agent - normalize telemetry
    2. Optimize Agent - run Graph RL/OR-Tools
    3. Output Agent - generate V2X vectors
    """
    # Placeholder logic - maintain smooth flow
    target_speed = 25.0  # ~55 mph optimal flow
    speed_delta = target_speed - telemetry.speed_mps

    # Clamp throttle adjustment
    throttle = max(-1.0, min(1.0, speed_delta / 10.0))

    return CoordinationVector(
        vehicle_id=telemetry.vehicle_id,
        timestamp=datetime.utcnow(),
        recommended_speed_mps=target_speed,
        throttle_adjustment=throttle,
        lane_change=None,
        confidence=0.85,
    )


async def publish_coordination(coordination: CoordinationVector):
    """Publish coordination vector to Pub/Sub."""
    if not state.publisher:
        return

    topic_path = state.publisher.topic_path(PROJECT_ID, COORDINATION_TOPIC)
    data = coordination.model_dump_json().encode("utf-8")

    try:
        future = state.publisher.publish(topic_path, data)
        future.result(timeout=5)
    except Exception as e:
        print(f"Pub/Sub publish failed: {e}")


@app.get("/vehicles")
async def list_vehicles():
    """List all tracked vehicles."""
    return {"count": state.get_vehicle_count(), "vehicles": list(state.vehicles.keys())}


@app.get("/metrics")
async def get_metrics():
    """Get coordination metrics."""
    if not state.vehicles:
        return {"message": "No vehicles tracked yet"}

    speeds = [v.speed_mps for v in state.vehicles.values()]
    return {
        "vehicles_tracked": len(speeds),
        "avg_speed_mps": sum(speeds) / len(speeds) if speeds else 0,
        "min_speed_mps": min(speeds) if speeds else 0,
        "max_speed_mps": max(speeds) if speeds else 0,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
