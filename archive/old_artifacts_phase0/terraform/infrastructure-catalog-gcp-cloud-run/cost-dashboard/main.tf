# Cloud Monitoring Cost Dashboard Module
# Creates a custom dashboard for cost visibility across Cloud Run services

variable "project_id" {
  type        = string
  description = "GCP project ID."
}

variable "service_names" {
  type        = list(string)
  default     = ["counselconduit"]
  description = "Cloud Run service names to monitor."
}

resource "google_monitoring_dashboard" "cost_dashboard" {
  project        = var.project_id
  dashboard_json = jsonencode({
    displayName = "ShadowTag — Cloud Run Cost & Resource Dashboard"
    mosaicLayout = {
      tiles = concat(
        # CPU utilization per service
        [for i, svc in var.service_names : {
          width  = 6
          height = 4
          xPos   = (i % 2) * 6
          yPos   = floor(i / 2) * 4
          widget = {
            title = "${svc} — CPU Utilization"
            xyChart = {
              dataSets = [{
                timeSeriesQuery = {
                  timeSeriesFilter = {
                    filter         = "metric.type=\"run.googleapis.com/container/cpu/utilizations\" resource.type=\"cloud_run_revision\" resource.label.\"service_name\"=\"${svc}\""
                    aggregation = {
                      alignmentPeriod  = "300s"
                      perSeriesAligner = "ALIGN_PERCENTILE_99"
                    }
                  }
                }
                plotType = "LINE"
              }]
            }
          }
        }],
        # Memory usage per service
        [for i, svc in var.service_names : {
          width  = 6
          height = 4
          xPos   = (i % 2) * 6
          yPos   = (floor(i / 2) + length(var.service_names)) * 4
          widget = {
            title = "${svc} — Memory Usage"
            xyChart = {
              dataSets = [{
                timeSeriesQuery = {
                  timeSeriesFilter = {
                    filter         = "metric.type=\"run.googleapis.com/container/memory/utilizations\" resource.type=\"cloud_run_revision\" resource.label.\"service_name\"=\"${svc}\""
                    aggregation = {
                      alignmentPeriod  = "300s"
                      perSeriesAligner = "ALIGN_PERCENTILE_99"
                    }
                  }
                }
                plotType = "LINE"
              }]
            }
          }
        }],
        # Request count widget
        [{
          width  = 12
          height = 4
          xPos   = 0
          yPos   = (length(var.service_names) * 2) * 4
          widget = {
            title = "Total Request Count (All Services)"
            xyChart = {
              dataSets = [{
                timeSeriesQuery = {
                  timeSeriesFilter = {
                    filter         = "metric.type=\"run.googleapis.com/request_count\" resource.type=\"cloud_run_revision\""
                    aggregation = {
                      alignmentPeriod    = "300s"
                      perSeriesAligner   = "ALIGN_RATE"
                      crossSeriesReducer = "REDUCE_SUM"
                      groupByFields      = ["resource.label.service_name"]
                    }
                  }
                }
                plotType = "STACKED_BAR"
              }]
            }
          }
        }],
        # Billable instance time
        [{
          width  = 12
          height = 4
          xPos   = 0
          yPos   = ((length(var.service_names) * 2) + 1) * 4
          widget = {
            title = "Billable Instance Time (Cost Proxy)"
            xyChart = {
              dataSets = [{
                timeSeriesQuery = {
                  timeSeriesFilter = {
                    filter         = "metric.type=\"run.googleapis.com/container/billable_instance_time\" resource.type=\"cloud_run_revision\""
                    aggregation = {
                      alignmentPeriod    = "300s"
                      perSeriesAligner   = "ALIGN_RATE"
                      crossSeriesReducer = "REDUCE_SUM"
                      groupByFields      = ["resource.label.service_name"]
                    }
                  }
                }
                plotType = "LINE"
              }]
            }
          }
        }]
      )
    }
  })
}

output "dashboard_id" {
  value       = google_monitoring_dashboard.cost_dashboard.id
  description = "Monitoring dashboard resource ID."
}
