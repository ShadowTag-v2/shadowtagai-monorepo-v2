terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

variable "project_id" {
  description = "Your GCP Project ID"
  type        = string
}

variable "region" {
  default = "us-central1"
}

# 1. Enable Required GCP APIs
resource "google_project_service" "required_apis" {
  for_each = toset([
    "run.googleapis.com",
    "aiplatform.googleapis.com",
    "secretmanager.googleapis.com",
    "iam.googleapis.com"
  ])
  service            = each.key
  disable_on_destroy = false
}

# 2. Create the Sovereign Identity (Service Account)
resource "google_service_account" "antigravity_sa" {
  account_id   = "antigravity-sovereign-sa"
  display_name = "Antigravity Sovereign Enclave Identity"
  depends_on   = [google_project_service.required_apis]
}

# 3. Grant Minimum Required IAM Roles
resource "google_project_iam_member" "vertex_user" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.antigravity_sa.email}"
}

resource "google_project_iam_member" "secret_accessor" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.antigravity_sa.email}"
}

# 4. Provision the Secure GCS Bucket (For FUSE Mount & Artifacts)
resource "google_storage_bucket" "antigravity_workspace" {
  name                        = "${var.project_id}-antigravity-workspace"
  location                    = var.region
  uniform_bucket_level_access = true
  force_destroy               = false

  # Optional: Enforce FedRAMP Customer-Managed Encryption Keys (CMEK) here
  # encryption { default_kms_key_name = "your-kms-key-id" }
}

# 5. Grant Storage Admin strictly to the Antigravity SA
resource "google_storage_bucket_iam_member" "workspace_admin" {
  bucket = google_storage_bucket.antigravity_workspace.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.antigravity_sa.email}"
}

# 6. The Cloud Run Gen 2 Enclave
resource "google_cloud_run_v2_service" "antigravity_engine" {
  name     = "antigravity-engine"
  location = var.region
  ingress  = "INGRESS_TRAFFIC_INTERNAL_ONLY" # Lock down ingress to VPC/Load Balancer

  template {
    service_account = google_service_account.antigravity_sa.email
    execution_environment = "EXECUTION_ENVIRONMENT_GEN2" # Required for GCS FUSE and Background CPU
    
    containers {
      # Replace with your actual Artifact Registry image path after docker push
      image = "us-central1-docker.pkg.dev/${var.project_id}/repo/antigravity-engine:latest"
      
      ports {
        container_port = 8080
      }

      resources {
        limits = {
          cpu    = "4"
          memory = "8Gi"
        }
        cpu_idle = false # Allow background CPU for ffmpeg video encoding & Playwright
      }

      # Mount the GCS Bucket as a local directory
      volume_mounts {
        name       = "workspace-volume"
        mount_path = "/workspace"
      }
    }

    volumes {
      name = "workspace-volume"
      gcs {
        bucket    = google_storage_bucket.antigravity_workspace.name
        read_only = false
      }
    }
  }

  depends_on = [
    google_project_service.required_apis,
    google_project_iam_member.vertex_user
  ]
}

# 7. Create the Pub/Sub Topic
resource "google_pubsub_topic" "agent_triggers" {
  name = "antigravity-agent-triggers"
  # FedRAMP Requirement: Ensure messages are encrypted with CMEK if configured
}

# 8. Create a dedicated Service Account for Pub/Sub to invoke Cloud Run
resource "google_service_account" "pubsub_invoker_sa" {
  account_id   = "pubsub-invoker-sa"
  display_name = "Pub/Sub Cloud Run Invoker"
}

# 9. Grant the Pub/Sub SA permission to invoke the Cloud Run engine
resource "google_cloud_run_service_iam_member" "pubsub_invoker" {
  project  = var.project_id
  location = var.region
  service  = google_cloud_run_v2_service.antigravity_engine.name
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.pubsub_invoker_sa.email}"
}

# 10. Create the Authenticated Push Subscription
resource "google_pubsub_subscription" "agent_push_sub" {
  name  = "antigravity-agent-push-sub"
  topic = google_pubsub_topic.agent_triggers.name

  push_config {
    # This URL will be automatically populated by Terraform
    push_endpoint = "${google_cloud_run_v2_service.antigravity_engine.uri}/webhook/pubsub"

    # Enforce OIDC Authentication (Zero-Trust)
    oidc_token {
      service_account_email = google_service_account.pubsub_invoker_sa.email
      audience              = google_cloud_run_v2_service.antigravity_engine.uri
    }
  }

  depends_on = [google_cloud_run_service_iam_member.pubsub_invoker]
}
