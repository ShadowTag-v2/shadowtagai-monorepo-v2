"""GAAS Integration for AiU+ShadowTag-v4 Platform
Generalized Autonomy Aviation System

Provides:
- Autonomous flight control (PX4 offboard)
- Lidar-based perception and mapping
- Path planning with obstacle avoidance
- HD-map relocalization
- Tower node deployment

All operations validated through AiUCRM pre-execution compliance
with aviation-grade safety requirements (FAA DO-178C).
"""

from .control.autonomous_flight import AutonomousFlightService
from .control.tower_deployment import TowerDeploymentDrone
from .perception.infrastructure_mapping import InfrastructureMappingService

__version__ = "1.0.0"
__all__ = [
    "AutonomousFlightService",
    "InfrastructureMappingService",
    "TowerDeploymentDrone",
]
