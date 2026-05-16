# Secret Manager configuration

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SECRETS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Anthropic Vertex Project ID secret
resource "google_secret_manager_secret" "anthropic_project_id" {
  secret_id = "anthropic-vertex-project-id"
  project   = var.project_id

  replication {
    auto {}
  }

  labels = {
    app       = "pnkln"
    component = "orchestrator"
  }

  depends_on = [google_project_service.required_apis]
}

# Secret version (actual value)
resource "google_secret_manager_secret_version" "anthropic_project_id_v1" {
  secret = google_secret_manager_secret.anthropic_project_id.id

  secret_data = var.anthropic_vertex_project_id
}

# IAM binding for service account to access secret
resource "google_secret_manager_secret_iam_member" "anthropic_project_id_accessor" {
  secret_id = google_secret_manager_secret.anthropic_project_id.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.pnkln_orchestrator.email}"
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# OUTPUT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

output "anthropic_secret_name" {
  value       = google_secret_manager_secret.anthropic_project_id.name
  description = "Secret Manager secret name for Anthropic project ID"
}
