# ============================================
# HEADFADE MCP – CLOUD MONITORING ALERT POLICIES (Terraform)
# ============================================

resource "google_monitoring_alert_policy" "cloudrun_error_rate" {
  display_name = "HeadFade MCP – High Error Rate"
  combiner     = "OR"
  project      = var.project_id

  conditions {
    display_name = "5xx error rate > 5%"

    condition_threshold {
      filter = <<EOT
        resource.type="cloud_run_revision"
        AND resource.labels.service_name="headfade-mcp"
        AND metric.type="run.googleapis.com/request_count"
        AND metric.labels.response_code_class="5xx"
      EOT

      aggregations {
        alignment_period   = "300s"
        per_series_aligner = "ALIGN_RATE"
      }

      comparison      = "COMPARISON_GT"
      threshold_value = 0.05
      duration        = "300s"
      trigger {
        count = 1
      }
    }
  }

  notification_channels = var.notification_channels
  documentation {
    content   = "HeadFade MCP is returning >5% 5xx errors. Investigate immediately."
    mime_type = "text/markdown"
  }
}

resource "google_monitoring_alert_policy" "cloudrun_latency" {
  display_name = "HeadFade MCP – High Latency (p95)"
  combiner     = "OR"
  project      = var.project_id

  conditions {
    display_name = "p95 latency > 500ms"

    condition_threshold {
      filter = <<EOT
        resource.type="cloud_run_revision"
        AND resource.labels.service_name="headfade-mcp"
        AND metric.type="run.googleapis.com/request_latencies"
      EOT

      aggregations {
        alignment_period   = "300s"
        per_series_aligner = "ALIGN_PERCENTILE_95"
      }

      comparison      = "COMPARISON_GT"
      threshold_value = 500
      duration        = "180s"
      trigger {
        count = 1
      }
    }
  }

  notification_channels = var.notification_channels
  documentation {
    content   = "HeadFade MCP p95 latency exceeded 500ms. Check for cold starts or resource contention."
    mime_type = "text/markdown"
  }
}

# Optional: License grant rate drop alert
resource "google_monitoring_alert_policy" "license_grant_drop" {
  display_name = "HeadFade – License Grant Rate Drop"
  combiner     = "OR"
  project      = var.project_id

  conditions {
    display_name = "License grants < 5 per hour"

    condition_threshold {
      filter = <<EOT
        resource.type="cloud_run_revision"
        AND resource.labels.service_name="headfade-mcp"
        AND metric.type="custom.googleapis.com/licenses_granted"
      EOT

      aggregations {
        alignment_period   = "3600s"
        per_series_aligner = "ALIGN_RATE"
      }

      comparison      = "COMPARISON_LT"
      threshold_value = 5
      duration        = "3600s"
    }
  }

  notification_channels = var.notification_channels
  documentation {
    content   = "HeadFade A2A license grant rate has dropped significantly. Check Stripe webhooks and database."
    mime_type = "text/markdown"
  }
}
```