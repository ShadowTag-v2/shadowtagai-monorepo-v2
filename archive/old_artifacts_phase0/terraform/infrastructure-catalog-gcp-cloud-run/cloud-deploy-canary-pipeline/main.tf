# Cloud Deploy Canary Pipeline Module
# Progressive traffic rollout: 25% → 50% → 75% → 100%

variable "project_id" {
  type        = string
  description = "GCP project ID."
}

variable "region" {
  type        = string
  default     = "us-central1"
  description = "GCP region."
}

variable "service_name" {
  type        = string
  description = "Cloud Run service name."
}

variable "canary_percentages" {
  type        = list(number)
  default     = [25, 50, 75]
  description = "Progressive canary percentages before full rollout."
}

variable "verify" {
  type        = bool
  default     = true
  description = "Enable canary verification at each stage."
}

resource "google_clouddeploy_delivery_pipeline" "canary" {
  project  = var.project_id
  location = var.region
  name     = "${var.service_name}-canary"

  serial_pipeline {
    stages {
      target_id = google_clouddeploy_target.prod.name
      strategy {
        canary {
          runtime_config {
            cloud_run {
              automatic_traffic_control = true
            }
          }
          canary_deployment {
            percentages = var.canary_percentages
            verify      = var.verify
          }
        }
      }
    }
  }

  labels = {
    managed_by  = "opentofu"
    service     = var.service_name
    environment = "prod"
  }
}

resource "google_clouddeploy_target" "prod" {
  project  = var.project_id
  location = var.region
  name     = "${var.service_name}-prod"

  run {
    location = "projects/${var.project_id}/locations/${var.region}"
  }

  labels = {
    managed_by  = "opentofu"
    environment = "prod"
  }
}

output "pipeline_name" {
  value       = google_clouddeploy_delivery_pipeline.canary.name
  description = "Cloud Deploy pipeline name."
}

output "target_name" {
  value       = google_clouddeploy_target.prod.name
  description = "Cloud Deploy target name."
}
