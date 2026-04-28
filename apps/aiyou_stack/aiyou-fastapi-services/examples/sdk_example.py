# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""FinJudge Python SDK - Usage Examples"""

from finjudge.client import FinJudgeClient, judge
from finjudge.models.judge import (
    Actor,
    ActorRole,
    DecisionContext,
    Exposure,
    Flags,
    JudgeRequest,
    Metrics,
    Objective,
    TailRisk,
    TimeHorizon,
)


def example_local_mode():
    """Example: Using embedded judge engine (local mode)"""
    print("=== Example 1: Local Mode (Embedded Judge) ===\n")

    # Create client
    client = FinJudgeClient(mode="local")

    # Create request
    request = JudgeRequest(
        decision_id="burn_rate_sdk_example",
        module="financial_runway_monitor",
        actor=Actor(role=ActorRole.CFO, org_unit="Finance", jurisdiction="US"),
        intent_nl="Hire 3 engineers, increasing burn from $180k to $240k/mo",
        context=DecisionContext(
            time_horizon=TimeHorizon.LONG_TERM,
            objective=Objective.ALPHA,
            constraints=["max_12mo_runway"],
        ),
        metrics=Metrics(
            exposure=Exposure(notional=720000.0, pct_aum=33.3, leverage_ratio=1.0),
            custom={
                "current_burn": 180000,
                "proposed_burn": 240000,
                "runway_months_proposed": 13.5,
            },
        ),
        flags=Flags(policy_flags=["approaching_12mo_runway_threshold"]),
    )

    # Judge
    ruling = client.judge(request)

    # Display results
    print(f"Decision ID: {ruling.decision_id}")
    print(f"Risk Level: {ruling.risk_matrix.risk_level.value}")
    print(f"Disposition: {ruling.recommendation.disposition.value}")
    print("\nSummary:")
    print(ruling.explanation_nl.short_summary)
    print("\nRequired Controls:")
    for control in ruling.recommendation.required_controls:
        print(f"  - {control}")


def example_remote_mode():
    """Example: Using remote API (requires API key)"""
    print("\n\n=== Example 2: Remote Mode (API) ===\n")

    # Note: Replace with your actual API URL and key
    # client = FinJudgeClient(
    #     mode="remote",
    #     api_url="https://api.finjudge.dev",
    #     api_key = "REDACTED_API_KEY"
    # )

    print("(Skipped - requires API credentials)")
    print("Usage:")
    print("""
    client = FinJudgeClient(
        mode="remote",
        api_url="https://api.finjudge.dev",
        api_key = "REDACTED_API_KEY"
    )
    ruling = client.judge(request)
    """)


def example_context_manager():
    """Example: Using context manager for auto-cleanup"""
    print("\n\n=== Example 3: Context Manager ===\n")

    with FinJudgeClient(mode="local") as client:
        request = JudgeRequest(
            decision_id="context_manager_example",
            module="trading_system",
            actor=Actor(role=ActorRole.TRADER, org_unit="Desk", jurisdiction="US"),
            intent_nl="Small SPY position",
            context=DecisionContext(time_horizon=TimeHorizon.LONG_TERM, objective=Objective.INCOME),
            metrics=Metrics(
                exposure=Exposure(notional=50000.0, pct_aum=1.0, leverage_ratio=1.0),
                tail_risk=TailRisk(var_95=5000.0),
            ),
        )

        ruling = client.judge(request)
        print(f"Risk Level: {ruling.risk_matrix.risk_level.value}")
        print(f"Disposition: {ruling.recommendation.disposition.value}")

    # Client automatically closed after context


def example_convenience_function():
    """Example: Using convenience function for quick judgments"""
    print("\n\n=== Example 4: Convenience Function ===\n")

    request = JudgeRequest(
        decision_id="convenience_example",
        module="test",
        actor=Actor(role=ActorRole.PM, org_unit="Test", jurisdiction="US"),
        intent_nl="Test decision",
        context=DecisionContext(time_horizon=TimeHorizon.SWING, objective=Objective.ALPHA),
        metrics=Metrics(exposure=Exposure(notional=100000.0, pct_aum=2.0)),
    )

    # One-liner judgment
    ruling = judge(request, mode="local")

    print(f"Risk: {ruling.risk_matrix.risk_level.value}")
    print(f"Disposition: {ruling.recommendation.disposition.value}")


def example_error_handling():
    """Example: Error handling"""
    print("\n\n=== Example 5: Error Handling ===\n")

    client = FinJudgeClient(mode="local")

    try:
        # Create invalid request (missing required fields)
        request = JudgeRequest(
            decision_id="invalid_example",
            module="test",
            actor=Actor(role=ActorRole.TRADER, org_unit="Test", jurisdiction="US"),
            intent_nl="Test",
            context=DecisionContext(time_horizon=TimeHorizon.SWING, objective=Objective.ALPHA),
            metrics=Metrics(),  # Empty metrics
        )

        ruling = client.judge(request)
        print(f"Ruling: {ruling.decision_id}")

    except ValueError as e:
        print(f"Validation error: {e!s}")
    except RuntimeError as e:
        print(f"Judge engine error: {e!s}")
    except Exception as e:
        print(f"Unexpected error: {e!s}")


if __name__ == "__main__":
    # Run all examples
    example_local_mode()
    example_remote_mode()
    example_context_manager()
    example_convenience_function()
    example_error_handling()

    print("\n\n=== All Examples Complete ===")
