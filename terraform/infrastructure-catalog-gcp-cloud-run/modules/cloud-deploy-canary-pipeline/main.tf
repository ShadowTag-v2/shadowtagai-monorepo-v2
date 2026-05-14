resource "google_clouddeploy_target" "run_target" {
  location = var.region
  name     = "${var.name}-target"
  project  = var.project_id

  run {
    location = var.region
  }

  labels = {
    managed_by = "opentofu"
    service    = var.cloud_run_service_name
  }
}

resource "google_clouddeploy_delivery_pipeline" "pipeline" {
  location    = var.region
  name        = "${var.name}-pipeline"
  project     = var.project_id
  description = var.description

  serial_pipeline {
    stages {
      target_id = google_clouddeploy_target.run_target.name
      profiles  = ["default"]

      strategy {
        canary {
          runtime_config {
            cloud_run {
              automatic_traffic_control = true
            }
          }
          canary_deployment {
            percentages = var.percentages
            verify      = var.verify
          }
        }
      }
    }
  }

  labels = {
    managed_by = "opentofu"
    service    = var.cloud_run_service_name
  }
}
