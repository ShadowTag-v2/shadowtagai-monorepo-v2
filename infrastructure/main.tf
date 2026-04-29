/**
 * Corrected Terraform Configuration for Claude_Code_6 Infrastructure
 *
 * FIXES APPLIED:
 * 1. Added missing KMS key resource definition
 * 2. Added missing service account resource
 * 3. Added required API enablement resources
 * 4. Fixed backend bucket (documented as prerequisite)
 * 5. Added proper IAM bindings
 * 6. Fixed artifact registry cleanup policy syntax
 * 7. Added workload identity binding
 * 8. Added proper dependency ordering
 *
 * PREREQUISITES:
 * 1. GCS bucket 'shadowtagai-terraform-state' must exist (create manually or via bootstrap)
 * 2. Terraform >= 1.5.0
 * 3. gcloud CLI authenticated
 */

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

  # Backend bucket must be created before running terraform init
  # Create with: gsutil mb -p shadowtagai-core-stack gs://shadowtagai-terraform-state
  backend "gcs" {
    bucket = "shadowtagai-terraform-state"
    prefix = "Claude_Code_6/terraform/state"
  }
}

# Configure providers
provider "google" {
  project = var.project_id
  region  = var.region
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
}

# Variables
variable "project_id" {
  description = "GCP Project ID"
  type        = string
  default     = "shadowtagai-core-stack"
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

# ============================================================================
# API Enablement
# ============================================================================

locals {
  required_apis = [
    "compute.googleapis.com",
    "container.googleapis.com",
    "aiplatform.googleapis.com",
    "artifactregistry.googleapis.com",
    "cloudkms.googleapis.com",
    "secretmanager.googleapis.com",
    "monitoring.googleapis.com",
    "logging.googleapis.com",
    "iam.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "binaryauthorization.googleapis.com",
  ]
}

resource "google_project_service" "required_apis" {
  for_each = toset(local.required_apis)
  project  = var.project_id
  service  = each.value

  disable_on_destroy = false
}

# ============================================================================
# KMS Encryption Key
# ============================================================================

resource "google_kms_key_ring" "shadowtagai_keyring" {
  name     = "shadowtagai-keyring"
  location = var.region
  project  = var.project_id

  depends_on = [google_project_service.required_apis]
}

resource "google_kms_crypto_key" "shadowtagai_key" {
  name            = "shadowtagai-key"
  key_ring        = google_kms_key_ring.shadowtagai_keyring.id
  rotation_period = "7776000s" # 90 days

  lifecycle {
    prevent_destroy = true
  }

  version_template {
    algorithm        = "GOOGLE_SYMMETRIC_ENCRYPTION"
    protection_level = "SOFTWARE"
  }

  depends_on = [google_kms_key_ring.shadowtagai_keyring]
}

# Grant Cloud Storage service account access to KMS key
resource "google_kms_crypto_key_iam_member" "storage_kms" {
  crypto_key_id = google_kms_crypto_key.shadowtagai_key.id
  role          = "roles/cloudkms.cryptoKeyEncrypterDecrypter"
  member        = "serviceAccount:service-${data.google_project.project.number}@gs-project-accounts.iam.gserviceaccount.com"
}

# ============================================================================
# Service Accounts
# ============================================================================

# Claude_Code_6 service account for GKE workloads
resource "google_service_account" "Claude_Code_6_sa" {
  account_id   = "Claude_Code_6"
  display_name = "Claude_Code_6 Service Account"
  description  = "Service account for Claude_Code_6 inference workloads"
  project      = var.project_id

  depends_on = [google_project_service.required_apis]
}

# Workbench service account
resource "google_service_account" "workbench_sa" {
  account_id   = "Claude_Code_6-workbench"
  display_name = "Claude_Code_6 Workbench Service Account"
  description  = "Service account for Vertex AI Workbench"
  project      = var.project_id

  depends_on = [google_project_service.required_apis]
}

# IAM bindings for Claude_Code_6 service account
resource "google_project_iam_member" "Claude_Code_6_vertex_user" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.Claude_Code_6_sa.email}"
}

resource "google_project_iam_member" "Claude_Code_6_storage_object_viewer" {
  project = var.project_id
  role    = "roles/storage.objectViewer"
  member  = "serviceAccount:${google_service_account.Claude_Code_6_sa.email}"
}

resource "google_project_iam_member" "Claude_Code_6_logging_writer" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.Claude_Code_6_sa.email}"
}

resource "google_project_iam_member" "Claude_Code_6_monitoring_writer" {
  project = var.project_id
  role    = "roles/monitoring.metricWriter"
  member  = "serviceAccount:${google_service_account.Claude_Code_6_sa.email}"
}

# ============================================================================
# Artifact Registry
# ============================================================================

resource "google_artifact_registry_repository" "Claude_Code_6" {
  provider      = google-beta
  location      = var.region
  repository_id = "Claude_Code_6"
  description   = "Docker repository for Claude_Code_6 container images"
  format        = "DOCKER"

  kms_key_name = google_kms_crypto_key.shadowtagai_key.id

  # Cleanup policy - delete images older than 30 days
  cleanup_policies {
    id     = "delete-old-images"
    action = "DELETE"

    condition {
      tag_state    = "UNTAGGED"
      older_than   = "2592000s" # 30 days in seconds
    }
  }

  # Keep at most 10 versions of each image
  cleanup_policies {
    id     = "keep-minimum-versions"
    action = "KEEP"

    most_recent_versions {
      keep_count = 10
    }
  }

  depends_on = [
    google_project_service.required_apis,
    google_kms_crypto_key_iam_member.storage_kms,
  ]
}

# Grant Claude_Code_6 SA permission to pull images
resource "google_artifact_registry_repository_iam_member" "Claude_Code_6_reader" {
  provider   = google-beta
  location   = google_artifact_registry_repository.Claude_Code_6.location
  repository = google_artifact_registry_repository.Claude_Code_6.name
  role       = "roles/artifactregistry.reader"
  member     = "serviceAccount:${google_service_account.Claude_Code_6_sa.email}"
}

# ============================================================================
# GCS Bucket for Model Artifacts
# ============================================================================

resource "google_storage_bucket" "model_artifacts" {
  name          = "${var.project_id}-model-artifacts"
  location      = var.region
  force_destroy = false

  uniform_bucket_level_access = true

  encryption {
    default_kms_key_name = google_kms_crypto_key.shadowtagai_key.id
  }

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      age = 90
    }
    action {
      type = "Delete"
    }
  }

  depends_on = [
    google_kms_crypto_key_iam_member.storage_kms,
  ]
}

# ============================================================================
# Vertex AI Resources
# ============================================================================

# Vertex AI Featurestore (if needed)
resource "google_vertex_ai_featurestore" "Claude_Code_6_featurestore" {
  provider = google-beta
  name     = "Claude_Code_6_featurestore"
  region   = var.region
  project  = var.project_id

  online_serving_config {
    fixed_node_count = 1
  }

  encryption_spec {
    kms_key_name = google_kms_crypto_key.shadowtagai_key.id
  }

  force_destroy = false

  depends_on = [
    google_project_service.required_apis,
    google_kms_crypto_key_iam_member.storage_kms,
  ]
}

# Vertex AI Model Registry (example placeholder)
# Note: Models are typically deployed via gcloud or Python SDK
# This is a placeholder showing the resource structure
resource "google_vertex_ai_endpoint" "Claude_Code_6_gemini" {
  provider     = google-beta
  name         = "Claude_Code_6-gemini"
  display_name = "Claude_Code_6 Gemini Endpoint"
  description  = "Endpoint for Claude_Code_6 Gemini model inference"
  region       = var.region
  project      = var.project_id

  encryption_spec {
    kms_key_name = google_kms_crypto_key.shadowtagai_key.id
  }

  depends_on = [
    google_project_service.required_apis,
    google_kms_crypto_key_iam_member.storage_kms,
  ]
}

# ============================================================================
# Vertex AI Workbench (Notebooks)
# ============================================================================

resource "google_notebooks_instance" "Claude_Code_6_workbench" {
  provider     = google-beta
  name         = "Claude_Code_6-workbench"
  location     = "${var.region}-a"
  machine_type = "n1-standard-4"

  vm_image {
    project      = "deeplearning-platform-release"
    image_family = "common-cpu-notebooks"
  }

  service_account = google_service_account.workbench_sa.email

  install_gpu_driver = false
  boot_disk_type     = "PD_SSD"
  boot_disk_size_gb  = 100

  no_public_ip    = false
  no_proxy_access = false

  network = "default"
  subnet  = "default"

  labels = {
    environment = var.environment
    component   = "workbench"
  }

  metadata = {
    terraform = "true"
  }

  depends_on = [
    google_project_service.required_apis,
    google_service_account.workbench_sa,
  ]
}

# ============================================================================
# Workload Identity Binding
# ============================================================================

# Bind Kubernetes SA to Google SA for Workload Identity
resource "google_service_account_iam_member" "Claude_Code_6_workload_identity" {
  service_account_id = google_service_account.Claude_Code_6_sa.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "serviceAccount:${var.project_id}.svc.id.goog[Claude_Code_6-system/Claude_Code_6-sa]"

  depends_on = [google_service_account.Claude_Code_6_sa]
}

# ============================================================================
# Data Sources
# ============================================================================

data "google_project" "project" {
  project_id = var.project_id
}

# ============================================================================
# Outputs
# ============================================================================

output "project_id" {
  description = "GCP Project ID"
  value       = var.project_id
}

output "region" {
  description = "GCP Region"
  value       = var.region
}

output "Claude_Code_6_service_account_email" {
  description = "Claude_Code_6 service account email"
  value       = google_service_account.Claude_Code_6_sa.email
}

output "workbench_service_account_email" {
  description = "Workbench service account email"
  value       = google_service_account.workbench_sa.email
}

output "artifact_registry_repository" {
  description = "Artifact Registry repository name"
  value       = google_artifact_registry_repository.Claude_Code_6.name
}

output "kms_key_id" {
  description = "KMS crypto key ID"
  value       = google_kms_crypto_key.shadowtagai_key.id
}

output "vertex_endpoint_id" {
  description = "Vertex AI endpoint ID"
  value       = google_vertex_ai_endpoint.Claude_Code_6_gemini.id
}

output "model_artifacts_bucket" {
  description = "GCS bucket for model artifacts"
  value       = google_storage_bucket.model_artifacts.name
}
