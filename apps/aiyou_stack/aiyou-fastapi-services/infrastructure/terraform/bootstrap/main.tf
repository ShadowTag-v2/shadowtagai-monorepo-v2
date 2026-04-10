# ═══════════════════════════════════════════════════════════════
# AIYOU PLATFORM - GKE BOOTSTRAP INFRASTRUCTURE
# ═══════════════════════════════════════════════════════════════
# Purpose: Bootstrap GCP project with required APIs, service accounts,
#          and IAM bindings before GKE cluster deployment
# ═══════════════════════════════════════════════════════════════

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

  backend "gcs" {
    bucket = "aiyou-terraform-state"
    prefix = "bootstrap"
  }
}

# ═══════════════════════════════════════════════════════════════
# VARIABLES
# ═══════════════════════════════════════════════════════════════

variable "project_id" {
  description = "GCP project ID for AiYOU platform"
  type        = string
}

variable "region" {
  description = "Primary GCP region"
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod"
  }
}

# ═══════════════════════════════════════════════════════════════
# PROVIDER CONFIGURATION
# ═══════════════════════════════════════════════════════════════

provider "google" {
  project = var.project_id
  region  = var.region
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
}

# ═══════════════════════════════════════════════════════════════
# ENABLE REQUIRED GCP APIs
# ═══════════════════════════════════════════════════════════════

locals {
  required_apis = [
    "compute.googleapis.com",              # Compute Engine
    "container.googleapis.com",            # Google Kubernetes Engine
    "containerregistry.googleapis.com",    # Container Registry
    "artifactregistry.googleapis.com",     # Artifact Registry (modern)
    "cloudresourcemanager.googleapis.com", # Resource Manager
    "iam.googleapis.com",                  # IAM
    "servicenetworking.googleapis.com",    # VPC peering
    "cloudkms.googleapis.com",             # KMS (encryption)
    "logging.googleapis.com",              # Cloud Logging
    "monitoring.googleapis.com",           # Cloud Monitoring
    "aiplatform.googleapis.com",           # Vertex AI
    "notebooks.googleapis.com",            # Vertex AI Workbench
    "storage-api.googleapis.com",          # Cloud Storage
    "storage-component.googleapis.com",    # GCS components
    "redis.googleapis.com",                # Memorystore Redis
    "sqladmin.googleapis.com",             # Cloud SQL
    "secretmanager.googleapis.com",        # Secret Manager
    "certificatemanager.googleapis.com",   # Certificate Manager
  ]
}

resource "google_project_service" "required_apis" {
  for_each = toset(local.required_apis)

  project = var.project_id
  service = each.value

  disable_on_destroy         = false
  disable_dependent_services = false
}

# ═══════════════════════════════════════════════════════════════
# SERVICE ACCOUNTS
# ═══════════════════════════════════════════════════════════════

# GKE Cluster Service Account
resource "google_service_account" "gke_cluster" {
  account_id   = "gke-cluster-${var.environment}"
  display_name = "GKE Cluster Service Account (${var.environment})"
  description  = "Service account for GKE cluster control plane"
  project      = var.project_id

  depends_on = [google_project_service.required_apis]
}

# GKE Node Pool Service Account (default)
resource "google_service_account" "gke_nodes" {
  account_id   = "gke-nodes-${var.environment}"
  display_name = "GKE Node Pool Service Account (${var.environment})"
  description  = "Default service account for GKE node pools"
  project      = var.project_id

  depends_on = [google_project_service.required_apis]
}

# Vertex AI Workload Identity Service Account
resource "google_service_account" "vertex_ai_workload" {
  account_id   = "vertex-ai-workload-${var.environment}"
  display_name = "Vertex AI Workload Identity (${var.environment})"
  description  = "Service account for Vertex AI workloads running in GKE"
  project      = var.project_id

  depends_on = [google_project_service.required_apis]
}

# TensorLake Worker Service Account
resource "google_service_account" "tensorlake_worker" {
  account_id   = "tensorlake-worker-${var.environment}"
  display_name = "TensorLake Worker Service Account (${var.environment})"
  description  = "Service account for TensorLake document processing workers"
  project      = var.project_id

  depends_on = [google_project_service.required_apis]
}

# NS Mesh Router Service Account
resource "google_service_account" "ns_mesh_router" {
  account_id   = "ns-mesh-router-${var.environment}"
  display_name = "NS Mesh Router Service Account (${var.environment})"
  description  = "Service account for NS mesh routing layer (<100μs latency)"
  project      = var.project_id

  depends_on = [google_project_service.required_apis]
}

# ═══════════════════════════════════════════════════════════════
# IAM ROLE BINDINGS - GKE Cluster SA
# ═══════════════════════════════════════════════════════════════

resource "google_project_iam_member" "gke_cluster_logging" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.gke_cluster.email}"
}

resource "google_project_iam_member" "gke_cluster_monitoring" {
  project = var.project_id
  role    = "roles/monitoring.metricWriter"
  member  = "serviceAccount:${google_service_account.gke_cluster.email}"
}

# ═══════════════════════════════════════════════════════════════
# IAM ROLE BINDINGS - GKE Nodes SA
# ═══════════════════════════════════════════════════════════════

resource "google_project_iam_member" "gke_nodes_logging" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.gke_nodes.email}"
}

resource "google_project_iam_member" "gke_nodes_monitoring" {
  project = var.project_id
  role    = "roles/monitoring.metricWriter"
  member  = "serviceAccount:${google_service_account.gke_nodes.email}"
}

resource "google_project_iam_member" "gke_nodes_metrics" {
  project = var.project_id
  role    = "roles/monitoring.viewer"
  member  = "serviceAccount:${google_service_account.gke_nodes.email}"
}

resource "google_project_iam_member" "gke_nodes_artifact_registry" {
  project = var.project_id
  role    = "roles/artifactregistry.reader"
  member  = "serviceAccount:${google_service_account.gke_nodes.email}"
}

# ═══════════════════════════════════════════════════════════════
# IAM ROLE BINDINGS - Vertex AI Workload SA
# ═══════════════════════════════════════════════════════════════

resource "google_project_iam_member" "vertex_ai_user" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.vertex_ai_workload.email}"
}

resource "google_project_iam_member" "vertex_ai_model_user" {
  project = var.project_id
  role    = "roles/aiplatform.modelUser"
  member  = "serviceAccount:${google_service_account.vertex_ai_workload.email}"
}

resource "google_project_iam_member" "vertex_ai_storage" {
  project = var.project_id
  role    = "roles/storage.objectViewer"
  member  = "serviceAccount:${google_service_account.vertex_ai_workload.email}"
}

# ═══════════════════════════════════════════════════════════════
# IAM ROLE BINDINGS - TensorLake Worker SA
# ═══════════════════════════════════════════════════════════════

resource "google_project_iam_member" "tensorlake_storage_admin" {
  project = var.project_id
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${google_service_account.tensorlake_worker.email}"
}

resource "google_project_iam_member" "tensorlake_secret_accessor" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.tensorlake_worker.email}"
}

# ═══════════════════════════════════════════════════════════════
# IAM ROLE BINDINGS - NS Mesh Router SA
# ═══════════════════════════════════════════════════════════════

resource "google_project_iam_member" "ns_mesh_redis_admin" {
  project = var.project_id
  role    = "roles/redis.admin"
  member  = "serviceAccount:${google_service_account.ns_mesh_router.email}"
}

resource "google_project_iam_member" "ns_mesh_monitoring" {
  project = var.project_id
  role    = "roles/monitoring.metricWriter"
  member  = "serviceAccount:${google_service_account.ns_mesh_router.email}"
}

# ═══════════════════════════════════════════════════════════════
# ARTIFACT REGISTRY FOR CONTAINER IMAGES
# ═══════════════════════════════════════════════════════════════

resource "google_artifact_registry_repository" "container_images" {
  location      = var.region
  repository_id = "aiyou-containers-${var.environment}"
  description   = "Container images for AiYOU platform (${var.environment})"
  format        = "DOCKER"
  project       = var.project_id

  depends_on = [google_project_service.required_apis]
}

# ═══════════════════════════════════════════════════════════════
# KMS KEY RING FOR ENCRYPTION
# ═══════════════════════════════════════════════════════════════

resource "google_kms_key_ring" "aiyou" {
  name     = "aiyou-${var.environment}"
  location = var.region
  project  = var.project_id

  depends_on = [google_project_service.required_apis]
}

resource "google_kms_crypto_key" "gke_secrets" {
  name     = "gke-secrets-${var.environment}"
  key_ring = google_kms_key_ring.aiyou.id

  purpose = "ENCRYPT_DECRYPT"

  lifecycle {
    prevent_destroy = true
  }
}

resource "google_kms_crypto_key_iam_member" "gke_secrets_encrypter" {
  crypto_key_id = google_kms_crypto_key.gke_secrets.id
  role          = "roles/cloudkms.cryptoKeyEncrypterDecrypter"
  member        = "serviceAccount:service-${data.google_project.project.number}@container-engine-robot.iam.gserviceaccount.com"
}

# ═══════════════════════════════════════════════════════════════
# DATA SOURCES
# ═══════════════════════════════════════════════════════════════

data "google_project" "project" {
  project_id = var.project_id
}

# ═══════════════════════════════════════════════════════════════
# OUTPUTS
# ═══════════════════════════════════════════════════════════════

output "project_id" {
  description = "GCP project ID"
  value       = var.project_id
}

output "project_number" {
  description = "GCP project number"
  value       = data.google_project.project.number
}

output "gke_cluster_sa_email" {
  description = "GKE cluster service account email"
  value       = google_service_account.gke_cluster.email
}

output "gke_nodes_sa_email" {
  description = "GKE nodes service account email"
  value       = google_service_account.gke_nodes.email
}

output "vertex_ai_sa_email" {
  description = "Vertex AI workload service account email"
  value       = google_service_account.vertex_ai_workload.email
}

output "tensorlake_worker_sa_email" {
  description = "TensorLake worker service account email"
  value       = google_service_account.tensorlake_worker.email
}

output "ns_mesh_router_sa_email" {
  description = "NS mesh router service account email"
  value       = google_service_account.ns_mesh_router.email
}

output "artifact_registry_url" {
  description = "Artifact Registry repository URL"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.container_images.repository_id}"
}

output "kms_key_ring_id" {
  description = "KMS key ring ID"
  value       = google_kms_key_ring.aiyou.id
}

output "gke_secrets_key_id" {
  description = "GKE secrets encryption key ID"
  value       = google_kms_crypto_key.gke_secrets.id
}
