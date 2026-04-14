"""Terraform models and schemas
"""

from typing import Any

from pydantic import BaseModel, Field

from app.models.infrastructure import CloudProvider


class TerraformGenerateRequest(BaseModel):
    """Request model for Terraform generation"""

    design_id: str = Field(..., description="Infrastructure design ID")
    cloud_provider: CloudProvider
    components: list[dict[str, Any]]
    backend_config: dict[str, str] | None = Field(
        default=None, description="Terraform backend configuration",
    )
    variables: dict[str, Any] | None = Field(default=None, description="Terraform variables")


class TerraformFile(BaseModel):
    """Terraform file content"""

    filename: str
    content: str
    description: str


class TerraformGenerateResponse(BaseModel):
    """Response model for Terraform generation"""

    files: list[TerraformFile]
    provider: CloudProvider
    modules_used: list[str]
    instructions: list[str]


class TerraformValidateRequest(BaseModel):
    """Request model for Terraform validation"""

    files: list[TerraformFile]
    cloud_provider: CloudProvider


class ValidationIssue(BaseModel):
    """Validation issue"""

    severity: str  # error, warning, info
    message: str
    file: str
    line: int | None = None


class TerraformValidateResponse(BaseModel):
    """Response model for Terraform validation"""

    valid: bool
    issues: list[ValidationIssue]
    best_practices: list[str]
    suggestions: list[str]
