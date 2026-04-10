# IAM and Workload Identity configuration

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SERVICE ACCOUNTS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# GCP Service Account for shadowtagai orchestrator
resource "google_service_account" "shadowtagai_orchestrator" {
  account_id   = "shadowtagai-orchestrator"
  display_name = "ShadowTagAi Orchestrator Service Account"
  description  = "Service account for shadowtagai orchestrator workloads"
  project      = var.project_id

  depends_on = [google_project_service.required_apis]
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# IAM ROLES FOR SERVICE ACCOUNT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Vertex AI User (to call Claude via Vertex AI)
resource "google_project_iam_member" "vertex_user" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.shadowtagai_orchestrator.email}"
}

# Secret Manager Secret Accessor (to read secrets)
resource "google_project_iam_member" "secret_accessor" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.shadowtagai_orchestrator.email}"
}

# Logging Writer (to write logs)
resource "google_project_iam_member" "log_writer" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.shadowtagai_orchestrator.email}"
}

# Monitoring Metric Writer (to write custom metrics)
resource "google_project_iam_member" "metric_writer" {
  project = var.project_id
  role    = "roles/monitoring.metricWriter"
  member  = "serviceAccount:${google_service_account.shadowtagai_orchestrator.email}"
}

# Cloud Trace Agent (for distributed tracing)
resource "google_project_iam_member" "trace_agent" {
  project = var.project_id
  role    = "roles/cloudtrace.agent"
  member  = "serviceAccount:${google_service_account.shadowtagai_orchestrator.email}"
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# WORKLOAD IDENTITY BINDING
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Allow Kubernetes SA to impersonate GCP SA
resource "google_service_account_iam_member" "workload_identity_binding" {
  service_account_id = google_service_account.shadowtagai_orchestrator.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "serviceAccount:${var.project_id}.svc.id.goog[shadowtagai-production/shadowtagai-orchestrator]"

  depends_on = [google_container_cluster.primary]
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CLOUD BUILD SERVICE ACCOUNT PERMISSIONS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Allow Cloud Build to deploy to GKE
resource "google_project_iam_member" "cloudbuild_gke_developer" {
  project = var.project_id
  role    = "roles/container.developer"
  member  = "serviceAccount:${data.google_project.project.number}@cloudbuild.gserviceaccount.com"
}

# Allow Cloud Build to act as service account
resource "google_service_account_iam_member" "cloudbuild_sa_user" {
  service_account_id = google_service_account.shadowtagai_orchestrator.name
  role               = "roles/iam.serviceAccountUser"
  member             = "serviceAccount:${data.google_project.project.number}@cloudbuild.gserviceaccount.com"
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# OUTPUTS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

output "service_account_email" {
  value       = google_service_account.shadowtagai_orchestrator.email
  description = "GCP Service Account email for shadowtagai orchestrator"
}

output "workload_identity_annotation" {
  value       = "iam.gke.io/gcp-service-account: ${google_service_account.shadowtagai_orchestrator.email}"
  description = "Annotation to add to Kubernetes ServiceAccount"
}
