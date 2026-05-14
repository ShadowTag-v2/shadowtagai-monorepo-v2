locals {
  merged_labels = merge(
    {
      environment = var.environment
      managed_by  = "opentofu"
    },
    var.labels,
  )
}

resource "google_cloud_run_v2_service" "service" {
  name                = var.service_name
  location            = var.region
  project             = var.project_id
  deletion_protection = var.deletion_protection
  ingress             = "INGRESS_TRAFFIC_ALL"
  labels              = local.merged_labels

  template {
    execution_environment = "EXECUTION_ENVIRONMENT_GEN2"
    service_account       = var.service_account_email
    startup_cpu_boost     = var.startup_cpu_boost

    scaling {
      min_instance_count = var.min_instances
      max_instance_count = var.max_instances
    }

    containers {
      image = var.image

      resources {
        limits = {
          cpu    = var.cpu
          memory = var.memory
        }
      }

      ports {
        container_port = 8080
      }

      # Static env vars
      dynamic "env" {
        for_each = var.env_vars
        content {
          name  = env.key
          value = env.value
        }
      }

      # Secret Manager env vars (rotation-safe: pin to "latest")
      dynamic "env" {
        for_each = var.secrets
        content {
          name = env.value.env_var_name
          value_source {
            secret_key_ref {
              secret  = env.value.secret_id
              version = env.value.version
            }
          }
        }
      }

      # Volume mounts for Cloud SQL
      dynamic "volume_mounts" {
        for_each = { for i, v in var.cloud_sql_instances : "cloudsql-${i}" => v }
        content {
          name       = volume_mounts.key
          mount_path = "/cloudsql"
        }
      }

      startup_probe {
        http_get { path = "/healthz" }
        initial_delay_seconds = 10
        period_seconds        = 30
        timeout_seconds       = 10
        failure_threshold     = 3
      }

      liveness_probe {
        http_get { path = "/healthz" }
        initial_delay_seconds = 30
        period_seconds        = 30
        timeout_seconds       = 10
        failure_threshold     = 3
      }
    }

    # Cloud SQL volume definitions
    dynamic "volumes" {
      for_each = { for i, v in var.cloud_sql_instances : "cloudsql-${i}" => v }
      content {
        name = volumes.key
        cloud_sql_instance {
          instances = [volumes.value]
        }
      }
    }

    dynamic "vpc_access" {
      for_each = var.vpc_connector_id != null ? [1] : []
      content {
        connector = var.vpc_connector_id
        egress    = var.vpc_egress
      }
    }
  }

  dynamic "traffic" {
    for_each = var.traffic
    content {
      percent         = traffic.value.percent
      latest_revision = traffic.value.latest_revision
      revision        = traffic.value.revision
    }
  }
}

resource "google_cloud_run_v2_service_iam_member" "invoker_allusers" {
  count    = var.allow_unauthenticated ? 1 : 0
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.service.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

resource "google_project_iam_member" "cloudsql_client" {
  count   = length(var.cloud_sql_instances) > 0 && var.service_account_email != null ? 1 : 0
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${var.service_account_email}"
}
