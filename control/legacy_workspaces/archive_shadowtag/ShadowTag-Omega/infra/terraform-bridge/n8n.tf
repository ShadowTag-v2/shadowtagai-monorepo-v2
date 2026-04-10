provider "google" {
  project = "shadowtag-omega-v2"
  region  = "us-central1"
}

resource "google_cloud_run_v2_service" "n8n" {
  name     = "n8n-server"
  location = "us-central1"
  ingress = "INGRESS_TRAFFIC_ALL"

  template {
    containers {
      image = "docker.io/n8nio/n8n:latest"
      
      ports {
        container_port = 5678
      }

      env {
        name  = "N8N_PORT"
        value = "5678"
      }
      
      env {
        name  = "N8N_HOST"
        value = "n8n-server-s2its66sea-uc.a.run.app" 
      }
      
      env {
        name = "N8N_PROTOCOL"
        value = "https"
      }

      resources {
        limits = {
          cpu    = "1000m"
          memory = "1024Mi"
        }
      }
    }
  }
}

output "n8n_url" {
  value = google_cloud_run_v2_service.n8n.uri
}
