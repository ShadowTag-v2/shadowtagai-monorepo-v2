# ============================================================================
# VERTEX AI MODULE - FILE SEARCH / RAG CONFIGURATION
# ============================================================================
# Purpose: Enable Vertex AI APIs and configure File Search capabilities
# Note: RAG corpus creation is done via Python scripts (not directly in TF)
# ============================================================================

# ============================================================================
# ENABLE REQUIRED APIs
# ============================================================================

resource "google_project_service" "vertex_ai" {
  project = var.project_id
  service = "aiplatform.googleapis.com"

  disable_on_destroy = false
}

resource "google_project_service" "generative_language" {
  project = var.project_id
  service = "generativelanguage.googleapis.com"

  disable_on_destroy = false
}

resource "google_project_service" "ml_api" {
  project = var.project_id
  service = "ml.googleapis.com"

  disable_on_destroy = false
}

resource "google_project_service" "notebooks" {
  project = var.project_id
  service = "notebooks.googleapis.com"

  disable_on_destroy = false
}

# ============================================================================
# VERTEX AI WORKBENCH INSTANCE (Optional)
# ============================================================================

resource "google_notebooks_instance" "vertex_workbench" {
  count = var.create_workbench_instance ? 1 : 0

  name         = "pnkln-file-search-workbench"
  location     = "${var.region}-a"  # Zone required for notebooks
  machine_type = var.workbench_machine_type
  project      = var.project_id

  vm_image {
    project      = "deeplearning-platform-release"
    image_family = "tf-latest-cpu"
  }

  install_gpu_driver = false
  boot_disk_type     = "PD_SSD"
  boot_disk_size_gb  = 100

  no_public_ip    = false
  no_proxy_access = false

  labels = {
    purpose = "file-search-management"
  }

  depends_on = [
    google_project_service.notebooks,
    google_project_service.vertex_ai
  ]
}

# ============================================================================
# METADATA FOR CORPUS CONFIGURATION
# ============================================================================
# Store corpus configuration as Cloud Storage object for scripts to reference

resource "google_storage_bucket_object" "corpus_config" {
  name    = "config/verticals.json"
  bucket  = var.config_bucket
  content = jsonencode({
    verticals      = var.verticals
    chunk_size     = var.chunk_size
    chunk_overlap  = var.chunk_overlap
    region         = var.region
    project_id     = var.project_id
  })

  content_type = "application/json"
}

# ============================================================================
# IAM FOR VERTEX AI ACCESS
# ============================================================================

# Service account for Vertex AI operations
resource "google_service_account" "vertex_ai_sa" {
  account_id   = "pnkln-vertex-ai-sa"
  display_name = "Service Account for Vertex AI File Search operations"
  project      = var.project_id
}

# Grant Vertex AI User role
resource "google_project_iam_member" "vertex_ai_user" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.vertex_ai_sa.email}"
}

# Grant ML Developer role
resource "google_project_iam_member" "ml_developer" {
  project = var.project_id
  role    = "roles/ml.developer"
  member  = "serviceAccount:${google_service_account.vertex_ai_sa.email}"
}

# Grant Storage Object Viewer for corpus access
resource "google_project_iam_member" "storage_viewer" {
  project = var.project_id
  role    = "roles/storage.objectViewer"
  member  = "serviceAccount:${google_service_account.vertex_ai_sa.email}"
}

# ============================================================================
# MONITORING - FILE SEARCH PERFORMANCE METRICS
# ============================================================================

# Create a notification channel for File Search alerts
resource "google_monitoring_notification_channel" "file_search_alerts" {
  display_name = "File Search Performance Alerts"
  type         = "email"
  project      = var.project_id

  labels = {
    email_address = var.alert_email
  }
}

# Alert policy for high latency
resource "google_monitoring_alert_policy" "file_search_latency" {
  display_name = "File Search P99 Latency Exceeded"
  project      = var.project_id
  combiner     = "OR"

  conditions {
    display_name = "File Search response time > 1000ms"

    condition_threshold {
      filter          = "resource.type = \"aiplatform.googleapis.com/Endpoint\" AND metric.type = \"aiplatform.googleapis.com/prediction/latencies\""
      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = 1000  # ms

      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_PERCENTILE_99"
      }
    }
  }

  notification_channels = [google_monitoring_notification_channel.file_search_alerts.id]

  alert_strategy {
    auto_close = "1800s"
  }
}

# Alert policy for high error rate
resource "google_monitoring_alert_policy" "file_search_errors" {
  display_name = "File Search Error Rate Elevated"
  project      = var.project_id
  combiner     = "OR"

  conditions {
    display_name = "File Search error rate > 5%"

    condition_threshold {
      filter          = "resource.type = \"aiplatform.googleapis.com/Endpoint\" AND metric.type = \"aiplatform.googleapis.com/prediction/error_count\""
      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = 0.05  # 5%

      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_RATE"
      }
    }
  }

  notification_channels = [google_monitoring_notification_channel.file_search_alerts.id]
}

# ============================================================================
# OUTPUTS
# ============================================================================

output "vertex_ai_api_endpoint" {
  description = "Vertex AI API endpoint"
  value       = "https://${var.region}-aiplatform.googleapis.com"
}

output "service_account_email" {
  description = "Vertex AI service account email"
  value       = google_service_account.vertex_ai_sa.email
}

output "workbench_instance" {
  description = "Vertex AI Workbench instance name (if created)"
  value       = var.create_workbench_instance ? google_notebooks_instance.vertex_workbench[0].name : null
}

output "enabled_apis" {
  description = "Enabled Vertex AI APIs"
  value = [
    google_project_service.vertex_ai.service,
    google_project_service.generative_language.service,
    google_project_service.ml_api.service,
    google_project_service.notebooks.service
  ]
}

output "corpus_config_location" {
  description = "Location of corpus configuration file"
  value       = "gs://${var.config_bucket}/config/verticals.json"
}
