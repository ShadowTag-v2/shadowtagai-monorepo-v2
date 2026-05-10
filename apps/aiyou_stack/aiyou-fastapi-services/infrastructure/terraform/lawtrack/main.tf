
# LawTrack Infrastructure Module

provider "google" {
  project = var.project_id
  region  = var.region
}

# =============================================================================
# VARIABLES
# =============================================================================

variable "project_id" {
  description = "GCP Project ID"
  type        = str
}

variable "region" {
  description = "GCP Region"
  type        = str
  default     = "us-central1"
}

variable "env" {
  description = "Environment (dev/staging/prod)"
  type        = str
  default     = "dev"
}

# =============================================================================
# KMS - ENCRYPTION KEYS ("THE SHIELD")
# =============================================================================

resource "google_kms_key_ring" "lawtrack_keyring" {
  name     = "lawtrack-keyring-${var.env}"
  location = var.region
}

resource "google_kms_crypto_key" "app_key" {
  name            = "lawtrack-app-key-${var.env}"
  key_ring        = google_kms_key_ring.lawtrack_keyring.id
  rotation_period = "7776000s" # 90 days

  lifecycle {
    prevent_destroy = true
  }
}

# =============================================================================
# S3 (GCS) - IMMUTABLE STORAGE ("THE VAULT")
# =============================================================================

resource "google_storage_bucket" "lawtrack_docs" {
  name          = "lawtrack-docs-${var.env}-${var.project_id}"
  location      = "US"
  force_destroy = false

  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  retention_policy {
    is_locked        = true
    retention_period = 2592000 # 30 days minimum
  }

  encryption {
    default_kms_key_name = google_kms_crypto_key.app_key.id
  }
}

# =============================================================================
# DATABASE (RDS/CloudSQL)
# =============================================================================

resource "google_sql_database_instance" "lawtrack_db" {
  name             = "lawtrack-db-${var.env}"
  database_version = "POSTGRES_15"
  region           = var.region

  settings {
    tier = "db-f1-micro" # Start small for MVP

    backup_configuration {
      enabled = true
    }

    ip_configuration {
      ipv4_enabled = true # Ideally verification only via Private IP
    }
  }

  deletion_protection = true # Critical for legal data
}

resource "google_sql_database" "database" {
  name     = "lawtrack"
  instance = google_sql_database_instance.lawtrack_db.name
}

resource "google_sql_user" "users" {
  name     = "lawtrack-user"
  instance = google_sql_database_instance.lawtrack_db.name
  password = "CHANGE-ME-IN-SECRET-MANAGER" # In real life, use secret manager
}
