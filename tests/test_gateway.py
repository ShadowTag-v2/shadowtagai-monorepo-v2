"""
Test Suite for Governance Gateway

Comprehensive tests for routing, risk assessment, and decision-making.
"""

import pytest
from datetime import datetime
from src.gateway.models import (
    GovernanceRequest,
    RiskLevel,
    DecisionPath,
    DecisionOutcome,
)
from src.gateway.risk_classifier import ATP519RiskClassifier
from src.gateway.router import GovernanceRouter


class TestATP519RiskClassifier:
    """Test ATP 5-19 risk classification"""

    def test_high_value_deletion_is_high_risk(self):
        """High-value deletion should be classified as high risk"""
        request = GovernanceRequest(
            request_id="test_001",
            user_id="user_123",
            action="delete_production_data",
            resource={"type": "database"},
            financial_value=50000.00,
            source_system="test",
        )

        assessment = ATP519RiskClassifier.assess_risk(request)

        assert assessment.risk_level in [RiskLevel.EXTREMELY_HIGH, RiskLevel.HIGH]
        assert assessment.probability in ["A", "B"]  # Frequent/Likely
        assert assessment.severity in ["I", "II"]  # Catastrophic/Critical

    def test_low_value_approval_is_low_risk(self):
        """Low-value approval should be classified as low risk"""
        request = GovernanceRequest(
            request_id="test_002",
            user_id="user_123",
            action="approve_expense",
            resource={"type": "expense"},
            financial_value=500.00,
            source_system="test",
        )

        assessment = ATP519RiskClassifier.assess_risk(request)

        assert assessment.risk_level in [RiskLevel.LOW, RiskLevel.MEDIUM]
        assert len(assessment.hazards) > 0
        assert len(assessment.controls) > 0

    def test_read_only_action_is_low_risk(self):
        """Read-only actions should be low risk"""
        request = GovernanceRequest(
            request_id="test_003",
            user_id="user_123",
            action="read_data",
            resource={"type": "report"},
            source_system="test",
        )

        assessment = ATP519RiskClassifier.assess_risk(request)

        assert assessment.probability == "E"  # Unlikely
        assert assessment.risk_level == RiskLevel.LOW


class TestRoutingLogic:
    """Test request routing to fast/slow path"""

    def test_high_risk_routes_to_fast_path(self):
        """High risk should route to OPA fast path"""
        request = GovernanceRequest(
            request_id="test_004",
            user_id="user_123",
            action="grant_admin_access",
            resource={"type": "iam"},
            source_system="test",
        )

        classifier = ATP519RiskClassifier()
        assessment = classifier.assess_risk(request)
        path = classifier.determine_path(assessment)

        assert path == DecisionPath.FAST_PATH
        assert classifier.estimate_latency(path) < 10  # <10ms for fast path

    def test_medium_risk_routes_to_slow_path(self):
        """Medium risk should route to agent slow path"""
        request = GovernanceRequest(
            request_id="test_005",
            user_id="user_123",
            action="approve_expense",
            resource={"type": "expense"},
            financial_value=5000.00,
            source_system="test",
        )

        classifier = ATP519RiskClassifier()
        assessment = classifier.assess_risk(request)
        path = classifier.determine_path(assessment)

        assert path == DecisionPath.SLOW_PATH
        assert classifier.estimate_latency(path) >= 1000  # >=1s for slow path


@pytest.mark.asyncio
class TestGovernanceRouter:
    """Test end-to-end governance routing"""

    async def test_router_handles_valid_request(self):
        """Router should process valid request without errors"""
        router = GovernanceRouter(opa_client=None, agent_client=None)

        request = GovernanceRequest(
            request_id="test_006",
            user_id="user_123",
            action="approve_expense",
            resource={"type": "expense", "amount": 5000},
            context={"user_role": "engineer"},
            financial_value=5000.00,
            source_system="test",
        )

        routing_decision, response = await router.route_request(request)

        assert response.request_id == "test_006"
        assert response.outcome in [
            DecisionOutcome.APPROVED,
            DecisionOutcome.DENIED,
            DecisionOutcome.ESCALATED,
        ]
        assert 0 <= response.confidence <= 1
        assert len(response.reasoning) > 0
        assert response.latency_ms >= 0

    async def test_router_explains_routing(self):
        """Router should provide clear routing explanation"""
        router = GovernanceRouter(opa_client=None, agent_client=None)

        request = GovernanceRequest(
            request_id="test_007",
            user_id="user_123",
            action="delete_production_data",
            resource={"type": "database"},
            source_system="test",
        )

        routing_decision, _ = await router.route_request(request)

        assert routing_decision.path in [DecisionPath.FAST_PATH, DecisionPath.SLOW_PATH]
        assert len(routing_decision.reason) > 0
        assert routing_decision.estimated_latency_ms > 0


class TestModelValidation:
    """Test Pydantic model validation"""

    def test_governance_request_requires_essential_fields(self):
        """Request must have required fields"""
        with pytest.raises(ValueError):
            GovernanceRequest(
                request_id="test_008",
                # Missing user_id, action, resource
                source_system="test",
            )

    def test_empty_action_is_rejected(self):
        """Empty action should be rejected"""
        with pytest.raises(ValueError):
            GovernanceRequest(
                request_id="test_009",
                user_id="user_123",
                action="",  # Empty action
                resource={"type": "test"},
                source_system="test",
            )

    def test_financial_value_must_be_non_negative(self):
        """Financial value cannot be negative"""
        with pytest.raises(ValueError):
            GovernanceRequest(
                request_id="test_010",
                user_id="user_123",
                action="test_action",
                resource={"type": "test"},
                financial_value=-1000.00,  # Negative value
                source_system="test",
            )


class TestATPRiskMatrix:
    """Test ATP 5-19 risk matrix calculations"""

    def test_risk_matrix_coverage(self):
        """Verify all probability/severity combinations covered"""
        probabilities = ["A", "B", "C", "D", "E"]
        severities = ["I", "II", "III", "IV"]

        for prob in probabilities:
            for sev in severities:
                assert (
                    prob,
                    sev,
                ) in ATP519RiskClassifier.RISK_MATRIX, f"Missing risk matrix entry for {prob}/{sev}"

    def test_extremely_high_risk_cases(self):
        """Verify EH risk classification"""
        eh_cases = [("A", "I"), ("A", "II"), ("B", "I")]

        for prob, sev in eh_cases:
            assert ATP519RiskClassifier.RISK_MATRIX[(prob, sev)] == RiskLevel.EXTREMELY_HIGH

    def test_low_risk_cases(self):
        """Verify low risk classification"""
        low_cases = [("C", "IV"), ("D", "IV"), ("E", "III"), ("E", "IV")]

        for prob, sev in low_cases:
            assert ATP519RiskClassifier.RISK_MATRIX[(prob, sev)] == RiskLevel.LOW


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
