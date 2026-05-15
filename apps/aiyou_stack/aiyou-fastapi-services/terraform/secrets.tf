# Secret Manager configuration
# Anthropic Vertex removed - using Gemini API

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# GEMINI API KEY SECRET
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

resource "google_secret_manager_secret" "gemini_api_key" {
  secret_id = "gemini-api-key"
  project   = var.project_id

  replication {
    auto {}
  }

  labels = {
    app       = "shadowtagai"
    component = "orchestrator"
  }

  depends_on = [google_project_service.required_apis]
}

# IAM binding for service account to access secret
resource "google_secret_manager_secret_iam_member" "gemini_api_key_accessor" {
  secret_id = google_secret_manager_secret.gemini_api_key.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.shadowtagai_orchestrator.email}"
}

# Add other secrets here as needed

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# OUTPUT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

output "gemini_secret_name" {
  value       = google_secret_manager_secret.gemini_api_key.name
  description = "Secret Manager secret name for Gemini API key"
}
