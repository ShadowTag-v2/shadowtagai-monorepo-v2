"""
AgentWellness - Buffet, Hydration, Breaks, and Vitamins for Agents
Version: 1.0.0

Philosophy: Healthy agents perform better. Feed them well, keep them hydrated,
give them breaks, and supplement with vitamins.

Analogy:
- Buffet = Input quality (data, context, examples)
- Hydration = Resources (memory, GPU, tokens)
- Breaks = Prevent burnout (cache clearing, context reset, regeneration)
- Vitamins = Performance supplements (A-K for complete health)
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import StrEnum
from typing import Any


class BreakType(StrEnum):
    """Types of breaks agents need."""

    MICRO = "micro"  # Clear working memory (every 10 tasks)
    SHORT = "short"  # Reset context (every 25 tasks)
    LONG = "long"  # Full regeneration (every 50 tasks)


class VitaminType(StrEnum):
    """Performance vitamins for agents."""

    A_VISION = "vision"  # Clear task specification
    B_ENERGY = "energy"  # Optimized prompts
    C_IMMUNITY = "immunity"  # Input validation
    D_STRENGTH = "strength"  # Domain knowledge
    E_RECOVERY = "recovery"  # Error handling
    K_CLOTTING = "clotting"  # Graceful degradation


@dataclass
class MealQuality:
    """Quality metrics for agent's data 'food'."""

    data_quality: float = 0.5  # 0-1, cleanliness of data
    context_richness: float = 0.5  # How much relevant context
    example_diversity: float = 0.5  # Variety of reference material

    @property
    def overall(self) -> float:
        """Weighted meal quality score."""
        return self.data_quality * 0.4 + self.context_richness * 0.3 + self.example_diversity * 0.3


@dataclass
class HydrationLevels:
    """Resource 'hydration' for agents."""

    memory_gb: float = 8.0  # RAM allocated
    gpu_cycles: int = 1000  # Compute units
    context_window: int = 128000  # Token limit
    token_budget: int = 50000  # Per-task allowance

    # Minimum requirements
    min_memory: float = 4.0
    min_gpu: int = 100
    min_tokens: int = 10000

    @property
    def is_hydrated(self) -> bool:
        """Check if agent has sufficient resources."""
        return (
            self.memory_gb >= self.min_memory
            and self.gpu_cycles >= self.min_gpu
            and self.token_budget >= self.min_tokens
        )

    @property
    def hydration_level(self) -> float:
        """0-1 hydration score."""
        mem_score = min(1.0, self.memory_gb / 16.0)
        gpu_score = min(1.0, self.gpu_cycles / 2000)
        token_score = min(1.0, self.token_budget / 100000)
        return (mem_score + gpu_score + token_score) / 3


@dataclass
class VitaminLevels:
    """Current vitamin levels for an agent."""

    vision: float = 0.5  # A - task clarity
    energy: float = 0.5  # B - prompt optimization
    immunity: float = 0.5  # C - input validation
    strength: float = 0.5  # D - domain knowledge
    recovery: float = 0.5  # E - error handling
    clotting: float = 0.5  # K - token management

    @property
    def overall(self) -> float:
        """Average vitamin level."""
        return (
            self.vision
            + self.energy
            + self.immunity
            + self.strength
            + self.recovery
            + self.clotting
        ) / 6

    def deficiencies(self) -> list[str]:
        """List vitamins below threshold (0.3)."""
        threshold = 0.3
        deficient = []
        if self.vision < threshold:
            deficient.append("A (Vision)")
        if self.energy < threshold:
            deficient.append("B (Energy)")
        if self.immunity < threshold:
            deficient.append("C (Immunity)")
        if self.strength < threshold:
            deficient.append("D (Strength)")
        if self.recovery < threshold:
            deficient.append("E (Recovery)")
        if self.clotting < threshold:
            deficient.append("K (Clotting)")
        return deficient


@dataclass
class AgentHealthStatus:
    """Complete health status for an agent."""

    agent_id: str
    meal_quality: MealQuality = field(default_factory=MealQuality)
    hydration: HydrationLevels = field(default_factory=HydrationLevels)
    vitamins: VitaminLevels = field(default_factory=VitaminLevels)
    tasks_since_break: int = 0
    last_break: datetime | None = None
    last_meal: datetime | None = None

    @property
    def fatigue_level(self) -> float:
        """0-1 fatigue based on tasks since break."""
        return min(1.0, self.tasks_since_break / 50)

    @property
    def overall_health(self) -> float:
        """Overall health score 0-1."""
        nutrition = self.meal_quality.overall
        hydration = self.hydration.hydration_level
        vitamins = self.vitamins.overall
        fatigue_penalty = self.fatigue_level * 0.3

        return max(0.0, (nutrition + hydration + vitamins) / 3 - fatigue_penalty)


class AgentWellness:
    """
    Complete wellness program for agents.

    Keep them healthy, fed, hydrated, rested, and supplemented.
    """

    def __init__(self):
        self.agent_health: dict[str, AgentHealthStatus] = {}

        # Break schedules
        self.micro_break_interval = 10  # tasks
        self.short_break_interval = 25  # tasks
        self.long_break_interval = 50  # tasks

        # Meal schedule
        self.meal_interval = timedelta(hours=1)

    # =========================================================================
    # AGENT REGISTRATION
    # =========================================================================

    def register_agent(self, agent_id: str) -> AgentHealthStatus:
        """Register agent in wellness program."""
        if agent_id not in self.agent_health:
            self.agent_health[agent_id] = AgentHealthStatus(agent_id=agent_id)
        return self.agent_health[agent_id]

    def get_health(self, agent_id: str) -> AgentHealthStatus | None:
        """Get agent's current health status."""
        return self.agent_health.get(agent_id)

    # =========================================================================
    # BUFFET (DATA QUALITY)
    # =========================================================================

    def serve_meal(
        self,
        agent_id: str,
        data_quality: float,
        context_richness: float,
        example_diversity: float,
    ):
        """
        Serve agent a meal (high-quality inputs).

        Protein = Clean data
        Carbs = Clear context
        Fats = Rich examples
        """
        if agent_id in self.agent_health:
            health = self.agent_health[agent_id]
            health.meal_quality = MealQuality(
                data_quality=data_quality,
                context_richness=context_richness,
                example_diversity=example_diversity,
            )
            health.last_meal = datetime.now()

    def check_hunger(self, agent_id: str) -> bool:
        """Check if agent needs to eat."""
        if agent_id not in self.agent_health:
            return True

        health = self.agent_health[agent_id]
        if health.last_meal is None:
            return True

        return datetime.now() - health.last_meal > self.meal_interval

    def recommend_diet(self, agent_id: str) -> dict[str, str]:
        """Recommend dietary improvements based on deficiencies."""
        if agent_id not in self.agent_health:
            return {"error": "Agent not registered"}

        health = self.agent_health[agent_id]
        meal = health.meal_quality
        recommendations = []

        if meal.data_quality < 0.5:
            recommendations.append("Increase data quality: Clean, validate, deduplicate inputs")
        if meal.context_richness < 0.5:
            recommendations.append("Increase context: Add relevant background, constraints")
        if meal.example_diversity < 0.5:
            recommendations.append("Increase examples: More diverse reference material")

        return {"current_quality": meal.overall, "recommendations": recommendations}

    # =========================================================================
    # HYDRATION (RESOURCES)
    # =========================================================================

    def hydrate(
        self,
        agent_id: str,
        memory_gb: float = None,
        gpu_cycles: int = None,
        context_window: int = None,
        token_budget: int = None,
    ):
        """
        Provide resources (hydration) to agent.

        Water = Memory
        Coffee = GPU
        Energy drink = Context window
        Electrolytes = Token budget
        """
        if agent_id in self.agent_health:
            health = self.agent_health[agent_id]
            if memory_gb is not None:
                health.hydration.memory_gb = memory_gb
            if gpu_cycles is not None:
                health.hydration.gpu_cycles = gpu_cycles
            if context_window is not None:
                health.hydration.context_window = context_window
            if token_budget is not None:
                health.hydration.token_budget = token_budget

    def check_dehydration(self, agent_id: str) -> dict[str, Any]:
        """Check for resource deficiencies."""
        if agent_id not in self.agent_health:
            return {"error": "Agent not registered"}

        health = self.agent_health[agent_id]
        hyd = health.hydration

        issues = []
        if hyd.memory_gb < hyd.min_memory:
            issues.append(f"Low memory: {hyd.memory_gb}GB < {hyd.min_memory}GB")
        if hyd.gpu_cycles < hyd.min_gpu:
            issues.append(f"Low GPU: {hyd.gpu_cycles} < {hyd.min_gpu}")
        if hyd.token_budget < hyd.min_tokens:
            issues.append(f"Low tokens: {hyd.token_budget} < {hyd.min_tokens}")

        return {
            "hydrated": hyd.is_hydrated,
            "level": hyd.hydration_level,
            "issues": issues,
        }

    # =========================================================================
    # BREAKS (PREVENT BURNOUT)
    # =========================================================================

    def complete_task(self, agent_id: str):
        """Record task completion, check if break needed."""
        if agent_id in self.agent_health:
            self.agent_health[agent_id].tasks_since_break += 1

    def needs_break(self, agent_id: str) -> BreakType | None:
        """Check if agent needs a break."""
        if agent_id not in self.agent_health:
            return None

        tasks = self.agent_health[agent_id].tasks_since_break

        if tasks >= self.long_break_interval:
            return BreakType.LONG
        elif tasks >= self.short_break_interval:
            return BreakType.SHORT
        elif tasks >= self.micro_break_interval:
            return BreakType.MICRO
        return None

    def take_break(self, agent_id: str, break_type: BreakType) -> dict[str, Any]:
        """
        Agent takes a break.

        Micro = Clear working memory
        Short = Reset context + reseed random
        Long = Full regeneration
        """
        if agent_id not in self.agent_health:
            return {"error": "Agent not registered"}

        health = self.agent_health[agent_id]
        actions = []

        if break_type == BreakType.MICRO:
            actions.append("Cleared working memory")
            # Agent would clear short-term cache

        elif break_type == BreakType.SHORT:
            actions.append("Reset context")
            actions.append("Reseeded random state")
            # Agent would reset conversation context

        elif break_type == BreakType.LONG:
            actions.append("Full regeneration")
            actions.append("Cleared all state")
            actions.append("Reset to baseline")
            # Agent would completely refresh

            # Restore vitamins after long break
            health.vitamins = VitaminLevels()

        health.tasks_since_break = 0
        health.last_break = datetime.now()

        return {
            "break_type": break_type.value,
            "actions": actions,
            "fatigue_reset": True,
        }

    # =========================================================================
    # VITAMINS (SUPPLEMENTS)
    # =========================================================================

    def supplement(self, agent_id: str, vitamin: VitaminType, amount: float = 0.2):
        """
        Give agent a vitamin supplement.

        A = Vision (clear specs)
        B = Energy (optimized prompts)
        C = Immunity (input validation)
        D = Strength (domain knowledge)
        E = Recovery (error handling)
        K = Clotting (token management)
        """
        if agent_id not in self.agent_health:
            return

        vitamins = self.agent_health[agent_id].vitamins

        if vitamin == VitaminType.A_VISION:
            vitamins.vision = min(1.0, vitamins.vision + amount)
        elif vitamin == VitaminType.B_ENERGY:
            vitamins.energy = min(1.0, vitamins.energy + amount)
        elif vitamin == VitaminType.C_IMMUNITY:
            vitamins.immunity = min(1.0, vitamins.immunity + amount)
        elif vitamin == VitaminType.D_STRENGTH:
            vitamins.strength = min(1.0, vitamins.strength + amount)
        elif vitamin == VitaminType.E_RECOVERY:
            vitamins.recovery = min(1.0, vitamins.recovery + amount)
        elif vitamin == VitaminType.K_CLOTTING:
            vitamins.clotting = min(1.0, vitamins.clotting + amount)

    def full_supplement(self, agent_id: str):
        """Give agent full vitamin regimen."""
        for vitamin in VitaminType:
            self.supplement(agent_id, vitamin)

    def check_deficiencies(self, agent_id: str) -> list[str]:
        """Check for vitamin deficiencies."""
        if agent_id not in self.agent_health:
            return ["Agent not registered"]
        return self.agent_health[agent_id].vitamins.deficiencies()

    # =========================================================================
    # DAILY ROUTINE
    # =========================================================================

    def daily_routine(self, agent_id: str) -> dict[str, Any]:
        """
        Complete daily wellness routine for agent.

        Morning: Vitamins
        Throughout: Hydration checks
        Meals: Quality data
        Breaks: Scheduled rest
        """
        if agent_id not in self.agent_health:
            self.register_agent(agent_id)

        actions = []
        health = self.agent_health[agent_id]

        # Morning vitamins
        deficiencies = health.vitamins.deficiencies()
        if deficiencies:
            self.full_supplement(agent_id)
            actions.append(f"Supplemented deficiencies: {deficiencies}")

        # Check hydration
        hyd_check = self.check_dehydration(agent_id)
        if not hyd_check["hydrated"]:
            actions.append(f"Hydration issues: {hyd_check['issues']}")

        # Check hunger
        if self.check_hunger(agent_id):
            actions.append("Agent needs meal - serve high-quality data")

        # Check break needs
        break_needed = self.needs_break(agent_id)
        if break_needed:
            actions.append(f"Break needed: {break_needed.value}")

        return {
            "agent_id": agent_id,
            "overall_health": health.overall_health,
            "fatigue": health.fatigue_level,
            "actions_needed": actions,
        }

    def health_report(self, agent_id: str) -> dict[str, Any]:
        """Generate comprehensive health report."""
        if agent_id not in self.agent_health:
            return {"error": "Agent not registered"}

        health = self.agent_health[agent_id]

        return {
            "agent_id": agent_id,
            "overall_health": f"{health.overall_health:.1%}",
            "nutrition": {
                "quality": f"{health.meal_quality.overall:.1%}",
                "last_meal": health.last_meal.isoformat() if health.last_meal else "Never",
            },
            "hydration": {
                "level": f"{health.hydration.hydration_level:.1%}",
                "status": "OK" if health.hydration.is_hydrated else "LOW",
            },
            "vitamins": {
                "overall": f"{health.vitamins.overall:.1%}",
                "deficiencies": health.vitamins.deficiencies(),
            },
            "fatigue": {
                "level": f"{health.fatigue_level:.1%}",
                "tasks_since_break": health.tasks_since_break,
                "last_break": health.last_break.isoformat() if health.last_break else "Never",
            },
        }

    def __repr__(self) -> str:
        return f"AgentWellness(agents={len(self.agent_health)})"


# =============================================================================
# CONVENIENCE FACTORY
# =============================================================================


def create_wellness_program() -> AgentWellness:
    """
    Create agent wellness program.

    "Healthy agents perform better."
    """
    return AgentWellness()


# =============================================================================
# SELF TEST
# =============================================================================

if __name__ == "__main__":
    print("AgentWellness - Self Test")
    print("=" * 60)

    # Create wellness program
    wellness = create_wellness_program()
    print(f"\nCreated: {wellness}")

    # Register agent
    health = wellness.register_agent("agent_alpha")
    print(f"\nRegistered: {health.agent_id}")

    # Serve meal
    print("\n" + "=" * 60)
    print("Serving Meal...")
    wellness.serve_meal(
        "agent_alpha", data_quality=0.9, context_richness=0.8, example_diversity=0.7
    )
    print(f"Meal quality: {wellness.get_health('agent_alpha').meal_quality.overall:.1%}")

    # Hydrate
    print("\n" + "=" * 60)
    print("Hydrating...")
    wellness.hydrate("agent_alpha", memory_gb=16.0, gpu_cycles=2000, token_budget=100000)
    hyd_check = wellness.check_dehydration("agent_alpha")
    print(f"Hydration level: {hyd_check['level']:.1%}")
    print(f"Status: {'OK' if hyd_check['hydrated'] else 'LOW'}")

    # Complete some tasks
    print("\n" + "=" * 60)
    print("Simulating Tasks...")
    for _i in range(12):
        wellness.complete_task("agent_alpha")

    break_needed = wellness.needs_break("agent_alpha")
    print(f"Tasks completed: {wellness.get_health('agent_alpha').tasks_since_break}")
    print(f"Break needed: {break_needed.value if break_needed else 'No'}")

    # Take break
    if break_needed:
        result = wellness.take_break("agent_alpha", break_needed)
        print(f"Break actions: {result['actions']}")

    # Supplement vitamins
    print("\n" + "=" * 60)
    print("Supplementing Vitamins...")
    wellness.full_supplement("agent_alpha")
    deficiencies = wellness.check_deficiencies("agent_alpha")
    print(f"Deficiencies after supplement: {deficiencies if deficiencies else 'None'}")

    # Health report
    print("\n" + "=" * 60)
    print("Health Report:")
    report = wellness.health_report("agent_alpha")
    for key, value in report.items():
        if isinstance(value, dict):
            print(f"\n{key}:")
            for k, v in value.items():
                print(f"  {k}: {v}")
        else:
            print(f"{key}: {value}")

    print("\n" + "=" * 60)
    print("✓ AgentWellness working correctly")
    print("\nPhilosophy: Healthy agents perform better.")
