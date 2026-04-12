# ============================================================================
# IAM MODULE - WORKLOAD IDENTITY & PERMISSIONS
# ============================================================================
# Purpose: Configure IAM bindings for GKE + Vertex AI + GCS integration
# Implements Workload Identity for secure pod-to-GCP authentication
# ============================================================================

# ============================================================================
# WORKLOAD IDENTITY BINDING
# ============================================================================

# Allow Kubernetes service account to impersonate GCP service account
resource "google_service_account_iam_member" "workload_identity_binding" {
  service_account_id = var.gke_service_account
  role               = "roles/iam.workloadIdentityUser"
  member             = "serviceAccount:${var.project_id}.svc.id.goog[${var.workload_identity_namespace}/${var.kubernetes_sa_name}]"
}

# ============================================================================
# VERTEX AI PERMISSIONS
# ============================================================================

# Grant GKE service account access to Vertex AI
resource "google_project_iam_member" "vertex_ai_user" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${var.gke_service_account}"
}

# Grant ML Developer role for corpus management
resource "google_project_iam_member" "ml_developer" {
  project = var.project_id
  role    = "roles/ml.developer"
  member  = "serviceAccount:${var.gke_service_account}"
}

# ============================================================================
# GCS CORPUS BUCKET PERMISSIONS
# ============================================================================

# Grant read access to all policy corpus buckets
resource "google_storage_bucket_iam_member" "corpus_object_viewer" {
  for_each = toset(var.corpus_buckets)

  bucket = each.value
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:${var.gke_service_account}"
}

# Grant write access for corpus updates (limited to specific buckets if needed)
resource "google_storage_bucket_iam_member" "corpus_object_creator" {
  for_each = toset(var.corpus_buckets)

  bucket = each.value
  role   = "roles/storage.objectCreator"
  member = "serviceAccount:${var.gke_service_account}"
}

# ============================================================================
# LOGGING & MONITORING PERMISSIONS
# ============================================================================

# Already granted in GKE module, but adding here for completeness
resource "google_project_iam_member" "logging" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${var.gke_service_account}"
}

resource "google_project_iam_member" "monitoring" {
  project = var.project_id
  role    = "roles/monitoring.metricWriter"
  member  = "serviceAccount:${var.gke_service_account}"
}

# ============================================================================
# SECRET MANAGER PERMISSIONS (for API keys, if needed)
# ============================================================================

resource "google_project_iam_member" "secret_accessor" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${var.gke_service_account}"
}

# ============================================================================
# CUSTOM ROLE FOR FILE SEARCH OPERATIONS
# ============================================================================

resource "google_project_iam_custom_role" "file_search_operator" {
  role_id     = "fileSearchOperator"
  title       = "File Search Operator"
  description = "Custom role for Pnkln File Search operations"
  project     = var.project_id

  permissions = [
    # Vertex AI permissions
    "aiplatform.endpoints.get",
    "aiplatform.endpoints.list",
    "aiplatform.endpoints.predict",

    # RAG corpus permissions
    "aiplatform.ragCorpora.get",
    "aiplatform.ragCorpora.list",
    "aiplatform.ragFiles.get",
    "aiplatform.ragFiles.list",

    # Storage permissions
    "storage.buckets.get",
    "storage.objects.get",
    "storage.objects.list",

    # Monitoring
    "monitoring.timeSeries.create",
    "logging.logEntries.create"
  ]
}

# Grant custom role to GKE service account
resource "google_project_iam_member" "file_search_operator" {
  project = var.project_id
  role    = google_project_iam_custom_role.file_search_operator.id
  member  = "serviceAccount:${var.gke_service_account}"
}

# ============================================================================
# KUBERNETES SERVICE ACCOUNT (via kubectl)
# ============================================================================
# Note: This needs to be applied after cluster creation
# Documented in deployment scripts

resource "local_file" "k8s_service_account_manifest" {
  content = yamlencode({
    apiVersion = "v1"
    kind       = "ServiceAccount"
    metadata = {
      name      = var.kubernetes_sa_name
      namespace = var.workload_identity_namespace
      annotations = {
        "iam.gke.io/gcp-service-account" = var.gke_service_account
      }
    }
  })

  filename = "${path.module}/../../k8s-manifests/service-account.yaml"
}

# ============================================================================
# OUTPUTS
# ============================================================================

output "workload_identity_binding" {
  description = "Workload Identity binding details"
  value = {
    kubernetes_sa = "${var.workload_identity_namespace}/${var.kubernetes_sa_name}"
    gcp_sa        = var.gke_service_account
  }
}

output "granted_roles" {
  description = "IAM roles granted to GKE service account"
  value = [
    "roles/aiplatform.user",
    "roles/ml.developer",
    "roles/storage.objectViewer",
    "roles/storage.objectCreator",
    "roles/logging.logWriter",
    "roles/monitoring.metricWriter",
    "roles/secretmanager.secretAccessor",
    google_project_iam_custom_role.file_search_operator.id
  ]
}

output "k8s_manifest_path" {
  description = "Path to Kubernetes ServiceAccount manifest"
  value       = local_file.k8s_service_account_manifest.filename
}
