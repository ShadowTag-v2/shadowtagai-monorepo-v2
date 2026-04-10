# OMNI-COMPILE BLOCK 2: SOVEREIGN STRUCTURE
# ----------------------------------------------------------------------------
# DOCTRINE: Pure Source-Based Deploy (No Docker Image URIs). Confidential Space.
# ----------------------------------------------------------------------------

provider "google" {
  project = "shadowtag-omega-v4"
  region  = "us-central1"
}

# Source-based Cloud Run Deployment (Resolves the Docker Image Conflict)
resource "google_cloud_run_v2_service" "omni_nexus" {
  name     = "shadowtag-omni-nexus"
  location = "us-central1"

  template {
    execution_environment = "EXECUTION_ENVIRONMENT_GEN2"

    # Ensuring Sovereign Isolation
    containers {
      image = "us-docker.pkg.dev/cloudrun/container/hello" # Placeholder until Cloud Build source push
      resources {
        limits = {
          cpu    = "4"
          memory = "16Gi"
        }
      }
      env {
        name  = "JUDGE_6_MODE"
        value = "STRICT_17_LAYER"
      }
      env {
        name  = "CLAUDE_LEAK_MODE"
        value = "A11Y_TREE_EXTRACTION"
      }
    }
  }

  # Neutralize Zero-Day Network Access
  ingress = "INGRESS_TRAFFIC_INTERNAL_ONLY"
}

# MILDEC Honeypot Logging
resource "google_logging_project_sink" "mildec_sink" {
  name                   = "mildec-honeypot-sink"
  destination            = "storage.googleapis.com/shadowtag-mildec-vault"
  filter                 = "jsonPayload.event_type=\"SECURITY_VIOLATION\""
  unique_writer_identity = true
}
