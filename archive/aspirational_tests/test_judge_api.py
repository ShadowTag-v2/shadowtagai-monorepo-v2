"""
Integration tests for Judge #6 API
Tests FastAPI endpoints end-to-end
"""

import pytest
from fastapi.testclient import TestClient
from src.api.judges import app


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


class TestHealthEndpoints:
    """Test health and status endpoints"""

    def test_root_endpoint(self, client):
        """Test root endpoint returns service info"""
        response = client.get("/judges")

        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "Judge #6 HITL System"
        assert data["version"] == "1.0.0"
        assert "verticals" in data

    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/judges/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "checks" in data


class TestEvaluateEndpoint:
    """Test primary /judges/evaluate endpoint"""

    def test_evaluate_finjudge(self, client):
        """Test FinJudge evaluation via API"""
        request_data = {
            "request_id": "test_api_fin_001",
            "judge_type": "FinJudge",
            "action_type": "wire_transfer",
            "context": {"amount_usd": 75000, "vendor_status": "new", "purchase_order": None, "destination_country": "Unknown"},
            "requested_by": "test@example.com",
        }

        response = client.post("/judges/evaluate", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert data["request_id"] == "test_api_fin_001"
        assert data["decision"] in ["ALLOW", "BLOCK"]
        assert "risk_assessment" in data
        assert "approval_gate" in data
        assert "reasoning" in data
        assert "semantic_trail" in data
        assert "latency_ms" in data
        assert data["latency_ms"] > 0

    def test_evaluate_casejudge(self, client):
        """Test CaseJudge evaluation via API"""
        request_data = {
            "request_id": "test_api_case_001",
            "judge_type": "CaseJudge",
            "action_type": "case_acceptance",
            "context": {"case_value_usd": 500000, "case_type": "contract_dispute", "conflict_check_passed": False, "probability_of_success": 0.6},
            "requested_by": "test@example.com",
        }

        response = client.post("/judges/evaluate", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert data["decision"] == "BLOCK"  # Conflict check failed
        assert "conflict" in data["reasoning"].lower()

    def test_evaluate_lawjudge(self, client):
        """Test LawJudge evaluation via API"""
        request_data = {
            "request_id": "test_api_law_001",
            "judge_type": "LawJudge",
            "action_type": "compliance_check",
            "context": {"compliance_area": "eu_ai_act", "ai_system_type": "biometric_identification", "legal_review_completed": False},
            "requested_by": "test@example.com",
        }

        response = client.post("/judges/evaluate", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert data["decision"] == "BLOCK"  # High-risk AI without legal review
        assert data["risk_assessment"]["severity"] == "I"  # Catastrophic

    def test_evaluate_fraudjudge(self, client):
        """Test FraudJudge evaluation via API"""
        request_data = {
            "request_id": "test_api_fraud_001",
            "judge_type": "FraudJudge",
            "action_type": "payment_authorization",
            "context": {"fraud_score": 0.85, "identity_verified": False, "amount_usd": 5000},
            "requested_by": "test@example.com",
        }

        response = client.post("/judges/evaluate", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert data["decision"] == "BLOCK"  # High fraud score
        assert "fraud" in data["reasoning"].lower()

    def test_evaluate_invalid_judge_type(self, client):
        """Test error handling for invalid judge type"""
        request_data = {
            "request_id": "test_invalid",
            "judge_type": "InvalidJudge",
            "action_type": "test",
            "context": {},
            "requested_by": "test@example.com",
        }

        response = client.post("/judges/evaluate", json=request_data)

        assert response.status_code == 422  # Validation error

    def test_evaluate_missing_required_fields(self, client):
        """Test error handling for missing required fields"""
        request_data = {
            "request_id": "test_incomplete",
            "judge_type": "FinJudge",
            # Missing action_type, context, requested_by
        }

        response = client.post("/judges/evaluate", json=request_data)

        assert response.status_code == 422  # Validation error


class TestAuditEndpoints:
    """Test audit trail endpoints"""

    def test_get_audit_trail(self, client):
        """Test audit trail retrieval"""
        # First, create a decision
        request_data = {
            "request_id": "test_audit_001",
            "judge_type": "FinJudge",
            "action_type": "wire_transfer",
            "context": {"amount_usd": 50000, "vendor_status": "new", "purchase_order": None},
            "requested_by": "test@example.com",
        }

        eval_response = client.post("/judges/evaluate", json=request_data)
        assert eval_response.status_code == 200

        # Retrieve audit trail
        audit_response = client.get("/judges/audit/test_audit_001")

        assert audit_response.status_code == 200
        data = audit_response.json()

        assert data["request_id"] == "test_audit_001"
        assert "trail_id" in data
        assert "semantic_summary" in data
        assert "full_context" in data

    def test_get_audit_trail_not_found(self, client):
        """Test audit trail retrieval for non-existent request"""
        response = client.get("/judges/audit/nonexistent_request")

        assert response.status_code == 404


class TestMetricsEndpoints:
    """Test metrics endpoints"""

    def test_get_judge_metrics(self, client):
        """Test metrics retrieval for specific judge"""
        # Create some decisions first
        for i in range(10):
            request_data = {
                "request_id": f"test_metrics_fin_{i}",
                "judge_type": "FinJudge",
                "action_type": "wire_transfer",
                "context": {"amount_usd": 50000 + i * 1000, "vendor_status": "approved", "purchase_order": "PO-123"},
                "requested_by": "test@example.com",
            }
            client.post("/judges/evaluate", json=request_data)

        # Get metrics
        response = client.get("/judges/metrics/FinJudge")

        assert response.status_code == 200
        data = response.json()

        assert "decision_count" in data
        assert "avg_latency_ms" in data
        assert "p50_latency_ms" in data
        assert "p99_latency_ms" in data
        assert data["decision_count"] >= 10

    def test_get_overview_stats(self, client):
        """Test system overview statistics"""
        # Create decisions across verticals
        judge_types = ["FinJudge", "CaseJudge", "LawJudge", "FraudJudge"]

        for i, judge_type in enumerate(judge_types):
            request_data = {
                "request_id": f"test_overview_{judge_type}_{i}",
                "judge_type": judge_type,
                "action_type": "test",
                "context": {"amount_usd": 1000},
                "requested_by": "test@example.com",
            }
            client.post("/judges/evaluate", json=request_data)

        # Get overview
        response = client.get("/judges/stats/overview")

        assert response.status_code == 200
        data = response.json()

        assert "total_decisions" in data
        assert "decisions" in data
        assert "latency" in data
        assert "by_vertical" in data

        # Check all verticals are represented
        for judge_type in judge_types:
            assert judge_type in data["by_vertical"]


class TestRecentDecisionsEndpoint:
    """Test recent decisions retrieval"""

    def test_get_recent_decisions_all(self, client):
        """Test retrieving all recent decisions"""
        # Create some decisions
        for i in range(5):
            request_data = {
                "request_id": f"test_recent_{i}",
                "judge_type": "FinJudge",
                "action_type": "test",
                "context": {"amount_usd": 1000},
                "requested_by": "test@example.com",
            }
            client.post("/judges/evaluate", json=request_data)

        response = client.get("/judges/decisions/recent?limit=10")

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        assert len(data) >= 5

    def test_get_recent_decisions_filtered(self, client):
        """Test retrieving recent decisions with judge_type filter"""
        # Create decisions for different judges
        for judge_type in ["FinJudge", "CaseJudge"]:
            for i in range(3):
                request_data = {
                    "request_id": f"test_filtered_{judge_type}_{i}",
                    "judge_type": judge_type,
                    "action_type": "test",
                    "context": {"amount_usd": 1000},
                    "requested_by": "test@example.com",
                }
                client.post("/judges/evaluate", json=request_data)

        response = client.get("/judges/decisions/recent?judge_type=FinJudge&limit=10")

        assert response.status_code == 200
        data = response.json()

        # All returned decisions should be FinJudge
        for decision in data:
            if decision["request_id"].startswith("test_filtered"):
                assert decision["judge_type"] == "FinJudge"


class TestSampleGeneration:
    """Test sample request generation"""

    def test_generate_sample_finjudge(self, client):
        """Test sample generation for FinJudge"""
        response = client.post("/judges/test/generate-sample?judge_type=FinJudge")

        assert response.status_code == 200
        data = response.json()

        assert data["judge_type"] == "FinJudge"
        assert "context" in data
        assert "amount_usd" in data["context"]

    def test_generate_sample_all_judges(self, client):
        """Test sample generation for all judge types"""
        judge_types = ["FinJudge", "CaseJudge", "LawJudge", "FraudJudge"]

        for judge_type in judge_types:
            response = client.post(f"/judges/test/generate-sample?judge_type={judge_type}")

            assert response.status_code == 200
            data = response.json()
            assert data["judge_type"] == judge_type


class TestEndToEndFlow:
    """Test complete end-to-end flow"""

    def test_full_decision_flow(self, client):
        """Test complete flow: evaluate → get audit → get metrics"""
        request_id = "test_e2e_001"

        # 1. Evaluate
        request_data = {
            "request_id": request_id,
            "judge_type": "FinJudge",
            "action_type": "wire_transfer",
            "context": {"amount_usd": 75000, "vendor_status": "new", "purchase_order": None},
            "requested_by": "test@example.com",
        }

        eval_response = client.post("/judges/evaluate", json=request_data)
        assert eval_response.status_code == 200
        eval_data = eval_response.json()

        # 2. Get audit trail
        audit_response = client.get(f"/judges/audit/{request_id}")
        assert audit_response.status_code == 200
        audit_data = audit_response.json()

        # Verify consistency
        assert audit_data["request_id"] == request_id
        assert audit_data["decision"] == eval_data["decision"]

        # 3. Get metrics
        metrics_response = client.get("/judges/metrics/FinJudge")
        assert metrics_response.status_code == 200

        # 4. Check recent decisions
        recent_response = client.get("/judges/decisions/recent?limit=100")
        assert recent_response.status_code == 200
        recent_data = recent_response.json()

        # Find our decision
        found = any(d["request_id"] == request_id for d in recent_data)
        assert found, "Decision not found in recent decisions"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
