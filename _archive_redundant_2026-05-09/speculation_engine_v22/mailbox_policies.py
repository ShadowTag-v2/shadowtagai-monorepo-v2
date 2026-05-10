# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Pre-defined agent policies for the AgentMailbox.

Defines the security reviewer, cost analyst, and architecture board
agent roles with their approval policies for plan delegation.

Usage::

    from speculation_engine.mailbox_policies import (
        SECURITY_POLICY,
        COST_POLICY,
        ARCHITECTURE_BOARD_POLICY,
        create_full_review_policy,
    )

    mailbox = AgentMailbox(policy=SECURITY_POLICY)
"""

from __future__ import annotations

from speculation_engine.mailbox import ApprovalPolicy


# --- Individual Agent Policies ---

SECURITY_POLICY = ApprovalPolicy(
  required_agents=["security_reviewer"],
  optional_agents=["compliance_auditor"],
  timeout_seconds=60.0,
  require_unanimous=True,
)
"""Security-only review. Blocks on security_reviewer approval.
Used for plans that modify auth, secrets, or permissions."""

COST_POLICY = ApprovalPolicy(
  required_agents=["cost_analyst"],
  optional_agents=["billing_monitor"],
  timeout_seconds=90.0,
  require_unanimous=True,
)
"""Cost-only review. Blocks on cost_analyst approval.
Used for plans that modify infrastructure, scaling, or billing config."""

ARCHITECTURE_BOARD_POLICY = ApprovalPolicy(
  required_agents=["cto_reviewer", "dx_reviewer", "infra_reviewer"],
  optional_agents=["qa_reviewer", "ux_reviewer", "legal_reviewer"],
  timeout_seconds=180.0,
  require_unanimous=True,
)
"""Full architecture board review. Requires CTO, DX, and Infra approval.
Used for STATE B decisions: architecture shifts >3 packages."""


# --- Composite Policies ---


def create_full_review_policy(
  *,
  timeout_seconds: float = 120.0,
  require_unanimous: bool = True,
) -> ApprovalPolicy:
  """Create a policy requiring security + cost + architecture approval.

  Args:
      timeout_seconds: Maximum voting window.
      require_unanimous: Whether all required agents must approve.

  Returns:
      A composite ApprovalPolicy with all three agent roles.
  """
  return ApprovalPolicy(
    required_agents=["security_reviewer", "cost_analyst", "architecture_board"],
    optional_agents=["compliance_auditor", "billing_monitor"],
    timeout_seconds=timeout_seconds,
    require_unanimous=require_unanimous,
  )


def create_lightweight_policy(
  *,
  timeout_seconds: float = 30.0,
) -> ApprovalPolicy:
  """Create a lightweight policy for low-risk plan changes.

  Only requires a single reviewer (security) with short timeout.
  Used for STATE A operations that still benefit from a review gate.

  Args:
      timeout_seconds: Maximum voting window.

  Returns:
      A lightweight ApprovalPolicy.
  """
  return ApprovalPolicy(
    required_agents=["security_reviewer"],
    optional_agents=[],
    timeout_seconds=timeout_seconds,
    require_unanimous=True,
  )


# --- Policy Selection ---

POLICY_CATALOG: dict[str, ApprovalPolicy] = {
  "security": SECURITY_POLICY,
  "cost": COST_POLICY,
  "architecture_board": ARCHITECTURE_BOARD_POLICY,
  "full_review": create_full_review_policy(),
  "lightweight": create_lightweight_policy(),
}
"""Catalog of all available policies, indexed by name."""


def select_policy(plan_risk_level: str) -> ApprovalPolicy:
  """Select an appropriate approval policy based on risk level.

  Args:
      plan_risk_level: One of "low", "medium", "high", "critical".

  Returns:
      The appropriate ApprovalPolicy for the risk level.
  """
  mapping = {
    "low": POLICY_CATALOG["lightweight"],
    "medium": POLICY_CATALOG["security"],
    "high": POLICY_CATALOG["full_review"],
    "critical": POLICY_CATALOG["architecture_board"],
  }
  return mapping.get(plan_risk_level, POLICY_CATALOG["security"])
