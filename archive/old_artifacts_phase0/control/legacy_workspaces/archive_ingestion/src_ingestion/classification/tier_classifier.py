"""Tier classification engine for scenario prioritization"""


from ..models import Scenario, ScenarioTier


class TierClassifier:
    """
    Classifies scenarios into three tiers based on safety and complexity

    Tier 1 (Critical Safety): 25%+ target
    - Near-collisions (TTC < 2s)
    - Sensor failures
    - Adverse weather
    - Complex intersections
    - Vulnerable road users

    Tier 2 (High-Value Edge Cases): 40% target
    - Urban high-density driving
    - Highway merges
    - Novel objects
    - Degraded markings

    Tier 3 (Baseline Training): 35% target
    - Standard cruising
    - Clear weather
    - Low traffic
    """

    def __init__(self):
        self.tier_1_threshold = 80.0  # Final score ≥ 80
        self.tier_2_threshold = 50.0  # Final score ≥ 50

    def classify_batch(self, scenarios: list[Scenario]) -> list[Scenario]:
        """
        Classify a batch of scenarios

        Args:
            scenarios: Scenarios with calculated safety/complexity scores

        Returns:
            Scenarios with tier assignments
        """
        print(f"[Tier Classifier] Classifying {len(scenarios)} scenarios...")

        classified = []
        tier_1_count = 0
        tier_2_count = 0
        tier_3_count = 0

        for scenario in scenarios:
            # Calculate final score if not already set
            if scenario.final_score is None:
                scenario.final_score = (
                    0.6 * (scenario.safety_score or 50) +
                    0.4 * (scenario.complexity_score or 50)
                )

            # Classify based on thresholds
            if scenario.final_score >= self.tier_1_threshold:
                scenario.tier = ScenarioTier.TIER_1
                tier_1_count += 1
            elif scenario.final_score >= self.tier_2_threshold:
                scenario.tier = ScenarioTier.TIER_2
                tier_2_count += 1
            else:
                scenario.tier = ScenarioTier.TIER_3
                tier_3_count += 1

            classified.append(scenario)

        # Print distribution
        total = len(scenarios)
        print(f"[Tier Classifier] Tier 1: {tier_1_count} ({tier_1_count/total*100:.1f}%)")
        print(f"[Tier Classifier] Tier 2: {tier_2_count} ({tier_2_count/total*100:.1f}%)")
        print(f"[Tier Classifier] Tier 3: {tier_3_count} ({tier_3_count/total*100:.1f}%)")

        return classified


if __name__ == "__main__":
    from datetime import datetime

    from ..models import DataSource, SensorData, TimeOfDay, WeatherCondition

    # Test scenarios with different scores
    test_scenarios = [
        Scenario(
            scenario_id="high_safety",
            source=DataSource.FLEET_TELEMETRY,
            safety_score=95,
            complexity_score=85,
            duration_seconds=10.0,
            num_agents=5,
            weather_condition=WeatherCondition.RAIN,
            time_of_day=TimeOfDay.NIGHT,
            sensor_data=SensorData(timestamp=datetime.utcnow()),
            consent_verified=True,
            privacy_scrubbed=True
        ),
        Scenario(
            scenario_id="medium_case",
            source=DataSource.SIMULATION,
            safety_score=60,
            complexity_score=70,
            duration_seconds=15.0,
            num_agents=3,
            weather_condition=WeatherCondition.CLEAR,
            time_of_day=TimeOfDay.DAY,
            sensor_data=SensorData(timestamp=datetime.utcnow()),
            consent_verified=True,
            privacy_scrubbed=True
        ),
        Scenario(
            scenario_id="baseline",
            source=DataSource.SIMULATION,
            safety_score=30,
            complexity_score=25,
            duration_seconds=20.0,
            num_agents=1,
            weather_condition=WeatherCondition.CLEAR,
            time_of_day=TimeOfDay.DAY,
            sensor_data=SensorData(timestamp=datetime.utcnow()),
            consent_verified=True,
            privacy_scrubbed=True
        ),
    ]

    classifier = TierClassifier()
    classified = classifier.classify_batch(test_scenarios)

    for scenario in classified:
        print(f"{scenario.scenario_id}: Tier={scenario.tier}, Score={scenario.final_score:.1f}")
