# OpenTofu: Firestore beta_accounts monitoring
# Part of shadowtag-omega-v4 infrastructure

resource "google_monitoring_alert_policy" "beta_accounts_reads" {
  project      = var.project_id
  display_name = "Firestore: beta_accounts High Read Rate"
  combiner     = "OR"

  conditions {
    display_name = "beta_accounts read operations > 100/min"
    condition_threshold {
      filter          = "resource.type = \"firestore_database\" AND metric.type = \"firestore.googleapis.com/document/read_count\" AND resource.label.\"database_id\" = \"(default)\""
      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = 100

      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_RATE"
      }
    }
  }

  notification_channels = [var.notification_channel_id]

  documentation {
    content   = "Firestore beta_accounts collection is experiencing high read rates (>100/min). Investigate potential abuse or misconfigured polling."
    mime_type = "text/markdown"
  }

  alert_strategy {
    auto_close = "1800s"
  }
}

resource "google_monitoring_alert_policy" "beta_accounts_writes" {
  project      = var.project_id
  display_name = "Firestore: beta_accounts Unexpected Writes"
  combiner     = "OR"

  conditions {
    display_name = "beta_accounts write operations > 10/min"
    condition_threshold {
      filter          = "resource.type = \"firestore_database\" AND metric.type = \"firestore.googleapis.com/document/write_count\" AND resource.label.\"database_id\" = \"(default)\""
      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = 10

      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_RATE"
      }
    }
  }

  notification_channels = [var.notification_channel_id]

  documentation {
    content   = "Firestore beta_accounts collection has unexpected write activity (>10/min). Only admin operations should write to this collection."
    mime_type = "text/markdown"
  }

  alert_strategy {
    auto_close = "1800s"
  }
}

variable "project_id" {
  type    = string
  default = "shadowtag-omega-v4"
}

variable "notification_channel_id" {
  type        = string
  description = "Notification channel for alerts (founder@shadowtagai.com channel ID)"
  default     = "projects/shadowtag-omega-v4/notificationChannels/17531835029676919705"
}
