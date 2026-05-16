# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Judge #6 - JR Engine Example Usage.

This demonstrates how to use the JR Engine for validation.
"""

import json

from judge_six import JREngine
from judge_six.models import Action


def example_1_approved_action():
  """Example 1: Action that should be APPROVED."""

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
  engine.validate(action)

  # Display results


def example_2_rejected_security():
  """Example 2: Action REJECTED due to security threat."""

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

  engine.validate(action)


def example_3_flagged_weak_reasons():
  """Example 3: Action FLAGGED due to weak justification."""

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

  engine.validate(action)


def example_4_json_output():
  """Example 4: JSON output for API integration."""

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
  json.dumps(verdict.to_dict(), indent=2)


def main():
  """Run all examples."""

  example_1_approved_action()
  example_2_rejected_security()
  example_3_flagged_weak_reasons()
  example_4_json_output()


if __name__ == "__main__":
  main()
