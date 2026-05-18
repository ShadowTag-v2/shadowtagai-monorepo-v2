resource "google_clouddeploy_delivery_pipeline" "pipeline" {
  name     = "${var.name}-pipeline"
  location = var.region
  project  = var.project_id

  serial_pipeline {
    stages {
      target_id = google_clouddeploy_target.run_target.name
      strategy {
        canary {
          runtime_config { cloud_run { automatic_traffic_control = true } }
          canary_deployment {
            percentages = var.percentages
            verify      = var.verify
          }
        }
      }
    }
  }
}
