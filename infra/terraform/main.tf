# Cor.LawTrack Phase 1 Terraform Infrastructure
# 100% GCP Native Serverless Architecture 
# Built under Business Judgment Rule Core Parameters

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

# 1. Zero-Trust Identity (Service Account for Cloud Run)
resource "google_service_account" "lawtrack_api_sa" {
  account_id   = "lawtrack-api-sa"
  display_name = "Cor.LawTrack Backend Service Account"
}

# Bind Vertex AI (Gemini 3.1 Pro via AI Platform)
resource "google_project_iam_member" "vertex_ai_access" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.lawtrack_api_sa.email}"
}

# Bind Cloud Tasks Enqueuer
resource "google_project_iam_member" "cloud_tasks_access" {
  project = var.project_id
  role    = "roles/cloudtasks.enqueuer"
  member  = "serviceAccount:${google_service_account.lawtrack_api_sa.email}"
}

# 2. Cloud KMS Key Management (Customer Managed Encryption Keys)
resource "google_kms_key_ring" "lawtrack_keyring" {
  name     = "lawtrack-keyring-v2"
  location = var.region
}

resource "google_kms_crypto_key" "lawtrack_core_key" {
  name            = "lawtrack-core-crypto-key"
  key_ring        = google_kms_key_ring.lawtrack_keyring.id
  rotation_period = "7776000s" # 90 Days
}

# 3. Cloud SQL (PostgreSQL Enterprise Plus)
resource "google_sql_database_instance" "lawtrack_postgres" {
  name             = "lawtrack-db-primary"
  database_version = "POSTGRES_15"
  region           = var.region
  
  encryption_key_name = google_kms_crypto_key.lawtrack_core_key.id

  settings {
    tier = "db-custom-2-8192"
    
    ip_configuration {
      require_ssl = true
    }
    backup_configuration {
      enabled                        = true
      point_in_time_recovery_enabled = true
    }
  }
}

# 4. Immutable Audit & Document Storage (WORM Compliance)
resource "google_storage_bucket" "lawtrack_audit_vault" {
  name          = "${var.project_id}-audit-vault-v1"
  location      = "US"
  force_destroy = false 

  encryption {
    default_kms_key_name = google_kms_crypto_key.lawtrack_core_key.id
  }

  versioning {
    enabled = true
  }

  retention_policy {
    is_locked        = true
    retention_period = 315360000 # 10 Years
  }
}

# 5. Asynchronous Event Queuing (Cloud Tasks)
resource "google_cloud_tasks_queue" "lawtrack_ingestion_queue" {
  name     = "lawtrack-ingestion-queue"
  location = var.region

  rate_limits {
    max_concurrent_dispatches = 100
    max_dispatches_per_second = 500
  }
  
  retry_config {
    max_attempts = 100
    min_backoff  = "1s"
    max_backoff  = "3600s" # 1 Hour
  }
}

# 6. Global Serverless API (Cloud Run)
resource "google_cloud_run_v2_service" "lawtrack_api" {
  name     = "lawtrack-core-api"
  location = var.region
  
  template {
    service_account = google_service_account.lawtrack_api_sa.email

    containers {
      image = "us-docker.pkg.dev/cloudrun/container/hello" # Deferred to GitHub Actions build
      
      env {
        name  = "DB_HOST"
        value = google_sql_database_instance.lawtrack_postgres.private_ip_address
      }
      env {
        name  = "PROJECT_ID"
        value = var.project_id
      }
      env {
        name  = "LOCATION"
        value = var.region
      }
      env {
        name  = "TASK_QUEUE_NAME"
        value = google_cloud_tasks_queue.lawtrack_ingestion_queue.name
      }
    }
  }
}
