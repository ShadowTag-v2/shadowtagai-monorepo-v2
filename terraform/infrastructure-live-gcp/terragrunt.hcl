# Root Terragrunt configuration for all GCP environments
# See: skills/terraform-comprehensive-workflow/SKILL.md Phase 10

locals {
  project_id = "shadowtag-omega-v4"
  region     = "us-central1"
}

remote_state {
  backend = "gcs"
  config = {
    project  = local.project_id
    location = local.region
    bucket   = "${local.project_id}-tfstate"
    prefix   = "${path_relative_to_include()}/terraform.tfstate"
  }
}

generate "provider" {
  path      = "provider.tf"
  if_exists = "overwrite_terragrunt"
  contents  = <<EOF
provider "google" {
  project = "${local.project_id}"
  region  = "${local.region}"
  default_labels = {
    managed_by = "terragrunt"
    repo       = "infrastructure-live-gcp"
  }
}
EOF
}

generate "versions" {
  path      = "versions.tf"
  if_exists = "overwrite_terragrunt"
  contents  = <<EOF
terraform {
  required_version = ">= 1.9.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"
    }
  }
}
EOF
}
