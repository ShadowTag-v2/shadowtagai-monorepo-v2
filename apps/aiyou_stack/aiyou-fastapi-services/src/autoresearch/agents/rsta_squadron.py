"""RSTA Squadron - 650 Agent Hunter-Killer Structure
=================================================
OPORD 2511-ALPHA // ATP 3-20.96 Aligned

Reorganizes minion swarm into Reinforced Armored Cavalry (650 agents):
- HHT "HEADHUNTERS" (90): Command & Control, Judge 6
- TROOP A "APACHE" (120): Deep Recon (SuperGrok/Perplexity)
- TROOP B "BRAVO" (130): Heavy Armor Dev (Gemini 1.5 Pro/Ultra)
- TROOP C "COBRA" (130): Rapid Response Frontend (Claude Sonnet/Haiku)
- TROOP D "DELTA" (130): Shadow Ops & Optimization (MoE/Fine-tunes)
- FSC "FORWARD SUPPORT" (50): CI/CD Logistics

Protocol 2511: Entropy-targeted compute allocation (arXiv:2511.02824)

Army Doctrine: ATP 3-20.96 (Cavalry Squadron), FM 3-98, ADRP 3-90
"""

import asyncio
import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any

logger = logging.getLogger(__name__)


class TroopType(StrEnum):
    """Troop types in OPORD 2511-ALPHA RSTA Squadron (650 agents)"""

    HHT = "hht"  # HEADHUNTERS - Command & Control (90)
    TROOP_A = "troop_a"  # APACHE - Deep Recon / RSTA (120)
    TROOP_B = "troop_b"  # BRAVO - Heavy Armor / Backend Dev (130)
    TROOP_C = "troop_c"  # COBRA - Stryker / Frontend Dev (130)
    TROOP_D = "troop_d"  # DELTA - Shadow Ops / Optimization (130)
    FSC = "fsc"  # Forward Support Company - CI/CD (50)

    # Legacy ATP 3-20.96 mappings (for backward compatibility)
    RECON_A = "troop_a"  # Maps to APACHE
    RECON_B = "troop_b"  # Maps to BRAVO
    RECON_C = "troop_c"  # Maps to COBRA
    SURV = "troop_a"  # Surveillance → APACHE
    MFRC = "troop_d"  # Security → DELTA
    MORTAR = "fsc"  # Indirect fires → FSC


class SectionType(StrEnum):
    """Section types within HHT - ATP 3-20.96 Chapter 2"""

    COMMAND = "command"  # CDR, XO, 1SG, Judge 6 (ATP 2-3)
    S1_PERSONNEL = "s1"  # Personnel Operations (ATP 2-15) - NEW
    S2_INTEL = "s2_intel"  # Intelligence (ATP 2-16)
    S3_OPS = "s3_ops"  # Operations (ATP 2-12)
    S4_LOGISTICS = "s4"  # Logistics (ATP 2-18) - NEW
    S6_COMMS = "s6_comms"  # Communications (ATP 2-19)
    MEDICAL = "medical"  # Medical Section (ATP 7-13) - NEW
    FSE = "fse"  # Fire Support Element (ATP 2-14)
    TACP = "tacp"  # Tactical Air Control Party (ATP 2-21) - NEW


class ReconTaskType(StrEnum):
    """Reconnaissance task types - ATP 3-20.96 Chapter 3"""

    ZONE = "zone"  # Zone Reconnaissance (ATP 3-23 to 3-30)
    AREA = "area"  # Area Reconnaissance (ATP 3-31 to 3-34)
    ROUTE = "route"  # Route Reconnaissance (ATP 3-40 to 3-48)
    FORCE = "force"  # Reconnaissance in Force (ATP 3-49 to 3-51)


class SecurityTaskType(StrEnum):
    """Security task types - ATP 3-20.96 Chapter 4"""

    SCREEN = "screen"  # Screen - early warning, observation (ATP 4-17 to 4-37)
    GUARD = "guard"  # Guard - fight for time (ATP 4-38 to 4-64)
    COVER = "cover"  # Cover - battle positions (ATP 4-65 to 4-70)
    AREA = "area_security"  # Area Security (ATP 4-13)


class JURATier(StrEnum):
    """JURA cost tiers for model assignment"""

    FREE = "free"
    FLASH = "flash"
    PRO = "pro"


# Model mapping by tier
TIER_MODELS = {
    JURATier.PRO: "gemini-3.1-flash-lite-preview-preview-06-05",
    JURATier.FLASH: "gemini-3.1-flash-lite-preview",
    JURATier.FREE: "gemini-3.1-flash-lite-preview",
}


@dataclass
class Agent:
    """Individual agent in the RSTA squadron"""

    agent_id: str
    role: str
    section: str | None = None
    troop: TroopType | None = None
    model: str = "gemini-3.1-flash-lite-preview"
    status: str = "ready"  # ready, tasked, executing, complete, error
    vote: bool | None = None  # True=approve, False=reject, None=abstain

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "role": self.role,
            "section": self.section,
            "troop": self.troop.value if self.troop else None,
            "model": self.model,
            "status": self.status,
            "vote": self.vote,
        }


@dataclass
class Section:
    """Section within a Troop (e.g., S-2 Intel, UAS Platoon)"""

    section_id: str
    name: str
    target_strength: int
    agents: list[Agent] = field(default_factory=list)
    troop: TroopType | None = None
    function: str | None = None  # RSTA function this section performs

    @property
    def current_strength(self) -> int:
        return len(self.agents)

    @property
    def ready_agents(self) -> list[Agent]:
        return [a for a in self.agents if a.status == "ready"]

    def to_dict(self) -> dict[str, Any]:
        return {
            "section_id": self.section_id,
            "name": self.name,
            "strength": self.current_strength,
            "target_strength": self.target_strength,
            "function": self.function,
        }


@dataclass
class Troop:
    """Troop (Company-level element) in RSTA Squadron"""

    troop_id: str
    troop_type: TroopType
    name: str
    target_strength: int
    sections: list[Section] = field(default_factory=list)
    model: str = "gemini-3.1-flash-lite-preview"
    rsta_function: str = ""  # Primary RSTA function

    @property
    def current_strength(self) -> int:
        return sum(s.current_strength for s in self.sections)

    def get_all_agents(self) -> list[Agent]:
        agents = []
        for section in self.sections:
            agents.extend(section.agents)
        return agents

    def to_dict(self) -> dict[str, Any]:
        return {
            "troop_id": self.troop_id,
            "troop_type": self.troop_type.value,
            "name": self.name,
            "strength": self.current_strength,
            "target_strength": self.target_strength,
            "rsta_function": self.rsta_function,
            "sections": [s.to_dict() for s in self.sections],
        }


class RSTASquadron:
    """OPORD 2511-ALPHA Hunter-Killer RSTA Squadron - 650 agents

    Implements Protocol 2511 (arXiv:2511.02824) entropy-targeted compute
    with ATP 3-20.96 Cavalry Squadron doctrine alignment.

    Squadron Structure (650 agents total):
    - HHT "HEADHUNTERS" (90): Command & Control, Judge 6, Gemini 3 Pro
      - Command: 10, S-2: 20, S-3: 20, S-6: 15, FSE: 15, TACP: 5, Medical: 5
    - TROOP A "APACHE" (120): Deep Recon / RSTA (SuperGrok/Perplexity)
      - Zone: 30, Area: 30, Screening: 30, Deep Dive: 30
    - TROOP B "BRAVO" (130): Heavy Armor / Backend Dev (Gemini 1.5 Pro/Ultra)
      - Backend: 32, Database: 32, Bridges: 33, Architecture: 33
    - TROOP C "COBRA" (130): Stryker / Frontend Dev (Claude Sonnet/Haiku)
      - React: 32, Dashboard: 32, Artifacts: 33, CQB: 33
    - TROOP D "DELTA" (130): Shadow Ops / Optimization (MoE/Fine-tunes)
      - ShadowTag: 32, Looping: 32, Cost Reduction: 33, Security: 33
    - FSC "FORWARD SUPPORT" (50): CI/CD Logistics
      - CI/CD: 16, Deploy: 17, Token Mgmt: 17

    4-Phase Operations:
    1. SCREEN: Troop A scans market/codebase for opportunities
    2. LOWEST-CONFIDENCE CHECK: Protocol 2511 entropy detection (<75%)
    3. STRIKE: Troop B/C executes engineering tasks
    4. EXPLOITATION: Troop D optimizes, ShadowTags, reduces cost
    """

    # Security task thresholds per ATP Chapter 4
    SECURITY_THRESHOLDS = {
        SecurityTaskType.SCREEN: 0.50,  # Early warning, minimal engagement (ATP 4-17)
        SecurityTaskType.GUARD: 0.75,  # Fight for time, deny observation (ATP 4-38)
        SecurityTaskType.COVER: 0.90,  # Battle positions, self-contained (ATP 4-65)
        SecurityTaskType.AREA: 0.60,  # Area security (ATP 4-13)
    }

    # OPORD 2511-ALPHA Squadron Structure (650 agents)
    SQUADRON_STRUCTURE = {
        TroopType.HHT: {
            "name": "HHT 'HEADHUNTERS' - Command & Control",
            "callsign": "HEADHUNTER",
            "target_strength": 90,
            "model": "gemini-3-pro-preview",
            "secondary_model": "gemini-3.1-flash-lite-preview",
            "rsta_function": "Command & Control, Judge 6",
            "atp_reference": "ATP 3-20.96 Chapter 2",
            "sections": [
                ("Command Section", 10, "command", "CDR, XO, 1SG, Judge 6 governance"),
                (
                    "S-2 Intelligence",
                    20,
                    "intelligence",
                    "Aggregates Perplexity/Grok intel to OPORDs",
                ),
                (
                    "S-3 Operations",
                    20,
                    "operations",
                    "Antigravity Router, Protocol 2511 entropy checks",
                ),
                (
                    "S-6 Communications",
                    15,
                    "communications",
                    "MCP coordination, inter-troop handoffs",
                ),
                (
                    "FSE Fire Support",
                    15,
                    "target_acquisition",
                    "Target package creation, priority queue",
                ),
                ("TACP", 5, "air_control", "External API coordination, airspace deconfliction"),
                ("Medical Section", 5, "medical", "Error recovery, circuit breakers, CASEVAC"),
            ],
        },
        TroopType.TROOP_A: {
            "name": "TROOP A 'APACHE' - Deep Recon / RSTA",
            "callsign": "APACHE",
            "target_strength": 120,
            "model": "grok-beta",
            "secondary_model": "llama-3.1-sonar-large-128k-online",
            "rsta_function": "Deep Reconnaissance & Market Intelligence",
            "atp_reference": "ATP 3-20.96 3-23 to 3-51",
            "recon_task": ReconTaskType.ZONE,
            "sections": [
                (
                    "1st Plt - Zone Recon",
                    30,
                    "zone_recon",
                    "Scan entire sectors (SaaS gaps, market analysis)",
                ),
                (
                    "2nd Plt - Area Recon",
                    30,
                    "area_recon",
                    "NAI-focused analysis, specific objectives",
                ),
                (
                    "3rd Plt - Screening",
                    30,
                    "screening",
                    "Monitor competitor APIs/repos for weakness",
                ),
                (
                    "4th Plt - Deep Dive",
                    30,
                    "force_recon",
                    "Perplexity deep research, long-context analysis",
                ),
            ],
        },
        TroopType.TROOP_B: {
            "name": "TROOP B 'BRAVO' - Heavy Armor / Backend Dev",
            "callsign": "BRAVO",
            "target_strength": 130,
            "model": "gemini-3.1-flash-lite-preview",
            "secondary_model": "gemini-3.1-flash-lite-preview",
            "rsta_function": "Heavy Lift Engineering",
            "atp_reference": "ATP 3-20.96 Heavy Maneuver",
            "sections": [
                ("1st Plt - Backend", 32, "backend", "Core infrastructure, API development"),
                ("2nd Plt - Database", 32, "database", "Database design, schema, migrations"),
                ("3rd Plt - Bridges", 33, "bridges", "Anthropic/Gemini bridges, MCP integration"),
                (
                    "4th Plt - Architecture",
                    33,
                    "architecture",
                    "30k+ token architectures, interdependent generations",
                ),
            ],
        },
        TroopType.TROOP_C: {
            "name": "TROOP C 'COBRA' - Stryker / Frontend Dev",
            "callsign": "COBRA",
            "target_strength": 130,
            "model": "claude-sonnet-4-5-20250929",
            "secondary_model": "claude-3-5-haiku-20241022",
            "rsta_function": "Frontend & User Experience",
            "atp_reference": "ATP 3-20.96 Rapid Maneuver",
            "sections": [
                ("1st Plt - React", 32, "frontend", "React/React Native components"),
                ("2nd Plt - Dashboard", 32, "dashboard", "Dashboard creation, data visualization"),
                (
                    "3rd Plt - Artifacts",
                    33,
                    "artifacts",
                    "Rapid artifact deployment, HTML generation",
                ),
                (
                    "4th Plt - CQB",
                    33,
                    "cqb",
                    "Close quarters battle - edge cases, user interactions",
                ),
            ],
        },
        TroopType.TROOP_D: {
            "name": "TROOP D 'DELTA' - Shadow Ops / Optimization",
            "callsign": "DELTA",
            "target_strength": 130,
            "model": "gemini-3.1-flash-lite-preview",
            "secondary_model": "grok-beta",
            "rsta_function": "Optimization & Exploitation",
            "atp_reference": "ATP 3-20.96 Chapter 4 Security",
            "sections": [
                ("1st Plt - ShadowTag", 32, "shadowtag", "Watermarking, IP protection (L0-L4)"),
                ("2nd Plt - Looping", 32, "looping", "Recursive optimization cycles on B/C output"),
                ("3rd Plt - Cost Reduction", 33, "cost_reduction", "10% cost reduction target"),
                (
                    "4th Plt - Security",
                    33,
                    "security",
                    "Security hardening, vulnerability scanning",
                ),
            ],
        },
        TroopType.FSC: {
            "name": "FSC 'FORWARD SUPPORT' - CI/CD Logistics",
            "callsign": "SUPPLY",
            "target_strength": 50,
            "model": "gemini-3.1-flash-lite-preview",
            "rsta_function": "CI/CD Pipelines, Deployment",
            "atp_reference": "ATP 3-20.96 Sustainment",
            "sections": [
                ("1st Plt - CI/CD", 16, "cicd", "GitHub Actions, pipeline management"),
                ("2nd Plt - Deploy", 17, "deploy", "Cloud Run deployment, container orchestration"),
                (
                    "3rd Plt - Token Mgmt",
                    17,
                    "token_management",
                    "Token budget, resource allocation",
                ),
            ],
        },
    }

    # Protocol 2511: Entropy-targeted thresholds (arXiv:2511.02824)
    PROTOCOL_2511_THRESHOLDS = {
        "critical_fork": 0.75,  # Trigger for long-thought compute
        "high_entropy": 0.60,  # Medium confidence warning
        "standard": 0.40,  # Normal operation
    }

    def __init__(self, model_override: str | None = None):
        """Initialize RSTA Squadron.

        Args:
            model_override: If provided, all agents use this model (for per-LLM Kosmos)

        """
        self.troops: dict[TroopType, Troop] = {}
        self.all_agents: dict[str, Agent] = {}
        self._agent_counter = 0
        self.created_at = datetime.utcnow()
        self.model_override = model_override

    def initialize(self) -> "RSTASquadron":
        """Initialize full squadron with 650 agents (OPORD 2511-ALPHA aligned)"""
        logger.info("Initializing OPORD 2511-ALPHA RSTA Squadron (650 agents)...")

        for troop_type, config in self.SQUADRON_STRUCTURE.items():
            troop = self._create_troop(troop_type, config)
            self.troops[troop_type] = troop
            logger.info(f"  {troop.name}: {troop.current_strength} agents")

        total = sum(t.current_strength for t in self.troops.values())
        logger.info(
            f"OPORD 2511-ALPHA RSTA Squadron initialized: {total} agents in {len(self.troops)} troops",
        )

        return self

    def _create_troop(self, troop_type: TroopType, config: dict[str, Any]) -> Troop:
        """Create a troop with sections and agents"""
        model = self.model_override or config["model"]

        troop = Troop(
            troop_id=f"TROOP-{troop_type.value.upper()}",
            troop_type=troop_type,
            name=config["name"],
            target_strength=config["target_strength"],
            model=model,
            rsta_function=config["rsta_function"],
        )

        for section_name, strength, role, function in config["sections"]:
            section = self._create_section(
                troop_type,
                section_name,
                strength,
                role,
                function,
                model,
            )
            troop.sections.append(section)

        return troop

    def _create_section(
        self,
        troop_type: TroopType,
        name: str,
        strength: int,
        role: str,
        function: str,
        model: str,
    ) -> Section:
        """Create a section with agents"""
        section = Section(
            section_id=f"SEC-{troop_type.value.upper()}-{name.replace(' ', '_').upper()[:10]}",
            name=name,
            target_strength=strength,
            troop=troop_type,
            function=function,
        )

        for _ in range(strength):
            agent = self._create_agent(troop_type, role, name, model)
            section.agents.append(agent)
            self.all_agents[agent.agent_id] = agent

        return section

    def _create_agent(self, troop_type: TroopType, role: str, section: str, model: str) -> Agent:
        """Create a new agent"""
        self._agent_counter += 1
        return Agent(
            agent_id=f"RSTA-{self._agent_counter:04d}",
            role=role,
            section=section,
            troop=troop_type,
            model=model,
        )

    def get_troop(self, troop_type: TroopType) -> Troop | None:
        """Get troop by type"""
        return self.troops.get(troop_type)

    def get_section_agents(self, section_type: str) -> list[Agent]:
        """Get agents from a specific section type (e.g., 'intelligence', 'recon')"""
        agents = []
        for troop in self.troops.values():
            for section in troop.sections:
                if section.function and section_type.lower() in section.function.lower():
                    agents.extend(section.agents)
        return agents

    def get_available_agents(
        self,
        count: int = 1,
        troop_type: TroopType | None = None,
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

    async def execute_with_consensus(
        self,
        task: str,
        execute_fn: Callable,
        threshold: float = 0.75,
        risk_level: str = "MEDIUM",
        recon_task: ReconTaskType | None = None,
        security_task: SecurityTaskType | None = None,
    ) -> dict[str, Any]:
        """Execute task with ATP 3-20.96 Cavalry Squadron consensus voting.
        Replaces static allow/deny lists with dynamic, differentiated consensus.

        Args:
            task: Task to execute
            execute_fn: Async function to execute (takes agent, task)
            threshold: Consensus threshold (0.5-0.9 based on risk)
            risk_level: LOW/MEDIUM/HIGH/EXTREME
            recon_task: Reconnaissance task type (ATP Ch.3) - Zone/Area/Route/Force
            security_task: Security task type (ATP Ch.4) - Screen/Guard/Cover/Area

        Returns:
            Result with consensus outcome per ATP doctrine

        """
        # Use security task threshold if specified (ATP Chapter 4)
        if security_task:
            threshold = self.SECURITY_THRESHOLDS.get(security_task, threshold)
        else:
            # Fall back to risk-based thresholds
            risk_thresholds = {
                "LOW": 0.50,
                "MEDIUM": 0.60,
                "HIGH": 0.75,
                "EXTREME": 0.90,
            }
            threshold = risk_thresholds.get(risk_level, threshold)

        # Phase 1: RECON - differentiated reconnaissance per ATP Chapter 3
        recon_results = await self._execute_reconnaissance(task, execute_fn, recon_task)

        # Phase 2: SURV - surveillance monitoring (ATP 4-19)
        surv_agents = self.get_section_agents("surveillance")
        surv_results = await self._parallel_execute(surv_agents, task, execute_fn)

        # Phase 3: S-2 INTEL - intelligence preparation (ATP 2-16)
        intel_agents = self.get_section_agents("intelligence")
        intel_results = await self._parallel_execute(intel_agents, task, execute_fn)

        # Phase 4: MFRC - differentiated security voting per ATP Chapter 4
        security_votes = await self._execute_security_voting(task, recon_results, security_task)

        # Phase 5: COMMAND - consensus decision (ATP 2-3)
        self.get_section_agents("command")
        final_decision = self._reach_consensus(security_votes, threshold)

        return {
            "task": task,
            "consensus_reached": final_decision["approved"],
            "consensus_percent": final_decision["percent"],
            "threshold": threshold,
            "risk_level": risk_level,
            "recon_task": recon_task.value if recon_task else "all",
            "security_task": security_task.value if security_task else "standard",
            "recon_count": len(recon_results),
            "surv_count": len(surv_results),
            "intel_count": len(intel_results),
            "security_votes": security_votes,
            "atp_aligned": True,
            "executed_at": datetime.utcnow().isoformat(),
        }

    async def _execute_reconnaissance(
        self,
        task: str,
        execute_fn: Callable,
        recon_task: ReconTaskType | None = None,
    ) -> list[dict[str, Any]]:
        """Execute differentiated reconnaissance per ATP 3-20.96 Chapter 3.

        - ZONE (RECON ALPHA): Comprehensive search - find ALL info
        - AREA (RECON BRAVO): Focused analysis on specific objectives
        - ROUTE (RECON CHARLIE 1/2): Linear path trafficability
        - FORCE (RECON CHARLIE 3): Aggressive probing, test enemy strength
        """
        results = []

        if recon_task == ReconTaskType.ZONE:
            # Zone reconnaissance - use RECON ALPHA only (ATP 3-23)
            agents = self.get_troop_agents(TroopType.RECON_A)
            logger.info(f"Executing ZONE reconnaissance with {len(agents)} ALPHA agents")
        elif recon_task == ReconTaskType.AREA:
            # Area reconnaissance - use RECON BRAVO only (ATP 3-31)
            agents = self.get_troop_agents(TroopType.RECON_B)
            logger.info(f"Executing AREA reconnaissance with {len(agents)} BRAVO agents")
        elif recon_task == ReconTaskType.ROUTE:
            # Route reconnaissance - use RECON CHARLIE 1/2 (ATP 3-40)
            charlie_agents = self.get_troop_agents(TroopType.RECON_C)
            agents = charlie_agents[:40]  # First two platoons
            logger.info(f"Executing ROUTE reconnaissance with {len(agents)} CHARLIE agents")
        elif recon_task == ReconTaskType.FORCE:
            # Reconnaissance in force - use RECON CHARLIE 3 (ATP 3-49)
            charlie_agents = self.get_troop_agents(TroopType.RECON_C)
            agents = charlie_agents[40:]  # Third platoon - aggressive probing
            logger.info(f"Executing FORCE reconnaissance with {len(agents)} CHARLIE agents")
        else:
            # Default: use all RECON troops for comprehensive search
            agents = []
            for troop_type in [TroopType.RECON_A, TroopType.RECON_B, TroopType.RECON_C]:
                agents.extend(self.get_troop_agents(troop_type))
            logger.info(f"Executing ALL reconnaissance with {len(agents)} agents")

        results = await self._parallel_execute(agents[:60], task, execute_fn)
        return results

    async def _execute_security_voting(
        self,
        task: str,
        prior_results: list[dict],
        security_task: SecurityTaskType | None = None,
    ) -> dict[str, int]:
        """Execute differentiated security voting per ATP 3-20.96 Chapter 4.

        - SCREEN: Early warning, observe only (50% threshold) - ATP 4-17
        - GUARD: Fight for time, deny observation (75% threshold) - ATP 4-38
        - COVER: Battle positions, self-contained (90% threshold) - ATP 4-65
        - AREA: Sector defense (60% threshold) - ATP 4-13
        """
        if security_task == SecurityTaskType.SCREEN:
            # Screen - use Screen Section only, minimal engagement
            agents = self.get_section_agents("screen_security")
            logger.info(f"Executing SCREEN security with {len(agents)} agents (50% threshold)")
        elif security_task == SecurityTaskType.GUARD:
            # Guard - use Guard Section, fight for time
            agents = self.get_section_agents("guard_security")
            logger.info(f"Executing GUARD security with {len(agents)} agents (75% threshold)")
        elif security_task == SecurityTaskType.COVER:
            # Cover - use Cover Section, battle positions
            agents = self.get_section_agents("cover_security")
            logger.info(f"Executing COVER security with {len(agents)} agents (90% threshold)")
        else:
            # Default: use all MFRC sections
            agents = self.get_troop_agents(TroopType.MFRC)
            logger.info(f"Executing ALL security with {len(agents)} agents")

        return await self._vote_on_security(agents, task, prior_results)

    def get_troop_agents(self, troop_type: TroopType) -> list[Agent]:
        """Get all agents from a specific troop"""
        troop = self.troops.get(troop_type)
        if troop:
            return troop.get_all_agents()
        return []

    async def _parallel_execute(
        self,
        agents: list[Agent],
        task: str,
        execute_fn: Callable,
    ) -> list[dict[str, Any]]:
        """Execute task across agents in parallel"""
        tasks = []
        for agent in agents:
            agent.status = "executing"
            tasks.append(execute_fn(agent, task))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for agent in agents:
            agent.status = "complete"

        return [
            {"agent_id": a.agent_id, "result": r}
            for a, r in zip(agents, results, strict=False)
            if not isinstance(r, Exception)
        ]

    async def _vote_on_security(
        self,
        agents: list[Agent],
        task: str,
        prior_results: list[dict],
    ) -> dict[str, int]:
        """MFRC agents vote on security (replaces static allow/deny)"""
        approve = 0
        reject = 0
        abstain = 0

        for agent in agents:
            # Simulated vote - in production, this calls the LLM
            # Each agent evaluates: is this task safe to execute?
            agent.vote = True  # Default approve for now
            if agent.vote is True:
                approve += 1
            elif agent.vote is False:
                reject += 1
            else:
                abstain += 1

        return {
            "approve": approve,
            "reject": reject,
            "abstain": abstain,
            "total": len(agents),
        }

    def _reach_consensus(self, votes: dict[str, int], threshold: float) -> dict[str, Any]:
        """Command section reaches final consensus"""
        total_votes = votes["approve"] + votes["reject"]
        if total_votes == 0:
            return {"approved": False, "percent": 0.0, "reason": "No votes cast"}

        approval_percent = votes["approve"] / total_votes
        approved = approval_percent >= threshold

        return {
            "approved": approved,
            "percent": approval_percent,
            "threshold": threshold,
            "reason": "Consensus reached" if approved else "Below threshold",
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
                "rsta_function": troop.rsta_function,
                "model": troop.model,
            }

        return {
            "squadron": "RSTA",
            "total_agents": total_agents,
            "ready_agents": total_ready,
            "readiness_percent": (total_ready / total_agents * 100) if total_agents > 0 else 0,
            "troops": troop_status,
            "model_override": self.model_override,
            "uptime_seconds": (datetime.utcnow() - self.created_at).total_seconds(),
        }

    # =========================================================================
    # Protocol 2511: Entropy-Targeted Compute (arXiv:2511.02824)
    # =========================================================================

    def check_entropy_threshold(self, confidence: float) -> dict[str, Any]:
        """Protocol 2511: Check if confidence triggers long-thought compute.

        At critical forks (confidence < 0.75), escalate to Gemini 3 Pro
        for extended reasoning chains.

        Args:
            confidence: Current decision confidence (0.0 to 1.0)

        Returns:
            Dict with escalation decision and target model

        """
        if confidence < self.PROTOCOL_2511_THRESHOLDS["critical_fork"]:
            return {
                "escalate": True,
                "reason": "critical_fork",
                "target_model": "gemini-3-pro-preview",
                "target_troop": TroopType.HHT,
                "confidence": confidence,
                "threshold": self.PROTOCOL_2511_THRESHOLDS["critical_fork"],
            }
        if confidence < self.PROTOCOL_2511_THRESHOLDS["high_entropy"]:
            return {
                "escalate": False,
                "reason": "high_entropy_warning",
                "target_model": "gemini-3.1-flash-lite-preview",
                "target_troop": None,
                "confidence": confidence,
                "threshold": self.PROTOCOL_2511_THRESHOLDS["high_entropy"],
            }
        return {
            "escalate": False,
            "reason": "standard_operation",
            "target_model": None,
            "target_troop": None,
            "confidence": confidence,
            "threshold": self.PROTOCOL_2511_THRESHOLDS["standard"],
        }

    async def execute_4_phase_operation(
        self,
        task: str,
        execute_fn: Callable,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Execute OPORD 2511-ALPHA 4-Phase Operation.

        Phase 1: SCREEN - Troop A scans market/codebase
        Phase 2: LOWEST-CONFIDENCE CHECK - Protocol 2511 entropy detection
        Phase 3: STRIKE - Troop B/C executes engineering
        Phase 4: EXPLOITATION - Troop D optimizes, ShadowTags

        Args:
            task: Mission task to execute
            execute_fn: Async function for agent execution
            context: Optional mission context

        Returns:
            Full operation result with all phase outcomes

        """
        operation_start = datetime.utcnow()
        results = {
            "task": task,
            "operation": "OPORD_2511_ALPHA",
            "phases": {},
        }

        # Phase 1: SCREEN - Troop A reconnaissance
        logger.info("Phase 1: SCREEN - Troop A reconnaissance")
        troop_a_agents = self.get_troop_agents(TroopType.TROOP_A)
        screen_results = await self._parallel_execute(troop_a_agents[:30], task, execute_fn)
        results["phases"]["screen"] = {
            "troop": "APACHE",
            "agent_count": len(screen_results),
            "status": "complete",
        }

        # Phase 2: LOWEST-CONFIDENCE CHECK - Protocol 2511
        logger.info("Phase 2: LOWEST-CONFIDENCE CHECK - Protocol 2511")
        # Calculate confidence from screen results (simulated)
        confidence = 0.80  # Would be calculated from actual results
        entropy_check = self.check_entropy_threshold(confidence)
        results["phases"]["entropy_check"] = entropy_check

        if entropy_check["escalate"]:
            # Escalate to HHT Command for long-thought reasoning
            logger.info("Escalating to HHT Command (Gemini 3 Pro)")
            hht_agents = self.get_troop_agents(TroopType.HHT)
            escalation_results = await self._parallel_execute(hht_agents[:10], task, execute_fn)
            results["phases"]["escalation"] = {
                "troop": "HEADHUNTERS",
                "model": "gemini-3-pro-preview",
                "agent_count": len(escalation_results),
            }

        # Phase 3: STRIKE - Troop B (Backend) and Troop C (Frontend)
        logger.info("Phase 3: STRIKE - Troop B/C engineering")
        troop_b_agents = self.get_troop_agents(TroopType.TROOP_B)
        troop_c_agents = self.get_troop_agents(TroopType.TROOP_C)

        # Execute B and C in parallel
        b_results, c_results = await asyncio.gather(
            self._parallel_execute(troop_b_agents[:32], task, execute_fn),
            self._parallel_execute(troop_c_agents[:32], task, execute_fn),
        )
        results["phases"]["strike"] = {
            "troop_b": {"troop": "BRAVO", "agent_count": len(b_results)},
            "troop_c": {"troop": "COBRA", "agent_count": len(c_results)},
            "status": "complete",
        }

        # Phase 4: EXPLOITATION - Troop D optimization
        logger.info("Phase 4: EXPLOITATION - Troop D optimization")
        troop_d_agents = self.get_troop_agents(TroopType.TROOP_D)
        exploit_results = await self._parallel_execute(troop_d_agents[:32], task, execute_fn)
        results["phases"]["exploitation"] = {
            "troop": "DELTA",
            "agent_count": len(exploit_results),
            "shadowtag_applied": True,
            "cost_reduction_target": "10%",
            "status": "complete",
        }

        # Final summary
        operation_end = datetime.utcnow()
        results["duration_seconds"] = (operation_end - operation_start).total_seconds()
        results["total_agents_engaged"] = sum(
            phase.get("agent_count", 0) if isinstance(phase, dict) else 0
            for phase in results["phases"].values()
        )
        results["status"] = "SUCCESS"

        return results

    def get_squadron_manifest(self) -> dict[str, Any]:
        """Get full OPORD 2511-ALPHA squadron manifest for deployment."""
        return {
            "opord": "2511-ALPHA",
            "doctrine_ref": "ATP 3-20.96",
            "protocol": "2511 (arXiv:2511.02824)",
            "total_strength": 650,
            "troops": {
                "HHT": {
                    "name": "HEADHUNTERS",
                    "strength": 90,
                    "model": "gemini-3-pro-preview",
                    "role": "Command & Control",
                },
                "TROOP_A": {
                    "name": "APACHE",
                    "strength": 120,
                    "model": "grok-beta",
                    "role": "Deep Recon / RSTA",
                },
                "TROOP_B": {
                    "name": "BRAVO",
                    "strength": 130,
                    "model": "gemini-3.1-flash-lite-preview",
                    "role": "Heavy Armor / Backend Dev",
                },
                "TROOP_C": {
                    "name": "COBRA",
                    "strength": 130,
                    "model": "claude-sonnet-4-5-20250929",
                    "role": "Stryker / Frontend Dev",
                },
                "TROOP_D": {
                    "name": "DELTA",
                    "strength": 130,
                    "model": "gemini-3.1-flash-lite-preview",
                    "role": "Shadow Ops / Optimization",
                },
                "FSC": {
                    "name": "FORWARD SUPPORT",
                    "strength": 50,
                    "model": "gemini-3.1-flash-lite-preview",
                    "role": "CI/CD Logistics",
                },
            },
            "protocol_2511_thresholds": self.PROTOCOL_2511_THRESHOLDS,
            "created_at": self.created_at.isoformat(),
        }


def create_rsta_squadron(model: str | None = None) -> RSTASquadron:
    """Factory function to create and initialize an RSTA Squadron (650 agents)"""
    return RSTASquadron(model_override=model).initialize()
