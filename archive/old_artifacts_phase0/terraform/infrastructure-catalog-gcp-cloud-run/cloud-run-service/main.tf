# Cloud Run Gen2 Service Module
# Extracted from cloud-foundation-fabric patterns + ShadowTag defaults

resource "google_cloud_run_v2_service" "main" {
  project  = var.project_id
  location = var.region
  name     = var.service_name
  ingress  = var.ingress

  template {
    scaling {
      min_instance_count = var.min_instances
      max_instance_count = var.max_instances
    }

    service_account = var.service_account != "" ? var.service_account : null

    dynamic "vpc_access" {
      for_each = var.vpc_connector != "" ? [1] : []
      content {
        connector = var.vpc_connector
        egress    = "PRIVATE_RANGES_ONLY"
      }
    }

    max_instance_request_concurrency = var.concurrency
    execution_environment            = "EXECUTION_ENVIRONMENT_GEN2"

    containers {
      image = var.image

      resources {
        limits = {
          cpu    = var.cpu
          memory = var.memory
        }
        startup_cpu_boost = var.startup_cpu_boost
      }

      # Plain environment variables
      dynamic "env" {
        for_each = merge(var.env_vars, {
          OTEL_EXPORTER_OTLP_ENDPOINT  = "https://monitoring.googleapis.com:443"
          OTEL_RESOURCE_ATTRIBUTES     = "service.name=${var.service_name},deployment.environment=${var.env}"
          OTEL_TRACES_SAMPLER          = "parentbased_traceidratio"
          OTEL_TRACES_SAMPLER_ARG      = var.trace_sample_rate
        })
        content {
          name  = env.key
          value = env.value
        }
      }

      # Secret Manager environment variables
      dynamic "env" {
        for_each = var.secret_env_vars
        content {
          name = env.key
          value_source {
            secret_key_ref {
              secret  = split(":", env.value)[0]
              version = try(split(":", env.value)[1], "latest")
            }
          }
        }
      }

      # Startup probe
      startup_probe {
        http_get {
          path = var.health_check_path
        }
        initial_delay_seconds = 5
        period_seconds        = 10
        failure_threshold     = 3
        timeout_seconds       = 5
      }

      # Liveness probe
      liveness_probe {
        http_get {
          path = var.health_check_path
        }
        period_seconds    = 30
        failure_threshold = 3
        timeout_seconds   = 5
      }
    }
  }

  labels = {
    environment = var.env
    managed_by  = "opentofu"
    service     = var.service_name
  }

  lifecycle {
    ignore_changes = [
      # Allow Cloud Deploy to manage traffic splits
      template[0].labels,
    ]
  }
}
