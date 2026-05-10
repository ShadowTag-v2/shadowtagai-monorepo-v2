"""Tests for Landing Page Optimizer service and endpoints"""

from unittest.mock import Mock, patch

import pytest

from app.services.landing_page_optimizer.schemas import (
    FocusArea,
    GenerateHeadlinesRequest,
    OptimizePageRequest,
)
from app.services.landing_page_optimizer.service import LandingPageOptimizerService


class TestLandingOptimizerEndpoints:
    """Test the Landing Page Optimizer API endpoints"""

    def test_service_info(self, client):
        """Test the service info endpoint"""
        response = client.get("/api/v1/landing-optimizer/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "Landing Page Optimizer"
        assert "capabilities" in data
        assert "endpoints" in data

    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_readiness_check(self, client):
        """Test readiness check endpoint"""
        response = client.get("/health/ready")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "checks" in data

    @patch("anthropic.Anthropic")
    def test_analyze_landing_page(self, mock_anthropic, client, sample_optimization_request):
        """Test landing page analysis endpoint"""
        # Mock the Anthropic response
        mock_client = Mock()
        mock_message = Mock()
        mock_message.content = [
            Mock(
                text="""
        {
            "overall_score": 65,
            "key_strengths": ["Clear visual hierarchy"],
            "key_weaknesses": ["Weak value proposition", "Generic CTA"],
            "recommendations": [
                {
                    "title": "Improve Headline",
                    "description": "Make it more specific",
                    "category": "headlines",
                    "priority": "high",
                    "expected_impact": "15-25% improvement",
                    "implementation_steps": ["Use specific benefits", "Add numbers"],
                    "before_example": "Welcome",
                    "after_example": "Build Your Site in 10 Minutes"
                }
            ],
            "headline_variations": [
                {
                    "text": "Build Professional Websites in Minutes",
                    "reasoning": "Focuses on speed and quality",
                    "target_emotion": "excitement"
                }
            ],
            "cta_variations": [
                {
                    "text": "Start Building Free",
                    "color_suggestion": "success-green",
                    "placement": "Above the fold",
                    "reasoning": "Low friction, immediate action"
                }
            ],
            "social_proof_suggestions": [],
            "estimated_conversion_lift": "20-35%"
        }
        """,
            ),
        ]
        mock_client.messages.create.return_value = mock_message
        mock_anthropic.return_value = mock_client

        response = client.post(
            "/api/v1/landing-optimizer/analyze",
            json=sample_optimization_request,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "analysis" in data
        assert data["analysis"]["overall_score"] == 65
        assert len(data["analysis"]["recommendations"]) > 0

    def test_analyze_landing_page_validation_error(self, client):
        """Test validation error handling"""
        response = client.post(
            "/api/v1/landing-optimizer/analyze",
            json={
                "page_content": "x",  # Too short
                "focus_areas": ["invalid_area"],  # Invalid focus area
            },
        )

        assert response.status_code == 422  # Validation error

    @patch("anthropic.Anthropic")
    def test_generate_headlines(self, mock_anthropic, client):
        """Test headline generation endpoint"""
        mock_client = Mock()
        mock_message = Mock()
        mock_message.content = [
            Mock(
                text="""
        [
            {
                "text": "Build Your Website in 10 Minutes",
                "reasoning": "Specific time commitment reduces friction",
                "target_emotion": "excitement"
            },
            {
                "text": "Professional Websites Made Simple",
                "reasoning": "Addresses pain point of complexity",
                "target_emotion": "relief"
            }
        ]
        """,
            ),
        ]
        mock_client.messages.create.return_value = mock_message
        mock_anthropic.return_value = mock_client

        request_data = {
            "product_service": "Website builder",
            "target_audience": "Small business owners",
            "key_benefit": "Build professional websites quickly",
            "tone": "professional",
            "count": 5,
        }

        response = client.post("/api/v1/landing-optimizer/headlines", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "headlines" in data
        assert len(data["headlines"]) > 0
        assert "text" in data["headlines"][0]
        assert "reasoning" in data["headlines"][0]

    @patch("anthropic.Anthropic")
    def test_generate_ctas(self, mock_anthropic, client):
        """Test CTA generation endpoint"""
        mock_client = Mock()
        mock_message = Mock()
        mock_message.content = [
            Mock(
                text="""
        [
            {
                "text": "Start Building Free",
                "color_suggestion": "success-green",
                "placement": "Above the fold, center",
                "reasoning": "No commitment required, action-oriented"
            }
        ]
        """,
            ),
        ]
        mock_client.messages.create.return_value = mock_message
        mock_anthropic.return_value = mock_client

        request_data = {
            "action_type": "signup",
            "product_service": "Website builder",
            "urgency_level": "medium",
            "count": 3,
        }

        response = client.post("/api/v1/landing-optimizer/ctas", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "ctas" in data
        assert len(data["ctas"]) > 0

    @patch("anthropic.Anthropic")
    def test_generate_social_proof(self, mock_anthropic, client):
        """Test social proof generation endpoint"""
        mock_client = Mock()
        mock_message = Mock()
        mock_message.content = [
            Mock(
                text="""
        [
            {
                "type": "testimonial",
                "content": "This tool helped us launch our site in just one day!",
                "placement": "Below hero section"
            },
            {
                "type": "statistic",
                "content": "Join 10,000+ happy customers",
                "placement": "Header area"
            }
        ]
        """,
            ),
        ]
        mock_client.messages.create.return_value = mock_message
        mock_anthropic.return_value = mock_client

        request_data = {
            "product_service": "Website builder",
            "existing_data": {"users": 10000, "rating": 4.8},
            "proof_types": ["testimonials", "statistics"],
        }

        response = client.post("/api/v1/landing-optimizer/social-proof", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "suggestions" in data
        assert len(data["suggestions"]) > 0


class TestLandingOptimizerService:
    """Test the Landing Page Optimizer service logic"""

    @pytest.mark.asyncio
    @patch("anthropic.Anthropic")
    async def test_optimize_page(self, mock_anthropic):
        """Test page optimization service method"""
        mock_client = Mock()
        mock_message = Mock()
        mock_message.content = [
            Mock(
                text="""
        {
            "overall_score": 70,
            "key_strengths": ["Good layout"],
            "key_weaknesses": ["Weak CTA"],
            "recommendations": [],
            "estimated_conversion_lift": "15-20%"
        }
        """,
            ),
        ]
        mock_client.messages.create.return_value = mock_message
        mock_anthropic.return_value = mock_client

        service = LandingPageOptimizerService()
        request = OptimizePageRequest(page_content="<h1>Test</h1>", focus_areas=[FocusArea.ALL])

        result = await service.optimize_page(request)

        assert result.overall_score == 70
        assert len(result.key_strengths) > 0
        assert len(result.key_weaknesses) > 0

    @pytest.mark.asyncio
    @patch("anthropic.Anthropic")
    async def test_generate_headlines_service(self, mock_anthropic):
        """Test headline generation service method"""
        mock_client = Mock()
        mock_message = Mock()
        mock_message.content = [
            Mock(
                text="""
        [
            {
                "text": "Test Headline",
                "reasoning": "Test reasoning",
                "target_emotion": "excitement"
            }
        ]
        """,
            ),
        ]
        mock_client.messages.create.return_value = mock_message
        mock_anthropic.return_value = mock_client

        service = LandingPageOptimizerService()
        request = GenerateHeadlinesRequest(
            product_service="Test product",
            target_audience="Test audience",
            key_benefit="Test benefit",
            count=3,
        )

        result = await service.generate_headlines(request)

        assert len(result) > 0
        assert result[0].text == "Test Headline"

    def test_parse_json_response(self):
        """Test JSON parsing from Claude responses"""
        service = LandingPageOptimizerService()

        # Test with JSON in markdown code block
        response_with_markdown = """
        Here's the analysis:
        ```json
        {"score": 85}
        ```
        """
        result = service._parse_json_response(response_with_markdown, dict)
        assert result["score"] == 85

        # Test with raw JSON
        response_raw = '{"score": 90}'
        result = service._parse_json_response(response_raw, dict)
        assert result["score"] == 90

    def test_build_optimization_prompt(self):
        """Test prompt building"""
        service = LandingPageOptimizerService()
        request = OptimizePageRequest(
            page_content="<h1>Test</h1>",
            focus_areas=[FocusArea.HEADLINES, FocusArea.CTA],
            current_conversion_rate=2.5,
            target_conversion_rate=5.0,
            target_audience="Test audience",
        )

        prompt = service._build_optimization_prompt(request)

        assert "Test" in prompt
        assert "headlines" in prompt
        assert "cta" in prompt
        assert "2.5" in prompt
        assert "5.0" in prompt
        assert "Test audience" in prompt
