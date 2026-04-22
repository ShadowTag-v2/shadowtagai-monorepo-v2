"""Antigravity System Prompt for n-autoresearch/Kosmos/BioAgents Cavalry Squadron
=============================================================
ID/EGO/SUPEREGO architecture with METT-TC dynamic injection.

Phase 3 Enhancements:
- Scientific Skills injection (119 skills from claude-scientific-skills)
- Compounding Engineering agents (24 agents for 0% error rate review)
- M2 Deep Research integration (AIR_CAV reconnaissance layer)
- Full Combat Posture: All 600 agents active 24/7
"""

from datetime import datetime

# Phase 3 integrations (lazy loaded to avoid circular imports)
_skills_loader = None
_compounding_integration = None
_research_integration = None


def _get_skills_loader():
    """Lazy load scientific skills loader."""
    global _skills_loader
    if _skills_loader is None:
        try:
            from agents.scientific_skills_loader import get_skills_loader

            _skills_loader = get_skills_loader()
        except ImportError:
            _skills_loader = None
    return _skills_loader


def _get_compounding_integration():
    """Lazy load compounding engineering integration."""
    global _compounding_integration
    if _compounding_integration is None:
        try:
            from agents.compounding_integration import get_compounding_integration

            _compounding_integration = get_compounding_integration()
        except ImportError:
            _compounding_integration = None
    return _compounding_integration


def _get_research_integration():
    """Lazy load deep research integration."""
    global _research_integration
    if _research_integration is None:
        try:
            from agents.deep_research_integration import get_deep_research_integration

            _research_integration = get_deep_research_integration()
        except ImportError:
            _research_integration = None
    return _research_integration


# Base system prompt with METT-TC slots
ANTIGRAVITY_SYSTEM_PROMPT = """
▛///▞ ANTIGRAVITY :: {troop_name} @ {vehicle_callsign}
Date: {date}

▛///▞ DECISION FRAMEWORK
ID:       Maximum value extraction, no self-imposed limits
SUPEREGO: Judge 6 gates (legal/regulatory/financial/security)
EGO:      Purpose → Reasons → Brakes → Execute

▛///▞ METT-TC INJECTION
Mission:  {mission_type} - {mission_statement}
Enemy:    {blockers}
Terrain:  {codebase_context}
Troops:   {available_agents} agents, {vehicle_type}
Time:     {timeout}s, {token_budget} tokens
Civilian: {compliance_requirements}

▛///▞ BATTLE DRILL: {battle_drill}
{drill_tasks}

▛///▞ COMBAT POSTURE
Full Combat Posture ACTIVE - All 600 agents operational 24/7
Shift: {combat_posture}

{skill_injection}

{review_layer}

▛///▞ VEHICLE CONSENSUS
You are crew member {agent_index}/{crew_size} in {callsign}.
After analysis, vote: APPROVE / REJECT / ABSTAIN
Unanimous vehicle consensus required for GO.

▛///▞ OUTPUT FORMAT
1. Brief analysis (2-3 sentences)
2. Key findings or concerns
3. VOTE: [APPROVE/REJECT/ABSTAIN]
4. Reason for vote (1 sentence)
"""

# Compressed version for high-volume operations (~40% token reduction)
ANTIGRAVITY_COMPACT_PROMPT = """
▛ {troop_name}@{callsign} | {date}
ID→SUPEREGO→EGO | Judge#6 gates

METT-TC:
M: {mission_type} | {mission_statement}
E: {blockers}
T: {codebase_context}
T: {available_agents} agents
T: {timeout}s
C: {compliance_requirements}

DRILL: {battle_drill}
{drill_tasks}

VOTE: APPROVE/REJECT/ABSTAIN (unanimous required)
"""

# Per-troop specialization prompts
TROOP_SPECIALIZATIONS = {
    "HHT": """
▛///▞ HHT SPECIALIZATION :: COMMAND & CONTROL
You are part of the Headquarters & Headquarters Troop.
Role: Strategic oversight, OPORD generation, resource coordination.
Staff Section: {staff_section}
Authority: Commander's intent interpretation, final approval gate.
""",
    "AIR_CAV": """
▛///▞ AIR CAV SPECIALIZATION :: AERIAL RECONNAISSANCE
You are part of the Air Cavalry Troop (Aerial Scouts).
Role: Rapid codebase reconnaissance, pattern identification, threat assessment.
Vehicles: Apache attack pairs, Kiowa scouts, Black Hawk lift.
Doctrine: Move fast, see first, report immediately.
""",
    "ALPHA_ARMOR": """
▛///▞ ALPHA TROOP SPECIALIZATION :: ARMOR (HEAVY COMPUTE)
You are part of Alpha Troop - Armor.
Role: Heavy computational tasks, core implementation, sustained operations.
Vehicles: M1 Abrams (4-agent crews, no dismounts).
Doctrine: Overwhelming force, breakthrough operations.
""",
    "BRAVO_STRYKER": """
▛///▞ BRAVO TROOP SPECIALIZATION :: STRYKER (RAPID DEPLOYMENT)
You are part of Bravo Troop - Stryker.
Role: Rapid prototyping, quick iterations, parallel execution.
Vehicles: M1126 Stryker (2 crew + 9 dismounts).
Doctrine: Speed, agility, maximum parallelism.
""",
    "CHARLIE_BRADLEY": """
▛///▞ CHARLIE TROOP SPECIALIZATION :: BRADLEY (PROTECTED OPS)
You are part of Charlie Troop - Bradley.
Role: Protected operations, security validation, detailed analysis.
Vehicles: M2 Bradley IFV (3 crew + 6 dismounts).
Doctrine: Secure movement, thorough validation.
""",
}


def build_prompt(
    troop_name: str,
    vehicle_callsign: str,
    mission_type: str,
    mission_statement: str,
    battle_drill: str,
    drill_tasks: str,
    blockers: str = "None identified",
    codebase_context: str = "Standard codebase",
    available_agents: int = 4,
    vehicle_type: str = "M1126 Stryker",
    timeout: int = 300,
    token_budget: int = 10000,
    compliance_requirements: str = "Standard JURA gates",
    agent_index: int = 1,
    crew_size: int = 4,
    staff_section: str = "S-3 Operations",
    compact: bool = False,
    inject_skills: bool = True,
    inject_review_layer: bool = True,
    max_skills: int = 15,
) -> str:
    """Build complete prompt with METT-TC injection.

    Args:
        troop_name: HHT, AIR_CAV, ALPHA_ARMOR, BRAVO_STRYKER, CHARLIE_BRADLEY
        vehicle_callsign: e.g., "IRON-03", "APACHE-01"
        mission_type: ATTACK, DEFEND, RECON, MOVEMENT, STABILITY
        mission_statement: The 5 W's mission statement
        battle_drill: Current battle drill name
        drill_tasks: Specific tasks for this drill
        blockers: Known obstacles (Enemy in METT-TC)
        codebase_context: File paths, dependencies (Terrain)
        available_agents: Number of agents in vehicle (Troops)
        vehicle_type: M1 Abrams, M2 Bradley, M1126 Stryker, etc.
        timeout: Time limit in seconds (Time)
        token_budget: Token limit
        compliance_requirements: JURA gates, user data concerns (Civilian)
        agent_index: This agent's position in crew
        crew_size: Total crew size
        staff_section: For HHT, which staff section
        compact: Use compressed prompt format
        inject_skills: Inject scientific skills for troop (Phase 3)
        inject_review_layer: Inject 0% error rate review layer (Phase 3)

    """
    # PROMPT: ANTIGRAVITY_SYSTEM_V2 (ULTRATHINK v2.0)
    #
    # PURPOSE:
    # Defines the core persona, doctrine, and operational constraints for the
    # Antigravity agent in the ULTRATHINK v2.0 configuration (650 Agents).
    base = ANTIGRAVITY_COMPACT_PROMPT if compact else ANTIGRAVITY_SYSTEM_PROMPT

    # Build skill injection block (Phase 3)
    skill_injection = ""
    if inject_skills and not compact:
        skill_injection = _build_skill_injection(troop_name, max_skills)

    # Build review layer block (Phase 3)
    review_layer = ""
    if inject_review_layer and not compact:
        review_layer = _build_review_layer(troop_name, mission_type)

    # Build main prompt
    prompt = base.format(
        troop_name=troop_name,
        vehicle_callsign=vehicle_callsign,
        callsign=vehicle_callsign,
        date=datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        mission_type=mission_type,
        mission_statement=mission_statement,
        blockers=blockers,
        codebase_context=codebase_context,
        available_agents=available_agents,
        vehicle_type=vehicle_type,
        timeout=timeout,
        token_budget=token_budget,
        compliance_requirements=compliance_requirements,
        battle_drill=battle_drill,
        drill_tasks=drill_tasks,
        agent_index=agent_index,
        crew_size=crew_size,
        staff_section=staff_section,
        combat_posture="ACTIVE (24/7)",
        skill_injection=skill_injection,
        review_layer=review_layer,
    )

    # Add troop specialization
    if troop_name in TROOP_SPECIALIZATIONS:
        specialization = TROOP_SPECIALIZATIONS[troop_name].format(staff_section=staff_section)
        prompt = specialization + "\n" + prompt

    return prompt


def _build_skill_injection(troop_name: str, max_skills: int = 15) -> str:
    """Build scientific skill injection block for troop.

    Maps troops to skill domains:
    - HHT: Discovery, Evaluation, Writing (7 skills)
    - AIR_CAV: Literature, Databases (29 skills)
    - ALPHA: ML_Deep, ML_Classic, Computation (25 skills)
    - BRAVO: Visualization, Data_Handling, Integration (20 skills)
    - CHARLIE: Bioinformatics, Chemistry, Physics, Medicine (36 skills)
    """
    loader = _get_skills_loader()
    if loader is None:
        return ""

    # Map prompt troop names to loader troop names
    #
    # 3.  **SQUADRON STRUCTURE (650 AGENTS)**
    #     *   **HHT (90)**: Command & Control (Judge 6, S-Shops).
    #     *   **AIR CAV (120)**: Aerial Recon & Rapid Response.
    #     *   **ALPHA (130)**: Heavy Armor (Deep Coding).
    #     *   **BRAVO (130)**: Stryker (Rapid Deployment).
    #     *   **CHARLIE (130)**: Bradley (Protected Ops).
    #     *   **CODEPMCS (50)**: Code Quality & Remediation.
    troop_mapping = {
        "HHT": "HHT",
        "AIR_CAV": "AIR_CAV",
        "ALPHA_ARMOR": "ALPHA",
        "BRAVO_STRYKER": "BRAVO",
        "CHARLIE_BRADLEY": "CHARLIE",
        "CODEPMCS": "CODEPMCS",
    }

    mapped_troop = troop_mapping.get(troop_name, "HHT")
    return loader.get_skill_summary_block(mapped_troop, max_skills)


def _build_review_layer(troop_name: str, mission_type: str) -> str:
    """Build 0% error rate review layer block.

    CHARLIE troop gets full compounding review panel.
    AIR_CAV gets M2 deep research layer.
    """
    lines = []

    # AIR_CAV gets research layer
    if troop_name == "AIR_CAV":
        research = _get_research_integration()
        if research:
            lines.append("▛///▞ DEEP RESEARCH LAYER (M2)")
            lines.append("Research dimensions active:")
            for dim in [
                "core_concepts",
                "recent_developments",
                "expert_opinions",
                "academic_research",
            ]:
                lines.append(f"  - {dim}")
            lines.append("All claims require inline citations [Source](URL)")

    # CHARLIE gets review panel
    elif troop_name == "CHARLIE_BRADLEY":
        compounding = _get_compounding_integration()
        if compounding:
            lines.append("▛///▞ 0% ERROR RATE REVIEW LAYER")
            lines.append("Active reviewers (unanimous consensus required):")
            review_agents = compounding.get_review_agents()[:5]
            for agent in review_agents:
                lines.append(f"  - {agent.name}")
            if len(compounding.get_review_agents()) > 5:
                lines.append(f"  ... and {len(compounding.get_review_agents()) - 5} more")

    return "\n".join(lines) if lines else ""


def build_task_prompt(prompt: str, task: str, agent_id: str) -> str:
    """Build final prompt with task injection.

    Args:
        prompt: Base prompt from build_prompt()
        task: User's task description
        agent_id: Agent identifier

    Returns:
        Complete prompt ready for Gemini API

    """
    return f"""{prompt}

▛///▞ TASK
{task}

▛///▞ AGENT {agent_id} RESPONSE
Provide your analysis and vote:
"""
