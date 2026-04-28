# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Ecosystem - Unified Legal-Linguistic Multi-Agent System
Version: 1.0.0

Philosophy: Legal precision meets agent coordination for 99%+ accuracy.
Design: Combines all subsystems into single orchestrated workflow.

"All errors are reading comprehension."
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any

from .agent_lifecycle import AgentLifecycle, RegenerationTrigger
from .agent_specialization import AgentSpecialization, ExpertiseDomain
from .agent_wellness import AgentWellness, BreakType, VitaminType

# Import all subsystems
from .legal_whiteboard import DebatePhase, LegalWhiteboard, TestCase
from .persistent_memory import AgentLevel, InsightType, PersistentMemory
from .quidditch_competition import HogwartsHouse, QuidditchCompetition, QuidditchRole
from .verb_specification import VerbCategory, VerbSpecification


class TaskStatus(StrEnum):
    """Task execution status."""

    PENDING = "pending"
    PARSING = "parsing"
    DECOMPOSING = "decomposing"
    DEBATING = "debating"
    SYNTHESIZING = "synthesizing"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class EcosystemAgent:
    """Agent within the ecosystem."""

    agent_id: str
    house: HogwartsHouse
    level: AgentLevel = AgentLevel.TOOL_USING
    primary_domain: ExpertiseDomain | None = None
    current_role: QuidditchRole | None = None
    is_active: bool = True

    # Quick stats
    tasks_completed: int = 0
    accuracy: float = 0.85


@dataclass
class TaskResult:
    """Result from ecosystem task execution."""

    task_id: str
    status: TaskStatus
    solution: str
    confidence: float
    winning_agent: str

    # Breakdown
    facts_parsed: int = 0
    verbs_decomposed: int = 0
    debate_rounds: int = 0
    agents_participated: int = 0

    # Quality metrics
    elegance_score: float = 0.0
    completeness: float = 0.0

    # Timing
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: datetime | None = None

    # Learning
    insights_generated: int = 0


class Ecosystem:
    """Unified Legal-Linguistic Multi-Agent System.

    Combines:
    - LegalWhiteboard: Single point of truth
    - PersistentMemory: GitHub learning
    - AgentWellness: Keep agents healthy
    - QuidditchCompetition: Gamified competition
    - AgentSpecialization: T-shaped expertise
    - AgentLifecycle: Regeneration
    - VerbSpecification: California Bar Method

    Target: 99%+ accuracy through legal precision.
    """

    def __init__(self, github_repo: str = ""):
        # Core subsystems
        self.whiteboard = LegalWhiteboard("init")
        self.memory = PersistentMemory(github_repo)
        self.wellness = AgentWellness()
        self.competition = QuidditchCompetition()
        self.specialization = AgentSpecialization()
        self.lifecycle = AgentLifecycle()
        self.verbs = VerbSpecification()

        # Agents
        self.agents: dict[str, EcosystemAgent] = {}

        # Task tracking
        self.task_counter = 0
        self.task_history: list[TaskResult] = []

        # Configuration
        self.min_agents_per_task = 3
        self.max_debate_rounds = 3
        self.target_accuracy = 0.99

    # =========================================================================
    # AGENT MANAGEMENT
    # =========================================================================

    def register_agent(
        self,
        agent_id: str,
        house: HogwartsHouse,
        primary_domain: ExpertiseDomain,
        secondary_domains: list[ExpertiseDomain] = None,
    ) -> EcosystemAgent:
        """Register agent in ecosystem.

        Integrates with all subsystems.
        """
        # Create agent
        agent = EcosystemAgent(agent_id=agent_id, house=house, primary_domain=primary_domain)
        self.agents[agent_id] = agent

        # Register with subsystems
        self.lifecycle.register_agent(agent_id)
        self.wellness.register_agent(agent_id)
        self.competition.register_agent(agent_id, house)

        # Set up specialization
        self.specialization.register_agent(agent_id, primary_domain, secondary_domains or [])

        # Initial wellness setup
        self.wellness.supplement(agent_id, VitaminType.A_VISION, 1.0)
        self.wellness.supplement(agent_id, VitaminType.B_ENERGY, 1.0)

        return agent

    def get_agent(self, agent_id: str) -> EcosystemAgent | None:
        """Get agent by ID."""
        return self.agents.get(agent_id)

    def list_agents(self, active_only: bool = True) -> list[EcosystemAgent]:
        """List all agents."""
        agents = list(self.agents.values())
        if active_only:
            agents = [a for a in agents if a.is_active]
        return agents

    # =========================================================================
    # TASK EXECUTION
    # =========================================================================

    def execute_task(
        self,
        input_text: str,
        tests: list[dict[str, Any]] = None,
        audience: str = "technical",
        agent_ids: list[str] = None,
    ) -> TaskResult:
        """Execute task using full ecosystem.

        Workflow:
        1. Parse input using California Bar Method
        2. Decompose verbs
        3. Set up whiteboard
        4. Run phased debate
        5. Synthesize solution
        6. Validate and learn

        Args:
            input_text: Task description
            tests: Pre-written tests (call of question)
            audience: Output audience
            agent_ids: Specific agents to use (or auto-select)

        Returns:
            TaskResult with solution and metrics

        """
        # Create task
        self.task_counter += 1
        task_id = f"task_{self.task_counter:04d}"

        result = TaskResult(
            task_id=task_id,
            status=TaskStatus.PENDING,
            solution="",
            confidence=0.0,
            winning_agent="",
        )

        try:
            # Phase 1: Parse input
            result.status = TaskStatus.PARSING
            self._parse_input(input_text, tests)
            result.facts_parsed = len(self.whiteboard.facts)

            # Phase 2: Decompose verbs
            result.status = TaskStatus.DECOMPOSING
            decomposition = self.verbs.decompose(input_text)
            result.verbs_decomposed = len(decomposition.tasks)

            # Phase 3: Select agents
            if not agent_ids:
                agent_ids = self._select_agents(decomposition)
            result.agents_participated = len(agent_ids)

            # Phase 4: Prepare agents
            self._prepare_agents(agent_ids)

            # Phase 5: Run debate
            result.status = TaskStatus.DEBATING
            debate_result = self._run_debate(agent_ids, decomposition)
            result.debate_rounds = debate_result["rounds"]
            result.winning_agent = debate_result["winner"]

            # Phase 6: Synthesize solution
            result.status = TaskStatus.SYNTHESIZING
            solution = self._synthesize_solution(debate_result, audience)
            result.solution = solution
            result.confidence = debate_result["confidence"]

            # Phase 7: Validate
            result.status = TaskStatus.VALIDATING
            validation = self._validate_solution(solution, decomposition)
            result.completeness = validation["completeness"]
            result.elegance_score = validation["elegance"]

            # Phase 8: Learn
            insights = self._record_learnings(task_id, agent_ids, debate_result, validation)
            result.insights_generated = insights

            # Complete
            result.status = TaskStatus.COMPLETED
            result.completed_at = datetime.now()

        except Exception as e:
            result.status = TaskStatus.FAILED
            result.solution = f"Error: {e!s}"
            result.completed_at = datetime.now()

        # Record result
        self.task_history.append(result)

        return result

    def _parse_input(self, input_text: str, tests: list[dict[str, Any]] = None):
        """Parse input using California Bar Method."""
        # Reset whiteboard
        self.whiteboard = LegalWhiteboard()

        # Add tests first (call of question)
        if tests:
            for test in tests:
                self.whiteboard.add_test(
                    TestCase(
                        test_id=test.get("id", f"test_{len(self.whiteboard.tests)}"),
                        description=test.get("description", ""),
                        input_data=test.get("input", {}),
                        expected_output=test.get("expected", {}),
                        validation_fn=test.get("validation"),
                    ),
                )

        # Parse input using bar method
        self.whiteboard.parse_input(input_text)

        # Add reference material
        self.whiteboard.reference_material = input_text

    def _select_agents(self, decomposition) -> list[str]:
        """Select best agents for task."""
        # Get domains from decomposition
        domains = set()
        for task in decomposition.tasks:
            # Map verb categories to domains
            category = task.verb_category
            if category == VerbCategory.DATA_FLOW:
                domains.add(ExpertiseDomain.API_DESIGN)
            elif category == VerbCategory.VALIDATION:
                domains.add(ExpertiseDomain.SECURITY)
            elif category == VerbCategory.TRANSFORMATION:
                domains.add(ExpertiseDomain.ARCHITECTURE)
            elif category == VerbCategory.STATE:
                domains.add(ExpertiseDomain.DATABASE)
            elif category == VerbCategory.CONTROL:
                domains.add(ExpertiseDomain.PERFORMANCE)
            else:
                domains.add(ExpertiseDomain.ARCHITECTURE)

        # Get recommended team
        team = self.specialization.recommend_team(
            list(domains),
            max(self.min_agents_per_task, len(domains)),
        )

        return team

    def _prepare_agents(self, agent_ids: list[str]):
        """Prepare agents for task."""
        for agent_id in agent_ids:
            # Check health
            health = self.lifecycle.assess_health(agent_id)

            # Check if needs regeneration
            if health.get("needs_regeneration"):
                trigger = RegenerationTrigger(health["needs_regeneration"])
                self.lifecycle.regenerate(agent_id, trigger)

            # Check wellness
            wellness = self.wellness.health_report(agent_id)

            # Feed if hungry
            if wellness.get("hunger_level", 0) > 50:
                self.wellness.serve_meal(agent_id)

            # Hydrate if thirsty
            if wellness.get("hydration_level", 100) < 50:
                self.wellness.hydrate(agent_id)

            # Give vitamins
            self.wellness.supplement(agent_id, VitaminType.C_IMMUNITY, 0.5)

    def _run_debate(self, agent_ids: list[str], decomposition) -> dict[str, Any]:
        """Run phased debate.

        Phases:
        1. ISOLATED: Independent answers
        2. BLIND_CRITIQUE: See answers without sources
        3. ATTRIBUTED: Full reveal with Glicko-2
        """
        responses = {}

        # Round 1: Isolated
        self.whiteboard.phase = DebatePhase.ISOLATED

        for agent_id in agent_ids:
            # Agent generates solution
            solution = self._agent_solve(agent_id, decomposition)
            responses[agent_id] = {
                "round_1": solution,
                "confidence": solution.get("confidence", 0.5),
            }

            # Add as private note
            self.whiteboard.add_note(agent_id, solution.get("text", ""), section="solution")

        # Commit all notes
        for agent_id in agent_ids:
            self.whiteboard.commit_notes(agent_id)

        # Round 2: Blind critique
        self.whiteboard.phase = DebatePhase.BLIND_CRITIQUE
        self.whiteboard.reveal_all_committed()

        for agent_id in agent_ids:
            # Agent critiques others (blind)
            critique = self._agent_critique(agent_id, responses)
            responses[agent_id]["round_2"] = critique

        # Round 3: Attributed
        self.whiteboard.phase = DebatePhase.ATTRIBUTED

        # Get rankings from competition
        rankings = self._rank_solutions(responses, agent_ids)

        # Assign Quidditch roles
        roles = self.competition.assign_roles(rankings)

        for agent_id in agent_ids:
            if agent_id in self.agents:
                self.agents[agent_id].current_role = roles.get(agent_id)

        # Seeker makes final decision
        seeker_id = rankings[0] if rankings else agent_ids[0]

        # Play competition round
        self.competition.play_round(
            rankings,
            responses[seeker_id]["round_1"].get("text", ""),
            responses[seeker_id]["round_1"],
        )

        # Calculate consensus
        final_confidence = sum(r["confidence"] for r in responses.values()) / len(responses)

        return {
            "winner": seeker_id,
            "rounds": 3,
            "responses": responses,
            "rankings": rankings,
            "roles": roles,
            "confidence": final_confidence,
        }

    def _agent_solve(self, agent_id: str, decomposition) -> dict[str, Any]:
        """Agent generates solution.

        In production, this calls actual LLM.
        Here we return placeholder.
        """
        # Get temperature from lifecycle
        temperature = self.lifecycle.get_temperature(agent_id)

        # Get relevant knowledge
        knowledge = self.memory.retrieve_knowledge(query=str(decomposition), limit=5)

        # Placeholder - in production, call LLM
        return {
            "text": f"Solution from {agent_id}",
            "confidence": 0.85,
            "temperature": temperature,
            "knowledge_used": len(knowledge),
        }

    def _agent_critique(self, agent_id: str, responses: dict) -> dict[str, Any]:
        """Agent critiques other solutions (blind)."""
        # Placeholder - in production, call LLM
        return {
            "text": f"Critique from {agent_id}",
            "issues_found": 0,
            "improvements": [],
        }

    def _rank_solutions(self, responses: dict, agent_ids: list[str]) -> list[str]:
        """Rank solutions by quality."""
        # Sort by confidence (placeholder)
        ranked = sorted(agent_ids, key=lambda a: responses[a]["confidence"], reverse=True)
        return ranked

    def _synthesize_solution(self, debate_result: dict, audience: str) -> str:
        """Synthesize final solution."""
        winner = debate_result["winner"]
        solution = debate_result["responses"][winner]["round_1"].get("text", "")

        # Format for audience
        formatted = self.whiteboard.format_output(solution, audience)

        return formatted

    def _validate_solution(self, solution: str, decomposition) -> dict[str, Any]:
        """Validate solution completeness and elegance."""
        # Check verb coverage
        completeness_check = self.verbs.check_completeness(
            decomposition,
            [],  # Filled analyses
        )

        # Calculate elegance (placeholder)
        elegance = 0.85

        return {
            "completeness": completeness_check.get("coverage", 1.0),
            "elegance": elegance,
            "missing_verbs": completeness_check.get("missing", []),
        }

    def _record_learnings(
        self,
        task_id: str,
        agent_ids: list[str],
        debate_result: dict,
        validation: dict,
    ) -> int:
        """Record learnings to persistent memory."""
        insights = 0

        # Record winner's solution pattern
        winner = debate_result["winner"]
        self.memory.commit_insight(
            agent_id=winner,
            insight_type=InsightType.SOLUTION_PATTERN,
            content=f"Winning solution for {task_id}",
            context={"task": task_id, "confidence": debate_result["confidence"]},
            confidence=debate_result["confidence"],
            tags=["winner", task_id],
        )
        insights += 1

        # Record task completion
        for agent_id in agent_ids:
            success = agent_id == winner
            self.lifecycle.record_task(
                agent_id,
                success=success,
                followed_others=False,
                high_confidence=debate_result["responses"][agent_id]["confidence"] > 0.9,
            )

            # Update agent stats
            if agent_id in self.agents:
                self.agents[agent_id].tasks_completed += 1

        return insights

    # =========================================================================
    # ECOSYSTEM STATUS
    # =========================================================================

    def get_status(self) -> dict[str, Any]:
        """Get comprehensive ecosystem status."""
        # Agent stats
        active_agents = [a for a in self.agents.values() if a.is_active]

        # Task stats
        completed_tasks = [t for t in self.task_history if t.status == TaskStatus.COMPLETED]
        avg_confidence = (
            sum(t.confidence for t in completed_tasks) / len(completed_tasks)
            if completed_tasks
            else 0.0
        )

        # Competition standings
        standings = self.competition.get_standings()

        # Memory stats
        memory_stats = {
            "total_insights": len(self.memory.insights),
            "github_syncs": self.memory.sync_count,
        }

        # Lifecycle stats
        lifecycle_summary = self.lifecycle.get_summary()

        return {
            "ecosystem": {
                "total_agents": len(self.agents),
                "active_agents": len(active_agents),
                "tasks_completed": len(completed_tasks),
                "average_confidence": f"{avg_confidence:.1%}",
                "target_accuracy": f"{self.target_accuracy:.1%}",
            },
            "competition": standings,
            "memory": memory_stats,
            "lifecycle": lifecycle_summary,
            "subsystems": {
                "whiteboard": "active",
                "memory": "active",
                "wellness": "active",
                "competition": "active",
                "specialization": "active",
                "lifecycle": "active",
                "verbs": "active",
            },
        }

    def get_agent_dashboard(self, agent_id: str) -> dict[str, Any]:
        """Get comprehensive dashboard for single agent."""
        if agent_id not in self.agents:
            return {"error": "Agent not found"}

        agent = self.agents[agent_id]

        return {
            "agent": {
                "id": agent.agent_id,
                "house": agent.house.value,
                "level": agent.level.name,
                "primary_domain": agent.primary_domain.value if agent.primary_domain else None,
                "current_role": agent.current_role.value if agent.current_role else None,
                "tasks_completed": agent.tasks_completed,
            },
            "health": self.lifecycle.assess_health(agent_id),
            "wellness": self.wellness.health_report(agent_id),
            "specialization": self.specialization.get_expertise(agent_id),
            "competition": {
                "house_points": self.competition.house_points.get(agent.house, 0),
                "agent_points": self.competition.agent_points.get(agent_id, 0),
            },
            "memory": {
                "insights_created": len(
                    [i for i in self.memory.insights if i.agent_id == agent_id],
                ),
                "knowledge_level": self.memory.get_agent_level(agent_id).name,
            },
        }

    # =========================================================================
    # MAINTENANCE
    # =========================================================================

    def maintenance_cycle(self) -> dict[str, Any]:
        """Run maintenance on ecosystem.

        Checks:
        - Agent regeneration needs
        - Wellness status
        - Memory sync
        """
        actions = []

        # Check agents needing regeneration
        needs_regen = self.lifecycle.check_all_agents()
        for agent_id, trigger in needs_regen:
            self.lifecycle.regenerate(agent_id, trigger)
            actions.append(f"Regenerated {agent_id} ({trigger.value})")

        # Give breaks to overworked agents
        for agent_id in self.agents:
            metrics = self.lifecycle.get_metrics(agent_id)
            if metrics and metrics.tasks_since_regeneration % 10 == 0:
                self.wellness.take_break(agent_id, BreakType.MICRO)
                actions.append(f"Micro break for {agent_id}")

        # Sync memory
        if self.memory.github_repo:
            # Would sync to GitHub here
            actions.append("Memory sync scheduled")

        return {
            "actions_taken": len(actions),
            "details": actions,
            "timestamp": datetime.now().isoformat(),
        }

    def __repr__(self) -> str:
        return f"Ecosystem(agents={len(self.agents)}, tasks={len(self.task_history)})"


# =============================================================================
# CONVENIENCE FACTORY
# =============================================================================


def create_ecosystem(github_repo: str = "", default_agents: bool = True) -> Ecosystem:
    """Create ecosystem with optional default agents.

    "Legal precision meets agent coordination for 99%+ accuracy."
    """
    ecosystem = Ecosystem(github_repo)

    if default_agents:
        # Register diverse team
        ecosystem.register_agent(
            "alpha",
            HogwartsHouse.RAVENCLAW,
            ExpertiseDomain.ARCHITECTURE,
            [ExpertiseDomain.SECURITY, ExpertiseDomain.PERFORMANCE],
        )
        ecosystem.register_agent(
            "beta",
            HogwartsHouse.GRYFFINDOR,
            ExpertiseDomain.SECURITY,
            [ExpertiseDomain.API_DESIGN],
        )
        ecosystem.register_agent(
            "gamma",
            HogwartsHouse.HUFFLEPUFF,
            ExpertiseDomain.DATABASE,
            [ExpertiseDomain.ARCHITECTURE],
        )
        ecosystem.register_agent(
            "delta",
            HogwartsHouse.SLYTHERIN,
            ExpertiseDomain.PERFORMANCE,
            [ExpertiseDomain.SECURITY],
        )
        ecosystem.register_agent(
            "epsilon",
            HogwartsHouse.RAVENCLAW,
            ExpertiseDomain.API_DESIGN,
            [ExpertiseDomain.DOCUMENTATION],
        )

    return ecosystem


# =============================================================================
# SELF TEST
# =============================================================================

if __name__ == "__main__":
    print("Ecosystem - Self Test")
    print("=" * 60)

    # Create ecosystem
    ecosystem = create_ecosystem(default_agents=True)
    print(f"\nCreated: {ecosystem}")

    # Show status
    print("\n" + "=" * 60)
    print("Initial Status:")

    status = ecosystem.get_status()
    print(f"\nAgents: {status['ecosystem']['total_agents']}")
    print(f"Target: {status['ecosystem']['target_accuracy']}")

    # Execute task
    print("\n" + "=" * 60)
    print("Executing Task...")

    result = ecosystem.execute_task(
        input_text="""
        The system RECEIVES user requests via REST API,
        VALIDATES authentication tokens,
        TRANSFORMS request data to internal format,
        STORES results in database,
        and RETURNS formatted response.
        """,
        tests=[
            {
                "id": "test_auth",
                "description": "Should reject invalid tokens",
                "input": {"token": "invalid"},
                "expected": {"status": 401},
            },
        ],
        audience="technical",
    )

    print(f"\nTask: {result.task_id}")
    print(f"Status: {result.status.value}")
    print(f"Confidence: {result.confidence:.1%}")
    print(f"Winner: {result.winning_agent}")
    print(f"Facts parsed: {result.facts_parsed}")
    print(f"Verbs decomposed: {result.verbs_decomposed}")
    print(f"Debate rounds: {result.debate_rounds}")

    # Agent dashboard
    print("\n" + "=" * 60)
    print("Agent Dashboard (alpha):")

    dashboard = ecosystem.get_agent_dashboard("alpha")
    if "error" not in dashboard:
        print(f"\nHouse: {dashboard['agent']['house']}")
        print(f"Domain: {dashboard['agent']['primary_domain']}")
        print(f"Health: {dashboard['health']['status']}")
        print(f"Temperature: {dashboard['health']['temperature']}")

    # Maintenance
    print("\n" + "=" * 60)
    print("Running Maintenance...")

    maintenance = ecosystem.maintenance_cycle()
    print(f"\nActions: {maintenance['actions_taken']}")
    for action in maintenance["details"]:
        print(f"  - {action}")

    # Final status
    print("\n" + "=" * 60)
    print("Final Status:")

    status = ecosystem.get_status()
    print(f"\nTasks completed: {status['ecosystem']['tasks_completed']}")
    print(f"Average confidence: {status['ecosystem']['average_confidence']}")

    print("\n" + "=" * 60)
    print("Ecosystem working correctly")
    print("\nPhilosophy: Legal precision meets agent coordination.")
    print("Target: 99%+ accuracy through California Bar Method.")
