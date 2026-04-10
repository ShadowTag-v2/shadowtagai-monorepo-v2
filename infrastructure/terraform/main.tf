# Main Terraform configuration for shadowtagai orchestrator
# Cloud Run ONLY infrastructure on Google Cloud Platform

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 5.0"
    }
  }

  # Remote state storage
  backend "gcs" {
    bucket = "acquired-jet-478701-b3-terraform-state"
    prefix = "shadowtagai/orchestrator"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DATA SOURCES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

data "google_project" "project" {
  project_id = var.project_id
}

data "google_client_config" "default" {}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ENABLE REQUIRED APIS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

resource "google_project_service" "required_apis" {
  for_each = toset([
    "run.googleapis.com",                 # Cloud Run (ADDED)
    "compute.googleapis.com",             # Compute Engine
    "aiplatform.googleapis.com",          # Vertex AI
    "artifactregistry.googleapis.com",    # Artifact Registry
    "cloudbuild.googleapis.com",          # Cloud Build
    "cloudresourcemanager.googleapis.com",# Resource Manager
    "iam.googleapis.com",                 # IAM
    "secretmanager.googleapis.com",       # Secret Manager
    "monitoring.googleapis.com",          # Cloud Monitoring
    "logging.googleapis.com",             # Cloud Logging
    "cloudtrace.googleapis.com",          # Cloud Trace
    "containerscanning.googleapis.com",   # Container Scanning
    "vpcaccess.googleapis.com",           # VPC Access (for future use)
  ])

  project = var.project_id
  service = each.value

  disable_on_destroy = false
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# VPC NETWORK
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

resource "google_compute_network" "vpc" {
  name                    = "shadowtagai-vpc"
  auto_create_subnetworks = false
  project                 = var.project_id

  depends_on = [google_project_service.required_apis]
}

resource "google_compute_subnetwork" "cloud_run_subnet" {
  name          = "shadowtagai-subnet"
  ip_cidr_range = "10.0.16.0/20"
  region        = var.region
  network       = google_compute_network.vpc.id
  project       = var.project_id

  private_ip_google_access = true
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# OUTPUTS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

output "vpc_name" {
  value       = google_compute_network.vpc.name
  description = "VPC network name"
}

output "subnet_name" {
  value       = google_compute_subnetwork.cloud_run_subnet.name
  description = "Subnet name"
}
