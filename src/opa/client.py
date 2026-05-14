# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Open Policy Agent (OPA) Client

Fast-path enforcement: deterministic, sub-millisecond decisions.
When speed matters and rules are clear, OPA is the answer.
"""

import httpx
import logging
from typing import Any
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class OPAClient:
    """
    OPA Policy Engine Client.

    Connects to OPA server for deterministic policy decisions.
    <10ms latency for critical path enforcement.
    """

    def __init__(
        self,
        opa_url: str = "http://opa:8181",
        timeout: float = 0.1,  # 100ms timeout (generous for <10ms target)
    ):
        """
        Initialize OPA client.

        Args:
            opa_url: OPA server base URL
            timeout: Request timeout in seconds
        """
        self.opa_url = opa_url.rstrip("/")
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)

    async def evaluate_policy(self, policy_path: str, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Evaluate OPA policy with input data.

        Args:
            policy_path: OPA policy path (e.g., "governance/approve")
            input_data: Input data for policy evaluation

        Returns:
            OPA decision result with allow/deny and metadata

        Raises:
            OPAException: If OPA evaluation fails
        """
        start_time = datetime.now(timezone.utc)

        try:
            url = f"{self.opa_url}/v1/data/{policy_path}"

            response = await self.client.post(url, json={"input": input_data}, headers={"Content-Type": "application/json"})

            response.raise_for_status()
            result = response.json()

            latency_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000

            logger.info(f"OPA policy evaluated: {policy_path} | Allow: {result.get('result', {}).get('allow', False)} | Latency: {latency_ms:.2f}ms")

            if latency_ms > 10:
                logger.warning(f"OPA latency exceeded 10ms target: {latency_ms:.2f}ms for {policy_path}")

            return result.get("result", {})

        except httpx.TimeoutException:
            logger.error(f"OPA timeout after {self.timeout}s for policy {policy_path}")
            raise OPAException(f"OPA request timeout: {policy_path}")

        except httpx.HTTPStatusError as e:
            logger.error(f"OPA HTTP error {e.response.status_code} for policy {policy_path}")
            raise OPAException(f"OPA HTTP error: {e.response.status_code}")

        except Exception as e:
            logger.error(f"OPA evaluation error for policy {policy_path}: {str(e)}")
            raise OPAException(f"OPA evaluation failed: {str(e)}")

    async def evaluate_governance(self, request_data: dict[str, Any]) -> dict[str, Any]:
        """
        Evaluate governance policy (convenience method).

        Args:
            request_data: Governance request data

        Returns:
            {
                "allow": bool,
                "reasons": List[str],
                "policies": List[str],
                "controls": List[str]
            }
        """
        result = await self.evaluate_policy("governance/decision", request_data)

        # Normalize OPA response
        return {
            "allow": result.get("allow", False),
            "reasons": result.get("reasons", []),
            "policies": result.get("applied_policies", []),
            "controls": result.get("required_controls", []),
        }

    async def check_health(self) -> bool:
        """
        Check if OPA server is healthy.

        Returns:
            True if healthy, False otherwise
        """
        try:
            response = await self.client.get(f"{self.opa_url}/health")
            return response.status_code == 200
        except Exception:
            return False

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

    async def __aenter__(self):
        """Async context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()


class OPAException(Exception):
    """OPA-specific exceptions"""

    pass


# ============================================================================
# OPA Policy Templates (Rego)
# ============================================================================

GOVERNANCE_POLICY_TEMPLATE = """
package governance

import future.keywords.if
import future.keywords.in

# Default deny
default allow := false

# Allow if all conditions met
allow if {
    not high_risk_action
    within_financial_limits
    has_required_approvals
    not blocked_user
}

# High-risk actions that require explicit approval
high_risk_actions := {
    "delete_production_data",
    "grant_admin_access",
    "modify_security_policy",
    "shutdown_service"
}

high_risk_action if {
    input.action in high_risk_actions
}

# Financial limits by user role
financial_limits := {
    "admin": 1000000,
    "manager": 100000,
    "engineer": 10000,
    "contractor": 1000
}

within_financial_limits if {
    not input.financial_value
}

within_financial_limits if {
    limit := financial_limits[input.user_role]
    input.financial_value <= limit
}

# Required approvals
has_required_approvals if {
    input.context.approver_id
    input.context.approver_id != input.user_id
}

# Blocked users
blocked_users := {"user_banned_001", "user_suspended_042"}

blocked_user if {
    input.user_id in blocked_users
}

# Reasoning for decision
reasons contains "Action within financial limits" if within_financial_limits
reasons contains "Required approvals present" if has_required_approvals
reasons contains "User not blocked" if not blocked_user
reasons contains "Not a high-risk action" if not high_risk_action

# Applied policies
applied_policies contains "POL-FIN-001" if within_financial_limits
applied_policies contains "POL-APP-002" if has_required_approvals

# Required controls
required_controls contains "Dual-person authorization" if {
    input.financial_value > 50000
}

required_controls contains "Manager approval" if {
    input.financial_value > 10000
    input.financial_value <= 50000
}
"""


def generate_opa_policy_file(output_path: str = "policies/governance.rego") -> None:
    """
    Generate OPA policy file.

    Usage:
        generate_opa_policy_file("policies/governance.rego")
    """
    with open(output_path, "w") as f:
        f.write(GOVERNANCE_POLICY_TEMPLATE.strip())

    logger.info(f"Generated OPA policy: {output_path}")
