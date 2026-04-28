# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""FM 3-0: Operations (Warfighting Functions)
==========================================

Source: FM 3-0 (October 2022)

Six Warfighting Functions:
1. Command and Control (C2)
2. Movement and Maneuver
3. Intelligence
4. Fires
5. Sustainment
6. Protection

These are the physical means that tactical commanders use to
execute operations and accomplish missions.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class WarfightingFunctionType(Enum):
    """FM 3-0 Chapter 3: Warfighting Functions"""

    COMMAND_CONTROL = "command_control"
    MOVEMENT_MANEUVER = "movement_maneuver"
    INTELLIGENCE = "intelligence"
    FIRES = "fires"
    SUSTAINMENT = "sustainment"
    PROTECTION = "protection"


class OperationType(Enum):
    """FM 3-0 Chapter 1: Types of Operations"""

    OFFENSIVE = "offensive"
    DEFENSIVE = "defensive"
    STABILITY = "stability"
    DEFENSE_SUPPORT = "defense_support_civil_authorities"


@dataclass
class WarfightingFunction(ABC):
    """Base class for all Warfighting Functions.

    Each function represents a group of tasks and systems
    united by a common purpose.
    """

    name: str
    function_type: WarfightingFunctionType
    tasks: list[str] = field(default_factory=list)
    systems: list[str] = field(default_factory=list)
    status: str = "ready"

    @abstractmethod
    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        """Execute the warfighting function"""

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "type": self.function_type.value,
            "tasks": self.tasks,
            "systems": self.systems,
            "status": self.status,
            "fm_reference": "FM 3-0",
        }


@dataclass
class CommandControl(WarfightingFunction):
    """FM 3-0: Command and Control Warfighting Function

    The related tasks and systems that enable commanders to
    synchronize and converge all elements of combat power.

    AI Implementation: Orchestrator + Command Section
    """

    def __post_init__(self):
        self.name = "Command and Control"
        self.function_type = WarfightingFunctionType.COMMAND_CONTROL
        self.tasks = [
            "Command forces",
            "Control operations",
            "Drive the operations process",
            "Establish command relationships",
            "Synchronize warfighting functions",
        ]
        self.systems = [
            "Command posts",
            "Communications systems",
            "Information systems",
            "Liaison elements",
        ]

    # Mission Command principles (FM 6-0)
    commander_intent: str = ""
    mission_orders: list[dict[str, Any]] = field(default_factory=list)
    disciplined_initiative_enabled: bool = True

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        """Execute C2 function.

        Provides authority and direction to subordinate elements.
        """
        return {
            "function": "command_control",
            "commander_intent": self.commander_intent,
            "orders_issued": len(self.mission_orders),
            "initiative_enabled": self.disciplined_initiative_enabled,
            "synchronization": "active",
            "status": self.status,
        }

    def issue_order(self, order: dict[str, Any]):
        """Issue a mission order to subordinate"""
        order["issued_at"] = datetime.utcnow().isoformat()
        self.mission_orders.append(order)

    def set_intent(self, intent: str):
        """Set commander's intent"""
        self.commander_intent = intent


@dataclass
class Intelligence(WarfightingFunction):
    """FM 3-0: Intelligence Warfighting Function

    The related tasks and systems that facilitate understanding
    of the enemy, terrain, weather, and civil considerations.

    AI Implementation: S-2 Section + RECON Troops
    """

    def __post_init__(self):
        self.name = "Intelligence"
        self.function_type = WarfightingFunctionType.INTELLIGENCE
        self.tasks = [
            "Support to situational understanding",
            "Support to targeting and information superiority",
            "Conduct intelligence operations",
            "Perform intelligence analysis",
        ]
        self.systems = [
            "Collection assets",
            "Processing systems",
            "Dissemination networks",
            "Analysis tools",
        ]

    # IPB components (ATP 2-01.3)
    terrain_analysis: dict[str, Any] = field(default_factory=dict)
    weather_analysis: dict[str, Any] = field(default_factory=dict)
    threat_evaluation: dict[str, Any] = field(default_factory=dict)
    civil_considerations: dict[str, Any] = field(default_factory=dict)

    # Priority Intelligence Requirements
    pir: list[str] = field(default_factory=list)

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        """Execute Intelligence function.

        Provides understanding of operational environment.
        """
        return {
            "function": "intelligence",
            "ipb_complete": all(
                [self.terrain_analysis, self.weather_analysis, self.threat_evaluation],
            ),
            "pir_count": len(self.pir),
            "threat_level": self._assess_threat_level(),
            "status": self.status,
        }

    def _assess_threat_level(self) -> str:
        """Assess current threat level"""
        if self.threat_evaluation.get("high_risk"):
            return "HIGH"
        if self.threat_evaluation.get("medium_risk"):
            return "MEDIUM"
        return "LOW"

    async def conduct_ipb(self, context: dict[str, Any]) -> dict[str, Any]:
        """Conduct Intelligence Preparation of the Battlefield.

        ATP 2-01.3 four-step IPB process:
        1. Define the operational environment
        2. Describe environmental effects
        3. Evaluate the threat
        4. Determine threat COAs
        """
        self.terrain_analysis = {
            "key_terrain": context.get("key_files", []),
            "obstacles": context.get("blockers", []),
            "avenues": context.get("approaches", []),
        }
        self.weather_analysis = {"conditions": context.get("environment", "stable")}
        self.threat_evaluation = {
            "threat_type": context.get("risk_type", "unknown"),
            "capabilities": context.get("threat_capabilities", []),
        }

        return {
            "terrain": self.terrain_analysis,
            "weather": self.weather_analysis,
            "threat": self.threat_evaluation,
            "civil": self.civil_considerations,
        }


@dataclass
class Fires(WarfightingFunction):
    """FM 3-0: Fires Warfighting Function

    The related tasks and systems that create and converge
    effects in all domains against the adversary.

    AI Implementation: FSE Section + Mortar Section
    """

    def __post_init__(self):
        self.name = "Fires"
        self.function_type = WarfightingFunctionType.FIRES
        self.tasks = [
            "Deliver fires",
            "Integrate fires with maneuver",
            "Execute targeting",
            "Coordinate fire support",
        ]
        self.systems = [
            "Field artillery",
            "Air support",
            "Naval surface fire",
            "Mortars",
        ]

    # Targeting data
    targets: list[dict[str, Any]] = field(default_factory=list)
    fire_missions: list[dict[str, Any]] = field(default_factory=list)

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        """Execute Fires function.

        Delivers effects against designated targets.
        """
        return {
            "function": "fires",
            "targets_acquired": len(self.targets),
            "missions_executed": len(self.fire_missions),
            "status": self.status,
        }

    def acquire_target(self, target: dict[str, Any]):
        """Add target to engagement list"""
        target["acquired_at"] = datetime.utcnow().isoformat()
        self.targets.append(target)

    async def execute_fire_mission(self, target_id: str) -> dict[str, Any]:
        """Execute fire mission against target"""
        mission = {
            "target_id": target_id,
            "executed_at": datetime.utcnow().isoformat(),
            "result": "effects_achieved",
        }
        self.fire_missions.append(mission)
        return mission


@dataclass
class Movement(WarfightingFunction):
    """FM 3-0: Movement and Maneuver Warfighting Function

    The related tasks and systems that move and employ forces
    to achieve a position of relative advantage.

    AI Implementation: GKE Autopilot + Agent Routing
    """

    def __post_init__(self):
        self.name = "Movement and Maneuver"
        self.function_type = WarfightingFunctionType.MOVEMENT_MANEUVER
        self.tasks = ["Deploy forces", "Move forces", "Maneuver", "Employ direct fire"]
        self.systems = ["Ground maneuver forces", "Aviation assets", "Movement control"]

    # Movement data
    routes: list[dict[str, Any]] = field(default_factory=list)
    positions: dict[str, str] = field(default_factory=dict)

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        """Execute Movement and Maneuver function.

        Positions forces for advantage.
        """
        return {
            "function": "movement_maneuver",
            "routes_established": len(self.routes),
            "units_positioned": len(self.positions),
            "status": self.status,
        }

    def establish_route(self, route: dict[str, Any]):
        """Establish movement route"""
        self.routes.append(route)

    def update_position(self, unit_id: str, position: str):
        """Update unit position"""
        self.positions[unit_id] = position


@dataclass
class Sustainment(WarfightingFunction):
    """FM 3-0: Sustainment Warfighting Function

    The related tasks and systems that provide support and
    services to ensure freedom of action, extend operational reach.

    AI Implementation: S-4 Section + Token Budget Management
    """

    def __post_init__(self):
        self.name = "Sustainment"
        self.function_type = WarfightingFunctionType.SUSTAINMENT
        self.tasks = [
            "Provide logistics",
            "Provide personnel services",
            "Provide health service support",
            "Conduct financial management",
        ]
        self.systems = ["Supply systems", "Maintenance", "Transportation", "Medical"]

    # Resource tracking
    token_budget: int = 0
    tokens_used: int = 0
    resources: dict[str, int] = field(default_factory=dict)

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        """Execute Sustainment function.

        Maintains combat power through resource management.
        """
        return {
            "function": "sustainment",
            "token_budget": self.token_budget,
            "tokens_used": self.tokens_used,
            "tokens_remaining": self.token_budget - self.tokens_used,
            "utilization": self.tokens_used / self.token_budget if self.token_budget > 0 else 0,
            "status": self.status,
        }

    def allocate_budget(self, tokens: int):
        """Allocate token budget"""
        self.token_budget = tokens

    def consume_tokens(self, amount: int) -> bool:
        """Consume tokens, return False if insufficient"""
        if self.tokens_used + amount <= self.token_budget:
            self.tokens_used += amount
            return True
        return False

    def get_utilization(self) -> float:
        """Get current utilization rate"""
        if self.token_budget == 0:
            return 0.0
        return self.tokens_used / self.token_budget


@dataclass
class Protection(WarfightingFunction):
    """FM 3-0: Protection Warfighting Function

    The related tasks and systems that preserve the force
    so the commander can apply maximum combat power.

    AI Implementation: MFRC (Screen/Guard/Cover) + Judge 6
    """

    def __post_init__(self):
        self.name = "Protection"
        self.function_type = WarfightingFunctionType.PROTECTION
        self.tasks = [
            "Conduct operational area security",
            "Employ safety techniques",
            "Implement OPSEC",
            "Provide force health protection",
        ]
        self.systems = ["Security forces", "Air defense", "Chemical defense", "EOD"]

    # Security posture
    security_level: str = "SCREEN"  # SCREEN, GUARD, COVER
    threats_detected: list[dict[str, Any]] = field(default_factory=list)
    threats_neutralized: int = 0

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        """Execute Protection function.

        Preserves force effectiveness.
        """
        return {
            "function": "protection",
            "security_level": self.security_level,
            "threats_detected": len(self.threats_detected),
            "threats_neutralized": self.threats_neutralized,
            "status": self.status,
        }

    def set_security_posture(self, level: str):
        """Set security posture per ATP 3-20.96:
        - SCREEN: Early warning, minimal engagement (50%)
        - GUARD: Fight for time, deny observation (75%)
        - COVER: Battle positions, self-contained (90%)
        """
        if level in ["SCREEN", "GUARD", "COVER"]:
            self.security_level = level

    def detect_threat(self, threat: dict[str, Any]):
        """Log detected threat"""
        threat["detected_at"] = datetime.utcnow().isoformat()
        self.threats_detected.append(threat)

    def neutralize_threat(self, threat_id: str) -> bool:
        """Neutralize a detected threat"""
        for threat in self.threats_detected:
            if threat.get("id") == threat_id:
                threat["neutralized"] = True
                self.threats_neutralized += 1
                return True
        return False

    def get_consensus_threshold(self) -> float:
        """Get consensus threshold based on security posture"""
        thresholds = {"SCREEN": 0.50, "GUARD": 0.75, "COVER": 0.90}
        return thresholds.get(self.security_level, 0.60)


def create_warfighting_functions() -> dict[WarfightingFunctionType, WarfightingFunction]:
    """Factory function to create all six warfighting functions.

    Returns dictionary mapping function type to instance.
    """
    return {
        WarfightingFunctionType.COMMAND_CONTROL: CommandControl(
            name="Command and Control",
            function_type=WarfightingFunctionType.COMMAND_CONTROL,
        ),
        WarfightingFunctionType.INTELLIGENCE: Intelligence(
            name="Intelligence",
            function_type=WarfightingFunctionType.INTELLIGENCE,
        ),
        WarfightingFunctionType.FIRES: Fires(
            name="Fires",
            function_type=WarfightingFunctionType.FIRES,
        ),
        WarfightingFunctionType.MOVEMENT_MANEUVER: Movement(
            name="Movement and Maneuver",
            function_type=WarfightingFunctionType.MOVEMENT_MANEUVER,
        ),
        WarfightingFunctionType.SUSTAINMENT: Sustainment(
            name="Sustainment",
            function_type=WarfightingFunctionType.SUSTAINMENT,
        ),
        WarfightingFunctionType.PROTECTION: Protection(
            name="Protection",
            function_type=WarfightingFunctionType.PROTECTION,
        ),
    }
