# infra/terraform/secrets.tf
# Terraform module for Secret Manager infrastructure.
# terraform init && terraform plan -var-file=prod.tfvars
#
# NOTE: This is declarative IaC for the existing Secret Manager secrets.
# All secrets were created via gcloud CLI and this codifies them.

terraform {
  required_version = ">= 1.5"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 5.0"
    }
  }
  backend "gcs" {
    bucket = "shadowtag-omega-v4-terraform-state"
    prefix = "secrets/terraform/state"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

variable "project_id" {
  description = "GCP project ID"
  type        = string
  default     = "shadowtag-omega-v4"
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "us-central1"
}

# ── Service Accounts ──────────────────────────────────────────────────────

variable "production_sa" {
  description = "Production Cloud Run SA"
  type        = string
  default     = "counselconduit-sa@shadowtag-omega-v4.iam.gserviceaccount.com"
}

variable "staging_sa" {
  description = "Staging Cloud Run SA"
  type        = string
  default     = "counselconduit-staging-sa@shadowtag-omega-v4.iam.gserviceaccount.com"
}

# ── Secrets ───────────────────────────────────────────────────────────────

locals {
  # Secrets that Cloud Run services need access to
  app_secrets = [
    "stripe-secret-key",
    "stripe-webhook-secret",
    "stripe-publishable-key",
    "gemini-api-key",
    "stitch-api-key",
    "developer-knowledge-api-key",
  ]

  # Infrastructure secrets (not exposed to Cloud Run)
  infra_secrets = [
    "devconnect-github-app-key",
    "devconnect-github-webhook",
    "temporal-api-key",
    "hugging-face-token",
    "envoy-conf",
    "otel-conf",
  ]
}

# Import existing secrets (these already exist in SM)
# Run: terraform import google_secret_manager_secret.app["stripe-secret-key"] projects/shadowtag-omega-v4/secrets/stripe-secret-key
resource "google_secret_manager_secret" "app" {
  for_each  = toset(local.app_secrets)
  secret_id = each.key
  project   = var.project_id

  replication {
    auto {}
  }

  labels = {
    environment = "production"
    managed_by  = "terraform"
    team        = "counselconduit"
  }

  # Rotation: 90 days for Stripe keys
  dynamic "rotation" {
    for_each = startswith(each.key, "stripe-") ? [1] : []
    content {
      rotation_period    = "7776000s" # 90 days
      next_rotation_time = "2026-07-18T00:00:00Z"
    }
  }
}

# Grant production SA access to app secrets
resource "google_secret_manager_secret_iam_member" "prod_accessor" {
  for_each  = toset(local.app_secrets)
  project   = var.project_id
  secret_id = google_secret_manager_secret.app[each.key].secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${var.production_sa}"
}

# Grant staging SA access to app secrets
resource "google_secret_manager_secret_iam_member" "staging_accessor" {
  for_each  = toset(local.app_secrets)
  project   = var.project_id
  secret_id = google_secret_manager_secret.app[each.key].secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${var.staging_sa}"
}

# ── Monitoring Alert: Secret Access Anomaly ──────────────────────────────

resource "google_monitoring_alert_policy" "secret_access_anomaly" {
  display_name = "Secret Manager Access Anomaly"
  project      = var.project_id
  combiner     = "OR"

  conditions {
    display_name = "Unusual secret access volume"
    condition_threshold {
      filter          = "resource.type=\"audited_resource\" AND protoPayload.serviceName=\"secretmanager.googleapis.com\""
      comparison      = "COMPARISON_GT"
      threshold_value = 100
      duration        = "300s"

      aggregations {
        alignment_period   = "300s"
        per_series_aligner = "ALIGN_COUNT"
      }
    }
  }

  notification_channels = []

  alert_strategy {
    auto_close = "604800s"
  }
}

# ── Outputs ──────────────────────────────────────────────────────────────

output "managed_secrets" {
  description = "List of managed secret IDs"
  value       = [for s in google_secret_manager_secret.app : s.secret_id]
}
