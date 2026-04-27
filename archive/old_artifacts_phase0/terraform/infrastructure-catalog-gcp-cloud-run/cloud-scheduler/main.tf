# Cloud Scheduler Module
# Manages Cloud Scheduler jobs for cron-triggered Cloud Run services
# Used for: Firestore GDPR deletion, backup verification, analytics

variable "project_id" {
  type        = string
  description = "GCP project ID."
}

variable "region" {
  type        = string
  default     = "us-central1"
  description = "GCP region."
}

variable "jobs" {
  type = map(object({
    description = string
    schedule    = string
    time_zone   = optional(string, "America/Los_Angeles")
    uri         = string
    http_method = optional(string, "POST")
    body        = optional(string, "")
    headers     = optional(map(string), {})
    oidc_sa     = optional(string, "")
    oidc_audience = optional(string, "")
    retry_count = optional(number, 1)
    paused      = optional(bool, false)
  }))
  description = "Map of Cloud Scheduler jobs to create."
}

resource "google_cloud_scheduler_job" "jobs" {
  for_each    = var.jobs
  project     = var.project_id
  region      = var.region
  name        = each.key
  description = each.value.description
  schedule    = each.value.schedule
  time_zone   = each.value.time_zone
  paused      = each.value.paused

  retry_config {
    retry_count = each.value.retry_count
  }

  http_target {
    http_method = each.value.http_method
    uri         = each.value.uri
    body        = each.value.body != "" ? base64encode(each.value.body) : null
    headers     = merge({ "Content-Type" = "application/json" }, each.value.headers)

    dynamic "oidc_token" {
      for_each = each.value.oidc_sa != "" ? [1] : []
      content {
        service_account_email = each.value.oidc_sa
        audience              = each.value.oidc_audience != "" ? each.value.oidc_audience : each.value.uri
      }
    }
  }
}

output "job_names" {
  value       = { for k, v in google_cloud_scheduler_job.jobs : k => v.name }
  description = "Map of created Cloud Scheduler job names."
}

output "job_schedules" {
  value       = { for k, v in google_cloud_scheduler_job.jobs : k => v.schedule }
  description = "Map of job schedules."
}
