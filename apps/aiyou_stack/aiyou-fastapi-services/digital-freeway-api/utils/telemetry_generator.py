"""Mock Telemetry Generator for Digital Freeway API
Simulates 10K vehicles with realistic movement patterns.
"""

import asyncio
import math
import random
from dataclasses import dataclass
from datetime import datetime

import httpx


@dataclass
class SimulatedVehicle:
    """A simulated vehicle with physics-based movement."""

    id: str
    lat: float
    lon: float
    speed: float  # m/s
    heading: float  # degrees
    acceleration: float = 0.0
    lane: int = 1

    def update(self, dt: float = 0.1):
        """Update vehicle position based on physics."""
        # Apply acceleration
        self.speed = max(0, min(40, self.speed + self.acceleration * dt))

        # Random heading jitter (lane keeping)
        self.heading += random.gauss(0, 0.5)
        self.heading = self.heading % 360

        # Convert heading to radians
        heading_rad = math.radians(self.heading)

        # Update position (simplified, assumes flat earth for small distances)
        # 1 degree lat ≈ 111km, 1 degree lon ≈ 111km * cos(lat)
        meters_per_degree = 111000

        dx = self.speed * dt * math.sin(heading_rad)  # east-west
        dy = self.speed * dt * math.cos(heading_rad)  # north-south

        self.lon += dx / (meters_per_degree * math.cos(math.radians(self.lat)))
        self.lat += dy / meters_per_degree

        # Random acceleration changes (traffic behavior)
        if random.random() < 0.1:
            self.acceleration = random.gauss(0, 1)

    def to_telemetry(self) -> dict:
        return {
            "vehicle_id": self.id,
            "timestamp": datetime.utcnow().isoformat(),
            "latitude": self.lat,
            "longitude": self.lon,
            "speed_mps": self.speed,
            "heading": self.heading,
            "acceleration": self.acceleration,
            "lane": self.lane,
        }


class TelemetryGenerator:
    """Generate mock telemetry for N vehicles.

    Usage:
        generator = TelemetryGenerator(num_vehicles=10000)
        await generator.run(api_url="http://localhost:8080")
    """

    def __init__(
        self,
        num_vehicles: int = 10000,
        center_lat: float = 37.7749,  # San Francisco
        center_lon: float = -122.4194,
        spread_km: float = 10.0,
    ):
        self.vehicles: list[SimulatedVehicle] = []

        # Initialize vehicles in a grid pattern
        spread_deg = spread_km / 111.0  # approximate km to degrees

        for i in range(num_vehicles):
            vehicle = SimulatedVehicle(
                id=f"v_{i:06d}",
                lat=center_lat + random.uniform(-spread_deg, spread_deg),
                lon=center_lon + random.uniform(-spread_deg, spread_deg),
                speed=random.uniform(10, 30),  # 22-67 mph
                heading=random.uniform(0, 360),
                lane=random.randint(1, 4),
            )
            self.vehicles.append(vehicle)

        print(f"Initialized {num_vehicles} simulated vehicles")

    async def run(
        self,
        api_url: str = "http://localhost:8080",
        update_hz: float = 10.0,
        duration_seconds: float | None = None,
        batch_size: int = 100,
    ):
        """Run the telemetry generator.

        Args:
            api_url: Digital Freeway API endpoint
            update_hz: Updates per second (10 = 100ms intervals)
            duration_seconds: How long to run (None = forever)
            batch_size: Vehicles to update per batch

        """
        dt = 1.0 / update_hz
        elapsed = 0.0
        requests_sent = 0

        async with httpx.AsyncClient(timeout=5.0) as client:
            print(f"Starting telemetry stream to {api_url}")

            while True:
                batch_start = asyncio.get_event_loop().time()

                # Update vehicle physics
                for vehicle in self.vehicles:
                    vehicle.update(dt)

                # Send batch of telemetry
                batch = random.sample(self.vehicles, min(batch_size, len(self.vehicles)))

                tasks = []
                for vehicle in batch:
                    task = client.post(f"{api_url}/telemetry", json=vehicle.to_telemetry())
                    tasks.append(task)

                try:
                    responses = await asyncio.gather(*tasks, return_exceptions=True)
                    successful = sum(
                        1
                        for r in responses
                        if not isinstance(r, Exception) and r.status_code == 200
                    )
                    requests_sent += successful
                except Exception as e:
                    print(f"Batch error: {e}")

                # Timing
                elapsed += dt
                if elapsed % 5 < dt:
                    print(
                        f"[{elapsed:.0f}s] Sent {requests_sent} requests, tracking {len(self.vehicles)} vehicles",
                    )

                if duration_seconds and elapsed >= duration_seconds:
                    break

                # Sleep to maintain update rate
                batch_time = asyncio.get_event_loop().time() - batch_start
                sleep_time = max(0, dt - batch_time)
                await asyncio.sleep(sleep_time)

        print(f"Generator stopped. Total requests: {requests_sent}")


async def main():
    """Run the telemetry generator."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate mock vehicle telemetry")
    parser.add_argument("--vehicles", type=int, default=1000, help="Number of vehicles")
    parser.add_argument("--url", default="http://localhost:8080", help="API URL")
    parser.add_argument("--hz", type=float, default=10.0, help="Updates per second")
    parser.add_argument("--duration", type=float, default=60.0, help="Duration in seconds")
    parser.add_argument("--batch", type=int, default=50, help="Batch size per update")

    args = parser.parse_args()

    generator = TelemetryGenerator(num_vehicles=args.vehicles)
    await generator.run(
        api_url=args.url,
        update_hz=args.hz,
        duration_seconds=args.duration,
        batch_size=args.batch,
    )


if __name__ == "__main__":
    asyncio.run(main())
