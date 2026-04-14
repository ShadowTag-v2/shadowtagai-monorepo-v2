"""Pre-defined load testing scenarios
"""

from dataclasses import dataclass


@dataclass
class LoadTestScenario:
    """Load test scenario configuration"""

    name: str
    description: str
    users: int
    spawn_rate: int
    duration: int  # seconds
    user_class: str = "ShadowTag-v2User"
    host: str = "http://localhost:8000"


# Predefined scenarios
SCENARIOS = {
    "smoke": LoadTestScenario(
        name="Smoke Test",
        description="Quick sanity check with minimal load",
        users=10,
        spawn_rate=2,
        duration=30,
        user_class="QuickLoadUser",
    ),
    "light": LoadTestScenario(
        name="Light Load",
        description="Light load with 100 users",
        users=100,
        spawn_rate=10,
        duration=60,
        user_class="ShadowTag-v2User",
    ),
    "medium": LoadTestScenario(
        name="Medium Load",
        description="Medium load with 500 users",
        users=500,
        spawn_rate=25,
        duration=120,
        user_class="ShadowTag-v2User",
    ),
    "heavy": LoadTestScenario(
        name="Heavy Load",
        description="Heavy load with 1,000 users",
        users=1000,
        spawn_rate=50,
        duration=180,
        user_class="ShadowTag-v2User",
    ),
    "stress": LoadTestScenario(
        name="Stress Test",
        description="Stress test with 2,500 users",
        users=2500,
        spawn_rate=100,
        duration=300,
        user_class="StressTestUser",
    ),
    "spike": LoadTestScenario(
        name="Spike Test",
        description="Sudden spike to 5,000 users",
        users=5000,
        spawn_rate=500,
        duration=120,
        user_class="ShadowTag-v2User",
    ),
    "endurance": LoadTestScenario(
        name="Endurance Test",
        description="Long-running test with 500 users for 30 minutes",
        users=500,
        spawn_rate=25,
        duration=1800,
        user_class="ShadowTag-v2User",
    ),
    "breaking_point": LoadTestScenario(
        name="Breaking Point Test",
        description="Find breaking point - up to 10,000 users",
        users=10000,
        spawn_rate=100,
        duration=600,
        user_class="ShadowTag-v2User",
    ),
}


def get_scenario(scenario_name: str) -> LoadTestScenario | None:
    """Get a scenario by name"""
    return SCENARIOS.get(scenario_name)


def list_scenarios():
    """List all available scenarios"""
    return SCENARIOS
