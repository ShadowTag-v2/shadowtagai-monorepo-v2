"""Cavalry Squadron Structure for minion
=============================================
Implements Cavalry Squadron organization with Air, Armor, Stryker, and Bradley elements.
Agents "ride" in virtual vehicles for companionship, safety, and redundancy.

Army Doctrine: FM 3-20.15, FM 3-98, ATP 3-20.15
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any

logger = logging.getLogger(__name__)


class VehicleType(StrEnum):
    """Vehicle types with crew/dismount capacities"""

    M1_ABRAMS = "m1_abrams"  # 4 crew, 0 dismount
    M2_BRADLEY = "m2_bradley"  # 3 crew, 6 dismount
    M1126_STRYKER = "m1126_stryker"  # 2 crew, 9 dismount
    AH64_APACHE = "ah64_apache"  # 2 crew, 0 dismount
    UH60_BLACKHAWK = "uh60_blackhawk"  # 4 crew, 10 dismount
    OH58_KIOWA = "oh58_kiowa"  # 2 crew, 0 dismount


class TroopType(StrEnum):
    """Troop types in Cavalry Squadron"""

    HHT = "hht"  # Headquarters & Headquarters Troop
    AIR_CAV = "air_cav"  # Air Cavalry Troop
    ALPHA_ARMOR = "alpha"  # Armor Troop (Abrams)
    BRAVO_STRYKER = "bravo"  # Stryker Troop
    CHARLIE_BRADLEY = "charlie"  # Bradley Troop
    CODEPMCS = "codepmcs"  # Code Quality & Remediation Troop


class JURATier(StrEnum):
    """JURA cost tiers for model assignment"""

    FREE = "free"
    FLASH = "flash"
    PRO = "pro"


# Vehicle specifications
VEHICLE_SPECS = {
    VehicleType.M1_ABRAMS: {"crew": 4, "dismount": 0, "jura_tier": JURATier.PRO},
    VehicleType.M2_BRADLEY: {"crew": 3, "dismount": 6, "jura_tier": JURATier.FLASH},
    VehicleType.M1126_STRYKER: {"crew": 2, "dismount": 9, "jura_tier": JURATier.FLASH},
    VehicleType.AH64_APACHE: {"crew": 2, "dismount": 0, "jura_tier": JURATier.PRO},
    VehicleType.UH60_BLACKHAWK: {"crew": 4, "dismount": 10, "jura_tier": JURATier.FLASH},
    VehicleType.OH58_KIOWA: {"crew": 2, "dismount": 0, "jura_tier": JURATier.FLASH},
}

# Model mapping by tier
TIER_MODELS = {
    JURATier.PRO: "gemini-3.1-flash-lite-preview-preview-06-05",
    JURATier.FLASH: "gemini-3.1-flash-lite-preview",
    JURATier.FREE: "gemini-3.1-flash-lite-preview",
}


@dataclass
class Agent:
    """Individual agent in the squadron"""

    agent_id: str
    role: str  # crew, dismount
    vehicle_id: str | None = None
    troop: TroopType | None = None
    model: str = "gemini-3.1-flash-lite-preview"
    status: str = "ready"  # ready, tasked, executing, complete, error

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "role": self.role,
            "vehicle_id": self.vehicle_id,
            "troop": self.troop.value if self.troop else None,
            "model": self.model,
            "status": self.status,
        }


@dataclass
class Vehicle:
    """Virtual vehicle containing agents.
    Agents never operate alone - always in vehicle crews.
    """

    vehicle_id: str
    vehicle_type: VehicleType
    callsign: str
    crew: list[Agent] = field(default_factory=list)
    dismounts: list[Agent] = field(default_factory=list)
    troop: TroopType | None = None
    status: str = "ready"

    @property
    def total_agents(self) -> int:
        return len(self.crew) + len(self.dismounts)

    @property
    def is_combat_effective(self) -> bool:
        """Vehicle needs minimum crew to operate"""
        specs = VEHICLE_SPECS[self.vehicle_type]
        min_crew = max(1, specs["crew"] // 2)  # At least half crew
        return len(self.crew) >= min_crew

    @property
    def jura_tier(self) -> JURATier:
        return VEHICLE_SPECS[self.vehicle_type]["jura_tier"]

    @property
    def model(self) -> str:
        return TIER_MODELS[self.jura_tier]

    def mount_agent(self, agent: Agent, as_crew: bool = True) -> bool:
        """Mount an agent in this vehicle"""
        specs = VEHICLE_SPECS[self.vehicle_type]

        if as_crew:
            if len(self.crew) < specs["crew"]:
                agent.vehicle_id = self.vehicle_id
                agent.role = "crew"
                agent.troop = self.troop
                agent.model = self.model
                self.crew.append(agent)
                return True
        elif len(self.dismounts) < specs["dismount"]:
            agent.vehicle_id = self.vehicle_id
            agent.role = "dismount"
            agent.troop = self.troop
            agent.model = self.model
            self.dismounts.append(agent)
            return True

        return False

    def get_all_agents(self) -> list[Agent]:
        """Get all agents in vehicle"""
        return self.crew + self.dismounts

    def to_dict(self) -> dict[str, Any]:
        return {
            "vehicle_id": self.vehicle_id,
            "vehicle_type": self.vehicle_type.value,
            "callsign": self.callsign,
            "crew_count": len(self.crew),
            "dismount_count": len(self.dismounts),
            "total_agents": self.total_agents,
            "troop": self.troop.value if self.troop else None,
            "status": self.status,
            "jura_tier": self.jura_tier.value,
            "model": self.model,
        }


@dataclass
class Platoon:
    """Platoon within a Troop"""

    platoon_id: str
    name: str
    vehicles: list[Vehicle] = field(default_factory=list)
    troop: TroopType | None = None

    @property
    def total_agents(self) -> int:
        return sum(v.total_agents for v in self.vehicles)

    def to_dict(self) -> dict[str, Any]:
        return {
            "platoon_id": self.platoon_id,
            "name": self.name,
            "vehicle_count": len(self.vehicles),
            "total_agents": self.total_agents,
            "troop": self.troop.value if self.troop else None,
        }


@dataclass
class Troop:
    """Troop (Company-level element) in Cavalry Squadron.
    Contains 3 platoons plus command element.
    """

    troop_id: str
    troop_type: TroopType
    name: str
    target_strength: int
    platoons: list[Platoon] = field(default_factory=list)
    model: str = "gemini-3.1-flash-lite-preview"
    commander: str | None = None

    @property
    def current_strength(self) -> int:
        return sum(p.total_agents for p in self.platoons)

    @property
    def strength_percent(self) -> float:
        if self.target_strength == 0:
            return 100.0
        return (self.current_strength / self.target_strength) * 100

    def get_all_vehicles(self) -> list[Vehicle]:
        """Get all vehicles in troop"""
        vehicles = []
        for platoon in self.platoons:
            vehicles.extend(platoon.vehicles)
        return vehicles

    def get_all_agents(self) -> list[Agent]:
        """Get all agents in troop"""
        agents = []
        for vehicle in self.get_all_vehicles():
            agents.extend(vehicle.get_all_agents())
        return agents

    def to_dict(self) -> dict[str, Any]:
        return {
            "troop_id": self.troop_id,
            "troop_type": self.troop_type.value,
            "name": self.name,
            "current_strength": self.current_strength,
            "target_strength": self.target_strength,
            "strength_percent": self.strength_percent,
            "platoon_count": len(self.platoons),
            "model": self.model,
            "commander": self.commander,
        }


class CavalrySquadron:
    """Cavalry Squadron "minion" - 600 agents

    Structure:
    - HHT (90 agents): Headquarters & Headquarters Troop
    - AIR CAV (120 agents): Aerial Scouts
    - ALPHA (130 agents): Armor Troop
    - BRAVO (130 agents): Stryker Troop
    - CHARLIE (130 agents): Bradley Troop

    Total: 600 agents
    """

    SQUADRON_STRUCTURE = {
        TroopType.HHT: {
            "name": "HHT - Headquarters & Headquarters Troop",
            "target_strength": 90,
            "model": "gemini-3.1-flash-lite-preview-preview-06-05",
            "commander": "Judge #6",
            "platoons": [
                ("S-1 Personnel", 12),
                ("S-2 Intel", 15),
                ("S-3 Operations", 15),
                ("S-4 Logistics", 12),
                ("S-6 Comms", 12),
                ("FSE Fire Support", 10),
                ("Scout PLT", 12),
                ("Command Element", 2),  # CDR + XO
            ],
            "vehicle_type": VehicleType.M1126_STRYKER,
        },
        TroopType.AIR_CAV: {
            "name": "AIR CAV - Aerial Scouts",
            "target_strength": 120,
            "model": "gemini-3.1-flash-lite-preview-preview-06-05",
            "commander": "Apache Lead",
            "platoons": [
                ("Attack Helo PLT", 40),
                ("Scout/Obs PLT", 40),
                ("Lift PLT", 40),
            ],
            "vehicle_type": VehicleType.AH64_APACHE,
        },
        TroopType.ALPHA_ARMOR: {
            "name": "ALPHA - Armor Troop",
            "target_strength": 130,
            "model": "gemini-3.1-flash-lite-preview",
            "commander": "Armor Lead",
            "platoons": [
                ("Tank PLT", 43),
                ("Scout PLT", 43),
                ("Mortar Section", 44),
            ],
            "vehicle_type": VehicleType.M1_ABRAMS,
        },
        TroopType.BRAVO_STRYKER: {
            "name": "BRAVO - Stryker Troop",
            "target_strength": 130,
            "model": "gemini-3.1-flash-lite-preview",
            "commander": "Stryker Lead",
            "platoons": [
                ("Scout PLT", 43),
                ("Rifle PLT", 43),
                ("MGS Section", 44),
            ],
            "vehicle_type": VehicleType.M1126_STRYKER,
        },
        TroopType.CHARLIE_BRADLEY: {
            "name": "CHARLIE - Bradley Troop",
            "target_strength": 130,
            "model": "gemini-3.1-flash-lite-preview",
            "commander": "Bradley Lead",
            "platoons": [
                ("Bradley PLT", 43),
                ("Dismount PLT", 43),
                ("TOW Section", 44),
            ],
            "vehicle_type": VehicleType.M2_BRADLEY,
        },
        TroopType.CODEPMCS: {
            "name": "CODEPMCS - Code Quality & Remediation",
            "target_strength": 50,
            "model": "gemini-3.1-flash-lite-preview-preview-06-05",
            "commander": "CodePMCS Lead",
            "platoons": [
                ("Scanner PLT", 20),
                ("Remediator PLT", 20),
                ("PR Generator PLT", 10),
            ],
            "vehicle_type": VehicleType.M1126_STRYKER,
        },
    }

    def __init__(self):
        self.troops: dict[TroopType, Troop] = {}
        self.all_agents: dict[str, Agent] = {}
        self.all_vehicles: dict[str, Vehicle] = {}
        self._agent_counter = 0
        self._vehicle_counter = 0
        self.created_at = datetime.utcnow()

    def initialize(self) -> "CavalrySquadron":
        """Initialize full squadron with 600 agents"""
        logger.info("Initializing Cavalry Squadron minion...")

        for troop_type, config in self.SQUADRON_STRUCTURE.items():
            troop = self._create_troop(troop_type, config)
            self.troops[troop_type] = troop
            logger.info(f"  {troop.name}: {troop.current_strength} agents")

        total = sum(t.current_strength for t in self.troops.values())
        logger.info(f"Squadron initialized: {total} agents in {len(self.troops)} troops")

        return self

    def _create_troop(self, troop_type: TroopType, config: dict[str, Any]) -> Troop:
        """Create a troop with platoons and vehicles"""
        troop = Troop(
            troop_id=f"TROOP-{troop_type.value.upper()}",
            troop_type=troop_type,
            name=config["name"],
            target_strength=config["target_strength"],
            model=config["model"],
            commander=config["commander"],
        )

        vehicle_type = config["vehicle_type"]

        for platoon_name, platoon_strength in config["platoons"]:
            platoon = self._create_platoon(
                troop_type,
                platoon_name,
                platoon_strength,
                vehicle_type,
            )
            platoon.troop = troop_type
            troop.platoons.append(platoon)

        return troop

    def _create_platoon(
        self,
        troop_type: TroopType,
        name: str,
        strength: int,
        vehicle_type: VehicleType,
    ) -> Platoon:
        """Create a platoon with vehicles and agents"""
        platoon = Platoon(
            platoon_id=f"PLT-{troop_type.value.upper()}-{name.replace(' ', '_').upper()[:10]}",
            name=name,
            troop=troop_type,
        )

        specs = VEHICLE_SPECS[vehicle_type]
        agents_per_vehicle = specs["crew"] + specs["dismount"]

        # Calculate vehicles needed
        vehicles_needed = (strength + agents_per_vehicle - 1) // agents_per_vehicle
        agents_remaining = strength

        for v_idx in range(vehicles_needed):
            vehicle = self._create_vehicle(troop_type, vehicle_type, v_idx)
            vehicle.troop = troop_type

            # Fill crew first
            for _ in range(min(specs["crew"], agents_remaining)):
                agent = self._create_agent(troop_type)
                if vehicle.mount_agent(agent, as_crew=True):
                    agents_remaining -= 1
                    self.all_agents[agent.agent_id] = agent

            # Then dismounts
            for _ in range(min(specs["dismount"], agents_remaining)):
                agent = self._create_agent(troop_type)
                if vehicle.mount_agent(agent, as_crew=False):
                    agents_remaining -= 1
                    self.all_agents[agent.agent_id] = agent

            platoon.vehicles.append(vehicle)
            self.all_vehicles[vehicle.vehicle_id] = vehicle

        return platoon

    def _create_vehicle(
        self,
        troop_type: TroopType,
        vehicle_type: VehicleType,
        index: int,
    ) -> Vehicle:
        """Create a new vehicle"""
        self._vehicle_counter += 1

        callsign_prefixes = {
            TroopType.HHT: "VIKING",
            TroopType.AIR_CAV: "APACHE",
            TroopType.ALPHA_ARMOR: "IRON",
            TroopType.BRAVO_STRYKER: "GHOST",
            TroopType.CHARLIE_BRADLEY: "THUNDER",
        }

        prefix = callsign_prefixes.get(troop_type, "UNIT")

        return Vehicle(
            vehicle_id=f"VEH-{self._vehicle_counter:04d}",
            vehicle_type=vehicle_type,
            callsign=f"{prefix}-{index + 1:02d}",
            troop=troop_type,
        )

    def _create_agent(self, troop_type: TroopType) -> Agent:
        """Create a new agent"""
        self._agent_counter += 1
        return Agent(
            agent_id=f"AGENT-{self._agent_counter:04d}",
            role="pending",
            troop=troop_type,
        )

    def get_troop(self, troop_type: TroopType) -> Troop | None:
        """Get troop by type"""
        return self.troops.get(troop_type)

    def get_section(self, section_name: str) -> list[Agent]:
        """Get agents from a staff section (for TLP)"""
        section_mapping = {
            "S-1": ("HHT", "S-1 Personnel"),
            "S-2": ("HHT", "S-2 Intel"),
            "S-3": ("HHT", "S-3 Operations"),
            "S-4": ("HHT", "S-4 Logistics"),
            "S-6": ("HHT", "S-6 Comms"),
            "FSE": ("HHT", "FSE Fire Support"),
            "CDR": ("HHT", "Command Element"),
            "XO": ("HHT", "Command Element"),
        }

        if section_name not in section_mapping:
            return []

        troop_name, platoon_name = section_mapping[section_name]
        troop_type = TroopType.HHT if troop_name == "HHT" else None

        if not troop_type:
            return []

        troop = self.troops.get(troop_type)
        if not troop:
            return []

        for platoon in troop.platoons:
            if platoon.name == platoon_name:
                agents = []
                for vehicle in platoon.vehicles:
                    agents.extend(vehicle.get_all_agents())
                return agents

        return []

    def get_available_agents(
        self,
        troop_type: TroopType | None = None,
        count: int = 1,
    ) -> list[Agent]:
        """Get available agents for tasking"""
        available = []

        troops_to_check = [self.troops[troop_type]] if troop_type else list(self.troops.values())

        for troop in troops_to_check:
            for agent in troop.get_all_agents():
                if agent.status == "ready":
                    available.append(agent)
                    if len(available) >= count:
                        return available

        return available

    def dispatch_mission(
        self,
        task: str,
        troop_assignments: dict[TroopType, list[str]],
    ) -> dict[str, Any]:
        """Dispatch mission to troops per OPORD assignments.

        Args:
            task: Mission task
            troop_assignments: Tasks per troop from OPORD

        Returns:
            Dispatch result with agents assigned

        """
        dispatched = {}

        for troop_type, tasks in troop_assignments.items():
            troop = self.troops.get(troop_type)
            if not troop:
                continue

            # Get available agents from this troop
            agents = [a for a in troop.get_all_agents() if a.status == "ready"]

            # Distribute tasks across agents
            agents_per_task = max(1, len(agents) // len(tasks)) if tasks else 0

            dispatched[troop_type.value] = {
                "troop": troop.name,
                "agents_assigned": len(agents),
                "tasks": tasks,
                "agents_per_task": agents_per_task,
                "model": troop.model,
            }

            # Mark agents as tasked
            for agent in agents:
                agent.status = "tasked"

        return {
            "mission": task,
            "dispatched_at": datetime.utcnow().isoformat(),
            "troops": dispatched,
            "total_agents": sum(d["agents_assigned"] for d in dispatched.values()),
        }

    def get_status(self) -> dict[str, Any]:
        """Get squadron status"""
        troop_status = {}
        total_agents = 0
        total_ready = 0

        for troop_type, troop in self.troops.items():
            agents = troop.get_all_agents()
            ready = sum(1 for a in agents if a.status == "ready")
            total_agents += len(agents)
            total_ready += ready

            troop_status[troop_type.value] = {
                "name": troop.name,
                "strength": len(agents),
                "ready": ready,
                "strength_percent": troop.strength_percent,
                "model": troop.model,
            }

        return {
            "squadron": "minion",
            "total_agents": total_agents,
            "ready_agents": total_ready,
            "readiness_percent": (total_ready / total_agents * 100) if total_agents > 0 else 0,
            "troops": troop_status,
            "vehicle_count": len(self.all_vehicles),
            "uptime_seconds": (datetime.utcnow() - self.created_at).total_seconds(),
        }


# Singleton squadron instance
_squadron_instance: CavalrySquadron | None = None


def get_squadron() -> CavalrySquadron:
    """Get or create the squadron singleton"""
    global _squadron_instance
    if _squadron_instance is None:
        _squadron_instance = CavalrySquadron().initialize()
    return _squadron_instance


def reset_squadron() -> CavalrySquadron:
    """Reset and reinitialize the squadron"""
    global _squadron_instance
    _squadron_instance = CavalrySquadron().initialize()
    return _squadron_instance
