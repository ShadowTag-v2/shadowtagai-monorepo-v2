# ============================================
# HEADFADE MCP - TERRAFORM MODULE (INFRASTRUCTURE AS CODE)
# ============================================

terraform {
  required_version = ">= 1.5"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# ============================================
# VARIABLES
# ============================================
variable "project_id" {
  description = "GCP Project ID"
  type        = string
  default     = "shadowtag-omega-v4"
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

variable "service_name" {
  description = "Cloud Run service name"
  type        = string
  default     = "headfade-mcp"
}

# ============================================
# SECRETS
# ============================================
resource "google_secret_manager_secret" "stripe_secret_key" {
  secret_id = "STRIPE_SECRET_KEY"
  replication {
    automatic = true
  }
}

resource "google_secret_manager_secret" "stripe_webhook_secret" {
  secret_id = "STRIPE_WEBHOOK_SECRET"
  replication {
    automatic = true
  }
}

resource "google_secret_manager_secret" "sentry_dsn" {
  secret_id = "SENTRY_DSN"
  replication {
    automatic = true
  }
}

# ============================================
# SERVICE ACCOUNT
# ============================================
resource "google_service_account" "headfade_mcp_sa" {
  account_id   = "headfade-mcp-sa"
  display_name = "HeadFade MCP Service Account"
}

# Grant access to secrets
resource "google_secret_manager_secret_iam_member" "stripe_key_accessor" {
  secret_id = google_secret_manager_secret.stripe_secret_key.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.headfade_mcp_sa.email}"
}

resource "google_secret_manager_secret_iam_member" "stripe_webhook_accessor" {
  secret_id = google_secret_manager_secret.stripe_webhook_secret.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.headfade_mcp_sa.email}"
}

resource "google_secret_manager_secret_iam_member" "sentry_dsn_accessor" {
  secret_id = google_secret_manager_secret.sentry_dsn.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.headfade_mcp_sa.email}"
}

# ============================================
# CLOUD RUN SERVICE
# ============================================
resource "google_cloud_run_service" "headfade_mcp" {
  name     = var.service_name
  location = var.region

  template {
    spec {
      service_account_name = google_service_account.headfade_mcp_sa.email

      containers {
        image = "gcr.io/${var.project_id}/${var.service_name}:latest"

        ports {
          container_port = 8080
        }

        resources {
          limits = {
            cpu    = "1"
            memory = "1Gi"
          }
        }

        env {
          name  = "NODE_ENV"
          value = "production"
        }

        env {
          name  = "PORT"
          value = "8080"
        }

        # Secrets
        env {
          name = "STRIPE_SECRET_KEY"
          value_from {
            secret_key_ref {
              name = google_secret_manager_secret.stripe_secret_key.secret_id
              key  = "latest"
            }
          }
        }

        env {
          name = "STRIPE_WEBHOOK_SECRET"
          value_from {
            secret_key_ref {
              name = google_secret_manager_secret.stripe_webhook_secret.secret_id
              key  = "latest"
            }
          }
        }

        env {
          name = "SENTRY_DSN"
          value_from {
            secret_key_ref {
              name = google_secret_manager_secret.sentry_dsn.secret_id
              key  = "latest"
            }
          }
        }
      }

      # Scaling
      scaling {
        min_instance_count = 25
        max_instance_count = 500
      }

      # Concurrency
      container_concurrency = 80
    }

    metadata {
      annotations = {
        "autoscaling.knative.dev/minScale" = "25"
        "autoscaling.knative.dev/maxScale" = "500"
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

# Allow unauthenticated access
resource "google_cloud_run_service_iam_member" "public_access" {
  service  = google_cloud_run_service.headfade_mcp.name
  location = google_cloud_run_service.headfade_mcp.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# ============================================
# OUTPUTS
# ============================================
output "service_url" {
  value = google_cloud_run_service.headfade_mcp.status[0].url
}

output "service_account_email" {
  value = google_service_account.headfade_mcp_sa.email
}
```