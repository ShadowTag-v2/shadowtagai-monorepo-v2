"""Tests for Market Analyst agent"""

from unittest.mock import Mock, patch

import pytest

from src.agents.market_analyst.agent import MarketAnalystAgent
from src.agents.market_analyst.tools import CompetitiveAnalysisTools, MarketPositioningTools


class TestCompetitiveAnalysisTools:
    """Test competitive analysis tools"""

    def test_create_feature_matrix(self):
        """Test feature matrix creation"""
        tools = CompetitiveAnalysisTools()

        matrix = tools.create_feature_matrix(
            product="MyProduct", competitors=["CompA", "CompB"], features=["Feature1", "Feature2"],
        )

        assert matrix["product"] == "MyProduct"
        assert len(matrix["competitors"]) == 2
        assert len(matrix["features"]) == 2
        assert "comparison" in matrix
        assert "Feature1" in matrix["comparison"]

    def test_calculate_feature_coverage(self):
        """Test feature coverage calculation"""
        tools = CompetitiveAnalysisTools()

        matrix = {
            "product": "MyProduct",
            "competitors": ["CompA"],
            "features": ["F1", "F2", "F3"],
            "comparison": {
                "F1": {"MyProduct": True, "CompA": True},
                "F2": {"MyProduct": True, "CompA": False},
                "F3": {"MyProduct": False, "CompA": True},
            },
        }

        coverage = tools.calculate_feature_coverage(matrix)

        assert coverage["total_features"] == 3
        assert coverage["coverage"]["MyProduct"]["count"] == 2
        assert coverage["coverage"]["CompA"]["count"] == 2

    def test_identify_gaps(self):
        """Test gap identification"""
        tools = CompetitiveAnalysisTools()

        matrix = {
            "product": "MyProduct",
            "competitors": ["CompA", "CompB"],
            "features": ["F1", "F2", "F3"],
            "comparison": {
                "F1": {"MyProduct": False, "CompA": True, "CompB": True},  # Critical gap
                "F2": {"MyProduct": False, "CompA": True, "CompB": False},  # Parity gap
                "F3": {"MyProduct": True, "CompA": False, "CompB": False},  # Unique
            },
        }

        gaps = tools.identify_gaps(matrix, "MyProduct")

        assert len(gaps["critical_gaps"]) == 1
        assert gaps["critical_gaps"][0]["feature"] == "F1"
        assert len(gaps["parity_gaps"]) == 1
        assert len(gaps["unique_features"]) == 1

    def test_prioritize_features(self):
        """Test feature prioritization"""
        tools = CompetitiveAnalysisTools()

        features = [
            {"name": "High Impact Low Effort", "impact": "high", "effort": "low"},
            {"name": "Low Impact High Effort", "impact": "low", "effort": "high"},
            {"name": "Medium Both", "impact": "medium", "effort": "medium"},
        ]

        prioritized = tools.prioritize_features(features)

        assert len(prioritized) == 3
        assert prioritized[0]["priority"] == "P0"
        assert prioritized[0]["name"] == "High Impact Low Effort"
        assert all("priority_score" in f for f in prioritized)

    def test_generate_swot_matrix(self):
        """Test SWOT matrix generation"""
        tools = CompetitiveAnalysisTools()

        swot = tools.generate_swot_matrix(
            strengths=["S1", "S2"], weaknesses=["W1"], opportunities=["O1", "O2"], threats=["T1"],
        )

        assert len(swot["swot_analysis"]["strengths"]) == 2
        assert len(swot["swot_analysis"]["weaknesses"]) == 1
        assert "strategic_insights" in swot
        assert "timestamp" in swot


class TestMarketPositioningTools:
    """Test market positioning tools"""

    def test_define_positioning_statement(self):
        """Test positioning statement generation"""
        tools = MarketPositioningTools()

        statement = tools.define_positioning_statement(
            target_market="SaaS companies",
            category="analytics platform",
            unique_benefit="provides real-time insights",
            reason_to_believe="we process data 10x faster",
        )

        assert "SaaS companies" in statement
        assert "analytics platform" in statement
        assert "real-time insights" in statement
        assert "10x faster" in statement

    def test_identify_unfair_advantages(self):
        """Test unfair advantage identification"""
        tools = MarketPositioningTools()

        capabilities = [
            {"name": "Strong Advantage", "uniqueness": 9, "defensibility": 8, "customer_value": 9},
            {"name": "Weak Advantage", "uniqueness": 5, "defensibility": 4, "customer_value": 5},
        ]

        advantages = tools.identify_unfair_advantages(capabilities)

        assert len(advantages) >= 1
        assert advantages[0]["name"] == "Strong Advantage"
        assert advantages[0]["is_unfair_advantage"]
        assert "advantage_score" in advantages[0]


class TestMarketAnalystAgent:
    """Test Market Analyst agent"""

    @pytest.fixture
    def mock_anthropic_client(self):
        """Mock Anthropic client"""
        with patch("src.agents.market_analyst.agent.anthropic.Anthropic") as mock:
            mock_response = Mock()
            mock_response.content = [Mock(text="Analysis result")]
            mock_response.usage = Mock(input_tokens=100, output_tokens=200)
            mock.return_value.messages.create.return_value = mock_response
            yield mock

    @pytest.fixture
    def agent(self, mock_anthropic_client):
        """Create agent instance with mocked client"""
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}):
            return MarketAnalystAgent()

    def test_agent_initialization(self, agent):
        """Test agent initializes correctly"""
        assert agent.name == "Market Analyst - Product Strategy"
        assert agent.tools is not None
        assert agent.positioning_tools is not None

    def test_get_capabilities(self, agent):
        """Test get capabilities"""
        capabilities = agent.get_capabilities()
        assert "competitive_analysis" in capabilities
        assert "feature_comparison" in capabilities

    def test_validate_input(self, agent):
        """Test input validation"""
        assert agent.validate_input("Valid prompt")
        assert not agent.validate_input("")
        assert not agent.validate_input("   ")

    @pytest.mark.asyncio
    async def test_process_request(self, agent, mock_anthropic_client):
        """Test processing a request"""
        result = await agent.process(prompt="Analyze competitors", context={"product": "MyProduct"})

        assert result["status"] == "success"
        assert "analysis" in result
        assert result["agent"] == "Market Analyst - Product Strategy"

    def test_get_templates(self, agent):
        """Test get templates"""
        templates = agent.get_templates()
        assert "competitive_analysis" in templates
        assert "feature_gap" in templates
        assert "differentiation" in templates


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
