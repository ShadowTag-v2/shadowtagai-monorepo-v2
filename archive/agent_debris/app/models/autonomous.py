"""Pydantic models for autonomous systems API."""

from typing import Any
from pydantic import BaseModel, Field


class Position3D(BaseModel):
    """3D position."""

    x: float = Field(..., description="X coordinate (meters)")
    y: float = Field(..., description="Y coordinate (meters)")
    z: float = Field(..., description="Z coordinate (meters)")


class Waypoint(BaseModel):
    """Flight waypoint."""

    x: float
    y: float
    z: float
    yaw: float = Field(0.0, description="Heading in radians")
    speed: float | None = Field(None, description="Target speed at waypoint (m/s)")


class PathPlanningRequest(BaseModel):
    """Request for path planning."""

    start: Position3D
    goal: Position3D
    map_id: str = Field(..., description="HD map identifier")
    safety_margin: float = Field(2.0, ge=0.5, le=10.0, description="Safety margin around obstacles (meters)")
    validate_safety: bool = Field(True, description="Use Judge #6 for safety validation")
    algorithm: str = Field("a_star", description="Planning algorithm (a_star, rrt, rrt_star)")


class PathPlanningResponse(BaseModel):
    """Response for path planning."""

    waypoints: list[Waypoint]
    total_distance: float
    estimated_time: float
    safety_score: float = Field(..., ge=0.0, le=1.0)
    obstacles_detected: int
    reasoning: str
    latency_ms: float


class LocalizationRequest(BaseModel):
    """Request for localization."""

    lidar_scan: str | None = Field(None, description="Base64-encoded point cloud (PCD format)")
    map_id: str
    initial_pose: Position3D | None = Field(None, description="Initial pose estimate")


class Pose(BaseModel):
    """6-DOF pose."""

    position: Position3D
    orientation: dict[str, float] = Field(..., description="Quaternion {x, y, z, w}")
    covariance: list[float] | None = Field(None, description="6x6 covariance matrix (flattened)")


class LocalizationResponse(BaseModel):
    """Response for localization."""

    pose: Pose
    accuracy: float = Field(..., description="Localization accuracy (meters)")
    confidence: float = Field(..., ge=0.0, le=1.0)
    latency_ms: float


class Obstacle(BaseModel):
    """Detected obstacle."""

    id: str
    position: Position3D
    dimensions: dict[str, float]  # {length, width, height} in meters
    velocity: Position3D | None = Field(None, description="Velocity vector (m/s)")
    classification: str | None = Field(None, description="Obstacle type (person, vehicle, etc.)")


class ObstacleDetectionRequest(BaseModel):
    """Request for obstacle detection."""

    lidar_scan: str = Field(..., description="Base64-encoded point cloud")
    detection_range: float = Field(50.0, ge=10.0, le=100.0, description="Detection range (meters)")
    include_static: bool = Field(True, description="Include static obstacles")
    include_dynamic: bool = Field(True, description="Include dynamic obstacles")


class ObstacleDetectionResponse(BaseModel):
    """Response for obstacle detection."""

    obstacles: list[Obstacle]
    timestamp: str
    latency_ms: float


class MissionPlanningRequest(BaseModel):
    """Request for high-level mission planning."""

    mission_type: str = Field(..., description="Mission type (patrol, inspection, delivery, search_rescue)")
    area_bounds: dict[str, Any] | None = Field(None, description="Geographic bounds {min_lat, max_lat, min_lon, max_lon}")
    waypoints: list[Waypoint] | None = Field(None, description="Pre-defined waypoints")
    map_id: str
    constraints: dict[str, Any] | None = Field(None, description="Mission constraints (max_altitude, no_fly_zones, etc.)")


class MissionPlan(BaseModel):
    """Mission plan."""

    mission_id: str
    waypoints: list[Waypoint]
    estimated_duration: float  # seconds
    estimated_distance: float  # meters
    safety_validations: list[dict[str, Any]]  # Judge #6 validations per segment
    reasoning: str  # Cor.17 reasoning for mission plan


class MissionPlanningResponse(BaseModel):
    """Response for mission planning."""

    mission_plan: MissionPlan
    latency_ms: float


class BuildMapRequest(BaseModel):
    """Request for HD map building."""

    map_id: str
    lidar_scans: list[str] = Field(..., description="List of base64-encoded point clouds")
    initial_pose: Position3D
    map_resolution: float = Field(0.1, ge=0.05, le=1.0, description="Map resolution (meters)")


class BuildMapResponse(BaseModel):
    """Response for map building."""

    map_id: str
    map_size: dict[str, float]  # {x_meters, y_meters, z_meters}
    point_count: int
    storage_path: str
    latency_ms: float


class SimulationRequest(BaseModel):
    """Request for Gazebo simulation."""

    scenario: str = Field(..., description="Simulation scenario (warehouse, city, outdoor)")
    drone_model: str = Field("iris", description="Drone model (iris, solo, custom)")
    mission_plan: MissionPlan | None = Field(None, description="Mission to simulate")
    real_time_factor: float = Field(1.0, ge=0.1, le=10.0, description="Simulation speed multiplier")


class SimulationMetrics(BaseModel):
    """Simulation metrics."""

    success: bool
    completion_time: float  # seconds
    collisions: int
    safety_violations: int
    trajectory_error: float  # meters (RMS)
    energy_consumed: float | None = Field(None, description="Battery consumed (mAh)")


class SimulationResponse(BaseModel):
    """Response for simulation."""

    simulation_id: str
    metrics: SimulationMetrics
    trajectory_log: str | None = Field(None, description="Path to trajectory CSV")
    video_recording: str | None = Field(None, description="Path to simulation video")
    latency_ms: float


class FlightTelemetry(BaseModel):
    """Real-time flight telemetry."""

    timestamp: str
    pose: Pose
    velocity: Position3D  # m/s
    battery_percent: float
    gps_satellites: int
    flight_mode: str  # manual, stabilized, position, mission, rtl
    armed: bool


class FlightCommand(BaseModel):
    """Flight controller command."""

    command_type: str = Field(..., description="Command type (arm, disarm, takeoff, land, goto, rtl)")
    parameters: dict[str, Any] | None = Field(None, description="Command-specific parameters")


class FlightCommandResponse(BaseModel):
    """Response for flight command."""

    command_id: str
    status: str  # accepted, rejected, executing, completed, failed
    message: str
    latency_ms: float
