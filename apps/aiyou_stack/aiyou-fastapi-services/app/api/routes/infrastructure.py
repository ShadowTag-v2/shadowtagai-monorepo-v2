"""Infrastructure design and management endpoints"""

from typing import Any

from fastapi import APIRouter, HTTPException

from app.models.infrastructure import (
    CostEstimateRequest,
    CostEstimateResponse,
    InfrastructureDesignRequest,
    InfrastructureDesignResponse,
    ScalingRecommendation,
)
from app.services.cost_optimizer import CostOptimizerService
from app.services.infrastructure_builder import InfrastructureBuilderService
from app.services.scaling_designer import ScalingDesignerService

router = APIRouter()
infrastructure_service = InfrastructureBuilderService()
cost_service = CostOptimizerService()
scaling_service = ScalingDesignerService()


@router.post("/design", response_model=InfrastructureDesignResponse)
async def design_infrastructure(request: InfrastructureDesignRequest):
    """Design cloud infrastructure based on requirements.
    Returns architecture design with components and recommendations.
    """
    try:
        design = infrastructure_service.design_architecture(request)
        return design
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/cost-estimate", response_model=CostEstimateResponse)
async def estimate_costs(request: CostEstimateRequest):
    """Estimate monthly costs for infrastructure design.
    Includes cost optimization recommendations.
    """
    try:
        estimate = cost_service.calculate_costs(request)
        return estimate
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/scaling-recommendations", response_model=ScalingRecommendation)
async def get_scaling_recommendations(request: dict[str, Any]):
    """Get scaling recommendations for infrastructure.
    Analyzes workload and provides auto-scaling configurations.
    """
    try:
        recommendations = scaling_service.analyze_and_recommend(request)
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/templates")
async def list_templates():
    """List available infrastructure templates"""
    return {
        "templates": [
            {
                "id": "web-app-basic",
                "name": "Basic Web Application",
                "description": "Simple web app with load balancer, app servers, and database",
                "cloud_providers": ["aws", "gcp", "azure"],
            },
            {
                "id": "microservices",
                "name": "Microservices Architecture",
                "description": "Kubernetes-based microservices with service mesh",
                "cloud_providers": ["aws", "gcp", "azure"],
            },
            {
                "id": "data-pipeline",
                "name": "Data Pipeline",
                "description": "ETL pipeline with data lake and analytics",
                "cloud_providers": ["aws", "gcp", "azure"],
            },
            {
                "id": "serverless",
                "name": "Serverless Architecture",
                "description": "Serverless functions with API Gateway and managed services",
                "cloud_providers": ["aws", "gcp", "azure"],
            },
        ],
    }


@router.get("/providers")
async def list_cloud_providers():
    """List supported cloud providers and their services"""
    return {
        "providers": {
            "aws": {
                "name": "Amazon Web Services",
                "services": ["EC2", "RDS", "S3", "Lambda", "ECS", "EKS", "CloudFront"],
                "regions": 20,
            },
            "gcp": {
                "name": "Google Cloud Platform",
                "services": [
                    "Compute Engine",
                    "Cloud SQL",
                    "Cloud Storage",
                    "Cloud Functions",
                    "GKE",
                ],
                "regions": 35,
            },
            "azure": {
                "name": "Microsoft Azure",
                "services": [
                    "Virtual Machines",
                    "Azure SQL",
                    "Blob Storage",
                    "Azure Functions",
                    "AKS",
                ],
                "regions": 60,
            },
        },
    }
