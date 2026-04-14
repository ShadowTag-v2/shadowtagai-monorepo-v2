"""Terraform Generator Service
Generates Terraform configurations from infrastructure designs
"""

from typing import Any

from app.models.infrastructure import CloudProvider
from app.models.terraform import (
    TerraformFile,
    TerraformGenerateRequest,
    TerraformGenerateResponse,
    TerraformValidateRequest,
    TerraformValidateResponse,
    ValidationIssue,
)


class TerraformGeneratorService:
    """Service for generating and validating Terraform code"""

    def generate(self, request: TerraformGenerateRequest) -> TerraformGenerateResponse:
        """Generate Terraform configuration files"""
        files = []
        modules_used = []

        # Generate provider configuration
        files.append(self._generate_provider_config(request.cloud_provider))

        # Generate backend configuration
        if request.backend_config:
            files.append(self._generate_backend_config(request.backend_config))

        # Generate variables file
        files.append(self._generate_variables(request.variables or {}))

        # Generate main infrastructure
        main_config = self._generate_main_config(request.components, request.cloud_provider)
        files.append(main_config)
        modules_used = self._extract_modules(request.components)

        # Generate outputs
        files.append(self._generate_outputs(request.components))

        instructions = self._generate_deployment_instructions(request.cloud_provider)

        return TerraformGenerateResponse(
            files=files,
            provider=request.cloud_provider,
            modules_used=modules_used,
            instructions=instructions,
        )

    def validate(self, request: TerraformValidateRequest) -> TerraformValidateResponse:
        """Validate Terraform configuration"""
        issues = []
        best_practices = []
        suggestions = []

        # Basic validation checks
        for file in request.files:
            # Check for common issues
            if "resource" in file.content and "provider" not in file.content:
                if file.filename == "main.tf":
                    issues.append(
                        ValidationIssue(
                            severity="warning",
                            message="No provider configuration found in main.tf",
                            file=file.filename,
                        ),
                    )

            # Check for hardcoded values
            if any(keyword in file.content for keyword in ["password", "secret", "key"]):
                issues.append(
                    ValidationIssue(
                        severity="error",
                        message="Potential hardcoded secrets detected. Use variables or secrets management.",
                        file=file.filename,
                    ),
                )

        # Best practices
        best_practices.append("Use remote state backend for team collaboration")
        best_practices.append("Enable state locking to prevent concurrent modifications")
        best_practices.append("Tag all resources for cost tracking and management")
        best_practices.append("Use modules for reusable infrastructure components")

        # Suggestions
        suggestions.append("Consider using Terraform workspaces for multiple environments")
        suggestions.append("Implement pre-commit hooks for terraform fmt and validate")
        suggestions.append("Use terraform-docs to generate documentation")

        valid = all(issue.severity != "error" for issue in issues)

        return TerraformValidateResponse(
            valid=valid, issues=issues, best_practices=best_practices, suggestions=suggestions,
        )

    def _generate_provider_config(self, provider: CloudProvider) -> TerraformFile:
        """Generate provider configuration"""
        if provider == CloudProvider.AWS:
            content = """terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Environment = var.environment
      ManagedBy   = "Terraform"
      Project     = var.project_name
    }
  }
}
"""
        elif provider == CloudProvider.GCP:
            content = """terraform {
  required_version = ">= 1.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.gcp_project
  region  = var.gcp_region

  labels = {
    environment = var.environment
    managed_by  = "terraform"
    project     = var.project_name
  }
}
"""
        else:  # Azure
            content = """terraform {
  required_version = ">= 1.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {}

  subscription_id = var.azure_subscription_id
}
"""

        return TerraformFile(
            filename="provider.tf", content=content, description="Terraform provider configuration",
        )

    def _generate_backend_config(self, backend_config: dict[str, str]) -> TerraformFile:
        """Generate backend configuration"""
        backend_type = backend_config.get("type", "s3")

        if backend_type == "s3":
            content = f"""terraform {{
  backend "s3" {{
    bucket         = "{backend_config.get("bucket", "terraform-state")}"
    key            = "{backend_config.get("key", "infrastructure/terraform.tfstate")}"
    region         = "{backend_config.get("region", "us-east-1")}"
    encrypt        = true
    dynamodb_table = "{backend_config.get("dynamodb_table", "terraform-locks")}"
  }}
}}
"""
        elif backend_type == "gcs":
            content = f"""terraform {{
  backend "gcs" {{
    bucket = "{backend_config.get("bucket", "terraform-state")}"
    prefix = "{backend_config.get("prefix", "infrastructure")}"
  }}
}}
"""
        else:
            content = """terraform {
  backend "local" {
    path = "terraform.tfstate"
  }
}
"""

        return TerraformFile(
            filename="backend.tf",
            content=content,
            description="Terraform backend configuration for state management",
        )

    def _generate_variables(self, variables: dict[str, Any]) -> TerraformFile:
        """Generate variables file"""
        content = """# Infrastructure Variables

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "gcp_region" {
  description = "GCP region"
  type        = string
  default     = "us-central1"
}

variable "gcp_project" {
  description = "GCP project ID"
  type        = string
  default     = ""
}

variable "azure_subscription_id" {
  description = "Azure subscription ID"
  type        = string
  default     = ""
}

variable "enable_monitoring" {
  description = "Enable monitoring and logging"
  type        = bool
  default     = true
}

variable "enable_backup" {
  description = "Enable automated backups"
  type        = bool
  default     = true
}
"""

        # Add custom variables
        for key, value in variables.items():
            var_type = "string" if isinstance(value, str) else "number"
            content += f"""
variable "{key}" {{
  description = "Custom variable: {key}"
  type        = {var_type}
  default     = {self._format_terraform_value(value)}
}}
"""

        return TerraformFile(
            filename="variables.tf", content=content, description="Terraform input variables",
        )

    def _generate_main_config(
        self, components: list[dict[str, Any]], provider: CloudProvider,
    ) -> TerraformFile:
        """Generate main infrastructure configuration"""
        content = "# Main Infrastructure Configuration\n\n"

        for component in components:
            component_type = component.get("type", "")

            if component_type == "compute":
                content += self._generate_compute_resource(component, provider)
            elif component_type == "database":
                content += self._generate_database_resource(component, provider)
            elif component_type == "load_balancer":
                content += self._generate_lb_resource(component, provider)
            elif component_type == "storage":
                content += self._generate_storage_resource(component, provider)
            elif component_type == "kubernetes":
                content += self._generate_k8s_resource(component, provider)

        return TerraformFile(
            filename="main.tf", content=content, description="Main infrastructure resources",
        )

    def _generate_compute_resource(self, component: dict[str, Any], provider: CloudProvider) -> str:
        """Generate compute resource configuration"""
        if provider == CloudProvider.AWS:
            return """
# Auto Scaling Group
resource "aws_launch_template" "app" {
  name_prefix   = "${var.project_name}-"
  image_id      = data.aws_ami.ubuntu.id
  instance_type = var.instance_type

  vpc_security_group_ids = [aws_security_group.app.id]

  tag_specifications {
    resource_type = "instance"
    tags = {
      Name = "${var.project_name}-app"
    }
  }
}

resource "aws_autoscaling_group" "app" {
  name                = "${var.project_name}-asg"
  vpc_zone_identifier = aws_subnet.private[*].id
  target_group_arns   = [aws_lb_target_group.app.arn]
  health_check_type   = "ELB"

  min_size         = 2
  max_size         = 10
  desired_capacity = 2

  launch_template {
    id      = aws_launch_template.app.id
    version = "$Latest"
  }

  tag {
    key                 = "Name"
    value               = "${var.project_name}-app"
    propagate_at_launch = true
  }
}

data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }
}

"""
        return ""

    def _generate_database_resource(
        self, component: dict[str, Any], provider: CloudProvider,
    ) -> str:
        """Generate database resource configuration"""
        if provider == CloudProvider.AWS:
            return """
# RDS Database
resource "aws_db_instance" "main" {
  identifier     = "${var.project_name}-db"
  engine         = "postgres"
  engine_version = "15"
  instance_class = "db.t3.medium"

  allocated_storage     = 100
  max_allocated_storage = 1000
  storage_encrypted     = true

  db_name  = var.database_name
  username = var.database_username
  password = var.database_password

  multi_az               = true
  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "mon:04:00-mon:05:00"

  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.database.id]

  skip_final_snapshot = false
  final_snapshot_identifier = "${var.project_name}-db-final-snapshot"

  tags = {
    Name = "${var.project_name}-database"
  }
}

resource "aws_db_subnet_group" "main" {
  name       = "${var.project_name}-db-subnet"
  subnet_ids = aws_subnet.private[*].id

  tags = {
    Name = "${var.project_name}-db-subnet-group"
  }
}

"""
        return ""

    def _generate_lb_resource(self, component: dict[str, Any], provider: CloudProvider) -> str:
        """Generate load balancer resource configuration"""
        if provider == CloudProvider.AWS:
            return """
# Application Load Balancer
resource "aws_lb" "main" {
  name               = "${var.project_name}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = aws_subnet.public[*].id

  enable_deletion_protection = false
  enable_http2              = true

  tags = {
    Name = "${var.project_name}-alb"
  }
}

resource "aws_lb_target_group" "app" {
  name     = "${var.project_name}-tg"
  port     = 80
  protocol = "HTTP"
  vpc_id   = aws_vpc.main.id

  health_check {
    enabled             = true
    healthy_threshold   = 2
    interval            = 30
    matcher             = "200"
    path                = "/health"
    port                = "traffic-port"
    protocol            = "HTTP"
    timeout             = 5
    unhealthy_threshold = 2
  }
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app.arn
  }
}

"""
        return ""

    def _generate_storage_resource(self, component: dict[str, Any], provider: CloudProvider) -> str:
        """Generate storage resource configuration"""
        if provider == CloudProvider.AWS:
            return """
# S3 Bucket
resource "aws_s3_bucket" "main" {
  bucket = "${var.project_name}-storage"

  tags = {
    Name = "${var.project_name}-storage"
  }
}

resource "aws_s3_bucket_versioning" "main" {
  bucket = aws_s3_bucket.main.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "main" {
  bucket = aws_s3_bucket.main.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "main" {
  bucket = aws_s3_bucket.main.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

"""
        return ""

    def _generate_k8s_resource(self, component: dict[str, Any], provider: CloudProvider) -> str:
        """Generate Kubernetes cluster configuration"""
        if provider == CloudProvider.AWS:
            return """
# EKS Cluster
resource "aws_eks_cluster" "main" {
  name     = "${var.project_name}-eks"
  role_arn = aws_iam_role.eks_cluster.arn
  version  = "1.28"

  vpc_config {
    subnet_ids              = concat(aws_subnet.public[*].id, aws_subnet.private[*].id)
    endpoint_private_access = true
    endpoint_public_access  = true
  }

  depends_on = [
    aws_iam_role_policy_attachment.eks_cluster_policy
  ]
}

resource "aws_eks_node_group" "main" {
  cluster_name    = aws_eks_cluster.main.name
  node_group_name = "${var.project_name}-node-group"
  node_role_arn   = aws_iam_role.eks_node.arn
  subnet_ids      = aws_subnet.private[*].id

  scaling_config {
    desired_size = 3
    max_size     = 10
    min_size     = 3
  }

  instance_types = ["t3.medium"]

  depends_on = [
    aws_iam_role_policy_attachment.eks_node_policy,
    aws_iam_role_policy_attachment.eks_cni_policy,
    aws_iam_role_policy_attachment.eks_container_registry_policy
  ]
}

"""
        return ""

    def _generate_outputs(self, components: list[dict[str, Any]]) -> TerraformFile:
        """Generate outputs file"""
        content = """# Infrastructure Outputs

output "infrastructure_info" {
  description = "Infrastructure deployment information"
  value = {
    environment = var.environment
    project     = var.project_name
    deployed_at = timestamp()
  }
}
"""

        return TerraformFile(
            filename="outputs.tf",
            content=content,
            description="Terraform outputs for deployed infrastructure",
        )

    def _extract_modules(self, components: list[dict[str, Any]]) -> list[str]:
        """Extract modules used in components"""
        modules = set()
        for component in components:
            component_type = component.get("type", "")
            if component_type:
                modules.add(component_type)

        return sorted(list(modules))

    def _format_terraform_value(self, value: Any) -> str:
        """Format value for Terraform"""
        if isinstance(value, str):
            return f'"{value}"'
        if isinstance(value, bool):
            return str(value).lower()
        return str(value)

    def _generate_deployment_instructions(self, provider: CloudProvider) -> list[str]:
        """Generate deployment instructions"""
        instructions = [
            "📋 Terraform Deployment Instructions:",
            "",
            "1. Initialize Terraform:",
            "   terraform init",
            "",
            "2. Review the execution plan:",
            "   terraform plan",
            "",
            "3. Apply the configuration:",
            "   terraform apply",
            "",
            "4. View outputs:",
            "   terraform output",
            "",
            "⚠️  Important Notes:",
            "- Review all configurations before applying",
            "- Ensure you have proper cloud provider credentials configured",
            "- Consider using Terraform workspaces for multiple environments",
            "- Store state files securely (use remote backend)",
            "",
            "💰 Cost Management:",
            "- Run 'terraform plan' to preview costs before applying",
            "- Use cloud provider cost calculators for detailed estimates",
            "- Set up budget alerts in your cloud provider console",
            "",
            "🔒 Security Best Practices:",
            "- Never commit secrets or credentials to version control",
            "- Use variables or secrets management services",
            "- Enable encryption for all data stores",
            "- Implement least-privilege IAM policies",
        ]

        return instructions
