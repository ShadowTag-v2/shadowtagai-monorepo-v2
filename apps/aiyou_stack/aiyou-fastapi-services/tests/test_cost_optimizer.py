# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Tests for AWS Cost Optimizer service."""

from unittest.mock import Mock, patch

import pytest

from src.models.cost_optimizer_models import OptimizationType
from src.services.cost_optimizer import CostOptimizerService


@pytest.fixture
def mock_ce_client():
    """Mock Cost Explorer client for testing."""
    with patch("src.services.cost_optimizer.get_cost_explorer_client") as mock:
        client = Mock()
        mock.return_value = client
        yield client


@pytest.fixture
def cost_optimizer_service(mock_ce_client):
    """Create Cost Optimizer service instance with mocked client."""
    return CostOptimizerService()


class TestCostAnalysis:
    """Test cost analysis functionality."""

    @pytest.mark.asyncio
    async def test_analyze_costs_default_dates(self, cost_optimizer_service, mock_ce_client):
        """Test cost analysis with default date range."""
        # Mock response
        mock_ce_client.get_cost_and_usage.return_value = {
            "ResultsByTime": [
                {
                    "TimePeriod": {"Start": "2024-01-01"},
                    "Total": {"UnblendedCost": {"Amount": "100.50", "Unit": "USD"}},
                },
            ],
        }

        result = await cost_optimizer_service.analyze_costs()

        assert result is not None
        assert result.summary.total_cost > 0
        assert len(result.data_points) > 0
        mock_ce_client.get_cost_and_usage.assert_called_once()

    @pytest.mark.asyncio
    async def test_analyze_costs_with_grouping(self, cost_optimizer_service, mock_ce_client):
        """Test cost analysis with service grouping."""
        mock_ce_client.get_cost_and_usage.return_value = {
            "ResultsByTime": [
                {
                    "TimePeriod": {"Start": "2024-01-01"},
                    "Groups": [
                        {
                            "Keys": ["Amazon EC2"],
                            "Metrics": {"UnblendedCost": {"Amount": "50.00", "Unit": "USD"}},
                        },
                        {
                            "Keys": ["Amazon S3"],
                            "Metrics": {"UnblendedCost": {"Amount": "25.00", "Unit": "USD"}},
                        },
                    ],
                },
            ],
        }

        result = await cost_optimizer_service.analyze_costs(
            start_date="2024-01-01",
            end_date="2024-01-31",
            group_by=["SERVICE"],
        )

        assert result.summary.total_cost == 75.00
        assert len(result.data_points) == 2
        assert result.data_points[0].service in ["Amazon EC2", "Amazon S3"]


class TestRecommendations:
    """Test optimization recommendations."""

    @pytest.mark.asyncio
    async def test_get_rightsizing_recommendations(self, cost_optimizer_service, mock_ce_client):
        """Test right-sizing recommendations."""
        mock_ce_client.get_rightsizing_recommendations.return_value = {
            "RightsizingRecommendations": [
                {
                    "CurrentInstance": {
                        "ResourceId": "i-1234567890abcdef0",
                        "MonthlyCost": "150.00",
                    },
                    "ModifyRecommendationDetail": {
                        "TargetInstances": [{"EstimatedMonthlySavings": "75.00"}],
                    },
                },
            ],
        }

        result = await cost_optimizer_service.get_optimization_recommendations(
            optimization_types=[OptimizationType.RIGHT_SIZING],
            min_savings_threshold=50.0,
        )

        assert result.total_estimated_savings >= 50.0
        assert result.recommendations_count > 0
        assert result.recommendations[0].recommendation_type == OptimizationType.RIGHT_SIZING

    @pytest.mark.asyncio
    async def test_recommendations_with_forecast(self, cost_optimizer_service, mock_ce_client):
        """Test recommendations with cost forecast."""
        mock_ce_client.get_rightsizing_recommendations.return_value = {
            "RightsizingRecommendations": [],
        }

        mock_ce_client.get_cost_forecast.return_value = {
            "Total": {"Amount": "5000.00", "Unit": "USD"},
        }

        result = await cost_optimizer_service.get_optimization_recommendations(
            include_forecast=True,
        )

        assert result.forecast is not None
        assert "forecasted_cost" in result.forecast


class TestWasteAnalysis:
    """Test waste analysis functionality."""

    @pytest.mark.asyncio
    async def test_analyze_waste(self, cost_optimizer_service):
        """Test waste analysis."""
        result = await cost_optimizer_service.analyze_waste()

        assert result is not None
        assert result.total_waste_cost >= 0
        assert isinstance(result.waste_categories, dict)
        assert isinstance(result.idle_resources, list)
        assert isinstance(result.unused_resources, list)


class TestDataProcessing:
    """Test data processing helpers."""

    def test_process_cost_data_ungrouped(self, cost_optimizer_service):
        """Test processing ungrouped cost data."""
        cost_data = {
            "ResultsByTime": [
                {
                    "TimePeriod": {"Start": "2024-01-01"},
                    "Total": {"UnblendedCost": {"Amount": "123.45", "Unit": "USD"}},
                },
            ],
        }

        data_points = cost_optimizer_service._process_cost_data(cost_data)

        assert len(data_points) == 1
        assert data_points[0].amount == 123.45
        assert data_points[0].date == "2024-01-01"

    def test_process_cost_data_grouped(self, cost_optimizer_service):
        """Test processing grouped cost data."""
        cost_data = {
            "ResultsByTime": [
                {
                    "TimePeriod": {"Start": "2024-01-01"},
                    "Groups": [
                        {
                            "Keys": ["Service1"],
                            "Metrics": {"UnblendedCost": {"Amount": "100.00", "Unit": "USD"}},
                        },
                    ],
                },
            ],
        }

        data_points = cost_optimizer_service._process_cost_data(cost_data)

        assert len(data_points) == 1
        assert data_points[0].service == "Service1"
        assert data_points[0].amount == 100.00


class TestCostSummary:
    """Test cost summary calculations."""

    def test_calculate_cost_summary(self, cost_optimizer_service):
        """Test cost summary calculation."""
        from src.models.cost_optimizer_models import CostDataPoint

        data_points = [
            CostDataPoint(date="2024-01-01", amount=100.00, service="EC2"),
            CostDataPoint(date="2024-01-02", amount=150.00, service="S3"),
            CostDataPoint(date="2024-01-03", amount=200.00, service="EC2"),
        ]

        summary = cost_optimizer_service._calculate_cost_summary(
            data_points=data_points,
            start_date="2024-01-01",
            end_date="2024-01-03",
            raw_data={},
        )

        assert summary.total_cost == 450.00
        assert summary.average_daily_cost == 150.00
        assert len(summary.top_services) > 0
        assert summary.top_services[0]["service"] == "EC2"
        assert summary.top_services[0]["cost"] == 300.00


@pytest.mark.asyncio
async def test_service_initialization():
    """Test service initialization."""
    with patch("src.services.cost_optimizer.get_cost_explorer_client"):
        service = CostOptimizerService()
        assert service is not None
        assert service.ce_client is not None
