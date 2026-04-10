# Budget Alert Configuration
resource "google_billing_budget" "pnkln_budget" {
  billing_account = var.billing_account_id
  display_name    = "PNKLN Monthly Budget Alert"

  budget_filter {
    projects = ["projects/${var.project_id}"]

    labels = {
      project = "pnkln"
    }
  }

  amount {
    specified_amount {
      currency_code = "USD"
      units         = tostring(var.monthly_budget_alert_usd)
    }
  }

  threshold_rules {
    threshold_percent = 0.5  # Alert at 50%
  }

  threshold_rules {
    threshold_percent = 0.75  # Alert at 75%
  }

  threshold_rules {
    threshold_percent = 0.9  # Alert at 90%
  }

  threshold_rules {
    threshold_percent = 1.0  # Alert at 100%
  }

  all_updates_rule {
    disable_default_iam_recipients = false
    monitoring_notification_channels = [
      google_monitoring_notification_channel.budget_email.id
    ]
  }
}

# Notification channel for budget alerts
resource "google_monitoring_notification_channel" "budget_email" {
  display_name = "PNKLN Budget Alert Email"
  type         = "email"
  project      = var.project_id

  labels = {
    email_address = var.budget_alert_email
  }
}

# Custom metric for inference latency (p99)
resource "google_monitoring_alert_policy" "inference_latency_p99" {
  display_name = "PNKLN Inference P99 Latency Alert"
  project      = var.project_id
  combiner     = "OR"

  conditions {
    display_name = "P99 Latency > 90ms"

    condition_threshold {
      filter          = "resource.type=\"k8s_container\" AND metric.type=\"custom.googleapis.com/inference/latency_ms\""
      duration        = "60s"
      comparison      = "COMPARISON_GT"
      threshold_value = 90

      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_PERCENTILE_99"
      }
    }
  }

  notification_channels = [
    google_monitoring_notification_channel.latency_alert.id
  ]

  alert_strategy {
    auto_close = "1800s"
  }
}

# Notification channel for latency alerts
resource "google_monitoring_notification_channel" "latency_alert" {
  display_name = "PNKLN Latency Alert"
  type         = "email"
  project      = var.project_id

  labels = {
    email_address = var.alert_email
  }
}

# Dashboard for inference metrics
resource "google_monitoring_dashboard" "pnkln_inference" {
  dashboard_json = jsonencode({
    displayName = "PNKLN Inference Dashboard"
    mosaicLayout = {
      columns = 12
      tiles = [
        {
          width  = 6
          height = 4
          widget = {
            title = "Inference Latency (P50, P90, P99)"
            xyChart = {
              dataSets = [
                {
                  timeSeriesQuery = {
                    timeSeriesFilter = {
                      filter = "resource.type=\"k8s_container\" AND metric.type=\"custom.googleapis.com/inference/latency_ms\""
                      aggregation = {
                        alignmentPeriod    = "60s"
                        perSeriesAligner   = "ALIGN_PERCENTILE_50"
                        crossSeriesReducer = "REDUCE_MEAN"
                      }
                    }
                  }
                  plotType   = "LINE"
                  targetAxis = "Y1"
                },
                {
                  timeSeriesQuery = {
                    timeSeriesFilter = {
                      filter = "resource.type=\"k8s_container\" AND metric.type=\"custom.googleapis.com/inference/latency_ms\""
                      aggregation = {
                        alignmentPeriod    = "60s"
                        perSeriesAligner   = "ALIGN_PERCENTILE_90"
                        crossSeriesReducer = "REDUCE_MEAN"
                      }
                    }
                  }
                  plotType   = "LINE"
                  targetAxis = "Y1"
                },
                {
                  timeSeriesQuery = {
                    timeSeriesFilter = {
                      filter = "resource.type=\"k8s_container\" AND metric.type=\"custom.googleapis.com/inference/latency_ms\""
                      aggregation = {
                        alignmentPeriod    = "60s"
                        perSeriesAligner   = "ALIGN_PERCENTILE_99"
                        crossSeriesReducer = "REDUCE_MEAN"
                      }
                    }
                  }
                  plotType   = "LINE"
                  targetAxis = "Y1"
                }
              ]
              yAxis = {
                label = "Latency (ms)"
                scale = "LINEAR"
              }
            }
          }
        },
        {
          xPos   = 6
          width  = 6
          height = 4
          widget = {
            title = "Requests per Second"
            xyChart = {
              dataSets = [
                {
                  timeSeriesQuery = {
                    timeSeriesFilter = {
                      filter = "resource.type=\"k8s_container\" AND metric.type=\"custom.googleapis.com/inference/requests_total\""
                      aggregation = {
                        alignmentPeriod    = "60s"
                        perSeriesAligner   = "ALIGN_RATE"
                        crossSeriesReducer = "REDUCE_SUM"
                      }
                    }
                  }
                  plotType = "LINE"
                }
              ]
            }
          }
        },
        {
          yPos   = 4
          width  = 6
          height = 4
          widget = {
            title = "GPU Utilization"
            xyChart = {
              dataSets = [
                {
                  timeSeriesQuery = {
                    timeSeriesFilter = {
                      filter = "resource.type=\"k8s_node\" AND metric.type=\"compute.googleapis.com/instance/gpu/utilization\""
                      aggregation = {
                        alignmentPeriod    = "60s"
                        perSeriesAligner   = "ALIGN_MEAN"
                        crossSeriesReducer = "REDUCE_MEAN"
                      }
                    }
                  }
                  plotType = "LINE"
                }
              ]
            }
          }
        },
        {
          xPos   = 6
          yPos   = 4
          width  = 6
          height = 4
          widget = {
            title = "Pod Count by Node Pool"
            xyChart = {
              dataSets = [
                {
                  timeSeriesQuery = {
                    timeSeriesFilter = {
                      filter = "resource.type=\"k8s_pod\" AND metadata.system_labels.\"cloud.googleapis.com/gke-nodepool\"=monitoring.regex.full_match(\".*\")"
                      aggregation = {
                        alignmentPeriod    = "60s"
                        perSeriesAligner   = "ALIGN_MEAN"
                        crossSeriesReducer = "REDUCE_COUNT"
                        groupByFields      = ["metadata.system_labels.\"cloud.googleapis.com/gke-nodepool\""]
                      }
                    }
                  }
                  plotType = "STACKED_AREA"
                }
              ]
            }
          }
        }
      ]
    }
  })

  project = var.project_id
}
