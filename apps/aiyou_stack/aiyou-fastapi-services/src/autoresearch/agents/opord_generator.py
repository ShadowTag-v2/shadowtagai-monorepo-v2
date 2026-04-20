"""OPORD Generator for minion Cavalry Squadron
===================================================
Implements 5-Paragraph Operations Order format for agent swarm coordination.
Integrates TLP (Troop Leading Procedures) with OODA loop for tactical agility.

Army Doctrine: FM 6-0, FM 5-0, ATP 5-19
"""

import hashlib
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any

logger = logging.getLogger(__name__)


class MissionType(StrEnum):
    """Mission types mapped to software engineering tasks"""

    ATTACK = "attack"  # New feature development
    DEFEND = "defend"  # Bug fixing, security patching
    RECONNAISSANCE = "recon"  # Research, analysis
    MOVEMENT = "movement"  # Refactoring, migration
    STABILITY = "stability"  # Maintenance, optimization


class OODAPhase(StrEnum):
    """Boyd's OODA Loop phases"""

    OBSERVE = "observe"
    ORIENT = "orient"
    DECIDE = "decide"
    ACT = "act"


@dataclass
class Situation:
    """Paragraph 1: SITUATION"""

    enemy: dict[str, Any] = field(default_factory=dict)  # Blockers, constraints
    friendly: dict[str, Any] = field(default_factory=dict)  # Resources available
    attachments: list[str] = field(default_factory=list)  # External dependencies
    detachments: list[str] = field(default_factory=list)  # Resources released


@dataclass
class Execution:
    """Paragraph 3: EXECUTION"""

    commander_intent: str = ""
    concept_of_operations: str = ""
    scheme_of_maneuver: str = ""
    tasks_to_subordinate_units: dict[str, list[str]] = field(default_factory=dict)
    coordinating_instructions: list[str] = field(default_factory=list)


@dataclass
class ServiceSupport:
    """Paragraph 4: SERVICE SUPPORT"""

    api_keys: dict[str, str] = field(default_factory=dict)
    compute_budget: float = 0.0
    token_limit: int = 0
    time_limit_seconds: int = 0
    fallback_resources: list[str] = field(default_factory=list)


@dataclass
class CommandAndSignal:
    """Paragraph 5: COMMAND AND SIGNAL"""

    command: dict[str, str] = field(default_factory=dict)  # Chain of command
    signal: dict[str, str] = field(default_factory=dict)  # Communication protocols
    succession_of_command: list[str] = field(default_factory=list)


@dataclass
class OPORD:
    """5-Paragraph Operations Order for Agent Swarm

    Based on FM 5-0 and FM 6-0 doctrine adapted for AI agents.
    Each paragraph maps to specific agent coordination needs.
    """

    # Metadata
    opord_id: str = ""
    dtg: str = ""  # Date-Time Group
    issuing_unit: str = "HHT/minion"

    # Para 1: SITUATION
    situation: Situation = field(default_factory=Situation)

    # Para 2: MISSION
    mission: str = ""  # Who, What, When, Where, Why (5 W's)

    # Para 3: EXECUTION
    execution: Execution = field(default_factory=Execution)

    # Para 4: SERVICE SUPPORT
    service_support: ServiceSupport = field(default_factory=ServiceSupport)

    # Para 5: COMMAND AND SIGNAL
    command_signal: CommandAndSignal = field(default_factory=CommandAndSignal)

    # Tracking
    status: str = "draft"  # draft, issued, executing, complete, cancelled
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
        """Serialize OPORD for transmission"""
        return {
            "opord_id": self.opord_id,
            "dtg": self.dtg,
            "issuing_unit": self.issuing_unit,
            "situation": {
                "enemy": self.situation.enemy,
                "friendly": self.situation.friendly,
                "attachments": self.situation.attachments,
                "detachments": self.situation.detachments,
            },
            "mission": self.mission,
            "execution": {
                "commander_intent": self.execution.commander_intent,
                "concept_of_operations": self.execution.concept_of_operations,
                "scheme_of_maneuver": self.execution.scheme_of_maneuver,
                "tasks": self.execution.tasks_to_subordinate_units,
                "coord_instructions": self.execution.coordinating_instructions,
            },
            "service_support": {
                "compute_budget": self.service_support.compute_budget,
                "token_limit": self.service_support.token_limit,
                "time_limit": self.service_support.time_limit_seconds,
            },
            "command_signal": {
                "command": self.command_signal.command,
                "signal": self.command_signal.signal,
            },
            "status": self.status,
        }


@dataclass
class FRAGO:
    """Fragmentary Order - updates to existing OPORD.
    Used for mid-mission adjustments without full replanning.
    """

    frago_id: str = ""
    parent_opord_id: str = ""
    changes: dict[str, Any] = field(default_factory=dict)
    effective_immediately: bool = True
    reason: str = ""
    issued_at: datetime = field(default_factory=datetime.utcnow)

    def apply_to(self, opord: OPORD) -> OPORD:
        """Apply FRAGO changes to existing OPORD"""
        for field_name, value in self.changes.items():
            if hasattr(opord, field_name):
                setattr(opord, field_name, value)
            elif hasattr(opord.execution, field_name):
                setattr(opord.execution, field_name, value)

        opord.status = "modified"
        return opord


class OPORDGenerator:
    """Generates OPORDs for minion Cavalry Squadron.
    Maps user tasks to military mission format.

    Staff Section Responsibilities:
    - S-2 (Intel): Classify mission, analyze threats
    - S-3 (Operations): Build OPORD, assign troops
    - S-4 (Logistics): Resource allocation
    """

    # Mission type keywords
    ATTACK_KEYWORDS = ["add", "create", "implement", "build", "new", "develop", "feature"]
    DEFEND_KEYWORDS = ["fix", "bug", "patch", "secure", "protect", "repair", "resolve"]
    RECON_KEYWORDS = ["research", "analyze", "find", "search", "investigate", "explore", "review"]
    MOVEMENT_KEYWORDS = ["refactor", "migrate", "move", "rename", "reorganize", "restructure"]

    def __init__(self, squadron_config: dict[str, Any] = None):
        self.squadron = squadron_config or {}
        self.hht = self.squadron.get("HHT", {})
        self._opord_counter = 0

    def generate(self, task: str, context: dict[str, Any] = None) -> OPORD:
        """Generate OPORD from user task.

        Args:
            task: User's task description
            context: Additional context (files, codebase state, etc.)

        Returns:
            Complete OPORD ready for issue

        """
        context = context or {}

        # S-2 Intel: Analyze task
        mission_type = self._classify_mission(task)

        # Generate OPORD ID
        opord_id = self._generate_opord_id(task)

        # S-3 Ops: Build OPORD
        opord = OPORD(
            opord_id=opord_id,
            dtg=datetime.utcnow().strftime("%d%H%MZ%b%Y").upper(),
            situation=self._build_situation(context),
            mission=self._build_mission(task, mission_type),
            execution=self._build_execution(task, mission_type, context),
            service_support=self._build_service_support(context),
            command_signal=self._build_command_signal(),
            status="issued",
        )

        logger.info(f"OPORD {opord_id} generated: {mission_type.value} mission")
        return opord

    def _classify_mission(self, task: str) -> MissionType:
        """S-2 classifies mission type from task description"""
        task_lower = task.lower()

        if any(kw in task_lower for kw in self.ATTACK_KEYWORDS):
            return MissionType.ATTACK
        if any(kw in task_lower for kw in self.DEFEND_KEYWORDS):
            return MissionType.DEFEND
        if any(kw in task_lower for kw in self.RECON_KEYWORDS):
            return MissionType.RECONNAISSANCE
        if any(kw in task_lower for kw in self.MOVEMENT_KEYWORDS):
            return MissionType.MOVEMENT
        return MissionType.STABILITY

    def _build_situation(self, context: dict[str, Any]) -> Situation:
        """Build Para 1: SITUATION"""
        return Situation(
            enemy={
                "blockers": context.get("blockers", []),
                "constraints": context.get("constraints", []),
                "rate_limits": context.get("rate_limits", {}),
            },
            friendly={
                "agents_available": context.get("agents_available", 600),
                "models": context.get(
                    "models", ["gemini-3.1-flash-lite-preview", "gemini-3.1-flash-lite-preview"]
                ),
                "existing_code": context.get("existing_code", []),
            },
            attachments=context.get("attachments", []),
            detachments=context.get("detachments", []),
        )

    def _build_mission(self, task: str, mission_type: MissionType) -> str:
        """Build Para 2: MISSION (5 W's)"""
        mission_verbs = {
            MissionType.ATTACK: "develops and deploys",
            MissionType.DEFEND: "identifies and resolves",
            MissionType.RECONNAISSANCE: "analyzes and reports on",
            MissionType.MOVEMENT: "refactors and migrates",
            MissionType.STABILITY: "maintains and optimizes",
        }

        verb = mission_verbs.get(mission_type, "executes")
        return f"minion Squadron {verb} {task} IOT achieve commander's intent."

    def _build_execution(
        self,
        task: str,
        mission_type: MissionType,
        context: dict[str, Any],
    ) -> Execution:
        """Build Para 3: EXECUTION"""
        # Commander's Intent
        intent = self._build_commander_intent(task, mission_type)

        # Concept of Operations
        concept = self._build_concept_of_ops(mission_type)

        # Task assignments per troop
        tasks = self._assign_troops(mission_type, task)

        # Coordinating instructions
        coord = [
            "Priority of effort: HHT > AIR CAV > ALPHA > BRAVO > CHARLIE",
            "All troops maintain vehicle integrity (min 2 agents per vehicle)",
            "Anonymous voting required for all GO/NO-GO decisions",
            "Report SITREP every 30 seconds during execution",
        ]

        return Execution(
            commander_intent=intent,
            concept_of_operations=concept,
            scheme_of_maneuver=f"{mission_type.value.upper()} operation with combined arms",
            tasks_to_subordinate_units=tasks,
            coordinating_instructions=coord,
        )

    def _build_commander_intent(self, task: str, mission_type: MissionType) -> str:
        """Build Commander's Intent statement"""
        end_states = {
            MissionType.ATTACK: "New capability deployed and operational",
            MissionType.DEFEND: "Vulnerability eliminated, system hardened",
            MissionType.RECONNAISSANCE: "Complete analysis delivered with recommendations",
            MissionType.MOVEMENT: "Codebase restructured with zero regressions",
            MissionType.STABILITY: "System performance optimized, stability maintained",
        }

        end_state = end_states.get(mission_type, "Mission complete")
        return f"Purpose: Execute {task}. End State: {end_state}. Key Tasks: Maintain 0% error rate through unanimous vehicle consensus."

    def _build_concept_of_ops(self, mission_type: MissionType) -> str:
        """Build Concept of Operations"""
        concepts = {
            MissionType.ATTACK: """
                Phase 1: AIR CAV conducts aerial reconnaissance of codebase
                Phase 2: ALPHA ARMOR executes main development effort
                Phase 3: BRAVO STRYKER provides rapid prototyping support
                Phase 4: CHARLIE BRADLEY secures deployment and rollback capability
            """,
            MissionType.DEFEND: """
                Phase 1: AIR CAV assesses threat vectors
                Phase 2: CHARLIE BRADLEY validates security posture
                Phase 3: ALPHA ARMOR develops and applies patches
                Phase 4: BRAVO STRYKER executes rapid response fixes
            """,
            MissionType.RECONNAISSANCE: """
                Phase 1: AIR CAV conducts primary reconnaissance
                Phase 2: BRAVO STRYKER executes parallel search threads
                Phase 3: ALPHA ARMOR performs deep analysis
                Phase 4: CHARLIE BRADLEY documents and reports findings
            """,
            MissionType.MOVEMENT: """
                Phase 1: AIR CAV maps dependencies and impact
                Phase 2: BRAVO STRYKER executes incremental moves
                Phase 3: ALPHA ARMOR completes major migrations
                Phase 4: CHARLIE BRADLEY verifies integrity post-move
            """,
            MissionType.STABILITY: """
                Phase 1: AIR CAV monitors performance baselines
                Phase 2: ALPHA ARMOR executes optimization cycles
                Phase 3: BRAVO STRYKER handles maintenance tasks
                Phase 4: CHARLIE BRADLEY ensures quality assurance
            """,
        }

        return concepts.get(mission_type, "Execute mission per SOP").strip()

    def _assign_troops(self, mission_type: MissionType, task: str) -> dict[str, list[str]]:
        """S-3 assigns troops based on mission type"""
        base_assignments = {
            MissionType.ATTACK: {
                "HHT": ["Command and control", "OPORD dissemination", "Resource coordination"],
                "AIR_CAV": [
                    "Aerial recon of codebase",
                    "Identify integration points",
                    "Report obstacles",
                ],
                "ALPHA_ARMOR": ["Heavy compute - core implementation", "Main development effort"],
                "BRAVO_STRYKER": ["Rapid prototyping", "Test coverage", "Parallel feature work"],
                "CHARLIE_BRADLEY": [
                    "Protected deployment",
                    "Rollback preparation",
                    "Security validation",
                ],
            },
            MissionType.DEFEND: {
                "HHT": ["Threat coordination", "Priority assignment", "Status tracking"],
                "AIR_CAV": [
                    "Threat assessment",
                    "Attack vector analysis",
                    "Vulnerability scanning",
                ],
                "ALPHA_ARMOR": ["Patch development", "System hardening", "Core fixes"],
                "BRAVO_STRYKER": ["Quick response fixes", "Hot patches", "Rapid deployment"],
                "CHARLIE_BRADLEY": ["Security validation", "Pen testing", "Compliance check"],
            },
            MissionType.RECONNAISSANCE: {
                "HHT": ["Research coordination", "Intel fusion", "Report compilation"],
                "AIR_CAV": ["Primary recon - full codebase scan", "Pattern identification"],
                "ALPHA_ARMOR": ["Deep analysis on findings", "Complex investigation"],
                "BRAVO_STRYKER": ["Parallel search threads", "Rapid file scanning"],
                "CHARLIE_BRADLEY": ["Document findings", "Report generation"],
            },
            MissionType.MOVEMENT: {
                "HHT": ["Migration planning", "Rollback coordination", "Progress tracking"],
                "AIR_CAV": ["Map dependencies", "Impact analysis", "Pre-migration recon"],
                "ALPHA_ARMOR": ["Execute major migrations", "Heavy lifting"],
                "BRAVO_STRYKER": ["Incremental moves", "Quick relocations"],
                "CHARLIE_BRADLEY": ["Verify integrity post-move", "Regression testing"],
            },
            MissionType.STABILITY: {
                "HHT": ["Performance monitoring", "SLA tracking", "Resource optimization"],
                "AIR_CAV": ["Monitor performance", "Detect anomalies"],
                "ALPHA_ARMOR": ["Optimization cycles", "Performance tuning"],
                "BRAVO_STRYKER": ["Maintenance tasks", "Routine updates"],
                "CHARLIE_BRADLEY": ["Quality assurance", "Stability testing"],
            },
        }

        return base_assignments.get(mission_type, base_assignments[MissionType.STABILITY])

    def _build_service_support(self, context: dict[str, Any]) -> ServiceSupport:
        """Build Para 4: SERVICE SUPPORT"""
        return ServiceSupport(
            api_keys=context.get("api_keys", {}),
            compute_budget=context.get("compute_budget", 10.0),  # $10 default
            token_limit=context.get("token_limit", 1_000_000),
            time_limit_seconds=context.get("time_limit", 300),  # 5 min default
            fallback_resources=[
                "gemini-3.1-flash-lite-preview-preview-05-20",
                "gemini-3.1-flash-lite-preview",
                "gemini-3.1-flash-lite-preview-lite",
            ],
        )

    def _build_command_signal(self) -> CommandAndSignal:
        """Build Para 5: COMMAND AND SIGNAL"""
        return CommandAndSignal(
            command={
                "squadron_commander": "Judge #6",
                "xo": "JR Engine",
                "s3": "OPORD Generator",
                "air_cav_co": "Apache Lead",
                "alpha_co": "Armor Lead",
                "bravo_co": "Stryker Lead",
                "charlie_co": "Bradley Lead",
            },
            signal={
                "primary": "HTTP/REST via port 8600",
                "alternate": "WebSocket for streaming",
                "emergency": "Direct Gemini API fallback",
            },
            succession_of_command=[
                "Squadron CDR (Judge #6)",
                "XO (JR Engine)",
                "S-3",
                "AIR CAV Troop CDR",
                "ALPHA Troop CDR",
            ],
        )

    def _generate_opord_id(self, task: str) -> str:
        """Generate unique OPORD ID"""
        self._opord_counter += 1
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M")
        task_hash = hashlib.sha256(task.encode()).hexdigest()[:6]
        return f"OPORD-{timestamp}-{task_hash}-{self._opord_counter:04d}"

    def issue_frago(self, opord: OPORD, changes: dict[str, Any], reason: str) -> FRAGO:
        """Issue FRAGO to modify existing OPORD"""
        frago = FRAGO(
            frago_id=f"FRAGO-{opord.opord_id}-{datetime.utcnow().strftime('%H%M')}",
            parent_opord_id=opord.opord_id,
            changes=changes,
            reason=reason,
        )

        logger.info(f"FRAGO {frago.frago_id} issued for {opord.opord_id}: {reason}")
        return frago


class TroopLeadingProcedures:
    """8-Step TLP with OODA loop embedded for tactical agility.
    Each step maps to Squadron staff functions.

    Based on FM 6-0 and ATP 5-19.
    """

    STEPS = [
        ("receive_mission", "S-3", OODAPhase.OBSERVE),
        ("issue_warning_order", "S-3", OODAPhase.OBSERVE),
        ("make_tentative_plan", "S-3", OODAPhase.ORIENT),
        ("initiate_movement", "S-4", OODAPhase.ORIENT),
        ("conduct_reconnaissance", "S-2", OODAPhase.ORIENT),
        ("complete_the_plan", "S-3", OODAPhase.DECIDE),
        ("issue_opord", "CDR", OODAPhase.DECIDE),
        ("supervise_and_refine", "XO", OODAPhase.ACT),
    ]

    def __init__(self, opord_generator: OPORDGenerator):
        self.generator = opord_generator
        self.current_step = 0
        self.context = {}

    async def execute(self, task: str, squadron: Any = None) -> OPORD:
        """Execute TLP to generate and issue OPORD.

        Args:
            task: Mission task description
            squadron: Squadron instance for agent coordination

        Returns:
            Issued OPORD

        """
        self.context = {"task": task, "squadron": squadron}

        for step_idx, (step_name, staff_section, ooda_phase) in enumerate(self.STEPS):
            self.current_step = step_idx

            logger.info(
                f"TLP Step {step_idx + 1}/8: {step_name} ({staff_section}) - {ooda_phase.value}",
            )

            result = await self._execute_step(step_name, staff_section, ooda_phase)
            self.context[step_name] = result

            # OODA: Check if we need to loop back
            if ooda_phase == OODAPhase.ACT and result.get("needs_replan", False):
                logger.warning("OODA loop triggered - replanning")
                return await self.execute(task, squadron)

        return self.context.get("issue_opord")

    async def _execute_step(
        self,
        step_name: str,
        staff_section: str,
        ooda_phase: OODAPhase,
    ) -> dict[str, Any]:
        """Execute individual TLP step"""
        if step_name == "receive_mission":
            return {"task": self.context["task"], "received": True}

        if step_name == "issue_warning_order":
            # Alert troops to prepare
            return {
                "warning_order_issued": True,
                "troops_alerted": ["AIR_CAV", "ALPHA", "BRAVO", "CHARLIE"],
            }

        if step_name == "make_tentative_plan":
            # Initial OPORD draft
            return {"tentative_plan": True}

        if step_name == "initiate_movement":
            # Position resources
            return {"resources_positioned": True}

        if step_name == "conduct_reconnaissance":
            # S-2 gathers intel
            return {"recon_complete": True, "intel": self.context.get("intel", {})}

        if step_name == "complete_the_plan":
            # Finalize OPORD
            opord = self.generator.generate(self.context["task"], self.context)
            return {"opord": opord, "plan_complete": True}

        if step_name == "issue_opord":
            # Commander issues OPORD
            opord = self.context.get("complete_the_plan", {}).get("opord")
            if opord:
                opord.status = "issued"
            return opord

        if step_name == "supervise_and_refine":
            # XO supervises execution
            return {"supervision_active": True, "needs_replan": False}

        return {}

    def get_status(self) -> dict[str, Any]:
        """Get current TLP execution status"""
        current = self.STEPS[self.current_step] if self.current_step < len(self.STEPS) else None

        return {
            "current_step": self.current_step + 1,
            "total_steps": len(self.STEPS),
            "step_name": current[0] if current else "complete",
            "staff_section": current[1] if current else "N/A",
            "ooda_phase": current[2].value if current else "complete",
            "progress_percent": ((self.current_step + 1) / len(self.STEPS)) * 100,
        }
