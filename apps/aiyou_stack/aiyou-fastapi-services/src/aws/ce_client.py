"""
AWS Cost Explorer client for cost analysis operations.
"""

import logging
from typing import Any

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from src.config import settings

logger = logging.getLogger(__name__)


class CostExplorerClient:
    """AWS Cost Explorer client wrapper with error handling and utilities."""

    def __init__(self):
        """Initialize Cost Explorer client."""
        try:
            session_config = {"region_name": settings.aws_region}

            # Add credentials if provided (otherwise use IAM role)
            if settings.aws_access_key_id and settings.aws_secret_access_key:
                session_config.update(
                    {
                        "aws_access_key_id": settings.aws_access_key_id,
                        "aws_secret_access_key": settings.aws_secret_access_key,
                    }
                )

            if settings.aws_session_token:
                session_config["aws_session_token"] = settings.aws_session_token

            self.client = boto3.client("ce", **session_config)
            logger.info("Cost Explorer client initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Cost Explorer client: {e}")
            raise

    def get_cost_and_usage(
        self,
        start_date: str,
        end_date: str,
        granularity: str = "DAILY",
        metrics: list[str] | None = None,
        group_by: list[dict[str, str]] | None = None,
        filter_expr: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Get cost and usage data from AWS Cost Explorer.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            granularity: DAILY, MONTHLY, or HOURLY
            metrics: List of metrics (e.g., ['UnblendedCost', 'UsageQuantity'])
            group_by: List of grouping dimensions
            filter_expr: Filter expression for narrowing results

        Returns:
            Cost and usage data from AWS Cost Explorer
        """
        try:
            if metrics is None:
                metrics = ["UnblendedCost", "UsageQuantity"]

            params = {
                "TimePeriod": {"Start": start_date, "End": end_date},
                "Granularity": granularity,
                "Metrics": metrics,
            }

            if group_by:
                params["GroupBy"] = group_by

            if filter_expr:
                params["Filter"] = filter_expr

            response = self.client.get_cost_and_usage(**params)
            logger.info(f"Retrieved cost data from {start_date} to {end_date}")
            return response

        except ClientError as e:
            logger.error(f"AWS Client error in get_cost_and_usage: {e}")
            raise
        except BotoCoreError as e:
            logger.error(f"Boto core error in get_cost_and_usage: {e}")
            raise

    def get_cost_forecast(
        self,
        start_date: str,
        end_date: str,
        metric: str = "UNBLENDED_COST",
        granularity: str = "MONTHLY",
    ) -> dict[str, Any]:
        """
        Get cost forecast from AWS Cost Explorer.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            metric: Metric to forecast
            granularity: DAILY or MONTHLY

        Returns:
            Cost forecast data
        """
        try:
            response = self.client.get_cost_forecast(
                TimePeriod={"Start": start_date, "End": end_date},
                Metric=metric,
                Granularity=granularity,
            )
            logger.info(f"Retrieved cost forecast from {start_date} to {end_date}")
            return response

        except ClientError as e:
            logger.error(f"AWS Client error in get_cost_forecast: {e}")
            raise
        except BotoCoreError as e:
            logger.error(f"Boto core error in get_cost_forecast: {e}")
            raise

    def get_rightsizing_recommendations(self) -> dict[str, Any]:
        """
        Get rightsizing recommendations from AWS Cost Explorer.

        Returns:
            Rightsizing recommendations
        """
        try:
            response = self.client.get_rightsizing_recommendation(Service="AmazonEC2")
            logger.info("Retrieved rightsizing recommendations")
            return response

        except ClientError as e:
            logger.error(f"AWS Client error in get_rightsizing_recommendations: {e}")
            raise
        except BotoCoreError as e:
            logger.error(f"Boto core error in get_rightsizing_recommendations: {e}")
            raise

    def get_savings_plans_recommendations(
        self, lookback_period: str = "THIRTY_DAYS", payment_option: str = "NO_UPFRONT"
    ) -> dict[str, Any]:
        """
        Get Savings Plans recommendations.

        Args:
            lookback_period: SEVEN_DAYS, THIRTY_DAYS, or SIXTY_DAYS
            payment_option: NO_UPFRONT, PARTIAL_UPFRONT, or ALL_UPFRONT

        Returns:
            Savings Plans recommendations
        """
        try:
            response = self.client.get_savings_plans_purchase_recommendation(
                LookbackPeriodInDays=lookback_period,
                PaymentOption=payment_option,
                SavingsPlansType="COMPUTE_SP",
            )
            logger.info("Retrieved Savings Plans recommendations")
            return response

        except ClientError as e:
            logger.error(f"AWS Client error in get_savings_plans_recommendations: {e}")
            raise
        except BotoCoreError as e:
            logger.error(f"Boto core error in get_savings_plans_recommendations: {e}")
            raise

    def get_reservation_recommendations(
        self, service: str = "Amazon Elastic Compute Cloud - Compute"
    ) -> dict[str, Any]:
        """
        Get reservation purchase recommendations.

        Args:
            service: AWS service name

        Returns:
            Reservation recommendations
        """
        try:
            response = self.client.get_reservation_purchase_recommendation(Service=service)
            logger.info(f"Retrieved reservation recommendations for {service}")
            return response

        except ClientError as e:
            logger.error(f"AWS Client error in get_reservation_recommendations: {e}")
            raise
        except BotoCoreError as e:
            logger.error(f"Boto core error in get_reservation_recommendations: {e}")
            raise

    def get_cost_categories(self) -> list[str]:
        """
        List available cost categories.

        Returns:
            List of cost category ARNs
        """
        try:
            response = self.client.list_cost_category_definitions()
            categories = [
                cat["CostCategoryArn"] for cat in response.get("CostCategoryReferences", [])
            ]
            logger.info(f"Retrieved {len(categories)} cost categories")
            return categories

        except ClientError as e:
            logger.error(f"AWS Client error in get_cost_categories: {e}")
            raise
        except BotoCoreError as e:
            logger.error(f"Boto core error in get_cost_categories: {e}")
            raise


# Global client instance
_cost_explorer_client: CostExplorerClient | None = None


def get_cost_explorer_client() -> CostExplorerClient:
    """
    Get or create the global Cost Explorer client instance.

    Returns:
        CostExplorerClient instance
    """
    global _cost_explorer_client

    if _cost_explorer_client is None:
        _cost_explorer_client = CostExplorerClient()

    return _cost_explorer_client
