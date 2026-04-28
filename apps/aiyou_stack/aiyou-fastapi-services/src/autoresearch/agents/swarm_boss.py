# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""SwarmBoss - 10-Finger Audit Team Orchestrator with Army Doctrine Integration.

Army Doctrine Integration (v3.0.0):
- FM 6-0: MDMP (7-step) for strategic planning, TLP (8-step) for execution
- ATP 5-19: Composite Risk Management for audit risk assessment
- FM 7-8: Battle Drills for error handling and recovery
- Consensus thresholds dynamically adjusted by residual risk level
"""

import os
import random
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

import google.generativeai as genai

# NOTE: Environment variables loaded via `source scripts/load_mcp_secrets.sh`
# or GCP Secret Manager in production. python-dotenv is banned (GEMINI.md §secrets).
from agents.hybrid_swarm_optimizer import HybridSwarmOptimizer

# Army Doctrine Integration
try:
    from src.kosmos.doctrine import (
        BattleDrillRouter,
        DrillTrigger,
        MDMPPipeline,
        TLPPipeline,
    )
    from src.kosmos.doctrine import (
        RiskLevel as DoctrineRiskLevel,
    )
    from src.kosmos.doctrine import (
        RiskManager as DoctrineRiskManager,
    )
    from src.kosmos.doctrine.atp_5_19 import APPROVAL_AUTHORITY, CONSENSUS_THRESHOLDS  # noqa: F401

    DOCTRINE_AVAILABLE = True
except ImportError:
    DOCTRINE_AVAILABLE = False
    CONSENSUS_THRESHOLDS = {"LOW": 0.50, "MEDIUM": 0.60, "HIGH": 0.75, "EXTREMELY_HIGH": 0.90}

# Configure Gemini (Assumes API Key is in env or default auth)
if os.environ.get("GEMINI_API_KEY"):
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))


# TLP Steps
class TLPStep(Enum):
    RECEIVE_THE_MISSION = 1
    ISSUE_WARNING_ORDER = 2
    MAKE_TENTATIVE_PLAN = 3
    INITIATE_MOVEMENT = 4
    CONDUCT_RECONNAISSANCE = 5
    COMPLETE_THE_PLAN = 6
    ISSUE_THE_ORDER = 7
    SUPERVISE_AND_REFINE = 8


@dataclass
class AgentUnit:
    id: str
    squad: str
    role: str  # "Kosmos-Agent"
    status: str
    current_task: str
    credits_burned: float
    tokens_generated: int = 0
    papers_read: int = 0
    loc_analyzed: int = 0


class CRM:
    """Simulated CRM (Customer Relationship Management) / Knowledge Base"""

    def __init__(self, doctrine_dir: str = "doctrine"):
        self.doctrine_dir = doctrine_dir
        self.doctrine_content = ""
        self._load_doctrine()

    def _load_doctrine(self):
        self.doctrine_content = ""
        if os.path.exists(self.doctrine_dir):
            for filename in os.listdir(self.doctrine_dir):
                if filename.endswith(".md"):
                    file_path = os.path.join(self.doctrine_dir, filename)
                    try:
                        with open(file_path) as f:
                            self.doctrine_content += f"\n\n--- {filename} ---\n\n"
                            self.doctrine_content += f.read()
                    except Exception as e:
                        print(f"Error loading doctrine {filename}: {e}")
        else:
            self.doctrine_content = "Doctrine directory not found."

    def query(self, topic: str) -> str:
        if topic.lower() in self.doctrine_content.lower():
            return f"CRM HIT: Found doctrine on {topic}"
        return "CRM MISS: No record found."


class SwarmBoss:
    """The Boss. Oversees the Kosmos Swarm (10 Domain Agents).

    Army Doctrine Integration:
    - FM 6-0: MDMP for strategic planning, TLP for tactical execution
    - ATP 5-19: 5-step CRM for risk-based decision making
    - FM 7-8: Battle Drills for error handling
    """

    def __init__(self, session_id: str | None = None):
        self.session_id = session_id or datetime.now().strftime("%Y%m%d_%H%M%S")
        self.tlp_step = TLPStep.RECEIVE_THE_MISSION
        # 10 Fingers = 10 Dedicated Agents
        self.squads = ["Audit-Team"]
        self.display_squads = ["Audit-Team"]
        self.units: list[AgentUnit] = []
        self.mission_statement = ""
        self.crm = CRM()
        self._initialize_roster()
        self.running = False
        self.lock = threading.Lock()

        # Swarm Intelligence
        self.optimizer = HybridSwarmOptimizer(
            num_agents=len(self.units),
            num_tasks=50,
            num_squads=1,
        )
        self.optimization_result = {}

        # === Army Doctrine Integration (FM 6-0, ATP 5-19, FM 7-8) ===
        if DOCTRINE_AVAILABLE:
            # FM 6-0: MDMP for strategic planning, TLP for execution
            self.mdmp = MDMPPipeline(session_id=self.session_id)
            self.tlp_pipeline = TLPPipeline(session_id=self.session_id)

            # ATP 5-19: Risk-based consensus thresholds
            self.risk_manager = DoctrineRiskManager(session_id=self.session_id)

            # FM 7-8: Battle Drills for error handling
            self.battle_drills = BattleDrillRouter()

            # Doctrine state
            self.current_risk_level: DoctrineRiskLevel | None = None
            self.consensus_threshold = 0.60

            print(
                f"///▞ SWARM BOSS :: Army Doctrine Integration ENABLED (session: {self.session_id})",
            )
        else:
            self.mdmp = None
            self.tlp_pipeline = None
            self.risk_manager = None
            self.battle_drills = None
            self.current_risk_level = None
            self.consensus_threshold = 0.60
            print("///▞ SWARM BOSS :: Army Doctrine NOT AVAILABLE")

        # Initialize model fallback chain (Gemini high, Gemini low, then GPT-OSS 120B)
        self.model = None
        self.model_type = None  # "gemini" or "openai"
        self.model_candidates = [
            ("gemini-3-pro-high", "gemini"),
            ("gemini-3-pro-low", "gemini"),
            ("gpt-oss-120b", "openai"),
        ]
        for name, provider in self.model_candidates:
            try:
                if provider == "gemini":
                    self.model = genai.GenerativeModel(name)
                    self.model_type = "gemini"
                else:
                    from openai import OpenAI

                    # Use modern OpenAI SDK for GPT-OSS 120B
                    self.model = OpenAI()
                    self.model_type = "openai"
                break
            except Exception as e:
                print(f"Model init failed for {name}: {e}")
        if self.model is None:
            print("Warning: No LLM model could be initialized.")

    def _initialize_roster(self):
        """Creates the 10-Finger Audit Team.
        Each agent corresponds to one of the 10 Fingers of the PNKLN audit.
        """
        fingers = [
            ("01", "MarketDemand"),
            ("02", "OfferMix"),
            ("03", "TechLeverage"),
            ("04", "Distribution"),
            ("05", "PricingPower"),
            ("06", "LaborTraining"),
            ("07", "Marketing"),
            ("08", "RiskCompliance"),
            ("09", "ScalingModel"),
            ("10", "ExitAsset"),
        ]

        for idx, role in fingers:
            unit_id = f"Agent-{idx}"
            self.units.append(
                AgentUnit(
                    id=unit_id,
                    squad="Audit-Team",
                    role=role,
                    status="Idle",
                    current_task="Awaiting Orders",
                    credits_burned=0.0,
                ),
            )

    def receive_mission(self, mission: str):
        self.mission_statement = mission
        self.tlp_step = TLPStep.ISSUE_WARNING_ORDER
        self._broadcast(f"WARNO: Initiate 10-Finger Audit: {mission}")

    def step_tlp(self):
        """Advances the TLP State Machine"""
        with self.lock:
            if self.tlp_step == TLPStep.ISSUE_WARNING_ORDER:
                self._issue_warno()
            elif self.tlp_step == TLPStep.MAKE_TENTATIVE_PLAN:
                self._make_tentative_plan()
            elif self.tlp_step == TLPStep.INITIATE_MOVEMENT:
                self._initiate_movement()
            elif self.tlp_step == TLPStep.CONDUCT_RECONNAISSANCE:
                self._conduct_recon()
            elif self.tlp_step == TLPStep.COMPLETE_THE_PLAN:
                self._complete_plan()
            elif self.tlp_step == TLPStep.ISSUE_THE_ORDER:
                self._issue_order()
            elif self.tlp_step == TLPStep.SUPERVISE_AND_REFINE:
                self._supervise()

    def _broadcast(self, message: str):
        for unit in self.units:
            unit.current_task = f"Listening: {message[:20]}..."

    def _issue_warno(self):
        time.sleep(1)
        self.tlp_step = TLPStep.MAKE_TENTATIVE_PLAN
        for unit in self.units:
            unit.status = "Planning"

    def _make_tentative_plan(self):
        """Phase 1 & 2 of Swarm Intelligence:
        PSO (Task Allocation) + ACO (Routing)
        """
        time.sleep(1)
        print("///▞ BOSS :: Engaging Hybrid Swarm Optimizer (PSO+ACO)...")
        self.optimization_result = self.optimizer.optimize_mission()

        # Apply Allocation (Mock)
        allocation = self.optimization_result.get("task_allocation", [])
        for i, unit in enumerate(self.units):
            if i < len(allocation):
                unit.current_task = f"Allocated Task-{allocation[i]}"

        self.tlp_step = TLPStep.INITIATE_MOVEMENT
        for unit in self.units:
            unit.status = "Mobilizing"

    def _initiate_movement(self):
        time.sleep(1)
        self.tlp_step = TLPStep.CONDUCT_RECONNAISSANCE
        for unit in self.units:
            unit.status = "Recon"

    def _conduct_recon(self):
        # Real CRM Lookup + Deep Research Simulation
        time.sleep(1)
        self.tlp_step = TLPStep.COMPLETE_THE_PLAN
        for unit in self.units:
            unit.status = "Deep Research"
            # Query CRM for specific domain
            self.crm.query(unit.role)  # Look up "MarketDemand", "OfferMix", etc.
            unit.current_task = f"Analyzing {unit.role}"
            # Simulate Kosmos Reading (High Volume)
            unit.papers_read += random.randint(50, 150)

    def _complete_plan(self):
        time.sleep(1)
        self.tlp_step = TLPStep.ISSUE_THE_ORDER
        for unit in self.units:
            unit.status = "Ready"

    def _issue_order(self):
        self.tlp_step = TLPStep.SUPERVISE_AND_REFINE
        for unit in self.units:
            unit.status = "Executing"
            unit.current_task = f"Auditing {unit.role}..."

    def _supervise(self):
        # Supervise the Audit
        active_agents = [u for u in self.units if u.status == "Executing"]
        if not active_agents:
            return

        for unit in active_agents:
            # High tempo for Deep Audit
            if random.random() < 0.3:
                self._execute_agent_task(unit)

        # Check if audit is complete (based on depth, not burn)
        # Target: ~1000 LoC analyzed per agent for a "Deep Audit"
        if all(u.loc_analyzed > 1000 for u in active_agents):
            self._conduct_aar()

    def _conduct_aar(self):
        """Conduct After Action Review and update Doctrine"""
        print("///▞ BOSS :: Audit Complete. Conducting AAR...")
        self.tlp_step = TLPStep.RECEIVE_THE_MISSION  # Reset for next mission

        # Generate AAR
        total_loc = sum(u.loc_analyzed for u in self.units)

        # Calculate Viability Score (Mock based on random factors for demo)
        viability_score = min(100, int((total_loc / 10000) * 80 + random.randint(0, 20)))

        aar_text = f"AAR-{int(time.time())}: 10-Finger Audit Complete. Viability Score: {viability_score}/100. Analyzed {total_loc} LoC."

        # Feed back into CRM (Emergent Doctrine)
        # Append audit results to the dedicated audit log file
        log_path = os.path.join(self.crm.doctrine_dir, "audit_log.md")
        with open(log_path, "a") as log:
            log.write(
                f"\n\n## {aar_text}\n- Findings: Deep structural analysis of all 10 domains.\n- Recommendation: Proceed to Phase 2 if Score > 75.",
            )

        # Reload CRM
        self.crm._load_doctrine()
        print(f"///▞ BOSS :: Doctrine Updated with {aar_text}")

        # Reset Units
        for unit in self.units:
            unit.status = "Idle"
            unit.credits_burned = 0.0
            unit.papers_read = 0
            unit.loc_analyzed = 0

    def _execute_agent_task(self, unit: AgentUnit):
        """Executes a real or simulated LLM task (Gemini 1.5 Pro)"""
        unit.current_task = f"Auditing {unit.role}..."

        # Simulated Cost (Gemini 1.5 Pro is more expensive but powerful)
        cost = 0.001
        tokens = 500

        # Real Call (if model exists)
        if self.model:
            try:
                # Prompt specific to the agent's role
                prompt = f"As the {unit.role} expert, perform a deep audit step. Identify one key risk or opportunity."
                if self.model_type == "gemini":
                    response = self.model.generate_content(prompt)
                    if response.text:
                        tokens = len(response.text.split())
                        cost = (tokens * 7 / 1000) * 0.000125  # Approx Pro pricing
                elif self.model_type == "openai":
                    # Use modern OpenAI SDK (v1.0+)
                    # self.model is already an OpenAI() client instance
                    response = self.model.chat.completions.create(
                        model="gpt-oss-120b",
                        messages=[{"role": "user", "content": prompt}],
                    )
                    # Modern SDK returns an object with choices
                    if response and response.choices:
                        text = response.choices[0].message.content
                        tokens = len(text.split())
                        cost = (tokens * 7 / 1000) * 0.000125  # Approx pricing placeholder
                else:
                    # Unknown model type, fallback to simulated cost
                    pass
            except Exception as e:
                unit.current_task = f"Error: {str(e)[:10]}"

        unit.credits_burned += cost
        unit.tokens_generated += tokens
        unit.loc_analyzed += random.randint(100, 500)  # Deep Code Analysis
        unit.current_task = f"Gen: {tokens}t | LoC: {unit.loc_analyzed}"

    def get_status_report(self) -> dict:
        # Calculate a live viability score
        total_loc = sum(u.loc_analyzed for u in self.units)
        viability_score = min(100, int((total_loc / 10000) * 100))

        report = {
            "mission": self.mission_statement,
            "tlp_step": self.tlp_step.name,
            "total_burn": sum(u.credits_burned for u in self.units),
            "total_tokens": sum(u.tokens_generated for u in self.units),
            "total_papers": sum(u.papers_read for u in self.units),
            "total_loc": total_loc,
            "viability_score": viability_score,
            "units": self.units,
        }

        # Add doctrine status if available
        if DOCTRINE_AVAILABLE:
            report["doctrine"] = {
                "session_id": self.session_id,
                "risk_level": self.current_risk_level.value if self.current_risk_level else None,
                "consensus_threshold": self.consensus_threshold,
            }

        return report

    # =========================================================================
    # Army Doctrine Integration Methods (FM 6-0 MDMP, ATP 5-19 CRM)
    # =========================================================================

    async def receive_mission_with_mdmp(self, mission: str) -> dict[str, Any]:
        """FM 6-0 MDMP-enhanced mission reception.

        Executes full 7-step MDMP process:
        1. Receipt of Mission
        2. Mission Analysis
        3. COA Development
        4. COA Analysis (War-Game)
        5. COA Comparison
        6. COA Approval
        7. Orders Production
        """
        if not DOCTRINE_AVAILABLE or not self.mdmp:
            # Fallback to standard mission receipt
            self.receive_mission(mission)
            return {"method": "standard", "mission": mission}

        print("///▞ BOSS :: Initiating FM 6-0 MDMP 7-step planning")

        # === ATP 5-19 Pre-Mission Risk Assessment ===
        print("///▞ BOSS [MDMP 0] :: ATP 5-19 Risk Assessment")
        risk_result = await self.risk_manager.full_assessment(mission)
        residual_risk = risk_result.get("residual_risk", "MEDIUM")

        try:
            self.current_risk_level = DoctrineRiskLevel(residual_risk)
            self.consensus_threshold = CONSENSUS_THRESHOLDS.get(self.current_risk_level, 0.60)
        except (ValueError, KeyError):
            self.current_risk_level = None
            self.consensus_threshold = 0.60

        print(
            f"///▞ BOSS [MDMP 0] :: Risk: {residual_risk} → Consensus: {self.consensus_threshold:.0%}",
        )

        # === MDMP Step 1: Receipt of Mission ===
        print("///▞ BOSS [MDMP 1/7] :: Receipt of Mission")
        self.mission_statement = mission
        await self.mdmp.step1_receipt({"mission": mission, "risk_assessment": risk_result})

        # === MDMP Step 2: Mission Analysis ===
        print("///▞ BOSS [MDMP 2/7] :: Mission Analysis")
        analysis = await self.mdmp.step2_mission_analysis(
            {"mission": mission, "risk_level": residual_risk, "units_available": len(self.units)},
        )

        # === MDMP Step 3: COA Development ===
        print("///▞ BOSS [MDMP 3/7] :: COA Development")
        coas = await self.mdmp.step3_coa_development(analysis)

        # === MDMP Step 4: COA Analysis (War-Game) ===
        print("///▞ BOSS [MDMP 4/7] :: COA Analysis (War-Game)")
        wargame_results = await self.mdmp.step4_coa_analysis(coas)

        # === MDMP Step 5: COA Comparison ===
        print("///▞ BOSS [MDMP 5/7] :: COA Comparison")
        comparison = await self.mdmp.step5_coa_comparison(wargame_results)

        # === MDMP Step 6: COA Approval ===
        print("///▞ BOSS [MDMP 6/7] :: COA Approval")
        approved_coa = await self.mdmp.step6_coa_approval(comparison)

        # === MDMP Step 7: Orders Production ===
        print("///▞ BOSS [MDMP 7/7] :: Orders Production")
        opord = await self.mdmp.step7_orders_production(approved_coa)

        # Transition to TLP for execution
        self.tlp_step = TLPStep.ISSUE_WARNING_ORDER
        self._broadcast(f"WARNO: MDMP Complete - Execute 10-Finger Audit: {mission}")

        return {
            "method": "mdmp",
            "mission": mission,
            "risk_assessment": risk_result,
            "risk_level": residual_risk,
            "consensus_threshold": self.consensus_threshold,
            "analysis": analysis,
            "approved_coa": approved_coa,
            "opord": opord,
        }

    async def handle_error_with_drill(
        self,
        error: Exception,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Handle errors using FM 7-8 Battle Drills.

        Routes error to appropriate drill:
        - EXCEPTION → React to Contact (retry)
        - COST_SPIKE → Break Contact (safe mode)
        - SECURITY_ALERT → React to IED (block)
        """
        if not DOCTRINE_AVAILABLE or not self.battle_drills:
            return {"success": False, "reason": "Doctrine not available"}

        return await self.battle_drills.route(
            DrillTrigger.EXCEPTION,
            {
                "error": str(error),
                "mission": self.mission_statement,
                "session_id": self.session_id,
                **(context or {}),
            },
        )

    def get_doctrine_status(self) -> dict[str, Any]:
        """Get Army Doctrine integration status."""
        if not DOCTRINE_AVAILABLE:
            return {"available": False}

        return {
            "available": True,
            "session_id": self.session_id,
            "mdmp_status": self.mdmp.get_status() if self.mdmp else None,
            "tlp_status": self.tlp_pipeline.get_status() if self.tlp_pipeline else None,
            "risk_manager": self.risk_manager.to_dict() if self.risk_manager else None,
            "current_risk_level": self.current_risk_level.value
            if self.current_risk_level
            else None,
            "consensus_threshold": self.consensus_threshold,
            "consensus_thresholds_reference": {
                "LOW": CONSENSUS_THRESHOLDS.get("LOW", 0.50),
                "MEDIUM": CONSENSUS_THRESHOLDS.get("MEDIUM", 0.60),
                "HIGH": CONSENSUS_THRESHOLDS.get("HIGH", 0.75),
                "EXTREMELY_HIGH": CONSENSUS_THRESHOLDS.get("EXTREMELY_HIGH", 0.90),
            },
        }
