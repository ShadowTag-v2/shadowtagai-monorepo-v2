# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""SpaceX Starlink Client Stub
Simulates interacting with a Starlink Flat High Performance Dish.
"""

import logging
import random
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class StarlinkTelemetry:
    snr: float
    latency_ms: float
    uplink_throughput_mbps: float
    downlink_throughput_mbps: float
    obstruction_pct: float


class StarlinkClient:
    def __init__(self, dish_id: str):
        self.dish_id = dish_id
        self.is_connected = False
        logger.info(f"Initialized StarlinkClient for Dish {dish_id}")

    def connect(self):
        """Establish connection to the dish management interface."""
        self.is_connected = True
        logger.info(f"Connected to Starlink Dish {self.dish_id}")

    def get_telemetry(self) -> StarlinkTelemetry:
        """Fetch real-time RF telemetry."""
        if not self.is_connected:
            raise ConnectionError("Dish not connected")

        # Simulation
        return StarlinkTelemetry(
            snr=random.uniform(9.0, 12.0),
            latency_ms=random.uniform(25.0, 45.0),
            uplink_throughput_mbps=random.uniform(10.0, 25.0),
            downlink_throughput_mbps=random.uniform(100.0, 250.0),
            obstruction_pct=0.0,
        )
