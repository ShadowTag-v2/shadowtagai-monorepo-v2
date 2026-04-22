provider "google" {
  project = "shadowtag-omega-v4"
  region  = "us-central1"
}

# ------------------------------------------------------------------------------
# 1. WORKER SERVICE (Python Brain) - Private
# ------------------------------------------------------------------------------
resource "google_cloud_run_v2_service" "worker" {
  name     = "n-autoresearch/Kosmos/BioAgentss-worker"
  location = "us-central1"
  ingress = "INGRESS_TRAFFIC_INTERNAL_ONLY" # Private

  template {
    containers {
      image = "us-central1-docker.pkg.dev/shadowtag-omega-v4/cloud-run-source-deploy/n-autoresearch/Kosmos/BioAgentss-worker:latest"
      resources {
        limits = {
          cpu    = "2"
          memory = "4Gi"
        }
      }
    }
    scaling {
      max_instance_count = 100
      min_instance_count = 0 # Scale to zero
    }
  }
}

# ------------------------------------------------------------------------------
# 2. GATEWAY SERVICE (Go Shell) - Public
# ------------------------------------------------------------------------------
resource "google_cloud_run_v2_service" "gateway" {
  name     = "n-autoresearch/Kosmos/BioAgentss-gateway"
  location = "us-central1"
  ingress = "INGRESS_TRAFFIC_ALL" # Public

  template {
    containers {
      image = "us-central1-docker.pkg.dev/shadowtag-omega-v4/cloud-run-source-deploy/n-autoresearch/Kosmos/BioAgentss-gateway:latest"
      env {
        name  = "WORKER_URL"
        value = google_cloud_run_v2_service.worker.uri
      }
      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
      }
    }
    scaling {
      max_instance_count = 100
      min_instance_count = 1 # Keep one warm for speed? Or 0 for cost? 1 for "Best Performance"
    }
  }
}

# ------------------------------------------------------------------------------
# 3. PUBLIC ACCESS (IAM)
# ------------------------------------------------------------------------------
data "google_iam_policy" "noauth" {
  binding {
    role = "roles/run.invoker"
    members = [
      "allUsers",
    ]
  }
}

resource "google_cloud_run_service_iam_policy" "gateway_noauth" {
  location    = google_cloud_run_v2_service.gateway.location
  project     = google_cloud_run_v2_service.gateway.project
  service     = google_cloud_run_v2_service.gateway.name
  policy_data = data.google_iam_policy.noauth.policy_data
}
