terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = "shadowtag-omega-v4"
  region  = "us-central1"
}

resource "google_cloud_run_v2_service" "mcp_service" {
  name     = "headfade-mcp"
  location = "us-central1"

  template {
    containers {
      image = "gcr.io/shadowtag-omega-v4/headfade-mcp:latest"
      resources {
        limits = {
          cpu    = "2"
          memory = "1024Mi"
        }
      }
    }
  }
}
