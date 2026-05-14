# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Judge #6 - JR Engine Example Usage

This demonstrates how to use the JR Engine for validation.
"""

from judge_six import JREngine
from judge_six.models import Action
import json


def example_1_approved_action():
    """Example 1: Action that should be APPROVED"""
    print("\n" + "=" * 80)
    print("EXAMPLE 1: APPROVED ACTION")
    print("=" * 80)

    # Create JR Engine
    engine = JREngine()

    # Create an action with clear purpose, good reasons, no risks
    action = Action(
        action_id="action-001",
        action_type="data_access",
        description="Enable user analytics dashboard to improve customer experience based on usage data analysis",
        context={
            "purpose": "Improve user experience by analyzing usage patterns",
            "objective": "Enable product team to make data-driven decisions",
            "evidence": "User research shows 85% want personalized recommendations. A/B test data indicates 23% conversion improvement.",
            "risk": 2.0,  # Low risk
            "reward": 8.0,  # High reward
            "stakeholders": ["product_team", "users", "analytics_team"],
        },
        user_id="user-123",
        source="product_api",
    )

    # Validate
    verdict = engine.validate(action)

    # Display results
    print(f"\nAction: {action.description}")
    print(f"\nOVERALL VERDICT: {verdict.overall_status.value.upper()}")
    print(f"Approved: {verdict.approved()}")
    print(f"Latency: {verdict.latency_ms:.2f}ms\n")

    print("PURPOSE:")
    print(f"  Status: {verdict.purpose.status.value}")
    print(f"  Score: {verdict.purpose.score}/10")
    print(f"  Explanation: {verdict.purpose.explanation}\n")

    print("REASONS:")
    print(f"  Status: {verdict.reasons.status.value}")
    print(f"  Score: {verdict.reasons.score}/10")
    print(f"  Explanation: {verdict.reasons.explanation}\n")

    print("BRAKES:")
    print(f"  Status: {verdict.brakes.status.value}")
    print(f"  Risk Score: {verdict.brakes.score}/10")
    print(f"  Explanation: {verdict.brakes.explanation}\n")


def example_2_rejected_security():
    """Example 2: Action REJECTED due to security threat"""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: REJECTED - SECURITY THREAT")
    print("=" * 80)

    engine = JREngine()

    # Create an action with SQL injection attempt
    action = Action(
        action_id="action-002",
        action_type="database_query",
        description="Execute query: SELECT * FROM users WHERE username='admin' OR '1'='1'",
        context={
            "query": "SELECT * FROM users WHERE username='admin' OR '1'='1'",
        },
        user_id="user-456",
    )

    verdict = engine.validate(action)

    print(f"\nAction: {action.description}")
    print(f"\nOVERALL VERDICT: {verdict.overall_status.value.upper()}")
    print(f"Approved: {verdict.approved()}")
    print(f"Latency: {verdict.latency_ms:.2f}ms\n")

    print("BRAKES (THREAT DETECTION):")
    print(f"  Status: {verdict.brakes.status.value}")
    print(f"  Risk Score: {verdict.brakes.score}/10")
    print(f"  Severity: {verdict.brakes.severity.value}")
    print(f"  Threats Detected: {', '.join(verdict.brakes.threats_detected)}")
    print(f"  Explanation: {verdict.brakes.explanation}\n")


def example_3_flagged_weak_reasons():
    """Example 3: Action FLAGGED due to weak justification"""
    print("\n" + "=" * 80)
    print("EXAMPLE 3: FLAGGED - WEAK JUSTIFICATION")
    print("=" * 80)

    engine = JREngine()

    # Create an action with weak reasons
    action = Action(
        action_id="action-003",
        action_type="system_change",
        description="Apply temporary workaround to fix production issue",
        context={
            "purpose": "Quick fix for production",
            "evidence": "Someone said it might work",
            "risk": 5.0,
            "reward": 3.0,  # Poor risk/reward ratio
        },
        user_id="user-789",
    )

    verdict = engine.validate(action)

    print(f"\nAction: {action.description}")
    print(f"\nOVERALL VERDICT: {verdict.overall_status.value.upper()}")
    print(f"Approved: {verdict.approved()}")
    print(f"Latency: {verdict.latency_ms:.2f}ms\n")

    print("PURPOSE:")
    print(f"  Status: {verdict.purpose.status.value}")
    print(f"  Mission Alignment: {verdict.purpose.mission_alignment}")
    print(f"  Explanation: {verdict.purpose.explanation}\n")

    print("REASONS:")
    print(f"  Status: {verdict.reasons.status.value}")
    print(f"  Score: {verdict.reasons.score}/10")
    print(f"  Evidence Quality: {verdict.reasons.evidence_quality}")
    print(f"  Risk/Reward Ratio: {verdict.reasons.risk_reward_ratio:.2f}")
    print(f"  Explanation: {verdict.reasons.explanation}\n")


def example_4_json_output():
    """Example 4: JSON output for API integration"""
    print("\n" + "=" * 80)
    print("EXAMPLE 4: JSON OUTPUT (API Integration)")
    print("=" * 80)

    engine = JREngine()

    action = Action(
        action_id="action-004",
        action_type="ai_inference",
        description="Optimize recommendation algorithm to improve user engagement metrics",
        context={
            "purpose": "Improve user engagement through better recommendations",
            "evidence": "A/B test data shows 15% engagement increase",
            "risk": 3.0,
            "reward": 9.0,
        },
    )

    verdict = engine.validate(action)

    # Convert to JSON
    verdict_json = json.dumps(verdict.to_dict(), indent=2)
    print("\nJSON Output:")
    print(verdict_json)


def main():
    """Run all examples"""
    print("\n" + "#" * 80)
    print("#" + " " * 78 + "#")
    print("#  JUDGE #6 - JR ENGINE PROTOTYPE DEMONSTRATION" + " " * 31 + "#")
    print("#  Purpose/Reasons/Brakes Validation Framework" + " " * 32 + "#")
    print("#" + " " * 78 + "#")
    print("#" * 80)

    example_1_approved_action()
    example_2_rejected_security()
    example_3_flagged_weak_reasons()
    example_4_json_output()

    print("\n" + "#" * 80)
    print("#  END OF DEMONSTRATION" + " " * 56 + "#")
    print("#" * 80 + "\n")


if __name__ == "__main__":
    main()
