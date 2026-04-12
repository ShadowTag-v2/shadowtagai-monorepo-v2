resource "google_cloud_run_v2_service" "default" {
  name     = var.service_name
  location = var.deployment_region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    scaling {
      min_instance_count = 0
      max_instance_count = 10
    }

    containers {
      name  = "server-container"
      # Using existing image to bootstrap Terraform state
      image = "us-central1-docker.pkg.dev/absolute-totem-478701-v1/cloud-run-source-deploy/aiyou-fastapi-services/n-autoresearch/Kosmos/BioAgentss-server:ccf2bc5d5c8fee74d38886a32a11a524d4923740"

      ports {
        container_port = 8080
      }

      resources {
        limits = {
          cpu    = "1000m"
          memory = "512Mi"
        }
      }



      env {
        name  = "PYTHONPATH"
        value = "/app"
      }
    }
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }
}
