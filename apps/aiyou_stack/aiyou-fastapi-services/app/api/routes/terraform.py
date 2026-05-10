"""Terraform infrastructure as code endpoints"""

from fastapi import APIRouter, HTTPException

from app.models.terraform import (
    TerraformGenerateRequest,
    TerraformGenerateResponse,
    TerraformValidateRequest,
    TerraformValidateResponse,
)
from app.services.terraform_generator import TerraformGeneratorService

router = APIRouter()
terraform_service = TerraformGeneratorService()


@router.post("/generate", response_model=TerraformGenerateResponse)
async def generate_terraform(request: TerraformGenerateRequest):
    """Generate Terraform configuration from infrastructure design.
    Returns complete .tf files ready to deploy.
    """
    try:
        terraform_code = terraform_service.generate(request)
        return terraform_code
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/validate", response_model=TerraformValidateResponse)
async def validate_terraform(request: TerraformValidateRequest):
    """Validate Terraform configuration.
    Checks syntax and best practices.
    """
    try:
        validation = terraform_service.validate(request)
        return validation
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/modules")
async def list_terraform_modules():
    """List available Terraform modules"""
    return {
        "modules": [
            {
                "name": "vpc",
                "description": "Virtual Private Cloud with subnets and routing",
                "providers": ["aws", "gcp", "azure"],
            },
            {
                "name": "compute",
                "description": "Compute instances with auto-scaling",
                "providers": ["aws", "gcp", "azure"],
            },
            {
                "name": "database",
                "description": "Managed database service",
                "providers": ["aws", "gcp", "azure"],
            },
            {
                "name": "kubernetes",
                "description": "Managed Kubernetes cluster",
                "providers": ["aws", "gcp", "azure"],
            },
            {
                "name": "load-balancer",
                "description": "Load balancer with SSL termination",
                "providers": ["aws", "gcp", "azure"],
            },
            {
                "name": "storage",
                "description": "Object storage bucket",
                "providers": ["aws", "gcp", "azure"],
            },
        ],
    }
