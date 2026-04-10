terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 5.10"
    }
  }
}

provider "google" {
  project = "shadowtag-omega-v2"
  region  = "us-central1"
}

variable "hive_api_key" {
  description = "Hive API Key (Secret)"
  type        = string
  sensitive   = true
}

# 1. STORAGE: The "Dynamic Brain" for Blocklists
resource "google_storage_bucket" "config_bucket" {
  name          = "shadowtag-omega-v2-safety-config"
  location      = "US"
  force_destroy = false
  uniform_bucket_level_access = true
}

# 2. MODEL ARMOR: The "Bodyguard" Policy
# Creates a strict template that blocks PII and Injection
resource "google_model_armor_template" "strict_policy" {
  project     = "shadowtag-omega-v2"
  location    = "us-central1"
  template_id = "antigravity-strict-v1"

  filter_config {
    pi_and_jailbreak_filter_settings {
      filter_enforcement = "ENABLED"
      confidence_level   = "LOW_AND_ABOVE" # Strict Block
    }
    sdp_settings {
      basic_config {
        filter_enforcement = "ENABLED" # Blocks PII (Names, Phones)
      }
    }
    rai_settings {
      filter_type      = "SEXUALLY_EXPLICIT"
      confidence_level = "LOW_AND_ABOVE"
    }
  }
}

# 3. IAM: Service Account (Least Privilege)
resource "google_service_account" "guardrail_sa" {
  account_id   = "guardrail-sa"
  display_name = "ShadowTag Guardrail Service Account"
}

resource "google_project_iam_member" "armor_user" {
  project = "shadowtag-omega-v2"
  role    = "roles/modelarmor.user"
  member  = "serviceAccount:${google_service_account.guardrail_sa.email}"
}

resource "google_storage_bucket_iam_member" "config_reader" {
  bucket = google_storage_bucket.config_bucket.name
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:${google_service_account.guardrail_sa.email}"
}

# 4. COMPUTE: The Cloud Run Service
resource "google_cloud_run_v2_service" "guardrail" {
  name     = "shadowtag-guardrail"
  location = "us-central1"
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    service_account = google_service_account.guardrail_sa.email
    
    containers {
      image = "gcr.io/shadowtag-omega-v2/guardrail:latest"
      
      env {
        name  = "HIVE_API_KEY"
        value = var.hive_api_key
      }
      env {
        name  = "CONFIG_BUCKET"
        value = google_storage_bucket.config_bucket.name
      }
      env {
        name  = "ARMOR_TEMPLATE_ID"
        value = google_model_armor_template.strict_policy.name
      }
    }
  }
}
