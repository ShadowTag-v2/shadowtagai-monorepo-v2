terraform {
  required_version = ">= 1.11.0"
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

# --------------------------------------------------------------------------------
# Branko-Proof OpenTofu Definitions for Pure Cloud Run Serverless (Gen2)
# Ref: infrastructure-catalog-gcp-cloud-run
# --------------------------------------------------------------------------------

# 1. KMS Key Ring for Zero-Trust Encryption
resource "google_kms_key_ring" "legaltrack_ring" {
  name     = "${var.environment}-legaltrack-keyring"
  location = var.region
}

resource "google_kms_crypto_key" "database_key" {
  name     = "${var.environment}-db-crypto-key"
  key_ring = google_kms_key_ring.legaltrack_ring.id
}

# 2. Private VPC Access Connector (for Cloud SQL)
resource "google_vpc_access_connector" "connector" {
  name          = "${var.environment}-private-run"
  region        = var.region
  project       = var.project_id
  machine_type  = "e2-micro"
  min_instances = 2
  max_instances = 10

  network = "default"  # Replace with actual dedicated VPC later
}

# 3. Cloud Run Service (Gen2)
resource "google_cloud_run_v2_service" "legaltrack_api" {
  name     = "${var.environment}-legaltrack-api"
  location = var.region
  project  = var.project_id

  template {
    execution_environment = "EXECUTION_ENVIRONMENT_GEN2"
    service_account       = "run-sa@${var.project_id}.iam.gserviceaccount.com"
    
    # 2026 Optimization: Cold start mitigation
    # startup_cpu_boost   = true  <- Handled via CLI/Deploy usually but noted

    scaling {
      min_instance_count = 1  # Keep 1 warm for MVP rapid response
      max_instance_count = 10
    }

    containers {
      image = "us-central1-docker.pkg.dev/${var.project_id}/legaltrack-repo/api:latest"
      
      resources {
        limits = {
          cpu    = "1"
          memory = "1024Mi"
        }
      }

      # Zero-Trust Environment Variables mapped via Secret Manager
      env {
        name = "DB_HOST"
        value = "private-cloudsql-ip" # Stub
      }

      startup_probe {
        initial_delay_seconds = 10
        timeout_seconds       = 10
        period_seconds        = 30
        http_get {
          path = "/health"
        }
      }
    }

    # Explicit VPC connection for the encrypted database
    vpc_access {
      connector = google_vpc_access_connector.connector.id
      egress    = "PRIVATE_RANGES_ONLY"
    }

    # Cloud SQL Volumes (Mounted explicitly)
    volumes {
      name = "cloudsql"
      cloud_sql_instance {
        instances = ["${var.project_id}:${var.region}:${var.environment}-legaltrack-pg"]
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }

  labels = {
    "clouddeploy-target" = "${var.environment}-legaltrack-api-target"
  }
}

# 4. Mandatory Enforced IAM (No allUsers for production API unless gateway)
resource "google_cloud_run_v2_service_iam_member" "invoker" {
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.legaltrack_api.name
  role     = "roles/run.invoker"
  member   = "serviceAccount:frontend-service@${var.project_id}.iam.gserviceaccount.com"
}
