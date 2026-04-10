# Secret Manager Definitions for AI Agents

# 1. Temporal API Key (for Workflow Refinery)
resource "google_secret_manager_secret" "temporal_api_key" {
  secret_id = "temporal-api-key"
  
  replication {
    auto {}
  }
}

# 2. Hugging Face Token (for Vision Refinery / vLLM)
resource "google_secret_manager_secret" "hf_token" {
  secret_id = "hugging-face-token"

  replication {
    auto {}
  }
}

# IAM Binding: Allow Cloud Run Service Account to Access Secrets
# Note: In a real environment, you might scope this per-service-account
resource "google_secret_manager_secret_iam_binding" "temporal_secret_access" {
  secret_id = google_secret_manager_secret.temporal_api_key.id
  role      = "roles/secretmanager.secretAccessor"
  members   = [
    "serviceAccount:${google_service_account.cloud_run_invoker.email}", # Using the invoker SA for simplicity in this demo
    # "serviceAccount:service-${var.project_num}@serverless-robot-prod.iam.gserviceaccount.com" # Example of default one
  ]
}

resource "google_secret_manager_secret_iam_binding" "hf_secret_access" {
  secret_id = google_secret_manager_secret.hf_token.id
  role      = "roles/secretmanager.secretAccessor"
  members   = [
    "serviceAccount:${google_service_account.cloud_run_invoker.email}"
  ]
}
