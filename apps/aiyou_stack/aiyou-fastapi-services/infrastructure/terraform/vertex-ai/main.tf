# ═══════════════════════════════════════════════════════════════
# AIYOU PLATFORM - VERTEX AI INTEGRATION
# ═══════════════════════════════════════════════════════════════
# Purpose: Vertex AI Workload Identity, service accounts, and
#          Workbench setup for Judge #6 Layer 1 training
# ═══════════════════════════════════════════════════════════════

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }

  backend "gcs" {
    bucket = "aiyou-terraform-state"
    prefix = "vertex-ai"
  }
}

# ═══════════════════════════════════════════════════════════════
# DATA SOURCES
# ═══════════════════════════════════════════════════════════════

data "terraform_remote_state" "bootstrap" {
  backend = "gcs"
  config = {
    bucket = "aiyou-terraform-state"
    prefix = "bootstrap"
  }
}

data "terraform_remote_state" "base_platform" {
  backend = "gcs"
  config = {
    bucket = "aiyou-terraform-state"
    prefix = "base-platform"
  }
}

# ═══════════════════════════════════════════════════════════════
# VARIABLES
# ═══════════════════════════════════════════════════════════════

variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "Environment"
  type        = string
}

# ═══════════════════════════════════════════════════════════════
# WORKLOAD IDENTITY BINDING
# Allows K8s service accounts to impersonate GCP service accounts
# ═══════════════════════════════════════════════════════════════

# Kubernetes service account (to be created in K8s manifests)
locals {
  k8s_service_accounts = {
    judge_service = {
      namespace  = "judge-system"
      gcp_sa     = data.terraform_remote_state.bootstrap.outputs.vertex_ai_sa_email
      k8s_sa     = "judge-workload-sa"
    }
    gemini_service = {
      namespace  = "gemini-video"
      gcp_sa     = data.terraform_remote_state.bootstrap.outputs.vertex_ai_sa_email
      k8s_sa     = "gemini-workload-sa"
    }
    tensorlake_service = {
      namespace  = "tensorlake"
      gcp_sa     = data.terraform_remote_state.bootstrap.outputs.tensorlake_worker_sa_email
      k8s_sa     = "tensorlake-workload-sa"
    }
  }
}

# Bind Kubernetes SA to GCP SA (Vertex AI)
resource "google_service_account_iam_member" "workload_identity_vertex_ai" {
  for_each = local.k8s_service_accounts

  service_account_id = "projects/${var.project_id}/serviceAccounts/${each.value.gcp_sa}"
  role               = "roles/iam.workloadIdentityUser"

  member = "serviceAccount:${data.terraform_remote_state.base_platform.outputs.workload_identity_pool}[${each.value.namespace}/${each.value.k8s_sa}]"
}

# ═══════════════════════════════════════════════════════════════
# VERTEX AI STORAGE BUCKET
# For training data, model artifacts, and experiment tracking
# ═══════════════════════════════════════════════════════════════

resource "google_storage_bucket" "vertex_ai_artifacts" {
  name     = "${var.project_id}-vertex-ai-${var.environment}"
  location = var.region
  project  = var.project_id

  uniform_bucket_level_access = true
  force_destroy               = false

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

  labels = {
    environment = var.environment
    purpose     = "vertex-ai-artifacts"
  }
}

# Grant Vertex AI SA access to storage bucket
resource "google_storage_bucket_iam_member" "vertex_ai_bucket_access" {
  bucket = google_storage_bucket.vertex_ai_artifacts.name
  role   = "roles/storage.admin"
  member = "serviceAccount:${data.terraform_remote_state.bootstrap.outputs.vertex_ai_sa_email}"
}

# ═══════════════════════════════════════════════════════════════
# VERTEX AI TENSORBOARD INSTANCE
# For experiment tracking and visualization
# ═══════════════════════════════════════════════════════════════

resource "google_vertex_ai_tensorboard" "judge_training" {
  display_name = "judge-training-${var.environment}"
  description  = "Tensorboard for Judge #6 Layer 1 training experiments"
  project      = var.project_id
  region       = var.region

  labels = {
    environment = var.environment
    workload    = "judge-training"
  }
}

# ═══════════════════════════════════════════════════════════════
# VERTEX AI METADATA STORE
# For ML metadata and lineage tracking
# ═══════════════════════════════════════════════════════════════

resource "google_vertex_ai_metadata_store" "aiyou_ml_metadata" {
  name        = "aiyou-ml-metadata-${var.environment}"
  description = "ML metadata store for AiYOU platform"
  project     = var.project_id
  region      = var.region
}

# ═══════════════════════════════════════════════════════════════
# VERTEX AI FEATURE STORE (OPTIONAL)
# For serving features to Judge models
# ═══════════════════════════════════════════════════════════════

# Commented out for now - enable if needed for feature engineering
# resource "google_vertex_ai_featurestore" "judge_features" {
#   name   = "judge-features-${var.environment}"
#   region = var.region
#   project = var.project_id
#
#   online_serving_config {
#     fixed_node_count = 1
#   }
#
#   force_destroy = false
# }

# ═══════════════════════════════════════════════════════════════
# OUTPUTS
# ═══════════════════════════════════════════════════════════════

output "vertex_ai_bucket_name" {
  description = "Vertex AI artifacts bucket name"
  value       = google_storage_bucket.vertex_ai_artifacts.name
}

output "vertex_ai_bucket_url" {
  description = "Vertex AI artifacts bucket URL"
  value       = google_storage_bucket.vertex_ai_artifacts.url
}

output "tensorboard_name" {
  description = "Tensorboard instance name"
  value       = google_vertex_ai_tensorboard.judge_training.name
}

output "metadata_store_name" {
  description = "ML Metadata store name"
  value       = google_vertex_ai_metadata_store.aiyou_ml_metadata.name
}

output "workload_identity_bindings" {
  description = "Workload Identity bindings (K8s SA -> GCP SA)"
  value = {
    for k, v in local.k8s_service_accounts : k => {
      namespace   = v.namespace
      k8s_sa      = v.k8s_sa
      gcp_sa      = v.gcp_sa
    }
  }
}
