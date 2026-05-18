# Copyright 2026 ShadowTag AI — All Rights Reserved.
# sidecar.tf — gVisor Sandboxing & VPC Target for Ralph Loop
#
# Terraform module for deploying the CounselConduit sidecar proxy
# with gVisor sandboxing on Cloud Run. Implements VPC egress for
# the Ralph Loop (recursive LLM audit pipeline).

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"
    }
  }
}

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

variable "vpc_connector_name" {
  description = "VPC Access Connector for private networking"
  type        = string
  default     = "counselconduit-vpc"
}

# ─── VPC Access Connector (Private egress for Ralph Loop) ─────────

resource "google_vpc_access_connector" "sidecar_connector" {
  name          = var.vpc_connector_name
  project       = var.project_id
  region        = var.region
  ip_cidr_range = "10.8.0.0/28"
  network       = "default"

  min_instances = 2
  max_instances = 3

  machine_type = "e2-micro"
}

# ─── Cloud Run Sidecar Service (gVisor Sandbox) ──────────────────

resource "google_cloud_run_v2_service" "sidecar_proxy" {
  name     = "counselconduit-sidecar"
  project  = var.project_id
  location = var.region
  ingress  = "INGRESS_TRAFFIC_INTERNAL_ONLY"

  template {
    # gVisor sandbox execution environment
    execution_environment = "EXECUTION_ENVIRONMENT_GEN2"

    scaling {
      min_instance_count = 0
      max_instance_count = 5
    }

    vpc_access {
      connector = google_vpc_access_connector.sidecar_connector.id
      egress    = "ALL_TRAFFIC"
    }

    containers {
      image = "gcr.io/${var.project_id}/counselconduit-sidecar:latest"

      ports {
        container_port = 8080
      }

      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
        cpu_idle          = true
        startup_cpu_boost = true
      }

      env {
        name  = "GCP_PROJECT"
        value = var.project_id
      }

      env {
        name  = "RALPH_LOOP_ENABLED"
        value = "true"
      }

      env {
        name  = "GVISOR_SANDBOX"
        value = "true"
      }

      # Secrets from GCP Secret Manager
      env {
        name = "GEMINI_API_KEY"
        value_source {
          secret_key_ref {
            secret  = "gemini-api-key"
            version = "latest"
          }
        }
      }
    }

    service_account = "counselconduit-sa@${var.project_id}.iam.gserviceaccount.com"
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }

  depends_on = [google_vpc_access_connector.sidecar_connector]
}

# ─── IAM: Allow main service to invoke sidecar ────────────────────

resource "google_cloud_run_v2_service_iam_member" "sidecar_invoker" {
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.sidecar_proxy.name
  role     = "roles/run.invoker"
  member   = "serviceAccount:counselconduit-sa@${var.project_id}.iam.gserviceaccount.com"
}

# ─── Outputs ──────────────────────────────────────────────────────

output "sidecar_url" {
  description = "Internal URL of the sidecar proxy"
  value       = google_cloud_run_v2_service.sidecar_proxy.uri
}

output "vpc_connector_id" {
  description = "VPC Access Connector ID"
  value       = google_vpc_access_connector.sidecar_connector.id
}
