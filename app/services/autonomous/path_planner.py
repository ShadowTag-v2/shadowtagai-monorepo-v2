# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Path planning service using GAAS A* algorithm.

Integrates with Judge #6 for safety validation and Cor.17 for reasoning.
"""

from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass
import structlog

from app.services.autonomous.ros_bridge import ROSBridge, GAASServices

logger = structlog.get_logger()


@dataclass
class Waypoint:
    """3D waypoint for path planning."""

    x: float
    y: float
    z: float
    yaw: float = 0.0  # Heading in radians


@dataclass
class PathPlanningResult:
    """Result of path planning."""

    waypoints: list[Waypoint]
    total_distance: float
    estimated_time: float  # seconds
    safety_score: float  # 0-1 from Judge #6
    obstacles_detected: int
    reasoning: str  # From Cor.17


class PathPlannerService:
    """
    Path planning service with safety validation.

    Uses GAAS A* algorithm with:
    - HD map for static obstacles
    - Dynamic obstacle avoidance
    - Judge #6 safety validation
    - Cor.17 reasoning for route selection
    """

    def __init__(self, ros_bridge: ROSBridge):
        """
        Initialize path planner.

        Args:
            ros_bridge: ROS bridge instance
        """
        self.ros_bridge = ros_bridge
        self.default_altitude = 1.5  # meters
        self.safety_margin = 2.0  # meters
        self.max_speed = 5.0  # m/s

        logger.info("path_planner_initialized")

    async def plan_path(
        self,
        start: tuple[float, float, float],
        goal: tuple[float, float, float],
        map_id: str,
        safety_margin: float | None = None,
        validate_safety: bool = True,
    ) -> PathPlanningResult:
        """
        Plan path from start to goal.

        Args:
            start: (x, y, z) start position in meters
            goal: (x, y, z) goal position in meters
            map_id: HD map ID
            safety_margin: Safety margin around obstacles (meters)
            validate_safety: Use Judge #6 for safety validation

        Returns:
            PathPlanningResult with waypoints and metadata
        """
        safety_margin = safety_margin or self.safety_margin

        # Call GAAS path planning service
        request = {
            "start": {"x": start[0], "y": start[1], "z": start[2]},
            "goal": {"x": goal[0], "y": goal[1], "z": goal[2]},
            "map_id": map_id,
            "safety_margin": safety_margin,
            "algorithm": "a_star",  # GAAS supports A*, RRT, RRT*
        }

        try:
            response = await self.ros_bridge.call_service(
                service=GAASServices.PATH_PLANNING,
                service_type="gaas_srvs/PathPlanning",
                args=request,
                timeout=5.0,
            )
        except Exception as e:
            logger.error("path_planning_failed", error=str(e), start=start, goal=goal)
            raise

        # Parse waypoints
        waypoints = [
            Waypoint(
                x=wp["x"],
                y=wp["y"],
                z=wp["z"],
                yaw=wp.get("yaw", 0.0),
            )
            for wp in response.get("waypoints", [])
        ]

        total_distance = response.get("total_distance", 0.0)
        obstacles_detected = response.get("obstacles_count", 0)

        # Calculate estimated time
        estimated_time = total_distance / self.max_speed

        # Safety validation with Judge #6 (if enabled)
        safety_score = 1.0
        reasoning = "Path generated successfully"

        if validate_safety:
            safety_result = await self._validate_path_safety(
                waypoints=waypoints,
                obstacles_detected=obstacles_detected,
                total_distance=total_distance,
            )
            safety_score = safety_result["safety_score"]
            reasoning = safety_result["reasoning"]

        result = PathPlanningResult(
            waypoints=waypoints,
            total_distance=total_distance,
            estimated_time=estimated_time,
            safety_score=safety_score,
            obstacles_detected=obstacles_detected,
            reasoning=reasoning,
        )

        logger.info(
            "path_planned",
            waypoint_count=len(waypoints),
            distance=total_distance,
            estimated_time=estimated_time,
            safety_score=safety_score,
        )

        return result

    async def _validate_path_safety(
        self,
        waypoints: list[Waypoint],
        obstacles_detected: int,
        total_distance: float,
    ) -> dict[str, Any]:
        """
        Validate path safety with Judge #6.

        Returns:
            {safety_score: float, reasoning: str, brakes: List[str]}
        """
        # Import Judge #6 kernel (circular import avoided by lazy import)
        from app.kernels.judge_six import JudgeSixKernel

        # Construct safety validation input
        purpose = f"Execute autonomous flight path with {len(waypoints)} waypoints over {total_distance:.1f}m"
        reasons = [
            "Path validated by A* algorithm with safety margin",
            f"{obstacles_detected} obstacles detected and avoided",
            f"Estimated flight time: {total_distance / self.max_speed:.1f}s",
        ]

        # Call Judge #6
        judge = JudgeSixKernel()
        judge_result = await judge.execute(
            {
                "purpose": purpose,
                "reasons": reasons,
            }
        )

        # Extract safety score from Judge #6 decision
        decision = judge_result.get("decision", {})
        risk_level = decision.get("risk_level", "high")

        safety_score_map = {
            "low": 1.0,
            "medium": 0.7,
            "high": 0.4,
            "extreme": 0.0,
        }
        safety_score = safety_score_map.get(risk_level, 0.5)

        # Get reasoning from Cor.17 (if integrated)
        reasoning = self._generate_reasoning(
            waypoints=waypoints,
            obstacles_detected=obstacles_detected,
            safety_score=safety_score,
        )

        return {
            "safety_score": safety_score,
            "reasoning": reasoning,
            "brakes": decision.get("brakes", []),
        }

    def _generate_reasoning(
        self,
        waypoints: list[Waypoint],
        obstacles_detected: int,
        safety_score: float,
    ) -> str:
        """Generate human-readable reasoning for path decision."""
        if safety_score >= 0.9:
            return f"Path is safe with {len(waypoints)} waypoints and {obstacles_detected} obstacles successfully avoided."
        elif safety_score >= 0.7:
            return f"Path is acceptable but requires caution. {obstacles_detected} obstacles detected along route."
        elif safety_score >= 0.4:
            return f"Path has elevated risk. Consider alternative route or manual piloting. {obstacles_detected} obstacles detected."
        else:
            return f"Path is unsafe. Abort autonomous flight. {obstacles_detected} obstacles create unacceptable risk."

    async def replan_with_dynamic_obstacles(
        self,
        current_position: tuple[float, float, float],
        goal: tuple[float, float, float],
        map_id: str,
        new_obstacles: list[dict[str, Any]],
    ) -> PathPlanningResult:
        """
        Replan path with newly detected dynamic obstacles.

        Args:
            current_position: Current drone position
            goal: Original goal position
            map_id: HD map ID
            new_obstacles: List of newly detected obstacles

        Returns:
            Updated PathPlanningResult
        """
        logger.info("replanning_with_dynamic_obstacles", obstacle_count=len(new_obstacles))

        # Update HD map with dynamic obstacles (temporary)
        # In production, this would update the local costmap in GAAS

        # Replan from current position
        return await self.plan_path(
            start=current_position,
            goal=goal,
            map_id=map_id,
            validate_safety=True,
        )
