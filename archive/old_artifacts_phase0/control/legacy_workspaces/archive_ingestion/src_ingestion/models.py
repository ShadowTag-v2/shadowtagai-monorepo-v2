"""Data models for ingestion pipeline"""

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, validator


class ScenarioTier(StrEnum):
    """Tier classification for scenarios"""

    TIER_1 = "tier_1"  # Critical safety scenarios
    TIER_2 = "tier_2"  # High-value edge cases
    TIER_3 = "tier_3"  # Baseline training data


class DataSource(StrEnum):
    """Available data sources"""

    FLEET_TELEMETRY = "fleet_telemetry"
    SIMULATION = "simulation"
    PUBLIC_DATASET = "public_dataset"
    EDGE_CASES = "edge_cases"


class WeatherCondition(StrEnum):
    """Weather classifications"""

    CLEAR = "clear"
    RAIN = "rain"
    SNOW = "snow"
    FOG = "fog"
    HEAVY_RAIN = "heavy_rain"
    MIXED = "mixed"


class TimeOfDay(StrEnum):
    """Time of day classifications"""

    DAY = "day"
    NIGHT = "night"
    DAWN = "dawn"
    DUSK = "dusk"


class SensorData(BaseModel):
    """Sensor frame data"""

    timestamp: datetime
    camera_frames: list[str] | None = None  # Cloud Storage paths
    lidar_pointclouds: list[str] | None = None
    radar_tracks: list[str] | None = None
    imu_data: dict[str, Any] | None = None
    gps_data: dict[str, float] | None = None  # lat, lon (obfuscated)


class Scenario(BaseModel):
    """Core scenario data structure"""

    scenario_id: str = Field(..., description="Unique identifier")
    source: DataSource
    tier: ScenarioTier | None = None
    ingestion_date: datetime = Field(default_factory=datetime.utcnow)

    # Scoring
    safety_score: float | None = Field(None, ge=0, le=100)
    complexity_score: float | None = Field(None, ge=0, le=100)
    final_score: float | None = Field(None, ge=0, le=100)

    # Metadata
    duration_seconds: float = Field(..., gt=0)
    num_agents: int = Field(..., ge=0)
    weather_condition: WeatherCondition
    time_of_day: TimeOfDay

    # Sensor data
    sensor_data: SensorData

    # Privacy & Compliance
    privacy_scrubbed: bool = False
    consent_verified: bool = False

    # Storage
    storage_path: str | None = None
    cost_usd: float | None = Field(None, ge=0)

    @validator("final_score", always=True)
    def calculate_final_score(cls, v, values):
        """Auto-calculate final score if not provided"""
        if v is None and values.get("safety_score") and values.get("complexity_score"):
            return 0.6 * values["safety_score"] + 0.4 * values["complexity_score"]
        return v

    @validator("tier", always=True)
    def classify_tier(cls, v, values):
        """Auto-classify tier based on final score"""
        if v is None and values.get("final_score"):
            score = values["final_score"]
            if score >= 80:
                return ScenarioTier.TIER_1
            elif score >= 50:
                return ScenarioTier.TIER_2
            else:
                return ScenarioTier.TIER_3
        return v


class DailyMetadata(BaseModel):
    """Daily ingestion summary"""

    date: datetime
    total_scenarios: int
    tier_1_count: int
    tier_2_count: int
    tier_3_count: int

    # Quality gates
    volume_gate_status: str  # "✅", "⚠️", "❌"
    diversity_gate_status: str
    cost_gate_status: str
    relevance_gate_status: str

    # Source breakdown
    source_counts: dict[DataSource, int]

    # Anomalies
    anomalies: list[str] = Field(default_factory=list)

    # Cost
    total_cost_usd: float
    avg_cost_per_scenario: float

    # Runtime
    runtime_minutes: float

    @property
    def tier_1_pct(self) -> float:
        if self.total_scenarios == 0:
            return 0.0
        return round(100 * self.tier_1_count / self.total_scenarios, 1)

    @property
    def tier_2_pct(self) -> float:
        if self.total_scenarios == 0:
            return 0.0
        return round(100 * self.tier_2_count / self.total_scenarios, 1)

    @property
    def tier_3_pct(self) -> float:
        if self.total_scenarios == 0:
            return 0.0
        return round(100 * self.tier_3_count / self.total_scenarios, 1)


class QualityGateResult(BaseModel):
    """Result of a quality gate check"""

    gate_name: str
    passed: bool
    measured_value: Any
    target_value: Any
    status_emoji: str  # "✅", "⚠️", "❌"
    message: str


class AMBriefing(BaseModel):
    """Morning briefing report"""

    date: datetime
    executive_summary: str
    quality_gates: list[QualityGateResult]
    top_tier1_scenarios: list[str]  # scenario_ids
    anomalies: list[str]
    cost_performance: dict[str, Any]
    recommendations: list[str]
