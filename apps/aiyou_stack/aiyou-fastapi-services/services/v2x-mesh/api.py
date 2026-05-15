import os

"""V2X Mesh API Service

import os
FastAPI application for V2X mesh network management.

Endpoints:
- POST /v1/events - Broadcast event to mesh
- GET  /v1/events/nearby - Query nearby events
- POST /v1/map/features - Add/update map feature
- GET  /v1/map/features - Query map features
- GET  /v1/mesh/peers - Get active peers
- GET  /v1/mesh/stats - Get mesh statistics
- WS   /v1/mesh/stream - WebSocket for real-time updates
"""

import time
from contextlib import asynccontextmanager
from typing import Any

import uvicorn
from crdt_mapping import CRDTMapStore, MapFeature
from edge_reasoning import AttentionContext, EdgeReasoningPipeline
from fastapi import FastAPI, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from safety_moderation import V2XSafetyModerator
from shadowtag_attestation import ShadowTagAttestation
from vehicle_client import V2XClientConfig, VehicleClient


# Pydantic models for API
class EventRequest(BaseModel):
    event_type: str = Field(..., description="Event type (collision_risk, hard_brake, etc.)")
    severity: int = Field(..., ge=0, le=10, description="Severity level 0-10")
    description: str = Field(..., max_length=500, description="Event description")
    position: tuple[float, float, float] = Field(..., description="Position (lat, lon, altitude)")
    affected_radius_m: float = Field(default=1000, description="Affected radius in meters")
    sensor_data_hash: str | None = Field(None, description="Hash of supporting sensor data")


class EventResponse(BaseModel):
    event_id: str
    status: str
    broadcast_time_ms: float
    moderation_passed: bool


class MapFeatureRequest(BaseModel):
    feature_type: str = Field(..., description="Feature type (work_zone, hazard, poi)")
    geometry: dict[str, Any] = Field(..., description="GeoJSON geometry")
    properties: dict[str, Any] = Field(..., description="Feature properties")
    valid_until: int | None = Field(None, description="Expiry timestamp (ms)")


class MapFeatureResponse(BaseModel):
    feature_id: str
    delta_id: str
    status: str


class MapQueryRequest(BaseModel):
    min_lat: float
    max_lat: float
    min_lon: float
    max_lon: float
    feature_types: list[str] | None = None


class MeshStatsResponse(BaseModel):
    active_peers: int
    total_messages_processed: int
    beacons_sent: int
    events_received: int
    fsd_interventions: int
    map_features_count: int
    uptime_seconds: float


class HealthResponse(BaseModel):
    status: str
    timestamp: int
    version: str


# Global state
class AppState:
    def __init__(self):
        self.vehicle_client: VehicleClient | None = None
        self.map_store: CRDTMapStore | None = None
        self.attestation: ShadowTagAttestation | None = None
        self.moderator: V2XSafetyModerator | None = None
        self.edge_pipeline: EdgeReasoningPipeline | None = None
        self.websocket_clients: list[WebSocket] = []


app_state = AppState()


# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup V2X mesh service"""
    # Startup
    print("Starting V2X Mesh Service...")

    # Initialize components
    config = V2XClientConfig(vehicle_id="mesh-gateway-001", vehicle_type="infrastructure")

    app_state.vehicle_client = VehicleClient(config=config)
    app_state.map_store = CRDTMapStore(node_id="mesh-gateway-001")
    app_state.attestation = ShadowTagAttestation(
        vehicle_id="mesh-gateway-001",
        use_tee=False,  # Gateway doesn't need TEE
    )
    app_state.moderator = V2XSafetyModerator()

    # Create edge reasoning pipeline
    context = AttentionContext(
        vehicle_position=(0.0, 0.0),
        vehicle_velocity=(0.0, 0.0),
        vehicle_heading=0.0,
    )
    app_state.edge_pipeline = EdgeReasoningPipeline(context, use_gpu=True)

    # Start vehicle client
    await app_state.vehicle_client.start()

    print("V2X Mesh Service started successfully")

    yield

    # Shutdown
    print("Shutting down V2X Mesh Service...")
    if app_state.vehicle_client:
        await app_state.vehicle_client.stop()


# Create FastAPI app
app = FastAPI(
    title="ShadowTag-v4 V2X Mesh API",
    description="API for V2X mesh network management and vehicle communication",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get(
        "CORS_ORIGINS", "http://localhost:3000,http://localhost:8000"
    ).split(","),
    allow_credentials=True,
    allow_methods=os.environ.get("CORS_METHODS", "GET,POST,PUT,DELETE,OPTIONS,PATCH").split(","),
    allow_headers=os.environ.get(
        "CORS_HEADERS", "Content-Type,Authorization,X-Requested-With"
    ).split(","),
)


# Health check endpoints
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(status="healthy", timestamp=int(time.time() * 1000), version="1.0.0")


@app.get("/ready", response_model=HealthResponse)
async def readiness_check():
    """Readiness check endpoint"""
    if not app_state.vehicle_client or not app_state.vehicle_client.running:
        raise HTTPException(status_code=503, detail="Service not ready")

    return HealthResponse(status="ready", timestamp=int(time.time() * 1000), version="1.0.0")


# Event endpoints
@app.post("/v1/events", response_model=EventResponse)
async def broadcast_event(event: EventRequest):
    """Broadcast safety event to mesh network"""
    start_time = time.time()

    # Moderate event content
    is_safe, moderation_result = await app_state.moderator.moderate_event_message(
        {
            "event_type": event.event_type,
            "severity": event.severity,
            "description": event.description,
        },
    )

    if not is_safe:
        raise HTTPException(
            status_code=400,
            detail=f"Event blocked by moderation: {moderation_result.categories}",
        )

    # Broadcast event
    await app_state.vehicle_client.broadcast_event(
        event_type=event.event_type,
        severity=event.severity,
        description=event.description,
        affected_radius_m=event.affected_radius_m,
        sensor_data_hash=event.sensor_data_hash,
    )

    # Notify WebSocket clients
    await broadcast_to_websockets({"type": "event", "data": event.dict()})

    broadcast_time = (time.time() - start_time) * 1000

    return EventResponse(
        event_id=f"evt-{int(time.time() * 1000)}",
        status="broadcast",
        broadcast_time_ms=broadcast_time,
        moderation_passed=True,
    )


@app.get("/v1/events/nearby")
async def get_nearby_events(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    radius_m: float = Query(1000, description="Search radius in meters"),
):
    """Get nearby events from mesh"""
    # In production, query from mesh state cache
    # For now, return from vehicle client stats

    stats = app_state.vehicle_client.get_stats()

    return {
        "position": {"lat": lat, "lon": lon},
        "radius_m": radius_m,
        "events": [],  # Would be populated from actual mesh cache
        "stats": stats,
    }


# Map endpoints
@app.post("/v1/map/features", response_model=MapFeatureResponse)
async def add_map_feature(feature_req: MapFeatureRequest):
    """Add or update map feature"""
    import uuid

    # Create feature
    feature = MapFeature(
        feature_id=str(uuid.uuid4()),
        feature_type=feature_req.feature_type,
        geometry=feature_req.geometry,
        properties=feature_req.properties,
        created_at=int(time.time() * 1000),
        updated_at=int(time.time() * 1000),
        creator_node="mesh-gateway-001",
        valid_until=feature_req.valid_until,
    )

    # Moderate content
    is_safe, moderation_result = await app_state.moderator.moderate_map_update(
        {
            "feature_id": feature.feature_id,
            "feature_type": feature.feature_type,
            "properties": feature.properties,
        },
    )

    if not is_safe:
        raise HTTPException(
            status_code=400,
            detail=f"Map feature blocked by moderation: {moderation_result.categories}",
        )

    # Create delta
    delta = app_state.map_store.create_delta("add", feature)

    # Notify WebSocket clients
    await broadcast_to_websockets(
        {
            "type": "map_update",
            "data": {
                "feature_id": feature.feature_id,
                "delta_id": delta.delta_id,
                "feature_type": feature.feature_type,
            },
        },
    )

    return MapFeatureResponse(
        feature_id=feature.feature_id,
        delta_id=delta.delta_id,
        status="added",
    )


@app.post("/v1/map/features/query")
async def query_map_features(query: MapQueryRequest):
    """Query map features in area"""
    features = app_state.map_store.query_area(
        min_lat=query.min_lat,
        max_lat=query.max_lat,
        min_lon=query.min_lon,
        max_lon=query.max_lon,
        feature_types=query.feature_types,
    )

    return {
        "count": len(features),
        "features": [
            {
                "feature_id": f.feature_id,
                "feature_type": f.feature_type,
                "geometry": f.geometry,
                "properties": f.properties,
                "created_at": f.created_at,
                "valid_until": f.valid_until,
            }
            for f in features
        ],
    }


# Mesh endpoints
@app.get("/v1/mesh/peers")
async def get_mesh_peers():
    """Get active mesh peers"""
    gossip_stats = app_state.vehicle_client.gossip.get_stats()

    peers = []
    for peer_id, peer_info in app_state.vehicle_client.gossip.peers.items():
        peers.append(
            {
                "peer_id": peer_id.hex(),
                "last_seen": peer_info.last_seen,
                "position": peer_info.position,
                "distance_m": peer_info.distance_m,
                "reliability_score": peer_info.reliability_score,
            },
        )

    return {"count": len(peers), "peers": peers, "stats": gossip_stats}


@app.get("/v1/mesh/stats", response_model=MeshStatsResponse)
async def get_mesh_stats():
    """Get mesh network statistics"""
    client_stats = app_state.vehicle_client.get_stats()
    map_stats = app_state.map_store.get_stats()

    return MeshStatsResponse(
        active_peers=client_stats.get("active_peers", 0),
        total_messages_processed=client_stats.get("total_messages_processed", 0),
        beacons_sent=client_stats.get("beacons_sent", 0),
        events_received=client_stats.get("events_received", 0),
        fsd_interventions=client_stats.get("fsd_interventions", 0),
        map_features_count=map_stats.get("active_features", 0),
        uptime_seconds=client_stats.get("uptime_seconds", 0),
    )


# WebSocket endpoint
@app.websocket("/v1/mesh/stream")
async def mesh_stream(websocket: WebSocket):
    """WebSocket stream for real-time mesh updates"""
    await websocket.accept()
    app_state.websocket_clients.append(websocket)

    try:
        # Send initial state
        await websocket.send_json({"type": "connected", "timestamp": int(time.time() * 1000)})

        # Keep connection alive and receive messages
        while True:
            data = await websocket.receive_text()
            # Echo back or process client messages
            await websocket.send_json({"type": "ack", "data": data})

    except WebSocketDisconnect:
        app_state.websocket_clients.remove(websocket)


async def broadcast_to_websockets(message: dict):
    """Broadcast message to all connected WebSocket clients"""
    disconnected = []

    for client in app_state.websocket_clients:
        try:
            await client.send_json(message)
        except Exception:
            disconnected.append(client)

    # Remove disconnected clients
    for client in disconnected:
        app_state.websocket_clients.remove(client)


# Metrics endpoint (Prometheus format)
@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    client_stats = app_state.vehicle_client.get_stats()
    map_stats = app_state.map_store.get_stats()
    mod_stats = app_state.moderator.get_stats()

    metrics_text = f"""# HELP v2x_active_peers Number of active mesh peers
# TYPE v2x_active_peers gauge
v2x_active_peers {client_stats.get("active_peers", 0)}

# HELP v2x_messages_processed_total Total messages processed
# TYPE v2x_messages_processed_total counter
v2x_messages_processed_total {client_stats.get("total_messages_processed", 0)}

# HELP v2x_events_received_total Total events received
# TYPE v2x_events_received_total counter
v2x_events_received_total {client_stats.get("events_received", 0)}

# HELP v2x_fsd_interventions_total Total FSD interventions triggered
# TYPE v2x_fsd_interventions_total counter
v2x_fsd_interventions_total {client_stats.get("fsd_interventions", 0)}

# HELP v2x_map_features_count Number of active map features
# TYPE v2x_map_features_count gauge
v2x_map_features_count {map_stats.get("active_features", 0)}

# HELP v2x_moderation_blocked_total Total content blocked by moderation
# TYPE v2x_moderation_blocked_total counter
v2x_moderation_blocked_total {mod_stats.get("blocked", 0)}
"""

    return JSONResponse(content=metrics_text, media_type="text/plain")


if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8010, log_level="info", access_log=True)
