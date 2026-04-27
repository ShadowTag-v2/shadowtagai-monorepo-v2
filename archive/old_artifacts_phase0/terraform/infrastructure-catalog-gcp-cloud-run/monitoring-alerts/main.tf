# Monitoring Alerts Module
# Extracted from terraform/monitoring.tf — standardized as reusable module

variable "project_id" {
  type        = string
  description = "GCP project ID."
}

variable "service_name" {
  type        = string
  description = "Service name for alert naming."
}

variable "service_host" {
  type        = string
  description = "Hostname for uptime checks (e.g. counselconduit-767252945109.us-central1.run.app)."
}

variable "admin_email" {
  type        = string
  default     = "admin@shadowtagai.com"
  description = "Admin email for alert notifications."
}

variable "health_check_path" {
  type        = string
  default     = "/health"
  description = "Health check endpoint path."
}

variable "uptime_check_period" {
  type        = string
  default     = "60s"
  description = "Uptime check interval."
}

variable "firestore_write_threshold" {
  type        = number
  default     = 50000
  description = "Firestore writes/min threshold for alerting."
}

variable "enable_uptime_check" {
  type        = bool
  default     = true
  description = "Enable HTTPS uptime check."
}

variable "enable_firestore_alert" {
  type        = bool
  default     = true
  description = "Enable Firestore write spike alert."
}

# Notification channel
resource "google_monitoring_notification_channel" "email" {
  project      = var.project_id
  display_name = "${var.service_name} Admin Alerts"
  type         = "email"
  labels = {
    email_address = var.admin_email
  }
}

# HTTPS uptime check
resource "google_monitoring_uptime_check_config" "health" {
  count        = var.enable_uptime_check ? 1 : 0
  project      = var.project_id
  display_name = "${var.service_name}-health"
  timeout      = "10s"
  period       = var.uptime_check_period

  http_check {
    port         = 443
    use_ssl      = true
    path         = var.health_check_path
    validate_ssl = true
  }

  monitored_resource {
    type = "uptime_url"
    labels = {
      project_id = var.project_id
      host       = var.service_host
    }
  }
}

# Uptime failure alert
resource "google_monitoring_alert_policy" "uptime_failure" {
  count        = var.enable_uptime_check ? 1 : 0
  project      = var.project_id
  display_name = "${var.service_name} — Uptime Failing"
  combiner     = "OR"

  conditions {
    display_name = "Uptime check failing"
    condition_threshold {
      filter          = "metric.type=\"monitoring.googleapis.com/uptime_check/check_passed\" AND resource.type=\"uptime_url\""
      comparison      = "COMPARISON_LT"
      threshold_value = 1
      duration        = "300s"
      aggregations {
        alignment_period     = "60s"
        per_series_aligner   = "ALIGN_NEXT_OLDER"
        cross_series_reducer = "REDUCE_FRACTION_TRUE"
      }
    }
  }

  notification_channels = [
    google_monitoring_notification_channel.email.name
  ]
}

# Firestore write spike alert
resource "google_monitoring_alert_policy" "firestore_spike" {
  count        = var.enable_firestore_alert ? 1 : 0
  project      = var.project_id
  display_name = "${var.service_name} — High Firestore Usage"
  combiner     = "OR"

  conditions {
    display_name = "Firestore Read/Write Spikes"
    condition_threshold {
      filter          = "metric.type=\"firestore.googleapis.com/document/write_count\" AND resource.type=\"firestore_database\""
      comparison      = "COMPARISON_GT"
      threshold_value = var.firestore_write_threshold
      duration        = "300s"
      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_RATE"
      }
    }
  }

  notification_channels = [
    google_monitoring_notification_channel.email.name
  ]
}

# Outputs
output "notification_channel" {
  value       = google_monitoring_notification_channel.email
  description = "The email notification channel."
}

output "notification_channel_name" {
  value       = google_monitoring_notification_channel.email.name
  description = "Notification channel resource name for use in other modules."
}
