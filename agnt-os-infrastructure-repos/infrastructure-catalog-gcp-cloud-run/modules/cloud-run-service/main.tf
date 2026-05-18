resource "google_cloud_run_v2_service" "service" {
  name     = var.service_name
  location = var.region
  project  = var.project_id

  template {
    execution_environment = "EXECUTION_ENVIRONMENT_GEN2"
    startup_cpu_boost     = true

    containers {
      image = var.image
      resources { limits = { cpu = var.cpu, memory = var.memory } }

      startup_probe {
        http_get { path = "/healthz" }
        initial_delay_seconds = 10
        period_seconds        = 30
      }
    }
  }

  traffic {
    for_each = var.traffic
    percent         = each.value.percent
    latest_revision = each.value.latest_revision
  }
}
