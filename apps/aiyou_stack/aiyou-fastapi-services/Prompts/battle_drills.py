"""
Battle Drills for n-autoresearch/Kosmos/BioAgents Cavalry Squadron
=================================================
Mission-typed battle drills with specific tasks per troop.
Based on Army Battle Drills adapted for software operations.
"""

from dataclasses import dataclass
from enum import Enum, StrEnum


class BattleDrill(StrEnum):
    """Battle drill types mapped to mission types"""

    ATTACK_FEATURE = "attack_feature"
    DEFEND_BUG = "defend_bug"
    RECON_RESEARCH = "recon_research"
    MOVEMENT_REFACTOR = "movement_refactor"
    REACT_TO_CONTACT = "react_to_contact"
    BREAK_CONTACT = "break_contact"
    HASTY_AMBUSH = "hasty_ambush"


@dataclass
class DrillDefinition:
    """Battle drill definition"""

    name: str
    trigger: str
    phases: list[str]
    troop_tasks: dict[str, list[str]]
    success_criteria: list[str]
    abort_conditions: list[str]


# Battle Drill Definitions
BATTLE_DRILLS: dict[BattleDrill, DrillDefinition] = {
    BattleDrill.ATTACK_FEATURE: DrillDefinition(
        name="Attack - New Feature Development",
        trigger="MissionType.ATTACK or keywords: add, create, implement, build, new",
        phases=[
            "Phase 1: Reconnaissance - Scout codebase for integration points",
            "Phase 2: Isolation - Identify affected files and dependencies",
            "Phase 3: Assault - Core implementation",
            "Phase 4: Consolidation - Test coverage and documentation",
            "Phase 5: Exploitation - Deploy and monitor",
        ],
        troop_tasks={
            "HHT": [
                "Issue OPORD with commander's intent",
                "Coordinate resource allocation",
                "Monitor progress and issue FRAGOs as needed",
            ],
            "AIR_CAV": [
                "Aerial recon of entire codebase",
                "Identify all integration points",
                "Map dependencies and potential conflicts",
                "Report obstacles to S-3",
            ],
            "ALPHA_ARMOR": [
                "Execute main development effort",
                "Heavy compute for core logic",
                "Build primary implementation",
                "Ensure code quality standards",
            ],
            "BRAVO_STRYKER": [
                "Rapid prototyping support",
                "Parallel feature branches",
                "Build test coverage",
                "Quick iteration cycles",
            ],
            "CHARLIE_BRADLEY": [
                "Security review of new code",
                "Protected deployment preparation",
                "Rollback plan development",
                "Compliance validation",
            ],
        },
        success_criteria=[
            "Feature implemented per requirements",
            "All tests passing",
            "Security review complete",
            "Documentation updated",
            "Deployment successful",
        ],
        abort_conditions=[
            "Critical blocker identified",
            "Security vulnerability discovered",
            "Rate limit exhaustion",
            "Timeout exceeded",
        ],
    ),
    BattleDrill.DEFEND_BUG: DrillDefinition(
        name="Defend - Bug Fix / Security Patch",
        trigger="MissionType.DEFEND or keywords: fix, bug, patch, secure, repair",
        phases=[
            "Phase 1: Assess - Identify threat vector",
            "Phase 2: Isolate - Contain affected area",
            "Phase 3: Neutralize - Develop and apply patch",
            "Phase 4: Verify - Validate fix effectiveness",
            "Phase 5: Harden - Prevent recurrence",
        ],
        troop_tasks={
            "HHT": [
                "Classify severity (critical/high/medium/low)",
                "Prioritize based on impact",
                "Coordinate response teams",
            ],
            "AIR_CAV": [
                "Threat assessment",
                "Attack vector analysis",
                "Identify all affected components",
                "Scan for similar vulnerabilities",
            ],
            "ALPHA_ARMOR": [
                "Develop patch",
                "System hardening",
                "Core fix implementation",
                "Regression testing",
            ],
            "BRAVO_STRYKER": [
                "Quick response fixes",
                "Hot patch deployment",
                "Rapid testing cycles",
                "Monitoring setup",
            ],
            "CHARLIE_BRADLEY": [
                "Security validation",
                "Penetration testing",
                "Compliance verification",
                "Audit trail documentation",
            ],
        },
        success_criteria=[
            "Bug/vulnerability eliminated",
            "No regressions introduced",
            "Security review passed",
            "Root cause documented",
            "Prevention measures in place",
        ],
        abort_conditions=[
            "Fix introduces new critical issue",
            "Cannot reproduce in test environment",
            "Requires architectural change beyond scope",
        ],
    ),
    BattleDrill.RECON_RESEARCH: DrillDefinition(
        name="Reconnaissance - Research & Analysis",
        trigger="MissionType.RECONNAISSANCE or keywords: research, analyze, find, search, investigate",
        phases=[
            "Phase 1: Zone Recon - Broad codebase scan",
            "Phase 2: Area Recon - Deep dive on findings",
            "Phase 3: Pattern Analysis - Identify commonalities",
            "Phase 4: Intelligence Fusion - Compile findings",
            "Phase 5: Report - Document and recommend",
        ],
        troop_tasks={
            "HHT": [
                "Define reconnaissance objectives",
                "Set priority intelligence requirements (PIR)",
                "Compile final intelligence estimate",
            ],
            "AIR_CAV": [
                "Primary recon - full codebase scan",
                "Pattern identification",
                "Anomaly detection",
                "Rapid reporting",
            ],
            "ALPHA_ARMOR": [
                "Deep analysis on findings",
                "Complex investigation",
                "Technical deep-dives",
                "Architecture assessment",
            ],
            "BRAVO_STRYKER": [
                "Parallel search threads",
                "Rapid file scanning",
                "Cross-reference validation",
                "Quick lookups",
            ],
            "CHARLIE_BRADLEY": [
                "Document findings",
                "Generate reports",
                "Compliance implications",
                "Risk assessment",
            ],
        },
        success_criteria=[
            "All PIRs answered",
            "Comprehensive analysis delivered",
            "Actionable recommendations provided",
            "Sources documented",
        ],
        abort_conditions=[
            "Scope creep beyond mission parameters",
            "Insufficient access to required resources",
        ],
    ),
    BattleDrill.MOVEMENT_REFACTOR: DrillDefinition(
        name="Movement - Refactoring & Migration",
        trigger="MissionType.MOVEMENT or keywords: refactor, migrate, move, rename, reorganize",
        phases=[
            "Phase 1: Route Recon - Map dependencies",
            "Phase 2: Advance Party - Test migration path",
            "Phase 3: Main Body - Execute migration",
            "Phase 4: Rear Guard - Verify integrity",
            "Phase 5: Consolidation - Clean up",
        ],
        troop_tasks={
            "HHT": [
                "Migration planning",
                "Rollback coordination",
                "Progress tracking",
                "Risk mitigation",
            ],
            "AIR_CAV": [
                "Map all dependencies",
                "Impact analysis",
                "Pre-migration recon",
                "Route clearance",
            ],
            "ALPHA_ARMOR": [
                "Execute major migrations",
                "Heavy lifting operations",
                "Core restructuring",
                "Database migrations",
            ],
            "BRAVO_STRYKER": [
                "Incremental moves",
                "Quick relocations",
                "Parallel migration streams",
                "Fast rollback capability",
            ],
            "CHARLIE_BRADLEY": [
                "Verify integrity post-move",
                "Regression testing",
                "Security validation",
                "Compliance check",
            ],
        },
        success_criteria=[
            "All components migrated successfully",
            "Zero regressions",
            "All tests passing",
            "Old code deprecated/removed",
            "Documentation updated",
        ],
        abort_conditions=[
            "Critical regression detected",
            "Data integrity issue",
            "Rollback triggered",
        ],
    ),
    BattleDrill.REACT_TO_CONTACT: DrillDefinition(
        name="React to Contact - Error Handling",
        trigger="Unexpected error during execution",
        phases=[
            "Phase 1: Return Fire - Immediate response",
            "Phase 2: Seek Cover - Isolate failure",
            "Phase 3: Assess - Determine enemy strength",
            "Phase 4: Report - SITREP to higher",
            "Phase 5: Decide - Continue, FRAGO, or abort",
        ],
        troop_tasks={
            "HHT": [
                "Receive SITREP",
                "Assess situation",
                "Issue FRAGO or abort order",
                "Reallocate resources",
            ],
            "AIR_CAV": [
                "Rapid damage assessment",
                "Identify error source",
                "Report to HHT",
            ],
            "ALPHA_ARMOR": [
                "Contain error spread",
                "Stabilize systems",
                "Prepare recovery options",
            ],
            "BRAVO_STRYKER": [
                "Quick workaround attempt",
                "Parallel recovery paths",
                "Fast failover",
            ],
            "CHARLIE_BRADLEY": [
                "Protect critical systems",
                "Secure data integrity",
                "Audit trail preservation",
            ],
        },
        success_criteria=[
            "Error contained",
            "Recovery executed or graceful degradation",
            "Root cause identified",
            "Lessons learned captured",
        ],
        abort_conditions=[
            "Cascading failures",
            "Data corruption risk",
            "Security breach",
        ],
    ),
    BattleDrill.BREAK_CONTACT: DrillDefinition(
        name="Break Contact - Graceful Abort",
        trigger="Mission abort required",
        phases=[
            "Phase 1: Suppress - Stop ongoing operations",
            "Phase 2: Cover - Secure current state",
            "Phase 3: Move - Rollback if needed",
            "Phase 4: Rally - Regroup at safe state",
        ],
        troop_tasks={
            "HHT": [
                "Issue abort order",
                "Coordinate withdrawal",
                "Preserve mission data",
            ],
            "AIR_CAV": [
                "Provide overwatch",
                "Monitor for issues",
            ],
            "ALPHA_ARMOR": [
                "Halt current operations",
                "Preserve state",
            ],
            "BRAVO_STRYKER": [
                "Fast withdrawal",
                "Quick rollback",
            ],
            "CHARLIE_BRADLEY": [
                "Secure and cover",
                "Protect data",
            ],
        },
        success_criteria=[
            "Clean abort achieved",
            "No partial state left",
            "All resources released",
            "AAR scheduled",
        ],
        abort_conditions=[],  # This IS the abort drill
    ),
}


def get_drill_for_mission(mission_type: str) -> BattleDrill:
    """Map mission type to appropriate battle drill"""
    mapping = {
        "attack": BattleDrill.ATTACK_FEATURE,
        "defend": BattleDrill.DEFEND_BUG,
        "recon": BattleDrill.RECON_RESEARCH,
        "reconnaissance": BattleDrill.RECON_RESEARCH,
        "movement": BattleDrill.MOVEMENT_REFACTOR,
        "stability": BattleDrill.ATTACK_FEATURE,  # Default to attack for stability
    }
    return mapping.get(mission_type.lower(), BattleDrill.ATTACK_FEATURE)


def get_drill_tasks_for_troop(drill: BattleDrill, troop: str) -> str:
    """Get formatted task list for a specific troop in a drill"""
    definition = BATTLE_DRILLS.get(drill)
    if not definition:
        return "Execute mission per SOP"

    tasks = definition.troop_tasks.get(troop, [])
    if not tasks:
        return "Support as directed"

    return "\n".join(f"  - {task}" for task in tasks)


def get_drill_phases(drill: BattleDrill) -> str:
    """Get formatted phases for a drill"""
    definition = BATTLE_DRILLS.get(drill)
    if not definition:
        return ""

    return "\n".join(definition.phases)
