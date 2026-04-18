"""Tests for Innovation Lab Service"""

import pytest
from fastapi.testclient import TestClient

from services.innovation_lab.main import create_innovation_app
from services.innovation_lab.models import (
    InnovationRequest,
    InnovationType,
    PrototypeRequest,
    TechDomain,
    TechEvaluationRequest,
)


@pytest.fixture
def client():
    """Create a test client for the Innovation Lab service"""
    app = create_innovation_app()
    return TestClient(app)


class TestHealthEndpoints:
    """Test health and system endpoints"""

    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "Innovation Lab & AI Innovation"
        assert data["innovation_ready"] is True

    def test_root_endpoint(self, client):
        """Test root endpoint returns service info"""
        response = client.get("/v1/")
        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        assert "endpoints" in data
        assert "features" in data
        assert "focus_areas" in data


class TestIdeationEndpoint:
    """Test ideation/idea generation endpoints"""

    def test_ideate_basic(self, client):
        """Test basic ideation request"""
        request_data = {
            "prompt": "How can we improve remote team collaboration?",
            "innovation_type": "ideation",
            "tech_domain": "ai_ml",
            "max_ideas": 3,
            "risk_tolerance": 0.7,
        }
        response = client.post("/v1/ideate", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert "summary" in data
        assert "ideas" in data
        assert len(data["ideas"]) <= 3
        assert "key_insights" in data
        assert "recommended_experiments" in data

    def test_ideate_with_context(self, client):
        """Test ideation with additional context"""
        request_data = {
            "prompt": "Blockchain for supply chain",
            "innovation_type": "ideation",
            "context": "Focus on food industry with traceability",
            "max_ideas": 2,
        }
        response = client.post("/v1/ideate", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert "ideas" in data

    def test_ideate_max_ideas_exceeded(self, client):
        """Test that exceeding max_ideas limit returns error"""
        request_data = {
            "prompt": "Test prompt",
            "max_ideas": 50,  # Exceeds default limit of 10
        }
        response = client.post("/v1/ideate", json=request_data)
        assert response.status_code == 400

    def test_ideate_invalid_prompt(self, client):
        """Test that too short prompt is rejected"""
        request_data = {
            "prompt": "Test",  # Too short (< 10 chars)
        }
        response = client.post("/v1/ideate", json=request_data)
        assert response.status_code == 422  # Validation error


class TestPrototypeEndpoint:
    """Test prototype design endpoints"""

    def test_design_prototype_basic(self, client):
        """Test basic prototype design"""
        request_data = {
            "concept": "Real-time collaborative whiteboard with AI assistance",
            "tech_domain": "ai_ml",
            "timeline": "2 weeks",
        }
        response = client.post("/v1/prototype", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert "architecture" in data
        assert "components" in data
        assert "tech_stack" in data
        assert "implementation_phases" in data
        assert "estimated_effort" in data

    def test_design_prototype_with_constraints(self, client):
        """Test prototype design with constraints"""
        request_data = {
            "concept": "Mobile-first task management app",
            "tech_domain": "general",
            "constraints": ["Must work offline", "Max 5MB app size"],
            "timeline": "4 weeks",
        }
        response = client.post("/v1/prototype", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert data["concept"] == request_data["concept"]


class TestTechEvaluationEndpoint:
    """Test technology evaluation endpoints"""

    def test_evaluate_technology_basic(self, client):
        """Test basic technology evaluation"""
        request_data = {
            "technology": "WebAssembly",
            "use_case": "High-performance web applications",
        }
        response = client.post("/v1/evaluate", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert "maturity_level" in data
        assert "strengths" in data
        assert "weaknesses" in data
        assert "opportunities" in data
        assert "threats" in data
        assert "adoption_readiness" in data

    def test_evaluate_with_comparison(self, client):
        """Test technology evaluation with comparisons"""
        request_data = {"technology": "Rust", "comparison_with": ["Go", "C++"]}
        response = client.post("/v1/evaluate", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert data["technology"] == "Rust"


class TestExperimentEndpoint:
    """Test experiment design endpoints"""

    def test_design_experiment(self, client):
        """Test experiment design"""
        response = client.post(
            "/v1/experiment",
            params={
                "hypothesis": "AI-powered search improves user satisfaction",
                "variables": ["search_accuracy", "response_time", "user_satisfaction"],
                "success_criteria": ["80% accuracy", "User satisfaction > 4.0/5"],
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "hypothesis" in data
        assert "methodology" in data
        assert "success_criteria" in data
        assert "timeline" in data


class TestTrendsEndpoint:
    """Test technology trends endpoints"""

    def test_get_trends_general(self, client):
        """Test getting general tech trends"""
        response = client.get("/v1/trends")
        assert response.status_code == 200
        data = response.json()
        assert "domain" in data
        assert "trends" in data
        assert len(data["trends"]) > 0

    def test_get_trends_specific_domain(self, client):
        """Test getting domain-specific trends"""
        response = client.get("/v1/trends?domain=ai_ml&limit=5")
        assert response.status_code == 200
        data = response.json()
        assert data["domain"] == "ai_ml"
        assert len(data["trends"]) <= 5

    def test_get_trends_blockchain(self, client):
        """Test getting blockchain trends"""
        response = client.get("/v1/trends?domain=blockchain")
        assert response.status_code == 200
        data = response.json()
        assert data["domain"] == "blockchain"


class TestDataModels:
    """Test Pydantic data models"""

    def test_innovation_request_model(self):
        """Test InnovationRequest model validation"""
        request = InnovationRequest(
            prompt="Test innovation prompt for validation",
            innovation_type=InnovationType.IDEATION,
            max_ideas=5,
        )
        assert request.prompt == "Test innovation prompt for validation"
        assert request.max_ideas == 5
        assert request.risk_tolerance == 0.7  # Default value

    def test_innovation_request_validation(self):
        """Test InnovationRequest validation"""
        with pytest.raises(Exception):
            # Should fail - prompt too short
            InnovationRequest(prompt="Test")

    def test_prototype_request_model(self):
        """Test PrototypeRequest model"""
        request = PrototypeRequest(
            concept="Test concept for prototype design validation",
            tech_domain=TechDomain.AI_ML,
            timeline="3 weeks",
        )
        assert request.concept == "Test concept for prototype design validation"
        assert request.timeline == "3 weeks"

    def test_tech_evaluation_request_model(self):
        """Test TechEvaluationRequest model"""
        request = TechEvaluationRequest(
            technology="Kubernetes",
            use_case="Container orchestration",
            comparison_with=["Docker Swarm", "Nomad"],
        )
        assert request.technology == "Kubernetes"
        assert len(request.comparison_with) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
