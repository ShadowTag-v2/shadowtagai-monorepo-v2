# CounselConduit — Terraform Infrastructure as Code
# Item #10: Terraform for all GCP monitoring resources

terraform {
  required_version = ">= 1.6"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"
    }
  }
  backend "gcs" {
    bucket = "shadowtag-omega-v4-tf-state"
    prefix = "counselconduit/monitoring"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

variable "project_id" {
  default = "shadowtag-omega-v4"
}

variable "region" {
  default = "us-central1"
}

variable "notification_email" {
  default = "founder@shadowtagai.com"
}

variable "service_url" {
  default = "https://counselconduit-767252945109.us-central1.run.app"
}

# ── Notification Channel ─────────────────────────────────────────────────

resource "google_monitoring_notification_channel" "email" {
  display_name = "CounselConduit Alerts"
  type         = "email"

  labels = {
    email_address = var.notification_email
  }
}

# ── Uptime Check ─────────────────────────────────────────────────────────

resource "google_monitoring_uptime_check_config" "health" {
  display_name = "counselconduit-health"
  timeout      = "10s"
  period       = "60s"

  http_check {
    path         = "/health"
    port         = 443
    use_ssl      = true
    validate_ssl = true
    accepted_response_status_codes {
      status_class = "STATUS_CLASS_2XX"
    }
  }

  monitored_resource {
    type = "uptime_url"
    labels = {
      project_id = var.project_id
      host       = "counselconduit-767252945109.us-central1.run.app"
    }
  }
}

resource "google_monitoring_uptime_check_config" "health_providers" {
  display_name = "counselconduit-health-providers"
  timeout      = "10s"
  period       = "60s"

  http_check {
    path         = "/health/providers"
    port         = 443
    use_ssl      = true
    validate_ssl = true
    accepted_response_status_codes {
      status_class = "STATUS_CLASS_2XX"
    }
  }

  monitored_resource {
    type = "uptime_url"
    labels = {
      project_id = var.project_id
      host       = "counselconduit-767252945109.us-central1.run.app"
    }
  }
}

resource "google_monitoring_uptime_check_config" "oracle_health" {
  display_name = "CounselConduit Oracle Studio Pipeline"
  timeout      = "10s"
  period       = "60s"

  http_check {
    path         = "/oracle/health"
    port         = 443
    use_ssl      = true
    validate_ssl = true
    accepted_response_status_codes {
      status_class = "STATUS_CLASS_2XX"
    }
  }

  monitored_resource {
    type = "uptime_url"
    labels = {
      project_id = var.project_id
      host       = "counselconduit-767252945109.us-central1.run.app"
    }
  }
}

resource "google_monitoring_alert_policy" "uptime" {
  display_name = "CounselConduit Uptime Failure"
  combiner     = "OR"

  conditions {
    display_name = "Uptime check failed"

    condition_threshold {
      filter          = "resource.type = \"uptime_url\" AND metric.type = \"monitoring.googleapis.com/uptime_check/check_passed\" AND metric.labels.check_id = \"${google_monitoring_uptime_check_config.health.uptime_check_id}\""
      comparison      = "COMPARISON_GT"
      threshold_value = 1
      duration        = "300s"

      aggregations {
        alignment_period   = "1200s"
        per_series_aligner = "ALIGN_NEXT_OLDER"
        cross_series_reducer = "REDUCE_COUNT_FALSE"
        group_by_fields    = ["resource.*"]
      }
    }
  }

  notification_channels = [google_monitoring_notification_channel.email.name]

  documentation {
    content   = "CounselConduit health endpoint is failing. Check Cloud Run logs."
    mime_type = "text/markdown"
  }
}

# ── Fallback Rate Alert ──────────────────────────────────────────────────

resource "google_logging_metric" "fallback_rate" {
  name   = "counselconduit_fallback_rate"
  filter = "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"counselconduit\" AND jsonPayload.message=~\"fallback.*activated\""

  metric_descriptor {
    metric_kind = "DELTA"
    value_type  = "INT64"
    unit        = "1"
  }
}

resource "google_monitoring_alert_policy" "fallback" {
  display_name = "CounselConduit High Fallback Rate"
  combiner     = "OR"

  conditions {
    display_name = "Fallback rate > 10/5min"

    condition_threshold {
      filter          = "resource.type = \"cloud_run_revision\" AND metric.type = \"logging.googleapis.com/user/${google_logging_metric.fallback_rate.name}\""
      comparison      = "COMPARISON_GT"
      threshold_value = 10
      duration        = "300s"

      aggregations {
        alignment_period   = "300s"
        per_series_aligner = "ALIGN_SUM"
      }
    }
  }

  notification_channels = [google_monitoring_notification_channel.email.name]
}

# ── Error Burn Rate Alert ────────────────────────────────────────────────

resource "google_monitoring_alert_policy" "burn_rate" {
  display_name = "CounselConduit High Error Burn Rate (P1)"
  combiner     = "OR"

  conditions {
    display_name = "5xx error rate > 5% over 5 minutes"

    condition_threshold {
      filter          = "resource.type = \"cloud_run_revision\" AND resource.labels.service_name = \"counselconduit\" AND metric.type = \"run.googleapis.com/request_count\" AND metric.labels.response_code_class = \"5xx\""
      comparison      = "COMPARISON_GT"
      threshold_value = 5
      duration        = "300s"

      aggregations {
        alignment_period     = "60s"
        per_series_aligner   = "ALIGN_RATE"
        cross_series_reducer = "REDUCE_SUM"
      }
    }
  }

  notification_channels = [google_monitoring_notification_channel.email.name]

  documentation {
    content   = "## P1 — High Error Burn Rate\n\nThe CounselConduit service is burning through its error budget.\n\n### Immediate Actions\n1. Check Cloud Run logs for 5xx errors\n2. Verify provider health via /admin/provider-health\n3. Check circuit breaker via /admin/circuit-breaker\n4. Consider rollback to previous revision"
    mime_type = "text/markdown"
  }
}

# ── Admin Auth Failures ──────────────────────────────────────────────────

resource "google_logging_metric" "admin_auth_failures" {
  name   = "counselconduit_admin_auth_failures"
  filter = "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"counselconduit\" AND jsonPayload.message=~\"admin.*auth.*fail|Unauthorized admin\""

  metric_descriptor {
    metric_kind = "DELTA"
    value_type  = "INT64"
    unit        = "1"
  }
}

resource "google_monitoring_alert_policy" "admin_auth" {
  display_name = "CounselConduit Admin Auth Failures"
  combiner     = "OR"

  conditions {
    display_name = "Admin auth failures > 5/5min"

    condition_threshold {
      filter          = "resource.type = \"cloud_run_revision\" AND metric.type = \"logging.googleapis.com/user/${google_logging_metric.admin_auth_failures.name}\""
      comparison      = "COMPARISON_GT"
      threshold_value = 5
      duration        = "300s"

      aggregations {
        alignment_period   = "300s"
        per_series_aligner = "ALIGN_SUM"
      }
    }
  }

  notification_channels = [google_monitoring_notification_channel.email.name]

  documentation {
    content   = "Multiple admin authentication failures detected. Check for brute-force or credential compromise."
    mime_type = "text/markdown"
  }
}

# ── Billing Budget ───────────────────────────────────────────────────────

resource "google_billing_budget" "counselconduit" {
  billing_account = "YOUR_BILLING_ACCOUNT_ID" # Replace with actual billing account
  display_name    = "CounselConduit Monthly Budget"

  budget_filter {
    projects               = ["projects/${var.project_id}"]
    credit_types_treatment = "INCLUDE_ALL_CREDITS"
  }

  amount {
    specified_amount {
      currency_code = "USD"
      units         = "50"
    }
  }

  threshold_rules {
    threshold_percent = 0.5
    spend_basis       = "CURRENT_SPEND"
  }
  threshold_rules {
    threshold_percent = 0.9
    spend_basis       = "CURRENT_SPEND"
  }
  threshold_rules {
    threshold_percent = 1.0
    spend_basis       = "CURRENT_SPEND"
  }

  all_updates_rule {
    monitoring_notification_channels = [google_monitoring_notification_channel.email.name]
    enable_project_level_recipients  = true
  }
}

# ── Cloud Armor WAF ──────────────────────────────────────────────────────

resource "google_compute_security_policy" "counselconduit" {
  name = "counselconduit-waf"

  # Admin rate limit
  rule {
    action   = "rate_based_ban"
    priority = 900
    match {
      expr {
        expression = "request.path.matches('/admin/.*')"
      }
    }
    rate_limit_options {
      rate_limit_threshold {
        count        = 20
        interval_sec = 60
      }
      ban_duration_sec = 600
      conform_action   = "allow"
      exceed_action    = "deny(429)"
    }
  }

  # XSS protection
  rule {
    action   = "deny(403)"
    priority = 1000
    match {
      expr {
        expression = "evaluatePreconfiguredWaf('xss-v33-stable')"
      }
    }
  }

  # SQLi protection
  rule {
    action   = "deny(403)"
    priority = 1001
    match {
      expr {
        expression = "evaluatePreconfiguredWaf('sqli-v33-stable')"
      }
    }
  }

  # General rate limit
  rule {
    action   = "rate_based_ban"
    priority = 1100
    match {
      versioned_expr = "SRC_IPS_V1"
      config {
        src_ip_ranges = ["*"]
      }
    }
    rate_limit_options {
      rate_limit_threshold {
        count        = 100
        interval_sec = 60
      }
      ban_duration_sec = 300
      conform_action   = "allow"
      exceed_action    = "deny(429)"
    }
  }

  # Default allow
  rule {
    action   = "allow"
    priority = 2147483647
    match {
      versioned_expr = "SRC_IPS_V1"
      config {
        src_ip_ranges = ["*"]
      }
    }
  }
}

# ── Cloud Scheduler Jobs ─────────────────────────────────────────────────

resource "google_cloud_scheduler_job" "session_cleanup" {
  name             = "counselconduit-session-cleanup"
  schedule         = "0 3 * * 0"
  time_zone        = "Etc/UTC"
  description      = "Weekly session pin cleanup (Sunday 3AM)"
  region           = var.region

  http_target {
    http_method = "POST"
    uri         = "${var.service_url}/admin/session-cleanup"

    oidc_token {
      service_account_email = "counselconduit-sa@${var.project_id}.iam.gserviceaccount.com"
      audience              = var.service_url
    }
  }
}

resource "google_cloud_scheduler_job" "policy_reload" {
  name             = "counselconduit-policy-reload"
  schedule         = "*/5 * * * *"
  time_zone        = "Etc/UTC"
  description      = "Reload firm policies from Firestore every 5 min"
  region           = var.region

  http_target {
    http_method = "POST"
    uri         = "${var.service_url}/admin/firm-policies/reload"

    oidc_token {
      service_account_email = "counselconduit-sa@${var.project_id}.iam.gserviceaccount.com"
      audience              = var.service_url
    }
  }
}

# ── Monitoring Service + SLO ─────────────────────────────────────────────

resource "google_monitoring_custom_service" "counselconduit" {
  display_name = "CounselConduit"

  telemetry {
    resource_name = "//run.googleapis.com/projects/${var.project_id}/locations/${var.region}/services/counselconduit"
  }
}

resource "google_monitoring_slo" "availability" {
  service      = google_monitoring_custom_service.counselconduit.service_id
  display_name = "CounselConduit 99.5% Availability"
  goal         = 0.995

  rolling_period_days = 30

  request_based_sli {
    good_total_ratio {
      good_service_filter  = "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"counselconduit\" AND metric.type=\"run.googleapis.com/request_count\" AND metric.labels.response_code_class!=\"5xx\""
      total_service_filter = "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"counselconduit\" AND metric.type=\"run.googleapis.com/request_count\""
    }
  }
}

# ── Outputs ──────────────────────────────────────────────────────────────

output "uptime_check_id" {
  value = google_monitoring_uptime_check_config.health.uptime_check_id
}

output "slo_id" {
  value = google_monitoring_slo.availability.slo_id
}

output "monitoring_service_id" {
  value = google_monitoring_custom_service.counselconduit.service_id
}

output "notification_channel_id" {
  value = google_monitoring_notification_channel.email.name
}
