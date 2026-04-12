# Enable Secret Manager API
resource "google_project_service" "secretmanager" {
  project = var.project_id
  service = "secretmanager.googleapis.com"

  disable_on_destroy = false
}

# Service Account for workload identity
resource "google_service_account" "pnkln_inference" {
  account_id   = "pnkln-inference-sa"
  display_name = "PNKLN Inference Service Account"
  project      = var.project_id
}

# Grant Secret Manager access to service account
resource "google_project_iam_member" "inference_secret_accessor" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.pnkln_inference.email}"
}

# Grant logging write permission
resource "google_project_iam_member" "inference_log_writer" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.pnkln_inference.email}"
}

# Grant monitoring metric writer permission
resource "google_project_iam_member" "inference_metric_writer" {
  project = var.project_id
  role    = "roles/monitoring.metricWriter"
  member  = "serviceAccount:${google_service_account.pnkln_inference.email}"
}

# Grant Cloud Storage access for model loading
resource "google_project_iam_member" "inference_storage_reader" {
  project = var.project_id
  role    = "roles/storage.objectViewer"
  member  = "serviceAccount:${google_service_account.pnkln_inference.email}"
}

# Workload Identity binding
resource "google_service_account_iam_member" "workload_identity_binding" {
  service_account_id = google_service_account.pnkln_inference.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "serviceAccount:${var.project_id}.svc.id.goog[default/pnkln-inference]"

  depends_on = [google_container_cluster.pnkln_cluster]
}

# Example secrets - create these manually or via automated processes
# Secret for API keys
resource "google_secret_manager_secret" "api_keys" {
  secret_id = "pnkln-api-keys"
  project   = var.project_id

  replication {
    auto {}
  }

  labels = merge(var.labels, {
    secret_type = "api-keys"
  })

  depends_on = [google_project_service.secretmanager]
}

# Secret for model credentials
resource "google_secret_manager_secret" "model_credentials" {
  secret_id = "pnkln-model-credentials"
  project   = var.project_id

  replication {
    auto {}
  }

  labels = merge(var.labels, {
    secret_type = "model-credentials"
  })

  depends_on = [google_project_service.secretmanager]
}

# Secret for database connection string
resource "google_secret_manager_secret" "database_url" {
  secret_id = "pnkln-database-url"
  project   = var.project_id

  replication {
    auto {}
  }

  labels = merge(var.labels, {
    secret_type = "database"
  })

  depends_on = [google_project_service.secretmanager]
}
