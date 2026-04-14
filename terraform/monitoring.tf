terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

variable "project_id" {
  type    = string
  default = "shadowtag-omega-v4"
}

variable "admin_email" {
  type    = string
  default = "admin@shadowtagai.com"
}

resource "google_monitoring_notification_channel" "admin_email" {
  project      = var.project_id
  display_name = "Admin Alerts"
  type         = "email"
  labels = {
    email_address = var.admin_email
  }
}

resource "google_monitoring_alert_policy" "firestore_spike" {
  project      = var.project_id
  display_name = "High Firestore Usage (Omega-v4)"
  combiner     = "OR"

  conditions {
    display_name = "Firestore Read/Write Spikes"
    condition_threshold {
      filter          = "metric.type=\"firestore.googleapis.com/document/write_count\" AND resource.type=\"firestore_database\""
      comparison      = "COMPARISON_GT"
      threshold_value = 50000
      duration        = "300s"

      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_RATE"
      }
    }
  }

  notification_channels = [
    google_monitoring_notification_channel.admin_email.name
  ]
}
