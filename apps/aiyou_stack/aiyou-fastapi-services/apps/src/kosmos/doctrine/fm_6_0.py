"""
FM 6-0: Commander and Staff Organization and Operations
========================================================

Source: FM 6-0 (May 2022)

Implements:
1. MDMP (Military Decision Making Process) - 7 steps for battalion+
2. TLP (Troop Leading Procedures) - 8 steps for company and below
3. Staff Section definitions (S-1 through S-6)

Mission Command Philosophy:
"Exercise of authority and direction by the commander using mission orders
to enable disciplined initiative within the commander's intent."
"""

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class MDMPStep(Enum):
    """FM 6-0 Chapter 9: Military Decision Making Process (7 Steps)"""

    RECEIPT_OF_MISSION = 1  # Receive the mission
    MISSION_ANALYSIS = 2  # Analyze the mission (1/3 of time)
    COA_DEVELOPMENT = 3  # Develop courses of action
    COA_ANALYSIS = 4  # Analyze COAs (wargaming)
    COA_COMPARISON = 5  # Compare COAs
    COA_APPROVAL = 6  # Commander approves COA
    ORDERS_PRODUCTION = 7  # Produce orders


class TLPStep(Enum):
    """FM 6-0 Chapter 10: Troop Leading Procedures (8 Steps)"""

    RECEIVE_MISSION = 1  # Receive the mission
    ISSUE_WARNING_ORDER = 2  # Issue a warning order
    MAKE_TENTATIVE_PLAN = 3  # Make a tentative plan
    INITIATE_MOVEMENT = 4  # Initiate movement (start prep)
    CONDUCT_RECON = 5  # Conduct reconnaissance
    COMPLETE_PLAN = 6  # Complete the plan
    ISSUE_ORDER = 7  # Issue the complete order
    SUPERVISE_REFINE = 8  # Supervise and refine


class StaffSectionType(Enum):
    """FM 6-0 Chapter 4: Staff Organization"""

    S1 = "S-1"  # Personnel (Adjutant)
    S2 = "S-2"  # Intelligence
    S3 = "S-3"  # Operations
    S4 = "S-4"  # Logistics
    S5 = "S-5"  # Civil Affairs (when assigned)
    S6 = "S-6"  # Signal/Communications


@dataclass
class StaffSection:
    """
    FM 6-0 Staff Section definition.

    Each staff section has specific responsibilities in the planning process.
    """

    section_type: StaffSectionType
    section_chief: str
    personnel_count: int

    # Running estimate components
    running_estimate: dict[str, Any] = field(default_factory=dict)

    # Staff section responsibilities
    responsibilities: list[str] = field(default_factory=list)

    def __post_init__(self):
        """Set default responsibilities per FM 6-0"""
        if not self.responsibilities:
            self.responsibilities = self._get_default_responsibilities()

    def _get_default_responsibilities(self) -> list[str]:
        """FM 6-0 Chapter 4: Staff responsibilities"""
        defaults = {
            StaffSectionType.S1: [
                "Personnel readiness management",
                "Casualty operations",
                "Personnel accountability",
                "Morale, welfare, recreation",
                "Awards and decorations",
                "Agent lifecycle management",  # AI adaptation
            ],
            StaffSectionType.S2: [
                "Intelligence preparation of battlefield (IPB)",
                "Threat assessment",
                "Collection management",
                "Priority intelligence requirements (PIR)",
                "Counterintelligence",
                "Context analysis",  # AI adaptation
            ],
            StaffSectionType.S3: [
                "Operations planning (MDMP/TLP)",
                "Training management",
                "Current operations",
                "Future operations",
                "Task organization",
                "Pipeline orchestration",  # AI adaptation
            ],
            StaffSectionType.S4: [
                "Supply operations",
                "Maintenance operations",
                "Transportation",
                "Field services",
                "Property accountability",
                "Token budget management",  # AI adaptation
            ],
            StaffSectionType.S5: [
                "Civil-military operations",
                "Civil affairs",
                "Host nation coordination",
                "User interface",  # AI adaptation
            ],
            StaffSectionType.S6: [
                "Signal operations",
                "Network operations",
                "Information systems",
                "Communications security",
                "Inter-agent messaging",  # AI adaptation
            ],
        }
        return defaults.get(self.section_type, [])

    def update_running_estimate(self, key: str, value: Any):
        """Update running estimate per FM 6-0 Appendix C"""
        self.running_estimate[key] = {
            "value": value,
            "updated_at": datetime.utcnow().isoformat(),
            "section": self.section_type.value,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "section": self.section_type.value,
            "chief": self.section_chief,
            "personnel": self.personnel_count,
            "responsibilities": self.responsibilities,
            "running_estimate": self.running_estimate,
            "fm_reference": "FM 6-0",
        }


@dataclass
class MDMPProduct:
    """Product from an MDMP step"""

    step: MDMPStep
    name: str
    content: Any
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class MDMPPipeline:
    """
    FM 6-0 Military Decision Making Process implementation.

    7-step planning process for battalion level and above.
    Provides analytical approach to problem solving.

    Time allocation rule: Subordinates get 2/3 of available time.
    Mission analysis should take 1/3 of commander's planning time.
    """

    session_id: str
    commander_intent: str = ""
    current_step: MDMPStep = MDMPStep.RECEIPT_OF_MISSION
    products: list[MDMPProduct] = field(default_factory=list)
    coas: list[dict[str, Any]] = field(default_factory=list)
    selected_coa: dict[str, Any] | None = None

    # Staff sections
    staff: dict[StaffSectionType, StaffSection] = field(default_factory=dict)

    # Callbacks for each step
    step_handlers: dict[MDMPStep, Callable] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize default staff sections"""
        if not self.staff:
            self.staff = {
                StaffSectionType.S1: StaffSection(StaffSectionType.S1, "S-1 Chief", 10),
                StaffSectionType.S2: StaffSection(StaffSectionType.S2, "S-2 Chief", 20),
                StaffSectionType.S3: StaffSection(StaffSectionType.S3, "S-3 Chief", 20),
                StaffSectionType.S4: StaffSection(StaffSectionType.S4, "S-4 Chief", 10),
                StaffSectionType.S6: StaffSection(StaffSectionType.S6, "S-6 Chief", 15),
            }

    async def step1_receive_mission(self, user_request: str) -> dict[str, Any]:
        """
        Step 1: Receipt of Mission

        Commander and staff receive mission from higher HQ.
        Initial time allocation determined.
        """
        self.current_step = MDMPStep.RECEIPT_OF_MISSION

        result = {
            "task": user_request,
            "higher_hq_guidance": self._extract_guidance(user_request),
            "initial_time_allocation": self._calculate_time_allocation(),
            "warning_order_needed": True,
        }

        self.products.append(
            MDMPProduct(
                step=MDMPStep.RECEIPT_OF_MISSION,
                name="Initial Mission Receipt",
                content=result,
            )
        )

        return result

    async def step2_mission_analysis(
        self, mission: dict[str, Any], atomize_func: Callable | None = None
    ) -> dict[str, Any]:
        """
        Step 2: Mission Analysis (1/3 of planning time)

        Products:
        - Restated mission
        - Initial commander's intent
        - Planning guidance
        - Specified/implied/essential tasks
        - IPB products (S-2)
        """
        self.current_step = MDMPStep.MISSION_ANALYSIS

        # S-2 conducts IPB
        ipb = await self._conduct_ipb(mission)
        self.staff[StaffSectionType.S2].update_running_estimate("ipb", ipb)

        # Extract tasks
        specified_tasks = self._extract_specified_tasks(mission)
        implied_tasks = self._extract_implied_tasks(mission)
        essential_tasks = self._identify_essential_tasks(specified_tasks, implied_tasks)

        # Atomize if function provided (Antigravity integration)
        atoms = []
        if atomize_func:
            atoms = await atomize_func(mission.get("task", ""))

        result = {
            "restated_mission": self._restate_mission(mission, essential_tasks),
            "commander_intent": self.commander_intent or self._draft_intent(essential_tasks),
            "planning_guidance": self._generate_planning_guidance(),
            "specified_tasks": specified_tasks,
            "implied_tasks": implied_tasks,
            "essential_tasks": essential_tasks,
            "ipb": ipb,
            "atoms": atoms,
            "constraints": self._extract_constraints(mission),
            "assumptions": self._identify_assumptions(mission),
        }

        self.products.append(
            MDMPProduct(
                step=MDMPStep.MISSION_ANALYSIS,
                name="Mission Analysis Products",
                content=result,
            )
        )

        return result

    async def step3_coa_development(
        self, analysis: dict[str, Any], approaches: list[str] = None
    ) -> list[dict[str, Any]]:
        """
        Step 3: COA Development

        Develop multiple courses of action.
        Each COA must be:
        - Suitable (accomplish mission)
        - Feasible (within capabilities)
        - Acceptable (worth the cost)
        - Distinguishable (different from others)
        - Complete (addresses all essential tasks)
        """
        self.current_step = MDMPStep.COA_DEVELOPMENT

        approaches = approaches or ["aggressive", "balanced", "conservative"]

        for approach in approaches:
            coa = {
                "name": f"COA_{approach.upper()}",
                "approach": approach,
                "concept": self._develop_concept(analysis, approach),
                "task_organization": self._develop_task_org(analysis, approach),
                "essential_tasks_addressed": analysis.get("essential_tasks", []),
                "risk_assessment": self._initial_risk_assessment(approach),
                "suitability": True,
                "feasibility": True,
                "acceptability": True,
                "distinguishable": True,
                "complete": True,
            }
            self.coas.append(coa)

        self.products.append(
            MDMPProduct(
                step=MDMPStep.COA_DEVELOPMENT,
                name="Courses of Action",
                content=self.coas,
            )
        )

        return self.coas

    async def step4_coa_analysis(
        self, coas: list[dict[str, Any]], wargame_func: Callable | None = None
    ) -> list[dict[str, Any]]:
        """
        Step 4: COA Analysis (Wargaming)

        War-game each COA to identify:
        - Strengths and weaknesses
        - Decision points
        - High payoff targets
        - Task adjustments needed
        """
        self.current_step = MDMPStep.COA_ANALYSIS

        results = []
        for coa in coas:
            if wargame_func:
                wargame_result = await wargame_func(coa)
            else:
                wargame_result = self._basic_wargame(coa)

            analysis = {
                "coa_name": coa["name"],
                "strengths": wargame_result.get("strengths", []),
                "weaknesses": wargame_result.get("weaknesses", []),
                "decision_points": wargame_result.get("decision_points", []),
                "branches": wargame_result.get("branches", []),
                "sequels": wargame_result.get("sequels", []),
                "risk_level": wargame_result.get("risk_level", "MEDIUM"),
            }
            results.append(analysis)

        self.products.append(
            MDMPProduct(step=MDMPStep.COA_ANALYSIS, name="Wargaming Results", content=results)
        )

        return results

    async def step5_coa_comparison(
        self, wargame_results: list[dict[str, Any]], criteria: list[str] = None
    ) -> dict[str, Any]:
        """
        Step 5: COA Comparison

        Compare COAs using evaluation criteria.
        Staff recommends best COA to commander.
        """
        self.current_step = MDMPStep.COA_COMPARISON

        criteria = criteria or [
            "mission_accomplishment",
            "risk_to_force",
            "flexibility",
            "simplicity",
            "resource_efficiency",
        ]

        comparison_matrix = []
        for result in wargame_results:
            scores = {}
            for criterion in criteria:
                scores[criterion] = self._score_criterion(result, criterion)
            scores["total"] = sum(scores.values())
            comparison_matrix.append({"coa_name": result["coa_name"], "scores": scores})

        # Sort by total score
        comparison_matrix.sort(key=lambda x: x["scores"]["total"], reverse=True)
        recommended = comparison_matrix[0]["coa_name"] if comparison_matrix else None

        result = {
            "criteria": criteria,
            "comparison_matrix": comparison_matrix,
            "staff_recommendation": recommended,
            "rationale": f"COA {recommended} scored highest across evaluation criteria",
        }

        self.products.append(
            MDMPProduct(step=MDMPStep.COA_COMPARISON, name="COA Comparison", content=result)
        )

        return result

    async def step6_coa_approval(
        self, comparison: dict[str, Any], commander_decision: str | None = None
    ) -> dict[str, Any]:
        """
        Step 6: COA Approval

        Commander approves, modifies, or rejects staff recommendation.
        Refines commander's intent.
        """
        self.current_step = MDMPStep.COA_APPROVAL

        approved_coa_name = commander_decision or comparison.get("staff_recommendation")

        # Find the approved COA
        for coa in self.coas:
            if coa["name"] == approved_coa_name:
                self.selected_coa = coa
                break

        result = {
            "approved_coa": approved_coa_name,
            "commander_intent": self.commander_intent,
            "refinements": [],
            "ccir": self._identify_ccir(),  # Commander's Critical Info Requirements
            "eefi": self._identify_eefi(),  # Essential Elements of Friendly Info
        }

        self.products.append(
            MDMPProduct(step=MDMPStep.COA_APPROVAL, name="COA Approval", content=result)
        )

        return result

    async def step7_orders_production(
        self, approved_coa: dict[str, Any], generate_func: Callable | None = None
    ) -> dict[str, Any]:
        """
        Step 7: Orders Production

        Produce the operations order (OPORD).
        Five-paragraph order format.
        """
        self.current_step = MDMPStep.ORDERS_PRODUCTION

        # Generate code if function provided (Antigravity integration)
        generated_code = None
        if generate_func and self.selected_coa:
            generated_code = await generate_func(self.selected_coa)

        opord = {
            "situation": {
                "enemy": self.staff[StaffSectionType.S2].running_estimate.get("ipb", {}),
                "friendly": self._friendly_situation(),
                "attachments_detachments": [],
            },
            "mission": self._format_mission_statement(),
            "execution": {
                "commander_intent": self.commander_intent,
                "concept_of_operations": self.selected_coa.get("concept", "")
                if self.selected_coa
                else "",
                "tasks_to_subordinate_units": self._assign_tasks(),
                "coordinating_instructions": [],
            },
            "sustainment": self.staff[StaffSectionType.S4].running_estimate,
            "command_and_signal": {
                "command": self._command_relationships(),
                "signal": self.staff[StaffSectionType.S6].running_estimate,
            },
            "generated_code": generated_code,
        }

        self.products.append(
            MDMPProduct(step=MDMPStep.ORDERS_PRODUCTION, name="Operations Order", content=opord)
        )

        return opord

    # Helper methods
    def _extract_guidance(self, request: str) -> dict[str, Any]:
        return {"raw_request": request, "constraints": [], "freedoms": []}

    def _calculate_time_allocation(self) -> dict[str, str]:
        return {"commander": "1/3", "subordinates": "2/3"}

    async def _conduct_ipb(self, mission: dict[str, Any]) -> dict[str, Any]:
        return {
            "terrain_analysis": {},
            "weather_analysis": {},
            "threat_evaluation": {},
            "civil_considerations": {},
        }

    def _extract_specified_tasks(self, mission: dict[str, Any]) -> list[str]:
        return mission.get("specified_tasks", [])

    def _extract_implied_tasks(self, mission: dict[str, Any]) -> list[str]:
        return []

    def _identify_essential_tasks(self, specified: list[str], implied: list[str]) -> list[str]:
        return specified[:3] if specified else []

    def _restate_mission(self, mission: dict[str, Any], essential: list[str]) -> str:
        return f"On order, {mission.get('task', 'execute mission')} in order to {', '.join(essential[:2]) if essential else 'accomplish objectives'}"

    def _draft_intent(self, essential_tasks: list[str]) -> str:
        return "Purpose: Accomplish mission. End state: All essential tasks complete."

    def _generate_planning_guidance(self) -> list[str]:
        return ["Focus on mission accomplishment", "Minimize risk to force"]

    def _extract_constraints(self, mission: dict[str, Any]) -> list[str]:
        return mission.get("constraints", [])

    def _identify_assumptions(self, mission: dict[str, Any]) -> list[str]:
        return []

    def _develop_concept(self, analysis: dict[str, Any], approach: str) -> str:
        return f"{approach.capitalize()} approach to mission execution"

    def _develop_task_org(self, analysis: dict[str, Any], approach: str) -> dict[str, Any]:
        return {"main_effort": "TBD", "supporting_efforts": []}

    def _initial_risk_assessment(self, approach: str) -> str:
        risk_map = {"aggressive": "HIGH", "balanced": "MEDIUM", "conservative": "LOW"}
        return risk_map.get(approach, "MEDIUM")

    def _basic_wargame(self, coa: dict[str, Any]) -> dict[str, Any]:
        return {
            "strengths": ["Addresses essential tasks"],
            "weaknesses": [],
            "decision_points": [],
            "branches": [],
            "sequels": [],
            "risk_level": coa.get("risk_assessment", "MEDIUM"),
        }

    def _score_criterion(self, result: dict[str, Any], criterion: str) -> int:
        return 3  # Default score

    def _identify_ccir(self) -> list[str]:
        return []

    def _identify_eefi(self) -> list[str]:
        return []

    def _friendly_situation(self) -> dict[str, Any]:
        return {}

    def _format_mission_statement(self) -> str:
        return (
            self.products[1].content.get("restated_mission", "") if len(self.products) > 1 else ""
        )

    def _assign_tasks(self) -> list[dict[str, Any]]:
        return []

    def _command_relationships(self) -> dict[str, Any]:
        return {}

    def get_status(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "current_step": self.current_step.value,
            "step_name": self.current_step.name,
            "products_generated": len(self.products),
            "coas_developed": len(self.coas),
            "selected_coa": self.selected_coa.get("name") if self.selected_coa else None,
            "fm_reference": "FM 6-0",
        }


@dataclass
class TLPPipeline:
    """
    FM 6-0 Troop Leading Procedures implementation.

    8-step planning process for company level and below.
    Faster, more flexible than MDMP.
    Steps are not sequential - can be performed in any order.
    """

    session_id: str
    current_step: TLPStep = TLPStep.RECEIVE_MISSION
    mission: dict[str, Any] = field(default_factory=dict)
    plan: dict[str, Any] = field(default_factory=dict)
    order_issued: bool = False

    async def quick_plan(self, task: str) -> dict[str, Any]:
        """Execute abbreviated TLP for time-critical tasks"""

        # Step 1: Receive
        self.mission = {"task": task, "received_at": datetime.utcnow().isoformat()}

        # Step 3: Tentative plan (skip warning order for speed)
        self.plan = {
            "task": task,
            "concept": f"Execute {task} with available resources",
            "tasks": [task],
            "timeline": "ASAP",
        }

        # Step 7: Issue order
        order = {
            "situation": "As briefed",
            "mission": task,
            "execution": self.plan["concept"],
            "sustainment": "Organic",
            "command_signal": "Standard",
        }
        self.order_issued = True

        return order

    def get_status(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "current_step": self.current_step.value,
            "order_issued": self.order_issued,
            "fm_reference": "FM 6-0",
        }
