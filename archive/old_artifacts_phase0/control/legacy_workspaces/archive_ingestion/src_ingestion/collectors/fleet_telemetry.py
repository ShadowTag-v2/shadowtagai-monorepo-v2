"""Fleet telemetry collector - ingests anonymized sensor logs from pilot fleet"""

import asyncio
import os
from datetime import datetime, timedelta
from uuid import uuid4

from ..models import DataSource, Scenario, SensorData, TimeOfDay, WeatherCondition


class FleetTelemetryCollector:
    """Collects telemetry from fleet management API"""

    def __init__(self):
        self.api_key = os.getenv("FLEET_API_KEY")
        self.api_secret = os.getenv("FLEET_API_SECRET")
        self.base_url = os.getenv("FLEET_API_URL", "https://fleet.roadmesh.ai/api/v1")

    async def collect_daily_scenarios(self) -> list[Scenario]:
        """
        Fetch scenarios from the past 24 hours

        Returns:
            List of raw scenarios (pre-privacy scrubbing)
        """
        print("[Fleet Collector] Starting collection...")

        # In production, this would call the Fleet Management API
        # For now, simulate with mock data
        scenarios = await self._fetch_mock_scenarios()

        print(f"[Fleet Collector] Collected {len(scenarios)} scenarios")
        return scenarios

    async def _fetch_mock_scenarios(self) -> list[Scenario]:
        """Mock implementation for demonstration"""
        # Simulate API latency
        await asyncio.sleep(2)

        scenarios = []
        # Generate 2000-3000 mock scenarios
        num_scenarios = 2500

        for i in range(num_scenarios):
            scenario = Scenario(
                scenario_id=f"fleet_{uuid4().hex[:12]}",
                source=DataSource.FLEET_TELEMETRY,
                duration_seconds=float(10 + (i % 50)),
                num_agents=2 + (i % 8),
                weather_condition=self._random_weather(i),
                time_of_day=self._random_time_of_day(i),
                sensor_data=SensorData(
                    timestamp=datetime.utcnow() - timedelta(hours=(i % 24)),
                    camera_frames=[f"gs://fleet-raw/cam_{i}.jpg"],
                    lidar_pointclouds=[f"gs://fleet-raw/lidar_{i}.pcd"],
                    gps_data={"lat": 37.7749 + (i % 100) * 0.001, "lon": -122.4194},
                ),
                # Fleet data has consent verified
                consent_verified=True,
                privacy_scrubbed=False,  # Will be scrubbed later
            )

            # Simulate safety scoring (fleet data tends to be higher quality)
            scenario.safety_score = 50 + (i % 40)
            scenario.complexity_score = 60 + (i % 35)

            scenarios.append(scenario)

        return scenarios

    def _random_weather(self, seed: int) -> WeatherCondition:
        """Generate deterministic weather based on seed"""
        options = [
            WeatherCondition.CLEAR,
            WeatherCondition.RAIN,
            WeatherCondition.FOG,
        ]
        return options[seed % len(options)]

    def _random_time_of_day(self, seed: int) -> TimeOfDay:
        """Generate deterministic time of day based on seed"""
        options = [TimeOfDay.DAY, TimeOfDay.NIGHT, TimeOfDay.DAWN, TimeOfDay.DUSK]
        return options[seed % len(options)]


if __name__ == "__main__":

    async def main():
        collector = FleetTelemetryCollector()
        scenarios = await collector.collect_daily_scenarios()
        print(f"Total: {len(scenarios)}")
        print(f"Sample: {scenarios[0].dict()}")

    asyncio.run(main())
