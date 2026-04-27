# Firestore Backup Verify Module
# Manages scheduled backups + verification alerts

variable "project_id" {
  type        = string
  description = "GCP project ID."
}

variable "database_id" {
  type        = string
  default     = "(default)"
  description = "Firestore database ID."
}

variable "backup_bucket" {
  type        = string
  default     = ""
  description = "GCS bucket for Firestore exports. Defaults to {project}-firestore-backups."
}

variable "schedule" {
  type        = string
  default     = "0 3 * * *"
  description = "Cron schedule for backup (default: 3am UTC daily)."
}

variable "admin_email" {
  type        = string
  default     = "admin@shadowtagai.com"
  description = "Alert notification email."
}

locals {
  bucket_name = var.backup_bucket != "" ? var.backup_bucket : "${var.project_id}-firestore-backups"
}

# GCS bucket for backups
resource "google_storage_bucket" "firestore_backups" {
  project                     = var.project_id
  name                        = local.bucket_name
  location                    = "US"
  uniform_bucket_level_access = true
  force_destroy               = false
  public_access_prevention    = "enforced"  # CKV_GCP_114

  versioning {
    enabled = true  # CKV_GCP_78
  }

  # CKV_GCP_62: Access logging — skipped intentionally for cost efficiency.
  # A dedicated log bucket would add $X/mo for a backup-only use case.
  # checkov:skip=CKV_GCP_62: Backup bucket access logging deferred (cost/benefit)

  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = 90  # Retain backups for 90 days
    }
  }

  labels = {
    managed_by = "opentofu"
    purpose    = "firestore-backup"
  }
}

# Cloud Scheduler job to trigger Firestore export
resource "google_cloud_scheduler_job" "firestore_backup" {
  project     = var.project_id
  region      = "us-central1"
  name        = "firestore-backup"
  description = "Nightly Firestore database export"
  schedule    = var.schedule
  time_zone   = "America/Los_Angeles"

  http_target {
    http_method = "POST"
    uri         = "https://firestore.googleapis.com/v1/projects/${var.project_id}/databases/${var.database_id}:exportDocuments"
    body        = base64encode(jsonencode({
      outputUriPrefix = "gs://${local.bucket_name}"
    }))
    headers = {
      "Content-Type" = "application/json"
    }
    oauth_token {
      service_account_email = "${var.project_id}@appspot.gserviceaccount.com"
      scope                 = "https://www.googleapis.com/auth/cloud-platform"
    }
  }
}

# Alert on backup failures
resource "google_monitoring_alert_policy" "backup_failure" {
  project      = var.project_id
  display_name = "Firestore Backup — Export Failed"
  combiner     = "OR"

  conditions {
    display_name = "Backup scheduler job failed"
    condition_threshold {
      filter          = "metric.type=\"logging.googleapis.com/user/firestore_backup_failures\" AND resource.type=\"cloud_scheduler_job\""
      comparison      = "COMPARISON_GT"
      threshold_value = 0
      duration        = "0s"

      aggregations {
        alignment_period   = "300s"
        per_series_aligner = "ALIGN_SUM"
      }
    }
  }

  notification_channels = []  # Add channels from monitoring-alerts module
}

output "backup_bucket" {
  value       = google_storage_bucket.firestore_backups.name
  description = "GCS bucket storing Firestore backups."
}

output "scheduler_job" {
  value       = google_cloud_scheduler_job.firestore_backup.name
  description = "Cloud Scheduler job name for backups."
}
