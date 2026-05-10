# infra/terraform/modules/counselconduit_phase3/main.tf
#
# Phase 3 Terraform module for CounselConduit sandbox infrastructure.
# Creates:
#   - Cloud Run Job for sandbox execution
#   - Secret Manager secrets for BYOK keys
#   - VPC connector for network isolation
#   - IAM bindings for sandbox SA

terraform {
  required_version = ">= 1.5"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"
    }
  }
}

variable "project_id" {
  type        = string
  default     = "shadowtag-omega-v4"
  description = "GCP project ID"
}

variable "region" {
  type        = string
  default     = "us-central1"
  description = "GCP region"
}

variable "sandbox_image" {
  type        = string
  default     = "us-central1-docker.pkg.dev/shadowtag-omega-v4/counselconduit/sandbox-runner:latest"
  description = "Container image for sandbox execution"
}

# ── Service Account for Sandbox ──

resource "google_service_account" "sandbox_sa" {
  account_id   = "cc-sandbox-runner"
  display_name = "CounselConduit Sandbox Runner"
  project      = var.project_id
}

resource "google_project_iam_member" "sandbox_secret_accessor" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.sandbox_sa.email}"
}

resource "google_project_iam_member" "sandbox_firestore_user" {
  project = var.project_id
  role    = "roles/datastore.user"
  member  = "serviceAccount:${google_service_account.sandbox_sa.email}"
}

# ── Cloud Run Job for sandbox execution ──

resource "google_cloud_run_v2_job" "sandbox_runner" {
  name     = "cc-sandbox-runner"
  location = var.region
  project  = var.project_id

  template {
    template {
      containers {
        image = var.sandbox_image

        resources {
          limits = {
            cpu    = "1"
            memory = "512Mi"
          }
        }

        env {
          name  = "SANDBOX_MODE"
          value = "true"
        }
        env {
          name  = "GCP_PROJECT"
          value = var.project_id
        }
      }

      service_account = google_service_account.sandbox_sa.email
      timeout         = "300s"
      max_retries     = 1

      # Network isolation — no VPC access by default
      # Enterprise tier gets VPC connector at runtime
    }

    task_count = 1
  }

  lifecycle {
    ignore_changes = [
      template[0].template[0].containers[0].image,
    ]
  }
}

# ── Secret Manager for BYOK keys ──

resource "google_secret_manager_secret" "byok_keys" {
  secret_id = "cc-byok-keys"
  project   = var.project_id

  replication {
    auto {}
  }

  labels = {
    purpose = "byok"
    service = "counselconduit"
  }
}

# ── Outputs ──

output "sandbox_sa_email" {
  value       = google_service_account.sandbox_sa.email
  description = "Sandbox runner service account email"
}

output "sandbox_job_name" {
  value       = google_cloud_run_v2_job.sandbox_runner.name
  description = "Cloud Run Job name for sandbox execution"
}

output "byok_secret_name" {
  value       = google_secret_manager_secret.byok_keys.name
  description = "Secret Manager secret for BYOK keys"
}
